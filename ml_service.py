"""
Serviço de Machine Learning para Predições
Implementa modelos simples para predição de NCs e análise de padrões
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
from flask import current_app
from models import (
    db, Document, Audit, NonConformity, CAPA, User, Team,
    Process, Norm, AuditLog, DocumentStatus, CAPAStatus
)
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import base64

class MLService:
    """Serviço de Machine Learning para predições"""

    def __init__(self):
        self.models = {}
        self.model_performance = {}

    def predict_nc_risk(self, user_id=None, process_id=None, norm_id=None):
        """
        Prediz risco de ocorrência de NCs baseado em dados históricos

        Args:
            user_id: ID do usuário para análise personalizada
            process_id: ID do processo para análise específica
            norm_id: ID da norma para análise específica

        Returns:
            Dicionário com predição de risco
        """
        try:
            # Coletar dados históricos (últimos 180 dias)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=180)

            # Query para NCs no período
            query = NonConformity.query.filter(
                NonConformity.identified_date >= start_date.date(),
                NonConformity.identified_date <= end_date.date()
            )

            if user_id:
                query = query.filter(NonConformity.assigned_to_id == user_id)
            if process_id:
                # Filtrar por processo (se houver relacionamento)
                pass
            if norm_id:
                query = query.join(Audit).filter(Audit.norm_id == norm_id)

            ncs = query.all()

            if len(ncs) < 10:
                return {
                    'risk_level': 'insufficient_data',
                    'confidence': 0.0,
                    'message': 'Dados insuficientes para predição (mínimo 10 NCs)',
                    'data_points': len(ncs)
                }

            # Análise estatística simples
            risk_analysis = self._analyze_nc_patterns(ncs)

            # Predição baseada em padrões
            prediction = self._calculate_risk_prediction(risk_analysis)

            return {
                'risk_level': prediction['level'],
                'confidence': prediction['confidence'],
                'risk_score': prediction['score'],
                'factors': prediction['factors'],
                'recommendations': prediction['recommendations'],
                'data_points': len(ncs),
                'analysis_period_days': 180,
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            current_app.logger.error(f"Erro na predição de risco de NCs: {str(e)}")
            return {
                'risk_level': 'error',
                'confidence': 0.0,
                'error': str(e)
            }

    def _analyze_nc_patterns(self, ncs):
        """Analisa padrões nas NCs"""
        # Análise por severidade
        severity_count = Counter(nc.severity for nc in ncs)

        # Análise temporal
        daily_ncs = defaultdict(int)
        for nc in ncs:
            day_key = nc.identified_date.strftime('%Y-%m-%d')
            daily_ncs[day_key] += 1

        # Análise por requisito
        requirement_count = Counter(nc.requirement for nc in ncs if nc.requirement)

        # Análise por auditor
        auditor_count = Counter()
        for nc in ncs:
            if nc.identified_by:
                auditor_count[nc.identified_by.full_name] += 1

        return {
            'total_ncs': len(ncs),
            'severity_distribution': dict(severity_count),
            'daily_frequency': dict(daily_ncs),
            'top_requirements': dict(requirement_count.most_common(5)),
            'top_auditors': dict(auditor_count.most_common(5)),
            'avg_resolution_time': self._calculate_avg_resolution_time(ncs)
        }

    def _calculate_avg_resolution_time(self, ncs):
        """Calcula tempo médio de resolução"""
        resolution_times = []

        for nc in ncs:
            if nc.actual_resolution_date and nc.identified_date:
                days = (nc.actual_resolution_date - nc.identified_date).days
                if days >= 0:  # Apenas resoluções válidas
                    resolution_times.append(days)

        if resolution_times:
            return {
                'average': sum(resolution_times) / len(resolution_times),
                'median': sorted(resolution_times)[len(resolution_times) // 2],
                'min': min(resolution_times),
                'max': max(resolution_times)
            }

        return None

    def _calculate_risk_prediction(self, analysis):
        """Calcula predição de risco baseada na análise"""
        total_ncs = analysis['total_ncs']

        # Fator 1: Volume de NCs (últimos 180 dias)
        if total_ncs > 50:
            volume_score = 0.8  # Alto risco
        elif total_ncs > 20:
            volume_score = 0.5  # Médio risco
        else:
            volume_score = 0.2  # Baixo risco

        # Fator 2: Severidade crítica/major
        critical_major = (analysis['severity_distribution'].get('critical', 0) +
                         analysis['severity_distribution'].get('major', 0))
        severity_ratio = critical_major / total_ncs if total_ncs > 0 else 0

        if severity_ratio > 0.3:
            severity_score = 0.8
        elif severity_ratio > 0.1:
            severity_score = 0.5
        else:
            severity_score = 0.2

        # Fator 3: Tempo de resolução
        resolution_time = analysis['avg_resolution_time']
        if resolution_time and resolution_time['average'] > 30:
            time_score = 0.7  # Resolução lenta indica problemas
        elif resolution_time and resolution_time['average'] > 15:
            time_score = 0.4
        else:
            time_score = 0.2

        # Calcular score final
        risk_score = (volume_score + severity_score + time_score) / 3

        # Determinar nível de risco
        if risk_score > 0.6:
            risk_level = 'high'
            confidence = 0.8
        elif risk_score > 0.4:
            risk_level = 'medium'
            confidence = 0.7
        else:
            risk_level = 'low'
            confidence = 0.6

        # Gerar recomendações
        recommendations = []
        if volume_score > 0.5:
            recommendations.append('Aumentar frequência de auditorias internas')
        if severity_score > 0.5:
            recommendations.append('Focar em treinamento para requisitos críticos')
        if time_score > 0.5:
            recommendations.append('Revisar processo de resolução de NCs')

        return {
            'score': risk_score,
            'level': risk_level,
            'confidence': confidence,
            'factors': {
                'volume': volume_score,
                'severity': severity_score,
                'resolution_time': time_score
            },
            'recommendations': recommendations
        }

    def predict_document_approval_time(self, document_data):
        """
        Prediz tempo de aprovação de documentos baseado em dados históricos

        Args:
            document_data: Dados do documento (categoria, tamanho, etc.)

        Returns:
            Predição de tempo de aprovação
        """
        try:
            # Coletar dados históricos de documentos
            documents = Document.query.filter(
                Document.status.in_([DocumentStatus.PUBLISHED, DocumentStatus.ARCHIVED])
            ).all()

            if len(documents) < 5:
                return {
                    'predicted_days': 7,
                    'confidence': 0.3,
                    'message': 'Dados insuficientes para predição precisa'
                }

            # Análise simples baseada em categoria
            category_times = defaultdict(list)

            for doc in documents:
                if doc.published_at and doc.created_at:
                    days = (doc.published_at - doc.created_at).days
                    if days > 0:
                        category_times[doc.category or 'uncategorized'].append(days)

            # Calcular médias por categoria
            avg_times = {}
            for category, times in category_times.items():
                avg_times[category] = sum(times) / len(times)

            # Predição baseada na categoria
            doc_category = document_data.get('category', 'uncategorized')
            predicted_days = avg_times.get(doc_category, 7)  # 7 dias como padrão

            # Calcular confiança baseada na quantidade de dados
            data_points = len(category_times.get(doc_category, []))
            confidence = min(data_points / 10.0, 1.0)  # Máximo 1.0

            return {
                'predicted_days': round(predicted_days, 1),
                'confidence': round(confidence, 2),
                'category': doc_category,
                'data_points': data_points,
                'category_average': round(avg_times.get(doc_category, predicted_days), 1)
            }

        except Exception as e:
            current_app.logger.error(f"Erro na predição de tempo de aprovação: {str(e)}")
            return {
                'predicted_days': 7,
                'confidence': 0.0,
                'error': str(e)
            }

    def analyze_audit_effectiveness(self):
        """
        Analisa efetividade das auditorias baseado em métricas

        Returns:
            Análise de efetividade das auditorias
        """
        try:
            # Coletar dados de auditorias e NCs
            audits = Audit.query.filter_by(status='completed').all()

            if len(audits) < 3:
                return {
                    'effectiveness_score': 0,
                    'message': 'Dados insuficientes para análise'
                }

            audit_effectiveness = []

            for audit in audits:
                # Calcular métricas da auditoria
                nc_count = len(audit.non_conformities)
                total_items_audited = 50  # Estimativa (em produção, calcular baseado no escopo)

                # Efetividade baseada na proporção de NCs encontradas
                if total_items_audited > 0:
                    nc_ratio = nc_count / total_items_audited
                    # Converter para score (menos NCs = mais efetiva)
                    effectiveness = max(0, 1 - nc_ratio)
                else:
                    effectiveness = 0.5  # Neutro se não houver dados

                audit_effectiveness.append({
                    'audit_id': audit.id,
                    'audit_title': audit.title,
                    'nc_count': nc_count,
                    'effectiveness_score': effectiveness,
                    'audit_date': audit.actual_date.isoformat() if audit.actual_date else None
                })

            # Calcular score médio
            avg_effectiveness = sum(a['effectiveness_score'] for a in audit_effectiveness) / len(audit_effectiveness)

            return {
                'overall_effectiveness': round(avg_effectiveness, 3),
                'total_audits_analyzed': len(audit_effectiveness),
                'audit_details': audit_effectiveness,
                'recommendations': self._generate_audit_recommendations(avg_effectiveness),
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            current_app.logger.error(f"Erro na análise de efetividade de auditorias: {str(e)}")
            return {
                'effectiveness_score': 0,
                'error': str(e)
            }

    def _generate_audit_recommendations(self, effectiveness_score):
        """Gera recomendações baseadas no score de efetividade"""
        recommendations = []

        if effectiveness_score < 0.3:
            recommendations.append('Revisar critérios de auditoria - muitas NCs indicam problemas')
            recommendations.append('Aumentar treinamento dos auditores')
            recommendations.append('Revisar checklist de auditoria')
        elif effectiveness_score < 0.6:
            recommendations.append('Focar auditorias em áreas de maior risco')
            recommendations.append('Melhorar preparação para auditorias')
        else:
            recommendations.append('Manter práticas atuais de auditoria')
            recommendations.append('Compartilhar boas práticas entre auditores')

        return recommendations

    def train_simple_model(self, model_type='nc_prediction'):
        """
        Treina modelo simples para predições

        Args:
            model_type: Tipo de modelo ('nc_prediction', 'document_classification')

        Returns:
            Resultado do treinamento
        """
        try:
            if model_type == 'nc_prediction':
                return self._train_nc_prediction_model()
            elif model_type == 'document_classification':
                return self._train_document_classification_model()
            else:
                return {'error': 'Tipo de modelo não suportado'}

        except Exception as e:
            current_app.logger.error(f"Erro no treinamento do modelo: {str(e)}")
            return {'error': str(e)}

    def _train_nc_prediction_model(self):
        """Treina modelo para predição de NCs"""
        # Coletar dados históricos
        ncs = NonConformity.query.filter(
            NonConformity.identified_date >= datetime.utcnow() - timedelta(days=365)
        ).all()

        if len(ncs) < 20:
            return {
                'status': 'insufficient_data',
                'message': 'Dados insuficientes para treinamento (mínimo 20 NCs)'
            }

        # Preparar dados para treinamento
        features = []
        labels = []

        for nc in ncs:
            # Features simples
            feature = [
                len(nc.description) if nc.description else 0,
                1 if nc.severity == 'critical' else 0,
                1 if nc.severity == 'major' else 0,
                1 if nc.severity == 'minor' else 0,
            ]

            # Label: 1 se foi resolvida dentro do prazo, 0 caso contrário
            if nc.target_resolution_date and nc.actual_resolution_date:
                label = 1 if nc.actual_resolution_date <= nc.target_resolution_date else 0
            else:
                label = 0  # Não consegue determinar

            features.append(feature)
            labels.append(label)

        if len(set(labels)) < 2:
            return {
                'status': 'insufficient_variability',
                'message': 'Pouca variabilidade nos dados para treinamento'
            }

        # Treinar modelo simples
        X = np.array(features)
        y = np.array(labels)

        # Divisão simples (em produção usar cross-validation)
        split_point = int(len(X) * 0.8)
        X_train, X_test = X[:split_point], X[split_point:]
        y_train, y_test = y[:split_point], y[split_point:]

        # Modelo simples (Random Forest)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        # Avaliar modelo
        train_accuracy = accuracy_score(y_train, model.predict(X_train))
        test_accuracy = accuracy_score(y_test, model.predict(X_test))

        # Salvar modelo (em produção, usar formato apropriado)
        model_data = {
            'model': base64.b64encode(pickle.dumps(model)).decode('utf-8'),
            'features': ['description_length', 'is_critical', 'is_major', 'is_minor'],
            'model_type': 'nc_prediction',
            'algorithm': 'RandomForest',
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'training_date': datetime.utcnow().isoformat(),
            'data_points': len(ncs)
        }

        return {
            'status': 'success',
            'model_type': 'nc_prediction',
            'train_accuracy': round(train_accuracy, 3),
            'test_accuracy': round(test_accuracy, 3),
            'data_points': len(ncs),
            'features': model_data['features'],
            'training_date': model_data['training_date']
        }

    def _train_document_classification_model(self):
        """Treina modelo para classificação de documentos"""
        # Implementação futura
        return {
            'status': 'not_implemented',
            'message': 'Modelo de classificação de documentos será implementado na próxima versão'
        }

    def get_ml_insights(self):
        """Obtém insights gerais do sistema usando análise de dados"""
        try:
            insights = {}

            # Insight 1: Tendência de NCs
            nc_trend = self._analyze_nc_trends()
            insights['nc_trends'] = nc_trend

            # Insight 2: Performance de usuários
            user_performance = self._analyze_user_performance()
            insights['user_performance'] = user_performance

            # Insight 3: Efetividade de processos
            process_effectiveness = self._analyze_process_effectiveness()
            insights['process_effectiveness'] = process_effectiveness

            return {
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat(),
                'analysis_period_days': 90
            }

        except Exception as e:
            current_app.logger.error(f"Erro ao gerar insights ML: {str(e)}")
            return {'error': str(e)}

    def _analyze_nc_trends(self):
        """Analisa tendências de NCs"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        recent_ncs = NonConformity.query.filter(
            NonConformity.identified_date >= thirty_days_ago.date()
        ).count()

        older_ncs = NonConformity.query.filter(
            NonConformity.identified_date.between(ninety_days_ago.date(), thirty_days_ago.date())
        ).count()

        if older_ncs > 0:
            trend = (recent_ncs - older_ncs) / older_ncs
        else:
            trend = 0

        return {
            'recent_count': recent_ncs,
            'previous_count': older_ncs,
            'trend_percentage': round(trend * 100, 2),
            'trend_direction': 'increasing' if trend > 0.1 else 'decreasing' if trend < -0.1 else 'stable'
        }

    def _analyze_user_performance(self):
        """Analisa performance dos usuários"""
        # Usuários ativos nos últimos 30 dias
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        users = User.query.filter(
            User.last_login >= thirty_days_ago
        ).all()

        performance_data = []

        for user in users:
            # NCs criadas pelo usuário
            ncs_created = NonConformity.query.filter_by(identified_by_id=user.id).count()

            # CAPAs atribuídas ao usuário
            capas_assigned = CAPA.query.filter_by(responsible_id=user.id).count()

            # CAPAs concluídas pelo usuário
            capas_completed = CAPA.query.filter(
                CAPA.responsible_id == user.id,
                CAPA.status == CAPAStatus.CLOSED
            ).count()

            performance_data.append({
                'user_id': user.id,
                'user_name': user.full_name,
                'ncs_created': ncs_created,
                'capas_assigned': capas_assigned,
                'capas_completed': capas_completed,
                'completion_rate': (capas_completed / capas_assigned * 100) if capas_assigned > 0 else 0
            })

        return {
            'total_active_users': len(performance_data),
            'users_data': performance_data[:10],  # Top 10
            'avg_completion_rate': sum(u['completion_rate'] for u in performance_data) / len(performance_data) if performance_data else 0
        }

    def _analyze_process_effectiveness(self):
        """Analisa efetividade dos processos"""
        # Análise baseada em auditorias e NCs por processo
        processes = Process.query.all()

        process_analysis = []

        for process in processes:
            # NCs relacionadas ao processo (estimativa)
            # Em produção, isso seria baseado em relacionamento direto
            process_ncs = NonConformity.query.count()  # Placeholder

            process_analysis.append({
                'process_id': process.id,
                'process_name': process.name,
                'related_ncs': process_ncs,
                'risk_score': min(process_ncs / 10, 1.0)  # Score simples
            })

        return {
            'total_processes': len(process_analysis),
            'processes_data': process_analysis,
            'high_risk_processes': [p for p in process_analysis if p['risk_score'] > 0.7]
        }

# Instância global
ml_service = MLService()