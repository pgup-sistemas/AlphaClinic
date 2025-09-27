from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from config import Config
import os
import datetime

# Initialize extensions - import db from models to avoid duplicate instances
from models import db
migrate = Migrate()
login_manager = LoginManager()

# Import Flask-WTF for CSRF protection
# from flask_wtf.csrf import CSRFProtect
# csrf = CSRFProtect()

def seed_admin_user():
    """Create default admin user and sample operational data"""
    from models import (
        User, UserRole, CIPAMeeting, ImprovementCycle, Notification,
        OperationalEvent, ImprovementStatus, NotificationType, Team
    )
    from datetime import datetime, timedelta

    # Create admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@alphaclinic.com',
            password_hash=generate_password_hash('admin123'),
            full_name='Administrator',
            role=UserRole.ADMIN
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with username: admin, password: admin123")

    # Create sample operational data if it doesn't exist
    if CIPAMeeting.query.count() == 0:
        # Create upcoming CIPA meeting
        upcoming_cipa = CIPAMeeting(
            title='Reunião Ordinária CIPA - Outubro 2024',
            meeting_date=datetime.utcnow() + timedelta(days=7),
            location='Sala de Reuniões - 2º andar',
            agenda='1. Análise de acidentes do mês\n2. Campanhas de prevenção\n3. Relatório de comissões',
            chairperson=admin,
            secretary=admin
        )
        db.session.add(upcoming_cipa)

        # Create completed CIPA meeting
        past_cipa = CIPAMeeting(
            title='Reunião Ordinária CIPA - Setembro 2024',
            meeting_date=datetime.utcnow() - timedelta(days=30),
            location='Sala de Reuniões - 2º andar',
            agenda='Análise de acidentes e medidas preventivas',
            minutes='Reunião realizada com presença de todos os membros...',
            decisions='Implementar nova campanha de conscientização',
            status='completed',
            chairperson=admin,
            secretary=admin
        )
        db.session.add(past_cipa)

    if ImprovementCycle.query.count() == 0:
        # Create active improvement cycle
        active_improvement = ImprovementCycle(
            title='Redução de Tempo de Espera na Recepção',
            description='Implementar sistema de agendamento online para reduzir tempo de espera',
            category='eficiência',
            priority='high',
            responsible=admin,
            created_by=admin,
            current_phase=ImprovementStatus.DO,
            plan_description='Análise do processo atual e identificação de gargalos',
            do_description='Implementação do sistema de agendamento online'
        )
        db.session.add(active_improvement)

        # Create completed improvement cycle
        completed_improvement = ImprovementCycle(
            title='Padronização de Procedimentos de Higienização',
            description='Criação de protocolo único para higienização de equipamentos',
            category='qualidade',
            priority='medium',
            responsible=admin,
            created_by=admin,
            current_phase=ImprovementStatus.COMPLETED,
            status='completed',
            actual_completion_date=datetime.utcnow().date(),
            plan_description='Análise de procedimentos existentes',
            do_description='Criação e implementação do protocolo único',
            check_description='Auditoria de conformidade',
            act_description='Treinamento da equipe e monitoramento contínuo'
        )
        db.session.add(completed_improvement)

    if OperationalEvent.query.count() == 0:
        # Create sample operational events
        events_data = [
            {
                'title': 'Manutenção do Ar-Condicionado - UTI',
                'description': 'Verificar filtros e limpeza do sistema',
                'category': 'manutenção',
                'priority': 'high',
                'status': 'todo',
                'due_date': datetime.utcnow() + timedelta(days=2)
            },
            {
                'title': 'Calibração da Balança Digital',
                'description': 'Calibração anual conforme norma ISO',
                'category': 'calibração',
                'priority': 'medium',
                'status': 'in_progress',
                'due_date': datetime.utcnow() + timedelta(days=5)
            },
            {
                'title': 'Inspeção de Extintores - Ala A',
                'description': 'Verificação mensal dos extintores',
                'category': 'inspeção',
                'priority': 'medium',
                'status': 'review',
                'due_date': datetime.utcnow() - timedelta(days=1)
            },
            {
                'title': 'Treinamento em Biossegurança',
                'description': 'Capacitação da equipe de enfermagem',
                'category': 'treinamento',
                'priority': 'high',
                'status': 'done',
                'due_date': datetime.utcnow() - timedelta(days=3)
            }
        ]

        for event_data in events_data:
            event = OperationalEvent(
                title=event_data['title'],
                description=event_data['description'],
                category=event_data['category'],
                priority=event_data['priority'],
                status=event_data['status'],
                due_date=event_data['due_date'],
                assigned_to=admin,
                created_by=admin
            )
            db.session.add(event)

    if Notification.query.count() == 0:
        # Create sample notifications
        notifications_data = [
            {
                'title': 'Reunião CIPA - Próxima Semana',
                'message': 'Lembrete: Reunião ordinária da CIPA na próxima sexta-feira às 14h.',
                'type': NotificationType.INFO,
                'priority': 'normal',
                'category': 'cipa'
            },
            {
                'title': 'Documento Aprovado',
                'message': 'O documento "Protocolo de Emergência" foi aprovado e publicado.',
                'type': NotificationType.SUCCESS,
                'priority': 'normal',
                'category': 'documento'
            },
            {
                'title': 'Manutenção Programada',
                'message': 'Sistema de ar-condicionado será desligado amanhã das 8h às 10h.',
                'type': NotificationType.WARNING,
                'priority': 'high',
                'category': 'manutenção'
            }
        ]

        for notif_data in notifications_data:
            notification = Notification(
                title=notif_data['title'],
                message=notif_data['message'],
                type=notif_data['type'],
                priority=notif_data['priority'],
                category=notif_data['category'],
                recipient=admin
            )
            db.session.add(notification)

    db.session.commit()
    print("Sample operational data created successfully")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Add datetime to Jinja globals
    app.jinja_env.globals['datetime'] = datetime

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.documents import documents_bp
    from blueprints.norms import norms_bp
    from blueprints.audits import audits_bp
    from blueprints.teams import teams_bp
    from blueprints.users import users_bp
    from blueprints.operational import operational_bp
    from blueprints.processes import processes_bp
    from blueprints.nonconformities import nonconformities_bp
    from blueprints.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(norms_bp, url_prefix='/norms')
    app.register_blueprint(audits_bp, url_prefix='/audits')
    app.register_blueprint(teams_bp, url_prefix='/teams')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(operational_bp, url_prefix='/operational')
    app.register_blueprint(processes_bp, url_prefix='/processes')
    app.register_blueprint(nonconformities_bp, url_prefix='/nonconformities')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_admin_user()
    app.run(host='localhost', port=5000, debug=True)