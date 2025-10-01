from flask import Blueprint, send_from_directory, current_app, render_template, request, redirect, url_for
from flask_login import login_required
import os
import subprocess
from datetime import datetime

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/')
@login_required
def docs_index():
    """Página inicial da documentação com busca e navegação"""
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M')

    # Estrutura da documentação
    doc_structure = {
        'user_guide': {
            'title': 'Guia do Usuário',
            'description': 'Guias práticos passo-a-passo para usar o sistema',
            'icon': '👥',
            'items': [
                {'title': 'Visão Geral', 'url': '/docs/', 'description': 'Introdução ao sistema'},
                {'title': 'Usuários e Equipes', 'url': '/docs/user-guide/users-teams/', 'description': 'Como gerenciar usuários'},
                {'title': 'Gestão Documental', 'url': '/docs/user-guide/documents/', 'description': 'Criar e aprovar documentos'},
                {'title': 'Auditorias', 'url': '/docs/user-guide/audits/', 'description': 'Planejar e executar auditorias'},
                {'title': 'Não Conformidades', 'url': '/docs/user-guide/ncs/', 'description': 'Tratar NCs e CAPA'},
                {'title': 'Relatórios', 'url': '/docs/user-guide/reports/', 'description': 'Gerar e interpretar relatórios'},
                {'title': 'Notificações', 'url': '/docs/user-guide/notifications/', 'description': 'Configurar alertas'},
                {'title': 'Solução de Problemas', 'url': '/docs/user-guide/troubleshooting/', 'description': 'Resolver problemas comuns'}
            ]
        },
        'installation': {
            'title': 'Instalação e Configuração',
            'description': 'Como instalar e configurar o sistema',
            'icon': '🛠️',
            'items': [
                {'title': 'Guia Rápido', 'url': '/docs/installation/quick-start/', 'description': 'Instalação em 5 minutos'},
                {'title': 'Instalação Completa', 'url': '/docs/installation/full-setup/', 'description': 'Setup para produção'},
                {'title': 'Configuração', 'url': '/docs/installation/configuration/', 'description': 'Configurações avançadas'},
                {'title': 'Solução de Problemas', 'url': '/docs/installation/troubleshooting/', 'description': 'Resolver problemas de instalação'}
            ]
        },
        'features': {
            'title': 'Funcionalidades Detalhadas',
            'description': 'Documentação técnica completa',
            'icon': '⚙️',
            'items': [
                {'title': 'Visão Geral', 'url': '/docs/features/overview/', 'description': 'Todas as funcionalidades'},
                {'title': 'APIs', 'url': '/docs/api/rest-api/', 'description': 'Documentação da API'},
                {'title': 'Webhooks', 'url': '/docs/api/webhooks/', 'description': 'Integrações em tempo real'},
                {'title': 'Integrações', 'url': '/docs/api/integrations/', 'description': 'Conectar sistemas externos'}
            ]
        },
        'development': {
            'title': 'Desenvolvimento',
            'description': 'Para desenvolvedores e técnicos',
            'icon': '👨‍💻',
            'items': [
                {'title': 'Arquitetura', 'url': '/docs/development/architecture/', 'description': 'Estrutura técnica'},
                {'title': 'Banco de Dados', 'url': '/docs/development/database/', 'description': 'Modelo de dados'},
                {'title': 'Segurança', 'url': '/docs/development/security/', 'description': 'Implementações de segurança'},
                {'title': 'Testes', 'url': '/docs/development/testing/', 'description': 'Estratégia de testes'}
            ]
        },
        'future': {
            'title': 'Funcionalidades Futuras',
            'description': 'O que está por vir',
            'icon': '🔮',
            'items': [
                {'title': 'Roadmap', 'url': '/docs/future/roadmap/', 'description': 'Plano de desenvolvimento'},
                {'title': 'Funcionalidades', 'url': '/docs/future/features/', 'description': 'Próximas implementações'},
                {'title': 'API Mobile', 'url': '/docs/future/mobile-api/', 'description': 'Aplicativo móvel'},
                {'title': 'BI e Analytics', 'url': '/docs/future/bi-analytics/', 'description': 'Business Intelligence'}
            ]
        },
        'about': {
            'title': 'Sobre o Projeto',
            'description': 'Informações do AlphaClinic QMS',
            'icon': '📋',
            'items': [
                {'title': 'Visão Geral', 'url': '/docs/about/overview/', 'description': 'Sobre o projeto'},
                {'title': 'Licença', 'url': '/docs/about/license/', 'description': 'Termos de uso'},
                {'title': 'Contribuição', 'url': '/docs/about/contributing/', 'description': 'Como contribuir'}
            ]
        }
    }

    return render_template('docs/index.html', current_time=current_time, doc_structure=doc_structure)

@docs_bp.route('/api/search')
@login_required
def api_search():
    """API para busca rápida"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')

    if not query:
        return {'results': [], 'total': 0}

    results = []
    total = 0

    def search_in_file(filepath, title):
        nonlocal total
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        total += 1
                        if len(results) < 20:  # Limitar resultados
                            # Contexto da linha
                            start = max(0, i-1)
                            end = min(len(lines), i+2)
                            context = '\n'.join(lines[start:end])

                            results.append({
                                'title': title,
                                'url': '/docs/' + filepath.replace('docs/', '').replace('.md', '/'),
                                'context': context,
                                'line_number': i + 1,
                                'type': 'document'
                            })
        except:
            pass

    # Buscar nos arquivos relevantes
    search_paths = []
    if category == 'user-guide' or not category:
        search_paths.extend([
            'docs/user-guide/users-teams.md',
            'docs/user-guide/documents.md',
            'docs/user-guide/audits.md',
            'docs/user-guide/ncs.md',
            'docs/user-guide/reports.md',
            'docs/user-guide/notifications.md',
            'docs/user-guide/troubleshooting.md'
        ])

    if category == 'installation' or not category:
        search_paths.extend([
            'docs/installation/quick-start.md',
            'docs/installation/full-setup.md',
            'docs/installation/configuration.md',
            'docs/installation/troubleshooting.md'
        ])

    if category == 'api' or not category:
        search_paths.extend([
            'docs/api/rest-api.md',
            'docs/api/webhooks.md',
            'docs/api/integrations.md'
        ])

    for filepath in search_paths:
        if os.path.exists(filepath):
            title = os.path.basename(filepath).replace('.md', '').replace('-', ' ').title()
            search_in_file(filepath, title)

    return {
        'results': results,
        'total': total,
        'query': query
    }

@docs_bp.route('/search-results')
@login_required
def search_results():
    """Página de resultados de busca"""
    query = request.args.get('q', '').strip()

    if not query:
        return redirect('/docs/')

    # Busca simples nos arquivos markdown
    results = []
    total = 0

    def search_in_file(filepath, title):
        nonlocal total
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        total += 1
                        if len(results) < 20:  # Limitar resultados
                            # Contexto da linha
                            start = max(0, i-1)
                            end = min(len(lines), i+2)
                            context = '\n'.join(lines[start:end])

                            results.append({
                                'title': title,
                                'url': '/docs/' + filepath.replace('docs/', '').replace('.md', '/'),
                                'context': context,
                                'line_number': i + 1,
                                'type': 'document'
                            })
        except:
            pass

    # Buscar em todos os arquivos markdown
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                title = file.replace('.md', '').replace('_', ' ').title()
                search_in_file(filepath, title)

    return render_template('docs/search_results.html', query=query, results=results, total=total)

@docs_bp.route('/search')
@login_required
def search_docs():
    """Busca na documentação"""
    query = request.args.get('q', '').strip()

    if not query:
        return redirect('/docs/')

    # Busca simples nos arquivos markdown
    results = []

    def search_in_file(filepath, title):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        # Contexto da linha
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        context = '\n'.join(lines[start:end])

                        results.append({
                            'title': title,
                            'url': '/docs/' + filepath.replace('docs/', '').replace('.md', '/'),
                            'context': context,
                            'line_number': i + 1
                        })
        except:
            pass

    # Buscar em todos os arquivos markdown
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                title = file.replace('.md', '').replace('_', ' ').title()
                search_in_file(filepath, title)

    return render_template('docs/search.html', query=query, results=results)

@docs_bp.route('/<path:filename>')
def docs_files(filename):
    """Serve arquivos da documentação"""
    # Tentar MkDocs primeiro se disponível
    try:
        import mkdocs
        # Se MkDocs está disponível, tentar usar
        return serve_mkdocs_documentation(filename)
    except ImportError:
        # Fallback para renderização customizada
        return serve_markdown(filename)

def serve_mkdocs_documentation(filename):
    """Tenta servir documentação via MkDocs se disponível"""
    try:
        # Verificar se MkDocs está disponível
        import mkdocs

        # Tentar usar MkDocs para servir
        from mkdocs.commands.serve import serve
        from mkdocs.commands.build import build

        # Se filename é index, redirecionar para MkDocs
        if filename == '' or filename == 'index' or filename == '/':
            # Tentar iniciar servidor MkDocs
            try:
                # Build da documentação
                result = subprocess.run(['mkdocs', 'build', '--clean'],
                                      capture_output=True, text=True,
                                      cwd=current_app.root_path, timeout=30)

                if result.returncode == 0:
                    # Servir arquivo buildado
                    return send_from_directory(os.path.join(current_app.root_path, 'site'), 'index.html')
                else:
                    # Fallback para markdown customizado
                    return serve_markdown('index.md')
            except:
                return serve_markdown('index.md')
        else:
            # Tentar servir arquivo específico
            return serve_markdown(filename)

    except ImportError:
        # MkDocs não disponível, usar fallback
        return serve_markdown(filename)

def serve_markdown(filename):
    """Serve arquivos markdown com renderização completa"""
    from flask import Response

    # Remove extensão .html se presente
    if filename.endswith('.html'):
        filename = filename[:-5] + '.md'

    # Handle trailing slash - try to find .md file
    if filename.endswith('/'):
        filename = filename[:-1] + '.md'

    # Se filename vazio, usar index.md
    if filename == '' or filename == '/':
        filename = 'index.md'

    file_path = os.path.join(current_app.root_path, 'docs', filename)

    if not os.path.exists(file_path):
        return Response("Documentação não encontrada", status=404)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to use full markdown rendering
        try:
            import markdown

            # Use comprehensive extensions
            md_extensions = [
                'extra',           # Extra markdown features
                'codehilite',      # Code highlighting
                'toc',             # Table of contents
                'tables',          # Tables
                'fenced_code',     # Fenced code blocks
                'nl2br',           # New lines to breaks
            ]

            # Convert markdown to HTML
            html_content = markdown.markdown(content, extensions=md_extensions)

            # Template completo com CSS moderno para documentação
            full_html = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Alphaclin QMS - Documentação</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.6;
                        background-color: #f8f9fa;
                    }}
                    .navbar-brand {{ font-weight: 600; }}
                    .search-container {{
                        background: white;
                        padding: 2rem;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        margin-bottom: 2rem;
                    }}
                    .search-input {{
                        border: 2px solid #e9ecef;
                        border-radius: 8px;
                        padding: 0.75rem 1rem;
                        font-size: 1rem;
                        transition: border-color 0.15s ease-in-out;
                    }}
                    .search-input:focus {{
                        border-color: #2563eb;
                        outline: 0;
                        box-shadow: 0 0 0 0.2rem rgba(37, 99, 235, 0.25);
                    }}
                    .doc-section {{
                        background: white;
                        padding: 2rem;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        margin-bottom: 2rem;
                    }}
                    .section-icon {{ font-size: 2rem; margin-right: 1rem; }}
                    .section-title {{ color: #2563eb; font-weight: 600; }}
                    .doc-item {{
                        border: 1px solid #e9ecef;
                        border-radius: 8px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                        transition: all 0.2s ease;
                    }}
                    .doc-item:hover {{
                        border-color: #2563eb;
                        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
                    }}
                    .doc-item-title {{ color: #374151; font-weight: 600; }}
                    .doc-item-description {{ color: #6b7280; margin-top: 0.5rem; }}
                    .doc-item-url {{ color: #2563eb; text-decoration: none; }}
                    .doc-item-url:hover {{ text-decoration: underline; }}
                    .markdown-content {{
                        background: white;
                        padding: 2rem;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .markdown-content h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
                    .markdown-content h2 {{ color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; }}
                    .markdown-content h3 {{ color: #4b5563; }}
                    .markdown-content pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                    .markdown-content code {{ background: #f1f3f4; padding: 2px 4px; border-radius: 3px; }}
                    .markdown-content blockquote {{ border-left: 4px solid #2563eb; padding-left: 15px; background: #f0f9ff; }}
                    .sidebar {{ background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .sidebar h5 {{ color: #374151; font-weight: 600; }}
                    .sidebar ul {{ list-style: none; padding: 0; }}
                    .sidebar li {{ margin-bottom: 0.5rem; }}
                    .sidebar a {{ color: #6b7280; text-decoration: none; }}
                    .sidebar a:hover {{ color: #2563eb; }}
                </style>
            </head>
            <body>
                <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
                    <div class="container">
                        <a class="navbar-brand" href="/docs/">
                            📚 Alphaclin QMS - Documentação
                        </a>
                        <div class="navbar-nav ms-auto">
                            <a class="nav-link" href="/dashboard">🏠 Dashboard</a>
                        </div>
                    </div>
                </nav>

                <div class="container mt-4">
                    <div class="row">
                        <div class="col-md-9">
                            <div class="markdown-content">
                                {html_content}
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="sidebar">
                                <h5>📚 Navegação Rápida</h5>
                                <ul>
                                    <li><a href="/docs/">🏠 Início</a></li>
                                    <li><a href="/docs/user-guide/users-teams/">👤 Usuários e Equipes</a></li>
                                    <li><a href="/docs/user-guide/documents/">📄 Documentos</a></li>
                                    <li><a href="/docs/user-guide/audits/">🔍 Auditorias</a></li>
                                    <li><a href="/docs/user-guide/ncs/">⚠️ Não Conformidades</a></li>
                                    <li><a href="/docs/user-guide/reports/">📊 Relatórios</a></li>
                                    <li><a href="/docs/installation/quick-start/">📦 Instalação</a></li>
                                    <li><a href="/docs/features/overview/">⚙️ Funcionalidades</a></li>
                                    <li><a href="/docs/api/rest-api/">🔌 APIs</a></li>
                                    <li><a href="/docs/development/architecture/">🏗️ Arquitetura</a></li>
                                </ul>
                                <hr>
                                <p class="small text-muted">
                                    <strong>✅ Recursos:</strong><br>
                                    • Guias Práticos<br>
                                    • Exemplos Reais<br>
                                    • Busca Integrada<br>
                                    • Formatação Completa
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
                <script>hljs.highlightAll();</script>
            </body>
            </html>
            """

        except ImportError:
            # Fallback to basic rendering
            full_html = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Alphaclin QMS - Documentação</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f8f9fa; }}
                    .search-container {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }}
                    .doc-section {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }}
                    .sidebar {{ background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                </style>
            </head>
            <body>
                <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
                    <div class="container">
                        <a class="navbar-brand" href="/docs/">
                            📚 Alphaclin QMS - Documentação
                        </a>
                        <div class="navbar-nav ms-auto">
                            <a class="nav-link" href="/dashboard">🏠 Dashboard</a>
                        </div>
                    </div>
                </nav>

                <div class="container mt-4">
                    <div class="row">
                        <div class="col-md-9">
                            <div class="alert alert-info">
                                <strong>📝 Documentação Básica:</strong> Para formatação avançada, instale as dependências necessárias.
                            </div>
                            <pre style="background: white; border: 1px solid #dee2e6; padding: 20px; border-radius: 5px; white-space: pre-wrap;">{content}</pre>
                        </div>
                        <div class="col-md-3">
                            <div class="sidebar">
                                <h5>📚 Navegação</h5>
                                <ul>
                                    <li><a href="/docs/">🏠 Início</a></li>
                                    <li><a href="/docs/user-guide/">👥 Guia do Usuário</a></li>
                                    <li><a href="/docs/installation/">📦 Instalação</a></li>
                                    <li><a href="/docs/features/">⚙️ Funcionalidades</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

        return Response(full_html, mimetype='text/html')

    except Exception as e:
        return Response(f"Erro ao carregar documentação: {e}", status=500)

@docs_bp.route('/build')
def build_docs():
    """Endpoint para rebuild da documentação (admin only)"""
    from flask_login import current_user

    if not current_user.is_authenticated or current_user.role.value != 'admin':
        return Response("Acesso negado", status=403)

    try:
        # Build da documentação
        result = subprocess.run(['mkdocs', 'build'],
                              capture_output=True,
                              text=True,
                              cwd=current_app.root_path)

        if result.returncode == 0:
            return Response("Documentação rebuildada com sucesso!", status=200)
        else:
            return Response(f"Erro no build: {result.stderr}", status=500)

    except Exception as e:
        return Response(f"Erro: {e}", status=500)