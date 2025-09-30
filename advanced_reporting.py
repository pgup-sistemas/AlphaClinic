"""
Sistema Avançado de Relatórios
Gera relatórios customizáveis em múltiplos formatos (PDF, Excel, HTML)
"""

import pandas as pd
from datetime import datetime, timedelta
from flask import current_app, render_template
from models import (
    db, Document, Audit, NonConformity, CAPA, User, Team,
    Process, Norm, AuditLog, DocumentStatus, CAPAStatus
)
from sqlalchemy import func, and_, or_, text
import json
import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns

class AdvancedReportingService:
    """Serviço avançado para geração de relatórios"""

    def __init__(self):
        self.report_templates = {
            'compliance_overview': self._generate_compliance_overview,
            'audit_effectiveness': self._generate_audit_effectiveness_report,
            'nc_analysis': self._generate_nc_analysis_report,
            'capa_status': self._generate_capa_status_report,
            'system_usage': self._generate_system_usage_report,
            'custom_dashboard': self._generate_custom_dashboard_report
        }

    def generate_report(self, report_type, format='pdf', filters=None, user_id=None):
        """
        Gera relatório no formato especificado

        Args:
            report_type: Tipo de relatório
            format: Formato de saída (pdf, excel, html, json)
            filters: Filtros para o relatório
            user_id: ID do usuário solicitante

        Returns:
            Dados do relatório em formato especificado
        """
        try:
            if report_type not in self.report_templates:
                return {'error': f'Tipo de relatório não suportado: {report_type}'}

            # Gerar dados do relatório
            report_data = self.report_templates[report_type](filters, user_id)

            # Converter para formato solicitado
            if format == 'pdf':
                return self._export_to_pdf(report_data, report_type)
            elif format == 'excel':
                return self._export_to_excel(report_data, report_type)
            elif format == 'html':
                return self._export_to_html(report_data, report_type)
            elif format == 'json':
                return self._export_to_json(report_data, report_type)
            else:
                return {'error': f'Formato não suportado: {format}'}

        except Exception as e:
            current_app.logger.error(f"Erro na geração do relatório: {str(e)}")
            return {'error': str(e)}

    def _generate_compliance_overview(self, filters=None, user_id=None):
        """Gera relatório geral de compliance"""
        # Período do relatório
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)

        if filters and 'start_date' in filters:
            start_date = datetime.fromisoformat(filters['start_date'])
        if filters and 'end_date' in filters:
            end_date = datetime.fromisoformat(filters['end_date'])

        report_data = {
            'title': 'Relatório de Compliance - Visão Geral',
            'period': {
                'start': start_date.date().isoformat(),
                'end': end_date.date().isoformat()
            },
            'generated_at': datetime.utcnow().isoformat(),
            'generated_by': user_id,
            'sections': {
                'documents': self._get_document_compliance_data(start_date, end_date),
                'audits': self._get_audit_compliance_data(start_date, end_date),
                'non_conformities': self._get_nc_compliance_data(start_date, end_date),
                'capa': self._get_capa_compliance_data(start_date, end_date),
                'system': self._get_system_compliance_data(start_date, end_date)
            },
            'summary': self._generate_compliance_summary()
        }

        return report_data

    def _get_document_compliance_data(self, start_date, end_date):
        """Dados de compliance de documentos"""
        # Query otimizada com índices
        docs_by_status = db.session.query(
            Document.status,
            func.count(Document.id)
        ).filter(
            Document.created_at >= start_date,
            Document.created_at <= end_date
        ).group_by(Document.status).all()

        # Documentos publicados no período
        published_docs = Document.query.filter(
            Document.status == DocumentStatus.PUBLISHED,
            Document.published_at >= start_date,
            Document.published_at <= end_date
        ).count()

        return {
            'status_distribution': {status.value: count for status, count in docs_by_status},
            'published_in_period': published_docs,
            'total_documents': sum(count for _, count in docs_by_status)
        }

    def _get_audit_compliance_data(self, start_date, end_date):
        """Dados de compliance de auditorias"""
        audits_by_status = db.session.query(
            Audit.status,
            func.count(Audit.id)
        ).filter(
            Audit.created_at >= start_date,
            Audit.created_at <= end_date
        ).group_by(Audit.status).all()

        # Auditorias concluídas com NCs
        completed_audits = Audit.query.filter(
            Audit.status == 'completed',
            Audit.actual_date >= start_date.date(),
            Audit.actual_date <= end_date.date()
        ).all()

        audits_with_ncs = sum(1 for audit in completed_audits if audit.non_conformities)

        return {
            'status_distribution': {status: count for status, count in audits_by_status},
            'completed_audits': len(completed_audits),
            'audits_with_ncs': audits_with_ncs,
            'effectiveness_rate': (audits_with_ncs / len(completed_audits) * 100) if completed_audits else 0
        }

    def _get_nc_compliance_data(self, start_date, end_date):
        """Dados de compliance de NCs"""
        ncs_by_status = db.session.query(
            NonConformity.status,
            func.count(NonConformity.id)
        ).filter(
            NonConformity.created_at >= start_date,
            NonConformity.created_at <= end_date
        ).group_by(NonConformity.status).all()

        # NCs por severidade
        ncs_by_severity = db.session.query(
            NonConformity.severity,
            func.count(NonConformity.id)
        ).filter(
            NonConformity.created_at >= start_date,
            NonConformity.created_at <= end_date
        ).group_by(NonConformity.severity).all()

        # Tempo médio de resolução
        resolved_ncs = NonConformity.query.filter(
            NonConformity.status == 'resolved',
            NonConformity.actual_resolution_date >= start_date.date(),
            NonConformity.actual_resolution_date <= end_date.date()
        ).all()

        avg_resolution_time = 0
        if resolved_ncs:
            resolution_times = []
            for nc in resolved_ncs:
                if nc.identified_date and nc.actual_resolution_date:
                    days = (nc.actual_resolution_date - nc.identified_date).days
                    if days >= 0:
                        resolution_times.append(days)

            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0

        return {
            'status_distribution': {status: count for status, count in ncs_by_status},
            'severity_distribution': {severity: count for severity, count in ncs_by_severity},
            'total_ncs': sum(count for _, count in ncs_by_status),
            'avg_resolution_time_days': round(avg_resolution_time, 1)
        }

    def _get_capa_compliance_data(self, start_date, end_date):
        """Dados de compliance de CAPA"""
        capas_by_status = db.session.query(
            CAPA.status,
            func.count(CAPA.id)
        ).filter(
            CAPA.created_at >= start_date,
            CAPA.created_at <= end_date
        ).group_by(CAPA.status).all()

        # CAPAs por tipo
        capas_by_type = db.session.query(
            CAPA.capa_type,
            func.count(CAPA.id)
        ).filter(
            CAPA.created_at >= start_date,
            CAPA.created_at <= end_date
        ).group_by(CAPA.capa_type).all()

        # Efetividade dos CAPAs fechados
        closed_capas = CAPA.query.filter(
            CAPA.status == CAPAStatus.CLOSED,
            CAPA.actual_completion_date >= start_date.date(),
            CAPA.actual_completion_date <= end_date.date()
        ).all()

        effectiveness_scores = [capa.effectiveness_rating for capa in closed_capas if capa.effectiveness_rating]

        return {
            'status_distribution': {status.value: count for status, count in capas_by_status},
            'type_distribution': {capa_type.value: count for capa_type, count in capas_by_type},
            'total_capas': sum(count for _, count in capas_by_status),
            'avg_effectiveness': sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
        }

    def _get_system_compliance_data(self, start_date, end_date):
        """Dados de compliance do sistema"""
        # Usuários ativos
        active_users = User.query.filter(
            User.last_login >= start_date,
            User.is_active == True
        ).count()

        # Logs de auditoria no período
        audit_logs = AuditLog.query.filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).count()

        # Assinaturas digitais
        digital_signatures = db.session.query(func.count(ElectronicSignature.id)).scalar()

        return {
            'active_users': active_users,
            'audit_logs_count': audit_logs,
            'digital_signatures_count': digital_signatures,
            'system_uptime_days': (end_date - start_date).days
        }

    def _generate_compliance_summary(self):
        """Gera resumo executivo do compliance"""
        # Calcular scores de compliance
        doc_compliance = self._calculate_document_compliance_score()
        audit_compliance = self._calculate_audit_compliance_score()
        nc_compliance = self._calculate_nc_compliance_score()

        overall_score = (doc_compliance + audit_compliance + nc_compliance) / 3

        return {
            'overall_compliance_score': round(overall_score, 1),
            'document_compliance_score': round(doc_compliance, 1),
            'audit_compliance_score': round(audit_compliance, 1),
            'nc_compliance_score': round(nc_compliance, 1),
            'compliance_level': self._get_compliance_level(overall_score)
        }

    def _calculate_document_compliance_score(self):
        """Calcula score de compliance de documentos"""
        total_docs = Document.query.count()
        published_docs = Document.query.filter_by(status=DocumentStatus.PUBLISHED).count()

        if total_docs == 0:
            return 100

        return (published_docs / total_docs) * 100

    def _calculate_audit_compliance_score(self):
        """Calcula score de compliance de auditorias"""
        total_audits = Audit.query.count()
        completed_audits = Audit.query.filter_by(status='completed').count()

        if total_audits == 0:
            return 100

        return (completed_audits / total_audits) * 100

    def _calculate_nc_compliance_score(self):
        """Calcula score de compliance de NCs"""
        total_ncs = NonConformity.query.count()
        resolved_ncs = NonConformity.query.filter_by(status='resolved').count()

        if total_ncs == 0:
            return 100

        return (resolved_ncs / total_ncs) * 100

    def _get_compliance_level(self, score):
        """Determina nível de compliance baseado no score"""
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'satisfactory'
        else:
            return 'needs_improvement'

    def _export_to_pdf(self, report_data, report_type):
        """Exporta relatório para PDF"""
        try:
            # Criar PDF em memória
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=30
            )
            elements.append(Paragraph(report_data['title'], title_style))

            # Período
            elements.append(Paragraph(f"Período: {report_data['period']['start']} a {report_data['period']['end']}", styles['Normal']))
            elements.append(Spacer(1, 20))

            # Resumo executivo
            if 'summary' in report_data:
                summary = report_data['summary']
                elements.append(Paragraph("Resumo Executivo", styles['Heading2']))
                elements.append(Paragraph(f"Score Geral de Compliance: {summary['overall_compliance_score']}%", styles['Normal']))
                elements.append(Paragraph(f"Nível: {summary['compliance_level'].replace('_', ' ').title()}", styles['Normal']))
                elements.append(Spacer(1, 20))

            # Seções do relatório
            for section_name, section_data in report_data.get('sections', {}).items():
                elements.append(Paragraph(section_name.replace('_', ' ').title(), styles['Heading2']))

                # Converter dados para tabela
                if isinstance(section_data, dict):
                    table_data = [[k.replace('_', ' ').title(), str(v)] for k, v in section_data.items()]
                    if table_data:
                        table = Table(table_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 14),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        elements.append(table)

                elements.append(Spacer(1, 20))

            # Construir PDF
            doc.build(elements)

            # Retornar dados do PDF
            buffer.seek(0)
            pdf_data = buffer.getvalue()
            buffer.close()

            return {
                'filename': f'{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                'data': base64.b64encode(pdf_data).decode('utf-8'),
                'mimetype': 'application/pdf',
                'size': len(pdf_data)
            }

        except Exception as e:
            current_app.logger.error(f"Erro na geração do PDF: {str(e)}")
            return {'error': f'Erro na geração do PDF: {str(e)}'}

    def _export_to_excel(self, report_data, report_type):
        """Exporta relatório para Excel"""
        try:
            # Criar Excel em memória
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Sheet de resumo
                summary_data = []
                if 'summary' in report_data:
                    for key, value in report_data['summary'].items():
                        summary_data.append({'Métrica': key.replace('_', ' ').title(), 'Valor': value})

                if summary_data:
                    df_summary = pd.DataFrame(summary_data)
                    df_summary.to_excel(writer, sheet_name='Resumo', index=False)

                # Sheets por seção
                for section_name, section_data in report_data.get('sections', {}).items():
                    if isinstance(section_data, dict):
                        df = pd.DataFrame([section_data])
                        df.to_excel(writer, sheet_name=section_name[:31], index=False)  # Limitar nome da sheet

            output.seek(0)
            excel_data = output.getvalue()
            output.close()

            return {
                'filename': f'{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                'data': base64.b64encode(excel_data).decode('utf-8'),
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'size': len(excel_data)
            }

        except Exception as e:
            current_app.logger.error(f"Erro na geração do Excel: {str(e)}")
            return {'error': f'Erro na geração do Excel: {str(e)}'}

    def _export_to_html(self, report_data, report_type):
        """Exporta relatório para HTML"""
        try:
            # Renderizar template HTML
            html_content = render_template(
                'reports/advanced_report.html',
                report_data=report_data,
                report_type=report_type,
                generated_at=datetime.utcnow()
            )

            return {
                'filename': f'{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html',
                'data': base64.b64encode(html_content.encode('utf-8')).decode('utf-8'),
                'mimetype': 'text/html',
                'size': len(html_content)
            }

        except Exception as e:
            current_app.logger.error(f"Erro na geração do HTML: {str(e)}")
            return {'error': f'Erro na geração do HTML: {str(e)}'}

    def _export_to_json(self, report_data, report_type):
        """Exporta relatório para JSON"""
        return {
            'filename': f'{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            'data': json.dumps(report_data, indent=2, default=str),
            'mimetype': 'application/json',
            'size': len(json.dumps(report_data, default=str))
        }

    def _generate_audit_effectiveness_report(self, filters=None, user_id=None):
        """Gera relatório de efetividade de auditorias"""
        # Implementação específica para auditorias
        return {
            'title': 'Relatório de Efetividade de Auditorias',
            'type': 'audit_effectiveness',
            'generated_at': datetime.utcnow().isoformat()
        }

    def _generate_nc_analysis_report(self, filters=None, user_id=None):
        """Gera relatório de análise de NCs"""
        # Implementação específica para NCs
        return {
            'title': 'Relatório de Análise de Não Conformidades',
            'type': 'nc_analysis',
            'generated_at': datetime.utcnow().isoformat()
        }

    def _generate_capa_status_report(self, filters=None, user_id=None):
        """Gera relatório de status de CAPAs"""
        # Implementação específica para CAPAs
        return {
            'title': 'Relatório de Status de CAPAs',
            'type': 'capa_status',
            'generated_at': datetime.utcnow().isoformat()
        }

    def _generate_system_usage_report(self, filters=None, user_id=None):
        """Gera relatório de uso do sistema"""
        # Implementação específica para uso do sistema
        return {
            'title': 'Relatório de Uso do Sistema',
            'type': 'system_usage',
            'generated_at': datetime.utcnow().isoformat()
        }

    def _generate_custom_dashboard_report(self, filters=None, user_id=None):
        """Gera relatório de dashboard customizado"""
        # Implementação específica para dashboard
        return {
            'title': 'Relatório de Dashboard Customizado',
            'type': 'custom_dashboard',
            'generated_at': datetime.utcnow().isoformat()
        }

# Instância global
reporting_service = AdvancedReportingService()