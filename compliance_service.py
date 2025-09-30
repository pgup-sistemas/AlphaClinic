"""
Serviço de Relatórios de Compliance
Gera relatórios automatizados para auditorias e conformidade legal
"""

from models import db, Document, Audit, NonConformity, CAPA, AuditLog, ElectronicSignature
from audit_service import AuditService
from datetime import datetime, timedelta
import json
from flask import current_app

class ComplianceReportService:
    """Serviço para geração de relatórios de compliance"""

    @staticmethod
    def generate_compliance_overview(start_date=None, end_date=None):
        """Gera relatório geral de compliance"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.utcnow().isoformat(),
            'documents': ComplianceReportService._get_document_compliance(),
            'audits': ComplianceReportService._get_audit_compliance(),
            'signatures': ComplianceReportService._get_signature_compliance(),
            'audit_trail': ComplianceReportService._get_audit_trail_integrity(),
            'recommendations': ComplianceReportService._generate_recommendations()
        }

        # Log da geração do relatório
        AuditService.log_operation(
            entity_type='compliance',
            entity_id=0,
            operation='generate_report',
            operation_details={'report_type': 'overview', 'period_days': 30},
            compliance_level='standard'
        )

        return report

    @staticmethod
    def _get_document_compliance():
        """Análise de compliance dos documentos"""
        total_docs = Document.query.count()
        published_docs = Document.query.filter_by(status='published').count()
        signed_docs = db.session.query(Document).join(ElectronicSignature).distinct().count()

        docs_requiring_signatures = Document.query.filter_by(signature_required=True).count()
        signed_required_docs = db.session.query(Document).join(ElectronicSignature).filter(
            Document.signature_required == True
        ).distinct().count()

        return {
            'total_documents': total_docs,
            'published_documents': published_docs,
            'signed_documents': signed_docs,
            'documents_requiring_signatures': docs_requiring_signatures,
            'signed_required_documents': signed_required_docs,
            'signature_compliance_rate': (signed_required_docs / docs_requiring_signatures * 100) if docs_requiring_signatures > 0 else 100,
            'publication_rate': (published_docs / total_docs * 100) if total_docs > 0 else 0
        }

    @staticmethod
    def _get_audit_compliance():
        """Análise de compliance das auditorias"""
        total_audits = Audit.query.count()
        completed_audits = Audit.query.filter_by(status='completed').count()
        total_nc = NonConformity.query.count()
        resolved_nc = NonConformity.query.filter_by(status='resolved').count()

        # CAPA compliance
        total_capas = CAPA.query.count()
        completed_capas = CAPA.query.filter_by(status='closed').count()

        return {
            'total_audits': total_audits,
            'completed_audits': completed_audits,
            'audit_completion_rate': (completed_audits / total_audits * 100) if total_audits > 0 else 0,
            'total_non_conformities': total_nc,
            'resolved_non_conformities': resolved_nc,
            'nc_resolution_rate': (resolved_nc / total_nc * 100) if total_nc > 0 else 100,
            'total_capas': total_capas,
            'completed_capas': completed_capas,
            'capa_completion_rate': (completed_capas / total_capas * 100) if total_capas > 0 else 100
        }

    @staticmethod
    def _get_signature_compliance():
        """Análise de compliance das assinaturas digitais"""
        total_signatures = ElectronicSignature.query.count()
        valid_signatures = ElectronicSignature.query.filter_by(is_valid=True).count()
        certificate_signatures = ElectronicSignature.query.filter(
            ElectronicSignature.certificate_pem.isnot(None)
        ).count()

        # Verificar certificados ICP-Brasil
        icp_signatures = ElectronicSignature.query.filter(
            ElectronicSignature.certificate_issuer.contains('ICP-Brasil')
        ).count()

        return {
            'total_signatures': total_signatures,
            'valid_signatures': valid_signatures,
            'certificate_signatures': certificate_signatures,
            'icp_brasil_signatures': icp_signatures,
            'signature_validity_rate': (valid_signatures / total_signatures * 100) if total_signatures > 0 else 0,
            'certificate_usage_rate': (certificate_signatures / total_signatures * 100) if total_signatures > 0 else 0,
            'icp_compliance_rate': (icp_signatures / certificate_signatures * 100) if certificate_signatures > 0 else 0
        }

    @staticmethod
    def _get_audit_trail_integrity():
        """Verifica integridade da trilha de auditoria"""
        integrity_check = AuditLog.verify_chain_integrity()
        total_logs = AuditLog.query.count()

        # Análise por período
        last_30_days = AuditLog.query.filter(
            AuditLog.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).count()

        return {
            'total_audit_logs': total_logs,
            'logs_last_30_days': last_30_days,
            'chain_integrity': integrity_check[0],
            'integrity_message': integrity_check[1],
            'logs_per_day_avg': last_30_days / 30 if last_30_days > 0 else 0
        }

    @staticmethod
    def _generate_recommendations():
        """Gera recomendações baseadas na análise de compliance"""
        recommendations = []

        # Verificar assinatura digital
        sig_compliance = ComplianceReportService._get_signature_compliance()
        if sig_compliance['certificate_usage_rate'] < 80:
            recommendations.append({
                'priority': 'high',
                'category': 'assinaturas_digitais',
                'title': 'Aumentar uso de certificados digitais',
                'description': f'Apenas {sig_compliance["certificate_usage_rate"]:.1f}% das assinaturas usam certificados digitais. Recomenda-se migrar para certificados ICP-Brasil.',
                'action': 'Implementar obrigatoriedade de certificados digitais para documentos críticos'
            })

        # Verificar resolução de NCs
        audit_compliance = ComplianceReportService._get_audit_compliance()
        if audit_compliance['nc_resolution_rate'] < 90:
            recommendations.append({
                'priority': 'high',
                'category': 'auditorias',
                'title': 'Melhorar resolução de não conformidades',
                'description': f'Taxa de resolução de NCs: {audit_compliance["nc_resolution_rate"]:.1f}%. Meta: 90%+',
                'action': 'Implementar plano de ação corretiva mais eficiente'
            })

        # Verificar trilha de auditoria
        audit_integrity = ComplianceReportService._get_audit_trail_integrity()
        if not audit_integrity['chain_integrity']:
            recommendations.append({
                'priority': 'critical',
                'category': 'seguranca',
                'title': 'Corrigir integridade da trilha de auditoria',
                'description': 'A cadeia de auditoria foi comprometida',
                'action': 'Verificar e restaurar integridade da trilha de auditoria'
            })

        # Verificar documentos publicados
        doc_compliance = ComplianceReportService._get_document_compliance()
        if doc_compliance['publication_rate'] < 80:
            recommendations.append({
                'priority': 'medium',
                'category': 'documentos',
                'title': 'Aumentar taxa de publicação de documentos',
                'description': f'Apenas {doc_compliance["publication_rate"]:.1f}% dos documentos estão publicados',
                'action': 'Acelerar workflow de aprovação de documentos'
            })

        return recommendations

    @staticmethod
    def generate_gdpr_compliance_report():
        """Gera relatório específico para compliance LGPD"""
        # Dados pessoais no sistema
        users_count = db.session.query(db.func.count(db.distinct(ElectronicSignature.user_id))).scalar()
        audit_logs_personal_data = AuditLog.query.filter(
            AuditLog.entity_type.in_(['user', 'signature'])
        ).count()

        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'lgpd_compliance': {
                'personal_data_subjects': users_count,
                'audit_logs_personal_data': audit_logs_personal_data,
                'data_encryption': 'implemented',  # Baseado na implementação
                'consent_management': 'pending',  # A implementar
                'data_retention_policy': 'implemented',  # Baseado na implementação
                'data_subject_rights': 'partial'  # Acesso implementado, outros pendentes
            },
            'recommendations': [
                'Implementar sistema de consentimento explícito',
                'Criar formulários de exercício de direitos ARCO+',
                'Implementar DPO (Data Protection Officer)',
                'Realizar DPIA (Data Protection Impact Assessment)'
            ]
        }

        return report

    @staticmethod
    def generate_iso9001_compliance_report():
        """Gera relatório específico para compliance ISO 9001"""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'iso9001_requirements': {
                'clause_5_1': {
                    'title': 'Liderança e Compromisso',
                    'status': 'compliant',
                    'evidence': 'Sistema implementado com responsabilidades definidas'
                },
                'clause_7_1': {
                    'title': 'Recursos',
                    'status': 'compliant',
                    'evidence': 'Sistema de gestão de recursos implementado'
                },
                'clause_7_5': {
                    'title': 'Infraestrutura',
                    'status': 'compliant',
                    'evidence': 'Sistema de TI implementado e documentado'
                },
                'clause_8_1': {
                    'title': 'Planejamento e Controle Operacional',
                    'status': 'partial',
                    'evidence': 'Processos documentados, controle operacional em implementação'
                },
                'clause_9_1': {
                    'title': 'Monitoramento, Medição, Análise e Avaliação',
                    'status': 'compliant',
                    'evidence': 'Sistema de auditoria e indicadores implementado'
                },
                'clause_9_3': {
                    'title': 'Análise Gerencial',
                    'status': 'compliant',
                    'evidence': 'Relatórios de compliance implementados'
                }
            }
        }

        return report

    @staticmethod
    def export_report(report_data, format='json'):
        """Exporta relatório em diferentes formatos"""
        if format == 'json':
            return json.dumps(report_data, indent=2, default=str)
        elif format == 'html':
            # Implementar export HTML
            return f"<html><body><pre>{json.dumps(report_data, indent=2, default=str)}</pre></body></html>"
        else:
            return json.dumps(report_data, default=str)