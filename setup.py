#!/usr/bin/env python3
"""
Script de Configuração Inicial - Alphaclin QMS
Executa automaticamente todas as etapas de instalação
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Executa comando e mostra resultado"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Sucesso!")
        if result.stdout.strip():
            print(f"   📄 {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Falhou!")
        print(f"   Erro: {e.stderr.strip()}")
        return False

def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detectado. Necessário Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_requirements():
    """Verifica se requirements.txt existe"""
    if not Path("requirements.txt").exists():
        print("❌ Arquivo requirements.txt não encontrado!")
        return False
    print("✅ requirements.txt encontrado")
    return True

def install_dependencies():
    """Instala dependências Python"""
    return run_command("pip install -r requirements.txt", "Instalando dependências Python")

def create_env_file():
    """Cria arquivo .env se não existir"""
    if Path(".env").exists():
        print("⚠️  Arquivo .env já existe - pulando criação")
        return True

    env_content = """# Alphaclin QMS - Configuração de Desenvolvimento
DATABASE_URL=sqlite:///alphaclin_qms.db
SECRET_KEY=dev-secret-key-change-in-production
SESSION_SECRET=dev-session-secret

# Email Configuration (configure para ativar notificações)
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=true
# MAIL_USERNAME=seu-email@gmail.com
# MAIL_PASSWORD=sua-senha-app
# MAIL_DEFAULT_SENDER=noreply@alphaclinic.com

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
"""

    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com configurações padrão")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def initialize_database():
    """Inicializa banco de dados e cria admin"""
    print("\n🔄 Inicializando banco de dados...")
    print("   📝 Isso pode levar alguns segundos...")

    try:
        # Importar aqui para garantir que dependências estão instaladas
        from app import create_app
        from models import db

        app = create_app()

        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            print("   📋 Tabelas criadas")

            # Popular dados iniciais (incluindo admin)
            from app import seed_admin_user
            seed_admin_user()
            print("   🌱 Dados iniciais populados")

        print("✅ Banco de dados inicializado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def create_email_templates():
    """Cria templates de e-mail padrão"""
    print("\n🔄 Criando templates de e-mail...")
    try:
        from app import create_app
        app = create_app()

        with app.app_context():
            from email_service import notification_service
            notification_service.create_default_templates()

        print("✅ Templates de e-mail criados!")
        return True

    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível criar templates de e-mail: {e}")
        print("   💡 Configure o e-mail no .env e execute: flask create-email-templates")
        return True  # Não é erro crítico

def show_success_message():
    """Mostra mensagem de sucesso e instruções"""
    print("\n" + "="*60)
    print("🎉 ALPHACLIN QMS INSTALADO COM SUCESSO!")
    print("="*60)
    print()
    print("🚀 Para iniciar o sistema:")
    print("   python app.py")
    print()
    print("🌐 Acesse em:")
    print("   http://localhost:5000")
    print()
    print("👤 Primeiro login:")
    print("   Usuário: admin")
    print("   Senha:   admin123")
    print()
    print("📧 Para ativar notificações por e-mail:")
    print("   1. Configure as variáveis MAIL_* no arquivo .env")
    print("   2. Execute: flask create-email-templates")
    print("   3. Configure processamento: flask process-emails")
    print()
    print("📚 Documentação completa:")
    print("   INSTALL.md - Guia detalhado de instalação")
    print("   README.md  - Funcionalidades do sistema")
    print()
    print("🆘 Suporte:")
    print("   Verifique INSTALL.md para solução de problemas")
    print("="*60)

def main():
    """Função principal de instalação"""
    print("🏥 Alphaclin QMS - Instalação Automática")
    print("="*50)

    # Verificações iniciais
    if not check_python_version():
        sys.exit(1)

    if not check_requirements():
        sys.exit(1)

    # Instalação
    if not install_dependencies():
        print("\n❌ Falha na instalação das dependências!")
        print("💡 Tente executar: pip install -r requirements.txt")
        sys.exit(1)

    if not create_env_file():
        sys.exit(1)

    if not initialize_database():
        print("\n❌ Falha na inicialização do banco!")
        print("💡 Verifique se não há outro processo usando a porta do banco")
        sys.exit(1)

    # Templates de e-mail (não crítico)
    create_email_templates()

    # Sucesso!
    show_success_message()

if __name__ == "__main__":
    main()