#!/usr/bin/env python3
"""
Serviço de E-mail para Alphaclin QMS
Gerencia envio de notificações por e-mail
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from flask import current_app
from models import db, EmailQueue, EmailTemplate, NotificationPreference, User

class EmailService:
    """Serviço para envio de e-mails"""

    def __init__(self):
        self.smtp_server = current_app.config.get('MAIL_SERVER')
        self.smtp_port = current_app.config.get('MAIL_PORT', 587)
        self.smtp_username = current_app.config.get('MAIL_USERNAME')
        self.smtp_password = current_app.config.get('MAIL_PASSWORD')
        self.use_tls = current_app.config.get('MAIL_USE_TLS', True)
        self.default_sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@alphaclinic.com')

    def send_email(self, to_email, subject, body_html, body_text=None,
                  from_email=None, cc=None, bcc=None, attachments=None):
        """
        Envia e-mail diretamente
        """
        if not self.smtp_server or not self.smtp_username:
            print("Configuração de e-mail não encontrada")
            return False

        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.default_sender
            msg['To'] = to_email
            if cc:
                msg['Cc'] = ', '.join(cc) if isinstance(cc, list) else cc

            # Adicionar corpo
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            msg.attach(MIMEText(body_html, 'html'))

            # Adicionar anexos
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                  f'attachment; filename="{attachment["filename"]}"')
                    msg.attach(part)

            # Enviar e-mail
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.smtp_username, self.smtp_password)

            recipients = [to_email]
            if cc:
                recipients.extend(cc if isinstance(cc, list) else [cc])
            if bcc:
                recipients.extend(bcc if isinstance(bcc, list) else [bcc])

            server.sendmail(from_email or self.default_sender, recipients, msg.as_string())
            server.quit()

            return True

        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            return False

    def queue_email(self, to_email, subject, body_html, body_text=None,
                   template_id=None, event_type=None, context_data=None,
                   priority='normal', cc=None, bcc=None):
        """
        Adiciona e-mail na fila para envio assíncrono
        """
        try:
            email_queue = EmailQueue(
                to_email=to_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                template_id=template_id,
                event_type=event_type,
                context_data=context_data or {},
                priority=priority,
                cc_emails=cc if isinstance(cc, list) else [cc] if cc else None,
                bcc_emails=bcc if isinstance(bcc, list) else [bcc] if bcc else None
            )

            db.session.add(email_queue)
            db.session.commit()

            return email_queue.id

        except Exception as e:
            print(f"Erro ao enfileirar e-mail: {e}")
            db.session.rollback()
            return None

    def process_email_queue(self, limit=10):
        """
        Processa fila de e-mails (chamar periodicamente)
        """
        try:
            # Buscar e-mails pendentes ordenados por prioridade
            pending_emails = EmailQueue.query.filter_by(status='pending')\
                .filter(
                    db.or_(
                        EmailQueue.next_attempt.is_(None),
                        EmailQueue.next_attempt <= datetime.utcnow()
                    )
                )\
                .order_by(
                    db.case(
                        (EmailQueue.priority == 'urgent', 1),
                        (EmailQueue.priority == 'high', 2),
                        (EmailQueue.priority == 'normal', 3),
                        (EmailQueue.priority == 'low', 4)
                    ),
                    EmailQueue.created_at
                )\
                .limit(limit)\
                .all()

            sent_count = 0
            failed_count = 0

            for email in pending_emails:
                success = self.send_email(
                    to_email=email.to_email,
                    subject=email.subject,
                    body_html=email.body_html,
                    body_text=email.body_text,
                    cc=email.cc_emails,
                    bcc=email.bcc_emails
                )

                if success:
                    email.mark_sent()
                    sent_count += 1
                else:
                    email.mark_failed("Falha no envio SMTP")
                    failed_count += 1

            db.session.commit()

            return {'sent': sent_count, 'failed': failed_count}

        except Exception as e:
            print(f"Erro ao processar fila de e-mails: {e}")
            db.session.rollback()
            return {'sent': 0, 'failed': 0}

class NotificationService:
    """Serviço para gerenciar notificações do QMS"""

    def __init__(self):
        self.email_service = EmailService()

    def send_notification(self, user_id, event_type, context_data=None, priority='normal'):
        """
        Envia notificação para usuário baseado em suas preferências
        """
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return False

        # Verificar preferências do usuário
        prefs = NotificationPreference.query.filter_by(user_id=user_id).first()
        if not prefs:
            # Criar preferências padrão
            prefs = NotificationPreference(user_id=user_id)
            db.session.add(prefs)
            db.session.commit()

        # Verificar se notificação está habilitada
        notification_enabled = self._is_notification_enabled(prefs, event_type)
        if not notification_enabled:
            return False

        # Buscar template de e-mail
        template = EmailTemplate.query.filter_by(
            event_type=event_type,
            is_active=True
        ).first()

        if not template:
            print(f"Template de e-mail não encontrado para evento: {event_type}")
            return False

        # Preparar contexto
        context = context_data or {}
        context.update({
            'user_name': user.full_name,
            'user_email': user.email,
            'event_type': event_type,
            'current_date': datetime.now().strftime('%d/%m/%Y %H:%M')
        })

        # Renderizar e-mail
        subject = template.render_subject(context)
        body_html = template.render_body_html(context)
        body_text = template.render_body_text(context)

        # Enviar por e-mail se habilitado
        if prefs.email_enabled and user.email:
            self.email_service.queue_email(
                to_email=user.email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                template_id=template.id,
                event_type=event_type,
                context_data=context,
                priority=priority
            )

        return True

    def _is_notification_enabled(self, prefs, event_type):
        """Verifica se tipo de notificação está habilitado"""
        mapping = {
            'document_approved': prefs.document_notifications,
            'document_rejected': prefs.document_notifications,
            'audit_created': prefs.audit_notifications,
            'nc_created': prefs.audit_notifications,
            'capa_created': prefs.capa_notifications,
            'capa_updated': prefs.capa_notifications,
            'cipa_meeting': prefs.operational_notifications,
            'improvement_created': prefs.operational_notifications,
            'system_alert': prefs.system_notifications
        }

        return mapping.get(event_type, True)

    def create_default_templates(self):
        """Cria templates de e-mail padrão"""
        templates = [
            {
                'name': 'Documento Aprovado',
                'event_type': 'document_approved',
                'subject': 'Documento Aprovado: {document_title}',
                'body_html': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #10b981;">Documento Aprovado ✅</h2>
                    <p>Olá {user_name},</p>
                    <p>O documento <strong>{document_title}</strong> foi aprovado e está disponível no sistema.</p>
                    <div style="background: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Código:</strong> {document_code}</p>
                        <p><strong>Versão:</strong> {document_version}</p>
                        <p><strong>Aprovado por:</strong> {approved_by}</p>
                    </div>
                    <p><a href="{document_url}" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Documento</a></p>
                    <p>Atenciosamente,<br>Equipe Alphaclin QMS</p>
                </div>
                '''
            },
            {
                'name': 'Nova NC Criada',
                'event_type': 'nc_created',
                'subject': 'Nova Não Conformidade: {nc_title}',
                'body_html': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #ef4444;">Nova Não Conformidade ⚠️</h2>
                    <p>Olá {user_name},</p>
                    <p>Uma nova não conformidade foi identificada e requer sua atenção.</p>
                    <div style="background: #fef2f2; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ef4444;">
                        <p><strong>Título:</strong> {nc_title}</p>
                        <p><strong>Severidade:</strong> {nc_severity}</p>
                        <p><strong>Responsável:</strong> {assigned_to}</p>
                    </div>
                    <p><a href="{nc_url}" style="background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Não Conformidade</a></p>
                    <p>Atenciosamente,<br>Equipe Alphaclin QMS</p>
                </div>
                '''
            },
            {
                'name': 'CAPA Criado',
                'event_type': 'capa_created',
                'subject': 'Plano CAPA Criado: {capa_reference}',
                'body_html': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #f59e0b;">Plano CAPA Criado 🛠️</h2>
                    <p>Olá {user_name},</p>
                    <p>Um novo plano de ação corretiva e preventiva foi criado.</p>
                    <div style="background: #fffbeb; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                        <p><strong>Referência:</strong> {capa_reference}</p>
                        <p><strong>Título:</strong> {capa_title}</p>
                        <p><strong>Tipo:</strong> {capa_type}</p>
                        <p><strong>Prioridade:</strong> {capa_priority}</p>
                    </div>
                    <p><a href="{capa_url}" style="background: #f59e0b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Plano CAPA</a></p>
                    <p>Atenciosamente,<br>Equipe Alphaclin QMS</p>
                </div>
                '''
            }
        ]

        for template_data in templates:
            existing = EmailTemplate.query.filter_by(event_type=template_data['event_type']).first()
            if not existing:
                template = EmailTemplate(**template_data)
                db.session.add(template)

        db.session.commit()
        print("Templates de e-mail padrão criados com sucesso!")

# Instâncias globais (lazy initialization)
_email_service = None
_notification_service = None

def get_email_service():
    """Obtém instância do serviço de e-mail"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

def get_notification_service():
    """Obtém instância do serviço de notificação"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service

# Para compatibilidade com código existente
email_service = None
notification_service = None