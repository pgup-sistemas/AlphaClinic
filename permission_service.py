"""
Sistema Avançado de Permissões e Controle de Acesso
Implementa RBAC (Role-Based Access Control) granular para sistema profissional
"""

from enum import Enum
from models import User, UserRole, db
from flask import current_app
from audit_service import AuditService
from functools import wraps
import json
from datetime import datetime, timedelta

class PermissionLevel(Enum):
    """Níveis de permissão hierárquicos"""
    NONE = 0
    READ = 1
    WRITE = 2
    DELETE = 3
    ADMIN = 4

class ResourceType(Enum):
    """Tipos de recursos do sistema"""
    DOCUMENT = "document"
    AUDIT = "audit"
    NON_CONFORMITY = "non_conformity"
    CAPA = "capa"
    USER = "user"
    TEAM = "team"
    PROCESS = "process"
    NORM = "norm"
    REPORT = "report"
    SYSTEM = "system"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"

class PermissionAction(Enum):
    """Ações possíveis em recursos"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    SIGN = "sign"
    EXPORT = "export"
    IMPORT = "import"
    CONFIGURE = "configure"

class PermissionService:
    """Serviço avançado de permissões com suporte a banco de dados"""

    # Matriz de permissões padrão por role (fallback)
    DEFAULT_PERMISSIONS = {
        UserRole.ADMIN.value: {
            ResourceType.DOCUMENT.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
                PermissionAction.DELETE.value: PermissionLevel.ADMIN,
                PermissionAction.APPROVE.value: PermissionLevel.ADMIN,
                PermissionAction.SIGN.value: PermissionLevel.ADMIN,
                PermissionAction.EXPORT.value: PermissionLevel.ADMIN,
            },
            ResourceType.AUDIT.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
                PermissionAction.DELETE.value: PermissionLevel.ADMIN,
                PermissionAction.APPROVE.value: PermissionLevel.ADMIN,
                PermissionAction.EXPORT.value: PermissionLevel.ADMIN,
            },
            ResourceType.USER.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
                PermissionAction.DELETE.value: PermissionLevel.ADMIN,
            },
            ResourceType.SYSTEM.value: {
                PermissionAction.CONFIGURE.value: PermissionLevel.ADMIN,
            }
        },
        UserRole.MANAGER.value: {
            ResourceType.DOCUMENT.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
                PermissionAction.APPROVE.value: PermissionLevel.ADMIN,
                PermissionAction.SIGN.value: PermissionLevel.ADMIN,
                PermissionAction.EXPORT.value: PermissionLevel.ADMIN,
            },
            ResourceType.AUDIT.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
                PermissionAction.APPROVE.value: PermissionLevel.ADMIN,
                PermissionAction.EXPORT.value: PermissionLevel.ADMIN,
            },
            ResourceType.NON_CONFORMITY.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
                PermissionAction.APPROVE.value: PermissionLevel.ADMIN,
            },
            ResourceType.CAPA.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
                PermissionAction.APPROVE.value: PermissionLevel.ADMIN,
            }
        },
        UserRole.AUDITOR.value: {
            ResourceType.DOCUMENT.value: {
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.WRITE,
            },
            ResourceType.AUDIT.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
            },
            ResourceType.NON_CONFORMITY.value: {
                PermissionAction.CREATE.value: PermissionLevel.ADMIN,
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.ADMIN,
            },
            ResourceType.REPORT.value: {
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.EXPORT.value: PermissionLevel.ADMIN,
            }
        },
        UserRole.REVIEWER.value: {
            ResourceType.DOCUMENT.value: {
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.WRITE,
                PermissionAction.APPROVE.value: PermissionLevel.ADMIN,
                PermissionAction.SIGN.value: PermissionLevel.ADMIN,
            }
        },
        UserRole.USER.value: {
            ResourceType.DOCUMENT.value: {
                PermissionAction.READ.value: PermissionLevel.READ,
                PermissionAction.CREATE.value: PermissionLevel.WRITE,
                PermissionAction.UPDATE.value: PermissionLevel.NONE,  # Apenas próprios documentos
            },
            ResourceType.AUDIT.value: {
                PermissionAction.READ.value: PermissionLevel.READ,
            },
            ResourceType.REPORT.value: {
                PermissionAction.READ.value: PermissionLevel.READ,
            }
        }
    }

    @staticmethod
    def check_permission(user, resource_type, action, resource_owner_id=None, resource_id=None):
        """
        Verifica se usuário tem permissão para ação em recurso

        Args:
            user: Usuário solicitante
            resource_type: Tipo do recurso (ResourceType)
            action: Ação solicitada (PermissionAction)
            resource_owner_id: ID do proprietário do recurso (para regras de ownership)
            resource_id: ID específico do recurso

        Returns:
            Tupla (has_permission, required_level, user_level, permission_source)
        """
        try:
            user_role = user.role.value if user.role else UserRole.USER.value
            resource_str = resource_type.value if hasattr(resource_type, 'value') else str(resource_type)
            action_str = action.value if hasattr(action, 'value') else str(action)

            # 1. Verificar permissões específicas do banco de dados
            db_permission = PermissionService._check_db_permissions(user_role, resource_str, action_str)
            if db_permission:
                user_level = PermissionLevel(db_permission.permission_level)
                permission_source = 'database'
            else:
                # 2. Fallback para matriz padrão
                user_permissions = PermissionService.DEFAULT_PERMISSIONS.get(user_role, {})
                resource_permissions = user_permissions.get(resource_str, {})
                user_level = resource_permissions.get(action_str, PermissionLevel.NONE)
                permission_source = 'default_matrix'

            # 3. Verificar regras especiais de ownership
            if (user_level == PermissionLevel.NONE and resource_owner_id and
                resource_owner_id == user.id and action_str in ['read', 'update']):
                user_level = PermissionLevel(action_str.upper())
                permission_source = 'ownership'

            # 4. Verificar acesso temporário
            if user_level == PermissionLevel.NONE and resource_id:
                temp_access = PermissionService._check_temporary_access(user.id, resource_str, resource_id, action_str)
                if temp_access:
                    user_level = PermissionLevel(temp_access.permission_level)
                    permission_source = 'temporary_access'

            # 5. Verificar permissões de equipe
            if user_level == PermissionLevel.NONE:
                team_permission = PermissionService._check_team_permissions(user.id, resource_str, action_str, resource_id)
                if team_permission:
                    user_level = PermissionLevel(team_permission.permission_level)
                    permission_source = 'team_permission'

            # Verificar se nível é suficiente
            required_level = PermissionService._map_action_to_level(action_str)
            has_permission = user_level.value >= required_level.value

            # Registrar auditoria detalhada
            PermissionService._audit_permission_check(
                user, resource_str, action_str, resource_id, resource_owner_id,
                user_level, required_level, has_permission, permission_source
            )

            return has_permission, required_level, user_level, permission_source

        except Exception as e:
            current_app.logger.error(f"Erro na verificação de permissão: {str(e)}")
            return False, PermissionLevel.NONE, PermissionLevel.NONE, 'error'

    @staticmethod
    def require_permission(resource_type, action, resource_owner_id=None):
        """
        Decorator para verificar permissões em endpoints

        Args:
            resource_type: Tipo do recurso
            action: Ação requerida
            resource_owner_id: ID do proprietário (opcional)
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                from flask_login import current_user

                if not current_user.is_authenticated:
                    return jsonify({
                        'success': False,
                        'error': 'Autenticação necessária'
                    }), 401

                has_permission, required_level, user_level = PermissionService.check_permission(
                    current_user, resource_type, action, resource_owner_id
                )

                if not has_permission:
                    return jsonify({
                        'success': False,
                        'error': 'Permissão negada',
                        'details': {
                            'required_level': required_level.value,
                            'user_level': user_level.value,
                            'resource_type': resource_type.value,
                            'action': action.value
                        }
                    }), 403

                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @staticmethod
    def get_user_permissions(user):
        """
        Obtém todas as permissões do usuário

        Args:
            user: Usuário para consultar permissões

        Returns:
            Dicionário com todas as permissões do usuário
        """
        try:
            user_role = user.role.value if user.role else UserRole.USER.value
            permissions = PermissionService.DEFAULT_PERMISSIONS.get(user_role, {})

            # Adicionar regras de ownership
            permissions = PermissionService._add_ownership_permissions(user, permissions)

            return {
                'user_id': user.id,
                'user_role': user_role,
                'permissions': permissions,
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            current_app.logger.error(f"Erro ao obter permissões do usuário: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def _add_ownership_permissions(user, permissions):
        """Adiciona permissões baseadas em ownership"""
        ownership_permissions = {
            ResourceType.DOCUMENT.value: {
                PermissionAction.READ.value: PermissionLevel.ADMIN,
                PermissionAction.UPDATE.value: PermissionLevel.WRITE,
            },
            ResourceType.AUDIT.value: {
                PermissionAction.READ.value: PermissionLevel.READ,
            }
        }

        # Mesclar com permissões existentes
        for resource, actions in ownership_permissions.items():
            if resource not in permissions:
                permissions[resource] = {}
            for action, level in actions.items():
                if action not in permissions[resource]:
                    permissions[resource][action] = level

        return permissions

    @staticmethod
    def can_user_access_resource(user, resource, action, resource_owner_id=None):
        """
        Verifica se usuário pode acessar recurso específico

        Args:
            user: Usuário solicitante
            resource: Instância do recurso (Document, Audit, etc.)
            action: Ação solicitada
            resource_owner_id: ID do proprietário do recurso

        Returns:
            Boolean indicando se tem acesso
        """
        try:
            # Determinar tipo do recurso
            resource_type = None
            if hasattr(resource, '__tablename__'):
                table_name = resource.__tablename__
                if table_name == 'documents':
                    resource_type = ResourceType.DOCUMENT
                elif table_name == 'audits':
                    resource_type = ResourceType.AUDIT
                elif table_name == 'non_conformities':
                    resource_type = ResourceType.NON_CONFORMITY
                elif table_name == 'capa':
                    resource_type = ResourceType.CAPA
                elif table_name == 'users':
                    resource_type = ResourceType.USER

            if not resource_type:
                return False

            # Verificar permissão
            return PermissionService.check_permission(user, resource_type, action, resource_owner_id)[0]

        except Exception as e:
            current_app.logger.error(f"Erro na verificação de acesso ao recurso: {str(e)}")
            return False

    @staticmethod
    def get_resource_owner_id(resource):
        """Obtém ID do proprietário de um recurso"""
        try:
            if hasattr(resource, 'created_by_id'):
                return resource.created_by_id
            elif hasattr(resource, 'responsible_id'):
                return resource.responsible_id
            elif hasattr(resource, 'assigned_to_id'):
                return resource.assigned_to_id
            else:
                return None
        except Exception:
            return None

    @staticmethod
    def validate_user_can_edit_resource(user, resource):
        """
        Valida se usuário pode editar recurso específico

        Args:
            user: Usuário solicitante
            resource: Recurso a ser editado

        Returns:
            Boolean indicando se pode editar
        """
        resource_owner_id = PermissionService.get_resource_owner_id(resource)

        # Verificar se é proprietário ou tem permissão global
        is_owner = resource_owner_id == user.id if resource_owner_id else False
        has_global_permission = PermissionService.check_permission(
            user, ResourceType.DOCUMENT, PermissionAction.UPDATE
        )[0] if hasattr(resource, 'title') else False

        return is_owner or has_global_permission

    @staticmethod
    def get_permission_matrix():
        """
        Obtém matriz completa de permissões do sistema

        Returns:
            Matriz de permissões formatada para documentação
        """
        matrix = {}

        for role, resources in PermissionService.DEFAULT_PERMISSIONS.items():
            matrix[role] = {}
            for resource, actions in resources.items():
                matrix[role][resource] = {
                    action: level.value for action, level in actions.items()
                }

        return {
            'permission_matrix': matrix,
            'roles': [role.value for role in UserRole],
            'resources': [resource.value for resource in ResourceType],
            'actions': [action.value for action in PermissionAction],
            'levels': [level.value for level in PermissionLevel],
            'generated_at': datetime.utcnow().isoformat()
        }

    @staticmethod
    def create_custom_role_permissions(role_name, permissions):
        """
        Cria permissões customizadas para roles específicas

        Args:
            role_name: Nome do role customizado
            permissions: Dicionário de permissões

        Returns:
            Permissões customizadas criadas
        """
        try:
            # Em produção: salvar no banco de dados
            # Por enquanto: retornar estrutura validada

            validated_permissions = PermissionService._validate_custom_permissions(permissions)

            custom_permissions = {
                'role_name': role_name,
                'permissions': validated_permissions,
                'created_at': datetime.utcnow().isoformat(),
                'is_active': True
            }

            # Auditoria
            AuditService.log_operation(
                entity_type='permission',
                entity_id=0,
                operation='create_custom_role',
                operation_details={
                    'role_name': role_name,
                    'permissions_count': len(validated_permissions)
                },
                compliance_level='critical'
            )

            return custom_permissions

        except Exception as e:
            current_app.logger.error(f"Erro ao criar permissões customizadas: {str(e)}")
            raise

    @staticmethod
    def _validate_custom_permissions(permissions):
        """Valida estrutura de permissões customizadas"""
        validated = {}

        for resource, actions in permissions.items():
            if not isinstance(actions, dict):
                raise ValueError(f"Permissões para {resource} devem ser dicionário")

            validated[resource] = {}
            for action, level in actions.items():
                # Validar que level é PermissionLevel válido
                if isinstance(level, int):
                    level_enum = PermissionLevel(level)
                elif isinstance(level, str):
                    level_enum = PermissionLevel[level.upper()]
                else:
                    level_enum = level

                validated[resource][action] = level_enum

        return validated

    @staticmethod
    def _check_db_permissions(user_role, resource_type, action):
        """Verifica permissões no banco de dados"""
        try:
            from models import Permission

            permission = Permission.query.filter_by(
                role=user_role,
                resource_type=resource_type,
                action=action,
                is_active=True
            ).first()

            # Verificar se não está expirada
            if permission and permission.is_expired():
                return None

            return permission

        except Exception as e:
            current_app.logger.error(f"Erro ao verificar permissões no banco: {str(e)}")
            return None

    @staticmethod
    def _check_temporary_access(user_id, resource_type, resource_id, action):
        """Verifica acesso temporário"""
        try:
            from models import TemporaryAccess

            temp_access = TemporaryAccess.query.filter_by(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                is_active=True
            ).first()

            if temp_access and not temp_access.is_expired():
                return temp_access

            return None

        except Exception as e:
            current_app.logger.error(f"Erro ao verificar acesso temporário: {str(e)}")
            return None

    @staticmethod
    def _check_team_permissions(user_id, resource_type, action, resource_id=None):
        """Verifica permissões de equipe"""
        try:
            from models import TeamPermission, Team

            # Obter equipes do usuário
            user_teams = Team.query.filter(Team.members.any(id=user_id)).all()

            for team in user_teams:
                # Verificar permissão específica da equipe
                team_permission = TeamPermission.query.filter_by(
                    team_id=team.id,
                    resource_type=resource_type,
                    action=action,
                    is_active=True
                ).first()

                if team_permission:
                    # Se resource_id específico, verificar se aplica
                    if resource_id is None or team_permission.resource_id is None or team_permission.resource_id == resource_id:
                        return team_permission

            return None

        except Exception as e:
            current_app.logger.error(f"Erro ao verificar permissões de equipe: {str(e)}")
            return None

    @staticmethod
    def _audit_permission_check(user, resource_type, action, resource_id, resource_owner_id,
                               user_level, required_level, granted, source):
        """Auditoria detalhada de verificação de permissão"""
        try:
            from models import AccessAudit

            audit = AccessAudit(
                user_id=user.id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                permission_used=f"{user.role.value}:{source}",
                access_granted=granted,
                ip_address=None,  # Em produção, obter do request
                user_agent=None,   # Em produção, obter do request
                method=None        # Em produção, obter do request
            )

            db.session.add(audit)

        except Exception as e:
            current_app.logger.error(f"Erro na auditoria de permissão: {str(e)}")

    @staticmethod
    def grant_temporary_access(user_id, resource_type, resource_id, action, granted_by, duration_hours=24, reason=None):
        """
        Concede acesso temporário a recurso específico

        Args:
            user_id: ID do usuário
            resource_type: Tipo do recurso
            resource_id: ID do recurso
            action: Ação permitida
            granted_by: ID do usuário que concedeu
            duration_hours: Duração em horas
            reason: Razão do acesso temporário

        Returns:
            Registro de acesso temporário criado
        """
        try:
            from models import TemporaryAccess

            # Verificar se já existe acesso ativo
            existing = TemporaryAccess.query.filter_by(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                is_active=True
            ).first()

            if existing:
                # Renovar acesso existente
                existing.expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
                existing.granted_by = granted_by
                existing.access_reason = reason
                db.session.commit()
                return existing

            # Criar novo acesso temporário
            temp_access = TemporaryAccess(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                granted_by=granted_by,
                expires_at=datetime.utcnow() + timedelta(hours=duration_hours),
                access_reason=reason
            )

            db.session.add(temp_access)
            db.session.commit()

            # Auditoria
            AuditService.log_operation(
                entity_type='temporary_access',
                entity_id=temp_access.id,
                operation='grant_temporary_access',
                operation_details={
                    'user_id': user_id,
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'action': action,
                    'duration_hours': duration_hours,
                    'reason': reason
                },
                compliance_level='critical'
            )

            return temp_access

        except Exception as e:
            current_app.logger.error(f"Erro ao conceder acesso temporário: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def revoke_temporary_access(access_id, revoked_by, reason=None):
        """Revoga acesso temporário"""
        try:
            from models import TemporaryAccess

            temp_access = TemporaryAccess.query.get(access_id)
            if not temp_access:
                raise ValueError("Acesso temporário não encontrado")

            temp_access.is_active = False

            # Auditoria
            AuditService.log_operation(
                entity_type='temporary_access',
                entity_id=access_id,
                operation='revoke_temporary_access',
                operation_details={
                    'original_user_id': temp_access.user_id,
                    'resource_type': temp_access.resource_type,
                    'resource_id': temp_access.resource_id,
                    'reason': reason
                },
                compliance_level='critical'
            )

            db.session.commit()
            return True

        except Exception as e:
            current_app.logger.error(f"Erro ao revogar acesso temporário: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def get_user_effective_permissions(user):
        """
        Obtém todas as permissões efetivas do usuário

        Args:
            user: Usuário para consultar

        Returns:
            Dicionário com permissões efetivas
        """
        try:
            permissions = {
                'role_permissions': PermissionService._get_role_permissions(user.role.value),
                'team_permissions': PermissionService._get_team_permissions(user.id),
                'temporary_permissions': PermissionService._get_temporary_permissions(user.id),
                'ownership_permissions': PermissionService._get_ownership_permissions(user.id),
                'generated_at': datetime.utcnow().isoformat()
            }

            return permissions

        except Exception as e:
            current_app.logger.error(f"Erro ao obter permissões efetivas: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def _get_role_permissions(user_role):
        """Obtém permissões baseadas no role"""
        from models import Permission

        permissions = Permission.get_user_permissions(user_role)
        return [p.to_dict() for p in permissions]

    @staticmethod
    def _get_team_permissions(user_id):
        """Obtém permissões baseadas em equipes"""
        from models import TeamPermission, Team

        # Obter equipes do usuário
        user_teams = Team.query.filter(Team.members.any(id=user_id)).all()

        team_permissions = []
        for team in user_teams:
            permissions = TeamPermission.query.filter_by(
                team_id=team.id,
                is_active=True
            ).all()
            team_permissions.extend([p.to_dict() for p in permissions])

        return team_permissions

    @staticmethod
    def _get_temporary_permissions(user_id):
        """Obtém permissões temporárias ativas"""
        from models import TemporaryAccess

        temp_permissions = TemporaryAccess.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            TemporaryAccess.expires_at > datetime.utcnow()
        ).all()

        return [{
            'id': tp.id,
            'resource_type': tp.resource_type,
            'resource_id': tp.resource_id,
            'action': tp.action,
            'expires_at': tp.expires_at.isoformat(),
            'reason': tp.access_reason,
            'usage_count': tp.usage_count
        } for tp in temp_permissions]

    @staticmethod
    def _get_ownership_permissions(user_id):
        """Obtém permissões baseadas em ownership"""
        # Recursos onde o usuário é proprietário
        ownership_perms = {
            'documents_owned': [],  # Documentos criados pelo usuário
            'audits_assigned': [],  # Auditorias atribuídas
            'capa_assigned': [],    # CAPAs atribuídos
        }

        # Em produção: consultar banco para recursos owned
        return ownership_perms

    @staticmethod
    def create_admin_interface_data():
        """Gera dados para interface administrativa de permissões"""
        try:
            from models import Permission, TeamPermission, TemporaryAccess, AccessAudit

            interface_data = {
                'roles': [role.value for role in UserRole],
                'resources': [resource.value for resource in ResourceType],
                'actions': [action.value for action in PermissionAction],
                'levels': [level.value for level in PermissionLevel],

                'permissions_count': Permission.query.filter_by(is_active=True).count(),
                'team_permissions_count': TeamPermission.query.filter_by(is_active=True).count(),
                'temporary_access_count': TemporaryAccess.query.filter_by(is_active=True).count(),
                'recent_audit_count': AccessAudit.query.filter(
                    AccessAudit.accessed_at >= datetime.utcnow() - timedelta(hours=24)
                ).count(),

                'permissions_by_role': PermissionService._get_permissions_by_role(),
                'permissions_by_resource': PermissionService._get_permissions_by_resource(),

                'generated_at': datetime.utcnow().isoformat()
            }

            return interface_data

        except Exception as e:
            current_app.logger.error(f"Erro ao gerar dados da interface administrativa: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def _get_permissions_by_role():
        """Obtém estatísticas de permissões por role"""
        from models import Permission

        stats = {}
        for role in UserRole:
            count = Permission.query.filter_by(
                role=role.value,
                is_active=True
            ).count()
            stats[role.value] = count

        return stats

    @staticmethod
    def _get_permissions_by_resource():
        """Obtém estatísticas de permissões por recurso"""
        from models import Permission

        stats = {}
        for resource in ResourceType:
            count = Permission.query.filter_by(
                resource_type=resource.value,
                is_active=True
            ).count()
            stats[resource.value] = count

        return stats

    @staticmethod
    def _map_action_to_level(action_str):
        """Mapeia string de ação para nível de permissão"""
        action_mapping = {
            'create': PermissionLevel.WRITE,  # CREATE maps to WRITE level
            'read': PermissionLevel.READ,
            'update': PermissionLevel.WRITE,
            'delete': PermissionLevel.DELETE,
            'approve': PermissionLevel.ADMIN,
            'sign': PermissionLevel.ADMIN,
            'export': PermissionLevel.READ,
            'import': PermissionLevel.WRITE,
            'configure': PermissionLevel.ADMIN
        }

        return action_mapping.get(action_str.lower(), PermissionLevel.NONE)

# Decorators de conveniência para uso comum
def require_admin(f):
    """Decorator para exigir role admin"""
    return PermissionService.require_permission(ResourceType.SYSTEM, PermissionAction.CONFIGURE)(f)

def require_manager(f):
    """Decorator para exigir role manager ou superior"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user

        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'Autenticação necessária'}), 401

        if current_user.role.value not in ['admin', 'manager']:
            return jsonify({'success': False, 'error': 'Permissão de gerente necessária'}), 403

        return f(*args, **kwargs)
    return decorated_function

def require_auditor(f):
    """Decorator para exigir role auditor ou superior"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user

        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'Autenticação necessária'}), 401

        if current_user.role.value not in ['admin', 'manager', 'auditor']:
            return jsonify({'success': False, 'error': 'Permissão de auditor necessária'}), 403

        return f(*args, **kwargs)
    return decorated_function

def can_edit_document(document):
    """Verifica se usuário atual pode editar documento"""
    from flask_login import current_user
    return PermissionService.validate_user_can_edit_resource(current_user, document)

def can_approve_capa(capa):
    """Verifica se usuário atual pode aprovar CAPA"""
    from flask_login import current_user
    return PermissionService.check_permission(
        current_user, ResourceType.CAPA, PermissionAction.APPROVE
    )[0]

# Instância global
permission_service = PermissionService()