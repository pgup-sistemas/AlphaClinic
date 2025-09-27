
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import NonConformity, Audit, User, CAPA, CAPAStatus, CAPAType, db
from datetime import datetime

nonconformities_bp = Blueprint('nonconformities', __name__)

@nonconformities_bp.route('/')
@login_required
def index():
    """Lista todas as não conformidades"""
    status_filter = request.args.get('status')
    severity_filter = request.args.get('severity')
    assigned_to = request.args.get('assigned_to')
    
    query = NonConformity.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if severity_filter:
        query = query.filter_by(severity=severity_filter)
    
    if assigned_to:
        query = query.filter_by(assigned_to_id=assigned_to)
    
    non_conformities = query.order_by(NonConformity.identified_date.desc()).all()
    users = User.query.filter_by(is_active=True).all()
    
    return render_template('nonconformities/index.html', 
                         non_conformities=non_conformities, 
                         users=users)

@nonconformities_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Criar nova não conformidade"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        severity = request.form['severity']
        requirement = request.form.get('requirement', '')
        audit_id = request.form.get('audit_id')
        target_resolution_date = request.form.get('target_resolution_date')
        assigned_to_id = request.form.get('assigned_to_id')
        
        nc = NonConformity(
            title=title,
            description=description,
            severity=severity,
            requirement=requirement,
            audit_id=audit_id if audit_id else None,
            target_resolution_date=datetime.strptime(target_resolution_date, '%Y-%m-%d').date() if target_resolution_date else None,
            identified_by_id=current_user.id,
            assigned_to_id=assigned_to_id if assigned_to_id else None
        )
        
        db.session.add(nc)
        db.session.commit()
        
        flash('Não conformidade registrada com sucesso!', 'success')
        return redirect(url_for('nonconformities.view', id=nc.id))
    
    audits = Audit.query.all()
    users = User.query.filter_by(is_active=True).all()
    return render_template('nonconformities/create.html', audits=audits, users=users)

@nonconformities_bp.route('/<int:id>')
@login_required
def view(id):
    """Visualizar não conformidade"""
    nc = NonConformity.query.get_or_404(id)
    return render_template('nonconformities/view.html', nc=nc)

@nonconformities_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    """Atualizar status da não conformidade"""
    nc = NonConformity.query.get_or_404(id)
    
    new_status = request.form.get('status')
    resolution_notes = request.form.get('resolution_notes')
    
    if new_status in ['open', 'in_progress', 'resolved', 'closed']:
        nc.status = new_status
        
        if new_status == 'resolved' and not nc.actual_resolution_date:
            nc.actual_resolution_date = datetime.utcnow().date()
        
        db.session.commit()
        flash(f'Status atualizado para: {new_status}', 'success')
    
    return redirect(url_for('nonconformities.view', id=id))

@nonconformities_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard de não conformidades"""
    # Statistics
    total_nc = NonConformity.query.count()
    open_nc = NonConformity.query.filter_by(status='open').count()
    overdue_nc = NonConformity.query.filter(
        NonConformity.target_resolution_date < datetime.utcnow().date(),
        NonConformity.status.in_(['open', 'in_progress'])
    ).count()
    
    # By severity
    critical_nc = NonConformity.query.filter_by(severity='critical').count()
    major_nc = NonConformity.query.filter_by(severity='major').count()
    minor_nc = NonConformity.query.filter_by(severity='minor').count()
    
    # Recent NCs
    recent_nc = NonConformity.query.order_by(NonConformity.identified_date.desc()).limit(10).all()
    
    stats = {
        'total_nc': total_nc,
        'open_nc': open_nc,
        'overdue_nc': overdue_nc,
        'critical_nc': critical_nc,
        'major_nc': major_nc,
        'minor_nc': minor_nc,
        'recent_nc': recent_nc
    }

    return render_template('nonconformities/dashboard.html', stats=stats)

# ==================== CAPA MANAGEMENT ====================

@nonconformities_bp.route('/<int:id>/capa/create', methods=['GET', 'POST'])
@login_required
def create_capa(id):
    """Criar plano de ação CAPA para uma não conformidade"""
    nc = NonConformity.query.get_or_404(id)

    # Check if CAPA already exists
    existing_capa = CAPA.query.filter_by(non_conformity_id=id).first()
    if existing_capa:
        flash('Já existe um plano CAPA para esta não conformidade.', 'warning')
        return redirect(url_for('nonconformities.view_capa', nc_id=id, capa_id=existing_capa.id))

    if request.method == 'POST':
        capa_type = CAPAType(request.form['capa_type'])

        # Create CAPA
        capa = CAPA(
            non_conformity_id=id,
            capa_type=capa_type,
            what=request.form['what'],
            why=request.form['why'],
            who=request.form['who'],
            when=datetime.strptime(request.form['when'], '%Y-%m-%d').date(),
            how=request.form['how'],
            how_much=request.form.get('how_much'),
            priority=request.form.get('priority', 'medium'),
            target_completion_date=datetime.strptime(request.form['target_completion_date'], '%Y-%m-%d').date() if request.form.get('target_completion_date') else None,
            created_by_id=current_user.id,
            responsible_id=request.form.get('responsible_id') if request.form.get('responsible_id') else None
        )

        # Generate reference number
        capa.generate_reference_number()

        db.session.add(capa)
        db.session.commit()

        # Send notification to assigned user
        if capa.responsible_id:
            try:
                from email_service import notification_service
                notification_service.send_notification(
                    user_id=capa.responsible_id,
                    event_type='capa_created',
                    context_data={
                        'capa_reference': capa.reference,
                        'capa_title': capa.title,
                        'capa_type': 'Corretivo' if capa.capa_type.value == 'corrective' else 'Preventivo',
                        'capa_priority': capa.priority.title(),
                        'nc_title': nc.title,
                        'capa_url': url_for('nonconformities.view_capa', nc_id=id, capa_id=capa.id, _external=True)
                    },
                    priority='high'
                )
            except Exception as e:
                print(f"Warning: Could not send CAPA creation notification: {e}")

        flash('Plano CAPA criado com sucesso!', 'success')
        return redirect(url_for('nonconformities.view_capa', nc_id=id, capa_id=capa.id))

    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('nonconformities/capa/create.html', nc=nc, users=users, CAPAType=CAPAType)

@nonconformities_bp.route('/<int:nc_id>/capa/<int:capa_id>')
@login_required
def view_capa(nc_id, capa_id):
    """Visualizar plano CAPA"""
    nc = NonConformity.query.get_or_404(nc_id)
    capa = CAPA.query.get_or_404(capa_id)

    if capa.non_conformity_id != nc_id:
        flash('CAPA não pertence a esta não conformidade.', 'error')
        return redirect(url_for('nonconformities.view', id=nc_id))

    return render_template('nonconformities/capa/view.html', nc=nc, capa=capa)

@nonconformities_bp.route('/<int:nc_id>/capa/<int:capa_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_capa(nc_id, capa_id):
    """Editar plano CAPA"""
    nc = NonConformity.query.get_or_404(nc_id)
    capa = CAPA.query.get_or_404(capa_id)

    if capa.non_conformity_id != nc_id:
        flash('CAPA não pertence a esta não conformidade.', 'error')
        return redirect(url_for('nonconformities.view', id=nc_id))

    # Check permissions - only creator or responsible can edit
    if current_user.id not in [capa.created_by_id, capa.responsible_id] and current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para editar este CAPA.', 'error')
        return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

    if request.method == 'POST':
        capa.what = request.form['what']
        capa.why = request.form['why']
        capa.who = request.form['who']
        capa.when = datetime.strptime(request.form['when'], '%Y-%m-%d').date()
        capa.how = request.form['how']
        capa.how_much = request.form.get('how_much')
        capa.priority = request.form.get('priority', 'medium')
        capa.target_completion_date = datetime.strptime(request.form['target_completion_date'], '%Y-%m-%d').date() if request.form.get('target_completion_date') else None
        capa.responsible_id = request.form.get('responsible_id') if request.form.get('responsible_id') else None

        db.session.commit()
        flash('Plano CAPA atualizado com sucesso!', 'success')
        return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('nonconformities/capa/edit.html', nc=nc, capa=capa, users=users)

@nonconformities_bp.route('/<int:nc_id>/capa/<int:capa_id>/approve', methods=['POST'])
@login_required
def approve_capa(nc_id, capa_id):
    """Aprovar plano CAPA"""
    nc = NonConformity.query.get_or_404(nc_id)
    capa = CAPA.query.get_or_404(capa_id)

    if capa.non_conformity_id != nc_id:
        flash('CAPA não pertence a esta não conformidade.', 'error')
        return redirect(url_for('nonconformities.view', id=nc_id))

    # Check permissions - only managers and admins can approve
    if current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para aprovar CAPA.', 'error')
        return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

    if capa.status != CAPAStatus.DRAFT:
        flash('CAPA já foi aprovado.', 'warning')
        return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

    capa.status = CAPAStatus.APPROVED
    capa.approved_by_id = current_user.id
    capa.approved_at = datetime.utcnow()

    db.session.commit()
    flash('Plano CAPA aprovado com sucesso!', 'success')
    return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

@nonconformities_bp.route('/<int:nc_id>/capa/<int:capa_id>/implement', methods=['GET', 'POST'])
@login_required
def implement_capa(nc_id, capa_id):
    """Registrar implementação do CAPA"""
    nc = NonConformity.query.get_or_404(nc_id)
    capa = CAPA.query.get_or_404(capa_id)

    if capa.non_conformity_id != nc_id:
        flash('CAPA não pertence a esta não conformidade.', 'error')
        return redirect(url_for('nonconformities.view', id=nc_id))

    # Check permissions
    if current_user.id != capa.responsible_id and current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para registrar implementação.', 'error')
        return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

    if request.method == 'POST':
        capa.status = CAPAStatus.IMPLEMENTED
        capa.implemented_by_id = current_user.id
        capa.implemented_at = datetime.utcnow()
        capa.implementation_notes = request.form.get('implementation_notes')
        capa.actual_completion_date = datetime.utcnow().date()

        db.session.commit()
        flash('Implementação do CAPA registrada com sucesso!', 'success')
        return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

    return render_template('nonconformities/capa/implement.html', nc=nc, capa=capa)

@nonconformities_bp.route('/<int:nc_id>/capa/<int:capa_id>/verify', methods=['GET', 'POST'])
@login_required
def verify_capa(nc_id, capa_id):
    """Verificar efetividade do CAPA"""
    nc = NonConformity.query.get_or_404(nc_id)
    capa = CAPA.query.get_or_404(capa_id)

    if capa.non_conformity_id != nc_id:
        flash('CAPA não pertence a esta não conformidade.', 'error')
        return redirect(url_for('nonconformities.view', id=nc_id))

    # Check permissions - only managers and admins can verify
    if current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para verificar CAPA.', 'error')
        return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

    if request.method == 'POST':
        capa.status = CAPAStatus.VERIFIED
        capa.verified_by_id = current_user.id
        capa.verified_at = datetime.utcnow()
        capa.verification_method = request.form.get('verification_method')
        capa.verification_result = request.form.get('verification_result')
        capa.effectiveness_rating = int(request.form.get('effectiveness_rating', 3))
        capa.verification_date = datetime.utcnow().date()

        # If effective, close the CAPA
        if request.form.get('close_capa') == 'true':
            capa.status = CAPAStatus.CLOSED

        db.session.commit()
        flash('Verificação do CAPA registrada com sucesso!', 'success')
        return redirect(url_for('nonconformities.view_capa', nc_id=nc_id, capa_id=capa_id))

    return render_template('nonconformities/capa/verify.html', nc=nc, capa=capa)
