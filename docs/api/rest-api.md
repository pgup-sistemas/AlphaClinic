# 🔌 API REST - AlphaClinic QMS

## Visão Geral

A API REST do AlphaClinic QMS fornece acesso programático completo às funcionalidades do sistema, com foco especial em integrações empresariais e conformidade legal.

## 🔐 Autenticação

Todas as APIs requerem autenticação via **API Key** no header `X-API-Key`.

```bash
curl -H "X-API-Key: your-api-key" \
     https://alphaclinic.com/api/v1/integrations/documents
```

### Configuração de API Keys

Configure as chaves válidas na variável de ambiente:
```bash
VALID_API_KEYS=key1,key2,key3
```

## 📋 Endpoints de Integração

### Documentos

#### GET /api/v1/integrations/documents
Lista documentos para integração externa.

**Parâmetros de Query:**
- `status` (string): Filtrar por status (draft, review, published, archived)
- `code` (string): Filtrar por código do documento
- `limit` (int): Máximo de resultados (padrão: 50, máximo: 100)
- `offset` (int): Offset para paginação (padrão: 0)

**Exemplo:**
```bash
curl -H "X-API-Key: your-key" \
     "https://alphaclinic.com/api/v1/integrations/documents?status=published&limit=10"
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code": "PROC-001",
      "title": "Procedimento de Calibração",
      "status": "published",
      "version": "1.0",
      "created_at": "2024-12-01T10:00:00Z",
      "effective_date": "2024-12-01",
      "review_date": "2025-12-01",
      "signature_required": true,
      "category": "Procedimentos",
      "tags": "calibração,equipamentos,qualidade"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 10,
    "count": 1
  }
}
```

#### GET /api/v1/integrations/documents/{id}
Obtém detalhes completos de um documento específico.

**Parâmetros de Path:**
- `id` (int): ID do documento

**Exemplo:**
```bash
curl -H "X-API-Key: your-key" \
     https://alphaclinic.com/api/v1/integrations/documents/1
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "code": "PROC-001",
    "title": "Procedimento de Calibração",
    "content": "<p>Conteúdo completo do documento...</p>",
    "status": "published",
    "version": "1.0",
    "created_at": "2024-12-01T10:00:00Z",
    "effective_date": "2024-12-01",
    "review_date": "2025-12-01",
    "signature_required": true,
    "category": "Procedimentos",
    "tags": "calibração,equipamentos,qualidade",
    "norms": [
      {
        "id": 1,
        "code": "ISO9001",
        "name": "ISO 9001:2015"
      }
    ],
    "signatures": [
      {
        "id": 1,
        "signature_type": "approval",
        "user": {
          "id": 1,
          "full_name": "João Silva",
          "role": "manager"
        },
        "signed_at": "2024-12-01T14:30:00Z",
        "is_valid": true,
        "ip_address": "192.168.1.100"
      }
    ]
  }
}
```

#### POST /api/v1/integrations/documents
Cria um novo documento via API.

**Corpo da Requisição:**
```json
{
  "title": "Novo Procedimento",
  "content": "<p>Conteúdo do documento...</p>",
  "code": "PROC-002",
  "category": "Procedimentos",
  "tags": "exemplo,demonstração",
  "signature_required": false,
  "norm_ids": [1, 2]
}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "code": "PROC-002",
    "status": "created"
  }
}
```

### Usuários

#### GET /api/v1/integrations/users
Lista usuários para integração com RH.

**Parâmetros de Query:**
- `role` (string): Filtrar por função (admin, manager, user, auditor)
- `active_only` (boolean): Apenas usuários ativos (padrão: true)
- `limit` (int): Máximo de resultados (padrão: 50, máximo: 100)
- `offset` (int): Offset para paginação (padrão: 0)

**Exemplo:**
```bash
curl -H "X-API-Key: your-key" \
     "https://alphaclinic.com/api/v1/integrations/users?role=manager&active_only=true"
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "joao.silva",
      "full_name": "João Silva",
      "email": "joao.silva@alphaclinic.com",
      "role": "manager",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-12-01T08:00:00Z"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 50,
    "count": 1
  }
}
```

### Auditorias

#### GET /api/v1/integrations/audits
Lista auditorias para integração.

**Parâmetros de Query:**
- `status` (string): Filtrar por status
- `audit_type` (string): Tipo de auditoria (internal, external)
- `limit` (int): Máximo de resultados (padrão: 50, máximo: 100)
- `offset` (int): Offset para paginação (padrão: 0)

**Exemplo:**
```bash
curl -H "X-API-Key: your-key" \
     "https://alphaclinic.com/api/v1/integrations/audits?status=completed&type=internal"
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Auditoria Interna - Sistema de Gestão",
      "audit_type": "internal",
      "status": "completed",
      "planned_date": "2024-11-01",
      "actual_date": "2024-11-15",
      "location": "Clínica Alphaclin - Todas as áreas",
      "progress_percentage": 100,
      "non_conformities_count": 2
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 50,
    "count": 1
  }
}
```

### Não Conformidades

#### GET /api/v1/integrations/non-conformities
Lista não conformidades.

**Parâmetros de Query:**
- `status` (string): Filtrar por status (open, in_progress, resolved, closed)
- `severity` (string): Filtrar por severidade (minor, major, critical)
- `limit` (int): Máximo de resultados (padrão: 50, máximo: 100)
- `offset` (int): Offset para paginação (padrão: 0)

**Exemplo:**
```bash
curl -H "X-API-Key: your-key" \
     "https://alphaclinic.com/api/v1/integrations/non-conformities?status=open&severity=major"
```

### Webhooks

#### POST /api/v1/integrations/webhooks/documents
Webhook para notificações de documentos.

**Eventos Suportados:**
- `document_published`: Documento aprovado e publicado
- `document_signed`: Documento assinado
- `document_archived`: Documento arquivado

**Corpo da Requisição:**
```json
{
  "event": "document_published",
  "document_id": 1,
  "document_code": "PROC-001",
  "document_title": "Procedimento de Calibração",
  "timestamp": "2024-12-01T10:00:00Z",
  "user_id": 1,
  "user_name": "João Silva"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Webhook processed"
}
```

### Métricas

#### GET /api/v1/integrations/metrics
Métricas do sistema para monitoramento.

**Resposta:**
```json
{
  "success": true,
  "data": {
    "documents": {
      "total": 150,
      "published": 120,
      "draft": 30
    },
    "users": {
      "total": 45,
      "active": 42
    },
    "audits": {
      "total": 12,
      "completed": 10,
      "in_progress": 2
    },
    "non_conformities": {
      "total": 25,
      "open": 5,
      "resolved": 20
    },
    "timestamp": "2024-12-01T12:00:00Z"
  }
}
```

### Health Check

#### GET /api/v1/integrations/health
Verificação de saúde do sistema.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-01T12:00:00Z",
  "version": "1.0.0"
}
```

## 📊 APIs de Compliance

### Relatórios

#### GET /compliance/api/reports/overview
Relatório geral de compliance.

**Parâmetros de Query:**
- `days` (int): Período em dias (padrão: 30)

**Exemplo:**
```bash
curl -H "X-API-Key: your-key" \
     "https://alphaclinic.com/compliance/api/reports/overview?days=90"
```

#### GET /compliance/api/audit-trail
Trilha de auditoria completa.

**Parâmetros de Query:**
- `entity_type` (string): Filtrar por tipo de entidade
- `user_id` (int): Filtrar por usuário
- `limit` (int): Máximo de resultados (padrão: 100, máximo: 500)
- `offset` (int): Offset para paginação (padrão: 0)

### Verificação de Integridade

#### GET /compliance/api/verify-integrity
Verifica integridade da trilha de auditoria.

**Resposta:**
```json
{
  "integrity_verified": true,
  "message": "Audit trail integrity verified successfully",
  "verified_at": "2024-12-01T12:00:00Z"
}
```

## 🔒 Segurança e Conformidade

### Rate Limiting
- **Limite:** 1000 requisições por hora por API Key
- **Headers de resposta:** `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Auditoria
- Todas as chamadas de API são auditadas
- Logs incluem: timestamp, API Key (mascarada), endpoint, parâmetros, resposta
- Retenção de logs: 7 anos conforme legislação brasileira

### Conformidade LGPD
- Dados pessoais mascarados em respostas
- Consentimento implícito via contrato de API
- Logs de acesso auditados
- Direito de exclusão de dados implementado

## 📝 Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Dados inválidos |
| 401 | API Key inválida ou ausente |
| 403 | Acesso negado |
| 404 | Recurso não encontrado |
| 429 | Rate limit excedido |
| 500 | Erro interno do servidor |

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# APIs
VALID_API_KEYS=prod-key-1,prod-key-2,staging-key-1

# Rate Limiting
API_RATE_LIMIT=1000

# Timeouts
API_TIMEOUT=30
```

### Monitoramento
- Logs estruturados em JSON
- Métricas Prometheus disponíveis
- Alertas automáticos para falhas
- Dashboard de monitoramento incluído

## 📞 Suporte

Para questões técnicas sobre as APIs:
- **Documentação:** [docs.alphaclinic.com/api](https://docs.alphaclinic.com/api)
- **Suporte:** api@alphaclinic.com
- **Status:** [status.alphaclinic.com](https://status.alphaclinic.com)

---

**Última atualização:** Dezembro 2024
**Versão da API:** v1.0.0