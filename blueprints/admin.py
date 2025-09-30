"""
Blueprint administrativo para gestão avançada de permissões
Interface para administradores gerenciarem roles, permissões e acessos
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from models import (
    db, Permission, TeamPermission, TemporaryAccess, AccessAudit,
    User, Team, UserRole
)
from permission_service import (
    PermissionService, permission_service
)
from permission_service import ResourceType, PermissionAction, PermissionLevel
from audit_service import AuditService
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ==================== DASHBOARD ADMINISTRATIVO ====================

@admin_bp.route('/permissions')
@login_required
def permissions_dashboard():
    """Dashboard administrativo de permissões"""
    if current_user.role.value != 'admin':
        flash('Apenas administradores podem acessar esta área.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        # Dados para o dashboard
        interface_data = permission_service.create_admin_interface_data()

        # Estatísticas adicionais
        stats = {
            'total_permissions': interface_data.get('permissions_count', 0),
            'total_team_permissions': interface_data.get('team_permissions_count', 0),
            'total_temporary_access': interface_data.get('temporary_access_count', 0),
            'recent_access_audits': interface_data.get('recent_audit_count', 0),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_teams': Team.query.count()
        }

        # Permissões recentes
        recent_permissions = Permission.query.filter_by(is_active=True)\
            .order_by(Permission.granted_at.desc()).limit(10).all()

        # Acessos temporários ativos
        active_temp_access = TemporaryAccess.query.filter_by(is_active=True)\
            .filter(TemporaryAccess.expires_at > datetime.utcnow())\
            .order_by(TemporaryAccess.expires_at).limit(10).all()

        return render_template('admin/permissions_dashboard.html',
                             stats=stats,
                             interface_data=interface_data,
                             recent_permissions=recent_permissions,
                             active_temp_access=active_temp_access)

    except Exception as e:
        current_app.logger.error(f"Erro no dashboard de permissões: {str(e)}")
        flash('Erro ao carregar dashboard de permissões.', 'error')
        return redirect(url_for('main.dashboard'))

# ==================== GESTÃO DE PERMISSÕES ====================

@admin_bp.route('/permissions/manage', methods=['GET', 'POST'])
@login_required
def manage_permissions():
    """Gerenciar permissões do sistema"""
    if current_user.role.value != 'admin':
        flash('Apenas administradores podem gerenciar permissões.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            # Criar nova permissão
            permission_data = {
                'name': request.form['name'],
                'role': request.form['role'],
                'resource_type': request.form['resource_type'],
                'action': request.form['action'],
                'permission_level': int(request.form['permission_level']),
                'is_temporary': 'is_temporary' in request.form,
                'expires_at': None
            }

            if permission_data['is_temporary']:
                hours = int(request.form.get('duration_hours', 24))
                permission_data['expires_at'] = datetime.utcnow() + timedelta(hours=hours)

            # Criar permissão
            permission = Permission(**permission_data)
            db.session.add(permission)
            db.session.commit()

            # Auditoria
            AuditService.log_operation(
                entity_type='permission',
                entity_id=permission.id,
                operation='create_permission',
                operation_details=permission_data,
                compliance_level='critical'
            )

            flash('Permissão criada com sucesso!', 'success')
            return redirect(url_for('admin.manage_permissions'))

        except Exception as e:
            current_app.logger.error(f"Erro ao criar permissão: {str(e)}")
            db.session.rollback()
            flash(f'Erro ao criar permissão: {str(e)}', 'error')

    # GET request - mostrar formulário
    roles = [role.value for role in UserRole]
    resources = [resource.value for resource in ResourceType]
    actions = [action.value for action in PermissionAction]
    levels = [level.value for level in PermissionLevel]

    # Listar permissões existentes
    permissions = Permission.query.filter_by(is_active=True).order_by(Permission.role).all()

    return render_template('admin/manage_permissions.html',
                         roles=roles,
                         resources=resources,
                         actions=actions,
                         levels=levels,
                         permissions=permissions)

@admin_bp.route('/permissions/<int:permission_id>/revoke', methods=['POST'])
@login_required
def revoke_permission(permission_id):
    """Revogar permissão específica"""
    if current_user.role.value != 'admin':
        flash('Apenas administradores podem revogar permissões.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        permission = Permission.query.get_or_404(permission_id)
        reason = request.form.get('reason', 'Revogado pelo administrador')

        permission.revoke(current_user.id, reason)
        db.session.commit()

        # Auditoria
        AuditService.log_operation(
            entity_type='permission',
            entity_id=permission_id,
            operation='revoke_permission',
            operation_details={
                'original_role': permission.role,
                'resource_type': permission.resource_type,
                'action': permission.action,
                'reason': reason
            },
            compliance_level='critical'
        )

        flash('Permissão revogada com sucesso!', 'success')

    except Exception as e:
        current_app.logger.error(f"Erro ao revogar permissão: {str(e)}")
        flash(f'Erro ao revogar permissão: {str(e)}', 'error')

    return redirect(url_for('admin.manage_permissions'))

# ==================== GESTÃO DE ACESSOS TEMPORÁRIOS ====================

@admin_bp.route('/temporary-access', methods=['GET', 'POST'])
@login_required
def manage_temporary_access():
    """Gerenciar acessos temporários"""
    if current_user.role.value != 'admin':
        flash('Apenas administradores podem gerenciar acessos temporários.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            # Conceder acesso temporário
            access_data = {
                'user_id': int(request.form['user_id']),
                'resource_type': request.form['resource_type'],
                'resource_id': int(request.form['resource_id']),
                'action': request.form['action'],
                'duration_hours': int(request.form['duration_hours']),
                'reason': request.form.get('reason', '')
            }

            temp_access = permission_service.grant_temporary_access(
                granted_by=current_user.id,
                **access_data
            )

            flash(f'Acesso temporário concedido por {access_data["duration_hours"]} horas!', 'success')
            return redirect(url_for('admin.manage_temporary_access'))

        except Exception as e:
            current_app.logger.error(f"Erro ao conceder acesso temporário: {str(e)}")
            flash(f'Erro ao conceder acesso temporário: {str(e)}', 'error')

    # GET request - mostrar lista
    temp_accesses = TemporaryAccess.query.filter_by(is_active=True)\
        .order_by(TemporaryAccess.expires_at).all()

    # Usuários para seleção
    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()

    return render_template('admin/manage_temporary_access.html',
                         temp_accesses=temp_accesses,
                         users=users)

@admin_bp.route('/temporary-access/<int:access_id>/revoke', methods=['POST'])
@login_required
def revoke_temporary_access(access_id):
    """Revogar acesso temporário"""
    if current_user.role.value != 'admin':
        flash('Apenas administradores podem revogar acessos temporários.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        reason = request.form.get('reason', 'Revogado pelo administrador')

        permission_service.revoke_temporary_access(access_id, current_user.id, reason)

        flash('Acesso temporário revogado com sucesso!', 'success')

    except Exception as e:
        current_app.logger.error(f"Erro ao revogar acesso temporário: {str(e)}")
        flash(f'Erro ao revogar acesso temporário: {str(e)}', 'error')

    return redirect(url_for('admin.manage_temporary_access'))

# ==================== AUDITORIA DE ACESSOS ====================

@admin_bp.route('/access-audit')
@login_required
def access_audit():
    """Visualizar auditoria de acessos"""
    if current_user.role.value not in ['admin', 'manager']:
        flash('Apenas administradores e gerentes podem visualizar auditoria de acessos.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        # Filtros
        user_filter = request.args.get('user_id', type=int)
        resource_filter = request.args.get('resource_type')
        action_filter = request.args.get('action')
        granted_filter = request.args.get('access_granted')
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))

        # Query base
        query = AccessAudit.query

        if user_filter:
            query = query.filter_by(user_id=user_filter)
        if resource_filter:
            query = query.filter_by(resource_type=resource_filter)
        if action_filter:
            query = query.filter_by(action=action_filter)
        if granted_filter is not None:
            query = query.filter_by(access_granted=granted_filter.lower() == 'true')

        # Ordenação por data (mais recente primeiro)
        query = query.order_by(AccessAudit.accessed_at.desc())

        # Paginação
        total = query.count()
        audits = query.offset(offset).limit(limit).all()

        # Usuários para filtro
        users = User.query.filter_by(is_active=True).order_by(User.full_name).all()

        return render_template('admin/access_audit.html',
                             audits=audits,
                             users=users,
                             total=total,
                             limit=limit,
                             offset=offset,
                             filters={
                                 'user_id': user_filter,
                                 'resource_type': resource_filter,
                                 'action': action_filter,
                                 'access_granted': granted_filter
                             })

    except Exception as e:
        current_app.logger.error(f"Erro ao visualizar auditoria de acessos: {str(e)}")
        flash('Erro ao carregar auditoria de acessos.', 'error')
        return redirect(url_for('main.dashboard'))

# ==================== PERMISSÕES DE EQUIPE ====================

@admin_bp.route('/team-permissions', methods=['GET', 'POST'])
@login_required
def manage_team_permissions():
    """Gerenciar permissões de equipes"""
    if current_user.role.value != 'admin':
        flash('Apenas administradores podem gerenciar permissões de equipe.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            # Criar permissão de equipe
            team_permission_data = {
                'team_id': int(request.form['team_id']),
                'resource_type': request.form['resource_type'],
                'resource_id': int(request.form['resource_id']) if request.form.get('resource_id') else None,
                'action': request.form['action'],
                'permission_level': int(request.form['permission_level'])
            }

            team_permission = TeamPermission(**team_permission_data)
            db.session.add(team_permission)
            db.session.commit()

            # Auditoria
            AuditService.log_operation(
                entity_type='team_permission',
                entity_id=team_permission.id,
                operation='create_team_permission',
                operation_details=team_permission_data,
                compliance_level='critical'
            )

            flash('Permissão de equipe criada com sucesso!', 'success')
            return redirect(url_for('admin.manage_team_permissions'))

        except Exception as e:
            current_app.logger.error(f"Erro ao criar permissão de equipe: {str(e)}")
            db.session.rollback()
            flash(f'Erro ao criar permissão de equipe: {str(e)}', 'error')

    # GET request - mostrar lista
    team_permissions = TeamPermission.query.filter_by(is_active=True).order_by(TeamPermission.team_id).all()
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()

    return render_template('admin/manage_team_permissions.html',
                          team_permissions=team_permissions,
                          teams=teams)

@admin_bp.route('/team-permissions/<int:permission_id>/revoke', methods=['POST'])
@login_required
def revoke_team_permission(permission_id):
    """Revogar permissão de equipe específica"""
    if current_user.role.value != 'admin':
        flash('Apenas administradores podem revogar permissões de equipe.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        team_permission = TeamPermission.query.get_or_404(permission_id)
        reason = request.form.get('reason', 'Revogado pelo administrador')

        team_permission.is_active = False

        # Auditoria
        AuditService.log_operation(
            entity_type='team_permission',
            entity_id=permission_id,
            operation='revoke_team_permission',
            operation_details={
                'team_id': team_permission.team_id,
                'resource_type': team_permission.resource_type,
                'action': team_permission.action,
                'reason': reason
            },
            compliance_level='critical'
        )

        db.session.commit()
        flash('Permissão de equipe revogada com sucesso!', 'success')

    except Exception as e:
        current_app.logger.error(f"Erro ao revogar permissão de equipe: {str(e)}")
        flash(f'Erro ao revogar permissão de equipe: {str(e)}', 'error')

    return redirect(url_for('admin.manage_team_permissions'))

# ==================== RELATÓRIOS DE PERMISSÕES ====================

@admin_bp.route('/permission-reports')
@login_required
def permission_reports():
    """Relatórios de permissões e acessos"""
    if current_user.role.value not in ['admin', 'manager']:
        flash('Apenas administradores e gerentes podem visualizar relatórios de permissões.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        # Estatísticas gerais
        stats = {
            'total_permissions': Permission.query.filter_by(is_active=True).count(),
            'total_team_permissions': TeamPermission.query.filter_by(is_active=True).count(),
            'total_temporary_access': TemporaryAccess.query.filter_by(is_active=True).count(),
            'expired_temp_access': TemporaryAccess.query.filter(
                TemporaryAccess.is_active == True,
                TemporaryAccess.expires_at <= datetime.utcnow()
            ).count(),
            'recent_access_denials': AccessAudit.query.filter(
                AccessAudit.access_granted == False,
                AccessAudit.accessed_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }

        # Permissões por role
        permissions_by_role = {}
        for role in UserRole:
            count = Permission.query.filter_by(role=role.value, is_active=True).count()
            permissions_by_role[role.value] = count

        # Acessos recentes (últimas 24h)
        recent_access = AccessAudit.query.filter(
            AccessAudit.accessed_at >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(AccessAudit.accessed_at.desc()).limit(20).all()

        return render_template('admin/permission_reports.html',
                             stats=stats,
                             permissions_by_role=permissions_by_role,
                             recent_access=recent_access)

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatórios de permissões: {str(e)}")
        flash('Erro ao carregar relatórios de permissões.', 'error')
        return redirect(url_for('main.dashboard'))

# ==================== APIs PARA INTERFACE ====================

@admin_bp.route('/api/permission-matrix')
@login_required
def get_permission_matrix():
    """API para obter matriz de permissões"""
    if current_user.role.value != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        matrix = permission_service.get_permission_matrix()
        return jsonify({'success': True, 'data': matrix})

    except Exception as e:
        current_app.logger.error(f"Erro ao obter matriz de permissões: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/user-permissions/<int:user_id>')
@login_required
def get_user_permissions(user_id):
    """API para obter permissões de usuário específico"""
    if current_user.role.value not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        user = User.query.get_or_404(user_id)
        permissions = permission_service.get_user_effective_permissions(user)

        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'name': user.full_name,
                    'role': user.role.value
                },
                'permissions': permissions
            }
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter permissões do usuário: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/grant-temp-access', methods=['POST'])
@login_required
def api_grant_temp_access():
    """API para conceder acesso temporário"""
    if current_user.role.value != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dados obrigatórios'}), 400

        temp_access = permission_service.grant_temporary_access(
            user_id=data['user_id'],
            resource_type=data['resource_type'],
            resource_id=data['resource_id'],
            action=data['action'],
            granted_by=current_user.id,
            duration_hours=data.get('duration_hours', 24),
            reason=data.get('reason')
        )

        return jsonify({
            'success': True,
            'data': {
                'access_id': temp_access.id,
                'expires_at': temp_access.expires_at.isoformat(),
                'duration_hours': data.get('duration_hours', 24)
            }
        })

    except Exception as e:
        current_app.logger.error(f"Erro na API de acesso temporário: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500