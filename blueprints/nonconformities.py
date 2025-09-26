
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import NonConformity, Audit, User, db
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
