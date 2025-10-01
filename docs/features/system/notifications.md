# 🔔 Sistema de Notificações - AlphaClinic QMS

## Visão Geral

O sistema de notificações do AlphaClinic QMS oferece comunicação eficaz e oportuna entre usuários, processos e sistemas, garantindo que informações críticas sejam entregues no momento certo através dos canais apropriados.

## 📢 Tipos de Notificação

### Notificações por Categoria

#### 1. Notificações de Sistema
```javascript
const systemNotifications = {
  "maintenance": {
    "title": "Manutenção Programada",
    "description": "Sistema indisponível para manutenção",
    "urgency": "high",
    "channels": ["email", "dashboard", "sms"],
    "schedule": "2024-12-15T02:00:00Z",
    "duration": "2 horas"
  },
  "security": {
    "title": "Alerta de Segurança",
    "description": "Tentativa de acesso não autorizado detectada",
    "urgency": "critical",
    "channels": ["email", "sms", "phone"],
    "immediate": true
  },
  "backup": {
    "title": "Backup Concluído",
    "description": "Backup automático realizado com sucesso",
    "urgency": "low",
    "channels": ["email"],
    "frequency": "daily"
  }
};
```

#### 2. Notificações de Processo
```javascript
const processNotifications = {
  "document_approval": {
    "title": "Documento Aguardando Aprovação",
    "description": "Documento '{title}' requer sua aprovação",
    "urgency": "medium",
    "channels": ["email", "dashboard"],
    "triggers": ["document_submitted", "document_reviewed"]
  },
  "audit_scheduled": {
    "title": "Auditoria Agendada",
    "description": "Auditoria '{title}' agendada para {date}",
    "urgency": "medium",
    "channels": ["email", "dashboard", "calendar"],
    "triggers": ["audit_scheduled", "audit_rescheduled"]
  },
  "nc_assigned": {
    "title": "Não Conformidade Atribuída",
    "description": "NC '{title}' foi atribuída a você",
    "urgency": "high",
    "channels": ["email", "dashboard", "mobile"],
    "triggers": ["nc_created", "nc_assigned"]
  }
};
```

#### 3. Notificações de Equipe
```javascript
const teamNotifications = {
  "team_mention": {
    "title": "Você foi Mencionado",
    "description": "{user} mencionou você em {context}",
    "urgency": "medium",
    "channels": ["dashboard", "email"],
    "triggers": ["mention_in_comment", "mention_in_document"]
  },
  "team_update": {
    "title": "Atualização de Equipe",
    "description": "Nova atualização em {team_name}",
    "urgency": "low",
    "channels": ["dashboard", "email"],
    "triggers": ["team_member_added", "team_goal_updated"]
  }
};
```

## 📱 Canais de Notificação

### 1. Dashboard (Interface Web)

#### Notificações no Dashboard
```html
<!-- Centro de notificações -->
<div class="notification-center">
  <div class="notification-header">
    <h3>Notificações</h3>
    <div class="notification-controls">
      <button onclick="markAllRead()">Marcar Todas como Lidas</button>
      <button onclick="notificationSettings()">Configurações</button>
    </div>
  </div>

  <div class="notification-filters">
    <button class="filter-btn active" data-filter="all">Todas</button>
    <button class="filter-btn" data-filter="unread">Não Lidas</button>
    <button class="filter-btn" data-filter="urgent">Urgentes</button>
  </div>

  <div class="notifications-list">
    <div class="notification-item unread urgent">
      <div class="notification-icon">
        <span class="icon">🚨</span>
      </div>
      <div class="notification-content">
        <div class="notification-title">Documento Requer Aprovação</div>
        <div class="notification-message">Procedimento de Higienização v2.0 aguarda aprovação</div>
        <div class="notification-time">2 minutos atrás</div>
      </div>
      <div class="notification-actions">
        <button onclick="viewDocument()">Ver Documento</button>
        <button onclick="approveDocument()">Aprovar</button>
      </div>
    </div>

    <div class="notification-item">
      <div class="notification-icon">
        <span class="icon">📋</span>
      </div>
      <div class="notification-content">
        <div class="notification-title">Auditoria Agendada</div>
        <div class="notification-message">Auditoria Interna Q4 2024 agendada para 15/12</div>
        <div class="notification-time">1 hora atrás</div>
      </div>
      <div class="notification-actions">
        <button onclick="viewAudit()">Ver Auditoria</button>
      </div>
    </div>
  </div>
</div>
```

### 2. Email

#### Templates de Email
```javascript
const emailTemplates = {
  "document_approval": {
    "subject": "Documento '{title}' requer sua aprovação",
    "template": `
      <h2>Documento Requer Aprovação</h2>
      <p>Olá {user_name},</p>
      <p>O documento <strong>{title}</strong> foi submetido e requer sua aprovação.</p>
      <div class="document-info">
        <p><strong>Código:</strong> {code}</p>
        <p><strong>Versão:</strong> {version}</p>
        <p><strong>Prazo:</strong> {deadline}</p>
      </div>
      <div class="action-buttons">
        <a href="{approval_url}" class="btn primary">Revisar e Aprovar</a>
        <a href="{document_url}" class="btn secondary">Ver Documento</a>
      </div>
      <p>Atenciosamente,<br>Equipe AlphaClinic QMS</p>
    `,
    "attachments": ["document.pdf"]
  },
  "system_maintenance": {
    "subject": "Manutenção Programada - {date}",
    "template": `
      <h2>Manutenção Programada</h2>
      <p>Informamos que o sistema estará indisponível para manutenção.</p>
      <div class="maintenance-info">
        <p><strong>Data:</strong> {date}</p>
        <p><strong>Horário:</strong> {time}</p>
        <p><strong>Duração:</strong> {duration}</p>
        <p><strong>Motivo:</strong> {reason}</p>
      </div>
      <p>Duração prevista: {duration}</p>
      <p>Atenciosamente,<br>Equipe de TI</p>
    `
  }
};
```

### 3. Mobile Push

#### Notificações Push
```javascript
const pushNotifications = {
  "urgent_nc": {
    "title": "NC Crítica Atribuída",
    "body": "Não conformidade crítica requer ação imediata",
    "icon": "warning",
    "badge": 1,
    "sound": "urgent_notification.mp3",
    "actions": [
      {"title": "Ver NC", "action": "view_nc"},
      {"title": "Adiar", "action": "snooze"}
    ]
  },
  "document_signed": {
    "title": "Documento Assinado",
    "body": "Documento {title} foi assinado por {signer}",
    "icon": "document",
    "badge": 1,
    "sound": "notification.mp3"
  }
};
```

### 4. SMS

#### Mensagens SMS
```javascript
const smsTemplates = {
  "urgent_notification": {
    "template": "URGENTE: {title}. {message}. Acesse: {short_url}",
    "max_length": 160,
    "priority": "high"
  },
  "appointment_reminder": {
    "template": "Lembrete: {event} em {time}. Local: {location}",
    "max_length": 160,
    "priority": "normal"
  }
};
```

## ⚙️ Configurações de Notificação

### Preferências do Usuário

#### Configurações Individuais
```javascript
const userNotificationPreferences = {
  "user_id": 123,
  "global_settings": {
    "email_enabled": true,
    "push_enabled": true,
    "sms_enabled": false,
    "dashboard_enabled": true,
    "quiet_hours": {
      "start": "22:00",
      "end": "07:00",
      "timezone": "America/Sao_Paulo"
    }
  },
  "category_settings": {
    "document_approval": {
      "email": true,
      "push": true,
      "sms": false,
      "frequency": "immediate"
    },
    "system_maintenance": {
      "email": true,
      "push": false,
      "sms": false,
      "frequency": "advance"
    },
    "team_updates": {
      "email": true,
      "push": false,
      "sms": false,
      "frequency": "daily_digest"
    }
  }
};
```

### Configurações Administrativas

#### Políticas de Notificação
```javascript
const notificationPolicies = {
  "frequency_limits": {
    "email_per_hour": 10,
    "sms_per_day": 5,
    "push_per_hour": 20
  },
  "urgency_mapping": {
    "critical": {
      "channels": ["email", "sms", "push", "phone"],
      "escalation_time": "immediate",
      "require_acknowledgment": true
    },
    "high": {
      "channels": ["email", "push"],
      "escalation_time": "15 minutes",
      "require_acknowledgment": true
    },
    "medium": {
      "channels": ["email", "dashboard"],
      "escalation_time": "1 hour",
      "require_acknowledgment": false
    },
    "low": {
      "channels": ["dashboard"],
      "escalation_time": "24 hours",
      "require_acknowledgment": false
    }
  }
};
```

## 📊 Relatórios de Notificação

### Métricas de Entrega

#### Relatório de Entregas
```bash
# Relatório de entregas por período
GET /api/v1/reports/notification-delivery?period=2024-12

# Resposta
{
  "period": "2024-12-01 to 2024-12-31",
  "summary": {
    "total_sent": 15420,
    "delivered": 14895,
    "failed": 525,
    "delivery_rate": "96.6%"
  },
  "by_channel": {
    "email": {
      "sent": 8500,
      "delivered": 8200,
      "failed": 300,
      "delivery_rate": "96.5%"
    },
    "push": {
      "sent": 4500,
      "delivered": 4350,
      "failed": 150,
      "delivery_rate": "96.7%"
    },
    "sms": {
      "sent": 2420,
      "delivered": 2345,
      "failed": 75,
      "delivery_rate": "96.9%"
    }
  },
  "by_urgency": {
    "critical": {"sent": 150, "delivered": 148, "delivery_rate": "98.7%"},
    "high": {"sent": 1200, "delivered": 1150, "delivery_rate": "95.8%"},
    "medium": {"sent": 8500, "delivered": 8200, "delivery_rate": "96.5%"},
    "low": {"sent": 5570, "delivered": 5397, "delivery_rate": "96.9%"}
  }
}
```

### Análise de Engajamento

#### Métricas de Engajamento
```javascript
const engagementMetrics = {
  "open_rates": {
    "email": "45.2%",
    "push": "78.5%",
    "dashboard": "92.1%"
  },
  "click_rates": {
    "email": "12.3%",
    "push": "25.7%"
  },
  "response_times": {
    "critical_notifications": "8.5 minutes",
    "high_notifications": "45.2 minutes",
    "medium_notifications": "2.1 hours"
  }
};
```

## 🔧 APIs de Notificação

### Endpoints Principais

#### Envio de Notificações
```bash
# Enviar notificação
POST /api/v1/notifications/send
{
  "recipients": [
    {"user_id": 123, "email": "joao.silva@alphaclin.com"},
    {"user_id": 124, "email": "maria.santos@alphaclin.com"}
  ],
  "template": "document_approval",
  "urgency": "high",
  "channels": ["email", "push"],
  "data": {
    "title": "Procedimento de Higienização",
    "code": "PROC-001",
    "version": "2.0",
    "deadline": "2024-12-15",
    "approval_url": "https://qms.alphaclin.com/documents/123/approve"
  }
}

# Enviar notificação para equipe
POST /api/v1/notifications/send-to-team
{
  "team_id": 1,
  "template": "team_update",
  "urgency": "medium",
  "channels": ["email", "dashboard"],
  "data": {
    "team_name": "Centro Cirúrgico",
    "update_type": "new_member",
    "member_name": "Ana Costa"
  }
}
```

#### Gerenciamento de Templates
```bash
# Criar template personalizado
POST /api/v1/notifications/templates
{
  "name": "custom_audit_reminder",
  "description": "Lembrete personalizado de auditoria",
  "subject": "Auditoria {audit_name} - {days_until} dias",
  "channels": ["email", "push"],
  "variables": ["audit_name", "days_until", "auditor", "location"],
  "content": {
    "email": "Template HTML do email...",
    "push": "Texto da notificação push...",
    "sms": "Texto SMS (se aplicável)..."
  }
}
```

#### Configurações de Usuário
```bash
# Atualizar preferências de notificação
PATCH /api/v1/users/{user_id}/notification-preferences
{
  "global_settings": {
    "email_enabled": true,
    "push_enabled": true,
    "quiet_hours": {
      "enabled": true,
      "start": "22:00",
      "end": "07:00"
    }
  },
  "category_settings": {
    "document_approval": {
      "email": true,
      "push": true,
      "frequency": "immediate"
    }
  }
}
```

## 🎯 Melhores Práticas

### Para Configuração de Notificações
- ✅ Defina canais apropriados para cada tipo de notificação
- ✅ Configure horários adequados (respeite quiet hours)
- ✅ Use urgência apropriada para cada situação
- ✅ Evite excesso de notificações (notification fatigue)
- ✅ Permita customização por usuário

### Para Templates
- ✅ Mantenha templates claros e objetivos
- ✅ Use variáveis para personalização
- ✅ Inclua ações claras (call-to-action)
- ✅ Teste templates antes de usar em produção
- ✅ Mantenha consistência visual

### Para Administração
- ✅ Monitore taxas de entrega e engajamento
- ✅ Ajuste configurações baseado em métricas
- ✅ Mantenha lista de usuários atualizada
- ✅ Gerencie limites de envio por canal
- ✅ Faça backup de configurações

## 🚨 Sistema de Escalonamento

### Escalonamento Automático

#### Regras de Escalonamento
```javascript
const escalationRules = {
  "document_approval": {
    "initial_recipient": "document_approver",
    "escalation_path": [
      {
        "after_minutes": 60,
        "escalate_to": "department_manager",
        "notification": "Documento ainda não aprovado"
      },
      {
        "after_minutes": 1440, // 24 horas
        "escalate_to": "quality_director",
        "notification": "Documento crítico não aprovado"
      }
    ]
  },
  "critical_nc": {
    "initial_recipient": "nc_responsible",
    "escalation_path": [
      {
        "after_hours": 4,
        "escalate_to": "department_manager",
        "notification": "NC crítica não tratada"
      },
      {
        "after_hours": 24,
        "escalate_to": "quality_director",
        "notification": "NC crítica requer atenção imediata"
      }
    ]
  }
};
```

### Processo de Escalonamento

#### Fluxo de Escalonamento
```mermaid
graph TD
    A[Notificação Enviada] --> B{Tempo Expirou?}
    B -->|Não| C[Aguardar]
    B -->|Sim| D[Próximo Nível]
    D --> E[Enviar Notificação]
    E --> F{Último Nível?}
    F -->|Não| B
    F -->|Sim| G[Alerta Administração]
    G --> H[Registrar Incidente]
```

## 📞 Integrações Externas

### Provedores de Email

#### Configuração de SMTP
```bash
# Configurações SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=notificacoes@alphaclin.com
SMTP_PASSWORD=sua-senha-de-app
SMTP_USE_TLS=true

# Configurações avançadas
SMTP_MAX_EMAILS_PER_DAY=1000
SMTP_RETRY_ATTEMPTS=3
SMTP_RETRY_DELAY=60
```

### Serviços de SMS

#### Provedores Suportados
```javascript
const smsProviders = {
  "twilio": {
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "your_auth_token",
    "from_number": "+1234567890",
    "features": ["delivery_reports", "two_way_sms"]
  },
  "aws_sns": {
    "region": "us-east-1",
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "features": ["delivery_reports", "multiple_regions"]
  }
};
```

### Push Notifications

#### Configuração de Push
```javascript
const pushConfig = {
  "firebase": {
    "server_key": "your-server-key",
    "project_id": "your-project-id",
    "features": ["web_push", "mobile_push", "rich_notifications"]
  },
  "apns": {
    "key_id": "your-key-id",
    "team_id": "your-team-id",
    "bundle_id": "com.alphaclin.qms",
    "features": ["ios_push", "safari_push"]
  }
};
```

## 📞 Suporte e Troubleshooting

### Problemas Comuns

#### Notificações Não Entregues
```bash
# Verificar status de entrega
flask check-notification-delivery --notification-id 123

# Diagnosticar problemas
flask diagnose-notification-issues --user-id 456 --channel email

# Corrigir problemas comuns
flask fix-notification-delivery --provider gmail --issue "authentication"
```

#### Configurações Incorretas
```bash
# Validar configurações
flask validate-notification-settings --user-id 123

# Corrigir preferências
flask fix-notification-preferences --user-id 123 --reset-to-defaults
```

#### Performance Lenta
```bash
# Otimizar sistema de notificações
flask optimize-notification-system --strategy "caching,batching"

# Limpar fila de notificações
flask cleanup-notification-queue --older-than-days 7
```

---

**Última atualização:** Dezembro 2024
**Versão:** 1.0.0