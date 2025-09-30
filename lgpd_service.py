"""
Serviço de Compliance LGPD (Lei Geral de Proteção de Dados)
Implementa funcionalidades para conformidade com a legislação brasileira
"""

from models import (
    db, User, AuditLog, ElectronicSignature, Document,
    NotificationPreference, DataProcessingConsent, DataSubjectRequest
)
from audit_service import AuditService
from encryption_service import EncryptionService
from datetime import datetime, timedelta
from flask import current_app
import json
from enum import Enum

class DataProcessingPurpose(Enum):
    """Finalidades de tratamento de dados"""
    USER_MANAGEMENT = "user_management"
    DOCUMENT_MANAGEMENT = "document_management"
    AUDIT_COMPLIANCE = "audit_compliance"
    QUALITY_MANAGEMENT = "quality_management"
    COMMUNICATION = "communication"
    ANALYTICS = "analytics"
    LEGAL_COMPLIANCE = "legal_compliance"

class DataSubjectRights(Enum):
    """Direitos do titular de dados (LGPD)"""
    ACCESS = "access"  # Confirmação da existência de tratamento
    ACCESS_DATA = "access_data"  # Acesso aos dados
    CORRECTION = "correction"  # Correção de dados incompletos
    ANONYMIZATION = "anonymization"  # Anonimização, bloqueio ou eliminação
    PORTABILITY = "portability"  # Portabilidade dos dados
    ELIMINATION = "elimination"  # Eliminação dos dados
    CONSENT_WITHDRAWAL = "consent_withdrawal"  # Retirada do consentimento
    OPPOSITION = "opposition"  # Oposição ao tratamento

class LGPDService:
    """Serviço para compliance LGPD"""

    @staticmethod
    def create_data_processing_consent(user_id, purpose, consent_data=None):
        """
        Cria registro de consentimento para tratamento de dados

        Args:
            user_id: ID do usuário
            purpose: Finalidade do tratamento (DataProcessingPurpose)
            consent_data: Dados adicionais do consentimento

        Returns:
            Registro de consentimento criado
        """
        try:
            # Verificar se já existe consentimento ativo
            existing_consent = DataProcessingConsent.query.filter_by(
                user_id=user_id,
                purpose=purpose.value,
                is_active=True
            ).first()

            if existing_consent:
                return existing_consent

            # Criar novo consentimento
            consent = DataProcessingConsent(
                user_id=user_id,
                purpose=purpose.value,
                consent_version="1.0",
                consent_data=json.dumps(consent_data or {}),
                ip_address=None,  # Em produção, obter do request
                user_agent=None,   # Em produção, obter do request
                legal_basis="consent",
                retention_period_days=2555,  # 7 anos conforme LGPD
                is_active=True
            )

            db.session.add(consent)
            db.session.commit()

            # Auditoria
            AuditService.log_operation(
                entity_type='consent',
                entity_id=consent.id,
                operation='consent_given',
                operation_details={
                    'purpose': purpose.value,
                    'user_id': user_id,
                    'consent_version': consent.consent_version
                },
                compliance_level='critical'
            )

            return consent

        except Exception as e:
            current_app.logger.error(f"Erro ao criar consentimento LGPD: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def withdraw_consent(user_id, purpose):
        """
        Retira consentimento de tratamento de dados

        Args:
            user_id: ID do usuário
            purpose: Finalidade do tratamento
        """
        try:
            consent = DataProcessingConsent.query.filter_by(
                user_id=user_id,
                purpose=purpose.value,
                is_active=True
            ).first()

            if consent:
                consent.is_active = False
                consent.withdrawn_at = datetime.utcnow()
                db.session.commit()

                # Auditoria
                AuditService.log_operation(
                    entity_type='consent',
                    entity_id=consent.id,
                    operation='consent_withdrawn',
                    operation_details={
                        'purpose': purpose.value,
                        'user_id': user_id
                    },
                    compliance_level='critical'
                )

            return True

        except Exception as e:
            current_app.logger.error(f"Erro ao retirar consentimento LGPD: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def create_data_subject_request(user_id, request_type, description=None, contact_email=None):
        """
        Cria solicitação de direitos do titular de dados

        Args:
            user_id: ID do usuário solicitante
            request_type: Tipo de solicitação (DataSubjectRights)
            description: Descrição da solicitação
            contact_email: E-mail para contato

        Returns:
            Solicitação criada
        """
        try:
            request_record = DataSubjectRequest(
                user_id=user_id,
                request_type=request_type.value,
                description=description,
                contact_email=contact_email or User.query.get(user_id).email,
                status='pending',
                priority='normal'
            )

            db.session.add(request_record)
            db.session.commit()

            # Auditoria
            AuditService.log_operation(
                entity_type='data_subject_request',
                entity_id=request_record.id,
                operation='request_created',
                operation_details={
                    'request_type': request_type.value,
                    'user_id': user_id,
                    'description': description
                },
                compliance_level='critical'
            )

            return request_record

        except Exception as e:
            current_app.logger.error(f"Erro ao criar solicitação LGPD: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def process_data_subject_request(request_id, response_data=None, status='completed'):
        """
        Processa solicitação de direitos do titular

        Args:
            request_id: ID da solicitação
            response_data: Dados de resposta
            status: Status final da solicitação
        """
        try:
            request_record = DataSubjectRequest.query.get(request_id)
            if not request_record:
                raise ValueError("Solicitação não encontrada")

            request_record.status = status
            request_record.response_data = json.dumps(response_data or {})
            request_record.processed_at = datetime.utcnow()
            request_record.processed_by = 0  # Sistema por enquanto

            db.session.commit()

            # Auditoria
            AuditService.log_operation(
                entity_type='data_subject_request',
                entity_id=request_id,
                operation='request_processed',
                operation_details={
                    'original_request_type': request_record.request_type,
                    'final_status': status,
                    'response_provided': response_data is not None
                },
                compliance_level='critical'
            )

        except Exception as e:
            current_app.logger.error(f"Erro ao processar solicitação LGPD: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def get_user_data_portfolio(user_id):
        """
        Obtém portfólio completo de dados do usuário para LGPD

        Args:
            user_id: ID do usuário

        Returns:
            Portfólio de dados pessoais
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("Usuário não encontrado")

            portfolio = {
                'personal_information': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role.value,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_active': user.is_active
                },
                'documents_created': Document.query.filter_by(created_by_id=user_id).count(),
                'documents_assigned_for_review': Document.query.filter_by(reviewed_by_id=user_id).count(),
                'audits_assigned': Audit.query.filter_by(assigned_auditor_id=user_id).count(),
                'non_conformities_identified': NonConformity.query.filter_by(identified_by_id=user_id).count(),
                'capa_assigned': CAPA.query.filter_by(responsible_id=user_id).count(),
                'electronic_signatures': ElectronicSignature.query.filter_by(user_id=user_id).count(),
                'audit_logs_count': AuditLog.query.filter_by(user_id=user_id).count(),
                'consent_records': LGPDService.get_user_consents(user_id),
                'data_retention_info': {
                    'retention_period_days': 2555,  # 7 anos
                    'estimated_deletion_date': (datetime.utcnow() + timedelta(days=2555)).date().isoformat()
                }
            }

            return portfolio

        except Exception as e:
            current_app.logger.error(f"Erro ao obter portfólio de dados LGPD: {str(e)}")
            raise

    @staticmethod
    def get_user_consents(user_id):
        """Obtém registros de consentimento do usuário"""
        try:
            consents = DataProcessingConsent.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()

            return [{
                'id': consent.id,
                'purpose': consent.purpose,
                'consent_version': consent.consent_version,
                'granted_at': consent.created_at.isoformat(),
                'legal_basis': consent.legal_basis,
                'retention_period_days': consent.retention_period_days
            } for consent in consents]

        except Exception as e:
            current_app.logger.error(f"Erro ao obter consentimentos LGPD: {str(e)}")
            return []

    @staticmethod
    def anonymize_user_data(user_id):
        """
        Anonimiza dados do usuário conforme LGPD

        Args:
            user_id: ID do usuário a ser anonimizado
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("Usuário não encontrado")

            # Manter dados essenciais para auditoria mas anonimizar informações pessoais
            original_email = user.email
            original_name = user.full_name

            # Anonimizar dados pessoais
            user.email = f"anonimizado_{user_id}@deleted.local"
            user.full_name = f"Usuário Anonimizado {user_id}"
            user.username = f"anon_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}"
            user.is_active = False

            db.session.commit()

            # Auditoria da anonimização
            AuditService.log_operation(
                entity_type='user',
                entity_id=user_id,
                operation='data_anonymized',
                operation_details={
                    'original_email': original_email,
                    'original_name': original_name,
                    'anonymization_date': datetime.utcnow().isoformat()
                },
                compliance_level='critical'
            )

            return True

        except Exception as e:
            current_app.logger.error(f"Erro na anonimização LGPD: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def generate_lgpd_compliance_report():
        """
        Gera relatório de compliance LGPD

        Returns:
            Relatório de compliance LGPD
        """
        try:
            # Contar titulares de dados
            data_subjects = User.query.filter_by(is_active=True).count()

            # Contar consentimentos ativos
            active_consents = DataProcessingConsent.query.filter_by(is_active=True).count()

            # Contar solicitações de direitos
            total_requests = DataSubjectRequest.query.count()
            pending_requests = DataSubjectRequest.query.filter_by(status='pending').count()
            completed_requests = DataSubjectRequest.query.filter_by(status='completed').count()

            # Análise de dados pessoais por categoria
            personal_data_categories = {
                'user_profiles': User.query.count(),
                'audit_logs': AuditLog.query.filter_by(compliance_level='critical').count(),
                'electronic_signatures': ElectronicSignature.query.count(),
                'consent_records': DataProcessingConsent.query.count()
            }

            # Verificar retenção de dados
            retention_analysis = LGPDService._analyze_data_retention()

            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'lgpd_compliance_summary': {
                    'data_subjects_count': data_subjects,
                    'active_consents_count': active_consents,
                    'consent_rate': (active_consents / data_subjects * 100) if data_subjects > 0 else 0,
                    'total_requests': total_requests,
                    'pending_requests': pending_requests,
                    'completed_requests': completed_requests,
                    'request_completion_rate': (completed_requests / total_requests * 100) if total_requests > 0 else 100
                },
                'personal_data_inventory': personal_data_categories,
                'data_retention_analysis': retention_analysis,
                'recommendations': LGPDService._generate_lgpd_recommendations(
                    data_subjects, active_consents, pending_requests
                ),
                'compliance_score': LGPDService._calculate_lgpd_compliance_score(
                    data_subjects, active_consents, pending_requests
                )
            }

            return report

        except Exception as e:
            current_app.logger.error(f"Erro na geração do relatório LGPD: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def _analyze_data_retention():
        """Analisa retenção de dados conforme LGPD"""
        try:
            # Análise de dados próximos à expiração
            thirty_days_from_now = datetime.utcnow() + timedelta(days=30)

            expiring_soon = AuditLog.query.filter(
                AuditLog.timestamp <= thirty_days_from_now,
                AuditLog.retention_period.isnot(None)
            ).count()

            # Dados já expirados (em produção, deveriam ser removidos)
            expired_data = AuditLog.query.filter(
                AuditLog.timestamp <= datetime.utcnow() - timedelta(days=2555)
            ).count()

            return {
                'expiring_soon_count': expiring_soon,
                'expired_data_count': expired_data,
                'retention_policy_days': 2555,
                'next_review_date': thirty_days_from_now.date().isoformat()
            }

        except Exception as e:
            current_app.logger.error(f"Erro na análise de retenção LGPD: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def _generate_lgpd_recommendations(data_subjects, active_consents, pending_requests):
        """Gera recomendações de compliance LGPD"""
        recommendations = []

        if active_consents / max(data_subjects, 1) < 0.8:
            recommendations.append({
                'priority': 'high',
                'category': 'consent_management',
                'title': 'Melhorar gestão de consentimentos',
                'description': 'Baixa taxa de consentimentos ativos detectada',
                'action': 'Implementar processo de coleta de consentimento mais eficiente'
            })

        if pending_requests > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'data_subject_rights',
                'title': 'Processar solicitações pendentes',
                'description': f'{pending_requests} solicitações de titulares aguardando processamento',
                'action': 'Designar equipe para processar solicitações dentro do prazo legal (15 dias)'
            })

        recommendations.append({
            'priority': 'medium',
            'category': 'data_mapping',
            'title': 'Manter inventário de dados pessoais',
            'description': 'Documentar todas as categorias de dados pessoais tratados',
            'action': 'Atualizar e manter inventário de dados pessoais conforme Art. 37 LGPD'
        })

        return recommendations

    @staticmethod
    def _calculate_lgpd_compliance_score(data_subjects, active_consents, pending_requests):
        """Calcula score de compliance LGPD"""
        # Base score
        score = 50

        # Consentimento (30 pontos)
        if data_subjects > 0:
            consent_rate = active_consents / data_subjects
            score += consent_rate * 30

        # Processamento de solicitações (20 pontos)
        if pending_requests == 0:
            score += 20
        elif pending_requests <= 2:
            score += 10
        # pending_requests > 2 não adiciona pontos

        return min(score, 100)

    @staticmethod
    def check_data_minimization(user_id, operation_type):
        """
        Verifica princípio da minimização de dados LGPD

        Args:
            user_id: ID do usuário
            operation_type: Tipo de operação sendo realizada

        Returns:
            Validação de minimização
        """
        try:
            # Em produção: implementar lógica de verificação baseada na operação
            # Por exemplo:
            # - Verificar se dados solicitados são necessários para a operação
            # - Validar se há consentimento para a finalidade específica
            # - Verificar se dados estão sendo retidos apenas pelo período necessário

            validation_result = {
                'is_minimized': True,
                'required_consent': DataProcessingPurpose.USER_MANAGEMENT.value,
                'retention_period_days': 2555,
                'validation_date': datetime.utcnow().isoformat(),
                'operation_type': operation_type
            }

            return validation_result

        except Exception as e:
            current_app.logger.error(f"Erro na verificação de minimização LGPD: {str(e)}")
            return {
                'is_minimized': False,
                'error': str(e)
            }

# Modelos para LGPD (se não existirem)
try:
    class DataProcessingConsent(db.Model):
        """Consentimento para tratamento de dados pessoais"""
        __tablename__ = 'data_processing_consents'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        purpose = db.Column(db.String(100), nullable=False)  # Finalidade do tratamento
        consent_version = db.Column(db.String(20), nullable=False)
        consent_data = db.Column(db.JSON)  # Dados específicos do consentimento

        # Controle legal
        legal_basis = db.Column(db.String(50), default='consent')  # consent, legitimate_interest, etc.
        retention_period_days = db.Column(db.Integer, default=2555)  # Dias de retenção

        # Contexto da coleta
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.Text)
        collected_at = db.Column(db.DateTime, default=datetime.utcnow)

        # Controle de validade
        is_active = db.Column(db.Boolean, default=True)
        withdrawn_at = db.Column(db.DateTime)

        # Relacionamentos
        user = db.relationship('User', backref='data_consents')

    class DataSubjectRequest(db.Model):
        """Solicitações de direitos do titular de dados"""
        __tablename__ = 'data_subject_requests'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        request_type = db.Column(db.String(50), nullable=False)  # Tipo de direito solicitado
        description = db.Column(db.Text)
        contact_email = db.Column(db.String(255))

        # Controle de processamento
        status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, rejected
        priority = db.Column(db.String(20), default='normal')

        # Dados da resposta
        response_data = db.Column(db.JSON)
        processed_at = db.Column(db.DateTime)
        processed_by = db.Column(db.Integer)  # ID do usuário que processou

        # Relacionamentos
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        user = db.relationship('User', backref='data_requests')

except NameError:
    # Modelos já definidos em outro lugar
    pass

# Instância global
lgpd_service = LGPDService()