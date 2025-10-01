# 👤 Gestão de Usuários e Equipes - Guia Prático

## Visão Geral

Este guia mostra como gerenciar usuários e equipes no Alphaclin QMS, desde o cadastro básico até configurações avançadas de permissões.

---

## 👤 Gerenciando Usuários

### Cadastrando um Novo Usuário

#### Passo 1: Acesse a Gestão de Usuários
1. Clique no menu lateral **"Usuários"**
2. Selecione **"Novo Usuário"**
3. A tela de cadastro será aberta

#### Passo 2: Informações Pessoais
Preencha os campos obrigatórios:
- **Nome Completo**: Nome completo do usuário
- **E-mail**: Endereço válido para notificações
- **CPF**: CPF do usuário (usado para validação)
- **Data de Nascimento**: Para controle de acesso
- **Telefone**: Contato alternativo

#### Passo 3: Informações Profissionais
- **Cargo**: Função na organização
- **Departamento**: Setor de atuação
- **Centro de Custo**: Para relatórios financeiros
- **Data de Admissão**: Quando iniciou na empresa

#### Passo 4: Configurações de Acesso
- **Perfil de Acesso**:
  - **Administrador**: Acesso total ao sistema
  - **Gerente**: Gerencia equipe e processos
  - **Usuário**: Acesso limitado às próprias tarefas
  - **Auditor**: Acesso apenas leitura para auditorias
  - **Visitante**: Acesso muito limitado

- **Status**: Ativo/Inativo
- **Data de Expiração**: Opcional, para acessos temporários

#### Passo 5: Configurações de Segurança
- **Exigir Troca de Senha**: Força mudança no primeiro acesso
- **Autenticação de Dois Fatores**: Recomendado para administradores
- **Bloqueio Automático**: Após tentativas falhidas

#### Passo 6: Salvar e Notificar
1. Clique em **"Salvar"**
2. O sistema gera automaticamente uma senha temporária
3. Um e-mail é enviado automaticamente com as credenciais
4. O usuário receberá instruções para primeiro acesso

### Editando Usuários Existentes

#### Localizar Usuário
1. Vá para **"Usuários"** → **"Listar Usuários"**
2. Use filtros para encontrar:
   - Por nome
   - Por departamento
   - Por status
   - Por perfil

#### Modificar Informações
1. Clique no nome do usuário
2. Altere os campos necessários
3. Salve as mudanças
4. O usuário será notificado se houver mudanças relevantes

### Desativando Usuários

#### Quando Desativar
- Funcionário demitido
- Acesso temporário expirado
- Suspensão disciplinar

#### Como Desativar
1. Abra o perfil do usuário
2. Mude **Status** para "Inativo"
3. Adicione **Motivo** da desativação
4. Salve as mudanças
5. O acesso será bloqueado imediatamente

---

## 👥 Gerenciando Equipes

### Criando uma Nova Equipe

#### Passo 1: Acesse Gestão de Equipes
1. Menu **"Equipes"** → **"Nova Equipe"**

#### Passo 2: Informações Básicas
- **Nome da Equipe**: Nome descritivo
- **Descrição**: Objetivos e responsabilidades
- **Tipo de Equipe**:
  - Operacional
  - Administrativa
  - Técnica
  - Multidisciplinar

#### Passo 3: Definir Liderança
- **Líder**: Selecione o responsável
- **Vice-Líder**: Substituto em caso de ausência
- **Coordenador**: Para equipes grandes

#### Passo 4: Adicionar Membros
1. **Buscar Usuários**: Use o campo de busca
2. **Selecionar**: Marque os usuários desejados
3. **Definir Papel**: Para cada membro
   - Líder
   - Membro Ativo
   - Consultor
   - Observador

#### Passo 5: Configurar Permissões
- **Acesso Compartilhado**: Documentos e processos
- **Nível de Visibilidade**: Interna/Externa
- **Permissões Especiais**: Aprovações, auditorias

#### Passo 6: Salvar Equipe
1. Clique em **"Criar Equipe"**
2. Todos os membros serão notificados
3. A equipe aparecerá no dashboard

### Gerenciando Equipes Existentes

#### Adicionar Novos Membros
1. Abra a equipe desejada
2. Vá para aba **"Membros"**
3. Clique **"Adicionar Membro"**
4. Selecione usuários e papéis
5. Salve as mudanças

#### Remover Membros
1. Na lista de membros, clique no **"X"** ao lado do nome
2. Confirme a remoção
3. O usuário será notificado

#### Alterar Liderança
1. Vá para **"Configurações da Equipe"**
2. Mude o **Líder** ou **Vice-Líder**
3. Salve as mudanças
4. Todos serão notificados

### Equipes Especiais

#### Equipe de Qualidade
- Responsável por auditorias e NCs
- Acesso a todos os módulos de qualidade
- Permissões especiais de aprovação

#### Equipe Técnica
- Manutenção e suporte do sistema
- Acesso a configurações avançadas
- Coordenação com desenvolvimento

#### Equipe de Gestão
- Acesso a relatórios executivos
- Aprovações de alto nível
- Configuração de políticas

---

## 🔐 Gerenciando Permissões

### Entendendo os Perfis

#### Administrador do Sistema
**Pode:**
- Gerenciar todos os usuários e equipes
- Configurar sistema e permissões
- Acessar todos os dados
- Modificar configurações críticas

**Não Pode:**
- Apenas restrições técnicas de segurança

#### Gerente
**Pode:**
- Gerenciar sua equipe
- Aprovar documentos e processos
- Visualizar relatórios da equipe
- Configurar notificações

**Restrições:**
- Não pode alterar configurações do sistema
- Acesso limitado a dados de outras equipes

#### Usuário Padrão
**Pode:**
- Criar e editar seus próprios documentos
- Participar de workflows atribuídos
- Visualizar dados relevantes
- Receber notificações

**Restrições:**
- Não pode gerenciar outros usuários
- Acesso limitado a configurações

#### Auditor
**Pode:**
- Visualizar todos os documentos
- Criar relatórios de auditoria
- Registrar não conformidades
- Acompanhar ações corretivas

**Restrições:**
- Apenas leitura, não pode modificar
- Não pode gerenciar usuários

### Configurando Permissões Avançadas

#### Permissões por Módulo
1. **Documentos**: Criar, editar, aprovar, arquivar
2. **Auditorias**: Planejar, executar, relatar
3. **NCs**: Registrar, investigar, resolver
4. **Relatórios**: Visualizar, exportar, agendar
5. **Configurações**: Sistema, usuários, equipes

#### Permissões Contextuais
- **Por Departamento**: Acesso específico
- **Por Projeto**: Equipes temporárias
- **Por Período**: Acessos temporários
- **Por Localização**: Filiais diferentes

### Administração Avançada (Apenas para Administradores)

#### Acessando o Painel de Administração
1. **Login como Admin**: Use credenciais de administrador
2. **Menu Lateral**: Clique em **"Administração"**
3. **Dashboard**: `http://localhost:5000/admin/permissions`

#### Funcionalidades de Administração Disponíveis
- **📊 Dashboard de Permissões**: Visão geral do sistema
- **⚙️ Gestão de Permissões**: Criar e gerenciar permissões
- **⏰ Acessos Temporários**: Conceder acesso limitado
- **👥 Permissões de Equipe**: Controle coletivo
- **📋 Auditoria de Acessos**: Logs de verificações
- **📊 Relatórios de Permissões**: Análise de uso

#### Como Criar Permissões Customizadas
1. **Acesse**: `/admin/permissions/manage`
2. **Novo Formulário**: Preencha informações
3. **Configurar**: Role, recurso, ação, nível
4. **Salvar**: Permissão criada automaticamente

#### Como Conceder Acesso Temporário
1. **Acesse**: `/admin/temporary-access`
2. **Selecionar Usuário**: Escolha quem receberá acesso
3. **Definir Recurso**: Documento, processo ou módulo
4. **Configurar Duração**: Horas de validade
5. **Justificar**: Motivo do acesso temporário

#### Monitorando Acessos
1. **Auditoria**: `/admin/access-audit`
2. **Filtros**: Por usuário, período, resultado
3. **Análise**: Padrões de acesso e tentativas
4. **Relatórios**: Exportar logs de segurança

---

## 📧 Notificações e Comunicação

### Configurando Notificações de Equipe

#### Tipos de Notificação
- **Novos Membros**: Quando alguém entra na equipe
- **Mudanças de Liderança**: Novos líderes
- **Tarefas Atribuídas**: Atividades para a equipe
- **Prazos Próximos**: Alertas de vencimento
- **Resultados de Auditoria**: Compartilhamento automático

#### Canais de Comunicação
- **E-mail**: Notificações individuais
- **Sistema**: Alertas no dashboard
- **Grupos**: Notificações para toda equipe
- **Mobile**: Push notifications (futuro)

### Comunicação Interna

#### Mensagens da Equipe
1. Vá para **"Equipes"** → Selecione equipe
2. Aba **"Comunicação"**
3. **"Nova Mensagem"**
4. Selecione destinatários
5. Escreva e envie

#### Anúncios Importantes
- Usar para comunicados oficiais
- Aparece destacado no dashboard
- Pode ser marcado como prioritário

---

## 📊 Relatórios de Usuários e Equipes

### Relatório de Atividades

#### Como Gerar
1. Menu **"Relatórios"** → **"Usuários e Equipes"**
2. Selecione **"Relatório de Atividades"**
3. Configure filtros:
   - Período
   - Usuário/Equipe
   - Tipo de atividade

#### Informações Incluídas
- Documentos criados/editados
- Participação em auditorias
- NCs tratadas
- Aprovações realizadas
- Tempo de atividade

### Relatório de Conformidade

#### Acesso
1. **"Relatórios"** → **"Conformidade"**
2. **"Relatório de Usuários"**

#### Métricas
- Treinamentos realizados
- Certificações válidas
- Participação em auditorias
- Conformidade com procedimentos

---

## 🔧 Solução de Problemas

### Problemas Comuns

#### Usuário Não Consegue Fazer Login
**Sintomas:**
- Erro de "usuário ou senha inválidos"
- Conta bloqueada

**Soluções:**
1. Verificar se usuário está **ativo**
2. Resetar senha se necessário
3. Desbloquear conta se bloqueada
4. Verificar data de expiração

#### Permissões Insuficientes
**Sintomas:**
- Acesso negado a funcionalidades
- Botões desabilitados

**Soluções:**
1. Verificar perfil do usuário
2. Confirmar permissões da equipe
3. Verificar configurações de acesso
4. Contatar administrador

#### Notificações Não Chegam
**Sintomas:**
- E-mails não são recebidos
- Alertas não aparecem

**Soluções:**
1. Verificar endereço de e-mail cadastrado
2. Confirmar configurações de notificação
3. Verificar pasta de spam
4. Testar envio manual

---

## 📚 Dicas e Boas Práticas

### Organização de Equipes
- **Tamanho Ideal**: 5-12 membros por equipe
- **Diversidade**: Mescle habilidades diferentes
- **Comunicação**: Reuniões regulares
- **Objetivos Claros**: Metas definidas e mensuráveis

### Gestão de Usuários
- **Onboarding**: Treinamento para novos usuários
- **Atualização Regular**: Manter dados atualizados
- **Segurança**: Senhas fortes e 2FA
- **Monitoramento**: Acompanhar atividade dos usuários

### Permissões Seguras
- **Princípio do Menor Privilégio**: Dar apenas acesso necessário
- **Revisão Regular**: Auditar permissões periodicamente
- **Documentação**: Registrar justificativas de acesso
- **Controle de Mudanças**: Aprovação para alterações

---

## 🎯 Próximos Passos

### Capacitação Avançada
1. **Configurações Avançadas**: Permissões complexas
2. **Relatórios Customizados**: Criar dashboards
3. **Integrações**: Conectar com outros sistemas
4. **Automação**: Workflows personalizados

### Suporte
- **Documentação Técnica**: Para administradores
- **Vídeos Tutoriais**: Passo-a-passo visual
- **Comunidade**: Fórum de usuários
- **Suporte Especializado**: Contato direto

---

**Dicas Rápidas:**
- Sempre mantenha dados de usuários atualizados
- Use equipes para organizar trabalho colaborativo
- Configure permissões com cuidado para segurança
- Monitore atividades regularmente
- Use notificações para manter equipe informada

## 👤 Meu Perfil - Gerenciamento Pessoal da Conta

### Visão Geral do Perfil

O **Meu Perfil** é sua central pessoal de gerenciamento de conta no Alphaclin QMS. Aqui você pode atualizar suas informações pessoais, alterar senha, configurar notificações e monitorar sua segurança.

### Acessando Seu Perfil

#### Como Acessar
1. **Faça login** no sistema
2. **Menu lateral** → Clique no ícone **👤** (Meu Perfil)
3. **URL direta**: `http://localhost:8000/auth/profile`

#### Informações Exibidas
- **Avatar personalizado**: Iniciais do seu nome
- **Nome completo** e e-mail atual
- **Perfil de acesso** (Admin, Manager, User, etc.)
- **Último login**: Data e hora do seu último acesso
- **Status da conta**: Ativo/Inativo

---

## 📝 Gerenciando Suas Informações Pessoais

### Editando Seu Perfil

#### Campos Disponíveis
- **Nome Completo**: Seu nome completo (obrigatório)
- **E-mail**: Endereço para notificações (obrigatório)
- **Telefone**: Contato alternativo (opcional)
- **CPF**: Documento de identificação (opcional)

#### Como Editar
1. Acesse **Meu Perfil**
2. Seção **"Informações Pessoais"**
3. Altere os campos desejados
4. Clique em **"Atualizar Informações"**
5. ✅ Dados salvos automaticamente

#### Validações Automáticas
- **Nome**: Mínimo 3 caracteres
- **E-mail**: Formato válido e único no sistema
- **CPF**: Validação completa de CPF brasileiro
- **Telefone**: Formato válido (10 ou 11 dígitos)

---

## 🔐 Gerenciando Sua Senha

### Alterando Sua Senha

#### Método 1: Pelo Perfil (Recomendado)
1. Acesse **Meu Perfil**
2. Seção **"Alterar Senha"**
3. Preencha:
   - **Senha Atual**: Sua senha atual
   - **Nova Senha**: Mínimo 6 caracteres
   - **Confirmar Nova Senha**: Repetir nova senha
4. Clique em **"Alterar Senha"**

#### Método 2: Redefinição por E-mail
1. Página de login → **"Esqueceu sua senha?"**
2. Digite seu **e-mail cadastrado**
3. Clique em **"Enviar instruções"**
4. Verifique seu **e-mail**
5. Clique no link de redefinição
6. Defina **nova senha**

#### Recursos de Segurança
- **Validação obrigatória**: Senha atual necessária para alteração
- **Confirmação dupla**: Nova senha deve ser digitada duas vezes
- **Comprimento mínimo**: 6 caracteres obrigatórios
- **Logs de auditoria**: Todas as alterações são registradas

---

## 🔔 Configurando Suas Notificações

### Preferências de Notificação

#### Tipos Disponíveis
- **E-mail habilitado**: Receber notificações por e-mail
- **Documentos**: Aprovações, novos documentos, alterações
- **Auditorias e NCs**: Novas auditorias, não conformidades
- **CAPA**: Planos de ação corretiva e preventiva
- **Operacional**: CIPA, melhorias, eventos operacionais
- **Sistema**: Avisos técnicos, manutenções, atualizações

#### Como Configurar
1. Acesse **Meu Perfil**
2. Seção **"Notificações"**
3. Marque/desmarque as opções desejadas
4. Clique em **"Salvar Preferências"**

#### Controle Granular
- **Habilitar/Desabilitar**: Controle geral por tipo
- **Frequência**: Imediato, diário ou semanal (futuro)
- **Canais**: E-mail, sistema, push (expansível)

---

## 🔒 Monitorando Sua Segurança

### Página de Segurança

#### Acesso
1. **Meu Perfil** → **"Configurações de Segurança"**
2. **URL direta**: `http://localhost:8000/auth/security`

#### Informações Disponíveis

##### Atividades Recentes
- **Histórico de ações**: Últimas operações realizadas
- **Data e hora**: Quando cada ação ocorreu
- **Endereço IP**: Origem dos acessos
- **Tipo de operação**: Login, alteração de perfil, etc.

##### Tentativas de Login
- **Logins bem-sucedidos**: ✅ Acesso autorizado
- **Tentativas falhadas**: ❌ Credenciais incorretas
- **Padrões suspeitos**: Múltiplas tentativas
- **Origem geográfica**: IP de acesso

##### Configurações de Segurança (Futuras)
- **Autenticação de Dois Fatores (2FA)**
- **Sessões ativas**: Dispositivos conectados
- **Alertas de segurança**: Notificações de atividades suspeitas

---

## 🚨 Redefinição de Senha - Guia Completo

### Quando Usar
- **Esqueceu a senha**: Não consegue fazer login
- **Primeiro acesso**: Conta criada por administrador
- **Suspeita de comprometimento**: Alteração por segurança
- **Política de segurança**: Renovação periódica obrigatória

### Processo de Redefinição

#### Passo 1: Solicitar Redefinição
1. **Página de login**: `http://localhost:8000`
2. Clique em **"Esqueceu sua senha?"**
3. Digite seu **e-mail cadastrado**
4. Clique em **"Enviar instruções"**
5. ✅ **E-mail automático** enviado

#### Passo 2: Verificar E-mail
- **Caixa de entrada**: Procure e-mail da Alphaclin QMS
- **Assunto**: "Redefinição de Senha - Alphaclin QMS"
- **Conteúdo**: Link seguro e instruções
- **Validade**: Link expira em 1 hora

#### Passo 3: Definir Nova Senha
1. Clique no **link do e-mail**
2. Página de redefinição será aberta
3. Digite sua **nova senha**
4. **Confirme** a nova senha
5. Clique em **"Redefinir senha"**
6. ✅ **Senha alterada** com sucesso

#### Passo 4: Fazer Login
1. Volte para **página de login**
2. Use suas **novas credenciais**
3. ✅ **Acesso liberado**

### Recursos de Segurança

#### Tokens Seguros
- **Únicos**: Cada solicitação gera token diferente
- **Temporários**: Válidos por apenas 1 hora
- **Uso único**: Não podem ser reutilizados
- **Criptografados**: Links seguros e protegidos

#### E-mail Profissional
```html
Assunto: Redefinição de Senha - Alphaclin QMS

Olá [Seu Nome],

Você solicitou a redefinição de sua senha no Alphaclin QMS.

Clique no link abaixo para definir uma nova senha:

[Redefinir Senha] (link seguro com token)

Este link expira em 1 hora por motivos de segurança.

Atenciosamente,
Equipe Alphaclin QMS
```

#### Auditoria Completa
- **Logs imutáveis**: Todas as ações são registradas
- **Detalhes contextuais**: IP, data/hora, user-agent
- **Cadeia de blocos**: Integridade garantida
- **Conformidade**: Atende requisitos de auditoria

---

## 📊 Relatórios Pessoais

### Meu Histórico de Atividades

#### Como Acessar
1. **Meu Perfil** → **"Configurações de Segurança"**
2. Visualize suas **atividades recentes**

#### Informações Incluídas
- **Operações realizadas**: Documentos, auditorias, NCs
- **Datas e horários**: Timeline completo
- **Status das ações**: Sucesso, erro, pendente
- **Impacto no sistema**: Alterações significativas

### Monitoramento de Segurança

#### Alertas Automáticos
- **Múltiplas tentativas**: Notificação de possíveis ataques
- **Acesso suspeito**: IPs diferentes ou horários incomuns
- **Mudanças críticas**: Alterações em configurações importantes

#### Boas Práticas
- **Verificação regular**: Monitore suas atividades mensalmente
- **Alertas de segurança**: Configure notificações para atividades suspeitas
- **Logs de auditoria**: Mantenha registros para conformidade

---

## 🔧 Solução de Problemas - Perfil

### Problemas Comuns

#### Não Consigo Acessar Meu Perfil
**Sintomas:**
- Erro 404 ao acessar `/auth/profile`
- Ícone de perfil não aparece no menu

**Soluções:**
1. **Verifique login**: Certifique-se de estar logado
2. **Permissões**: Alguns perfis podem ter acesso limitado
3. **Cache do navegador**: Limpe cache e cookies
4. **Recarregue a página**: Pressione Ctrl+F5

#### Dados Não Estão Sendo Salvos
**Sintomas:**
- Alterações não persistem
- Mensagens de erro ao salvar

**Soluções:**
1. **Campos obrigatórios**: Preencha nome e e-mail
2. **Validações**: Verifique formato de CPF/telefone
3. **Conflitos**: E-mail já usado por outro usuário
4. **Permissões**: Verifique se tem acesso de escrita

#### Notificações Não Funcionam
**Sintomas:**
- Não recebo e-mails de atualização
- Preferências não são aplicadas

**Soluções:**
1. **E-mail válido**: Verifique endereço cadastrado
2. **Configurações**: Habilite notificações desejadas
3. **Pasta de spam**: Verifique lixo eletrônico
4. **Servidor de e-mail**: Teste configuração SMTP

#### Esqueci Minha Senha
**Sintomas:**
- Não consigo fazer login
- Não lembro credenciais

**Soluções:**
1. **Redefinição por e-mail**: Use "Esqueceu sua senha?"
2. **Contato administrador**: Peça reset pelo admin
3. **Dados de recuperação**: Use e-mail alternativo
4. **Suporte técnico**: Entre em contato com TI

---

## 📚 Dicas e Boas Práticas - Perfil

### Manutenção do Perfil
- **Atualização regular**: Mantenha dados sempre atualizados
- **E-mail válido**: Use endereço que você verifica diariamente
- **Telefone alternativo**: Para recuperações de emergência
- **Monitoramento ativo**: Verifique atividades regularmente

### Segurança da Conta
- **Senhas fortes**: Combine letras, números e símbolos
- **Alteração periódica**: Mude senha a cada 90 dias
- **Não compartilhar**: Mantenha credenciais pessoais
- **Logout seguro**: Sempre saia ao terminar uso

### Notificações Eficientes
- **Seletividade**: Habilite apenas notificações relevantes
- **Organização**: Use filtros para gerenciar volume
- **Canais adequados**: Escolha e-mail para itens importantes
- **Feedback**: Ajuste preferências baseado na experiência

### Conformidade e Auditoria
- **Dados corretos**: Mantenha informações precisas
- **Logs preservados**: Não exclua históricos importantes
- **Políticas atendidas**: Siga normas de segurança da empresa
- **Documentação**: Registre mudanças significativas

---

## 🎯 Recursos Avançados

### Integrações Futuras
- **Autenticação de Dois Fatores (2FA)**
- **Biometria**: Reconhecimento facial/digital
- **Single Sign-On (SSO)**
- **Redes sociais**: Login com Google/Microsoft

### Personalização
- **Temas visuais**: Cores e layouts personalizados
- **Dashboards customizados**: Widgets pessoais
- **Atalhos de teclado**: Acesso rápido às funções
- **Layouts salvos**: Configurações por dispositivo

### Análise Pessoal
- **Métricas de uso**: Tempo no sistema, ações realizadas
- **Produtividade**: Documentos criados, tarefas concluídas
- **Colaboração**: Interações com equipe
- **Tendências**: Padrões de uso ao longo do tempo

---

## 📞 Suporte e Ajuda

### Canais de Suporte
- **📧 E-mail**: suporte@alphaclin.com
- **📱 WhatsApp**: +55 11 99999-9999
- **💬 Chat interno**: Sistema de mensagens
- **📋 Central de ajuda**: Base de conhecimento

### Documentação Relacionada
- **[Guia do Usuário](../user-guide/)**: Funcionalidades básicas
- **[Guia Administrativo](../../development/)**: Configurações avançadas
- **[Solução de Problemas](../../installation/troubleshooting.md)**: Problemas comuns
- **[API Documentation](../../api/)**: Integrações técnicas

### Treinamento
- **Vídeos tutoriais**: Passo-a-passo visual
- **Webinars mensais**: Treinamentos ao vivo
- **Certificações**: Cursos de capacitação
- **Comunidade**: Fórum de usuários e especialistas

---

**Dicas Rápidas:**
- Mantenha seu perfil sempre atualizado
- Use a redefinição de senha quando necessário
- Configure notificações conforme sua rotina
- Monitore regularmente sua segurança
- Aproveite todos os recursos disponíveis

**Precisa de ajuda?** Entre em contato com o administrador do sistema ou consulte a documentação completa.