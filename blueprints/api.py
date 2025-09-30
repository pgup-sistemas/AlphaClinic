"""
Blueprint para APIs RESTful
Fornece endpoints JSON para integração com sistemas externos
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from models import (
    Document, Audit, NonConformity, CAPA, User, Team,
    DocumentStatus, AuditType, CAPAStatus, db
)
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import json
from cache_service import cache_service
from audit_service import AuditService

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# === MIDDLEWARE PARA AUDITORIA ===
@api_bp.before_request
@login_required
def api_audit_middleware():
    """Auditoria automática de todas as requisições API"""
    AuditService.log_operation(
        entity_type='api_request',
        entity_id=0,
        operation=f"{request.method}:{request.endpoint}",
        operation_details={
            'method': request.method,
            'endpoint': request.endpoint,
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'query_params': dict(request.args),
            'content_length': len(request.get_data())
        },
        compliance_level='standard'
    )

# === HEALTH CHECK ===
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoramento"""
    health = cache_service.get_system_health()

    return jsonify({
        'status': 'healthy' if health['database_connected'] else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': health
    })

# === DASHBOARD METRICS ===
@api_bp.route('/dashboard-metrics', methods=['GET'])
@login_required
def get_dashboard_metrics():
    """Métricas do dashboard em formato JSON"""
    try:
        # Usar cache para melhorar performance
        metrics = cache_service.get_dashboard_metrics(current_user.id)

        return jsonify({
            'success': True,
            'data': metrics,
            'cached': True,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter métricas do dashboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# === DOCUMENTOS ===
@api_bp.route('/documents', methods=['GET'])
@login_required
def get_documents():
    """Lista documentos com filtros"""
    try:
        # Filtros
        status = request.args.get('status')
        category = request.args.get('category')
        limit = min(int(request.args.get('limit', 50)), 100)  # Máximo 100
        offset = int(request.args.get('offset', 0))

        # Query base
        query = Document.query

        if status:
            query = query.filter_by(status=DocumentStatus(status))
        if category:
            query = query.filter_by(category=category)

        # Ordenação
        query = query.order_by(Document.created_at.desc())

        # Paginação
        total = query.count()
        documents = query.offset(offset).limit(limit).all()

        # Serializar
        documents_data = []
        for doc in documents:
            documents_data.append({
                'id': doc.id,
                'title': doc.title,
                'code': doc.code,
                'version': doc.version,
                'status': doc.status.value,
                'category': doc.category,
                'created_by': doc.creator.full_name,
                'created_at': doc.created_at.isoformat(),
                'published_at': doc.published_at.isoformat() if doc.published_at else None,
                'effective_date': doc.effective_date.isoformat() if doc.effective_date else None,
                'signature_required': doc.signature_required,
                'norms': [norm.name for norm in doc.norms]
            })

        return jsonify({
            'success': True,
            'data': documents_data,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            },
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar documentos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/documents/<int:document_id>', methods=['GET'])
@login_required
def get_document(document_id):
    """Obtém documento específico"""
    try:
        document = Document.query.get_or_404(document_id)

        # Verificar permissões (simplificado)
        if document.status == DocumentStatus.DRAFT and document.created_by_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403

        document_data = {
            'id': document.id,
            'title': document.title,
            'code': document.code,
            'content': document.content,
            'version': document.version,
            'status': document.status.value,
            'category': document.category,
            'created_by': document.creator.full_name,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat() if document.updated_at else None,
            'published_at': document.published_at.isoformat() if document.published_at else None,
            'effective_date': document.effective_date.isoformat() if document.effective_date else None,
            'review_deadline': document.review_deadline.isoformat() if document.review_deadline else None,
            'signature_required': document.signature_required,
            'norms': [norm.name for norm in document.norms],
            'attachments': [
                {
                    'id': att.id,
                    'filename': att.filename,
                    'original_filename': att.original_filename,
                    'file_size': att.file_size,
                    'uploaded_at': att.uploaded_at.isoformat()
                } for att in document.attachments
            ]
        }

        return jsonify({
            'success': True,
            'data': document_data,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter documento {document_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Documento não encontrado'
        }), 404

# === AUDITORIAS ===
@api_bp.route('/audits', methods=['GET'])
@login_required
def get_audits():
    """Lista auditorias com filtros"""
    try:
        # Filtros
        status = request.args.get('status')
        audit_type = request.args.get('type')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        query = Audit.query

        if status:
            query = query.filter_by(status=status)
        if audit_type:
            query = query.filter_by(audit_type=AuditType(audit_type))

        query = query.order_by(Audit.created_at.desc())

        total = query.count()
        audits = query.offset(offset).limit(limit).all()

        audits_data = []
        for audit in audits:
            audits_data.append({
                'id': audit.id,
                'title': audit.title,
                'type': audit.audit_type.value,
                'status': audit.status,
                'norm': audit.norm.name if audit.norm else None,
                'location': audit.location,
                'planned_date': audit.planned_date.isoformat() if audit.planned_date else None,
                'actual_date': audit.actual_date.isoformat() if audit.actual_date else None,
                'assigned_auditor': audit.assigned_auditor.full_name if audit.assigned_auditor else None,
                'responsible': audit.responsible.full_name if audit.responsible else None,
                'progress_percentage': audit.progress_percentage,
                'non_conformities_count': len(audit.non_conformities),
                'created_at': audit.created_at.isoformat()
            })

        return jsonify({
            'success': True,
            'data': audits_data,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            }
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar auditorias: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# === MACHINE LEARNING E PREDIÇÕES ===
@api_bp.route('/ml/predict/nc-risk', methods=['GET'])
@login_required
def predict_nc_risk():
    """Predição de risco de NCs"""
    try:
        from ml_service import ml_service

        # Parâmetros opcionais
        user_id = request.args.get('user_id', type=int)
        process_id = request.args.get('process_id', type=int)
        norm_id = request.args.get('norm_id', type=int)

        prediction = ml_service.predict_nc_risk(user_id, process_id, norm_id)

        return jsonify({
            'success': True,
            'data': prediction
        })

    except Exception as e:
        current_app.logger.error(f"Erro na predição de risco de NCs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# === RELATÓRIOS AVANÇADOS ===
@api_bp.route('/reports/generate/<report_type>', methods=['POST'])
@login_required
def generate_advanced_report(report_type):
    """Gera relatório avançado em formato especificado"""
    try:
        from advanced_reporting import reporting_service

        # Obter parâmetros
        format_type = request.args.get('format', 'json')
        filters = request.get_json() or {}

        # Gerar relatório
        report_result = reporting_service.generate_report(
            report_type=report_type,
            format=format_type,
            filters=filters,
            user_id=current_user.id
        )

        if 'error' in report_result:
            return jsonify({
                'success': False,
                'error': report_result['error']
            }), 400

        return jsonify({
            'success': True,
            'data': report_result,
            'report_type': report_type,
            'format': format_type
        })

    except Exception as e:
        current_app.logger.error(f"Erro na geração de relatório avançado: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/reports/types', methods=['GET'])
@login_required
def get_report_types():
    """Lista tipos de relatórios disponíveis"""
    try:
        from advanced_reporting import reporting_service

        report_types = [
            {
                'type': 'compliance_overview',
                'name': 'Visão Geral de Compliance',
                'description': 'Relatório completo de compliance com todas as métricas',
                'formats': ['pdf', 'excel', 'html', 'json']
            },
            {
                'type': 'audit_effectiveness',
                'name': 'Efetividade de Auditorias',
                'description': 'Análise detalhada da efetividade das auditorias',
                'formats': ['pdf', 'excel', 'html', 'json']
            },
            {
                'type': 'nc_analysis',
                'name': 'Análise de Não Conformidades',
                'description': 'Análise profunda de NCs e padrões',
                'formats': ['pdf', 'excel', 'html', 'json']
            },
            {
                'type': 'capa_status',
                'name': 'Status de CAPAs',
                'description': 'Relatório de status e progresso dos CAPAs',
                'formats': ['pdf', 'excel', 'html', 'json']
            },
            {
                'type': 'system_usage',
                'name': 'Uso do Sistema',
                'description': 'Métricas de uso e performance do sistema',
                'formats': ['pdf', 'excel', 'html', 'json']
            }
        ]

        return jsonify({
            'success': True,
            'data': report_types
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar tipos de relatório: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# === LGPD COMPLIANCE ===
@api_bp.route('/lgpd/consent', methods=['POST'])
@login_required
def create_lgpd_consent():
    """Cria consentimento LGPD"""
    try:
        from lgpd_service import lgpd_service, DataProcessingPurpose

        data = request.get_json()
        if not data or 'purpose' not in data:
            return jsonify({
                'success': False,
                'error': 'Dados de consentimento são obrigatórios'
            }), 400

        purpose = DataProcessingPurpose(data['purpose'])
        consent_data = data.get('consent_data')

        consent = lgpd_service.create_data_processing_consent(
            current_user.id, purpose, consent_data
        )

        return jsonify({
            'success': True,
            'data': {
                'consent_id': consent.id,
                'purpose': consent.purpose,
                'granted_at': consent.created_at.isoformat(),
                'is_active': consent.is_active
            }
        })

    except Exception as e:
        current_app.logger.error(f"Erro na criação de consentimento LGPD: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/lgpd/consent/<purpose>', methods=['DELETE'])
@login_required
def withdraw_lgpd_consent(purpose):
    """Retira consentimento LGPD"""
    try:
        from lgpd_service import lgpd_service, DataProcessingPurpose

        purpose_enum = DataProcessingPurpose(purpose)

        lgpd_service.withdraw_consent(current_user.id, purpose_enum)

        return jsonify({
            'success': True,
            'message': 'Consentimento retirado com sucesso'
        })

    except Exception as e:
        current_app.logger.error(f"Erro na retirada de consentimento LGPD: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/lgpd/data-portfolio', methods=['GET'])
@login_required
def get_lgpd_data_portfolio():
    """Obtém portfólio de dados LGPD do usuário"""
    try:
        from lgpd_service import lgpd_service

        portfolio = lgpd_service.get_user_data_portfolio(current_user.id)

        return jsonify({
            'success': True,
            'data': portfolio
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter portfólio LGPD: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/lgpd/request', methods=['POST'])
@login_required
def create_lgpd_request():
    """Cria solicitação de direitos LGPD"""
    try:
        from lgpd_service import lgpd_service, DataSubjectRights

        data = request.get_json()
        if not data or 'request_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Tipo de solicitação é obrigatório'
            }), 400

        request_type = DataSubjectRights(data['request_type'])
        description = data.get('description')
        contact_email = data.get('contact_email')

        request_record = lgpd_service.create_data_subject_request(
            current_user.id, request_type, description, contact_email
        )

        return jsonify({
            'success': True,
            'data': {
                'request_id': request_record.id,
                'request_type': request_record.request_type,
                'status': request_record.status,
                'created_at': request_record.created_at.isoformat()
            }
        })

    except Exception as e:
        current_app.logger.error(f"Erro na criação de solicitação LGPD: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/lgpd/compliance-report', methods=['GET'])
@login_required
def get_lgpd_compliance_report():
    """Gera relatório de compliance LGPD"""
    try:
        from lgpd_service import lgpd_service

        report = lgpd_service.generate_lgpd_compliance_report()

        return jsonify({
            'success': True,
            'data': report
        })

    except Exception as e:
        current_app.logger.error(f"Erro na geração de relatório LGPD: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# === BLOCKCHAIN AUDITORIA ===
@api_bp.route('/blockchain/chain-info', methods=['GET'])
@login_required
def get_blockchain_info():
    """Obtém informações da cadeia de auditoria"""
    try:
        from blockchain_service import blockchain_service

        chain_info = blockchain_service.get_chain_info()

        return jsonify({
            'success': True,
            'data': chain_info
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter informações da cadeia: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/blockchain/verify/<int:log_id>', methods=['GET'])
@login_required
def verify_log_in_chain(log_id):
    """Verifica se log está na cadeia e é válido"""
    try:
        from blockchain_service import blockchain_service

        verification = blockchain_service.verify_log_in_chain(log_id)

        return jsonify({
            'success': True,
            'data': verification
        })

    except Exception as e:
        current_app.logger.error(f"Erro na verificação do log na cadeia: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/blockchain/audit-trail', methods=['GET'])
@login_required
def get_blockchain_audit_trail():
    """Obtém trilha de auditoria com informações de blockchain"""
    try:
        from blockchain_service import blockchain_service

        # Filtros opcionais
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        trail_data = blockchain_service.get_audit_trail_with_blockchain(start_date, end_date)

        return jsonify({
            'success': True,
            'data': trail_data
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter trilha com blockchain: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/blockchain/export', methods=['GET'])
@login_required
def export_blockchain():
    """Exporta cadeia de auditoria"""
    try:
        from blockchain_service import blockchain_service

        format_type = request.args.get('format', 'json')
        export_data = blockchain_service.export_chain(format_type)

        return jsonify({
            'success': True,
            'data': export_data,
            'format': format_type,
            'content_type': 'application/json'
        })

    except Exception as e:
        current_app.logger.error(f"Erro na exportação da cadeia: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/reports/schedule', methods=['POST'])
@login_required
def schedule_report():
    """Agenda geração automática de relatórios"""
    try:
        # Em produção: implementar sistema de agendamento
        # Por enquanto: apenas validar parâmetros

        schedule_data = request.get_json()
        if not schedule_data:
            return jsonify({
                'success': False,
                'error': 'Dados de agendamento são obrigatórios'
            }), 400

        # Validar campos obrigatórios
        required_fields = ['report_type', 'format', 'frequency']
        for field in required_fields:
            if field not in schedule_data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {field}'
                }), 400

        # Em produção: salvar no banco e configurar job
        schedule_response = {
            'schedule_id': f"schedule_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'report_type': schedule_data['report_type'],
            'format': schedule_data['format'],
            'frequency': schedule_data['frequency'],
            'next_run': (datetime.utcnow() + timedelta(days=1)).isoformat(),
            'status': 'scheduled'
        }

        return jsonify({
            'success': True,
            'data': schedule_response,
            'message': 'Relatório agendado com sucesso (funcionalidade em desenvolvimento)'
        })

    except Exception as e:
        current_app.logger.error(f"Erro no agendamento de relatório: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/ml/predict/document-approval-time', methods=['POST'])
@login_required
def predict_document_approval_time():
    """Predição de tempo de aprovação de documentos"""
    try:
        from ml_service import ml_service

        document_data = request.get_json()
        if not document_data:
            return jsonify({
                'success': False,
                'error': 'Dados do documento são obrigatórios'
            }), 400

        prediction = ml_service.predict_document_approval_time(document_data)

        return jsonify({
            'success': True,
            'data': prediction
        })

    except Exception as e:
        current_app.logger.error(f"Erro na predição de tempo de aprovação: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/ml/insights', methods=['GET'])
@login_required
def get_ml_insights():
    """Insights gerais usando análise de dados"""
    try:
        from ml_service import ml_service

        insights = ml_service.get_ml_insights()

        return jsonify({
            'success': True,
            'data': insights
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter insights ML: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@api_bp.route('/ml/train/<model_type>', methods=['POST'])
@login_required
def train_ml_model(model_type):
    """Treina modelo de ML"""
    try:
        from ml_service import ml_service

        # Apenas admin pode treinar modelos
        if current_user.role.value != 'admin':
            return jsonify({
                'success': False,
                'error': 'Apenas administradores podem treinar modelos'
            }), 403

        result = ml_service.train_simple_model(model_type)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        current_app.logger.error(f"Erro no treinamento do modelo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# === NÃO CONFORMIDADES ===
@api_bp.route('/non-conformities', methods=['GET'])
@login_required
def get_non_conformities():
    """Lista não conformidades com filtros"""
    try:
        # Filtros
        status = request.args.get('status')
        severity = request.args.get('severity')
        assigned_to = request.args.get('assigned_to')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        query = NonConformity.query

        if status:
            query = query.filter_by(status=status)
        if severity:
            query = query.filter_by(severity=severity)
        if assigned_to:
            query = query.filter_by(assigned_to_id=assigned_to)

        query = query.order_by(NonConformity.identified_date.desc())

        total = query.count()
        ncs = query.offset(offset).limit(limit).all()

        ncs_data = []
        for nc in ncs:
            ncs_data.append({
                'id': nc.id,
                'title': nc.title,
                'description': nc.description,
                'severity': nc.severity,
                'status': nc.status,
                'requirement': nc.requirement,
                'identified_date': nc.identified_date.isoformat(),
                'target_resolution_date': nc.target_resolution_date.isoformat() if nc.target_resolution_date else None,
                'actual_resolution_date': nc.actual_resolution_date.isoformat() if nc.actual_resolution_date else None,
                'identified_by': nc.identified_by.full_name if nc.identified_by else None,
                'assigned_to': nc.assigned_to.full_name if nc.assigned_to else None,
                'audit_title': nc.audit.title if nc.audit else None,
                'has_capa': nc.capa_plans is not None and len(nc.capa_plans) > 0
            })

        return jsonify({
            'success': True,
            'data': ncs_data,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            }
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar NCs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# === CAPA ===
@api_bp.route('/capa', methods=['GET'])
@login_required
def get_capa():
    """Lista planos CAPA com filtros"""
    try:
        # Filtros
        status = request.args.get('status')
        capa_type = request.args.get('type')
        priority = request.args.get('priority')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        query = CAPA.query

        if status:
            query = query.filter_by(status=CAPAStatus(status))
        if capa_type:
            query = query.filter_by(capa_type=capa_type)
        if priority:
            query = query.filter_by(priority=priority)

        query = query.order_by(CAPA.created_at.desc())

        total = query.count()
        capas = query.offset(offset).limit(limit).all()

        capas_data = []
        for capa in capas:
            capas_data.append({
                'id': capa.id,
                'reference_number': capa.reference_number,
                'type': capa.capa_type.value,
                'status': capa.status.value,
                'priority': capa.priority,
                'what': capa.what,
                'why': capa.why,
                'who': capa.who,
                'when': capa.when.isoformat(),
                'how': capa.how,
                'how_much': capa.how_much,
                'target_completion_date': capa.target_completion_date.isoformat() if capa.target_completion_date else None,
                'actual_completion_date': capa.actual_completion_date.isoformat() if capa.actual_completion_date else None,
                'effectiveness_rating': capa.effectiveness_rating,
                'created_by': capa.created_by.full_name,
                'responsible': capa.responsible.full_name if capa.responsible else None,
                'non_conformity_title': capa.non_conformity.title if capa.non_conformity else None
            })

        return jsonify({
            'success': True,
            'data': capas_data,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            }
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao listar CAPAs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# === ESTATÍSTICAS ===
@api_bp.route('/stats/summary', methods=['GET'])
@login_required
def get_stats_summary():
    """Estatísticas resumidas para widgets"""
    try:
        # Usar cache para melhorar performance
        doc_stats = cache_service.get_document_stats()
        audit_stats = cache_service.get_audit_stats()

        # Calcular estatísticas adicionais
        from models import NonConformity, CAPA, User

        nc_stats = db.session.query(
            NonConformity.status,
            func.count(NonConformity.id)
        ).group_by(NonConformity.status).all()

        capa_stats = db.session.query(
            CAPA.status,
            func.count(CAPA.id)
        ).group_by(CAPA.status).all()

        stats = {
            'documents': {status: count for status, count in doc_stats.items() if status != 'total' and status != 'cached_at'},
            'audits': {status: count for status, count in audit_stats.items() if status != 'total' and status != 'cached_at'},
            'non_conformities': {status: count for status, count in nc_stats},
            'capa': {status.value: count for status, count in capa_stats},
            'system': {
                'total_users': User.query.count(),
                'active_users': User.query.filter_by(is_active=True).count(),
                'total_teams': Team.query.count()
            },
            'generated_at': datetime.utcnow().isoformat()
        }

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# === ERROS ===
@api_bp.errorhandler(404)
def not_found(error):
    """Tratamento de erro 404"""
    return jsonify({
        'success': False,
        'error': 'Recurso não encontrado',
        'timestamp': datetime.utcnow().isoformat()
    }), 404

@api_bp.errorhandler(500)
def internal_error(error):
    """Tratamento de erro 500"""
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

@api_bp.errorhandler(403)
def forbidden(error):
    """Tratamento de erro 403"""
    return jsonify({
        'success': False,
        'error': 'Acesso negado',
        'timestamp': datetime.utcnow().isoformat()
    }), 403