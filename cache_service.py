"""
Serviço de Cache para Otimização de Performance
Implementa cache Redis para consultas frequentes e dados de dashboard
"""

import json
import pickle
from datetime import datetime, timedelta
from flask import current_app
from models import db
from sqlalchemy import text

class CacheService:
    """Serviço de cache para otimização de performance"""

    def __init__(self):
        self.cache_ttl = {
            'dashboard_metrics': 300,  # 5 minutos
            'document_stats': 600,     # 10 minutos
            'audit_stats': 600,        # 10 minutos
            'user_stats': 1800,        # 30 minutos
            'system_health': 60        # 1 minuto
        }

    def _get_cache_key(self, key: str) -> str:
        """Gera chave de cache com prefixo"""
        return f"alphaclin_qms:{key}"

    def _serialize_data(self, data) -> str:
        """Serializa dados para cache"""
        try:
            # Tentar JSON primeiro (mais eficiente)
            return json.dumps(data, default=str)
        except (TypeError, ValueError):
            # Fallback para pickle se JSON falhar
            return pickle.dumps(data).decode('latin-1')

    def _deserialize_data(self, data: str):
        """Deserializa dados do cache"""
        try:
            # Tentar JSON primeiro
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            # Fallback para pickle
            return pickle.loads(data.encode('latin-1'))

    def get(self, key: str):
        """Obtém valor do cache"""
        try:
            # Em produção: usar Redis
            # Por enquanto: usar cache simples em memória (não persistente)
            cache_key = self._get_cache_key(key)

            # Simular cache (em produção usar Redis)
            # return redis_client.get(cache_key)

            # Para desenvolvimento: retornar None (sempre buscar do banco)
            return None

        except Exception as e:
            current_app.logger.error(f"Erro ao obter do cache: {str(e)}")
            return None

    def set(self, key: str, value, ttl: int = None):
        """Define valor no cache"""
        try:
            cache_key = self._get_cache_key(key)
            serialized_value = self._serialize_data(value)

            # Em produção: usar Redis
            # redis_client.setex(cache_key, ttl or self.cache_ttl.get(key, 300), serialized_value)

            # Para desenvolvimento: apenas log
            current_app.logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")

        except Exception as e:
            current_app.logger.error(f"Erro ao definir cache: {str(e)}")

    def delete(self, key: str):
        """Remove valor do cache"""
        try:
            cache_key = self._get_cache_key(key)

            # Em produção: usar Redis
            # redis_client.delete(cache_key)

            current_app.logger.debug(f"Cache DELETE: {cache_key}")

        except Exception as e:
            current_app.logger.error(f"Erro ao remover do cache: {str(e)}")

    def clear_pattern(self, pattern: str):
        """Limpa cache baseado em padrão"""
        try:
            cache_pattern = self._get_cache_key(pattern)

            # Em produção: usar Redis
            # keys = redis_client.keys(cache_pattern)
            # if keys:
            #     redis_client.delete(*keys)

            current_app.logger.debug(f"Cache CLEAR PATTERN: {cache_pattern}")

        except Exception as e:
            current_app.logger.error(f"Erro ao limpar cache por padrão: {str(e)}")

    def get_dashboard_metrics(self, user_id: int = None):
        """Obtém métricas do dashboard do cache ou calcula"""
        cache_key = f"dashboard_metrics:{user_id}" if user_id else "dashboard_metrics:global"

        # Tentar obter do cache
        cached_data = self.get(cache_key)
        if cached_data:
            return self._deserialize_data(cached_data)

        # Calcular métricas (em produção, usar analytics_service)
        from analytics_service import analytics_service
        metrics = analytics_service.get_dashboard_data(user_id)

        # Armazenar no cache
        self.set(cache_key, metrics, self.cache_ttl['dashboard_metrics'])

        return metrics

    def get_document_stats(self):
        """Obtém estatísticas de documentos do cache"""
        cache_key = "document_stats"

        cached_data = self.get(cache_key)
        if cached_data:
            return self._deserialize_data(cached_data)

        # Calcular estatísticas usando consulta otimizada
        from models import Document, DocumentStatus

        stats = db.session.query(
            Document.status,
            db.func.count(Document.id)
        ).group_by(Document.status).all()

        stats_dict = {status.value: count for status, count in stats}

        # Adicionar totais
        stats_dict['total'] = sum(stats_dict.values())
        stats_dict['cached_at'] = datetime.utcnow().isoformat()

        self.set(cache_key, stats_dict, self.cache_ttl['document_stats'])

        return stats_dict

    def get_audit_stats(self):
        """Obtém estatísticas de auditorias do cache"""
        cache_key = "audit_stats"

        cached_data = self.get(cache_key)
        if cached_data:
            return self._deserialize_data(cached_data)

        # Consulta otimizada com índices
        from models import Audit

        stats = db.session.query(
            Audit.status,
            db.func.count(Audit.id)
        ).group_by(Audit.status).all()

        stats_dict = {status: count for status, count in stats}
        stats_dict['total'] = sum(stats_dict.values())
        stats_dict['cached_at'] = datetime.utcnow().isoformat()

        self.set(cache_key, stats_dict, self.cache_ttl['audit_stats'])

        return stats_dict

    def get_system_health(self):
        """Obtém métricas de saúde do sistema"""
        cache_key = "system_health"

        cached_data = self.get(cache_key)
        if cached_data:
            return self._deserialize_data(cached_data)

        # Verificar saúde do sistema
        health = {
            'database_connected': self._check_database_connection(),
            'cache_available': True,  # Em produção verificar Redis
            'disk_space': self._get_disk_space(),
            'memory_usage': self._get_memory_usage(),
            'active_users': self._get_active_users_count(),
            'pending_emails': self._get_pending_emails_count(),
            'checked_at': datetime.utcnow().isoformat()
        }

        self.set(cache_key, health, self.cache_ttl['system_health'])

        return health

    def _check_database_connection(self) -> bool:
        """Verifica conexão com banco de dados"""
        try:
            db.session.execute(text('SELECT 1'))
            return True
        except Exception:
            return False

    def _get_disk_space(self) -> dict:
        """Obtém informações de espaço em disco"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            return {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'usage_percent': round((used / total) * 100, 2)
            }
        except Exception:
            return {'error': 'Não foi possível obter informações de disco'}

    def _get_memory_usage(self) -> dict:
        """Obtém informações de uso de memória"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'usage_percent': memory.percent
            }
        except Exception:
            return {'error': 'Não foi possível obter informações de memória'}

    def _get_active_users_count(self) -> int:
        """Obtém contagem de usuários ativos"""
        try:
            from models import User
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            return User.query.filter(
                User.last_login >= thirty_days_ago
            ).count()
        except Exception:
            return 0

    def _get_pending_emails_count(self) -> int:
        """Obtém contagem de e-mails pendentes"""
        try:
            from models import EmailQueue
            return EmailQueue.query.filter_by(status='pending').count()
        except Exception:
            return 0

    def invalidate_user_cache(self, user_id: int):
        """Invalida cache relacionado ao usuário"""
        patterns_to_clear = [
            f"dashboard_metrics:{user_id}",
            f"dashboard_layout:{user_id}",
            f"user_notifications:{user_id}",
            f"user_preferences:{user_id}"
        ]

        for pattern in patterns_to_clear:
            self.delete(pattern)

    def invalidate_document_cache(self, document_id: int = None):
        """Invalida cache relacionado a documentos"""
        self.clear_pattern("document_stats")
        self.clear_pattern("dashboard_metrics:*")

        if document_id:
            self.delete(f"document:{document_id}")

    def invalidate_audit_cache(self, audit_id: int = None):
        """Invalida cache relacionado a auditorias"""
        self.clear_pattern("audit_stats")
        self.clear_pattern("dashboard_metrics:*")

        if audit_id:
            self.delete(f"audit:{audit_id}")

    def warmup_cache(self):
        """Pré-carrega cache com dados importantes"""
        try:
            current_app.logger.info("Iniciando warm-up do cache...")

            # Carregar métricas principais
            self.get_dashboard_metrics()
            self.get_document_stats()
            self.get_audit_stats()
            self.get_system_health()

            current_app.logger.info("Warm-up do cache concluído")

        except Exception as e:
            current_app.logger.error(f"Erro no warm-up do cache: {str(e)}")

# Instância global
cache_service = CacheService()