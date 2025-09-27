from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import (
    Document, Audit, NonConformity, User, DocumentStatus,
    CAPA, CIPAMeeting, ImprovementCycle, OperationalEvent,
    Notification, Team, Process, Norm, EmailQueue,
    ImprovementStatus, CAPAStatus, db
)
from sqlalchemy import func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Dashboard completo com métricas dinâmicas de todas as funcionalidades"""

    # === DOCUMENTOS ===
    total_documents = Document.query.count()
    documents_draft = Document.query.filter_by(status=DocumentStatus.DRAFT).count()
    documents_in_review = Document.query.filter_by(status=DocumentStatus.REVIEW).count()
    documents_published = Document.query.filter_by(status=DocumentStatus.PUBLISHED).count()
    documents_archived = Document.query.filter_by(status=DocumentStatus.ARCHIVED).count()

    # === AUDITORIAS ===
    total_audits = Audit.query.count()
    audits_planned = Audit.query.filter_by(status='planned').count()
    audits_in_progress = Audit.query.filter_by(status='in_progress').count()
    audits_completed = Audit.query.filter_by(status='completed').count()

    # === NÃO CONFORMIDADES ===
    total_nc = NonConformity.query.count()
    nc_open = NonConformity.query.filter_by(status='open').count()
    nc_in_progress = NonConformity.query.filter_by(status='in_progress').count()
    nc_resolved = NonConformity.query.filter_by(status='resolved').count()
    nc_closed = NonConformity.query.filter_by(status='closed').count()

    # === CAPA ===
    total_capa = CAPA.query.count()
    capa_draft = CAPA.query.filter_by(status=CAPAStatus.DRAFT).count()
    capa_approved = CAPA.query.filter_by(status=CAPAStatus.APPROVED).count()
    capa_implemented = CAPA.query.filter_by(status=CAPAStatus.IMPLEMENTED).count()
    capa_verified = CAPA.query.filter_by(status=CAPAStatus.VERIFIED).count()
    capa_closed = CAPA.query.filter_by(status=CAPAStatus.CLOSED).count()

    # === CIPA ===
    total_cipa = CIPAMeeting.query.count()
    cipa_scheduled = CIPAMeeting.query.filter_by(status='scheduled').count()
    cipa_completed = CIPAMeeting.query.filter_by(status='completed').count()

    # === CICLOS DE MELHORIA (PDCA) ===
    total_improvements = ImprovementCycle.query.count()
    improvements_active = ImprovementCycle.query.filter_by(status='active').count()
    improvements_completed = ImprovementCycle.query.filter_by(status='completed').count()

    # === EVENTOS OPERACIONAIS (KANBAN) ===
    total_operational = OperationalEvent.query.count()
    operational_todo = OperationalEvent.query.filter_by(status='todo').count()
    operational_in_progress = OperationalEvent.query.filter_by(status='in_progress').count()
    operational_review = OperationalEvent.query.filter_by(status='review').count()
    operational_done = OperationalEvent.query.filter_by(status='done').count()

    # === NOTIFICAÇÕES ===
    total_notifications = Notification.query.count()
    unread_notifications = Notification.query.filter(
        (Notification.recipient_id == current_user.id) |
        (Notification.team_id.in_([t.id for t in current_user.teams])),
        Notification.is_read == False
    ).count()

    # === FILA DE E-MAILS ===
    total_emails_queued = EmailQueue.query.count()
    emails_pending = EmailQueue.query.filter_by(status='pending').count()
    emails_sent = EmailQueue.query.filter_by(status='sent').count()
    emails_failed = EmailQueue.query.filter_by(status='failed').count()

    # === EQUIPES E USUÁRIOS ===
    total_teams = Team.query.count()
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()

    # === PROCESSOS ===
    total_processes = Process.query.count()

    # === NORMAS ===
    total_norms = Norm.query.filter_by(is_active=True).count()

    # === TAREFAS PESSOAIS ===
    my_review_tasks = Document.query.filter_by(
        reviewed_by_id=current_user.id,
        status=DocumentStatus.REVIEW
    ).limit(5).all()

    my_assigned_capa = CAPA.query.filter_by(responsible_id=current_user.id).limit(5).all()

    # === ATIVIDADES RECENTES ===
    recent_audits = Audit.query.order_by(Audit.created_at.desc()).limit(3).all()
    recent_nc = NonConformity.query.order_by(NonConformity.identified_date.desc()).limit(3).all()
    recent_capa = CAPA.query.order_by(CAPA.created_at.desc()).limit(3).all()

    # === DASHBOARD COMPLETO ===
    dashboard_data = {
        # Documentos
        'documents': {
            'total': total_documents,
            'draft': documents_draft,
            'review': documents_in_review,
            'published': documents_published,
            'archived': documents_archived
        },

        # Auditorias
        'audits': {
            'total': total_audits,
            'planned': audits_planned,
            'in_progress': audits_in_progress,
            'completed': audits_completed
        },

        # Não Conformidades
        'non_conformities': {
            'total': total_nc,
            'open': nc_open,
            'in_progress': nc_in_progress,
            'resolved': nc_resolved,
            'closed': nc_closed
        },

        # CAPA
        'capa': {
            'total': total_capa,
            'draft': capa_draft,
            'approved': capa_approved,
            'implemented': capa_implemented,
            'verified': capa_verified,
            'closed': capa_closed
        },

        # CIPA
        'cipa': {
            'total': total_cipa,
            'scheduled': cipa_scheduled,
            'completed': cipa_completed
        },

        # Melhorias (PDCA)
        'improvements': {
            'total': total_improvements,
            'active': improvements_active,
            'completed': improvements_completed
        },

        # Operacional (Kanban)
        'operational': {
            'total': total_operational,
            'todo': operational_todo,
            'in_progress': operational_in_progress,
            'review': operational_review,
            'done': operational_done
        },

        # Sistema
        'system': {
            'teams': total_teams,
            'users': total_users,
            'active_users': active_users,
            'processes': total_processes,
            'norms': total_norms,
            'notifications': total_notifications,
            'unread_notifications': unread_notifications
        },

        # E-mails
        'emails': {
            'total_queued': total_emails_queued,
            'pending': emails_pending,
            'sent': emails_sent,
            'failed': emails_failed
        },

        # Tarefas pessoais
        'my_tasks': {
            'review_documents': my_review_tasks,
            'assigned_capa': my_assigned_capa
        },

        # Atividades recentes
        'recent': {
            'audits': recent_audits,
            'non_conformities': recent_nc,
            'capa': recent_capa
        },

        # Metadados
        'last_update': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'user_name': current_user.full_name,
        'user_role': current_user.role.value.title()
    }

    return render_template('dashboard.html', data=dashboard_data)

@main_bp.route('/api/dashboard-metrics')
@login_required
def dashboard_metrics():
    """API endpoint for real-time dashboard metrics - TODAS as funcionalidades"""

    # === MÉTRICAS DINÂMICAS COMPLETAS ===

    # Documentos por status
    document_stats = db.session.query(
        Document.status,
        func.count(Document.id)
    ).group_by(Document.status).all()

    # Auditorias por status
    audit_stats = db.session.query(
        Audit.status,
        func.count(Audit.id)
    ).group_by(Audit.status).all()

    # NC por status
    nc_stats = db.session.query(
        NonConformity.status,
        func.count(NonConformity.id)
    ).group_by(NonConformity.status).all()

    # CAPA por status
    capa_stats = db.session.query(
        CAPA.status,
        func.count(CAPA.id)
    ).group_by(CAPA.status).all()

    # Melhorias por status
    improvement_stats = db.session.query(
        ImprovementCycle.status,
        func.count(ImprovementCycle.id)
    ).group_by(ImprovementCycle.status).all()

    # Eventos operacionais por status
    operational_stats = db.session.query(
        OperationalEvent.status,
        func.count(OperationalEvent.id)
    ).group_by(OperationalEvent.status).all()

    # === MÉTRICAS TEMPORAIS ===
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # Atividades recentes (últimos 30 dias)
    recent_documents = Document.query.filter(Document.created_at >= thirty_days_ago).count()
    recent_audits = Audit.query.filter(Audit.created_at >= thirty_days_ago).count()
    recent_nc = NonConformity.query.filter(NonConformity.created_at >= thirty_days_ago).count()
    recent_capa = CAPA.query.filter(CAPA.created_at >= thirty_days_ago).count()

    # Usuários ativos (últimos 30 dias)
    active_users = User.query.filter(User.last_login >= thirty_days_ago).count()

    # === NOTIFICAÇÕES DO USUÁRIO ===
    user_unread_notifications = Notification.query.filter(
        (Notification.recipient_id == current_user.id) |
        (Notification.team_id.in_([t.id for t in current_user.teams])),
        Notification.is_read == False
    ).count()

    # === TAREFAS PESSOAIS ===
    my_pending_reviews = Document.query.filter_by(
        reviewed_by_id=current_user.id,
        status=DocumentStatus.REVIEW
    ).count()

    my_assigned_capa = CAPA.query.filter_by(responsible_id=current_user.id).count()

    # === MÉTRICAS COMPLETAS ===
    metrics = {
        # === DOCUMENTOS ===
        'documents': {
            'total': Document.query.count(),
            'draft': Document.query.filter_by(status=DocumentStatus.DRAFT).count(),
            'review': Document.query.filter_by(status=DocumentStatus.REVIEW).count(),
            'published': Document.query.filter_by(status=DocumentStatus.PUBLISHED).count(),
            'archived': Document.query.filter_by(status=DocumentStatus.ARCHIVED).count(),
            'stats': [{'status': status.value, 'count': count} for status, count in document_stats],
            'recent': recent_documents
        },

        # === AUDITORIAS ===
        'audits': {
            'total': Audit.query.count(),
            'planned': Audit.query.filter_by(status='planned').count(),
            'in_progress': Audit.query.filter_by(status='in_progress').count(),
            'completed': Audit.query.filter_by(status='completed').count(),
            'stats': [{'status': status, 'count': count} for status, count in audit_stats],
            'recent': recent_audits
        },

        # === NÃO CONFORMIDADES ===
        'non_conformities': {
            'total': NonConformity.query.count(),
            'open': NonConformity.query.filter_by(status='open').count(),
            'in_progress': NonConformity.query.filter_by(status='in_progress').count(),
            'resolved': NonConformity.query.filter_by(status='resolved').count(),
            'closed': NonConformity.query.filter_by(status='closed').count(),
            'stats': [{'status': status, 'count': count} for status, count in nc_stats],
            'recent': recent_nc
        },

        # === CAPA ===
        'capa': {
            'total': CAPA.query.count(),
            'draft': CAPA.query.filter_by(status=CAPAStatus.DRAFT).count(),
            'approved': CAPA.query.filter_by(status=CAPAStatus.APPROVED).count(),
            'implemented': CAPA.query.filter_by(status=CAPAStatus.IMPLEMENTED).count(),
            'verified': CAPA.query.filter_by(status=CAPAStatus.VERIFIED).count(),
            'closed': CAPA.query.filter_by(status=CAPAStatus.CLOSED).count(),
            'stats': [{'status': status.value, 'count': count} for status, count in capa_stats],
            'recent': recent_capa
        },

        # === CIPA ===
        'cipa': {
            'total': CIPAMeeting.query.count(),
            'scheduled': CIPAMeeting.query.filter_by(status='scheduled').count(),
            'completed': CIPAMeeting.query.filter_by(status='completed').count()
        },

        # === MELHORIAS (PDCA) ===
        'improvements': {
            'total': ImprovementCycle.query.count(),
            'active': ImprovementCycle.query.filter_by(status='active').count(),
            'completed': ImprovementCycle.query.filter_by(status='completed').count(),
            'stats': [{'status': status, 'count': count} for status, count in improvement_stats]
        },

        # === OPERACIONAL (KANBAN) ===
        'operational': {
            'total': OperationalEvent.query.count(),
            'todo': OperationalEvent.query.filter_by(status='todo').count(),
            'in_progress': OperationalEvent.query.filter_by(status='in_progress').count(),
            'review': OperationalEvent.query.filter_by(status='review').count(),
            'done': OperationalEvent.query.filter_by(status='done').count(),
            'stats': [{'status': status, 'count': count} for status, count in operational_stats]
        },

        # === SISTEMA ===
        'system': {
            'teams': Team.query.count(),
            'users': User.query.count(),
            'active_users': active_users,
            'processes': Process.query.count(),
            'norms': Norm.query.filter_by(is_active=True).count(),
            'total_notifications': Notification.query.count()
        },

        # === E-MAILS ===
        'emails': {
            'total_queued': EmailQueue.query.count(),
            'pending': EmailQueue.query.filter_by(status='pending').count(),
            'sent': EmailQueue.query.filter_by(status='sent').count(),
            'failed': EmailQueue.query.filter_by(status='failed').count()
        },

        # === USUÁRIO ATUAL ===
        'user': {
            'unread_notifications': user_unread_notifications,
            'pending_reviews': my_pending_reviews,
            'assigned_capa': my_assigned_capa,
            'name': current_user.full_name,
            'role': current_user.role.value
        },

        # === METADADOS ===
        'last_update': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'timestamp': datetime.utcnow().isoformat(),
        'server_status': 'online'
    }

    return jsonify(metrics)

@main_bp.route('/process-emails', methods=['POST'])
@login_required
def process_emails_ajax():
    """Processar fila de e-mails via AJAX"""
    try:
        from email_service import email_service
        result = email_service.process_email_queue()

        return jsonify({
            'success': True,
            'message': f'{result["sent"]} e-mails enviados, {result["failed"]} falharam',
            'sent': result['sent'],
            'failed': result['failed']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao processar e-mails: {str(e)}'
        }), 500