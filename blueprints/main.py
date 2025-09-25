from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import Document, Audit, NonConformity, User, DocumentStatus
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    # Dashboard metrics as per specification
    total_documents = Document.query.count()
    documents_in_review = Document.query.filter_by(status=DocumentStatus.REVIEW).count()
    documents_published = Document.query.filter_by(status=DocumentStatus.PUBLISHED).count()
    
    # My tasks - documents assigned to current user
    my_review_tasks = Document.query.filter_by(
        reviewed_by_id=current_user.id, 
        status=DocumentStatus.REVIEW
    ).limit(5).all()
    
    # Recent audits
    recent_audits = Audit.query.order_by(Audit.created_at.desc()).limit(5).all()
    
    # Open non-conformities
    open_non_conformities = NonConformity.query.filter_by(status='open').count()
    
    # Dashboard data for charts
    dashboard_data = {
        'total_documents': total_documents,
        'documents_in_review': documents_in_review,
        'documents_published': documents_published,
        'open_non_conformities': open_non_conformities,
        'my_review_tasks': my_review_tasks,
        'recent_audits': recent_audits
    }
    
    return render_template('dashboard.html', data=dashboard_data)

@main_bp.route('/api/dashboard-metrics')
@login_required
def dashboard_metrics():
    """API endpoint for real-time dashboard metrics"""
    
    # Document metrics by status
    document_stats = db.session.query(
        Document.status, 
        func.count(Document.id)
    ).group_by(Document.status).all()
    
    # Audit progress by month
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_audits = Audit.query.filter(Audit.created_at >= thirty_days_ago).count()
    
    # User activity metrics
    active_users = User.query.filter(User.last_login >= thirty_days_ago).count()
    
    metrics = {
        'document_stats': [{'status': status.value, 'count': count} for status, count in document_stats],
        'recent_audits': recent_audits,
        'active_users': active_users,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(metrics)