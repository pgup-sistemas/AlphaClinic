from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import User, UserRole, Team, db

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@login_required
def index():
    """Lista todos os usuários"""
    if current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para visualizar usuários.', 'error')
        return redirect(url_for('main.dashboard'))

    search = request.args.get('search')
    role_filter = request.args.get('role')
    active_only = request.args.get('active', 'true') == 'true'

    query = User.query

    if active_only:
        query = query.filter_by(is_active=True)

    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.full_name.contains(search))
        )

    if role_filter:
        query = query.filter_by(role=UserRole(role_filter))

    page = request.args.get('page', 1, type=int)
    per_page = 10  # Items per page

    users_pagination = query.order_by(User.full_name).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('users/index.html', users_pagination=users_pagination, UserRole=UserRole)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Criar novo usuário"""
    if current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para criar usuários.', 'error')
        return redirect(url_for('users.index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        team_ids = request.form.getlist('team_ids')

        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('users/create.html')

        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('users/create.html')

        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'error')
            return render_template('users/create.html')

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=generate_password_hash(password),
            role=UserRole(role)
        )

        db.session.add(user)
        db.session.flush()  # Get user ID

        # Add to teams
        if team_ids:
            teams = Team.query.filter(Team.id.in_(team_ids)).all()
            for team in teams:
                team.members.append(user)

        db.session.commit()

        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('users.view', id=user.id))

    # GET request
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    return render_template('users/create.html', teams=teams, UserRole=UserRole)

@users_bp.route('/<int:id>')
@login_required
def view(id):
    """Visualizar usuário"""
    if current_user.role.value not in ['admin', 'manager'] and current_user.id != id:
        flash('Sem permissão para visualizar este usuário.', 'error')
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(id)

    # User statistics
    total_teams = len(user.teams)
    total_created_documents = user.created_documents.count()

    # Recent activity
    recent_activity = []

    # Add document creation activity
    from models import Document
    for doc in user.created_documents.order_by(Document.created_at.desc()).limit(5).all():
        recent_activity.append({
            'type': 'document_created',
            'description': f'Criou documento: {doc.title}',
            'date': doc.created_at
        })

    # Sort by date
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:10]

    user_stats = {
        'total_teams': total_teams,
        'total_created_documents': total_created_documents,
        'recent_activity': recent_activity
    }

    return render_template('users/view.html', user=user, stats=user_stats)

@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar usuário"""
    user = User.query.get_or_404(id)

    if current_user.role.value not in ['admin', 'manager'] and current_user.id != id:
        flash('Sem permissão para editar este usuário.', 'error')
        return redirect(url_for('users.view', id=id))

    # Managers can't edit admins
    if current_user.role.value == 'manager' and user.role.value == 'admin':
        flash('Gerentes não podem editar administradores.', 'error')
        return redirect(url_for('users.view', id=id))

    if request.method == 'POST':
        user.email = request.form['email']
        user.full_name = request.form['full_name']

        # Only admins can change role and active status
        if current_user.role.value == 'admin':
            user.role = UserRole(request.form['role'])
            user.is_active = 'is_active' in request.form

        # Password change (optional)
        new_password = request.form.get('new_password')
        if new_password:
            confirm_password = request.form.get('confirm_new_password')
            if new_password != confirm_password:
                flash('As novas senhas não coincidem.', 'error')
                teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
                return render_template('users/edit.html', user=user, teams=teams, UserRole=UserRole)
            user.password_hash = generate_password_hash(new_password)

        # Update teams (only admins)
        if current_user.role.value == 'admin':
            team_ids = request.form.getlist('team_ids')
            user.teams.clear()
            if team_ids:
                teams = Team.query.filter(Team.id.in_(team_ids)).all()
                for team in teams:
                    team.members.append(user)

        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('users.view', id=id))

    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    return render_template('users/edit.html', user=user, teams=teams, UserRole=UserRole)

@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Excluir usuário"""
    if current_user.role.value not in ['admin']:
        flash('Apenas administradores podem excluir usuários.', 'error')
        return redirect(url_for('users.index'))

    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('Não é possível excluir seu próprio usuário.', 'error')
        return redirect(url_for('users.view', id=id))

    # Remove from teams
    for team in user.teams:
        team.members.remove(user)

    db.session.delete(user)
    db.session.commit()

    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/api/user-stats/<int:id>')
@login_required
def user_stats_api(id):
    """API endpoint para estatísticas do usuário"""
    if current_user.role.value not in ['admin', 'manager'] and current_user.id != id:
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(id)

    stats = {
        'user_id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role.value,
        'is_active': user.is_active,
        'teams_count': len(user.teams),
        'documents_created': user.created_documents.count(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    }

    return jsonify(stats)