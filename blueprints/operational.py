from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import (
    CIPAMeeting, ImprovementCycle, Notification, OperationalEvent,
    ImprovementStatus, NotificationType, User, Team, db
)
from datetime import datetime, timedelta
import json

operational_bp = Blueprint('operational', __name__)

# Make datetime available in templates
@operational_bp.context_processor
def inject_datetime():
    return {'datetime': datetime}

# ==================== CIPA MANAGEMENT ====================

@operational_bp.route('/cipa')
@login_required
def cipa_index():
    """Lista todas as reuniões CIPA"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')

    query = CIPAMeeting.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    cipa_meetings = query.order_by(CIPAMeeting.meeting_date.desc()).paginate(page=page, per_page=10)

    return render_template('operational/cipa/index.html', cipa_meetings=cipa_meetings)

@operational_bp.route('/cipa/create', methods=['GET', 'POST'])
@login_required
def cipa_create():
    """Criar nova reunião CIPA"""
    if request.method == 'POST':
        title = request.form['title']
        meeting_date = datetime.strptime(request.form['meeting_date'], '%Y-%m-%dT%H:%M')
        location = request.form.get('location')
        agenda = request.form.get('agenda')
        chairperson_id = request.form.get('chairperson_id')
        secretary_id = request.form.get('secretary_id')
        attendee_ids = request.form.getlist('attendee_ids')

        meeting = CIPAMeeting(
            title=title,
            meeting_date=meeting_date,
            location=location,
            agenda=agenda,
            chairperson_id=chairperson_id,
            secretary_id=secretary_id
        )

        # Add attendees
        if attendee_ids:
            attendees = User.query.filter(User.id.in_(attendee_ids)).all()
            meeting.attendees.extend(attendees)

        db.session.add(meeting)
        db.session.commit()

        flash('Reunião CIPA criada com sucesso!', 'success')
        return redirect(url_for('operational.cipa_view', id=meeting.id))

    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('operational/cipa/create.html', users=users)

@operational_bp.route('/cipa/<int:id>')
@login_required
def cipa_view(id):
    """Visualizar reunião CIPA"""
    meeting = CIPAMeeting.query.get_or_404(id)
    return render_template('operational/cipa/view.html', meeting=meeting)

@operational_bp.route('/cipa/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def cipa_edit(id):
    """Editar reunião CIPA"""
    meeting = CIPAMeeting.query.get_or_404(id)

    if request.method == 'POST':
        meeting.title = request.form['title']
        meeting.meeting_date = datetime.strptime(request.form['meeting_date'], '%Y-%m-%dT%H:%M')
        meeting.location = request.form.get('location')
        meeting.agenda = request.form.get('agenda')
        meeting.minutes = request.form.get('minutes')
        meeting.decisions = request.form.get('decisions')
        meeting.chairperson_id = request.form.get('chairperson_id')
        meeting.secretary_id = request.form.get('secretary_id')

        # Update attendees
        attendee_ids = request.form.getlist('attendee_ids')
        meeting.attendees.clear()
        if attendee_ids:
            attendees = User.query.filter(User.id.in_(attendee_ids)).all()
            meeting.attendees.extend(attendees)

        db.session.commit()
        flash('Reunião CIPA atualizada com sucesso!', 'success')
        return redirect(url_for('operational.cipa_view', id=id))

    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('operational/cipa/edit.html', meeting=meeting, users=users)

# ==================== IMPROVEMENT CYCLES (PDCA) ====================

# Redirect Portuguese URLs to English ones
@operational_bp.route('/melhorias')
@login_required
def melhorias_redirect():
    return redirect(url_for('operational.improvements_index'))

@operational_bp.route('/melhorias/criar')
@login_required
def melhorias_criar_redirect():
    return redirect(url_for('operational.improvements_create'))

@operational_bp.route('/improvements')
@login_required
def improvements_index():
    """Lista todos os ciclos de melhoria"""
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')

    query = ImprovementCycle.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if category_filter:
        query = query.filter_by(category=category_filter)

    improvements = query.order_by(ImprovementCycle.created_at.desc()).all()

    return render_template('operational/improvements/index.html', improvements=improvements)

@operational_bp.route('/improvements/create', methods=['GET', 'POST'])
@login_required
def improvements_create():
    """Criar novo ciclo de melhoria (PDCA)"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        category = request.form.get('category')
        priority = request.form.get('priority', 'medium')
        responsible_id = request.form.get('responsible_id')
        target_completion_date = request.form.get('target_completion_date')

        improvement = ImprovementCycle(
            title=title,
            description=description,
            category=category,
            priority=priority,
            responsible_id=responsible_id,
            created_by_id=current_user.id
        )

        if target_completion_date:
            improvement.target_completion_date = datetime.strptime(target_completion_date, '%Y-%m-%d').date()

        db.session.add(improvement)
        db.session.commit()

        flash('Ciclo de melhoria criado com sucesso!', 'success')
        return redirect(url_for('operational.improvements_view', id=improvement.id))

    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('operational/improvements/create.html', users=users)

@operational_bp.route('/improvements/<int:id>')
@login_required
def improvements_view(id):
    """Visualizar ciclo de melhoria"""
    improvement = ImprovementCycle.query.get_or_404(id)
    return render_template('operational/improvements/view.html', improvement=improvement)

@operational_bp.route('/improvements/<int:id>/update-phase', methods=['POST'])
@login_required
def improvements_update_phase(id):
    """Atualizar fase do PDCA"""
    improvement = ImprovementCycle.query.get_or_404(id)

    new_phase = request.form.get('phase')
    phase_description = request.form.get('description')

    if new_phase in ['plan', 'do', 'check', 'act', 'completed']:
        improvement.current_phase = ImprovementStatus(new_phase)

        # Update the appropriate description field
        if new_phase == 'plan':
            improvement.plan_description = phase_description
        elif new_phase == 'do':
            improvement.do_description = phase_description
        elif new_phase == 'check':
            improvement.check_description = phase_description
        elif new_phase == 'act':
            improvement.act_description = phase_description

        # Mark as completed if reaching ACT phase
        if new_phase == 'completed':
            improvement.status = 'completed'
            improvement.actual_completion_date = datetime.utcnow().date()

        db.session.commit()
        flash(f'Fase {new_phase.upper()} atualizada com sucesso!', 'success')

    return redirect(url_for('operational.improvements_view', id=id))

# ==================== NOTIFICATIONS ====================

# Redirect Portuguese URLs to English ones
@operational_bp.route('/notificações')
@login_required
def notificacoes_redirect():
    return redirect(url_for('operational.notifications_index'))

@operational_bp.route('/notifications')
@login_required
def notifications_index():
    """Lista todas as notificações"""
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type')
    unread_only = request.args.get('unread', 'false') == 'true'

    query = Notification.query.filter(
        (Notification.recipient_id == current_user.id) |
        (Notification.team_id.in_([t.id for t in current_user.teams]))
    )

    if type_filter:
        query = query.filter_by(type=NotificationType(type_filter))

    if unread_only:
        query = query.filter_by(is_read=False)

    notifications = query.order_by(Notification.created_at.desc()).paginate(page=page, per_page=20)

    return render_template('operational/notifications/index.html', notifications=notifications)

@operational_bp.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def notifications_mark_read(id):
    """Marcar notificação como lida"""
    notification = Notification.query.get_or_404(id)

    # Check if user can read this notification
    if (notification.recipient_id == current_user.id or
        (notification.team_id and notification.team_id in [t.id for t in current_user.teams])):

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'success': True})

    return jsonify({'error': 'Unauthorized'}), 403

@operational_bp.route('/notifications/create', methods=['POST'])
@login_required
def notifications_create():
    """Criar nova notificação (para admins)"""
    if current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para criar notificações.', 'error')
        return redirect(url_for('operational.notifications_index'))

    title = request.form['title']
    message = request.form['message']
    type = request.form.get('type', 'info')
    priority = request.form.get('priority', 'normal')
    category = request.form.get('category')
    recipient_ids = request.form.getlist('recipient_ids')
    team_ids = request.form.getlist('team_ids')

    # Create notifications for individual recipients
    if recipient_ids:
        for recipient_id in recipient_ids:
            notification = Notification(
                title=title,
                message=message,
                type=NotificationType(type),
                priority=priority,
                category=category,
                recipient_id=recipient_id
            )
            db.session.add(notification)

    # Create notifications for teams
    if team_ids:
        for team_id in team_ids:
            notification = Notification(
                title=title,
                message=message,
                type=NotificationType(type),
                priority=priority,
                category=category,
                team_id=team_id
            )
            db.session.add(notification)

    db.session.commit()
    flash('Notificações enviadas com sucesso!', 'success')
    return redirect(url_for('operational.notifications_index'))

# ==================== KANBAN BOARD ====================

@operational_bp.route('/kanban')
@login_required
def kanban_board():
    """Visual Kanban para eventos operacionais"""
    events = OperationalEvent.query.order_by(OperationalEvent.created_at.desc()).all()

    # Group by status for Kanban columns
    kanban_data = {
        'todo': [e for e in events if e.status == 'todo'],
        'in_progress': [e for e in events if e.status == 'in_progress'],
        'review': [e for e in events if e.status == 'review'],
        'done': [e for e in events if e.status == 'done']
    }

    return render_template('operational/kanban/index.html', kanban_data=kanban_data)

@operational_bp.route('/kanban/create', methods=['GET', 'POST'])
@login_required
def kanban_create():
    """Criar novo evento operacional"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        category = request.form.get('category')
        priority = request.form.get('priority', 'medium')
        assigned_to_id = request.form.get('assigned_to_id')
        due_date = request.form.get('due_date')

        event = OperationalEvent(
            title=title,
            description=description,
            category=category,
            priority=priority,
            assigned_to_id=assigned_to_id,
            created_by_id=current_user.id
        )

        if due_date:
            event.due_date = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')

        db.session.add(event)
        db.session.commit()

        flash('Evento operacional criado com sucesso!', 'success')
        return redirect(url_for('operational.kanban_board'))

    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('operational/kanban/create.html', users=users)

@operational_bp.route('/kanban/<int:id>/update-status', methods=['POST'])
@login_required
def kanban_update_status(id):
    """Atualizar status do evento no Kanban"""
    event = OperationalEvent.query.get_or_404(id)

    # Try to get status from form data first, then from request data
    new_status = request.form.get('status') or request.get_data(as_text=True).split('=')[1] if '=' in request.get_data(as_text=True) else None

    print(f"Updating event {id} to status: {new_status}")  # Debug log

    if new_status in ['todo', 'in_progress', 'review', 'done']:
        old_status = event.status
        event.status = new_status
        db.session.commit()

        print(f"Event {id} status changed from {old_status} to {new_status}")  # Debug log

        return jsonify({
            'success': True,
            'event': {
                'id': event.id,
                'title': event.title,
                'status': event.status
            }
        })

    print(f"Invalid status: {new_status}")  # Debug log
    return jsonify({'error': 'Status inválido'}), 400

# ==================== DASHBOARD OPERACIONAL ====================

# Redirect Portuguese URLs to English ones
@operational_bp.route('/operacional')
@login_required
def operacional_redirect():
    return redirect(url_for('operational.dashboard'))

@operational_bp.route('/')
@login_required
def dashboard():
    """Dashboard operacional principal"""
    # CIPA stats
    upcoming_cipa = CIPAMeeting.query.filter(
        CIPAMeeting.meeting_date >= datetime.utcnow(),
        CIPAMeeting.status == 'scheduled'
    ).order_by(CIPAMeeting.meeting_date).first()

    # Improvement cycles stats
    active_improvements = ImprovementCycle.query.filter_by(status='active').count()
    completed_improvements = ImprovementCycle.query.filter_by(status='completed').count()

    # Notifications stats
    unread_notifications = Notification.query.filter(
        (Notification.recipient_id == current_user.id) |
        (Notification.team_id.in_([t.id for t in current_user.teams])),
        Notification.is_read == False
    ).count()

    # Kanban stats
    kanban_stats = {}
    for status in ['todo', 'in_progress', 'review', 'done']:
        kanban_stats[status] = OperationalEvent.query.filter_by(status=status).count()

    # Recent activities
    recent_events = OperationalEvent.query.order_by(OperationalEvent.created_at.desc()).limit(3).all()
    recent_notifications = Notification.query.filter(
        (Notification.recipient_id == current_user.id) |
        (Notification.team_id.in_([t.id for t in current_user.teams]))
    ).order_by(Notification.created_at.desc()).limit(2).all()
    recent_improvements = ImprovementCycle.query.order_by(ImprovementCycle.created_at.desc()).limit(2).all()

    dashboard_data = {
        'upcoming_cipa': upcoming_cipa,
        'active_improvements': active_improvements,
        'completed_improvements': completed_improvements,
        'unread_notifications': unread_notifications,
        'kanban_stats': kanban_stats,
        'recent_events': recent_events,
        'recent_notifications': recent_notifications,
        'recent_improvements': recent_improvements
    }

    return render_template('operational/dashboard.html', data=dashboard_data)