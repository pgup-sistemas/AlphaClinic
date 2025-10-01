# ⚠️ Gestão de Não Conformidades - AlphaClinic QMS

## Visão Geral

O sistema de gestão de não conformidades (NCs) do AlphaClinic QMS oferece controle completo do ciclo de vida das não conformidades, desde a identificação até o encerramento, garantindo tratamento adequado e prevenção de recorrências.

## 🚨 Identificação de Não Conformidades

### Fontes de Identificação

#### Durante Auditorias
- 🔍 **Auditorias internas**: Achados identificados por auditores
- 📋 **Auditorias externas**: Não conformidades apontadas por certificadoras
- 👥 **Auditorias de cliente**: NCs identificadas por clientes/parceiros

#### Operação Diária
- 👤 **Relatos de funcionários**: Comunicação de problemas observados
- 📊 **Indicadores**: Desvios em métricas de qualidade
- 👥 **Reclamações de clientes**: Problemas reportados por pacientes/clientes
- 🔧 **Manutenção**: Problemas identificados em equipamentos/processos

#### Monitoramento Contínuo
- 📈 **Indicadores de processo**: KPIs fora do padrão
- 🧪 **Controles de qualidade**: Testes e verificações
- 📋 **Checklists**: Verificações rotineiras
- 🔄 **Feedback de processos**: Melhorias identificadas

### Critérios de Classificação

#### Gravidade da Não Conformidade
```javascript
const ncClassification = {
  "critical": {
    "definition": "Afeta segurança do paciente ou conformidade legal",
    "examples": [
      "Erro de medicação",
      "Infecção hospitalar",
      "Violação de privacidade de dados",
      "Não conformidade com legislação sanitária"
    ],
    "deadline_hours": 24,
    "requires_immediate_action": true,
    "notification_levels": ["supervisor", "manager", "director", "quality_director"]
  },
  "major": {
    "definition": "Afeta sistema de gestão ou resultados",
    "examples": [
      "Procedimento não seguido",
      "Registro inadequado",
      "Treinamento não realizado",
      "Equipamento com manutenção atrasada"
    ],
    "deadline_days": 7,
    "requires_immediate_action": true,
    "notification_levels": ["supervisor", "manager", "quality_team"]
  },
  "minor": {
    "definition": "Não afeta significativamente o sistema",
    "examples": [
      "Erro de digitação em documento",
      "Formatação inconsistente",
      "Atualização de referência desatualizada"
    ],
    "deadline_days": 15,
    "requires_immediate_action": false,
    "notification_levels": ["supervisor", "quality_team"]
  }
};
```

## 📝 Registro de Não Conformidades

### Formulário de Registro

#### Campos Essenciais
```javascript
const ncRecord = {
  "nc_number": "NC-2024-001",
  "title": "Procedimento de Higienização Não Seguido",
  "description": "Durante auditoria, observou-se que técnicos não utilizam EPIs adequados conforme procedimento documentado",
  "classification": "major",
  "source": "internal_audit",
  "source_id": "AUD-2024-001",
  "process_affected": "Higienização de Equipamentos",
  "area_responsible": "Centro Cirúrgico",
  "immediate_action_taken": "Treinamento imediato da equipe",
  "reported_by": {
    "user_id": 1,
    "name": "João Silva",
    "role": "Auditor Interno",
    "contact": "joao.silva@alphaclin.com"
  },
  "reported_at": "2024-12-01T10:30:00Z",
  "deadline": "2024-12-08T17:00:00Z"
};
```

### Evidências de Apoio

#### Tipos de Evidência
- 📷 **Fotografias**: Registro visual do problema
- 📄 **Documentos**: Registros relacionados
- 📊 **Dados**: Indicadores relevantes
- 👥 **Testemunhos**: Declarações de envolvidos
- 🔧 **Amostras**: Quando aplicável

## 🔍 Análise de Causa Raiz

### Metodologia de Análise

#### Técnica dos 5 Porquês
```javascript
const fiveWhys = {
  "problem": "Técnicos não utilizam EPIs adequados",
  "why1": "Por que? Não conhecem o procedimento correto",
  "why2": "Por que? Treinamento não foi realizado",
  "why3": "Por que? Instrutor não estava disponível",
  "why4": "Por que? Falta de planejamento de treinamento",
  "why5": "Por que? Sistema de gestão de treinamento inadequado",
  "root_cause": "Sistema de gestão de treinamento inadequado"
};
```

#### Diagrama de Ishikawa (Espinha de Peixe)
```javascript
const ishikawa = {
  "effect": "Não conformidade em higienização",
  "causes": {
    "people": [
      "Falta de treinamento",
      "Falta de supervisão",
      "Rotatividade alta"
    ],
    "process": [
      "Procedimento inadequado",
      "Falta de checklist",
      "Controle insuficiente"
    ],
    "equipment": [
      "EPIs inadequados",
      "Equipamentos quebrados",
      "Falta de manutenção"
    ],
    "materials": [
      "EPIs não disponíveis",
      "Produtos de limpeza inadequados"
    ],
    "environment": [
      "Espaço físico inadequado",
      "Iluminação insuficiente"
    ],
    "management": [
      "Falta de liderança",
      "Objetivos não claros",
      "Recursos insuficientes"
    ]
  }
};
```

## 🛠️ Plano de Ação Corretiva

### Estrutura do Plano de Ação

#### Ações Imediatas
```javascript
const immediateActions = [
  {
    "action": "Treinamento imediato da equipe",
    "responsible": "Enfermeiro Chefe",
    "deadline": "2024-12-01T17:00:00Z",
    "resources": ["Material de treinamento", "Sala disponível"],
    "verification": "Lista de presença assinada"
  },
  {
    "action": "Verificação de disponibilidade de EPIs",
    "responsible": "Técnico de Enfermagem",
    "deadline": "2024-12-01T16:00:00Z",
    "resources": ["Estoque de EPIs"],
    "verification": "Relatório de estoque"
  }
];
```

#### Ações Corretivas
```javascript
const correctiveActions = [
  {
    "action": "Implementar sistema de treinamento online",
    "responsible": "Gerente de RH",
    "deadline": "2024-12-15T17:00:00Z",
    "resources": ["Plataforma EAD", "Conteúdo desenvolvido"],
    "verification": "Sistema implementado e funcionando"
  },
  {
    "action": "Revisar procedimento de higienização",
    "responsible": "Comissão de Controle de Infecção",
    "deadline": "2024-12-20T17:00:00Z",
    "resources": ["Tempo da comissão", "Dados de auditoria"],
    "verification": "Procedimento atualizado e aprovado"
  }
];
```

#### Ações Preventivas
```javascript
const preventiveActions = [
  {
    "action": "Auditoria mensal de processos críticos",
    "responsible": "Equipe da Qualidade",
    "deadline": "2024-12-31T17:00:00Z",
    "resources": ["Cronograma de auditorias", "Checklists"],
    "verification": "Relatórios mensais de auditoria"
  },
  {
    "action": "Indicadores de monitoramento de EPIs",
    "responsible": "Supervisor de Enfermagem",
    "deadline": "2024-12-10T17:00:00Z",
    "resources": ["Sistema de indicadores"],
    "verification": "Dashboard de monitoramento"
  }
];
```

## 🔄 Implementação e Acompanhamento

### Processo de Implementação

#### Responsabilidades
- 👤 **Responsável pela NC**: Implementar ações designadas
- 👥 **Equipe da Qualidade**: Acompanhar progresso
- 👨‍💼 **Gestor Responsável**: Fornecer recursos necessários
- 📋 **Auditor**: Verificar eficácia quando aplicável

#### Ferramentas de Acompanhamento
```javascript
const trackingTools = {
  "kanban_board": {
    "columns": ["To Do", "In Progress", "Review", "Verification", "Done"],
    "cards": "Cada ação como um card",
    "assignments": "Responsáveis designados",
    "deadlines": "Prazos visíveis",
    "progress": "Status atualizado"
  },
  "notifications": {
    "email": "Notificações automáticas",
    "dashboard": "Alertas no painel",
    "reports": "Relatórios de progresso"
  }
};
```

## ✅ Verificação de Eficácia

### Processo de Verificação

#### Critérios de Eficácia
```javascript
const effectivenessCriteria = {
  "problem_solved": "Não conformidade não recorrente",
  "process_improved": "Indicadores melhorados",
  "people_trained": "Equipe capacitada",
  "systems_updated": "Controles implementados",
  "documentation": "Registros adequados"
};
```

#### Métodos de Verificação
- 📊 **Indicadores**: Monitoramento de KPIs relacionados
- 🔍 **Auditoria de seguimento**: Verificação específica da NC
- 👥 **Feedback**: Consulta aos envolvidos
- 📋 **Observação**: Verificação in loco
- 📄 **Documentos**: Análise de registros

### Encerramento da NC

#### Condições para Encerramento
- ✅ **Ações implementadas**: Todas as ações concluídas
- ✅ **Eficácia verificada**: Problema resolvido
- ✅ **Documentação completa**: Registros adequados
- ✅ **Lições aprendidas**: Análise de melhorias
- ✅ **Prevenção garantida**: Medidas para evitar recorrência

## 📊 Relatórios e Análises

### Relatórios de Não Conformidades

#### Relatório Mensal de NCs
```bash
# Relatório consolidado
GET /api/v1/reports/ncs/monthly?year=2024&month=12

# Resposta
{
  "total_ncs": 25,
  "by_classification": {
    "critical": 2,
    "major": 8,
    "minor": 15
  },
  "by_process": {
    "higienizacao": 8,
    "medicacao": 6,
    "registros": 11
  },
  "average_resolution_time": "12 dias",
  "recurrence_rate": "8%",
  "effectiveness_rate": "94%"
}
```

#### Análise de Tendências
```javascript
const trendAnalysis = {
  "period": "Últimos 12 meses",
  "total_ncs": 180,
  "trend": "decreasing",
  "change_percentage": "-15%",
  "top_processes": [
    "Higienização": 45,
    "Medicação": 38,
    "Registros": 32
  ],
  "improvement_opportunities": [
    "Treinamento adicional em higienização",
    "Revisão de processos de medicação",
    "Sistematização de registros"
  ]
};
```

## 📱 Interface do Usuário

### Dashboard de Não Conformidades

#### Visão Geral
```html
<!-- Dashboard principal -->
<div class="ncs-dashboard">
  <div class="kpi-cards">
    <div class="kpi-card critical">
      <h3>NCs Críticas</h3>
      <span class="number">2</span>
      <span class="deadline">Vencem hoje</span>
    </div>
    <div class="kpi-card major">
      <h3>NCs Majors</h3>
      <span class="number">8</span>
      <span class="deadline">5 vencem esta semana</span>
    </div>
    <div class="kpi-card trend">
      <h3>Tendência</h3>
      <span class="number">-15%</span>
      <span class="description">vs mês anterior</span>
    </div>
  </div>

  <div class="charts-section">
    <div class="chart-container">
      <!-- Gráfico de NCs por processo -->
    </div>
    <div class="chart-container">
      <!-- Gráfico de tempo de resolução -->
    </div>
  </div>

  <div class="recent-ncs">
    <!-- Lista de NCs recentes -->
  </div>
</div>
```

### Formulário de NC

#### Captura de Nova NC
```html
<!-- Formulário de registro -->
<form class="nc-registration-form">
  <div class="form-section">
    <label>Título da NC:</label>
    <input type="text" name="title" required>
  </div>

  <div class="form-section">
    <label>Descrição Detalhada:</label>
    <textarea name="description" rows="4" required></textarea>
  </div>

  <div class="form-section">
    <label>Classificação:</label>
    <select name="classification" required>
      <option value="critical">Crítica</option>
      <option value="major">Major</option>
      <option value="minor">Menor</option>
    </select>
  </div>

  <div class="form-section">
    <label>Processo Afetado:</label>
    <select name="process" required>
      <option value="higienizacao">Higienização</option>
      <option value="medicacao">Medicação</option>
      <option value="registros">Registros</option>
    </select>
  </div>

  <div class="form-section">
    <label>Evidências:</label>
    <div class="file-upload">
      <input type="file" multiple accept="image/*,.pdf,.doc,.docx">
      <div class="upload-preview"></div>
    </div>
  </div>

  <div class="form-actions">
    <button type="button" onclick="saveDraft()">Salvar Rascunho</button>
    <button type="submit">Registrar NC</button>
  </div>
</form>
```

## 🔧 APIs de Não Conformidades

### Endpoints Principais

#### Gerenciamento de NCs
```bash
# Criar nova NC
POST /api/v1/non-conformities
{
  "title": "Procedimento de Higienização Não Seguido",
  "description": "Durante auditoria...",
  "classification": "major",
  "process_affected": "Higienização de Equipamentos",
  "immediate_action": "Treinamento imediato",
  "evidence_files": ["evidencia1.jpg", "evidencia2.pdf"]
}

# Listar NCs
GET /api/v1/non-conformities?status=open&classification=major

# Obter NC específica
GET /api/v1/non-conformities/{id}
```

#### Análise de Causa Raiz
```bash
# Registrar análise de causa raiz
POST /api/v1/non-conformities/{id}/root-cause-analysis
{
  "method": "5_whys",
  "analysis": {
    "problem": "Técnicos não utilizam EPIs",
    "whys": ["Não conhecem procedimento", "Treinamento não realizado"],
    "root_cause": "Sistema de treinamento inadequado"
  },
  "analyst": "Maria Santos"
}
```

#### Plano de Ação
```bash
# Registrar plano de ação
POST /api/v1/non-conformities/{id}/action-plan
{
  "immediate_actions": [
    {
      "description": "Treinamento imediato",
      "responsible": "Enfermeiro Chefe",
      "deadline": "2024-12-01T17:00:00Z"
    }
  ],
  "corrective_actions": [
    {
      "description": "Implementar sistema EAD",
      "responsible": "Gerente de RH",
      "deadline": "2024-12-15T17:00:00Z"
    }
  ],
  "preventive_actions": [
    {
      "description": "Auditorias mensais",
      "responsible": "Qualidade",
      "deadline": "2024-12-31T17:00:00Z"
    }
  ]
}
```

## 🎯 Melhores Práticas

### Para Identificação de NCs
- ✅ Registre NCs assim que identificadas
- ✅ Seja específico na descrição
- ✅ Colete evidências adequadas
- ✅ Classifique corretamente a gravidade
- ✅ Notifique responsáveis imediatamente

### Para Tratamento de NCs
- ✅ Analise causas raiz adequadamente
- ✅ Implemente ações corretivas efetivas
- ✅ Estabeleça ações preventivas
- ✅ Monitore implementação e eficácia
- ✅ Documente todo o processo

### Para Gestão
- ✅ Monitore indicadores de NCs
- ✅ Identifique tendências e padrões
- ✅ Foque em prevenção de recorrências
- ✅ Use dados para melhoria contínua
- ✅ Celebre reduções de NCs

## 📞 Suporte e Troubleshooting

### Problemas Comuns

#### NCs Recorrentes
```bash
# Análise de recorrência
flask analyze-recurring-ncs --process higienizacao --months 6

# Identificar causas comuns
flask identify-common-causes --classification major

# Plano de prevenção
flask create-prevention-plan --nc-id 123
```

#### Atraso no Tratamento
```bash
# Identificar NCs atrasadas
flask find-overdue-ncs --days 7

# Notificar responsáveis
flask notify-overdue-ncs --escalate

# Relatório de pendências
flask generate-pending-report --manager-id 456
```

#### Dados Incompletos
```bash
# Verificar completude
flask validate-nc-data --nc-id 123

# Completar informações
flask complete-nc-data --nc-id 123 --required-fields
```

---

**Última atualização:** Dezembro 2024
**Versão:** 1.0.0