#!/usr/bin/env python3
"""
Serviço de Analytics e BI para Alphaclin QMS
Gerencia coleta, processamento e visualização de dados analíticos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import current_app
from models import (
    db, Document, Audit, NonConformity, CAPA, User, Team,
    Process, Norm, CIPAMeeting, ImprovementCycle, OperationalEvent,
    AnalyticsMetric, AnalyticsData, DashboardWidget, DashboardLayout,
    DocumentStatus, CAPAStatus, ImprovementStatus
)
from sqlalchemy import func, text
import json

class AnalyticsService:
    """Serviço principal de analytics"""

    def __init__(self):
        self.db = db

    def collect_daily_metrics(self):
        """Coleta métricas diárias de todas as funcionalidades"""
        today = datetime.utcnow().date()

        metrics_data = []

        # === DOCUMENTOS ===
        doc_stats = self.db.session.query(
            Document.status,
            func.count(Document.id)
        ).group_by(Document.status).all()

        for status, count in doc_stats:
            metrics_data.append({
                'metric_name': f'documents_{status.value}',
                'category': 'documents',
                'value': count,
                'period': today,
                'period_type': 'daily'
            })

        # === AUDITORIAS ===
        audit_stats = self.db.session.query(
            Audit.status,
            func.count(Audit.id)
        ).group_by(Audit.status).all()

        for status, count in audit_stats:
            metrics_data.append({
                'metric_name': f'audits_{status}',
                'category': 'audits',
                'value': count,
                'period': today,
                'period_type': 'daily'
            })

        # === NÃO CONFORMIDADES ===
        nc_stats = self.db.session.query(
            NonConformity.status,
            func.count(NonConformity.id)
        ).group_by(NonConformity.status).all()

        for status, count in nc_stats:
            metrics_data.append({
                'metric_name': f'nc_{status}',
                'category': 'non_conformities',
                'value': count,
                'period': today,
                'period_type': 'daily'
            })

        # === CAPA ===
        capa_stats = self.db.session.query(
            CAPA.status,
            func.count(CAPA.id)
        ).group_by(CAPA.status).all()

        for status, count in capa_stats:
            metrics_data.append({
                'metric_name': f'capa_{status.value}',
                'category': 'capa',
                'value': count,
                'period': today,
                'period_type': 'daily'
            })

        # === USUÁRIOS ===
        active_users = User.query.filter(
            User.last_login >= datetime.utcnow() - timedelta(days=30)
        ).count()

        metrics_data.append({
            'metric_name': 'active_users_30d',
            'category': 'system',
            'value': active_users,
            'period': today,
            'period_type': 'daily'
        })

        # === SALVAR MÉTRICAS ===
        for metric_data in metrics_data:
            # Verificar se já existe
            existing = AnalyticsData.query.filter_by(
                metric_name=metric_data['metric_name'],
                period=metric_data['period'],
                period_type=metric_data['period_type']
            ).first()

            if not existing:
                # Criar nova entrada
                metric = AnalyticsMetric.query.filter_by(
                    name=metric_data['metric_name'],
                    category=metric_data['category']
                ).first()

                if not metric:
                    metric = AnalyticsMetric(
                        name=metric_data['metric_name'],
                        category=metric_data['category'],
                        metric_type='count',
                        calculation_method='daily_collection'
                    )
                    self.db.session.add(metric)
                    self.db.session.flush()

                data_point = AnalyticsData(
                    metric_id=metric.id,
                    period=metric_data['period'],
                    period_type=metric_data['period_type'],
                    value=metric_data['value'],
                    data_source='database'
                )
                self.db.session.add(data_point)

        self.db.session.commit()
        return len(metrics_data)

    def get_dashboard_data(self, user_id=None, layout_name='default'):
        """Obtém dados para o dashboard"""
        try:
            # Verificar se o banco está disponível
            if not self.db or not self.db.session:
                print("Banco de dados não disponível")
                return self._get_empty_metrics()

            # Métricas principais
            main_metrics = {
                'documents': self._get_document_metrics(),
                'audits': self._get_audit_metrics(),
                'non_conformities': self._get_nc_metrics(),
                'capa': self._get_capa_metrics(),
                'system': self._get_system_metrics(),
                'operational': self._get_operational_metrics()
            }

            # Layout personalizado se existir
            if user_id:
                try:
                    layout = DashboardLayout.query.filter_by(
                        user_id=user_id,
                        layout_name=layout_name,
                        is_active=True
                    ).first()

                    if layout:
                        main_metrics['layout'] = layout.layout_data
                        main_metrics['custom_widgets'] = self._get_custom_widgets(user_id)
                except Exception as e:
                    print(f"Erro ao carregar layout personalizado: {e}")

            return main_metrics

        except Exception as e:
            print(f"Erro ao coletar dados do dashboard: {e}")
            return self._get_empty_metrics()

    def _get_empty_metrics(self):
        """Retorna métricas vazias em caso de erro"""
        return {
            'documents': {'total': 0, 'draft': 0, 'review': 0, 'published': 0, 'archived': 0, 'recent_30d': 0},
            'audits': {'total': 0, 'planned': 0, 'in_progress': 0, 'completed': 0, 'recent_30d': 0},
            'non_conformities': {'total': 0, 'open': 0, 'in_progress': 0, 'resolved': 0, 'closed': 0, 'overdue': 0},
            'capa': {'total': 0, 'draft': 0, 'approved': 0, 'implemented': 0, 'verified': 0, 'closed': 0},
            'system': {'total_users': 0, 'active_users': 0, 'total_teams': 0, 'total_processes': 0, 'total_norms': 0},
            'operational': {'cipa_total': 0, 'cipa_scheduled': 0, 'improvements_total': 0, 'improvements_active': 0, 'operational_total': 0, 'operational_todo': 0}
        }

    def _get_document_metrics(self):
        """Métricas de documentos"""
        try:
            return {
                'total': Document.query.count(),
                'draft': Document.query.filter_by(status=DocumentStatus.DRAFT).count(),
                'review': Document.query.filter_by(status=DocumentStatus.REVIEW).count(),
                'published': Document.query.filter_by(status=DocumentStatus.PUBLISHED).count(),
                'archived': Document.query.filter_by(status=DocumentStatus.ARCHIVED).count(),
                'recent_30d': Document.query.filter(
                    Document.created_at >= datetime.utcnow() - timedelta(days=30)
                ).count()
            }
        except Exception as e:
            print(f"Erro ao obter métricas de documentos: {e}")
            return {'total': 0, 'draft': 0, 'review': 0, 'published': 0, 'archived': 0, 'recent_30d': 0}

    def _get_audit_metrics(self):
        """Métricas de auditorias"""
        try:
            return {
                'total': Audit.query.count(),
                'planned': Audit.query.filter_by(status='planned').count(),
                'in_progress': Audit.query.filter_by(status='in_progress').count(),
                'completed': Audit.query.filter_by(status='completed').count(),
                'recent_30d': Audit.query.filter(
                    Audit.created_at >= datetime.utcnow() - timedelta(days=30)
                ).count()
            }
        except Exception as e:
            print(f"Erro ao obter métricas de auditorias: {e}")
            return {'total': 0, 'planned': 0, 'in_progress': 0, 'completed': 0, 'recent_30d': 0}

    def _get_nc_metrics(self):
        """Métricas de não conformidades"""
        try:
            return {
                'total': NonConformity.query.count(),
                'open': NonConformity.query.filter_by(status='open').count(),
                'in_progress': NonConformity.query.filter_by(status='in_progress').count(),
                'resolved': NonConformity.query.filter_by(status='resolved').count(),
                'closed': NonConformity.query.filter_by(status='closed').count(),
                'overdue': NonConformity.query.filter(
                    NonConformity.target_resolution_date < datetime.utcnow().date(),
                    NonConformity.status.in_(['open', 'in_progress'])
                ).count()
            }
        except Exception as e:
            print(f"Erro ao obter métricas de NCs: {e}")
            return {'total': 0, 'open': 0, 'in_progress': 0, 'resolved': 0, 'closed': 0, 'overdue': 0}

    def _get_capa_metrics(self):
        """Métricas de CAPA"""
        try:
            return {
                'total': CAPA.query.count(),
                'draft': CAPA.query.filter_by(status=CAPAStatus.DRAFT).count(),
                'approved': CAPA.query.filter_by(status=CAPAStatus.APPROVED).count(),
                'implemented': CAPA.query.filter_by(status=CAPAStatus.IMPLEMENTED).count(),
                'verified': CAPA.query.filter_by(status=CAPAStatus.VERIFIED).count(),
                'closed': CAPA.query.filter_by(status=CAPAStatus.CLOSED).count()
            }
        except Exception as e:
            print(f"Erro ao obter métricas de CAPA: {e}")
            return {'total': 0, 'draft': 0, 'approved': 0, 'implemented': 0, 'verified': 0, 'closed': 0}

    def _get_system_metrics(self):
        """Métricas do sistema"""
        try:
            return {
                'total_users': User.query.count(),
                'active_users': User.query.filter_by(is_active=True).count(),
                'total_teams': Team.query.count(),
                'total_processes': Process.query.count(),
                'total_norms': Norm.query.filter_by(is_active=True).count()
            }
        except Exception as e:
            print(f"Erro ao obter métricas do sistema: {e}")
            return {'total_users': 0, 'active_users': 0, 'total_teams': 0, 'total_processes': 0, 'total_norms': 0}

    def _get_operational_metrics(self):
        """Métricas operacionais"""
        return {
            'cipa_total': CIPAMeeting.query.count(),
            'cipa_scheduled': CIPAMeeting.query.filter_by(status='scheduled').count(),
            'improvements_total': ImprovementCycle.query.count(),
            'improvements_active': ImprovementCycle.query.filter_by(status='active').count(),
            'operational_total': OperationalEvent.query.count(),
            'operational_todo': OperationalEvent.query.filter_by(status='todo').count()
        }

    def _get_custom_widgets(self, user_id):
        """Obtém widgets personalizados do usuário"""
        widgets = DashboardWidget.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(DashboardWidget.position_y, DashboardWidget.position_x).all()

        return [{
            'id': w.id,
            'name': w.name,
            'type': w.widget_type,
            'title': w.title,
            'config': w.config,
            'position': {'x': w.position_x, 'y': w.position_y},
            'size': {'width': w.width, 'height': w.height},
            'icon': w.icon,
            'color_scheme': w.color_scheme
        } for w in widgets]

    def get_chart_data(self, chart_type, period='30d', category=None):
        """Obtém dados para gráficos"""
        end_date = datetime.utcnow()
        if period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '30d':
            start_date = end_date - timedelta(days=30)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)

        if chart_type == 'documents_trend':
            return self._get_documents_trend(start_date, end_date)
        elif chart_type == 'audits_status':
            return self._get_audits_status()
        elif chart_type == 'nc_resolution_time':
            return self._get_nc_resolution_time()
        elif chart_type == 'capa_effectiveness':
            return self._get_capa_effectiveness()

        return {}

    def _get_documents_trend(self, start_date, end_date):
        """Tendência de documentos ao longo do tempo"""
        # Query para obter dados diários
        daily_data = self.db.session.query(
            func.date(Document.created_at).label('date'),
            func.count(Document.id).label('count')
        ).filter(
            Document.created_at >= start_date,
            Document.created_at <= end_date
        ).group_by(
            func.date(Document.created_at)
        ).order_by(
            func.date(Document.created_at)
        ).all()

        return {
            'labels': [str(row.date) for row in daily_data],
            'datasets': [{
                'label': 'Documentos Criados',
                'data': [row.count for row in daily_data],
                'borderColor': 'rgb(59, 130, 246)',
                'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                'tension': 0.1
            }]
        }

    def _get_audits_status(self):
        """Status das auditorias"""
        status_data = self.db.session.query(
            Audit.status,
            func.count(Audit.id)
        ).group_by(Audit.status).all()

        return {
            'labels': [status.title() for status, _ in status_data],
            'datasets': [{
                'label': 'Auditorias',
                'data': [count for _, count in status_data],
                'backgroundColor': [
                    'rgba(34, 197, 94, 0.8)',   # completed - green
                    'rgba(59, 130, 246, 0.8)',  # in_progress - blue
                    'rgba(251, 191, 36, 0.8)',  # planned - yellow
                    'rgba(239, 68, 68, 0.8)'    # cancelled - red
                ]
            }]
        }

    def _get_nc_resolution_time(self):
        """Tempo de resolução de NCs"""
        # NCs resolvidas nos últimos 90 dias
        resolved_ncs = NonConformity.query.filter(
            NonConformity.status == 'resolved',
            NonConformity.actual_resolution_date >= datetime.utcnow() - timedelta(days=90)
        ).all()

        resolution_times = []
        for nc in resolved_ncs:
            if nc.actual_resolution_date and nc.identified_date:
                days = (nc.actual_resolution_date - nc.identified_date).days
                resolution_times.append(days)

        if resolution_times:
            avg_time = sum(resolution_times) / len(resolution_times)
            return {
                'average_resolution_time': avg_time,
                'min_resolution_time': min(resolution_times),
                'max_resolution_time': max(resolution_times),
                'resolution_times': resolution_times
            }

        return {'average_resolution_time': 0}

    def _get_capa_effectiveness(self):
        """Efetividade dos CAPAs"""
        closed_capa = CAPA.query.filter_by(status=CAPAStatus.CLOSED).all()

        effectiveness_scores = []
        for capa in closed_capa:
            if capa.effectiveness_rating:
                effectiveness_scores.append(capa.effectiveness_rating)

        if effectiveness_scores:
            return {
                'average_effectiveness': sum(effectiveness_scores) / len(effectiveness_scores),
                'effectiveness_distribution': {
                    '1_star': effectiveness_scores.count(1),
                    '2_star': effectiveness_scores.count(2),
                    '3_star': effectiveness_scores.count(3),
                    '4_star': effectiveness_scores.count(4),
                    '5_star': effectiveness_scores.count(5)
                }
            }

        return {'average_effectiveness': 0}

    def export_data(self, export_format, data_type, filters=None):
        """Exporta dados em formato específico"""
        if data_type == 'documents':
            data = self._get_documents_export_data(filters)
        elif data_type == 'audits':
            data = self._get_audits_export_data(filters)
        elif data_type == 'ncs':
            data = self._get_ncs_export_data(filters)
        elif data_type == 'capa':
            data = self._get_capa_export_data(filters)
        else:
            return None

        if export_format == 'excel':
            return self._export_to_excel(data, data_type)
        elif export_format == 'pdf':
            return self._export_to_pdf(data, data_type)
        elif export_format == 'csv':
            return self._export_to_csv(data, data_type)

        return None

    def _get_documents_export_data(self, filters):
        """Dados de documentos para exportação"""
        query = Document.query

        if filters:
            if filters.get('status'):
                query = query.filter_by(status=DocumentStatus(filters['status']))
            if filters.get('category'):
                query = query.filter_by(category=filters['category'])

        documents = query.all()

        return [{
            'id': doc.id,
            'title': doc.title,
            'code': doc.code,
            'version': doc.version,
            'status': doc.status.value,
            'category': doc.category,
            'created_by': doc.creator.full_name,
            'created_at': doc.created_at.strftime('%Y-%m-%d %H:%M'),
            'published_at': doc.published_at.strftime('%Y-%m-%d %H:%M') if doc.published_at else '',
            'norms': ', '.join([norm.name for norm in doc.norms])
        } for doc in documents]

    def _get_audits_export_data(self, filters):
        """Dados de auditorias para exportação"""
        query = Audit.query

        if filters:
            if filters.get('status'):
                query = query.filter_by(status=filters['status'])
            if filters.get('type'):
                query = query.filter_by(audit_type=filters['type'])

        audits = query.all()

        return [{
            'id': audit.id,
            'title': audit.title,
            'type': audit.audit_type.value,
            'status': audit.status,
            'norm': audit.norm.name if audit.norm else '',
            'location': audit.location,
            'planned_date': audit.planned_date.strftime('%Y-%m-%d') if audit.planned_date else '',
            'actual_date': audit.actual_date.strftime('%Y-%m-%d') if audit.actual_date else '',
            'auditor': audit.assigned_auditor.full_name if audit.assigned_auditor else '',
            'responsible': audit.responsible.full_name if audit.responsible else '',
            'progress': audit.progress_percentage,
            'non_conformities': len(audit.non_conformities)
        } for audit in audits]

    def _get_ncs_export_data(self, filters):
        """Dados de NCs para exportação"""
        query = NonConformity.query

        if filters:
            if filters.get('status'):
                query = query.filter_by(status=filters['status'])
            if filters.get('severity'):
                query = query.filter_by(severity=filters['severity'])

        ncs = query.all()

        return [{
            'id': nc.id,
            'title': nc.title,
            'description': nc.description,
            'severity': nc.severity,
            'status': nc.status,
            'requirement': nc.requirement,
            'identified_date': nc.identified_date.strftime('%Y-%m-%d'),
            'target_resolution_date': nc.target_resolution_date.strftime('%Y-%m-%d') if nc.target_resolution_date else '',
            'actual_resolution_date': nc.actual_resolution_date.strftime('%Y-%m-%d') if nc.actual_resolution_date else '',
            'identified_by': nc.identified_by.full_name if nc.identified_by else '',
            'assigned_to': nc.assigned_to.full_name if nc.assigned_to else '',
            'audit': nc.audit.title if nc.audit else ''
        } for nc in ncs]

    def _get_capa_export_data(self, filters):
        """Dados de CAPA para exportação"""
        query = CAPA.query

        if filters:
            if filters.get('status'):
                query = query.filter_by(status=CAPAStatus(filters['status']))
            if filters.get('type'):
                query = query.filter_by(capa_type=filters['type'])

        capas = query.all()

        return [{
            'id': capa.id,
            'reference': capa.reference,
            'title': capa.title,
            'type': capa.capa_type.value,
            'status': capa.status.value,
            'priority': capa.priority,
            'what': capa.what,
            'why': capa.why,
            'who': capa.who,
            'when': capa.when.strftime('%Y-%m-%d'),
            'how': capa.how,
            'how_much': capa.how_much,
            'effectiveness_rating': capa.effectiveness_rating,
            'created_by': capa.created_by.full_name,
            'responsible': capa.responsible.full_name if capa.responsible else '',
            'created_at': capa.created_at.strftime('%Y-%m-%d %H:%M'),
            'closed_at': capa.updated_at.strftime('%Y-%m-%d %H:%M') if capa.status == CAPAStatus.CLOSED else ''
        } for capa in capas]

    def _export_to_excel(self, data, data_type):
        """Exporta dados para Excel"""
        try:
            df = pd.DataFrame(data)
            filename = f'{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            filepath = f'/tmp/{filename}'

            df.to_excel(filepath, index=False)

            with open(filepath, 'rb') as f:
                file_data = f.read()

            return {
                'filename': filename,
                'data': file_data,
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }

        except Exception as e:
            print(f"Erro na exportação para Excel: {e}")
            return None

    def _export_to_pdf(self, data, data_type):
        """Exporta dados para PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors

            filename = f'{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            filepath = f'/tmp/{filename}'

            # Criar PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()

            elements = []

            # Título
            title = Paragraph(f"Relatório {data_type.title()}", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Dados em tabela
            if data:
                df = pd.DataFrame(data)
                table_data = [df.columns.tolist()] + df.values.tolist()

                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                elements.append(table)

            doc.build(elements)

            with open(filepath, 'rb') as f:
                file_data = f.read()

            return {
                'filename': filename,
                'data': file_data,
                'mimetype': 'application/pdf'
            }

        except Exception as e:
            print(f"Erro na exportação para PDF: {e}")
            return None

    def _export_to_csv(self, data, data_type):
        """Exporta dados para CSV"""
        try:
            df = pd.DataFrame(data)
            filename = f'{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            filepath = f'/tmp/{filename}'

            df.to_csv(filepath, index=False)

            with open(filepath, 'rb') as f:
                file_data = f.read()

            return {
                'filename': filename,
                'data': file_data,
                'mimetype': 'text/csv'
            }

        except Exception as e:
            print(f"Erro na exportação para CSV: {e}")
            return None

    def predict_nc_risk(self, user_id=None):
        """Prediz risco de NCs usando dados históricos"""
        try:
            # Coletar dados dos últimos 90 dias
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)

            # NCs por mês
            monthly_ncs = self.db.session.query(
                func.strftime('%Y-%m', NonConformity.identified_date).label('month'),
                func.count(NonConformity.id).label('count')
            ).filter(
                NonConformity.identified_date >= start_date
            ).group_by(
                func.strftime('%Y-%m', NonConformity.identified_date)
            ).all()

            if len(monthly_ncs) < 2:
                return {'risk_level': 'low', 'confidence': 0.5, 'message': 'Dados insuficientes para predição'}

            # Análise de tendência simples
            counts = [count for _, count in monthly_ncs]
            trend = 'increasing' if counts[-1] > counts[0] else 'decreasing' if counts[-1] < counts[0] else 'stable'

            # Calcular média móvel
            if len(counts) >= 3:
                moving_avg = sum(counts[-3:]) / 3
                current = counts[-1]
                risk_score = current / moving_avg if moving_avg > 0 else 1
            else:
                risk_score = 1

            # Determinar nível de risco
            if risk_score > 1.5:
                risk_level = 'high'
                message = 'Tendência de aumento de NCs detectada'
            elif risk_score > 1.2:
                risk_level = 'medium'
                message = 'Aumento moderado de NCs'
            else:
                risk_level = 'low'
                message = 'Tendência estável ou decrescente'

            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'trend': trend,
                'confidence': 0.7,
                'message': message,
                'data_points': len(counts),
                'period': '90_days'
            }

        except Exception as e:
            print(f"Erro na predição de NCs: {e}")
            return {'risk_level': 'unknown', 'error': str(e)}

# Instância global
analytics_service = AnalyticsService()