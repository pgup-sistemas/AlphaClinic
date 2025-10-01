from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db, PasswordResetToken
import secrets
import string
from datetime import datetime, timedelta
from email_service import get_email_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'error')
            return render_template('auth/register.html')
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Se o e-mail estiver cadastrado, você receberá instruções para redefinir sua senha.', 'info')
            return redirect(url_for('auth.login'))

        # Gerar token de redefinição
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

        # Criar token no banco
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1)  # Token válido por 1 hora
        )

        db.session.add(reset_token)
        db.session.commit()

        # Enviar e-mail com link de redefinição
        reset_url = url_for('auth.reset_password', token=token, _external=True)

        email_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3b82f6;">Redefinição de Senha 🔐</h2>
            <p>Olá {user.full_name},</p>
            <p>Você solicitou a redefinição de sua senha no Alphaclin QMS.</p>
            <p>Clique no link abaixo para definir uma nova senha:</p>
            <p style="margin: 30px 0;">
                <a href="{reset_url}"
                   style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                   Redefinir Senha
                </a>
            </p>
            <p><small>Este link expira em 1 hora por motivos de segurança.</small></p>
            <p>Se você não solicitou esta redefinição, ignore este e-mail.</p>
            <p>Atenciosamente,<br>Equipe Alphaclin QMS</p>
        </div>
        """

        email_service = get_email_service()
        email_sent = email_service.send_email(
            to_email=user.email,
            subject='Redefinição de Senha - Alphaclin QMS',
            body_html=email_body
        )

        if email_sent:
            flash('E-mail de redefinição enviado! Verifique sua caixa de entrada.', 'success')
        else:
            flash('Erro ao enviar e-mail. Tente novamente.', 'error')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verificar token
    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token or reset_token.expires_at < datetime.utcnow() or reset_token.used:
        flash('Token inválido ou expirado.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('auth/reset_password.html', token=token)

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('auth/reset_password.html', token=token)

        # Atualizar senha do usuário
        user = User.query.get(reset_token.user_id)
        user.password_hash = generate_password_hash(password)

        # Marcar token como usado
        reset_token.used = True

        db.session.commit()

        flash('Senha redefinida com sucesso! Faça o login com sua nova senha.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            # Validar dados
            full_name = request.form['full_name'].strip()
            email = request.form['email'].strip()
            phone = request.form.get('phone', '').strip()
            cpf = request.form.get('cpf', '').strip()

            # Validações básicas
            if not full_name or len(full_name) < 3:
                flash('Nome completo deve ter pelo menos 3 caracteres.', 'error')
                return redirect(url_for('auth.profile'))

            if not email or '@' not in email:
                flash('E-mail inválido.', 'error')
                return redirect(url_for('auth.profile'))

            # Validar CPF se fornecido
            if cpf and not User.validate_cpf(cpf):
                flash('CPF inválido.', 'error')
                return redirect(url_for('auth.profile'))

            # Validar telefone se fornecido
            if phone and not User.validate_phone(phone):
                flash('Telefone inválido. Use formato (11) 99999-9999 ou 11999999999.', 'error')
                return redirect(url_for('auth.profile'))

            # Atualizar informações pessoais
            current_user.full_name = full_name
            current_user.email = email
            current_user.phone = phone if phone else None
            current_user.cpf = cpf if cpf else None

            # Verificar se e-mail já existe (exceto para o próprio usuário)
            existing_email = User.query.filter_by(email=current_user.email).first()
            if existing_email and existing_email.id != current_user.id:
                flash('Este e-mail já está sendo usado por outro usuário.', 'error')
                return redirect(url_for('auth.profile'))

            db.session.commit()

            # Log de auditoria
            from models import AuditLog
            audit_log = AuditLog(
                entity_type='user',
                entity_id=current_user.id,
                entity_code=current_user.username,
                operation='update_profile',
                operation_details={'fields': ['full_name', 'email', 'phone', 'cpf']},
                user_id=current_user.id,
                user_full_name=current_user.full_name,
                user_role=current_user.role.value
            )
            audit_log.save_immutable()

            flash('Perfil atualizado com sucesso!', 'success')

        elif action == 'change_password':
            # Alterar senha
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if not check_password_hash(current_user.password_hash, current_password):
                flash('Senha atual incorreta.', 'error')
                return redirect(url_for('auth.profile'))

            if new_password != confirm_password:
                flash('As novas senhas não coincidem.', 'error')
                return redirect(url_for('auth.profile'))

            if len(new_password) < 6:
                flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
                return redirect(url_for('auth.profile'))

            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            # Log de auditoria
            from models import AuditLog
            audit_log = AuditLog(
                entity_type='user',
                entity_id=current_user.id,
                entity_code=current_user.username,
                operation='change_password',
                operation_details={'method': 'profile_change'},
                user_id=current_user.id,
                user_full_name=current_user.full_name,
                user_role=current_user.role.value
            )
            audit_log.save_immutable()

            flash('Senha alterada com sucesso!', 'success')

        elif action == 'update_preferences':
            # Atualizar preferências de notificação
            prefs = current_user.notification_preferences or NotificationPreference(user_id=current_user.id)
            prefs.email_enabled = request.form.get('email_enabled') == 'on'
            prefs.document_notifications = request.form.get('document_notifications') == 'on'
            prefs.audit_notifications = request.form.get('audit_notifications') == 'on'
            prefs.capa_notifications = request.form.get('capa_notifications') == 'on'
            prefs.operational_notifications = request.form.get('operational_notifications') == 'on'
            prefs.system_notifications = request.form.get('system_notifications') == 'on'

            db.session.add(prefs)
            db.session.commit()

            flash('Preferências atualizadas com sucesso!', 'success')

    # Buscar preferências do usuário
    preferences = current_user.notification_preferences

    return render_template('auth/profile.html',
                         user=current_user,
                         preferences=preferences)

@auth_bp.route('/security')
@login_required
def security():
    """Página dedicada às configurações de segurança"""
    # Buscar atividades recentes de segurança
    recent_audits = AuditLog.query.filter_by(
        entity_type='user',
        entity_id=current_user.id
    ).order_by(AuditLog.timestamp.desc()).limit(10).all()

    # Buscar tentativas de login recentes
    login_attempts = AuditLog.query.filter_by(
        entity_type='user',
        entity_id=current_user.id,
        operation='login'
    ).order_by(AuditLog.timestamp.desc()).limit(5).all()

    return render_template('auth/security.html',
                         user=current_user,
                         recent_audits=recent_audits,
                         login_attempts=login_attempts)