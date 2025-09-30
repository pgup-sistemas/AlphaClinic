# Instalação Rápida - Alphaclin QMS

## 🚀 Instalação Automática (Recomendado)

### Pré-requisitos

- **Python 3.8 ou superior**
- **Git** (para clonar o repositório)
- **PostgreSQL 12+** (opcional, SQLite é usado por padrão)

### Passos de Instalação

#### 1. Clone o Repositório
```bash
git clone <repository-url>
cd alphaclin-qms
```

#### 2. Execute o Setup Automático
```bash
python setup.py
```

**O que o setup faz automaticamente:**
- ✅ Instala todas as dependências Python
- ✅ Cria ambiente virtual (venv)
- ✅ Configura banco de dados SQLite
- ✅ Executa migrações
- ✅ Cria usuário administrador
- ✅ Insere dados de exemplo

#### 3. Inicie o Servidor
```bash
python app.py
```

#### 4. Primeiro Acesso
- **URL**: `http://localhost:5000`
- **Usuário**: `admin`
- **Senha**: `admin123`

---

## 🛠️ Instalação Manual (Avançado)

### Passo 1: Criar Ambiente Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### Passo 2: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 3: Configurar Banco de Dados

#### Opção A: SQLite (Padrão - Recomendado)
```bash
# O sistema cria automaticamente o arquivo instance/alphaclin_qms.db
# Não é necessária configuração adicional
```

#### Opção B: PostgreSQL (Produção)
```bash
# Instalar PostgreSQL
# Criar banco de dados
createdb alphaclin_qms

# Configurar variável de ambiente
export DATABASE_URL="postgresql://user:password@localhost:5432/alphaclin_qms"
```

### Passo 4: Executar Migrações
```bash
# Inicializar migrações (primeira vez)
flask db init

# Criar migração inicial
flask db migrate -m "Initial migration"

# Aplicar migrações
flask db upgrade
```

### Passo 5: Criar Usuário Administrador
```python
# No shell Python
from app import create_app, db
from models import User, UserRole
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@alphaclinic.com',
        password_hash=generate_password_hash('admin123'),
        full_name='Administrator',
        role=UserRole.ADMIN
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")
```

### Passo 6: Executar Aplicação
```bash
# Modo desenvolvimento
python app.py

# Ou com Flask CLI
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run
```

---

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Banco de dados
DATABASE_URL=sqlite:///instance/alphaclin_qms.db
# ou
DATABASE_URL=postgresql://user:password@localhost:5432/alphaclin_qms

# Segurança
SECRET_KEY=your-secret-key-here
SESSION_SECRET=your-session-secret-here

# E-mail (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Debug
FLASK_DEBUG=1
FLASK_ENV=development
```

### Configuração do E-mail

Para notificações por e-mail:

1. **Gmail**: Gere uma senha de aplicativo
2. **Outlook**: Use autenticação moderna
3. **SMTP Personalizado**: Configure servidor próprio

```python
# Exemplo Gmail
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME="seu-email@gmail.com"
MAIL_PASSWORD="sua-senha-app"
```

### Upload de Arquivos

```bash
# Criar diretórios
mkdir -p uploads/documents
mkdir -p uploads/images

# Ajustar permissões
chmod 755 uploads/
```

---

## 🧪 Testes e Verificação

### Verificar Instalação
```bash
# Testar imports
python -c "from app import create_app; print('✅ App OK')"

# Testar banco
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('✅ DB OK')"

# Testar servidor
curl http://localhost:5000
```

### Executar Testes
```bash
# Instalar pytest
pip install pytest

# Executar testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html
```

---

## 🚀 Deploy em Produção

### Usando Gunicorn + Nginx

#### 1. Instalar Gunicorn
```bash
pip install gunicorn
```

#### 2. Criar arquivo de configuração
`gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
```

#### 3. Executar com Gunicorn
```bash
gunicorn -c gunicorn.conf.py app:create_app
```

#### 4. Configurar Nginx
`/etc/nginx/sites-available/alphaclin-qms`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 5. Configurar SSL (Let's Encrypt)
```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d your-domain.com
```

### Usando Docker

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/alphaclin_qms
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=alphaclin_qms
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 🔧 Solução de Problemas

### Problema: Porta 5000 ocupada
```bash
# Verificar processo usando a porta
lsof -i :5000

# Matar processo
kill -9 <PID>

# Ou usar porta diferente
python app.py --port 5001
```

### Problema: Erro de permissões
```bash
# Ajustar permissões
sudo chown -R $USER:$USER /path/to/project
chmod -R 755 /path/to/project
```

### Problema: Banco não encontrado
```bash
# Para SQLite
ls -la instance/
# Deve existir alphaclin_qms.db

# Recriar banco
rm instance/alphaclin_qms.db
flask db upgrade
```

---

## 📞 Suporte

- **📧 E-mail**: suporte@alphaclin.com
- **📱 WhatsApp**: +55 11 99999-9999
- **📋 Issues**: [GitHub Issues](https://github.com/alphaclin/qms/issues)
- **📚 Documentação**: [Solução de Problemas](troubleshooting.md)

---

## ✅ Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Banco de dados configurado
- [ ] Migrações executadas
- [ ] Usuário admin criado
- [ ] Servidor iniciado
- [ ] Acesso via navegador funcionando
- [ ] Funcionalidades básicas testadas

**🎉 Instalação concluída! O Alphaclin QMS está pronto para uso.**