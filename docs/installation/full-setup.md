# 🛠️ Instalação Completa - AlphaClinic QMS

## Visão Geral

Este guia fornece instruções detalhadas para uma instalação completa do AlphaClinic QMS, incluindo configuração de produção, banco de dados PostgreSQL e configurações avançadas.

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- **Windows**: Windows 10+, Windows Server 2019+
- **macOS**: macOS 11.0+

### Recursos Mínimos
- **CPU**: 2 núcleos
- **RAM**: 4 GB
- **Armazenamento**: 20 GB
- **Rede**: Conexão estável com internet

### Software Necessário
- **Python**: 3.8 ou superior
- **PostgreSQL**: 12 ou superior (recomendado)
- **Git**: 2.20 ou superior
- **Node.js**: 16+ (para assets estáticos)
- **Redis**: 6+ (opcional, para cache)

## 🚀 Instalação Passo a Passo

### 1. Clone o Repositório

```bash
# Navegue até o diretório desejado
cd /opt

# Clone o repositório
git clone https://github.com/alphaclin/qms.git
cd qms

# Verifique a branch/tag desejada
git checkout v1.0.0
```

### 2. Configuração do Ambiente Python

#### Criação do Ambiente Virtual
```bash
# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Atualize o pip
pip install --upgrade pip
```

#### Instalação das Dependências
```bash
# Instale as dependências do projeto
pip install -r requirements.txt

# Para produção, instale também as dependências de desenvolvimento
pip install -r requirements-dev.txt
```

### 3. Configuração do Banco de Dados

#### PostgreSQL (Recomendado)

```bash
# Instalar PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Instalar PostgreSQL (CentOS/RHEL)
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb

# Iniciar serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar banco de dados e usuário
sudo -u postgres psql

# No prompt do PostgreSQL:
CREATE DATABASE alphaclin_qms;
CREATE USER alphaclin_user WITH PASSWORD 'sua_senha_segura_aqui';
GRANT ALL PRIVILEGES ON DATABASE alphaclin_qms TO alphaclin_user;
ALTER USER alphaclin_user CREATEDB;
\q
```

#### SQLite (Desenvolvimento)
Para desenvolvimento rápido, o SQLite é usado por padrão. Nenhum configuração adicional necessária.

### 4. Configuração de Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
nano .env  # Linux/macOS
notepad .env  # Windows
```

#### Variáveis Essenciais
```bash
# Ambiente
FLASK_ENV=production
FLASK_APP=app.py

# Banco de dados
DATABASE_URL=postgresql://alphaclin_user:sua_senha_segura_aqui@localhost:5432/alphaclin_qms

# Para SQLite (desenvolvimento)
# DATABASE_URL=sqlite:///instance/alphaclin_qms.db

# Segurança
SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria-aqui
JWT_SECRET_KEY=outra-chave-secreta-para-jwt

# API Keys válidas (separadas por vírgula)
VALID_API_KEYS=chave-api-1,chave-api-2,chave-api-3

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app

# Rate Limiting
API_RATE_LIMIT=1000

# Upload de arquivos
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/alphaclin_qms.log
```

### 5. Inicialização do Banco de Dados

```bash
# Execute as migrações
flask db upgrade

# Para PostgreSQL, inicialize com dados de exemplo (opcional)
flask db-seed

# Para desenvolvimento, crie dados básicos
flask create-admin
```

### 6. Configuração de Assets Estáticos

```bash
# Instalar Node.js dependencies
npm install

# Build dos assets
npm run build

# Para desenvolvimento com hot reload
npm run dev
```

### 7. Configuração de Serviços do Sistema

#### Systemd (Linux)
```bash
# Crie o arquivo de serviço
sudo nano /etc/systemd/system/alphaclin-qms.service

# Conteúdo do arquivo:
[Unit]
Description=AlphaClinic QMS
After=network.target postgresql.service

[Service]
Type=simple
User=alphaclin
Group=alphaclin
WorkingDirectory=/opt/qms
Environment=PATH=/opt/qms/venv/bin
ExecStart=/opt/qms/venv/bin/gunicorn --config gunicorn.conf.py app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

# Recarregue o systemd e inicie o serviço
sudo systemctl daemon-reload
sudo systemctl start alphaclin-qms
sudo systemctl enable alphaclin-qms
```

#### Windows Service (Opcional)
```powershell
# Use NSSM ou similar para criar serviço Windows
nssm install AlphaClinicQMS "C:\Python39\python.exe" "C:\qms\run.py"
nssm set AlphaClinicQMS AppDirectory "C:\qms"
nssm set AlphaClinicQMS Start SERVICE_AUTO_START
nssm start AlphaClinicQMS
```

### 8. Configuração de Proxy Reverso (Nginx)

```bash
# Instalar Nginx
sudo apt-get install nginx

# Criar configuração do site
sudo nano /etc/nginx/sites-available/alphaclin-qms

# Conteúdo do arquivo:
server {
    listen 80;
    server_name qms.alphaclin.com;

    client_max_body_size 32M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Servir arquivos estáticos diretamente
    location /static {
        alias /opt/qms/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logs de erro e acesso
    error_log /var/log/nginx/alphaclin_qms_error.log;
    access_log /var/log/nginx/alphaclin_qms_access.log;
}

# Ative o site
sudo ln -s /etc/nginx/sites-available/alphaclin-qms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9. Configuração de SSL (HTTPS)

#### Certbot (Let's Encrypt)
```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d qms.alphaclin.com

# Renovação automática já configurada
sudo systemctl status certbot.timer
```

### 10. Configuração de Backup

```bash
# Criar script de backup
sudo nano /opt/qms/scripts/backup.sh

# Conteúdo do script:
#!/bin/bash
BACKUP_DIR="/backup/alphaclin-qms"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup do banco de dados
pg_dump -h localhost -U alphaclin_user alphaclin_qms > $BACKUP_DIR/db_backup_$DATE.sql

# Backup dos uploads
tar -czf $BACKUP_DIR/uploads_backup_$DATE.tar.gz /opt/qms/uploads/

# Manter apenas últimos 7 dias
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -type f -name "*.tar.gz" -mtime +7 -delete

# Execute o backup
chmod +x /opt/qms/scripts/backup.sh
/opt/qms/scripts/backup.sh
```

## 🔧 Configurações Avançadas

### Cache com Redis

```bash
# Instalar Redis
sudo apt-get install redis-server

# Configurar no .env
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis
```

### Monitoramento com Prometheus

```bash
# Adicionar métricas no código
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Configurar scraping no Prometheus
# Veja development/monitoring.md para detalhes completos
```

### Configuração de Logs Estruturados

```bash
# No .env
LOG_FORMAT=json
LOG_LEVEL=INFO
SENTRY_DSN=https://sua-chave@sentry.io/projeto-id
```

## 🧪 Verificação da Instalação

### Testes Básicos

```bash
# Teste de saúde
curl http://localhost:5000/api/v1/integrations/health

# Acesso à aplicação
# Abra http://localhost:5000 no navegador

# Acesso à documentação
# Abra http://localhost:5000/docs no navegador
```

### Testes Automatizados

```bash
# Execute os testes
pytest tests/ -v

# Cobertura de testes
coverage run -m pytest
coverage report -m
```

## 🔍 Solução de Problemas

### Problemas Comuns

#### Erro de Conexão com Banco de Dados
```bash
# Verifique se PostgreSQL está rodando
sudo systemctl status postgresql

# Teste conexão manual
psql -h localhost -U alphaclin_user -d alphaclin_qms

# Verifique logs da aplicação
tail -f logs/alphaclin_qms.log
```

#### Problemas de Permissão
```bash
# Ajuste permissões de arquivos
sudo chown -R alphaclin:alphaclin /opt/qms

# Permissões de diretórios
chmod -R 755 /opt/qms
chmod -R 777 /opt/qms/instance
chmod -R 777 /opt/qms/uploads
chmod -R 777 /opt/qms/logs
```

#### Problemas de Memória
```bash
# Monitore uso de memória
htop

# Ajuste configuração do Gunicorn
# workers = multiprocessing.cpu_count() * 2 + 1
# No arquivo gunicorn.conf.py
```

## 📞 Suporte

Em caso de problemas durante a instalação:

1. **Logs**: Verifique os logs em `logs/alphaclin_qms.log`
2. **Documentação**: Consulte este guia e guias específicos
3. **Comunidade**: [GitHub Issues](https://github.com/alphaclin/qms/issues)
4. **Suporte**: suporte@alphaclin.com

## 🔄 Próximos Passos

Após instalação bem-sucedida:

1. ✅ Configure usuários iniciais
2. ✅ Personalize configurações da organização
3. ✅ Importe dados existentes (se aplicável)
4. ✅ Configure backups automáticos
5. ✅ Treine a equipe
6. ✅ Configure monitoramento

---

**Última atualização:** Dezembro 2024
**Versão:** 1.0.0