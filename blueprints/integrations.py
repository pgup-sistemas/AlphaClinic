"""
APIs de Integração Empresarial
Fornece endpoints REST para integração com ERPs, sistemas de RH, etc.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Document, User, Audit, NonConformity, CAPA, Norm, db
from audit_service import AuditService
from encryption_service import EncryptionService
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound
import json
from datetime import datetime, timedelta

integrations_bp = Blueprint('integrations', __name__, url_prefix='/api/v1/integrations')

# Middleware para autenticação de API
def require_api_key(f):
    """Decorator para verificar chave de API para integrações externas"""
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            raise Unauthorized("API Key required")

        # Validar chave contra configuração
        valid_keys = current_app.config.get('API_KEYS', [])
        if api_key not in valid_keys:
            raise Unauthorized("Invalid API Key")

        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_integration_permission(permission):
    """Verifica permissões específicas de integração"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # Implementar verificação de permissões baseada no usuário da API
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# ==================== DOCUMENTOS ====================

@integrations_bp.route('/documents', methods=['GET'])
@require_api_key
def get_documents():
    """Lista documentos para integração externa"""
    try:
        # Filtros
        status = request.args.get('status')
        code = request.args.get('code')
        limit = min(int(request.args.get('limit', 50)), 100)  # Máximo 100
        offset = int(request.args.get('offset', 0))

        query = Document.query

        if status:
            query = query.filter_by(status=status)
        if code:
            query = query.filter(Document.code.contains(code))

        documents = query.offset(offset).limit(limit).all()

        result = []
        for doc in documents:
            result.append({
                'id': doc.id,
                'code': doc.code,
                'title': doc.title,
                'status': doc.status.value if doc.status else None,
                'version': doc.version,
                'created_at': doc.created_at.isoformat(),
                'effective_date': doc.effective_date.isoformat() if doc.effective_date else None,
                'review_date': doc.review_date.isoformat() if doc.review_date else None,
                'signature_required': doc.signature_required,
                'category': doc.category,
                'tags': doc.tags
            })

        # Log de auditoria
        AuditService.log_operation(
            entity_type='integration',
            entity_id=0,
            operation='api_get_documents',
            operation_details={
                'filters': {'status': status, 'code': code},
                'result_count': len(result)
            },
            compliance_level='standard'
        )

        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'offset': offset,
                'limit': limit,
                'count': len(result)
            }
        })

    except Exception as e:
        current_app.logger.error(f"Integration API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@integrations_bp.route('/documents/<int:document_id>', methods=['GET'])
@require_api_key
def get_document(document_id):
    """Obtém detalhes de um documento específico"""
    try:
        document = Document.query.get_or_404(document_id)

        # Verificar se documento é público ou se API tem permissão
        if document.status.value not in ['published']:
            raise Unauthorized("Document not available for integration")

        result = {
            'id': document.id,
            'code': document.code,
            'title': document.title,
            'content': document.content,  # Em produção, pode precisar descriptografar
            'status': document.status.value,
            'version': document.version,
            'created_at': document.created_at.isoformat(),
            'effective_date': document.effective_date.isoformat() if document.effective_date else None,
            'review_date': document.review_date.isoformat() if document.review_date else None,
            'signature_required': document.signature_required,
            'category': document.category,
            'tags': document.tags,
            'norms': [{'id': norm.id, 'code': norm.code, 'name': norm.name} for norm in document.norms],
            'signatures': [sig.to_dict() for sig in document.signatures]
        }

        # Log de auditoria
        AuditService.log_operation(
            entity_type='integration',
            entity_id=document_id,
            operation='api_get_document',
            operation_details={'document_code': document.code},
            compliance_level='standard'
        )

        return jsonify({'success': True, 'data': result})

    except NotFound:
        return jsonify({'success': False, 'error': 'Document not found'}), 404
    except Unauthorized as e:
        return jsonify({'success': False, 'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Integration API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@integrations_bp.route('/documents', methods=['POST'])
@require_api_key
@require_integration_permission('create_documents')
def create_document():
    """Cria novo documento via API"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("JSON data required")

        # Validar campos obrigatórios
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Field '{field}' is required")

        # Criar documento
        document = Document(
            title=data['title'],
            content=data['content'],
            code=data.get('code'),
            category=data.get('category'),
            tags=data.get('tags'),
            status='draft',  # Documentos criados via API começam como rascunho
            created_by_id=1,  # Usuário sistema ou específico da integração
            signature_required=data.get('signature_required', False)
        )

        # Adicionar normas se especificadas
        if 'norm_ids' in data:
            norms = Norm.query.filter(Norm.id.in_(data['norm_ids'])).all()
            document.norms.extend(norms)

        db.session.add(document)
        db.session.commit()

        # Log de auditoria
        AuditService.log_document_operation(
            document,
            'create_via_api',
            details={'source': 'integration_api', 'fields': list(data.keys())}
        )

        return jsonify({
            'success': True,
            'data': {
                'id': document.id,
                'code': document.code,
                'status': 'created'
            }
        }), 201

    except BadRequest as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Integration API error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== USUÁRIOS ====================

@integrations_bp.route('/users', methods=['GET'])
@require_api_key
@require_integration_permission('read_users')
def get_users():
    """Lista usuários para integração com RH"""
    try:
        # Filtros seguros (não expor dados sensíveis)
        role = request.args.get('role')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        query = User.query

        if role:
            query = query.filter_by(role=role)
        if active_only:
            query = query.filter_by(is_active=True)

        users = query.offset(offset).limit(limit).all()

        result = []
        for user in users:
            result.append({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,  # Em produção, pode precisar mascarar
                'role': user.role.value if user.role else None,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            })

        # Log de auditoria
        AuditService.log_operation(
            entity_type='integration',
            entity_id=0,
            operation='api_get_users',
            operation_details={
                'filters': {'role': role, 'active_only': active_only},
                'result_count': len(result)
            },
            compliance_level='critical'  # Dados pessoais
        )

        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'offset': offset,
                'limit': limit,
                'count': len(result)
            }
        })

    except Exception as e:
        current_app.logger.error(f"Integration API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== AUDITORIAS ====================

@integrations_bp.route('/audits', methods=['GET'])
@require_api_key
def get_audits():
    """Lista auditorias para integração"""
    try:
        status = request.args.get('status')
        audit_type = request.args.get('type')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        query = Audit.query

        if status:
            query = query.filter_by(status=status)
        if audit_type:
            query = query.filter_by(audit_type=audit_type)

        audits = query.offset(offset).limit(limit).all()

        result = []
        for audit in audits:
            result.append({
                'id': audit.id,
                'title': audit.title,
                'audit_type': audit.audit_type.value if audit.audit_type else None,
                'status': audit.status,
                'planned_date': audit.planned_date.isoformat() if audit.planned_date else None,
                'actual_date': audit.actual_date.isoformat() if audit.actual_date else None,
                'location': audit.location,
                'progress_percentage': audit.progress_percentage,
                'non_conformities_count': len(audit.non_conformities)
            })

        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'offset': offset,
                'limit': limit,
                'count': len(result)
            }
        })

    except Exception as e:
        current_app.logger.error(f"Integration API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== NÃO CONFORMIDADES ====================

@integrations_bp.route('/non-conformities', methods=['GET'])
@require_api_key
def get_non_conformities():
    """Lista não conformidades para integração"""
    try:
        status = request.args.get('status')
        severity = request.args.get('severity')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        query = NonConformity.query

        if status:
            query = query.filter_by(status=status)
        if severity:
            query = query.filter_by(severity=severity)

        ncs = query.offset(offset).limit(limit).all()

        result = []
        for nc in ncs:
            result.append({
                'id': nc.id,
                'audit_id': nc.audit_id,
                'title': nc.title,
                'description': nc.description,
                'severity': nc.severity,
                'status': nc.status,
                'requirement': nc.requirement,
                'identified_date': nc.identified_date.isoformat() if nc.identified_date else None,
                'target_resolution_date': nc.target_resolution_date.isoformat() if nc.target_resolution_date else None,
                'actual_resolution_date': nc.actual_resolution_date.isoformat() if nc.actual_resolution_date else None
            })

        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'offset': offset,
                'limit': limit,
                'count': len(result)
            }
        })

    except Exception as e:
        current_app.logger.error(f"Integration API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== WEBHOOKS ====================

@integrations_bp.route('/webhooks/documents', methods=['POST'])
@require_api_key
def document_webhook():
    """Webhook para notificações de documentos"""
    try:
        data = request.get_json()
        if not data or 'event' not in data:
            raise BadRequest("Invalid webhook data")

        event = data['event']
        document_id = data.get('document_id')

        # Processar evento
        if event == 'document_published':
            # Notificar sistemas externos sobre documento publicado
            current_app.logger.info(f"Document {document_id} published - webhook received")

        elif event == 'document_signed':
            # Notificar sobre assinatura
            current_app.logger.info(f"Document {document_id} signed - webhook received")

        # Log de auditoria
        AuditService.log_operation(
            entity_type='webhook',
            entity_id=document_id or 0,
            operation=f'webhook_{event}',
            operation_details=data,
            compliance_level='standard'
        )

        return jsonify({'success': True, 'message': 'Webhook processed'})

    except BadRequest as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== HEALTH CHECK ====================

@integrations_bp.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoramento"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# ==================== METRICS ====================

@integrations_bp.route('/metrics', methods=['GET'])
@require_api_key
def get_metrics():
    """Métricas do sistema para monitoramento"""
    try:
        # Métricas básicas
        metrics = {
            'documents': {
                'total': Document.query.count(),
                'published': Document.query.filter_by(status='published').count(),
                'draft': Document.query.filter_by(status='draft').count()
            },
            'users': {
                'total': User.query.count(),
                'active': User.query.filter_by(is_active=True).count()
            },
            'audits': {
                'total': Audit.query.count(),
                'completed': Audit.query.filter_by(status='completed').count(),
                'in_progress': Audit.query.filter_by(status='in_progress').count()
            },
            'non_conformities': {
                'total': NonConformity.query.count(),
                'open': NonConformity.query.filter_by(status='open').count(),
                'resolved': NonConformity.query.filter_by(status='resolved').count()
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        return jsonify({'success': True, 'data': metrics})

    except Exception as e:
        current_app.logger.error(f"Metrics API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500