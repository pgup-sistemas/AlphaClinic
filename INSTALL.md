# 🚀 Alphaclin QMS - Guia de Instalação

Este guia fornece instruções completas para instalar e configurar o **Sistema Alphaclin QMS** (Quality Management System).

## 📋 Pré-requisitos

### Sistema Operacional
- **Windows 10/11**
- **Linux** (Ubuntu/Debian/CentOS)
- **macOS**

### Python
- **Python 3.8 ou superior**
- **pip** (gerenciador de pacotes)

### Banco de Dados (Opcional)
- **PostgreSQL 12+** (para produção)
- **SQLite** (incluído por padrão para desenvolvimento)

## 🛠️ Instalação Rápida

### Passo 1: Clonar o Repositório
```bash
git clone <repository-url>
cd alphaclin-qms
```

### Passo 2: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 3: Configurar Ambiente
```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar .env conforme necessário
# Para desenvolvimento: manter SQLite (padrão)
# Para produção: configurar PostgreSQL
```

### Passo 4: Inicializar Banco de Dados
```bash
# Criar tabelas e dados iniciais
python app.py
```

**Aguarde a mensagem:** `Admin user created with username: admin, password: admin123`

### Passo 5: Configurar E-mail (Opcional)
```bash
# Criar templates de e-mail
flask create-email-templates
```

### Passo 6: Executar Sistema
```bash
python app.py
```

### Passo 7: Acessar Sistema
- **URL:** `http://localhost:5000`
- **Usuário:** `admin`
- **Senha:** `admin123`

## 📧 Configuração de E-mail

### Gmail (Recomendado)
1. **Ativar autenticação de 2 fatores** na conta Gmail
2. **Gerar senha de app:**
   - Acesse: https://myaccount.google.com/apppasswords
   - Criar senha para "Alphaclin QMS"
3. **Configurar no .env:**
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=senha-gerada-pelo-app
MAIL_DEFAULT_SENDER=noreply@alphaclinic.com
```

### Outlook/Hotmail
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@outlook.com
MAIL_PASSWORD=sua-senha
MAIL_DEFAULT_SENDER=noreply@alphaclinic.com
```

### Testar Configuração
```bash
# Processar fila de e-mails
flask process-emails
```

## 🐘 Configuração PostgreSQL (Produção)

### Instalar PostgreSQL

#### Windows
1. Baixar: https://www.postgresql.org/download/windows/
2. Instalar com configurações padrão
3. Criar banco: `alphaclin_qms`

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb alphaclin_qms
```

#### Docker
```bash
docker run --name postgres-qms \
  -e POSTGRES_DB=alphaclin_qms \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 -d postgres:13
```

### Migrar para PostgreSQL
```bash
# 1. Configurar .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/alphaclin_qms

# 2. Testar conexão
python migrate_to_postgres.py test

# 3. Executar migração
python migrate_to_postgres.py
```

## 👥 Gerenciamento de Usuários

### Criar Primeiro Admin
O sistema cria automaticamente um usuário admin na primeira execução:

- **Usuário:** `admin`
- **Senha:** `admin123`
- **Email:** `admin@alphaclinic.com`

### Criar Novos Usuários
1. **Logar como admin**
2. **Ir para:** `Usuários → Criar`
3. **Definir:** nome, e-mail, senha, função
4. **Atribuir:** equipes e permissões

### Funções Disponíveis
- **Admin:** Acesso completo ao sistema
- **Manager:** Gerenciamento de usuários e processos
- **Auditor:** Acesso a auditorias e NCs
- **Reviewer:** Revisão de documentos
- **User:** Acesso básico

## 🔧 Comandos Úteis

### Flask CLI
```bash
# Criar templates de e-mail
flask create-email-templates

# Processar fila de e-mails
flask process-emails

# Mostrar rotas disponíveis
flask routes
```

### Gerenciamento de Banco
```bash
# Criar migração
flask db migrate -m "descrição da mudança"

# Aplicar migração
flask db upgrade

# Reverter migração
flask db downgrade
```

### Desenvolvimento
```bash
# Executar com debug
FLASK_ENV=development flask run

# Executar em porta específica
flask run --host=0.0.0.0 --port=8000
```

## 🚀 Deploy em Produção

### Usando Gunicorn
```bash
# Instalar gunicorn
pip install gunicorn

# Executar
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

### Usando Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

```bash
# Construir e executar
docker build -t alphaclin-qms .
docker run -p 5000:5000 alphaclin-qms
```

## 🔍 Solução de Problemas

### Erro: "Porta já em uso"
```bash
# Matar processo na porta 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Erro: "Banco não existe"
```bash
# Para PostgreSQL
createdb alphaclin_qms

# Para SQLite: será criado automaticamente
```

### Erro: "E-mail não enviado"
```bash
# Verificar configurações no .env
# Testar conexão SMTP manualmente
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('user@gmail.com', 'app-password')
print('SMTP OK')
"
```

### Erro: "Módulo não encontrado"
```bash
# Reinstalar dependências
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

## 📊 Verificação da Instalação

### Checklist de Instalação
- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Banco de dados criado
- [ ] Sistema executando em localhost:5000
- [ ] Login admin funcionando
- [ ] E-mail configurado (opcional)

### Testes Funcionais
1. **Login:** admin / admin123
2. **Criar documento:** Documentos → Criar
3. **Aprovar documento:** Deve enviar e-mail
4. **Criar NC:** Não Conformidades → Criar
5. **Criar CAPA:** Deve enviar e-mail
6. **Ver relatórios:** Relatórios → Dashboard

## 📞 Suporte

Para problemas de instalação ou configuração:

1. **Verificar logs:** Arquivo de log da aplicação
2. **Testar componentes:** Executar comandos individualmente
3. **Verificar versões:** `python --version` e `pip list`
4. **Documentação:** README.md para funcionalidades

---

## 🎯 Resumo dos Comandos Essenciais

```bash
# Instalação
git clone <repo>
cd alphaclin-qms
pip install -r requirements.txt
cp .env.example .env

# Configuração
python app.py  # Cria admin automaticamente

# E-mail (opcional)
flask create-email-templates

# Execução
python app.py

# Acesso
# URL: http://localhost:5000
# User: admin
# Pass: admin123
```

**Sistema Alphaclin QMS instalado e funcionando!** 🚀🏥