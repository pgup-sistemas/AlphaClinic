"""
Serviço de Auditoria Imutável para Compliance Legal
Implementa trilha de auditoria append-only com integridade criptográfica
"""

from models import AuditLog, db
from flask import request, current_app
from flask_login import current_user
import json
from datetime import datetime

class AuditService:
    """Serviço para gerenciamento de trilha de auditoria imutável"""

    @staticmethod
    def log_operation(entity_type, entity_id, operation, operation_details=None,
                     old_values=None, new_values=None, entity_code=None,
                     compliance_level='standard', retention_period=None):
        """
        Registra uma operação na trilha de auditoria de forma imutável

        Args:
            entity_type: Tipo da entidade (document, user, audit, etc.)
            entity_id: ID da entidade
            operation: Tipo da operação (create, update, delete, sign, etc.)
            operation_details: Detalhes específicos da operação
            old_values: Valores anteriores (para updates)
            new_values: Valores novos (para updates)
            entity_code: Código identificador da entidade
            compliance_level: Nível de compliance (standard, critical, restricted)
            retention_period: Período de retenção em dias
        """

        try:
            # Criar registro de auditoria
            audit_log = AuditLog(
                entity_type=entity_type,
                entity_id=entity_id,
                entity_code=entity_code,
                operation=operation,
                operation_details=operation_details,
                old_values=old_values,
                new_values=new_values,
                compliance_level=compliance_level,
                retention_period=retention_period
            )

            # Preencher informações do usuário
            if current_user and current_user.is_authenticated:
                audit_log.user_id = current_user.id
                audit_log.user_full_name = current_user.full_name
                audit_log.user_role = current_user.role.value if current_user.role else None
            else:
                # Para operações do sistema
                audit_log.user_id = 0  # Usuário sistema
                audit_log.user_full_name = "Sistema"
                audit_log.user_role = "system"

            # Preencher contexto da requisição
            if request:
                audit_log.ip_address = request.remote_addr
                audit_log.user_agent = request.headers.get('User-Agent')
                # session_id poderia vir de session se implementado

            # Salvar de forma imutável
            audit_log.save_immutable()

            current_app.logger.info(f"Audit log created: {entity_type}:{entity_id} - {operation}")

        except Exception as e:
            # Em caso de erro na auditoria, logar mas não falhar a operação
            try:
                current_app.logger.error(f"Failed to create audit log: {str(e)}")
            except:
                print(f"Failed to create audit log: {str(e)}")
            # Em produção, poderia enviar alerta para equipe de compliance

    @staticmethod
    def log_document_operation(document, operation, details=None, old_values=None, new_values=None):
        """Log específico para operações em documentos"""
        AuditService.log_operation(
            entity_type='document',
            entity_id=document.id,
            entity_code=document.code,
            operation=operation,
            operation_details=details,
            old_values=old_values,
            new_values=new_values,
            compliance_level='critical' if document.signature_required else 'standard',
            retention_period=2555  # 7 anos para documentos críticos
        )

    @staticmethod
    def log_user_operation(user, operation, details=None, old_values=None, new_values=None):
        """Log específico para operações em usuários"""
        AuditService.log_operation(
            entity_type='user',
            entity_id=user.id,
            entity_code=user.username,
            operation=operation,
            operation_details=details,
            old_values=old_values,
            new_values=new_values,
            compliance_level='critical',  # Dados pessoais
            retention_period=2555  # 7 anos conforme LGPD
        )

    @staticmethod
    def log_audit_operation(audit, operation, details=None, old_values=None, new_values=None):
        """Log específico para operações em auditorias"""
        AuditService.log_operation(
            entity_type='audit',
            entity_id=audit.id,
            entity_code=f"AUDIT-{audit.id}",
            operation=operation,
            operation_details=details,
            old_values=old_values,
            new_values=new_values,
            compliance_level='critical',
            retention_period=2555  # 7 anos
        )

    @staticmethod
    def log_signature_operation(signature, operation, details=None):
        """Log específico para operações de assinatura"""
        entity_code = f"SIGN-{signature.id}"
        if signature.document:
            entity_code = f"DOC-{signature.document.id}-SIGN-{signature.id}"

        AuditService.log_operation(
            entity_type='signature',
            entity_id=signature.id,
            entity_code=entity_code,
            operation=operation,
            operation_details=details,
            compliance_level='critical',
            retention_period=2555  # 7 anos para assinaturas legais
        )

    @staticmethod
    def verify_audit_integrity():
        """Verifica a integridade de toda a cadeia de auditoria"""
        return AuditLog.verify_chain_integrity()

    @staticmethod
    def get_audit_trail(entity_type=None, entity_id=None, user_id=None,
                       start_date=None, end_date=None, limit=100, offset=0):
        """Consulta a trilha de auditoria com filtros"""

        query = AuditLog.query

        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=entity_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        # Ordenar por sequência (mais recente primeiro)
        query = query.order_by(AuditLog.sequence_number.desc())

        # Paginação
        total = query.count()
        records = query.offset(offset).limit(limit).all()

        return {
            'total': total,
            'records': [record.to_dict() for record in records],
            'integrity_verified': AuditService.verify_audit_integrity()[0]
        }

    @staticmethod
    def export_audit_trail(start_date, end_date, format='json'):
        """Exporta trilha de auditoria para compliance"""
        records = AuditLog.query.filter(
            AuditLog.timestamp.between(start_date, end_date)
        ).order_by(AuditLog.sequence_number).all()

        if format == 'json':
            data = {
                'export_date': datetime.utcnow().isoformat(),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'integrity_check': AuditService.verify_audit_integrity(),
                'records': [record.to_dict() for record in records]
            }
            return json.dumps(data, indent=2, default=str)

        # Outros formatos podem ser implementados (CSV, XML, etc.)
        return None

# Decorators para automatizar logging
def audit_operation(entity_type, operation=None):
    """Decorator para automatizar logging de operações"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Executar função
            result = func(*args, **kwargs)

            # Tentar inferir operação se não especificada
            op = operation or func.__name__.replace('_', ' ')

            # Logar baseado no tipo de entidade
            if entity_type == 'document' and hasattr(result, 'id'):
                AuditService.log_document_operation(result, op)
            elif entity_type == 'user' and hasattr(result, 'id'):
                AuditService.log_user_operation(result, op)
            # Adicionar outros tipos conforme necessário

            return result
        return wrapper
    return decorator

# Hook para SQLAlchemy events
def setup_audit_hooks():
    """Configura hooks automáticos para auditoria"""

    @db.event.listens_for(AuditLog, 'before_update')
    def prevent_audit_log_updates(mapper, connection, target):
        """Impede updates em registros de auditoria (imutabilidade)"""
        raise ValueError("Audit logs are immutable and cannot be modified")

    @db.event.listens_for(AuditLog, 'before_delete')
    def prevent_audit_log_deletes(mapper, connection, target):
        """Impede deletes em registros de auditoria (imutabilidade)"""
        raise ValueError("Audit logs are immutable and cannot be deleted")

# Inicializar hooks quando o módulo for importado
setup_audit_hooks()