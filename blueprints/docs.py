from flask import Blueprint, send_from_directory, current_app, render_template
import os
import subprocess
from datetime import datetime

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/')
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
    """Fallback para servir arquivos markdown diretamente"""
    from flask import Response

    # Remove extensão .html se presente
    if filename.endswith('.html'):
        filename = filename[:-5] + '.md'

    file_path = os.path.join(current_app.root_path, 'docs', filename)

    if not os.path.exists(file_path):
        return Response("Documentação não encontrada", status=404)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Template básico sem markdown (fallback)
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
                            Para experiência completa, instale as dependências opcionais.
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
                                Para instalar dependências completas:<br>
                                <code>pip install Markdown</code>
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