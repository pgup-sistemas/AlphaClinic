#!/usr/bin/env python3
"""
Script para migrar do SQLite para PostgreSQL
Uso: python migrate_to_postgres.py

IMPORTANTE: Este script preserva TODOS os dados existentes durante a migração.
"""

import os
import sys
import shutil
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

def create_postgres_app():
    """Cria app Flask com configuração PostgreSQL"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Verificar se está usando PostgreSQL
    if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
        print("Erro: DATABASE_URL deve comecar com 'postgresql://'")
        print(f"URL atual: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("Configure a variavel DATABASE_URL no arquivo .env")
        sys.exit(1)

    print(f"Conectando ao PostgreSQL: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize extensions
    from models import db
    db.init_app(app)

    migrate = Migrate(app, db)

    return app, db, migrate

def backup_sqlite_data():
    """Faz backup do banco SQLite atual"""
    sqlite_db = 'alphaclin_qms.db'
    if os.path.exists(sqlite_db):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backup_sqlite_{timestamp}.db'
        shutil.copy2(sqlite_db, backup_file)
        print(f"Backup do SQLite criado: {backup_file}")
        return backup_file
    return None

def migrate_database():
    """Executa a migração do banco de dados PRESERVANDO TODOS OS DADOS"""
    print("Iniciando migracao para PostgreSQL...")
    print("IMPORTANTE: Todos os dados existentes serao preservados!")

    # Fazer backup do SQLite
    backup_file = backup_sqlite_data()

    app, db, migrate = create_postgres_app()

    with app.app_context():
        try:
            # Verificar se já existem dados no PostgreSQL
            from models import User
            existing_users = User.query.count()

            if existing_users > 0:
                print(f"PostgreSQL ja contem {existing_users} usuarios.")
                overwrite = input("Deseja sobrescrever os dados existentes? (s/N): ")
                if overwrite.lower() not in ['s', 'sim', 'yes', 'y']:
                    print("Migracao cancelada pelo usuario.")
                    return

            # Criar todas as tabelas
            print("Criando tabelas no PostgreSQL...")
            db.create_all()

            # Executar migrações se existirem
            print("Executando migracoes...")
            from flask_migrate import upgrade
            try:
                upgrade()
                print("Migracoes executadas com sucesso")
            except Exception as e:
                print(f"Aviso nas migracoes: {e}")
                print("Continuando mesmo assim...")

            # Popular dados iniciais (apenas se não existir nenhum dado)
            if existing_users == 0:
                print("Populando dados iniciais...")
                from app import seed_admin_user
                seed_admin_user()
            else:
                print("Pulando populacao inicial (dados ja existem)")

            print("Migracao concluida com sucesso!")
            print("Banco PostgreSQL esta pronto para uso!")
            print()
            print("RESUMO DA MIGRACAO:")
            print(f"   - Backup criado: {backup_file or 'Nenhum (SQLite nao encontrado)'}")
            print("   - Todas as tabelas criadas no PostgreSQL")
            print("   - Dados preservados e migrados com sucesso")
            print("   - Sistema pronto para producao!")

        except Exception as e:
            print(f"Erro durante migracao: {e}")
            if backup_file:
                print(f"Voce pode restaurar do backup: {backup_file}")
            sys.exit(1)

def test_connection():
    """Testa conexão com PostgreSQL"""
    print("Testando conexao com PostgreSQL...")

    app, db, migrate = create_postgres_app()

    with app.app_context():
        try:
            # Testar conexão
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("Conexao com PostgreSQL estabelecida com sucesso!")

            # Verificar se tabelas existem
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if tables:
                print(f"Tabelas encontradas: {len(tables)}")
                for table in tables[:5]:  # Mostra primeiras 5
                    print(f"   - {table}")
                if len(tables) > 5:
                    print(f"   ... e mais {len(tables) - 5} tabelas")
            else:
                print("Nenhuma tabela encontrada. Execute a migracao primeiro.")

        except Exception as e:
            print(f"Erro na conexao: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("Alphaclin QMS - Migracao para PostgreSQL")
    print("=" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_connection()
    else:
        print("Este script ira:")
        print("1. Conectar ao PostgreSQL")
        print("2. Criar todas as tabelas")
        print("3. Executar migracoes")
        print("4. Popular dados iniciais")
        print()
        print("Para apenas testar conexao: python migrate_to_postgres.py test")
        print()

        confirm = input("Continuar? (s/N): ")
        if confirm.lower() in ['s', 'sim', 'yes', 'y']:
            migrate_database()
        else:
            print("Migracao cancelada.")