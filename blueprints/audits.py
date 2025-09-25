from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Audit, NonConformity, Norm, User, AuditType, db
from datetime import datetime

audits_bp = Blueprint('audits', __name__)

@audits_bp.route('/')
@login_required
def index():
    """Lista todas as auditorias"""
    audit_type = request.args.get('type')
    status = request.args.get('status')
    norm_id = request.args.get('norm_id')
    
    query = Audit.query
    
    if audit_type:
        query = query.filter_by(audit_type=AuditType(audit_type))
    
    if status:
        query = query.filter_by(status=status)
    
    if norm_id:
        query = query.filter_by(norm_id=norm_id)
    
    audits = query.order_by(Audit.created_at.desc()).all()
    norms = Norm.query.filter_by(is_active=True).all()
    
    return render_template('audits/index.html', audits=audits, norms=norms)

@audits_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Criar nova auditoria interna/externa"""
    if request.method == 'POST':
        title = request.form['title']
        audit_type = AuditType(request.form['audit_type'])
        norm_id = request.form.get('norm_id')
        location = request.form.get('location', '')
        planned_date = request.form.get('planned_date')
        assigned_auditor_id = request.form.get('assigned_auditor_id')
        responsible_id = request.form.get('responsible_id')
        objectives = request.form.get('objectives', '')
        scope = request.form.get('scope', '')
        
        audit = Audit(
            title=title,
            audit_type=audit_type,
            norm_id=norm_id if norm_id else None,
            location=location,
            planned_date=datetime.strptime(planned_date, '%Y-%m-%d').date() if planned_date else None,
            assigned_auditor_id=assigned_auditor_id if assigned_auditor_id else None,
            responsible_id=responsible_id if responsible_id else None,
            objectives=objectives,
            scope=scope,
            status='planned'
        )
        
        db.session.add(audit)
        db.session.commit()
        
        flash('Auditoria criada com sucesso!', 'success')
        return redirect(url_for('audits.view', id=audit.id))
    
    # GET request
    norms = Norm.query.filter_by(is_active=True).all()
    users = User.query.filter_by(is_active=True).all()
    auditors = User.query.filter(User.role.in_(['admin', 'auditor'])).all()
    
    return render_template('audits/create.html', norms=norms, users=users, auditors=auditors)

@audits_bp.route('/<int:id>')
@login_required
def view(id):
    """Visualizar auditoria com progresso visual"""
    audit = Audit.query.get_or_404(id)
    
    # Count non-conformities by severity
    nc_stats = {
        'total': len(audit.non_conformities),
        'critical': len([nc for nc in audit.non_conformities if nc.severity == 'critical']),
        'major': len([nc for nc in audit.non_conformities if nc.severity == 'major']),
        'minor': len([nc for nc in audit.non_conformities if nc.severity == 'minor']),
        'open': len([nc for nc in audit.non_conformities if nc.status == 'open']),
        'resolved': len([nc for nc in audit.non_conformities if nc.status == 'resolved'])
    }
    
    return render_template('audits/view.html', audit=audit, nc_stats=nc_stats)

@audits_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar auditoria"""
    audit = Audit.query.get_or_404(id)
    
    # Check permissions
    if current_user.role.value not in ['admin', 'manager', 'auditor']:
        flash('Sem permissão para editar auditorias.', 'error')
        return redirect(url_for('audits.view', id=id))
    
    if request.method == 'POST':
        audit.title = request.form['title']
        audit.audit_type = AuditType(request.form['audit_type'])
        audit.norm_id = request.form.get('norm_id') if request.form.get('norm_id') else None
        audit.location = request.form.get('location', '')
        audit.planned_date = datetime.strptime(request.form['planned_date'], '%Y-%m-%d').date() if request.form.get('planned_date') else None
        audit.actual_date = datetime.strptime(request.form['actual_date'], '%Y-%m-%d').date() if request.form.get('actual_date') else None
        audit.assigned_auditor_id = request.form.get('assigned_auditor_id') if request.form.get('assigned_auditor_id') else None
        audit.responsible_id = request.form.get('responsible_id') if request.form.get('responsible_id') else None
        audit.objectives = request.form.get('objectives', '')
        audit.scope = request.form.get('scope', '')
        audit.findings = request.form.get('findings', '')
        audit.conclusion = request.form.get('conclusion', '')
        audit.status = request.form.get('status', 'planned')
        audit.progress_percentage = int(request.form.get('progress_percentage', 0))
        audit.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Auditoria atualizada com sucesso!', 'success')
        return redirect(url_for('audits.view', id=id))
    
    norms = Norm.query.filter_by(is_active=True).all()
    users = User.query.filter_by(is_active=True).all()
    auditors = User.query.filter(User.role.in_(['admin', 'auditor'])).all()
    
    return render_template('audits/edit.html', audit=audit, norms=norms, users=users, auditors=auditors)

@audits_bp.route('/<int:id>/non-conformities')
@login_required
def non_conformities(id):
    """Listar não conformidades da auditoria"""
    audit = Audit.query.get_or_404(id)
    
    severity_filter = request.args.get('severity')
    status_filter = request.args.get('status')
    
    query = NonConformity.query.filter_by(audit_id=id)
    
    if severity_filter:
        query = query.filter_by(severity=severity_filter)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    non_conformities = query.order_by(NonConformity.identified_date.desc()).all()
    
    return render_template('audits/non_conformities.html', audit=audit, non_conformities=non_conformities)

@audits_bp.route('/<int:id>/add-non-conformity', methods=['GET', 'POST'])
@login_required
def add_non_conformity(id):
    """Adicionar não conformidade à auditoria"""
    audit = Audit.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        severity = request.form['severity']
        requirement = request.form.get('requirement', '')
        target_resolution_date = request.form.get('target_resolution_date')
        assigned_to_id = request.form.get('assigned_to_id')
        
        nc = NonConformity(
            audit_id=id,
            title=title,
            description=description,
            severity=severity,
            requirement=requirement,
            target_resolution_date=datetime.strptime(target_resolution_date, '%Y-%m-%d').date() if target_resolution_date else None,
            identified_by_id=current_user.id,
            assigned_to_id=assigned_to_id if assigned_to_id else None
        )
        
        db.session.add(nc)
        db.session.commit()
        
        flash('Não conformidade registrada com sucesso!', 'success')
        return redirect(url_for('audits.view', id=id))
    
    users = User.query.filter_by(is_active=True).all()
    return render_template('audits/add_non_conformity.html', audit=audit, users=users)

@audits_bp.route('/progress-by-unit')
@login_required
def progress_by_unit():
    """Progresso visual por unidade/norma"""
    norms = Norm.query.filter_by(is_active=True).all()
    
    progress_data = []
    
    for norm in norms:
        total_audits = Audit.query.filter_by(norm_id=norm.id).count()
        completed_audits = Audit.query.filter_by(norm_id=norm.id, status='completed').count()
        in_progress_audits = Audit.query.filter_by(norm_id=norm.id, status='in_progress').count()
        
        # Total non-conformities for this norm
        total_nc = db.session.query(NonConformity).join(Audit).filter(Audit.norm_id == norm.id).count()
        resolved_nc = db.session.query(NonConformity).join(Audit).filter(Audit.norm_id == norm.id, NonConformity.status == 'resolved').count()
        
        progress_percentage = (completed_audits / total_audits * 100) if total_audits > 0 else 0
        nc_resolution_rate = (resolved_nc / total_nc * 100) if total_nc > 0 else 100
        
        progress_data.append({
            'norm': norm,
            'total_audits': total_audits,
            'completed_audits': completed_audits,
            'in_progress_audits': in_progress_audits,
            'progress_percentage': progress_percentage,
            'total_nc': total_nc,
            'resolved_nc': resolved_nc,
            'nc_resolution_rate': nc_resolution_rate,
            'overall_score': (progress_percentage + nc_resolution_rate) / 2
        })
    
    return render_template('audits/progress_by_unit.html', progress_data=progress_data)

@audits_bp.route('/api/audit-metrics')
@login_required
def audit_metrics_api():
    """API endpoint para métricas de auditoria"""
    total_audits = Audit.query.count()
    completed_audits = Audit.query.filter_by(status='completed').count()
    in_progress_audits = Audit.query.filter_by(status='in_progress').count()
    
    total_nc = NonConformity.query.count()
    open_nc = NonConformity.query.filter_by(status='open').count()
    resolved_nc = NonConformity.query.filter_by(status='resolved').count()
    
    metrics = {
        'audits': {
            'total': total_audits,
            'completed': completed_audits,
            'in_progress': in_progress_audits,
            'completion_rate': (completed_audits / total_audits * 100) if total_audits > 0 else 0
        },
        'non_conformities': {
            'total': total_nc,
            'open': open_nc,
            'resolved': resolved_nc,
            'resolution_rate': (resolved_nc / total_nc * 100) if total_nc > 0 else 0
        }
    }
    
    return jsonify(metrics)