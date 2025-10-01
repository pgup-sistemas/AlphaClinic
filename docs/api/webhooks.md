# 🔗 Webhooks - AlphaClinic QMS

## Visão Geral

Os webhooks do AlphaClinic QMS permitem integração em tempo real com sistemas externos, enviando notificações automáticas quando eventos específicos ocorrem no sistema.

## 📋 Eventos Disponíveis

### Eventos de Documentos

#### Documento Criado
```javascript
{
  "event": "document.created",
  "timestamp": "2024-12-01T10:30:00Z",
  "data": {
    "document_id": 123,
    "code": "PROC-001",
    "title": "Procedimento de Higienização",
    "version": "1.0",
    "status": "draft",
    "created_by": {
      "user_id": 1,
      "name": "João Silva",
      "email": "joao.silva@alphaclin.com"
    },
    "category": "Procedimentos",
    "priority": "high"
  }
}
```

#### Documento Aprovado
```javascript
{
  "event": "document.approved",
  "timestamp": "2024-12-01T14:45:00Z",
  "data": {
    "document_id": 123,
    "code": "PROC-001",
    "title": "Procedimento de Higienização",
    "version": "1.0",
    "status": "published",
    "approved_by": {
      "user_id": 2,
      "name": "Maria Santos",
      "email": "maria.santos@alphaclin.com"
    },
    "approval_date": "2024-12-01T14:45:00Z",
    "effective_date": "2024-12-01"
  }
}
```

#### Documento Assinado
```javascript
{
  "event": "document.signed",
  "timestamp": "2024-12-01T16:20:00Z",
  "data": {
    "document_id": 123,
    "code": "PROC-001",
    "title": "Procedimento de Higienização",
    "version": "1.0",
    "signed_by": {
      "user_id": 3,
      "name": "Carlos Oliveira",
      "email": "carlos.oliveira@alphaclin.com"
    },
    "signature_type": "qualified",
    "certificate_info": {
      "issuer": "Serasa Experian",
      "valid_until": "2024-12-31"
    }
  }
}
```

### Eventos de Auditorias

#### Auditoria Iniciada
```javascript
{
  "event": "audit.started",
  "timestamp": "2024-12-01T09:00:00Z",
  "data": {
    "audit_id": 456,
    "title": "Auditoria Interna Q4 2024",
    "type": "internal",
    "status": "in_progress",
    "auditors": [
      {
        "user_id": 4,
        "name": "Ana Costa",
        "email": "ana.costa@alphaclin.com"
      }
    ],
    "areas": ["Centro Cirúrgico", "Enfermagem"],
    "planned_end_date": "2024-12-05"
  }
}
```

#### Não Conformidade Identificada
```javascript
{
  "event": "audit.finding_identified",
  "timestamp": "2024-12-01T11:15:00Z",
  "data": {
    "audit_id": 456,
    "finding_id": 789,
    "title": "Procedimento Não Seguido",
    "classification": "major",
    "description": "Equipe não utiliza EPIs conforme procedimento",
    "process_affected": "Higienização de Equipamentos",
    "area": "Centro Cirúrgico",
    "auditor": {
      "user_id": 4,
      "name": "Ana Costa"
    },
    "deadline": "2024-12-15"
  }
}
```

#### Auditoria Concluída
```javascript
{
  "event": "audit.completed",
  "timestamp": "2024-12-05T17:00:00Z",
  "data": {
    "audit_id": 456,
    "title": "Auditoria Interna Q4 2024",
    "type": "internal",
    "status": "completed",
    "findings_summary": {
      "critical": 0,
      "major": 2,
      "minor": 5,
      "observations": 3
    },
    "overall_result": "Satisfatório",
    "report_url": "https://qms.alphaclin.com/audits/456/report"
  }
}
```

### Eventos de Não Conformidades

#### NC Criada
```javascript
{
  "event": "nc.created",
  "timestamp": "2024-12-01T10:30:00Z",
  "data": {
    "nc_id": 101,
    "number": "NC-2024-001",
    "title": "Procedimento de Higienização Não Seguido",
    "classification": "major",
    "description": "Durante auditoria, observou-se que técnicos não utilizam EPIs adequados",
    "reported_by": {
      "user_id": 4,
      "name": "Ana Costa"
    },
    "responsible": {
      "user_id": 5,
      "name": "Roberto Lima"
    },
    "deadline": "2024-12-15"
  }
}
```

#### NC Encerrada
```javascript
{
  "event": "nc.closed",
  "timestamp": "2024-12-10T14:20:00Z",
  "data": {
    "nc_id": 101,
    "number": "NC-2024-001",
    "title": "Procedimento de Higienização Não Seguido",
    "classification": "major",
    "closed_by": {
      "user_id": 5,
      "name": "Roberto Lima"
    },
    "resolution_time_days": 9,
    "effectiveness": "effective",
    "actions_taken": [
      "Treinamento realizado",
      "Procedimento atualizado",
      "Auditoria de acompanhamento agendada"
    ]
  }
}
```

### Eventos de Sistema

#### Usuário Conectado
```javascript
{
  "event": "user.login",
  "timestamp": "2024-12-01T08:30:00Z",
  "data": {
    "user_id": 1,
    "username": "joao.silva",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "location": "São Paulo, SP",
    "login_method": "password"
  }
}
```

#### Backup Realizado
```javascript
{
  "event": "system.backup_completed",
  "timestamp": "2024-12-01T02:00:00Z",
  "data": {
    "backup_id": "backup_20241201_020000",
    "type": "full",
    "size_mb": 1250,
    "duration_minutes": 15,
    "status": "success",
    "files_backed_up": [
      "database",
      "documents",
      "configurations",
      "audit_logs"
    ]
  }
}
```

## ⚙️ Configuração de Webhooks

### Criação de Webhook

#### Interface de Configuração
```html
<!-- Formulário de criação de webhook -->
<form class="webhook-form">
  <div class="form-section">
    <h3>Informações Básicas</h3>
    <div class="form-row">
      <div class="form-group">
        <label>Nome do Webhook:</label>
        <input type="text" name="name" placeholder="Ex: Sistema ERP" required>
      </div>
      <div class="form-group">
        <label>URL de Destino:</label>
        <input type="url" name="url" placeholder="https://exemplo.com/webhook" required>
      </div>
    </div>
    <div class="form-group">
      <label>Descrição:</label>
      <textarea name="description" rows="3" placeholder="Descreva o propósito deste webhook"></textarea>
    </div>
  </div>

  <div class="form-section">
    <h3>Eventos</h3>
    <div class="events-selection">
      <div class="event-category">
        <h4>Documentos</h4>
        <label class="checkbox-label">
          <input type="checkbox" name="events" value="document.created">
          <span>Documento Criado</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="events" value="document.approved">
          <span>Documento Aprovado</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="events" value="document.signed">
          <span>Documento Assinado</span>
        </label>
      </div>

      <div class="event-category">
        <h4>Auditorias</h4>
        <label class="checkbox-label">
          <input type="checkbox" name="events" value="audit.started">
          <span>Auditoria Iniciada</span>
        </label>
        <label class="checkbox-label">
          <input type="checkbox" name="events" value="audit.completed">
          <span>Auditoria Concluída</span>
        </label>
      </div>
    </div>
  </div>

  <div class="form-section">
    <h3>Configurações de Segurança</h3>
    <div class="form-row">
      <div class="form-group">
        <label>Token de Autenticação:</label>
        <input type="password" name="auth_token" placeholder="Token para validar requests">
      </div>
      <div class="form-group">
        <label>Secret:</label>
        <input type="password" name="secret" placeholder="Secret para assinatura">
      </div>
    </div>
  </div>

  <div class="form-section">
    <h3>Configurações Avançadas</h3>
    <div class="form-row">
      <div class="form-group">
        <label>Timeout (segundos):</label>
        <input type="number" name="timeout" value="30" min="5" max="60">
      </div>
      <div class="form-group">
        <label>Tentativas de Retry:</label>
        <input type="number" name="retry_attempts" value="3" min="0" max="5">
      </div>
    </div>
    <div class="form-group">
      <label>Filtros (JSON):</label>
      <textarea name="filters" rows="3" placeholder='{"departments": ["Centro Cirúrgico"], "document_types": ["procedure"]}'></textarea>
    </div>
  </div>

  <div class="form-actions">
    <button type="button" onclick="testWebhook()">Testar Webhook</button>
    <button type="submit">Salvar Webhook</button>
  </div>
</form>
```

### Configuração via API

#### Criar Webhook
```bash
# Criar webhook via API
POST /api/v1/webhooks
{
  "name": "Sistema ERP",
  "url": "https://erp.alphaclin.com/webhooks/qms",
  "events": [
    "document.created",
    "document.approved",
    "document.signed",
    "audit.completed",
    "nc.created",
    "nc.closed"
  ],
  "auth_token": "seu-token-aqui",
  "secret": "seu-secret-aqui",
  "timeout": 30,
  "retry_attempts": 3,
  "filters": {
    "departments": ["Centro Cirúrgico", "Enfermagem"],
    "document_categories": ["Procedimentos", "Políticas"]
  }
}
```

## 🔒 Segurança de Webhooks

### Validação de Requests

#### Assinatura HMAC
```javascript
const crypto = require('crypto');

// Verificação da assinatura
function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');

  return signature === `sha256=${expectedSignature}`;
}

// Exemplo de uso
app.post('/webhooks/qms', (req, res) => {
  const signature = req.headers['x-qms-signature'];
  const secret = process.env.QMS_WEBHOOK_SECRET;

  if (!verifyWebhookSignature(req.body, signature, secret)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // Processar webhook
  processWebhook(req.body);
  res.json({ status: 'received' });
});
```

### Rate Limiting

#### Controle de Taxa
```javascript
const rateLimit = {
  "per_minute": 60,
  "per_hour": 1000,
  "per_day": 10000,
  "by_ip": true,
  "by_webhook": true
};
```

## 📊 Monitoramento de Webhooks

### Dashboard de Webhooks

#### Status dos Webhooks
```html
<!-- Dashboard de monitoramento -->
<div class="webhooks-dashboard">
  <div class="webhooks-header">
    <h2>Monitoramento de Webhooks</h2>
    <div class="time-filter">
      <select id="time-range">
        <option value="1h">Última Hora</option>
        <option value="24h">Últimas 24h</option>
        <option value="7d">Últimos 7 dias</option>
      </select>
    </div>
  </div>

  <div class="webhooks-stats">
    <div class="stat-card">
      <h3>Total de Envios</h3>
      <span class="number">1,247</span>
      <span class="change up">+12%</span>
    </div>
    <div class="stat-card">
      <h3>Taxa de Sucesso</h3>
      <span class="number">96.8%</span>
      <span class="change up">+0.5%</span>
    </div>
    <div class="stat-card">
      <h3>Tempo Médio</h3>
      <span class="number">245ms</span>
      <span class="change down">-15ms</span>
    </div>
  </div>

  <div class="webhooks-list">
    <table>
      <thead>
        <tr>
          <th>Webhook</th>
          <th>URL</th>
          <th>Eventos</th>
          <th>Últimos Envios</th>
          <th>Taxa de Sucesso</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Sistema ERP</td>
          <td>https://erp.alphaclin.com/...</td>
          <td>6 eventos</td>
          <td>145</td>
          <td>98.2%</td>
          <td><span class="status healthy">Saudável</span></td>
        </tr>
        <tr>
          <td>Sistema de RH</td>
          <td>https://rh.alphaclin.com/...</td>
          <td>3 eventos</td>
          <td>67</td>
          <td>94.1%</td>
          <td><span class="status warning">Atenção</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

### Logs de Webhook

#### Estrutura de Log
```javascript
const webhookLog = {
  "log_id": "whl_abc123def456",
  "webhook_id": "wh_123456",
  "event": "document.approved",
  "timestamp": "2024-12-01T14:45:00Z",
  "request": {
    "url": "https://erp.alphaclin.com/webhooks/qms",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-QMS-Signature": "sha256=abc123...",
      "User-Agent": "AlphaClinic-QMS-Webhook/1.0"
    },
    "payload": {
      "event": "document.approved",
      "timestamp": "2024-12-01T14:45:00Z",
      "data": { /* dados do evento */ }
    }
  },
  "response": {
    "status_code": 200,
    "headers": {
      "Content-Type": "application/json"
    },
    "body": "{\"status\": \"received\"}",
    "response_time_ms": 245
  },
  "result": "success"
};
```

## 🔧 APIs de Gerenciamento

### Endpoints de Webhooks

#### CRUD de Webhooks
```bash
# Listar webhooks
GET /api/v1/webhooks

# Criar webhook
POST /api/v1/webhooks

# Atualizar webhook
PATCH /api/v1/webhooks/{webhook_id}

# Excluir webhook
DELETE /api/v1/webhooks/{webhook_id}

# Testar webhook
POST /api/v1/webhooks/{webhook_id}/test
```

#### Monitoramento
```bash
# Obter estatísticas de webhook
GET /api/v1/webhooks/{webhook_id}/stats?period=7d

# Resposta
{
  "webhook_id": "wh_123456",
  "period": "2024-11-24 to 2024-12-01",
  "total_requests": 145,
  "successful_requests": 142,
  "failed_requests": 3,
  "success_rate": 97.9,
  "average_response_time_ms": 245,
  "events_breakdown": {
    "document.created": 45,
    "document.approved": 38,
    "document.signed": 32,
    "audit.completed": 18,
    "nc.created": 8,
    "nc.closed": 4
  }
}
```

#### Logs de Webhook
```bash
# Obter logs de webhook
GET /api/v1/webhooks/{webhook_id}/logs?limit=50&status=failed

# Resposta
{
  "webhook_id": "wh_123456",
  "logs": [
    {
      "log_id": "whl_abc123def456",
      "timestamp": "2024-12-01T14:45:00Z",
      "event": "document.approved",
      "status_code": 200,
      "response_time_ms": 245,
      "error_message": null
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 145
  }
}
```

## 🚨 Tratamento de Falhas

### Estratégias de Retry

#### Configuração de Retry
```javascript
const retryConfig = {
  "exponential_backoff": {
    "enabled": true,
    "initial_delay_seconds": 1,
    "max_delay_seconds": 300,
    "multiplier": 2,
    "max_attempts": 5
  },
  "immediate_retry": {
    "enabled": true,
    "max_attempts": 3,
    "delay_seconds": 0
  }
};
```

### Dead Letter Queue

#### Configuração de DLQ
```javascript
const dlqConfig = {
  "enabled": true,
  "provider": "redis",
  "key_prefix": "qms:webhook:dlq",
  "retention_days": 30,
  "max_size": 10000,
  "alert_threshold": 100
};
```

## 📞 Exemplos de Integração

### Exemplo 1: Integração com ERP

#### Webhook para ERP
```javascript
// Endpoint do ERP para receber webhooks
app.post('/webhooks/qms', async (req, res) => {
  try {
    // Verificar assinatura
    const signature = req.headers['x-qms-signature'];
    if (!verifySignature(req.body, signature)) {
      return res.status(401).json({ error: 'Invalid signature' });
    }

    const { event, data } = req.body;

    switch (event) {
      case 'document.approved':
        await handleDocumentApproved(data);
        break;
      case 'document.signed':
        await handleDocumentSigned(data);
        break;
      default:
        console.log('Evento não tratado:', event);
    }

    res.json({ status: 'processed' });
  } catch (error) {
    console.error('Erro ao processar webhook:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

async function handleDocumentApproved(data) {
  // Atualizar status no ERP
  await erpApi.updateDocumentStatus(data.document_id, 'approved');

  // Notificar usuários relevantes
  await notifyRelevantUsers(data);
}
```

### Exemplo 2: Integração com Slack

#### Notificações no Slack
```javascript
const slackWebhook = {
  "url": "https://your-notification-service.com/webhooks/qms",
  "events": ["nc.created", "audit.completed"],
  "template": {
    "nc.created": {
      "text": "🚨 Nova NC Criada",
      "blocks": [
        {
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": "🚨 Nova Não Conformidade"
          }
        },
        {
          "type": "section",
          "fields": [
            {
              "type": "mrkdwn",
              "text": `*Título:* ${data.title}`
            },
            {
              "type": "mrkdwn",
              "text": `*Classificação:* ${data.classification}`
            },
            {
              "type": "mrkdwn",
              "text": `*Responsável:* ${data.responsible.name}`
            },
            {
              "type": "mrkdwn",
              "text": `*Prazo:* ${formatDate(data.deadline)}`
            }
          ]
        },
        {
          "type": "actions",
          "elements": [
            {
              "type": "button",
              "text": {
                "type": "plain_text",
                "text": "Ver NC"
              },
              "url": `${qmsUrl}/ncs/${data.nc_id}`
            }
          ]
        }
      ]
    }
  }
};
```

## 🎯 Melhores Práticas

### Para Implementação
- ✅ Use HTTPS sempre
- ✅ Implemente validação de assinatura
- ✅ Configure timeouts apropriados
- ✅ Trate falhas adequadamente
- ✅ Monitore performance

### Para Segurança
- ✅ Mantenha secrets seguros
- ✅ Use rate limiting
- ✅ Valide origem dos requests
- ✅ Implemente logs de auditoria
- ✅ Revise configurações regularmente

### Para Manutenção
- ✅ Monitore taxas de sucesso
- ✅ Configure alertas para falhas
- ✅ Teste webhooks regularmente
- ✅ Documente integrações
- ✅ Mantenha documentação atualizada

## 📞 Suporte e Troubleshooting

### Problemas Comuns

#### Webhook Não Funcionando
```bash
# Testar webhook
flask test-webhook --webhook-id 123 --event "document.created"

# Verificar logs
flask check-webhook-logs --webhook-id 123 --last-hours 24

# Diagnosticar problemas
flask diagnose-webhook-issues --webhook-id 123
```

#### Alta Latência
```bash
# Analisar performance
flask analyze-webhook-performance --webhook-id 123 --period "7d"

# Otimizar configurações
flask optimize-webhook-config --webhook-id 123 --strategy "async_processing"
```

#### Muitas Falhas
```bash
# Identificar padrões de falha
flask analyze-webhook-failures --webhook-id 123 --pattern-analysis

# Plano de correção
flask create-webhook-fix-plan --webhook-id 123 --based-on-analysis
```

---

**Última atualização:** Dezembro 2024
**Versão:** 1.0.0