
from flask import Blueprint, render_template, request, jsonify, make_response
from flask_login import login_required, current_user
from models import Document, Audit, NonConformity, Process, Norm, User, DocumentStatus, db
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import json

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    """Dashboard de relatórios"""
    return render_template('reports/index.html')

@reports_bp.route('/documents')
@login_required
def documents_report():
    """Relatório de documentos"""
    # Document statistics
    total_docs = Document.query.count()
    published_docs = Document.query.filter_by(status=DocumentStatus.PUBLISHED).count()
    draft_docs = Document.query.filter_by(status=DocumentStatus.DRAFT).count()
    review_docs = Document.query.filter_by(status=DocumentStatus.REVIEW).count()
    
    # Documents by category
    category_stats = db.session.query(
        Document.category, 
        func.count(Document.id)
    ).group_by(Document.category).all()
    
    # Documents by month (last 12 months)
    current_date = datetime.utcnow()
    monthly_stats = []
    
    for i in range(12):
        month_start = (current_date - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_count = Document.query.filter(
            Document.created_at >= month_start,
            Document.created_at <= month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_count
        })
    
    monthly_stats.reverse()
    
    data = {
        'total_docs': total_docs,
        'published_docs': published_docs,
        'draft_docs': draft_docs,
        'review_docs': review_docs,
        'category_stats': dict(category_stats),
        'monthly_stats': monthly_stats
    }
    
    return render_template('reports/documents.html', data=data)

@reports_bp.route('/audits')
@login_required
def audits_report():
    """Relatório de auditorias"""
    total_audits = Audit.query.count()
    completed_audits = Audit.query.filter_by(status='completed').count()
    in_progress_audits = Audit.query.filter_by(status='in_progress').count()
    
    # Audits by type
    internal_audits = Audit.query.filter_by(audit_type='internal').count()
    external_audits = Audit.query.filter_by(audit_type='external').count()
    
    # Non-conformities by severity
    critical_nc = NonConformity.query.filter_by(severity='critical').count()
    major_nc = NonConformity.query.filter_by(severity='major').count()
    minor_nc = NonConformity.query.filter_by(severity='minor').count()
    
    # NC resolution rate
    total_nc = NonConformity.query.count()
    resolved_nc = NonConformity.query.filter_by(status='resolved').count()
    resolution_rate = (resolved_nc / total_nc * 100) if total_nc > 0 else 0
    
    data = {
        'total_audits': total_audits,
        'completed_audits': completed_audits,
        'in_progress_audits': in_progress_audits,
        'internal_audits': internal_audits,
        'external_audits': external_audits,
        'critical_nc': critical_nc,
        'major_nc': major_nc,
        'minor_nc': minor_nc,
        'total_nc': total_nc,
        'resolved_nc': resolved_nc,
        'resolution_rate': resolution_rate
    }
    
    return render_template('reports/audits.html', data=data)

@reports_bp.route('/compliance')
@login_required
def compliance_report():
    """Relatório de conformidade por norma"""
    norms = Norm.query.filter_by(is_active=True).all()
    
    compliance_data = []
    
    for norm in norms:
        # Documents associated with norm
        total_docs = len(norm.documents)
        published_docs = len([d for d in norm.documents if d.status == DocumentStatus.PUBLISHED])
        doc_compliance = (published_docs / total_docs * 100) if total_docs > 0 else 0
        
        # Audits for this norm
        total_audits = len(norm.audits)
        completed_audits = len([a for a in norm.audits if a.status == 'completed'])
        audit_compliance = (completed_audits / total_audits * 100) if total_audits > 0 else 0
        
        # Non-conformities
        nc_count = sum(len(audit.non_conformities) for audit in norm.audits)
        resolved_nc_count = sum(len([nc for nc in audit.non_conformities if nc.status == 'resolved']) for audit in norm.audits)
        nc_resolution_rate = (resolved_nc_count / nc_count * 100) if nc_count > 0 else 100
        
        # Overall compliance score
        overall_score = (doc_compliance + audit_compliance + nc_resolution_rate) / 3
        
        compliance_data.append({
            'norm': norm,
            'doc_compliance': doc_compliance,
            'audit_compliance': audit_compliance,
            'nc_resolution_rate': nc_resolution_rate,
            'overall_score': overall_score,
            'total_docs': total_docs,
            'published_docs': published_docs,
            'total_audits': total_audits,
            'completed_audits': completed_audits,
            'nc_count': nc_count,
            'resolved_nc_count': resolved_nc_count
        })
    
    return render_template('reports/compliance.html', compliance_data=compliance_data)

@reports_bp.route('/users')
@login_required
def users_report():
    """Relatório de usuários e atividade"""
    if current_user.role.value not in ['admin', 'manager']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Users by role
    role_stats = db.session.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    # Recent user activity
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_activity = User.query.filter(User.last_login >= thirty_days_ago).count()
    
    data = {
        'total_users': total_users,
        'active_users': active_users,
        'role_stats': {role.value: count for role, count in role_stats},
        'recent_activity': recent_activity
    }
    
    return render_template('reports/users.html', data=data)

@reports_bp.route('/api/dashboard-data')
@login_required
def dashboard_api():
    """API for dashboard data"""
    # Quick stats
    total_docs = Document.query.count()
    total_audits = Audit.query.count()
    total_nc = NonConformity.query.count()
    total_processes = Process.query.count()
    
    # Recent activity
    recent_docs = Document.query.order_by(Document.created_at.desc()).limit(5).all()
    recent_audits = Audit.query.order_by(Audit.created_at.desc()).limit(5).all()
    
    data = {
        'stats': {
            'total_docs': total_docs,
            'total_audits': total_audits,
            'total_nc': total_nc,
            'total_processes': total_processes
        },
        'recent_activity': {
            'documents': [{'id': d.id, 'title': d.title, 'created_at': d.created_at.isoformat()} for d in recent_docs],
            'audits': [{'id': a.id, 'title': a.title, 'created_at': a.created_at.isoformat()} for a in recent_audits]
        }
    }
    
    return jsonify(data)
