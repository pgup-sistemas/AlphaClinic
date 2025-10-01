# 🏥 Alphaclin QMS - Guia do Usuário

<div style="text-align: center; margin: 2rem 0;">
  <img src="https://img.shields.io/badge/Status-Ativo-brightgreen?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Versão-1.0.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Licença-MIT-green?style=for-the-badge" alt="License">
</div>

## 📋 Bem-vindo ao Alphaclin QMS

O **Alphaclin QMS** é um sistema completo de gestão da qualidade desenvolvido especificamente para clínicas e instituições de saúde. Este guia irá ajudá-lo a entender e utilizar todas as funcionalidades do sistema de forma prática e eficiente.

---

## 🚀 Início Rápido

### Primeiro Acesso
1. **Acesse**: `http://localhost:5000`
2. **Login**: Use as credenciais fornecidas pelo administrador
3. **Dashboard**: Você será direcionado ao painel principal

### Navegação Básica
- **Menu Lateral**: Acesso a todas as funcionalidades
- **Barra Superior**: Notificações, perfil e configurações
- **Busca**: Campo de pesquisa no topo para encontrar qualquer coisa

---

## 👤 Gestão de Usuários e Equipes

### Como Cadastrar um Novo Usuário

#### Passo 1: Acessar Gestão de Usuários
```
Menu → Usuários → Novo Usuário
```

#### Passo 2: Preencher Informações Básicas
- **Nome Completo**: Nome completo do usuário
- **E-mail**: Endereço de e-mail válido
- **CPF**: CPF do usuário
- **Cargo**: Função na organização
- **Departamento**: Setor de atuação

#### Passo 3: Definir Permissões
- **Perfil**: Selecione o nível de acesso
  - Administrador: Acesso total ao sistema
  - Gerente: Gerenciamento de equipe e processos
  - Usuário: Acesso limitado às próprias tarefas
  - Auditor: Acesso apenas leitura para auditorias

#### Passo 4: Configurar Equipe
- **Equipe**: Vincule o usuário a uma equipe existente
- **Líder**: Marque se é líder da equipe

#### Passo 5: Salvar e Notificar
- Clique em "Salvar"
- O sistema enviará automaticamente um e-mail com as credenciais

### Como Criar uma Equipe

#### Passo 1: Acessar Gestão de Equipes
```
Menu → Equipes → Nova Equipe
```

#### Passo 2: Informações da Equipe
- **Nome**: Nome da equipe
- **Descrição**: Objetivo e responsabilidades
- **Líder**: Selecione o responsável

#### Passo 3: Adicionar Membros
- **Buscar Usuários**: Use o campo de busca
- **Selecionar**: Marque os usuários desejados
- **Função**: Defina o papel na equipe

#### Passo 4: Configurar Permissões
- **Acesso Compartilhado**: Permissões para documentos e processos
- **Notificações**: Configurar alertas automáticos

---

## 📄 Gestão Documental

### Como Criar um Novo Documento

#### Passo 1: Iniciar Criação
```
Menu → Documentos → Novo Documento
```

#### Passo 2: Selecionar Tipo e Categoria
- **Tipo**: Procedimento, Política, Formulário, etc.
- **Categoria**: Área específica (Enfermagem, Médica, Administrativa)
- **Código**: Gerado automaticamente ou personalizado

#### Passo 3: Preencher Metadados
- **Título**: Nome descritivo do documento
- **Descrição**: Resumo do conteúdo
- **Palavras-chave**: Tags para facilitar busca
- **Prazo de Revisão**: Frequência de atualização

#### Passo 4: Escrever Conteúdo
- **Editor Rich Text**: Formatação completa disponível
- **Inserir Imagens**: Upload direto ou arrastar
- **Tabelas**: Criar tabelas complexas
- **Links**: Referências cruzadas entre documentos

#### Passo 5: Configurar Workflow
- **Revisores**: Selecionar usuários para revisão
- **Aprovadores**: Definir níveis de aprovação
- **Prazo**: Data limite para conclusão

#### Passo 6: Enviar para Aprovação
- Clique em "Enviar para Revisão"
- O sistema notificará automaticamente os envolvidos

### Como Aprovar um Documento

#### Passo 1: Receber Notificação
- Verifique suas notificações no dashboard
- Ou acesse: `Menu → Documentos → Pendentes de Aprovação`

#### Passo 2: Revisar Conteúdo
- Leia o documento completo
- Verifique conformidade com normas
- Adicione comentários se necessário

#### Passo 3: Tomar Decisão
- **Aprovar**: Documento segue para próximo nível
- **Reprovar**: Retorna para revisão com comentários
- **Solicitar Alterações**: Especificar mudanças necessárias

#### Passo 4: Assinar Digitalmente (se aplicável)
- Use certificado digital ICP-Brasil
- Ou assinatura biométrica no mobile

### Como Pesquisar Documentos

#### Busca Básica
- Use o campo de busca no topo
- Digite palavras-chave, códigos ou títulos

#### Busca Avançada
```
Menu → Documentos → Busca Avançada
```
- **Categoria**: Filtrar por tipo
- **Status**: Rascunho, Revisão, Aprovado, etc.
- **Data**: Período de criação ou modificação
- **Autor**: Documentos de um usuário específico
- **Conteúdo**: Busca dentro do texto dos documentos

---

## 🔍 Auditorias

### Como Planejar uma Auditoria

#### Passo 1: Criar Nova Auditoria
```
Menu → Auditorias → Nova Auditoria
```

#### Passo 2: Definir Escopo
- **Tipo**: Interna ou Externa
- **Área**: Setor ou processo a ser auditado
- **Norma**: Referência normativa (ISO 9001, etc.)
- **Período**: Datas de realização

#### Passo 3: Selecionar Equipe
- **Auditor Líder**: Responsável principal
- **Auditores**: Membros da equipe
- **Especialistas**: Consultores técnicos se necessário

#### Passo 4: Preparar Checklist
- **Baseado em Norma**: Checklist automático
- **Personalizado**: Adicionar itens específicos
- **Evidências**: Definir tipos de prova necessários

#### Passo 5: Agendar e Comunicar
- Definir cronograma detalhado
- Notificar áreas auditadas
- Preparar documentação de apoio

### Como Registrar Não Conformidades

#### Durante a Auditoria
1. **Identificar Problema**: Durante inspeção ou entrevista
2. **Registrar Imediatamente**: Use o botão "Nova NC"
3. **Classificar**: Crítica, Major, Menor ou Observação

#### Campos Obrigatórios
- **Descrição**: O que foi observado
- **Requisito**: Norma ou procedimento violado
- **Evidências**: Fotos, documentos, testemunhos
- **Responsável**: Quem deve corrigir
- **Prazo**: Data limite para correção

#### Após Registro
- Sistema notifica automaticamente o responsável
- NC entra no workflow de tratamento
- Acompanhamento automático de prazos

---

## ⚠️ Não Conformidades (NCs)

### Como Tratar uma NC

#### Passo 1: Receber Atribuição
- Verifique notificações ou dashboard
- Acesse: `Menu → Qualidade → NCs → Minhas NCs`

#### Passo 2: Analisar Causa Raiz
- Use técnica dos 5 Porquês
- Ou diagrama de Ishikawa (Espinha de Peixe)
- Identifique causas fundamentais

#### Passo 3: Planejar Ações
- **Ações Imediatas**: Correções rápidas
- **Ações Corretivas**: Soluções permanentes
- **Ações Preventivas**: Evitar recorrência

#### Passo 4: Implementar
- Executar ações planejadas
- Documentar evidências
- Atualizar status regularmente

#### Passo 5: Verificar Eficácia
- Testar se a solução resolveu o problema
- Monitorar indicadores relacionados
- Obter feedback dos envolvidos

#### Passo 6: Encerrar
- Documentar lições aprendidas
- Atualizar procedimentos se necessário
- Arquivar com evidências completas

---

## 📊 Relatórios e Dashboards

### Como Gerar um Relatório

#### Passo 1: Selecionar Tipo
```
Menu → Relatórios → Novo Relatório
```

#### Tipos Disponíveis
- **Relatório de Conformidade**: Status por norma
- **Relatório de Auditorias**: Resultados e tendências
- **Relatório de NCs**: Análise de não conformidades
- **Relatório de Documentos**: Controle documental
- **Relatório de Produtividade**: Métricas de equipe

#### Passo 2: Configurar Parâmetros
- **Período**: Datas de início e fim
- **Filtros**: Por departamento, usuário, tipo, etc.
- **Formato**: PDF, Excel ou visualização web

#### Passo 3: Gerar e Exportar
- Clique em "Gerar Relatório"
- Aguarde processamento
- Baixe ou compartilhe o arquivo

### Como Personalizar Dashboard

#### Passo 1: Acessar Configurações
```
Menu → Dashboard → Personalizar
```

#### Passo 2: Adicionar Widgets
- **KPIs**: Indicadores principais
- **Gráficos**: Tendências e comparações
- **Listas**: Tarefas pendentes, alertas
- **Calendário**: Eventos e prazos

#### Passo 3: Configurar Layout
- Arraste widgets para reorganizar
- Redimensione conforme necessidade
- Salve layout personalizado

#### Passo 4: Compartilhar
- Compartilhar dashboard com equipe
- Definir permissões de visualização
- Agendar envio automático

---

## 🔔 Notificações

### Como Configurar Notificações

#### Passo 1: Acessar Preferências
```
Menu → Perfil → Notificações
```

#### Passo 2: Tipos de Notificação
- **E-mail**: Notificações por e-mail
- **Sistema**: Alertas no dashboard
- **Mobile**: Push notifications (quando disponível)

#### Passo 3: Configurar por Categoria
- **Documentos**: Aprovações, revisões, publicações
- **Auditorias**: Planejamento, execução, resultados
- **NCs**: Atribuições, prazos, encerramentos
- **Sistema**: Manutenção, atualizações, alertas

#### Passo 4: Horários de Silêncio
- Definir período noturno
- Configurar feriados
- Exceções para alertas críticos

---

## 🔧 Solução de Problemas

### Problemas Comuns

#### Não Consigo Fazer Login
- Verifique se o usuário está ativo
- Confirme senha (diferencia maiúsculas/minúsculas)
- Tente redefinir senha
- Contate administrador se persistir

#### Documento Não Aparece na Busca
- Verifique filtros aplicados
- Confirme permissões de acesso
- Tente busca por código ou título exato
- Aguarde indexação se documento é novo

#### Relatório Não Gera
- Verifique se há dados no período selecionado
- Confirme permissões para os dados
- Tente período menor
- Contate suporte se erro persistir

#### Notificações Não Chegam
- Verifique pasta de spam
- Confirme endereço de e-mail cadastrado
- Verifique configurações de notificação
- Teste envio manual

---

## 📚 Recursos Adicionais

### Tutoriais em Vídeo
- **Introdução ao Sistema**: Visão geral completa
- **Gestão Documental**: Passo-a-passo detalhado
- **Auditorias Práticas**: Como realizar auditorias
- **Relatórios Avançados**: Análise de dados

### Base de Conhecimento
- **Perguntas Frequentes**: Respostas para dúvidas comuns
- **Guias Detalhados**: Tutoriais passo-a-passo
- **Dicas e Truques**: Otimizações de uso
- **Casos de Uso**: Exemplos práticos

### Suporte
- **Chat Online**: Atendimento em tempo real
- **E-mail**: suporte@alphaclin.com
- **Telefone**: +55 11 99999-9999
- **Comunidade**: Fórum de usuários

---

## 👨‍💼 Administração do Sistema (Apenas para Administradores)

### Funcionalidades de Administração Disponíveis
O sistema inclui funcionalidades avançadas de administração acessíveis apenas para usuários com perfil **Administrador**:

#### 🎛️ **Sistema de Permissões Avançado**
- **Controle Granular**: Permissões específicas por usuário e recurso
- **Acessos Temporários**: Concessão de acesso limitado por tempo
- **Permissões de Equipe**: Controle coletivo de acesso
- **Auditoria Completa**: Registro de todas as verificações de permissão

#### 📊 **Dashboard de Administração**
- **Acesso**: `http://localhost:5000/admin/permissions`
- **Estatísticas**: Visão geral do sistema de permissões
- **Monitoramento**: Acessos e atividades em tempo real
- **Relatórios**: Análise de uso e segurança

#### 🔧 **Ferramentas Administrativas**
- **Gestão de Usuários**: Controle completo de usuários e perfis
- **Auditoria de Segurança**: Logs detalhados de acesso
- **Configurações Avançadas**: Personalização do sistema
- **Relatórios de Conformidade**: LGPD, ISO 9001, etc.

### Como Acessar Recursos de Administração
1. **Login como Admin**: Use credenciais de administrador
2. **Menu Lateral**: Aparece opção **"Administração"** apenas para admins
3. **Dashboard**: Visualize estatísticas e opções administrativas
4. **Configurações**: Gerencie permissões, usuários e equipes

**Nota**: Se você é administrador e não vê essas opções, entre em contato com o suporte técnico.

---

## 🎯 Próximos Passos

### Capacitação Recomendada
1. **Complete o Tutorial Inicial**: 15 minutos
2. **Assista Vídeos Essenciais**: 1 hora
3. **Pratique com Dados de Teste**: 30 minutos
4. **Configure seu Dashboard**: 15 minutos
5. **Explore Funcionalidades Avançadas**: Conforme necessidade

### Certificação
- **Certificado Básico**: Após completar tutoriais
- **Certificado Avançado**: Após uso consistente
- **Certificado Especialista**: Para usuários avançados

---

<div style="text-align: center; margin: 3rem 0; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
  <h2>🚀 Alphaclin QMS - Seu Parceiro em Qualidade</h2>
  <p style="font-size: 1.2em; margin: 1rem 0;">
    Sistema completo para gestão da qualidade em saúde
  </p>
  <p style="font-size: 1.1em;">
    <strong>Aprenda • Implemente • Melhore</strong>
  </p>
</div>