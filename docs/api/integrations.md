# 🔌 APIs de Integração - AlphaClinic QMS

## Visão Geral

As APIs de integração do AlphaClinic QMS permitem conexão com sistemas externos, oferecendo acesso programático completo às funcionalidades do sistema com foco em integrações empresariais e conformidade legal.

## 🔐 Autenticação

### API Keys

#### Obtenção de API Key
```bash
# Solicitar API Key via interface web
POST /api/v1/api-keys/request
{
  "requester_name": "João Silva",
  "requester_email": "joao.silva@alphaclin.com",
  "company": "AlphaClinic",
  "purpose": "Integração com sistema ERP",
  "requested_permissions": [
    "documents.read",
    "audits.read",
    "ncs.read",
    "users.read"
  ],
  "contact_person": "Maria Santos",
  "technical_contact": "ti@alphaclin.com"
}
```

#### Uso de API Key
```bash
# Todas as requisições devem incluir a API Key
curl -H "X-API-Key: sua-api-key-aqui" \
     -H "Content-Type: application/json" \
     https://api.alphaclin.com/v1/integrations/documents
```

### OAuth 2.0 (Para aplicações web)

#### Fluxo de Autorização
```javascript
// 1. Redirecionar usuário para autorização
const authUrl = `https://qms.alphaclin.com/oauth/authorize?
  client_id=${clientId}&
  redirect_uri=${redirectUri}&
  response_type=code&
  scope=documents.read%20audits.read&
  state=${state}`;

// 2. Trocar código por token
const tokenResponse = await fetch('https://qms.alphaclin.com/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: clientId,
    client_secret: clientSecret,
    code: authorizationCode,
    redirect_uri: redirectUri
  })
});

// 3. Usar token nas requisições
const apiResponse = await fetch('https://api.alphaclin.com/v1/integrations/documents', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

## 📋 Endpoints de Integração

### Gestão Documental

#### Listar Documentos
```bash
GET /api/v1/integrations/documents

# Parâmetros de query
?status=published
&category=procedimentos
&code=PROC-001
&limit=50
&offset=0
&updated_after=2024-01-01T00:00:00Z
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "code": "PROC-001",
      "title": "Procedimento de Higienização",
      "status": "published",
      "version": "2.1",
      "category": "Procedimentos",
      "type": "procedure",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-11-20T14:30:00Z",
      "effective_date": "2024-01-15",
      "review_date": "2025-01-15",
      "signature_required": true,
      "confidentiality": "internal",
      "tags": ["higienização", "equipamentos", "qualidade"],
      "norms": [
        {
          "id": 1,
          "code": "ISO9001",
          "name": "ISO 9001:2015",
          "section": "8.5.1"
        }
      ],
      "author": {
        "id": 1,
        "name": "João Silva",
        "email": "joao.silva@alphaclin.com"
      },
      "file_info": {
        "size_bytes": 245760,
        "mime_type": "application/pdf",
        "pages": 15
      }
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 50,
    "total": 1247,
    "has_next": true,
    "next_offset": 50
  },
  "metadata": {
    "generated_at": "2024-12-01T10:30:00Z",
    "filters_applied": {
      "status": "published",
      "category": "procedimentos"
    }
  }
}
```

#### Obter Documento Específico
```bash
GET /api/v1/integrations/documents/{document_id}

# Parâmetros opcionais
?include_content=true
&include_attachments=true
&include_signatures=true
&include_audit_trail=true
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "code": "PROC-001",
    "title": "Procedimento de Higienização",
    "content": "<p>Conteúdo completo do documento em HTML...</p>",
    "status": "published",
    "version": "2.1",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-11-20T14:30:00Z",
    "effective_date": "2024-01-15",
    "review_date": "2025-01-15",
    "category": "Procedimentos",
    "type": "procedure",
    "priority": "high",
    "confidentiality": "internal",
    "tags": ["higienização", "equipamentos", "qualidade"],
    "norms": [
      {
        "id": 1,
        "code": "ISO9001",
        "name": "ISO 9001:2015",
        "section": "8.5.1"
      }
    ],
    "author": {
      "id": 1,
      "name": "João Silva",
      "email": "joao.silva@alphaclin.com"
    },
    "reviewers": [
      {
        "user_id": 2,
        "name": "Maria Santos",
        "review_date": "2024-11-18T10:00:00Z",
        "status": "approved"
      }
    ],
    "approvers": [
      {
        "user_id": 3,
        "name": "Carlos Oliveira",
        "approval_date": "2024-11-20T14:30:00Z",
        "status": "approved"
      }
    ],
    "signatures": [
      {
        "signature_id": 1,
        "user_id": 3,
        "signature_type": "qualified",
        "signed_at": "2024-11-20T14:30:00Z",
        "is_valid": true,
        "certificate_info": {
          "issuer": "Serasa Experian",
          "valid_until": "2024-12-31"
        }
      }
    ],
    "attachments": [
      {
        "id": 1,
        "name": "fluxograma.pdf",
        "size_bytes": 102400,
        "mime_type": "application/pdf",
        "uploaded_at": "2024-11-20T14:25:00Z"
      }
    ],
    "audit_trail": [
      {
        "event": "document_created",
        "timestamp": "2024-01-15T10:00:00Z",
        "user": "João Silva",
        "details": "Documento criado inicialmente"
      },
      {
        "event": "document_updated",
        "timestamp": "2024-11-20T14:30:00Z",
        "user": "Carlos Oliveira",
        "details": "Versão 2.1 aprovada e publicada"
      }
    ]
  }
}
```

#### Criar Documento
```bash
POST /api/v1/integrations/documents

# Corpo da requisição
{
  "title": "Novo Procedimento",
  "code": "PROC-002",
  "content": "<p>Conteúdo do documento em HTML</p>",
  "category": "Procedimentos",
  "type": "procedure",
  "priority": "medium",
  "confidentiality": "internal",
  "tags": ["exemplo", "integração"],
  "norms": [1, 2],
  "signature_required": true,
  "reviewers": [2, 3],
  "approvers": [4],
  "effective_date": "2024-12-01",
  "review_period_months": 12
}
```

### Gestão de Usuários

#### Listar Usuários
```bash
GET /api/v1/integrations/users

# Filtros disponíveis
?role=manager
&department=Centro_Cirurgico
&active_only=true
&limit=100
&offset=0
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "joao.silva",
      "full_name": "João Silva Santos",
      "email": "joao.silva@alphaclin.com",
      "role": "enfermeiro_chefe",
      "department": "Centro Cirúrgico",
      "is_active": true,
      "last_login": "2024-12-01T08:30:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "permissions": [
        "documents.read",
        "documents.create",
        "documents.approve"
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 100,
    "total": 156,
    "has_next": true
  }
}
```

### Gestão de Auditorias

#### Listar Auditorias
```bash
GET /api/v1/integrations/audits

# Filtros disponíveis
?status=completed
&type=internal
&year=2024
&limit=50
&offset=0
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 456,
      "title": "Auditoria Interna Q4 2024",
      "type": "internal",
      "status": "completed",
      "planned_date": "2024-11-01",
      "actual_date": "2024-11-15",
      "completion_date": "2024-11-15",
      "auditors": [
        {
          "id": 4,
          "name": "Ana Costa",
          "email": "ana.costa@alphaclin.com"
        }
      ],
      "areas": ["Centro Cirúrgico", "Enfermagem"],
      "findings_count": {
        "critical": 0,
        "major": 2,
        "minor": 5,
        "observations": 3
      },
      "overall_result": "Satisfatório"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 50,
    "total": 12,
    "has_next": false
  }
}
```

### Gestão de Não Conformidades

#### Listar NCs
```bash
GET /api/v1/integrations/non-conformities

# Filtros disponíveis
?status=open
&classification=major
&responsible_user=5
&limit=50
&offset=0
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "number": "NC-2024-001",
      "title": "Procedimento de Higienização Não Seguido",
      "classification": "major",
      "status": "in_progress",
      "description": "Durante auditoria, observou-se que técnicos não utilizam EPIs adequados",
      "process_affected": "Higienização de Equipamentos",
      "area_responsible": "Centro Cirúrgico",
      "reported_by": {
        "id": 4,
        "name": "Ana Costa"
      },
      "responsible": {
        "id": 5,
        "name": "Roberto Lima"
      },
      "created_at": "2024-12-01T10:30:00Z",
      "deadline": "2024-12-15T17:00:00Z",
      "progress_percentage": 60,
      "actions_taken": [
        "Treinamento realizado",
        "Procedimento sendo revisado"
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 50,
    "total": 25,
    "has_next": false
  }
}
```

## 📊 APIs de Relatórios

### Relatórios de Visão Geral

#### Métricas Gerais
```bash
GET /api/v1/integrations/metrics

# Parâmetros opcionais
?period=30d
&include_trends=true
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "documents": {
      "total": 1247,
      "published": 1156,
      "draft": 91,
      "trend": "+5% vs mês anterior"
    },
    "users": {
      "total": 156,
      "active": 142,
      "inactive": 14,
      "new_this_month": 3
    },
    "audits": {
      "total": 12,
      "completed": 10,
      "in_progress": 2,
      "planned": 8
    },
    "non_conformities": {
      "total": 25,
      "open": 5,
      "in_progress": 12,
      "closed": 8,
      "overdue": 2
    },
    "system_health": {
      "uptime_percentage": 99.8,
      "average_response_time_ms": 245,
      "error_rate_percentage": 0.2
    }
  },
  "generated_at": "2024-12-01T10:30:00Z"
}
```

### Relatórios Específicos

#### Relatório de Conformidade
```bash
GET /api/v1/integrations/reports/compliance

# Parâmetros
?norm=ISO9001
&period=2024
&format=json
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "norm": "ISO 9001:2015",
    "period": "2024-01-01 to 2024-12-31",
    "overall_compliance": 94.2,
    "requirements": [
      {
        "section": "4 - Contexto da organização",
        "compliance_percentage": 96.5,
        "findings": 2,
        "status": "Conforme"
      },
      {
        "section": "5 - Liderança",
        "compliance_percentage": 92.1,
        "findings": 3,
        "status": "Conforme com observações"
      },
      {
        "section": "8 - Operação",
        "compliance_percentage": 94.8,
        "findings": 1,
        "status": "Conforme"
      }
    ],
    "trends": {
      "quarterly_compliance": [91.2, 92.8, 93.5, 94.2],
      "findings_trend": [15, 12, 8, 6]
    }
  }
}
```

## 🔒 Segurança e Conformidade

### Rate Limiting

#### Controle de Taxa por API Key
```bash
# Headers de resposta incluem limites
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1609459200
```

**Resposta quando limite excedido:**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "retry_after": 3600
  }
}
```

### Auditoria de API

#### Log de Todas as Chamadas
```javascript
const apiAuditLog = {
  "request_id": "req_abc123def456",
  "timestamp": "2024-12-01T10:30:00Z",
  "api_key": "ak_1234567890abcdef", // Mascarada para segurança
  "client_info": {
    "ip_address": "192.168.1.100",
    "user_agent": "ERP-System/1.0",
    "application": "ERP-AlphaClinic"
  },
  "request": {
    "method": "GET",
    "endpoint": "/api/v1/integrations/documents",
    "query_parameters": {
      "status": "published",
      "limit": "50"
    },
    "headers": {
      "X-API-Key": "ak_1234567890abcdef",
      "User-Agent": "ERP-System/1.0"
    }
  },
  "response": {
    "status_code": 200,
    "response_size_bytes": 15420,
    "response_time_ms": 245
  },
  "data_accessed": {
    "resource_type": "documents",
    "record_count": 45,
    "fields_accessed": ["id", "code", "title", "status", "version"]
  }
};
```

## 📞 Webhooks para Integração

### Configuração de Webhooks

#### Webhook para Documentos
```bash
# Webhook para notificações de documentos
POST /api/v1/integrations/webhooks/documents

# Payload enviado
{
  "event": "document_published",
  "timestamp": "2024-12-01T10:30:00Z",
  "document": {
    "id": 123,
    "code": "PROC-001",
    "title": "Procedimento de Higienização",
    "version": "2.1",
    "status": "published",
    "effective_date": "2024-12-01",
    "url": "https://qms.alphaclin.com/documents/123"
  },
  "user": {
    "id": 3,
    "name": "Carlos Oliveira",
    "email": "carlos.oliveira@alphaclin.com"
  }
}
```

### Eventos Disponíveis para Webhook

#### Eventos de Documento
- `document.created` - Novo documento criado
- `document.updated` - Documento modificado
- `document.submitted` - Documento submetido para revisão
- `document.reviewed` - Documento revisado
- `document.approved` - Documento aprovado
- `document.published` - Documento publicado
- `document.signed` - Documento assinado
- `document.archived` - Documento arquivado

#### Eventos de Auditoria
- `audit.scheduled` - Auditoria agendada
- `audit.started` - Auditoria iniciada
- `audit.finding_identified` - Achado identificado
- `audit.completed` - Auditoria concluída

#### Eventos de NC
- `nc.created` - NC criada
- `nc.assigned` - NC atribuída
- `nc.in_progress` - NC em andamento
- `nc.resolved` - NC resolvida
- `nc.closed` - NC encerrada

## 🔧 Configuração Avançada

### Variáveis de Ambiente

#### Configurações de Integração
```bash
# APIs
API_HOST=https://api.alphaclin.com
API_VERSION=v1
API_TIMEOUT=30

# Autenticação
VALID_API_KEYS=key1,key2,key3,key4,key5
API_RATE_LIMIT_PER_KEY=1000

# Webhooks
WEBHOOK_TIMEOUT=10
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_SECRET_KEY=sua-chave-secreta-webhook

# Auditoria
API_AUDIT_ENABLED=true
API_AUDIT_RETENTION_DAYS=2555

# Rate Limiting
RATE_LIMIT_WINDOW_HOURS=1
RATE_LIMIT_MAX_REQUESTS=1000
```

### Timeouts e Retries

#### Configuração de Timeout
```javascript
const timeoutConfig = {
  "connect_timeout": 10,     // Tempo para estabelecer conexão
  "request_timeout": 30,     // Tempo total da requisição
  "retry_attempts": 3,       // Número de tentativas
  "retry_delay": 1,          // Delay entre tentativas (segundos)
  "retry_backoff": "exponential" // Estratégia de backoff
};
```

## 📊 Monitoramento e Health Check

### Health Check
```bash
GET /api/v1/integrations/health

# Resposta
{
  "status": "healthy",
  "timestamp": "2024-12-01T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "storage": "healthy",
    "email": "healthy"
  },
  "response_time_ms": 45
}
```

### Métricas de Performance
```bash
GET /api/v1/integrations/metrics/performance

# Resposta
{
  "period": "2024-12-01T00:00:00Z to 2024-12-01T23:59:59Z",
  "requests": {
    "total": 15420,
    "successful": 14895,
    "failed": 525,
    "success_rate": 96.6
  },
  "response_times": {
    "average_ms": 245,
    "median_ms": 180,
    "p95_ms": 850,
    "p99_ms": 1200
  },
  "endpoints": {
    "/documents": {
      "requests": 8500,
      "avg_response_ms": 180,
      "error_rate": 0.02
    },
    "/audits": {
      "requests": 3200,
      "avg_response_ms": 320,
      "error_rate": 0.01
    }
  }
}
```

## 🚨 Tratamento de Erros

### Códigos de Erro

#### Erros de Autenticação
```json
{
  "success": false,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid or expired",
    "details": "API key 'ak_invalid' not found in system"
  }
}
```

#### Erros de Autorização
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "Your API key does not have permission to access this resource",
    "details": "Required permission: 'documents.write', provided: ['documents.read']"
  }
}
```

#### Erros de Rate Limiting
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded for this API key",
    "details": "Limit: 1000 requests/hour, used: 1000, retry after: 3600 seconds"
  }
}
```

#### Erros de Dados
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The provided data is invalid",
    "details": {
      "title": ["Title is required"],
      "category": ["Category must be one of: procedimentos, políticas, formulários"]
    }
  }
}
```

## 📞 Exemplos de Integração

### Exemplo 1: Sincronização de Documentos com ERP

#### Script de Sincronização
```python
import requests
import json
from datetime import datetime, timedelta

class QMSIntegration:
    def __init__(self, api_key, base_url="https://api.alphaclin.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def get_updated_documents(self, since_date):
        """Obter documentos atualizados desde data específica"""
        endpoint = f"{self.base_url}/integrations/documents"
        params = {
            "status": "published",
            "updated_after": since_date.isoformat(),
            "limit": 100
        }

        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()["data"]

    def sync_to_erp(self, documents):
        """Sincronizar documentos com ERP"""
        for doc in documents:
            erp_document = {
                "code": doc["code"],
                "title": doc["title"],
                "version": doc["version"],
                "effective_date": doc["effective_date"],
                "content_hash": hash(doc["content"])
            }

            # Enviar para ERP
            erp_response = requests.post(
                "https://erp.alphaclin.com/api/documents/sync",
                json=erp_document,
                headers={"Authorization": f"Bearer {erp_token}"}
            )

            if erp_response.status_code == 200:
                print(f"Documento {doc['code']} sincronizado com sucesso")
            else:
                print(f"Erro ao sincronizar documento {doc['code']}: {erp_response.text}")

# Uso da integração
if __name__ == "__main__":
    qms = QMSIntegration(api_key="sua-api-key")

    # Sincronizar documentos das últimas 24 horas
    since_date = datetime.now() - timedelta(days=1)
    updated_docs = qms.get_updated_documents(since_date)

    qms.sync_to_erp(updated_docs)
```

### Exemplo 2: Dashboard de NCs em Tempo Real

#### Aplicação Web para Monitoramento
```javascript
class NCDashboard {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://api.alphaclin.com/v1';
        this.headers = {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        };
    }

    async loadNCs() {
        try {
            const response = await fetch(
                `${this.baseUrl}/integrations/non-conformities?status=open&limit=100`,
                { headers: this.headers }
            );

            const data = await response.json();

            if (data.success) {
                this.renderNCs(data.data);
                this.updateKPIs(data.data);
            }
        } catch (error) {
            console.error('Erro ao carregar NCs:', error);
        }
    }

    renderNCs(ncs) {
        const container = document.getElementById('ncs-container');

        container.innerHTML = ncs.map(nc => `
            <div class="nc-card ${nc.classification}">
                <div class="nc-header">
                    <h3>${nc.number}</h3>
                    <span class="classification ${nc.classification}">${nc.classification}</span>
                </div>
                <div class="nc-content">
                    <h4>${nc.title}</h4>
                    <p>${nc.description}</p>
                    <div class="nc-meta">
                        <span>Responsável: ${nc.responsible.name}</span>
                        <span>Prazo: ${formatDate(nc.deadline)}</span>
                    </div>
                </div>
                <div class="nc-actions">
                    <button onclick="viewNC(${nc.id})">Ver Detalhes</button>
                    <button onclick="updateNC(${nc.id})">Atualizar</button>
                </div>
            </div>
        `).join('');
    }

    updateKPIs(ncs) {
        const critical = ncs.filter(nc => nc.classification === 'critical').length;
        const major = ncs.filter(nc => nc.classification === 'major').length;
        const overdue = ncs.filter(nc => new Date(nc.deadline) < new Date()).length;

        document.getElementById('kpi-critical').textContent = critical;
        document.getElementById('kpi-major').textContent = major;
        document.getElementById('kpi-overdue').textContent = overdue;
    }
}

// Inicializar dashboard
const dashboard = new NCDashboard('sua-api-key');
dashboard.loadNCs();

// Atualizar a cada 5 minutos
setInterval(() => dashboard.loadNCs(), 5 * 60 * 1000);
```

## 🎯 Melhores Práticas

### Para Desenvolvedores
- ✅ Use HTTPS sempre
- ✅ Implemente tratamento adequado de erros
- ✅ Respeite rate limits
- ✅ Mantenha logs de integração
- ✅ Teste integrações em ambiente de desenvolvimento

### Para Segurança
- ✅ Mantenha API keys seguras
- ✅ Use variáveis de ambiente
- ✅ Implemente validação de dados
- ✅ Monitore acessos não autorizados
- ✅ Revise permissões regularmente

### Para Performance
- ✅ Use paginação para grandes conjuntos de dados
- ✅ Implemente cache quando apropriado
- ✅ Minimize número de requisições
- ✅ Use compressão de dados
- ✅ Monitore tempos de resposta

## 📞 Suporte

### Documentação Adicional
- **Swagger UI**: https://api.alphaclin.com/docs
- **Postman Collection**: Disponível para download
- **Exemplos de Código**: https://github.com/alphaclin/qms-api-examples

### Contato de Suporte
- **Email**: api@alphaclin.com
- **Slack**: #api-support
- **Telefone**: +55 11 99999-9999

---

**Última atualização:** Dezembro 2024
**Versão da API:** v1.0.0