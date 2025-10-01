# 📋 Controle de Versões - AlphaClinic QMS

## Visão Geral

O sistema de controle de versões do AlphaClinic QMS garante rastreabilidade completa de todas as alterações em documentos, atendendo requisitos de normas como ISO 9001, RDC ANVISA e boas práticas de gestão documental em ambientes clínicos.

## 🔢 Sistema de Versionamento

### Convenção de Numeração

#### Versão Principal (Major)
- **Formato**: `v2.0`, `v3.0`
- **Uso**: Mudanças significativas no documento
- **Critérios**:
  - Alteração de procedimentos críticos
  - Mudanças em políticas organizacionais
  - Revisões que afetam segurança do paciente
  - Atualizações normativas importantes

#### Versão Secundária (Minor)
- **Formato**: `v1.1`, `v1.2`, `v2.1`
- **Uso**: Melhorias e ajustes menores
- **Critérios**:
  - Correções de erros textuais
  - Esclarecimentos de procedimentos
  - Atualizações de referências
  - Pequenas otimizações

#### Versão de Correção (Patch)
- **Formato**: `v1.0.1`, `v1.1.1`
- **Uso**: Correções pontuais
- **Critérios**:
  - Erros de digitação
  - Correções gramaticais
  - Ajustes de formatação
  - Correções de dados

### Numeração Automática

#### Algoritmo de Versionamento
```javascript
function generateNextVersion(currentVersion, changeType) {
  const [major, minor, patch] = currentVersion.split('.').map(Number);

  switch(changeType) {
    case 'major':
      return `${major + 1}.0.0`;
    case 'minor':
      return `${major}.${minor + 1}.0`;
    case 'patch':
      return `${major}.${minor}.${patch + 1}`;
    default:
      return currentVersion;
  }
}
```

## 📋 Controle de Revisões

### Processo de Revisão

#### Tipos de Revisão
1. **Revisão Periódica**: Baseada em prazo definido
2. **Revisão Eventual**: Disparada por eventos específicos
3. **Revisão Crítica**: Para correções urgentes

#### Configuração de Prazos
```javascript
const reviewSettings = {
  "policies": {
    "review_months": 12,
    "urgent_review_days": 7,
    "critical_review_hours": 24
  },
  "procedures": {
    "review_months": 6,
    "urgent_review_days": 3,
    "critical_review_hours": 12
  },
  "forms": {
    "review_months": 24,
    "urgent_review_days": 15,
    "critical_review_hours": 72
  }
};
```

### Alertas e Notificações

#### Sistema de Alertas
- 🚨 **Alerta Vermelho**: Vencimento em 7 dias
- 🟡 **Alerta Amarelo**: Vencimento em 30 dias
- 🔵 **Alerta Azul**: Vencimento em 60 dias

#### Canais de Notificação
```bash
# Configurações de notificação
NOTIFICATION_CHANNELS=email,webhook,whatsapp
NOTIFICATION_RECIPIENTS=document_owner,department_manager,quality_team
NOTIFICATION_SCHEDULE=workdays_8to18
```

## 📊 Comparação de Versões

### Visualização de Diferenças

#### Interface de Comparação
```html
<!-- Visualização lado a lado -->
<div class="version-comparison">
  <div class="version-selector">
    <select id="version1">
      <option value="1.0">Versão 1.0</option>
      <option value="1.1">Versão 1.1</option>
      <option value="2.0">Versão 2.0</option>
    </select>
    <select id="version2">
      <option value="1.1">Versão 1.1</option>
      <option value="2.0">Versão 2.0</option>
      <option value="2.1">Versão 2.1</option>
    </select>
  </div>

  <div class="diff-viewer">
    <div class="old-version">
      <!-- Conteúdo versão antiga com destaques -->
    </div>
    <div class="new-version">
      <!-- Conteúdo versão nova com destaques -->
    </div>
  </div>

  <div class="diff-summary">
    <!-- Resumo das mudanças -->
    <p>Adicionadas: 15 linhas</p>
    <p>Removidas: 3 linhas</p>
    <p>Modificadas: 8 linhas</p>
  </div>
</div>
```

### Tipos de Mudanças Detectadas

#### Mudanças de Conteúdo
- ➕ **Adições**: Novo texto inserido
- ➖ **Remoções**: Texto removido
- 🔄 **Modificações**: Texto alterado
- 🔀 **Reordenações**: Mudança de posição

#### Mudanças de Formatação
- 🎨 **Estilo**: Mudanças de formatação
- 📊 **Estrutura**: Alterações em tabelas/listas
- 🔗 **Links**: Modificações de referências
- 🖼️ **Mídia**: Alterações em imagens/anexos

## 📋 Histórico Completo

### Registro de Alterações

#### Campos Auditados
```javascript
const auditFields = [
  "title",           // Título do documento
  "content",         // Conteúdo principal
  "metadata",        // Metadados
  "attachments",     // Anexos
  "signatures",      // Assinaturas
  "approvals",       // Aprovações
  "review_date",     // Data de revisão
  "effective_date",  // Data de vigência
  "status",          // Status do documento
  "permissions"      // Permissões de acesso
];
```

#### Estrutura do Registro de Auditoria
```json
{
  "version_id": "ver_abc123def456",
  "document_id": 123,
  "version_number": "1.1",
  "change_type": "minor",
  "created_at": "2024-12-01T10:30:00Z",
  "created_by": {
    "user_id": 1,
    "name": "João Silva",
    "role": "Enfermeiro Chefe"
  },
  "changes": [
    {
      "field": "content",
      "change_type": "modification",
      "old_value": "Procedimento antigo...",
      "new_value": "Procedimento atualizado...",
      "position": "section_3_paragraph_2"
    },
    {
      "field": "review_date",
      "change_type": "modification",
      "old_value": "2024-06-01",
      "new_value": "2024-12-01"
    }
  ],
  "reason": "Atualização conforme nova normativa RDC 123/2024",
  "approved_by": {
    "user_id": 2,
    "name": "Maria Santos",
    "role": "Gerente da Qualidade"
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

## 🔒 Controle de Acesso por Versão

### Permissões Granulares

#### Níveis de Acesso
```javascript
const versionPermissions = {
  "current": {
    "view": ["all_users"],
    "edit": ["document_owner", "editors"],
    "delete": ["admin_only"],
    "restore": ["admin_only"]
  },
  "previous": {
    "view": ["all_users"],
    "edit": ["admin_only"],
    "delete": ["admin_only"],
    "restore": ["document_owner", "admin_only"]
  },
  "archived": {
    "view": ["auditors", "admin_only"],
    "edit": ["admin_only"],
    "delete": ["admin_only"],
    "restore": ["admin_only"]
  }
};
```

### Controle de Visibilidade

#### Visibilidade por Status
- 👁️ **Rascunho**: Apenas criador e editores
- 🔍 **Revisão**: Criador, revisores e editores
- ✅ **Aprovado**: Todos os usuários autorizados
- 📦 **Arquivado**: Apenas auditores e administradores

## 📊 Relatórios de Versionamento

### Relatórios Disponíveis

#### Relatório de Mudanças
```bash
# Relatório mensal de mudanças
GET /api/v1/reports/version-changes?period=2024-12

# Resposta
{
  "total_changes": 45,
  "by_document_type": {
    "procedures": 25,
    "policies": 10,
    "forms": 10
  },
  "by_change_type": {
    "major": 5,
    "minor": 30,
    "patch": 10
  },
  "average_versions_per_document": 3.2,
  "most_changed_documents": [
    {
      "document_code": "PROC-001",
      "title": "Procedimento de Higienização",
      "versions": 5,
      "last_change": "2024-11-15"
    }
  ]
}
```

#### Relatório de Conformidade
```bash
# Documentos atualizados conforme normas
GET /api/v1/reports/compliance-versions?norm=RDC123

# Resposta
{
  "norm": "RDC 123/2024",
  "total_documents_affected": 15,
  "updated_documents": 12,
  "pending_documents": 3,
  "compliance_rate": 0.80,
  "last_update": "2024-11-20"
}
```

## 🔧 Configurações Avançadas

### Configurações de Versionamento

#### Parâmetros do Sistema
```bash
# Controle de versões
MAX_VERSIONS_PER_DOCUMENT=50
VERSION_COMPARISON_ENABLED=true
AUTO_VERSION_COMMENTS=true

# Backup de versões
VERSION_BACKUP_ENABLED=true
VERSION_BACKUP_FREQUENCY=daily
VERSION_BACKUP_RETENTION_DAYS=2555  # 7 anos

# Performance
VERSION_CACHE_TIMEOUT=3600  # 1 hora
VERSION_DIFF_CACHE=true
```

### Políticas de Retenção

#### Retenção por Tipo de Documento
```javascript
const retentionPolicies = {
  "critical": {
    "keep_all_versions": true,
    "retention_years": "permanent",
    "backup_frequency": "daily"
  },
  "important": {
    "keep_all_versions": true,
    "retention_years": 10,
    "backup_frequency": "weekly"
  },
  "standard": {
    "keep_all_versions": false,
    "retention_years": 5,
    "backup_frequency": "monthly"
  }
};
```

## 🚨 Gerenciamento de Conflitos

### Detecção de Conflitos

#### Cenários de Conflito
- ✏️ **Edição simultânea**: Dois usuários editando ao mesmo tempo
- 🔀 **Merge de mudanças**: Integração de alterações paralelas
- 📤 **Upload conflitante**: Upload de nova versão durante edição

#### Resolução de Conflitos
```javascript
const conflictResolution = {
  "simultaneous_edit": {
    "detection": "WebSocket + timestamp",
    "notification": "Ambos os usuários alertados",
    "resolution": "Last write wins + manual merge"
  },
  "parallel_changes": {
    "detection": "Diff algorithm",
    "notification": "Revisores alertados",
    "resolution": "Manual merge required"
  }
};
```

## 📱 Interface do Usuário

### Visualização de Versões

#### Lista de Versões
```html
<!-- Interface de versões -->
<div class="versions-list">
  <div class="version-item current">
    <span class="version-number">v2.1</span>
    <span class="version-date">01/12/2024</span>
    <span class="version-author">João Silva</span>
    <span class="version-status">Atual</span>
    <div class="version-actions">
      <button onclick="viewVersion()">Visualizar</button>
      <button onclick="compareVersions()">Comparar</button>
      <button onclick="restoreVersion()">Restaurar</button>
    </div>
  </div>

  <div class="version-item">
    <span class="version-number">v2.0</span>
    <span class="version-date">15/11/2024</span>
    <span class="version-author">Maria Santos</span>
    <span class="version-status">Anterior</span>
    <div class="version-actions">
      <button onclick="viewVersion()">Visualizar</button>
      <button onclick="compareVersions()">Comparar</button>
    </div>
  </div>
</div>
```

### Editor de Comparação

#### Ferramentas de Comparação
- 🔍 **Diff visual**: Destaque de mudanças
- 📊 **Mapa de mudanças**: Visão geral das diferenças
- 🔀 **Merge inteligente**: Sugestões de integração
- 💬 **Comentários**: Discussão sobre mudanças

## 🔧 APIs de Versionamento

### API REST para Versões

#### Listar Versões
```bash
# Listar todas as versões de um documento
GET /api/v1/documents/{id}/versions

# Resposta
{
  "document_id": 123,
  "current_version": "2.1",
  "total_versions": 5,
  "versions": [
    {
      "version_id": "ver_abc123",
      "version_number": "2.1",
      "created_at": "2024-12-01T10:30:00Z",
      "created_by": "João Silva",
      "change_type": "minor",
      "file_size": 245760,
      "is_current": true
    }
  ]
}
```

#### Comparar Versões
```bash
# Comparar duas versões específicas
GET /api/v1/documents/{id}/versions/compare?from=1.0&to=2.1

# Resposta
{
  "from_version": "1.0",
  "to_version": "2.1",
  "changes": [
    {
      "type": "addition",
      "content": "Novo procedimento adicionado",
      "position": "section_3",
      "lines_added": 15
    },
    {
      "type": "modification",
      "old_content": "Texto antigo",
      "new_content": "Texto atualizado",
      "position": "section_2_paragraph_1"
    }
  ],
  "summary": {
    "additions": 15,
    "deletions": 3,
    "modifications": 8
  }
}
```

#### Reverter Versão
```bash
# Reverter para versão específica
POST /api/v1/documents/{id}/versions/{version_id}/restore

{
  "reason": "Correção de erro identificado na versão atual",
  "notify_users": true,
  "create_backup": true
}
```

## 🎯 Melhores Práticas

### Para Criadores de Documentos
- ✅ Documente sempre o motivo da mudança
- ✅ Use tipos de mudança adequados (major/minor/patch)
- ✅ Revise mudanças antes de publicar
- ✅ Mantenha versões anteriores acessíveis

### Para Administradores
- ✅ Configure retenção adequada por tipo de documento
- ✅ Monitore versões regularmente
- ✅ Faça backups regulares de versões críticas
- ✅ Treine usuários sobre versionamento

### Para Auditores
- ✅ Verifique trilha de auditoria completa
- ✅ Valide processos de versionamento
- ✅ Confirme conformidade com normas
- ✅ Documente findings de auditoria

## 📞 Suporte e Troubleshooting

### Problemas Comuns

#### Perda de Dados
```bash
# Recuperar versão anterior
flask restore-version --document-id 123 --version 1.0

# Verificar backups
ls -la /backup/versions/

# Restaurar backup
flask restore-backup --file backup_20241201.zip
```

#### Performance Lenta
```bash
# Otimizar cache de versões
redis-cli flushall

# Reindexar versões
flask reindex-versions

# Limpar versões antigas
flask cleanup-versions --older-than 365
```

#### Conflitos de Edição
```bash
# Resolver conflitos manualmente
flask resolve-conflicts --document-id 123

# Forçar resolução automática
flask auto-resolve-conflicts --document-id 123 --strategy last_write_wins
```

---

**Última atualização:** Dezembro 2024
**Versão:** 1.0.0