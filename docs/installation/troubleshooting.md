# Solução de Problemas - Alphaclin QMS

## Problemas Comuns e Soluções

### 1. Erro de Conexão com Banco de Dados

#### Sintomas
- Erro: `sqlalchemy.exc.OperationalError`
- Mensagem: "Can't connect to MySQL server"

#### Soluções

**Para SQLite (padrão):**
```bash
# Verificar se o arquivo existe
ls -la instance/alphaclin_qms.db

# Se não existir, inicializar o banco
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

**Para PostgreSQL:**
```bash
# Instalar dependências
pip install psycopg2-binary

# Configurar variável de ambiente
export DATABASE_URL="postgresql://user:password@localhost:5432/alphaclin_qms"

# Testar conexão
python -c "from app import create_app; app = create_app(); print('Conexão OK')"
```

### 2. Erro de Permissões

#### Sintomas
- Erro 403: "Acesso negado"
- Usuário não consegue acessar certas funcionalidades

#### Soluções

**Verificar roles do usuário:**
```python
# No shell Python
from app import create_app, db
from models import User, UserRole

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    print(f"Role: {user.role}")
    print(f"Is active: {user.is_active}")
```

**Alterar role se necessário:**
```python
# No shell Python
user.role = UserRole.ADMIN
db.session.commit()
```

### 3. Problemas com E-mail

#### Sintomas
- E-mails não são enviados
- Erro: "SMTP connection failed"

#### Soluções

**Configurar SMTP:**
```bash
# Para Gmail
export MAIL_SERVER="smtp.gmail.com"
export MAIL_PORT="587"
export MAIL_USE_TLS="true"
export MAIL_USERNAME="seu-email@gmail.com"
export MAIL_PASSWORD="sua-senha-app"
```

**Testar envio:**
```python
# No shell Python
from app import create_app
from email_service import send_email

app = create_app()
with app.app_context():
    send_email(
        to='teste@email.com',
        subject='Teste',
        body='Teste de envio'
    )
```

### 4. Erro de Upload de Arquivos

#### Sintomas
- Arquivos não são salvos
- Erro: "Permission denied" ou "No such file or directory"

#### Soluções

**Verificar permissões:**
```bash
# Criar diretório de uploads
mkdir -p uploads/documents
mkdir -p uploads/images

# Ajustar permissões
chmod 755 uploads/
chmod 755 uploads/documents/
chmod 755 uploads/images/
```

**Configurar tamanho máximo:**
```python
# Em config.py
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### 5. Problemas com Assinaturas Digitais

#### Sintomas
- Assinaturas não são válidas
- Erro: "Invalid signature"

#### Soluções

**Verificar bibliotecas criptográficas:**
```bash
pip install cryptography
pip install PyJWT
```

**Testar assinatura:**
```python
# No shell Python
import hashlib
import hmac

message = b"teste"
key = b"chave-secreta"
signature = hmac.new(key, message, hashlib.sha256).hexdigest()
print(f"Assinatura: {signature}")
```

### 6. Erro 500 - Internal Server Error

#### Sintomas
- Página retorna erro 500
- Aplicação para de funcionar

#### Soluções

**Verificar logs:**
```bash
# Ativar modo debug
export FLASK_DEBUG=1
python app.py
```

**Verificar dependências:**
```bash
pip check
pip install -r requirements.txt --upgrade
```

**Limpar cache:**
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### 7. Problemas de Performance

#### Sintomas
- Aplicação lenta
- Alto uso de CPU/memória

#### Soluções

**Otimizar consultas:**
```python
# Usar eager loading
documents = Document.query.options(joinedload(Document.author)).all()

# Usar paginação
documents = Document.query.paginate(page=1, per_page=20)
```

**Configurar cache:**
```python
# Instalar redis
pip install redis

# Configurar cache
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

### 8. Problemas com Documentação

#### Sintomas
- Documentação mostra "Modo Básico"
- Markdown não renderiza corretamente

#### Soluções

**Instalar bibliotecas completas:**
```bash
pip install Markdown Pygments pymdown-extensions
```

**Verificar instalação:**
```python
# No shell Python
import markdown
import pygments
import pymdownx
print("Todas as bibliotecas instaladas!")
```

### 9. Erro de Migração do Banco

#### Sintomas
- Erro: "alembic.util.exc.CommandError"
- Migrações não aplicam

#### Soluções

**Resetar migrações:**
```bash
# Remover pasta migrations
rm -rf migrations/

# Recriar
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Aplicar migrações manualmente:**
```bash
flask db upgrade
```

### 10. Problemas com Sessões

#### Sintomas
- Usuário é deslogado automaticamente
- Sessões não persistem

#### Soluções

**Configurar secret key:**
```python
# Em config.py
SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-muito-forte'
```

**Configurar lifetime da sessão:**
```python
# Em config.py
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
```

## Logs de Debug

### Ativar Logs Detalhados

```python
# Em app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou para arquivo
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Verificar Logs

```bash
# Ver logs em tempo real
tail -f app.log

# Ou no terminal
python app.py 2>&1 | tee app.log
```

## Suporte

Para suporte adicional:

1. **Verifique os logs** da aplicação
2. **Teste em modo debug** (`FLASK_DEBUG=1`)
3. **Verifique as dependências** (`pip check`)
4. **Consulte a documentação** oficial das bibliotecas
5. **Abra uma issue** no repositório do projeto

## Checklist de Verificação

- [ ] Python versão 3.8+
- [ ] Todas as dependências instaladas
- [ ] Banco de dados configurado
- [ ] Variáveis de ambiente definidas
- [ ] Permissões de arquivo corretas
- [ ] Porta 5000 livre
- [ ] Firewall configurado
- [ ] Antivirus não bloqueando