# ⚙️ Configuração - AlphaClinic QMS

## Visão Geral

Este guia detalha todas as opções de configuração disponíveis no AlphaClinic QMS, incluindo variáveis de ambiente, arquivos de configuração e personalizações avançadas.

## 📄 Arquivo de Configuração Principal

O arquivo `.env` é o principal ponto de configuração do sistema.

### Configurações Essenciais

#### Ambiente de Aplicação
```bash
# Ambiente da aplicação
FLASK_ENV=production          # development, testing, production
FLASK_APP=app.py             # Arquivo principal da aplicação
SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria-aqui
```

#### Banco de Dados
```bash
# PostgreSQL (Produção)
DATABASE_URL=postgresql://usuario:senha@localhost:5432/alphaclin_qms

# SQLite (Desenvolvimento)
DATABASE_URL=sqlite:///instance/alphaclin_qms.db

# Configurações adicionais
DB_POOL_SIZE=10              # Tamanho do pool de conexões
DB_MAX_OVERFLOW=20           # Conexões extras permitidas
DB_POOL_TIMEOUT=30           # Timeout do pool em segundos
```

#### Segurança
```bash
# JWT para autenticação
JWT_SECRET_KEY=outra-chave-secreta-para-jwt
JWT_ACCESS_TOKEN_EXPIRES=3600    # 1 hora em segundos
JWT_REFRESH_TOKEN_EXPIRES=86400  # 24 horas em segundos

# Senhas
BCRYPT_LOG_ROUNDS=12         # Rounds para hash de senha

# Rate Limiting
API_RATE_LIMIT=1000          # Requisições por hora por API Key
RATE_LIMIT_PER_MINUTE=100    # Requisições por minuto por IP

# CORS
CORS_ORIGINS=http://localhost:3000,https://app.alphaclin.com
```

#### Email
```bash
# Configuração SMTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
MAIL_DEFAULT_SENDER=noreply@alphaclin.com

# Configurações avançadas
MAIL_MAX_EMAILS=100          # Emails por dia
MAIL_SUPPRESS_SEND=false     # true para desabilitar envio
ADMINS=admin@alphaclin.com,manager@alphaclin.com
```

#### Upload de Arquivos
```bash
# Limites de upload
MAX_CONTENT_LENGTH=16777216  # 16MB em bytes
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=pdf,doc,docx,xls,xlsx,ppt,pptx,txt,jpg,jpeg,png

# Processamento de imagens
MAX_IMAGE_SIZE=1920x1080     # Resolução máxima
IMAGE_QUALITY=85             # Qualidade de compressão
```

### Configurações Avançadas

#### Cache
```bash
# Redis (Recomendado para produção)
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300    # 5 minutos

# Configuração simples (memória)
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300
```

#### Logging
```bash
# Nível de logging
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json              # text ou json
LOG_FILE=logs/alphaclin_qms.log

# Rotação de logs
LOG_MAX_SIZE=10485760        # 10MB
LOG_BACKUP_COUNT=5           # Número de arquivos de backup

# Sentry (Monitoramento de erros)
SENTRY_DSN=https://sua-chave@sentry.io/projeto-id
SENTRY_ENVIRONMENT=production
```

#### Internacionalização
```bash
# Idioma padrão
BABEL_DEFAULT_LOCALE=pt_BR
BABEL_DEFAULT_TIMEZONE=America/Sao_Paulo

# Timezone suportados
SUPPORTED_TIMEZONES=America/Sao_Paulo,America/Manaus,America/Fortaleza
```

#### Integrações Externas
```bash
# WhatsApp (quando implementado)
WHATSAPP_TOKEN=sua-chave-whatsapp
WHATSAPP_VERIFY_TOKEN=seu-token-de-verificacao

# APIs externas
EXTERNAL_API_TIMEOUT=30      # Timeout em segundos
EXTERNAL_API_RETRIES=3       # Número de tentativas

# Webhooks
WEBHOOK_TIMEOUT=10           # Timeout para webhooks
WEBHOOK_RETRIES=3            # Tentativas de webhook
```

## 🔧 Arquivos de Configuração

### config.py

Arquivo principal de configuração Python com classes de configuração.

```python
import os
from datetime import timedelta

class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'

    # Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'INFO'

    # Configurações específicas de produção
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30))
    }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
```

### pyproject.toml

Configurações do projeto Python e dependências.

```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

## 🔒 Configurações de Segurança

### Headers de Segurança
```bash
# No Nginx ou aplicação
SECURE_HEADERS=true
SECURE_HSTS_SECONDS=31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS=true
SECURE_HSTS_PRELOAD=true
```

### Configurações de Sessão
```bash
# Sessão segura
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE='Lax'
PERMANENT_SESSION_LIFETIME=86400  # 24 horas
```

### Configurações de API
```bash
# API Keys válidas
VALID_API_KEYS=key1,key2,key3,key4,key5

# Rate limiting por API key
API_KEY_RATE_LIMITS='{"key1": 5000, "key2": 1000, "default": 100}'

# Timeouts
API_TIMEOUT=30
API_KEY_EXPIRY_DAYS=365
```

## 🌐 Configurações de Rede

### Proxy e Load Balancer
```bash
# Detecção de proxy
PROXY_FIX=true
PREFERRED_URL_SCHEME=https

# Headers confiáveis
TRUSTED_PROXIES=192.168.1.0/24,10.0.0.0/8
REAL_IP_HEADER=X-Real-IP
```

### Configurações de Porta
```bash
# Porta do servidor
PORT=5000

# Bind address
HOST=0.0.0.0  # Todas as interfaces

# Para desenvolvimento
HOST=127.0.0.1
```

## 📊 Configurações de Monitoramento

### Métricas e Health Checks
```bash
# Health check endpoint
HEALTH_CHECK_PATH=/health

# Métricas Prometheus
PROMETHEUS_METRICS=true
METRICS_PATH=/metrics

# Status page
STATUS_PAGE=true
```

### Notificações de Alerta
```bash
# Email de alertas
ALERT_EMAILS=devops@alphaclin.com,admin@alphaclin.com

# Webhooks de alerta
ALERT_WEBHOOKS=https://your-webhook-service.com/webhook

# Thresholds de alerta
HIGH_ERROR_RATE_THRESHOLD=0.05  # 5%
HIGH_RESPONSE_TIME_THRESHOLD=5000  # 5 segundos
```

## 🔄 Configurações de Backup

### Backup Automático
```bash
# Frequência de backup
BACKUP_FREQUENCY_HOURS=24

# Retenção de backups
BACKUP_RETENTION_DAYS=30

# Diretórios de backup
BACKUP_DATABASE_PATH=/backup/database
BACKUP_FILES_PATH=/backup/files
BACKUP_CONFIG_PATH=/backup/config
```

### Compressão e Encriptação
```bash
# Compressão
BACKUP_COMPRESSION=gzip
BACKUP_COMPRESSION_LEVEL=6

# Encriptação
BACKUP_ENCRYPTION=true
BACKUP_ENCRYPTION_KEY=sua-chave-de-encriptacao
```

## 🛠️ Configurações de Desenvolvimento

### Debug e Desenvolvimento
```bash
# Debug
DEBUG=true
DEBUG_TB_ENABLED=true
DEBUG_TB_INTERCEPT_REDIRECTS=false

# Hot reload
TEMPLATES_AUTO_RELOAD=true
SEND_FILE_MAX_AGE_DEFAULT=0

# SQL Echo (verbose SQL logging)
SQLALCHEMY_ECHO=false
```

### Testes
```bash
# Configurações de teste
TESTING=true
TEST_DATABASE_URL=sqlite:///:memory:
TEST_LOG_LEVEL=WARNING

# Coverage
COVERAGE_MIN_PERCENTAGE=80
COVERAGE_EXCLUDE_PATTERNS=tests/*,*/migrations/*
```

## 📱 Configurações de Interface

### Tema e Aparência
```bash
# Tema padrão
DEFAULT_THEME=light

# Temas disponíveis
AVAILABLE_THEMES=light,dark,auto

# Cores personalizadas
PRIMARY_COLOR=#007bff
SECONDARY_COLOR=#6c757d
```

### Idioma e Localização
```bash
# Idioma padrão
DEFAULT_LANGUAGE=pt_BR

# Idiomas suportados
SUPPORTED_LANGUAGES=pt_BR,en_US,es_ES

# Formato de data/hora
DATETIME_FORMAT=%d/%m/%Y %H:%M:%S
DATE_FORMAT=%d/%m/%Y
TIME_FORMAT=%H:%M:%S
```

## 🔧 Comandos de Gerenciamento

### Flask CLI
```bash
# Inicializar banco de dados
flask db init

# Criar migração
flask db migrate -m "descrição da mudança"

# Aplicar migração
flask db upgrade

# Reverter migração
flask db downgrade

# Criar usuário admin
flask create-admin

# Popular dados de exemplo
flask db-seed

# Executar testes
flask test

# Verificar saúde do sistema
flask health-check
```

### Scripts Customizados
```bash
# Backup
python scripts/backup.py

# Restore
python scripts/restore.py backup_file.sql

# Limpeza de dados antigos
python scripts/cleanup.py --days 30

# Relatório de uso
python scripts/usage_report.py
```

## 🔍 Variáveis de Ambiente por Ambiente

### Desenvolvimento
```bash
FLASK_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///instance/alphaclin_qms.db
MAIL_SUPPRESS_SEND=true
```

### Testes
```bash
FLASK_ENV=testing
TESTING=true
LOG_LEVEL=WARNING
DATABASE_URL=sqlite:///:memory:
WTF_CSRF_ENABLED=false
```

### Produção
```bash
FLASK_ENV=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://usuario:senha@host:5432/banco
MAIL_SUPPRESS_SEND=false
REDIS_URL=redis://localhost:6379/0
```

## 🚨 Configurações Sensíveis

### Variáveis que NÃO devem ser versionadas
```bash
# Nunca commite estas variáveis
SECRET_KEY
JWT_SECRET_KEY
DATABASE_PASSWORD
MAIL_PASSWORD
API_KEYS
ENCRYPTION_KEYS
```

### Arquivo .env.example
Mantenha sempre atualizado o arquivo `.env.example` com todas as variáveis necessárias, usando valores de exemplo.

## 📞 Suporte e Troubleshooting

### Verificar Configuração
```bash
# Verificar se todas as variáveis estão carregadas
python -c "import os; print('Variáveis carregadas:', len([k for k in os.environ.keys() if k.startswith('FLASK') or k.startswith('DB')]))"

# Testar conexão com banco
python -c "from app import db; db.create_all()"

# Verificar configurações carregadas
python -c "from app import app; print('Config:', app.config)"
```

### Logs de Configuração
```bash
# Verificar logs de inicialização
tail -f logs/alphaclin_qms.log | grep -i "config\|error"

# Logs específicos de configuração
grep "CONFIG" logs/alphaclin_qms.log
```

---

**Última atualização:** Dezembro 2024
**Versão:** 1.0.0