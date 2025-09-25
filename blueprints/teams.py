from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Team, User, Document, DocumentRead
from app import db
from datetime import datetime

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/')
@login_required
def index():
    """Lista todas as equipes"""
    search = request.args.get('search')
    active_only = request.args.get('active', 'true') == 'true'
    
    query = Team.query
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    if search:
        query = query.filter(Team.name.contains(search))
    
    teams = query.order_by(Team.name).all()
    
    return render_template('teams/index.html', teams=teams)

@teams_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Criar nova equipe"""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        member_ids = request.form.getlist('member_ids')
        
        # Check if team name already exists
        if Team.query.filter_by(name=name).first():
            flash('Nome da equipe já existe.', 'error')
            return render_template('teams/create.html')
        
        team = Team(
            name=name,
            description=description
        )
        
        db.session.add(team)
        db.session.flush()  # Get team ID
        
        # Add members
        if member_ids:
            members = User.query.filter(User.id.in_(member_ids)).all()
            team.members.extend(members)
        
        db.session.commit()
        
        flash('Equipe criada com sucesso!', 'success')
        return redirect(url_for('teams.view', id=team.id))
    
    # GET request
    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('teams/create.html', users=users)

@teams_bp.route('/<int:id>')
@login_required
def view(id):
    """Visualizar equipe"""
    team = Team.query.get_or_404(id)
    
    # Team statistics
    total_members = len(team.members)
    
    # Recent documents sent to team members
    recent_documents = []
    for member in team.members:
        member_docs = DocumentRead.query.filter_by(user_id=member.id).order_by(DocumentRead.read_at.desc()).limit(5).all()
        recent_documents.extend([(doc.document, member, doc.read_at) for doc in member_docs])
    
    # Sort by read date
    recent_documents.sort(key=lambda x: x[2], reverse=True)
    recent_documents = recent_documents[:10]  # Top 10 most recent
    
    team_stats = {
        'total_members': total_members,
        'recent_documents': recent_documents
    }
    
    return render_template('teams/view.html', team=team, stats=team_stats)

@teams_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar equipe"""
    team = Team.query.get_or_404(id)
    
    # Check permissions
    if current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para editar equipes.', 'error')
        return redirect(url_for('teams.view', id=id))
    
    if request.method == 'POST':
        team.name = request.form['name']
        team.description = request.form.get('description', '')
        member_ids = request.form.getlist('member_ids')
        
        # Update members
        team.members.clear()
        if member_ids:
            members = User.query.filter(User.id.in_(member_ids)).all()
            team.members.extend(members)
        
        db.session.commit()
        flash('Equipe atualizada com sucesso!', 'success')
        return redirect(url_for('teams.view', id=id))
    
    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return render_template('teams/edit.html', team=team, users=users)

@teams_bp.route('/<int:id>/send-documents', methods=['GET', 'POST'])
@login_required
def send_documents(id):
    """Envio de documentos para leitura/revisão a equipes inteiras"""
    team = Team.query.get_or_404(id)
    
    if request.method == 'POST':
        document_ids = request.form.getlist('document_ids')
        action_type = request.form.get('action_type')  # 'read' or 'review'
        deadline = request.form.get('deadline')
        message = request.form.get('message', '')
        
        if not document_ids:
            flash('Selecione pelo menos um documento.', 'error')
            return redirect(url_for('teams.send_documents', id=id))
        
        documents = Document.query.filter(Document.id.in_(document_ids)).all()
        
        success_count = 0
        
        for member in team.members:
            for document in documents:
                if action_type == 'read':
                    # Create read assignment
                    existing_read = DocumentRead.query.filter_by(
                        document_id=document.id,
                        user_id=member.id
                    ).first()
                    
                    if not existing_read:
                        read_record = DocumentRead(
                            document_id=document.id,
                            user_id=member.id
                        )
                        db.session.add(read_record)
                        success_count += 1
                
                elif action_type == 'review':
                    # Assign for review (if document is in review status)
                    if document.status.value == 'review' and not document.reviewed_by_id:
                        document.reviewed_by_id = member.id
                        if deadline:
                            document.review_deadline = datetime.strptime(deadline, '%Y-%m-%d')
                        success_count += 1
        
        db.session.commit()
        
        action_text = "leitura" if action_type == 'read' else "revisão"
        flash(f'{success_count} documentos enviados para {action_text} aos membros da equipe!', 'success')
        return redirect(url_for('teams.view', id=id))
    
    # GET request - show document selection form
    available_documents = Document.query.filter(Document.status.in_(['published', 'review'])).order_by(Document.title).all()
    
    return render_template('teams/send_documents.html', team=team, documents=available_documents)

@teams_bp.route('/<int:id>/bulk-notifications', methods=['GET', 'POST'])
@login_required
def bulk_notifications(id):
    """Notificações em lote para todos os membros"""
    team = Team.query.get_or_404(id)
    
    if request.method == 'POST':
        notification_type = request.form.get('notification_type')
        subject = request.form['subject']
        message = request.form['message']
        send_email = 'send_email' in request.form
        
        # Here you would implement actual notification sending
        # For now, we'll just flash a success message
        
        notification_count = len(team.members)
        
        flash(f'Notificação enviada para {notification_count} membros da equipe!', 'success')
        return redirect(url_for('teams.view', id=id))
    
    return render_template('teams/bulk_notifications.html', team=team)

@teams_bp.route('/<int:id>/permissions', methods=['GET', 'POST'])
@login_required
def permissions(id):
    """Gestão de permissões em grupo"""
    team = Team.query.get_or_404(id)
    
    # Check permissions
    if current_user.role.value not in ['admin']:
        flash('Apenas administradores podem gerenciar permissões.', 'error')
        return redirect(url_for('teams.view', id=id))
    
    if request.method == 'POST':
        # This would implement group permission changes
        # For now, just show success message
        flash('Permissões da equipe atualizadas!', 'success')
        return redirect(url_for('teams.view', id=id))
    
    return render_template('teams/permissions.html', team=team)

@teams_bp.route('/api/team-stats/<int:id>')
@login_required
def team_stats_api(id):
    """API endpoint para estatísticas da equipe"""
    team = Team.query.get_or_404(id)
    
    # Document reading statistics
    total_reads = 0
    confirmed_reads = 0
    
    for member in team.members:
        member_reads = DocumentRead.query.filter_by(user_id=member.id).all()
        total_reads += len(member_reads)
        confirmed_reads += len([r for r in member_reads if r.confirmed])
    
    # Team activity metrics
    active_members = len([m for m in team.members if m.last_login and m.last_login >= datetime.utcnow().replace(day=datetime.utcnow().day - 30)])
    
    stats = {
        'team_id': team.id,
        'team_name': team.name,
        'total_members': len(team.members),
        'active_members': active_members,
        'total_reads': total_reads,
        'confirmed_reads': confirmed_reads,
        'read_confirmation_rate': (confirmed_reads / total_reads * 100) if total_reads > 0 else 0
    }
    
    return jsonify(stats)