from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from config import Config
import os
import datetime
import socket

# Initialize extensions - import db from models to avoid duplicate instances
from models import db
migrate = Migrate()
login_manager = LoginManager()

# Import Flask-WTF for CSRF protection
# from flask_wtf.csrf import CSRFProtect
# csrf = CSRFProtect()

def get_local_ip():
    """Obtém o endereço IP local da máquina"""
    try:
        # Criar um socket temporário para determinar o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def find_available_port(start_port=8000):
    """Encontra uma porta disponível começando pela porta especificada"""
    port = start_port

    while port < start_port + 100:  # Tentar até 100 portas acima
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            port += 1

    return start_port  # Retornar a original se nenhuma disponível

def check_network_connectivity():
    """Verifica conectividade de rede e firewall"""
    local_ip = get_local_ip()
    port = 8000

    print("Verificando conectividade de rede...")

    # Testar se a porta padrão está disponível
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((local_ip, port))
        if result == 0:
            print(f"  [AVISO] Porta {port} ja esta em uso em {local_ip}")
            print("  Procurando porta alternativa...")

            # Tentar encontrar porta disponível
            available_port = find_available_port(port + 1)
            if available_port != port:
                print(f"  [OK] Porta alternativa encontrada: {available_port}")
                return available_port
            else:
                print(f"  [ERRO] Nenhuma porta alternativa disponivel")
                return port
        else:
            print(f"  [OK] Porta {port} disponivel em {local_ip}")
            return port
        sock.close()
    except Exception as e:
        print(f"  [ERRO] Nao foi possivel verificar porta: {e}")
        return port

    # Verificar interfaces de rede
    try:
        hostname = socket.gethostname()
        local_ips = socket.gethostbyname_ex(hostname)[2]
        print(f"  Interfaces de rede encontradas: {local_ips}")
    except Exception as e:
        print(f"  [ERRO] Nao foi possivel obter interfaces: {e}")

def print_startup_info(port=None):
    """Exibe informações de inicialização do sistema"""
    if port is None:
        port = 8000

    print("\n" + "="*60)
    print("ALPHACLIN QMS - SISTEMA INICIADO COM SUCESSO!")
    print("="*60)
    print(f"Acesso Local:     http://localhost:{port}")
    print(f"Usuario Admin:    admin")
    print(f"Senha Admin:      admin123")
    print("="*60)
    print("Instrucoes para Teste:")
    print(f"   1. Abra http://localhost:{port} no navegador")
    print("   2. Use as credenciais acima para fazer login")
    print("="*60)
    print("Dicas para Troubleshooting:")
    print("   - Se nao conseguir acessar:")
    print(f"   * Certifique-se de que nao ha outro processo usando a porta {port}")
    print("   * Verifique se o firewall permite conexoes locais")
    print("="*60 + "\n")

def seed_admin_user():
    """Create default admin user and sample operational data"""
    from models import (
        User, UserRole, CIPAMeeting, ImprovementCycle, Notification,
        OperationalEvent, ImprovementStatus, NotificationType, Team,
        Audit, NonConformity, CAPA, CAPAStatus, CAPAType, AuditType, Norm
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

    # Create sample CAPA data
    if NonConformity.query.count() == 0:
        # Create a sample norm first
        sample_norm = Norm.query.filter_by(code='ISO9001').first()
        if not sample_norm:
            sample_norm = Norm(
                name='ISO 9001:2015 - Sistema de Gestão da Qualidade',
                code='ISO9001',
                description='Norma internacional para sistemas de gestão da qualidade',
                version='2015',
                effective_date=datetime.utcnow().date(),
                is_active=True
            )
            db.session.add(sample_norm)

        # Create sample audit
        sample_audit = Audit(
            title='Auditoria Interna - Sistema de Gestão da Qualidade',
            audit_type=AuditType.INTERNAL,
            norm_id=sample_norm.id,
            location='Clínica Alphaclin - Todas as áreas',
            planned_date=datetime.utcnow().date(),
            actual_date=datetime.utcnow().date(),
            assigned_auditor_id=admin.id,
            responsible_id=admin.id,
            objectives='Verificar conformidade com requisitos da ISO 9001',
            scope='Todo o sistema de gestão da qualidade',
            status='completed',
            progress_percentage=100
        )
        db.session.add(sample_audit)
        db.session.flush()

        # Create sample non-conformity
        sample_nc = NonConformity(
            audit_id=sample_audit.id,
            title='Ausência de procedimento documentado para calibração de equipamentos',
            description='Durante a auditoria, foi identificado que não existe procedimento documentado para calibração dos equipamentos médicos, violando o requisito 7.1.5.2.1 da ISO 9001.',
            severity='major',
            requirement='ISO 9001:2015 - 7.1.5.2.1 - Calibração',
            identified_by_id=admin.id,
            assigned_to_id=admin.id,
            status='open'
        )
        db.session.add(sample_nc)
        db.session.flush()

        # Create sample CAPA
        sample_capa = CAPA(
            non_conformity_id=sample_nc.id,
            capa_type=CAPAType.CORRECTIVE,
            what='Elaborar e implementar procedimento documentado para calibração de equipamentos médicos',
            why='Garantir conformidade com requisitos da ISO 9001 e prevenir falhas nos equipamentos',
            who='Engenheiro Clínico / Equipe de Manutenção',
            when=datetime.utcnow().date() + timedelta(days=30),
            how='1. Pesquisar normas aplicáveis; 2. Elaborar procedimento; 3. Treinar equipe; 4. Implementar sistema de calibração',
            how_much='R$ 5.000,00 (treinamento + equipamentos de calibração)',
            priority='high',
            target_completion_date=datetime.utcnow().date() + timedelta(days=30),
            created_by_id=admin.id,
            responsible_id=admin.id
        )
        sample_capa.generate_reference_number()
        db.session.add(sample_capa)
        db.session.flush()

        # Update CAPA to approved status
        sample_capa.status = CAPAStatus.APPROVED
        sample_capa.approved_by_id = admin.id
        sample_capa.approved_at = datetime.utcnow()

        # Update CAPA to implemented status
        sample_capa.status = CAPAStatus.IMPLEMENTED
        sample_capa.implemented_by_id = admin.id
        sample_capa.implemented_at = datetime.utcnow()
        sample_capa.implementation_notes = 'Procedimento elaborado e aprovado. Treinamento realizado para 15 funcionários. Sistema implementado com agendamento automático de calibrações.'
        sample_capa.actual_completion_date = datetime.utcnow().date()

        # Update CAPA to verified status
        sample_capa.status = CAPAStatus.VERIFIED
        sample_capa.verified_by_id = admin.id
        sample_capa.verified_at = datetime.utcnow()
        sample_capa.verification_method = 'Auditoria de acompanhamento e verificação da implementação do procedimento'
        sample_capa.verification_result = 'Procedimento implementado corretamente. Todos os equipamentos críticos foram calibrados. Sistema de agendamento funcionando.'
        sample_capa.effectiveness_rating = 5
        sample_capa.verification_date = datetime.utcnow().date()

        # Close the CAPA
        sample_capa.status = CAPAStatus.CLOSED

        print("Sample CAPA data created successfully")

        # Create sample document for signature testing
        sample_document = Document.query.filter_by(title='Procedimento de Calibração de Equipamentos').first()
        if not sample_document:
            sample_document = Document(
                title='Procedimento de Calibração de Equipamentos',
                code='PROC-CAL-001',
                content='<h1>Procedimento de Calibração</h1><p>Este documento descreve o procedimento padrão para calibração de equipamentos médicos na Alphaclin.</p><h2>Objetivo</h2><p>Garantir que todos os equipamentos estejam calibrados conforme normas vigentes.</p><h2>Responsabilidades</h2><p>Engenheiro Clínico: Realizar calibração</p><p>Equipe de Manutenção: Apoiar atividades</p>',
                version='1.0',
                status=DocumentStatus.PUBLISHED,
                created_by_id=admin.id,
                published_by_id=admin.id,
                published_at=datetime.utcnow(),
                category='Procedimentos',
                effective_date=datetime.utcnow().date()
            )
            db.session.add(sample_document)
            db.session.flush()

            # Create sample electronic signatures
            approval_signature = ElectronicSignature(
                document_id=sample_document.id,
                user_id=admin.id,
                signature_type=SignatureType.APPROVAL,
                context=f"Aprovação versão {sample_document.version} - {sample_document.title}",
                ip_address='127.0.0.1',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                certificate_info={
                    'user_id': admin.id,
                    'user_name': admin.full_name,
                    'user_email': admin.email,
                    'timestamp': datetime.utcnow().isoformat()
                },
                signed_at=datetime.utcnow()
            )
            content_to_sign = f"{sample_document.title}{sample_document.content}{sample_document.version}{admin.id}{datetime.utcnow().isoformat()}"
            approval_signature.signature_data = approval_signature.generate_signature_hash(content_to_sign)
            db.session.add(approval_signature)

            reading_signature = ElectronicSignature(
                document_id=sample_document.id,
                user_id=admin.id,
                signature_type=SignatureType.READING,
                context=f"Confirmação de leitura - {sample_document.title}",
                ip_address='127.0.0.1',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                certificate_info={
                    'user_id': admin.id,
                    'user_name': admin.full_name,
                    'user_email': admin.email,
                    'timestamp': datetime.utcnow().isoformat()
                },
                signed_at=datetime.utcnow()
            )
            reading_signature.signature_data = reading_signature.generate_signature_hash(content_to_sign)
            db.session.add(reading_signature)

            print("Sample document and signatures created successfully")

    # Create default email templates
    try:
        from email_service import notification_service
        notification_service.create_default_templates()
        print("Email templates created successfully")
    except Exception as e:
        print(f"Warning: Could not create email templates: {e}")

    # Create notification preferences for admin
    try:
        from models import NotificationPreference
        admin_prefs = NotificationPreference.query.filter_by(user_id=admin.id).first()
        if not admin_prefs:
            admin_prefs = NotificationPreference(
                user_id=admin.id,
                email_enabled=True,
                document_notifications=True,
                audit_notifications=True,
                capa_notifications=True,
                operational_notifications=True,
                system_notifications=True
            )
            db.session.add(admin_prefs)
        print("Notification preferences created successfully")
    except Exception as e:
        print(f"Warning: Could not create notification preferences: {e}")

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

    # Analytics e BI
    from blueprints.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/analytics')

    # Documentação integrada
    from blueprints.docs import docs_bp
    app.register_blueprint(docs_bp, url_prefix='/docs')

    # APIs de Integração Empresarial
    from blueprints.integrations import integrations_bp
    app.register_blueprint(integrations_bp)

    # Relatórios de Compliance
    from blueprints.compliance import compliance_bp
    app.register_blueprint(compliance_bp, url_prefix='/compliance')
    
    return app

if __name__ == '__main__':
    app = create_app()

    @app.cli.command('process-emails')
    def process_emails():
        """Processar fila de e-mails pendentes"""
        with app.app_context():
            try:
                from email_service import email_service
                result = email_service.process_email_queue()
                print(f"E-mails processados: {result['sent']} enviados, {result['failed']} falharam")
            except Exception as e:
                print(f"Erro ao processar e-mails: {e}")

    @app.cli.command('create-email-templates')
    def create_email_templates():
        """Criar templates de e-mail padrão"""
        with app.app_context():
            try:
                from email_service import notification_service
                notification_service.create_default_templates()
                print("Templates de e-mail criados com sucesso!")
            except Exception as e:
                print(f"Erro ao criar templates: {e}")

    # Inicialização única e completa
    with app.app_context():
        db.create_all()
        seed_admin_user()

    # Verificar conectividade de rede e encontrar porta disponível
    port = check_network_connectivity()

    # Exibir informações de inicialização
    print_startup_info(port)

    # Iniciar servidor apenas em localhost
    print("Iniciando servidor Flask...")
    print(f"Configuracao: host='127.0.0.1', port={port}")
    app.run(host='127.0.0.1', port=port, debug=True)