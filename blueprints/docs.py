from flask import Blueprint, send_from_directory, current_app, render_template
from flask_login import login_required
import os
import subprocess
from datetime import datetime

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/')
@login_required
def docs_index():
    """Página inicial da documentação"""
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M')
    return render_template('docs/index.html', current_time=current_time)

@docs_bp.route('/<path:filename>')
def docs_files(filename):
    """Serve arquivos da documentação - direto do markdown"""
    # Sempre usar fallback markdown (mkdocs não instalado)
    return serve_markdown(filename)

def serve_markdown(filename):
    """Serve arquivos markdown com renderização completa ou fallback"""
    from flask import Response

    # Remove extensão .html se presente
    if filename.endswith('.html'):
        filename = filename[:-5] + '.md'

    # Handle trailing slash - try to find .md file
    if filename.endswith('/'):
        filename = filename[:-1] + '.md'

    file_path = os.path.join(current_app.root_path, 'docs', filename)

    if not os.path.exists(file_path):
        return Response("Documentação não encontrada", status=404)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to use full markdown rendering
        try:
            import markdown

            # Use basic extensions that are always available
            md_extensions = [
                'extra',           # Extra markdown features
                'codehilite',      # Code highlighting
            ]

            # Convert markdown to HTML
            html_content = markdown.markdown(content, extensions=md_extensions)

            # Template completo com CSS para markdown
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Alphaclin QMS - Documentação Completa</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
                <style>
                    body {{ padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; }}
                    .markdown-body {{ max-width: none; }}
                    pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                    code {{ background: #f1f3f4; padding: 2px 4px; border-radius: 3px; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }}
                    pre code {{ background: transparent; padding: 0; }}
                    h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; margin-top: 2rem; }}
                    h2 {{ color: #374151; margin-top: 2rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; }}
                    h3 {{ color: #4b5563; margin-top: 1.5rem; }}
                    h4 {{ color: #6b7280; margin-top: 1.25rem; }}
                    .sidebar {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                    .content {{ max-width: 900px; }}
                    blockquote {{ border-left: 4px solid #2563eb; padding-left: 15px; margin: 15px 0; background: #f0f9ff; padding: 10px 15px; border-radius: 0 5px 5px 0; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                    th, td {{ border: 1px solid #dee2e6; padding: 8px 12px; text-align: left; }}
                    th {{ background: #f8f9fa; font-weight: 600; }}
                    .admonition {{ border-left: 4px solid; padding: 10px 15px; margin: 15px 0; border-radius: 0 5px 5px 0; }}
                    .admonition.note {{ border-color: #2563eb; background: #eff6ff; }}
                    .admonition.warning {{ border-color: #f59e0b; background: #fffbeb; }}
                    .admonition.danger {{ border-color: #ef4444; background: #fef2f2; }}
                    .admonition.success {{ border-color: #10b981; background: #f0fdf4; }}
                    .highlight {{ background: #f8f9fa; border-radius: 5px; padding: 15px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
                    <div class="container">
                        <a class="navbar-brand" href="/docs/">
                            📚 Alphaclin QMS - Documentação Completa
                        </a>
                        <span class="badge bg-success">Modo Completo</span>
                    </div>
                </nav>
                <div class="container">
                    <div class="row">
                        <div class="col-md-9 content">
                            <div class="alert alert-success">
                                <strong>🎉 Modo Completo:</strong> Documentação renderizada com formatação avançada,
                                syntax highlighting e recursos completos de markdown!
                            </div>
                            <div class="markdown-body">
                                {html_content}
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="sidebar">
                                <h5>Navegação</h5>
                                <ul class="list-unstyled">
                                    <li><a href="/docs/">🏠 Início</a></li>
                                    <div class="border-t border-gray-200 my-2 pt-2">
                                        <li class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Instalação</li>
                                        <li><a href="/docs/installation/quick-start/" class="ml-2 text-sm">📦 Instalação Rápida</a></li>
                                        <li><a href="/docs/installation/troubleshooting/" class="ml-2 text-sm">🔧 Solução de Problemas</a></li>
                                    </div>
                                    <div class="border-t border-gray-200 my-2 pt-2">
                                        <li class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Usuário</li>
                                        <li><a href="/docs/features/overview/">⚙️ Funcionalidades</a></li>
                                        <li><a href="/docs/api/rest-api/">🔌 API REST</a></li>
                                    </div>
                                    <div class="border-t border-gray-200 my-2 pt-2">
                                        <li class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Desenvolvedor</li>
                                        <li><a href="/docs/development/architecture/">🏗️ Arquitetura</a></li>
                                        <li><a href="/docs/future/roadmap/">🗺️ Roadmap</a></li>
                                    </div>
                                </ul>
                                <hr>
                                <p class="small text-muted">
                                    <strong>✅ Bibliotecas instaladas:</strong><br>
                                    • Markdown<br>
                                    • Pygments<br>
                                    • Pymdown-extensions
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
            <html>
            <head>
                <title>Alphaclin QMS - Docs</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ padding: 20px; font-family: Arial, sans-serif; }}
                    pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; white-space: pre-wrap; }}
                    code {{ background: #f1f3f4; padding: 2px 4px; border-radius: 3px; }}
                    h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
                    h2 {{ color: #374151; margin-top: 30px; }}
                    h3 {{ color: #4b5563; }}
                    .sidebar {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                    .content {{ max-width: 800px; }}
                </style>
            </head>
            <body>
                <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
                    <div class="container">
                        <a class="navbar-brand" href="/docs/">
                            📚 Alphaclin QMS - Documentação
                        </a>
                        <span class="badge bg-info">Modo Básico</span>
                    </div>
                </nav>
                <div class="container">
                    <div class="row">
                        <div class="col-md-9 content">
                            <div class="alert alert-info">
                                <strong>📝 Modo Básico:</strong> Documentação renderizada sem formatação avançada.
                                Para experiência completa, instale: <code>pip install Pygments pymdown-extensions</code>
                            </div>
                            <pre style="background: white; border: 1px solid #dee2e6; padding: 20px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;">{content}</pre>
                        </div>
                        <div class="col-md-3">
                            <div class="sidebar">
                                <h5>Navegação</h5>
                                <ul class="list-unstyled">
                                    <li><a href="/docs/">🏠 Início</a></li>
                                    <li><a href="/docs/features/overview/">⚙️ Funcionalidades</a></li>
                                    <li><a href="/docs/future/roadmap/">🗺️ Roadmap</a></li>
                                    <li><a href="/docs/installation/quick-start/">📦 Instalação</a></li>
                                </ul>
                                <hr>
                                <p class="small text-muted">
                                    <strong>❌ Bibliotecas faltando:</strong><br>
                                    • Pygments<br>
                                    • Pymdown-extensions
                                </p>
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