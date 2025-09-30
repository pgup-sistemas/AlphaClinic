# 📚 Alphaclin QMS - API Documentation

## 🚀 **VISÃO GERAL**

Sistema completo de Gestão da Qualidade com APIs RESTful modernas para integração com sistemas externos.

**Base URL:** `http://localhost:8000/api/v1`

## 🔐 **AUTENTICAÇÃO**

Todas as APIs (exceto health check) requerem autenticação via sessão Flask-Login.

## 📊 **ENDPOINTS PRINCIPAIS**

### **Health Check**
```http
GET /api/v1/health
```
**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "1.0.0",
  "services": {
    "database_connected": true,
    "cache_available": true
  }
}
```

### **Dashboard Metrics**
```http
GET /api/v1/dashboard-metrics
```
**Resposta:**
```json
{
  "success": true,
  "data": {
    "documents": {"total": 150, "published": 120, "draft": 30},
    "audits": {"total": 45, "completed": 40, "in_progress": 5},
    "non_conformities": {"total": 12, "open": 3, "resolved": 9},
    "capa": {"total": 8, "closed": 6, "in_progress": 2},
    "system": {"total_users": 25, "active_users": 20}
  },
  "cached": true,
  "timestamp": "2024-01-01T00:00:00"
}
```

### **Documentos**
```http
GET /api/v1/documents?status=published&limit=10&offset=0
```
**Parâmetros:**
- `status`: `draft`, `review`, `published`, `archived`
- `category`: Categoria específica
- `limit`: Número de resultados (máx 100)
- `offset`: Offset para paginação

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Procedimento de Calibração",
      "code": "PROC-CAL-001",
      "version": "1.0",
      "status": "published",
      "category": "Procedimentos",
      "created_by": "Administrador",
      "created_at": "2024-01-01T10:00:00",
      "signature_required": true,
      "norms": ["ISO9001", "ONA"]
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

### **Auditorias**
```http
GET /api/v1/audits?status=completed&type=internal&limit=20
```
**Parâmetros:**
- `status`: `planned`, `in_progress`, `completed`
- `type`: `internal`, `external`
- `limit`: Número de resultados (máx 100)

### **Não Conformidades**
```http
GET /api/v1/non-conformities?severity=critical&assigned_to=5
```
**Parâmetros:**
- `status`: `open`, `in_progress`, `resolved`, `closed`
- `severity`: `minor`, `major`, `critical`
- `assigned_to`: ID do usuário responsável

### **CAPA (Planos de Ação)**
```http
GET /api/v1/capa?status=approved&priority=high
```
**Parâmetros:**
- `status`: `draft`, `approved`, `implemented`, `verified`, `closed`
- `type`: `corrective`, `preventive`
- `priority`: `low`, `medium`, `high`, `critical`

## 🤖 **MACHINE LEARNING E PREDIÇÕES**

### **Predição de Risco de NCs**
```http
GET /api/v1/ml/predict/nc-risk?user_id=5&process_id=10
```
**Parâmetros:**
- `user_id`: ID do usuário (opcional)
- `process_id`: ID do processo (opcional)
- `norm_id`: ID da norma (opcional)

**Resposta:**
```json
{
  "success": true,
  "data": {
    "risk_level": "medium",
    "confidence": 0.75,
    "risk_score": 0.65,
    "factors": {
      "volume": 0.7,
      "severity": 0.6,
      "resolution_time": 0.65
    },
    "recommendations": [
      "Aumentar frequência de auditorias internas",
      "Focar em treinamento para requisitos críticos"
    ],
    "data_points": 45,
    "analysis_period_days": 180
  }
}
```

### **Predição de Tempo de Aprovação**
```http
POST /api/v1/ml/predict/document-approval-time
Content-Type: application/json

{
  "category": "Procedimentos",
  "complexity": "medium",
  "signature_required": true
}
```

### **Insights do Sistema**
```http
GET /api/v1/ml/insights
```
**Resposta:**
```json
{
  "success": true,
  "data": {
    "nc_trends": {
      "recent_count": 12,
      "previous_count": 8,
      "trend_percentage": 50.0,
      "trend_direction": "increasing"
    },
    "user_performance": {
      "total_active_users": 20,
      "avg_completion_rate": 85.5
    },
    "process_effectiveness": {
      "total_processes": 15,
      "high_risk_processes": 2
    }
  }
}
```

## 📈 **RELATÓRIOS AVANÇADOS**

### **Geração de Relatórios**
```http
POST /api/v1/reports/generate/compliance_overview?format=pdf
Content-Type: application/json

{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```
**Tipos de relatório:**
- `compliance_overview`: Visão geral de compliance
- `audit_effectiveness`: Efetividade de auditorias
- `nc_analysis`: Análise de NCs
- `capa_status`: Status de CAPAs
- `system_usage`: Uso do sistema

**Formatos suportados:**
- `pdf`: Relatório em PDF
- `excel`: Planilha Excel
- `html`: Página HTML
- `json`: Dados JSON

### **Tipos de Relatório Disponíveis**
```http
GET /api/v1/reports/types
```

## 🔒 **LGPD COMPLIANCE**

### **Consentimento LGPD**
```http
POST /api/v1/lgpd/consent
Content-Type: application/json

{
  "purpose": "document_management",
  "consent_data": {
    "ip_address": "192.168.1.100",
    "consent_version": "1.0"
  }
}
```

### **Retirada de Consentimento**
```http
DELETE /api/v1/lgpd/consent/document_management
```

### **Portfólio de Dados**
```http
GET /api/v1/lgpd/data-portfolio
```

### **Solicitação de Direitos**
```http
POST /api/v1/lgpd/request
Content-Type: application/json

{
  "request_type": "access_data",
  "description": "Solicito acesso aos meus dados pessoais",
  "contact_email": "usuario@exemplo.com"
}
```

### **Relatório LGPD**
```http
GET /api/v1/lgpd/compliance-report
```

## ⛓️ **BLOCKCHAIN AUDITORIA**

### **Informações da Cadeia**
```http
GET /api/v1/blockchain/chain-info
```

### **Verificação de Log**
```http
GET /api/v1/blockchain/verify/123
```

### **Trilha com Blockchain**
```http
GET /api/v1/blockchain/audit-trail?start_date=2024-01-01&end_date=2024-01-31
```

### **Exportação da Cadeia**
```http
GET /api/v1/blockchain/export?format=json
```

## 📋 **CÓDIGOS DE STATUS**

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado |
| 400 | Requisição inválida |
| 401 | Não autorizado |
| 403 | Acesso negado |
| 404 | Não encontrado |
| 500 | Erro interno do servidor |

## 🚦 **TRATAMENTO DE ERROS**

Todas as respostas incluem:
```json
{
  "success": false,
  "error": "Mensagem de erro descritiva",
  "timestamp": "2024-01-01T00:00:00"
}
```

## 📊 **PERFORMANCE**

- **Cache:** Implementado para métricas de dashboard (TTL: 5 minutos)
- **Paginação:** Todos os endpoints suportam paginação
- **Índices:** Otimizados para consultas frequentes
- **Compressão:** Respostas comprimidas automaticamente

## 🔄 **VERSIONAMENTO**

API Version: **v1**
- Todas as mudanças breaking serão na v2+
- Campos novos são adicionados sem breaking changes
- Campos obsoletos são marcados como deprecated

## 📞 **SUPORTE**

Para dúvidas ou problemas:
- Documentação online: `/docs/api/rest-api`
- E-mail: admin@alphaclinic.com
- Sistema de tickets: Integrado ao módulo de suporte

---

**Alphaclin QMS API v1.0** - Sistema de Gestão da Qualidade de última geração