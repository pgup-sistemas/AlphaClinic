# 👷‍♀️ CIPA - Comissão Interna de Prevenção de Acidentes - AlphaClinic QMS

## Visão Geral

O módulo CIPA do AlphaClinic QMS oferece gestão completa da Comissão Interna de Prevenção de Acidentes, atendendo aos requisitos da Norma Regulamentadora NR-5 do Ministério do Trabalho e Emprego, garantindo segurança e saúde ocupacional.

## 📋 Estrutura da CIPA

### Composição da Comissão

#### Membros Representantes
```javascript
const cipaMembers = {
  "employer_representatives": [
    {
      "name": "João Silva",
      "role": "Presidente",
      "position": "Gerente de RH",
      "mandate": "2024-2025",
      "responsibilities": [
        "Coordenar atividades da CIPA",
        "Representar empregador",
        "Convocar reuniões",
        "Aprovar planos de ação"
      ]
    },
    {
      "name": "Maria Santos",
      "role": "Membro Titular",
      "position": "Enfermeira do Trabalho",
      "mandate": "2024-2025",
      "responsibilities": [
        "Executar inspeções de segurança",
        "Investigar acidentes",
        "Promover treinamentos"
      ]
    }
  ],
  "employee_representatives": [
    {
      "name": "Carlos Oliveira",
      "role": "Vice-Presidente",
      "position": "Técnico de Enfermagem",
      "mandate": "2024-2025",
      "responsibilities": [
        "Representar empregados",
        "Participar de inspeções",
        "Divulgar informações de segurança"
      ]
    },
    {
      "name": "Ana Costa",
      "role": "Membro Titular",
      "position": "Auxiliar de Serviços Gerais",
      "mandate": "2024-2025",
      "responsibilities": [
        "Identificar riscos",
        "Sugerir melhorias",
        "Participar de campanhas"
      ]
    }
  ]
};
```

### Dimensionamento da CIPA

#### Cálculo de Membros
```javascript
function calculateCipaMembers(employeeCount, riskLevel) {
  const baseMembers = {
    "1-19": {"titular": 2, "suplente": 2},
    "20-50": {"titular": 3, "suplente": 3},
    "51-100": {"titular": 4, "suplente": 4},
    "101-200": {"titular": 5, "suplente": 5},
    "201-500": {"titular": 6, "suplente": 6}
  };

  let members = baseMembers["51-100"]; // Exemplo

  // Ajuste por nível de risco
  if (riskLevel >= 4) {
    members.titular += 1;
    members.suplente += 1;
  }

  return members;
}
```

## 📅 Processo Eleitoral

### Etapas do Processo Eleitoral

#### 1. Planejamento
- **Período**: Outubro/Novembro (anualmente)
- **Responsável**: RH + CIPA atual
- **Atividades**:
  - Definir cronograma
  - Elaborar edital
  - Comunicar empregados
  - Preparar material de votação

#### 2. Inscrição de Candidatos
```javascript
const candidateRegistration = {
  "period": "01/10/2024 - 15/10/2024",
  "requirements": [
    "Tempo mínimo de 6 meses na empresa",
    "Não ter sido punido disciplinarmente",
    "Disponibilidade para participar de reuniões",
    "Perfil adequado para função"
  ],
  "registration_form": {
    "personal_info": true,
    "motivation": true,
    "experience": true,
    "availability": true
  }
};
```

#### 3. Campanha Eleitoral
- **Duração**: 15 dias antes da votação
- **Meios**: Murais, e-mail, reuniões
- **Regras**:
  - Material aprovado pela CIPA
  - Sem uso de recursos da empresa
  - Respeito aos candidatos

#### 4. Votação
```javascript
const votingProcess = {
  "date": "15/11/2024",
  "time": "07:00 - 17:00",
  "method": "Votação eletrônica + urna física",
  "eligibility": "Todos os empregados com mais de 90 dias",
  "secrecy": "Garantia de sigilo do voto",
  "supervision": "Comissão eleitoral independente"
};
```

#### 5. Apuração e Posse
- **Apuração**: Imediata após encerramento
- **Divulgação**: Resultado oficial no dia seguinte
- **Posse**: 1º dia útil do ano subsequente
- **Certificação**: Emissão de certificados

## 🔍 Inspeções de Segurança

### Programa de Inspeções

#### Tipos de Inspeção
1. **Inspeções Planejadas**: Rotina mensal/trimestral
2. **Inspeções Eventuais**: Após acidentes ou mudanças
3. **Inspeções Especiais**: Focadas em áreas críticas
4. **Inspeções de Rotina**: Diárias por supervisores

#### Checklist de Inspeção
```javascript
const inspectionChecklist = {
  "area": "Centro Cirúrgico",
  "date": "2024-12-01",
  "inspector": "Maria Santos",
  "items": [
    {
      "category": "Instalações Físicas",
      "items": [
        {"item": "Piso antiderrapante", "status": "OK", "observations": ""},
        {"item": "Iluminação adequada", "status": "OK", "observations": ""},
        {"item": "Ventilação funcionando", "status": "NOK", "observations": "Exaustor com defeito"}
      ]
    },
    {
      "category": "Equipamentos de Proteção",
      "items": [
        {"item": "EPIs disponíveis", "status": "OK", "observations": ""},
        {"item": "EPIs em bom estado", "status": "OK", "observations": ""},
        {"item": "Treinamento de uso", "status": "NOK", "observations": "Treinamento pendente"}
      ]
    },
    {
      "category": "Procedimentos",
      "items": [
        {"item": "Procedimentos afixados", "status": "OK", "observations": ""},
        {"item": "Equipe treinada", "status": "OK", "observations": ""},
        {"item": "Registros atualizados", "status": "NOK", "observations": "Última atualização há 6 meses"}
      ]
    }
  ]
};
```

### Mapa de Riscos

#### Elaboração do Mapa
```javascript
const riskMap = {
  "areas": [
    {
      "area": "Centro Cirúrgico",
      "risks": [
        {
          "type": "Biológico",
          "description": "Contato com fluidos corporais",
          "probability": "High",
          "severity": "High",
          "control_measures": ["EPIs", "Treinamento", "Procedimentos"],
          "responsible": "CCI"
        },
        {
          "type": "Químico",
          "description": "Manipulação de medicamentos",
          "probability": "Medium",
          "severity": "High",
          "control_measures": ["Treinamento", "EPIs", "Armazenamento adequado"],
          "responsible": "Farmácia"
        }
      ]
    }
  ],
  "overall_risk_level": "Medium",
  "review_frequency": "Annual",
  "last_review": "2024-01-15"
};
```

## 🩹 Investigação de Acidentes

### Processo de Investigação

#### Notificação de Acidente
```javascript
const accidentNotification = {
  "immediate_actions": [
    "Prestar primeiros socorros",
    "Preservar local do acidente",
    "Comunicar supervisor imediato",
    "Acionar SESMT/CIPA",
    "Comunicar família (se necessário)"
  ],
  "notification_deadline": "Primeira hora após ocorrência",
  "required_information": [
    "Dados do acidentado",
    "Local e hora do acidente",
    "Descrição do ocorrido",
    "Testemunhas",
    "Medidas imediatas tomadas"
  ]
};
```

#### Análise de Causas
```javascript
const accidentAnalysis = {
  "methods": [
    "Árvore de Causas",
    "Análise de Barreiras",
    "Timeline Analysis",
    "Human Factors Analysis"
  ],
  "investigation_team": [
    "Membro da CIPA",
    "Supervisor da área",
    "Especialista em segurança",
    "Representante do RH"
  ],
  "timeline": {
    "immediate": "Análise preliminar (24h)",
    "short_term": "Análise detalhada (7 dias)",
    "long_term": "Análise de tendências (30 dias)"
  }
};
```

## 📚 Treinamentos e Capacitações

### Programa Anual de Treinamentos

#### Cursos Obrigatórios
```javascript
const mandatoryTrainings = {
  "seguranca_trabalho": {
    "title": "Segurança e Saúde no Trabalho",
    "workload": "8 horas",
    "frequency": "Anual",
    "target_audience": "Todos os empregados",
    "content": [
      "NR-5 (CIPA)",
      "NR-6 (EPIs)",
      "NR-26 (Sinalização)",
      "Primeiros Socorros",
      "Prevenção de Incêndios"
    ]
  },
  "cipa_members": {
    "title": "Capacitação para Membros da CIPA",
    "workload": "20 horas",
    "frequency": "Mandato",
    "target_audience": "Membros da CIPA",
    "content": [
      "Legislação trabalhista",
      "Metodologia de investigação",
      "Técnicas de inspeção",
      "Elaboração de mapas de risco"
    ]
  }
};
```

### Controle de Treinamentos

#### Registro e Acompanhamento
```javascript
const trainingControl = {
  "employee": "João Silva",
  "trainings": [
    {
      "course": "Segurança e Saúde no Trabalho",
      "completion_date": "2024-03-15",
      "validity": "2025-03-15",
      "status": "Valid",
      "certificate": "CERT-2024-001",
      "instructor": "Maria Santos"
    },
    {
      "course": "Primeiros Socorros",
      "completion_date": "2024-06-10",
      "validity": "2025-06-10",
      "status": "Valid",
      "certificate": "CERT-2024-002",
      "instructor": "Carlos Oliveira"
    }
  ],
  "next_due": "2025-03-15",
  "compliance_rate": "100%"
};
```

## 📊 Indicadores de Segurança

### Métricas CIPA

#### Taxa de Acidentes
```javascript
const accidentMetrics = {
  "period": "2024",
  "total_accidents": 5,
  "by_type": {
    "typical": 3,
    "trajectory": 1,
    "equipment": 1,
    "other": 0
  },
  "by_area": {
    "Centro Cirúrgico": 2,
    "Enfermagem": 2,
    "Manutenção": 1
  },
  "severity": {
    "without_leave": 4,
    "with_leave": 1,
    "fatal": 0
  },
  "trend": "Melhorando (-40% vs 2023)"
};
```

#### Indicadores de Gestão
```javascript
const managementIndicators = {
  "inspections_completed": {
    "planned": 48,
    "completed": 45,
    "compliance": "94%"
  },
  "trainings_completed": {
    "planned": 120,
    "completed": 115,
    "compliance": "96%"
  },
  "risk_mitigation": {
    "identified_risks": 25,
    "mitigated_risks": 20,
    "effectiveness": "80%"
  },
  "cipa_activities": {
    "meetings_held": 12,
    "attendance_rate": "85%",
    "actions_completed": "90%"
  }
};
```

## 📋 Reuniões da CIPA

### Calendário de Reuniões

#### Reuniões Ordinárias
```javascript
const regularMeetings = {
  "frequency": "Mensal",
  "duration": "2 horas",
  "schedule": "Primeira terça-feira do mês, 14:00",
  "venue": "Sala de reuniões principal",
  "required_attendance": "Todos os membros titulares",
  "agenda_template": [
    "Verificação de pauta",
    "Assuntos pendentes da reunião anterior",
    "Análise de acidentes ocorridos",
    "Planejamento de inspeções",
    "Avaliação de medidas implementadas",
    "Assuntos gerais",
    "Definição de próximos passos"
  ]
};
```

#### Reuniões Extraordinárias
- **Convocação**: Quando necessário
- **Motivos**: Acidentes graves, situações de emergência
- **Prazo**: Mínimo 24h de antecedência
- **Documentação**: Ata específica

### Atas de Reuniões

#### Estrutura da Ata
```javascript
const meetingMinutes = {
  "header": {
    "meeting_number": "012/2024",
    "date": "2024-12-01",
    "time": "14:00 - 16:00",
    "venue": "Sala de reuniões",
    "type": "Ordinária"
  },
  "attendance": {
    "present": ["João Silva", "Maria Santos", "Carlos Oliveira"],
    "absent": ["Ana Costa"],
    "guests": ["Dr. Roberto", "Enf. Patricia"]
  },
  "agenda": [
    {
      "item": "Análise de acidente do mês",
      "discussion": "Acidente em 15/11 - Queda de funcionário",
      "decisions": ["Implementar treinamento adicional", "Revisar procedimentos"],
      "responsible": "Maria Santos",
      "deadline": "2024-12-15"
    }
  ],
  "next_meeting": {
    "date": "2025-01-05",
    "main_topics": ["Avaliação de treinamentos", "Planejamento de inspeções"]
  }
};
```

## 🛠️ Plano de Ação Anual

### Estrutura do Plano

#### Objetivos Estratégicos
```javascript
const strategicObjectives = {
  "year": 2024,
  "objectives": [
    {
      "id": "OBJ-001",
      "description": "Reduzir acidentes em 30%",
      "baseline": "7 acidentes em 2023",
      "target": "5 acidentes em 2024",
      "kpis": ["Taxa de acidentes", "Taxa de frequência", "Taxa de gravidade"]
    },
    {
      "id": "OBJ-002",
      "description": "Aumentar cobertura de treinamentos",
      "baseline": "80% em 2023",
      "target": "95% em 2024",
      "kpis": ["% empregados treinados", "Treinamentos realizados"]
    }
  ]
};
```

#### Ações Específicas
```javascript
const actionPlan = {
  "inspections": [
    {
      "id": "INS-001",
      "description": "Inspeção mensal de todas as áreas",
      "responsible": "CIPA",
      "frequency": "Mensal",
      "resources": ["Checklists", "Câmera fotográfica"],
      "monitoring": "Relatório mensal"
    }
  ],
  "trainings": [
    {
      "id": "TRE-001",
      "description": "Treinamento anual de segurança",
      "responsible": "SESMT",
      "schedule": "Março 2024",
      "target_audience": "Todos os empregados",
      "evaluation": "Prova teórica + prática"
    }
  ],
  "campaigns": [
    {
      "id": "CAM-001",
      "description": "Campanha de prevenção de quedas",
      "responsible": "CIPA",
      "period": "Abril-Maio 2024",
      "activities": ["Palestras", "Cartazes", "Treinamento prático"],
      "evaluation": "Questionário de conhecimento"
    }
  ]
};
```

## 📱 Interface do Usuário

### Módulo CIPA

#### Dashboard Principal
```html
<!-- Dashboard CIPA -->
<div class="cipa-dashboard">
  <div class="header">
    <h2>CIPA - Comissão Interna de Prevenção de Acidentes</h2>
    <div class="quick-actions">
      <button onclick="newInspection()">Nova Inspeção</button>
      <button onclick="reportAccident()">Reportar Acidente</button>
      <button onclick="scheduleMeeting()">Agendar Reunião</button>
    </div>
  </div>

  <div class="kpi-cards">
    <div class="kpi-card">
      <h3>Acidentes Este Ano</h3>
      <span class="number">5</span>
      <span class="trend down">-40% vs 2023</span>
    </div>
    <div class="kpi-card">
      <h3>Inspeções Realizadas</h3>
      <span class="number">45/48</span>
      <span class="percentage">94%</span>
    </div>
    <div class="kpi-card">
      <h3>Treinamentos</h3>
      <span class="number">115/120</span>
      <span class="percentage">96%</span>
    </div>
  </div>

  <div class="upcoming-activities">
    <h3>Próximas Atividades</h3>
    <!-- Lista de atividades -->
  </div>
</div>
```

### Formulário de Inspeção

#### Captura de Inspeção
```html
<!-- Formulário de inspeção -->
<form class="inspection-form">
  <div class="form-section">
    <h3>Dados da Inspeção</h3>
    <div class="form-row">
      <div class="form-group">
        <label>Área Inspeccionada:</label>
        <select name="area" required>
          <option value="centro_cirurgico">Centro Cirúrgico</option>
          <option value="enfermagem">Enfermagem</option>
        </select>
      </div>
      <div class="form-group">
        <label>Data da Inspeção:</label>
        <input type="date" name="date" required>
      </div>
    </div>
  </div>

  <div class="form-section">
    <h3>Checklist de Verificação</h3>
    <div class="checklist-container">
      <!-- Itens do checklist dinâmicos -->
    </div>
  </div>

  <div class="form-section">
    <h3>Observações Gerais</h3>
    <textarea name="observations" rows="4"></textarea>
  </div>

  <div class="form-section">
    <h3>Fotos/Evidências</h3>
    <div class="file-upload">
      <input type="file" multiple accept="image/*">
    </div>
  </div>

  <div class="form-actions">
    <button type="button" onclick="saveDraft()">Salvar Rascunho</button>
    <button type="submit">Finalizar Inspeção</button>
  </div>
</form>
```

## 🔧 APIs da CIPA

### Endpoints Principais

#### Gerenciamento de Inspeções
```bash
# Criar nova inspeção
POST /api/v1/cipa/inspections
{
  "area": "Centro Cirúrgico",
  "scheduled_date": "2024-12-01",
  "inspectors": [1, 2],
  "checklist_template": "seguranca_hospitalar"
}

# Registrar resultado de inspeção
POST /api/v1/cipa/inspections/{id}/results
{
  "items": [
    {
      "checklist_item_id": 1,
      "status": "OK",
      "observations": "Tudo em ordem"
    },
    {
      "checklist_item_id": 2,
      "status": "NOK",
      "observations": "Extintor vencido",
      "photos": ["photo1.jpg", "photo2.jpg"]
    }
  ]
}
```

#### Gerenciamento de Acidentes
```bash
# Reportar acidente
POST /api/v1/cipa/accidents
{
  "type": "typical",
  "date_time": "2024-12-01T10:30:00Z",
  "location": "Centro Cirúrgico - Sala 2",
  "injured_person": {
    "name": "João Silva",
    "position": "Técnico de Enfermagem",
    "immediate_care": "Ambulatório interno"
  },
  "description": "Queda durante transporte de paciente",
  "witnesses": ["Maria Santos", "Carlos Oliveira"],
  "immediate_actions": ["Primeiros socorros", "Preservação do local"]
}
```

## 🎯 Melhores Práticas

### Para Membros da CIPA
- ✅ Participe ativamente das reuniões
- ✅ Realize inspeções regularmente
- ✅ Mantenha sigilo sobre informações sensíveis
- ✅ Divulgue informações de segurança
- ✅ Esteja sempre atualizado sobre legislação

### Para Empregadores
- ✅ Forneça recursos necessários para CIPA
- ✅ Implemente recomendações da comissão
- ✅ Respeite estabilidade de membros
- ✅ Incentive participação dos empregados
- ✅ Mantenha diálogo aberto com a CIPA

### Para SESMT
- ✅ Apoie tecnicamente a CIPA
- ✅ Forneça treinamentos especializados
- ✅ Participe de investigações de acidentes
- ✅ Auxilie na elaboração de documentos
- ✅ Monitore indicadores de segurança

## 📞 Suporte e Troubleshooting

### Problemas Comuns

#### Baixa Participação
```bash
# Estratégias para aumentar participação
flask increase-cipa-participation --strategies "comunicacao,treinamento,reconhecimento"

# Campanhas de sensibilização
flask create-awareness-campaign --target "empregados" --topic "seguranca_trabalho"
```

#### Inspeções Incompletas
```bash
# Identificar inspeções pendentes
flask find-pending-inspections --overdue-days 7

# Plano de regularização
flask create-inspection-catchup-plan --areas "all" --priority "critical_first"
```

#### Dados Inconsistentes
```bash
# Verificar consistência de dados
flask validate-cipa-data --year 2024

# Corrigir inconsistências
flask fix-cipa-data-inconsistencies --backup-first
```

---

**Última atualização:** Dezembro 2024
**Versão:** 1.0.0