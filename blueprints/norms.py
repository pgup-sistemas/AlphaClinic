from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Norm, Document, Process, Audit, db
from datetime import datetime
import json

norms_bp = Blueprint('norms', __name__)

@norms_bp.route('/')
@login_required
def index():
    """Lista todas as normas/acreditações"""
    search = request.args.get('search')
    active_only = request.args.get('active', 'true') == 'true'
    
    query = Norm.query
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    if search:
        query = query.filter(Norm.name.contains(search) | Norm.code.contains(search))
    
    norms = query.order_by(Norm.name).all()
    
    return render_template('norms/index.html', norms=norms)

@norms_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Criar nova norma/acreditação"""
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        description = request.form.get('description', '')
        version = request.form.get('version', '')
        effective_date = request.form.get('effective_date')
        review_date = request.form.get('review_date')
        
        # Handle custom fields (JSON)
        custom_fields = {}
        for key, value in request.form.items():
            if key.startswith('custom_'):
                field_name = key.replace('custom_', '')
                custom_fields[field_name] = value
        
        # Check if code already exists
        if Norm.query.filter_by(code=code).first():
            flash('Código da norma já existe.', 'error')
            return render_template('norms/create.html')
        
        norm = Norm(
            name=name,
            code=code,
            description=description,
            version=version,
            effective_date=datetime.strptime(effective_date, '%Y-%m-%d').date() if effective_date else None,
            review_date=datetime.strptime(review_date, '%Y-%m-%d').date() if review_date else None,
            custom_fields=custom_fields if custom_fields else None
        )
        
        db.session.add(norm)
        db.session.commit()
        
        flash('Norma criada com sucesso!', 'success')
        return redirect(url_for('norms.view', id=norm.id))
    
    return render_template('norms/create.html')

@norms_bp.route('/<int:id>')
@login_required
def view(id):
    """Visualizar norma com painel de progresso"""
    norm = Norm.query.get_or_404(id)
    
    # Calculate progress metrics
    total_documents = len(norm.documents)
    published_documents = len([d for d in norm.documents if d.status.value == 'published'])
    
    total_processes = len(norm.processes)
    
    total_audits = len(norm.audits)
    completed_audits = len([a for a in norm.audits if a.status == 'completed'])
    
    progress_data = {
        'documents': {
            'total': total_documents,
            'published': published_documents,
            'percentage': (published_documents / total_documents * 100) if total_documents > 0 else 0
        },
        'processes': {
            'total': total_processes,
            'mapped': total_processes,  # Assuming all processes with norm association are mapped
            'percentage': 100 if total_processes > 0 else 0
        },
        'audits': {
            'total': total_audits,
            'completed': completed_audits,
            'percentage': (completed_audits / total_audits * 100) if total_audits > 0 else 0
        }
    }
    
    return render_template('norms/view.html', norm=norm, progress=progress_data)

@norms_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar norma"""
    norm = Norm.query.get_or_404(id)
    
    if request.method == 'POST':
        norm.name = request.form['name']
        norm.code = request.form['code']
        norm.description = request.form.get('description', '')
        norm.version = request.form.get('version', '')
        norm.effective_date = datetime.strptime(request.form['effective_date'], '%Y-%m-%d').date() if request.form.get('effective_date') else None
        norm.review_date = datetime.strptime(request.form['review_date'], '%Y-%m-%d').date() if request.form.get('review_date') else None
        
        # Handle custom fields
        custom_fields = {}
        for key, value in request.form.items():
            if key.startswith('custom_'):
                field_name = key.replace('custom_', '')
                custom_fields[field_name] = value
        
        norm.custom_fields = custom_fields if custom_fields else None
        
        db.session.commit()
        flash('Norma atualizada com sucesso!', 'success')
        return redirect(url_for('norms.view', id=id))
    
    return render_template('norms/edit.html', norm=norm)

@norms_bp.route('/progress-dashboard')
@login_required
def progress_dashboard():
    """Painel de progresso por norma e unidade"""
    norms = Norm.query.filter_by(is_active=True).all()
    
    dashboard_data = []
    
    for norm in norms:
        # Calculate comprehensive progress
        total_documents = len(norm.documents)
        published_documents = len([d for d in norm.documents if d.status.value == 'published'])
        
        total_audits = len(norm.audits)
        completed_audits = len([a for a in norm.audits if a.status == 'completed'])
        
        # Overall compliance score
        doc_score = (published_documents / total_documents * 100) if total_documents > 0 else 0
        audit_score = (completed_audits / total_audits * 100) if total_audits > 0 else 0
        overall_score = (doc_score + audit_score) / 2 if total_audits > 0 or total_documents > 0 else 0
        
        dashboard_data.append({
            'norm': norm,
            'documents': {'total': total_documents, 'published': published_documents, 'score': doc_score},
            'audits': {'total': total_audits, 'completed': completed_audits, 'score': audit_score},
            'overall_score': overall_score
        })
    
    return render_template('norms/progress_dashboard.html', dashboard_data=dashboard_data)

@norms_bp.route('/api/progress-data')
@login_required
def progress_api():
    """API endpoint for progress data"""
    norms = Norm.query.filter_by(is_active=True).all()
    
    data = []
    for norm in norms:
        total_documents = len(norm.documents)
        published_documents = len([d for d in norm.documents if d.status.value == 'published'])
        
        data.append({
            'id': norm.id,
            'name': norm.name,
            'code': norm.code,
            'documents_progress': (published_documents / total_documents * 100) if total_documents > 0 else 0,
            'total_documents': total_documents,
            'published_documents': published_documents
        })
    
    return jsonify(data)