
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Process, Norm, db
import json
from datetime import datetime

processes_bp = Blueprint('processes', __name__)

@processes_bp.route('/')
@login_required
def index():
    """Lista todos os processos mapeados"""
    search = request.args.get('search')
    norm_id = request.args.get('norm_id')
    
    query = Process.query
    
    if search:
        query = query.filter(Process.name.contains(search) | Process.code.contains(search))
    
    if norm_id:
        query = query.filter(Process.norms.any(id=norm_id))
    
    processes = query.order_by(Process.name).all()
    norms = Norm.query.filter_by(is_active=True).all()
    
    return render_template('processes/index.html', processes=processes, norms=norms)

@processes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Criar novo processo"""
    if request.method == 'POST':
        name = request.form['name']
        code = request.form.get('code', '')
        description = request.form.get('description', '')
        
        # Parse inputs, outputs, responsibilities, risks as JSON
        inputs = []
        outputs = []
        responsibilities = []
        risks = []
        
        # Process form arrays
        input_names = request.form.getlist('input_name[]')
        input_descriptions = request.form.getlist('input_description[]')
        for i, name_val in enumerate(input_names):
            if name_val.strip():
                inputs.append({
                    'name': name_val,
                    'description': input_descriptions[i] if i < len(input_descriptions) else ''
                })
        
        output_names = request.form.getlist('output_name[]')
        output_descriptions = request.form.getlist('output_description[]')
        for i, name_val in enumerate(output_names):
            if name_val.strip():
                outputs.append({
                    'name': name_val,
                    'description': output_descriptions[i] if i < len(output_descriptions) else ''
                })
        
        resp_roles = request.form.getlist('resp_role[]')
        resp_descriptions = request.form.getlist('resp_description[]')
        for i, role in enumerate(resp_roles):
            if role.strip():
                responsibilities.append({
                    'role': role,
                    'description': resp_descriptions[i] if i < len(resp_descriptions) else ''
                })
        
        risk_names = request.form.getlist('risk_name[]')
        risk_descriptions = request.form.getlist('risk_description[]')
        risk_mitigations = request.form.getlist('risk_mitigation[]')
        for i, risk_name in enumerate(risk_names):
            if risk_name.strip():
                risks.append({
                    'name': risk_name,
                    'description': risk_descriptions[i] if i < len(risk_descriptions) else '',
                    'mitigation': risk_mitigations[i] if i < len(risk_mitigations) else ''
                })
        
        norm_ids = request.form.getlist('norm_ids')
        
        process = Process(
            name=name,
            code=code,
            description=description,
            inputs=inputs if inputs else None,
            outputs=outputs if outputs else None,
            responsibilities=responsibilities if responsibilities else None,
            risks=risks if risks else None
        )
        
        db.session.add(process)
        db.session.flush()
        
        # Associate with norms
        if norm_ids:
            norms = Norm.query.filter(Norm.id.in_(norm_ids)).all()
            process.norms.extend(norms)
        
        db.session.commit()
        
        flash('Processo criado com sucesso!', 'success')
        return redirect(url_for('processes.view', id=process.id))
    
    norms = Norm.query.filter_by(is_active=True).all()
    return render_template('processes/create.html', norms=norms)

@processes_bp.route('/<int:id>')
@login_required
def view(id):
    """Visualizar processo com fluxo"""
    process = Process.query.get_or_404(id)
    return render_template('processes/view.html', process=process)

@processes_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar processo"""
    process = Process.query.get_or_404(id)
    
    if request.method == 'POST':
        process.name = request.form['name']
        process.code = request.form.get('code', '')
        process.description = request.form.get('description', '')
        
        # Parse inputs, outputs, responsibilities, risks
        inputs = []
        outputs = []
        responsibilities = []
        risks = []
        
        input_names = request.form.getlist('input_name[]')
        input_descriptions = request.form.getlist('input_description[]')
        for i, name_val in enumerate(input_names):
            if name_val.strip():
                inputs.append({
                    'name': name_val,
                    'description': input_descriptions[i] if i < len(input_descriptions) else ''
                })
        
        output_names = request.form.getlist('output_name[]')
        output_descriptions = request.form.getlist('output_description[]')
        for i, name_val in enumerate(output_names):
            if name_val.strip():
                outputs.append({
                    'name': name_val,
                    'description': output_descriptions[i] if i < len(output_descriptions) else ''
                })
        
        resp_roles = request.form.getlist('resp_role[]')
        resp_descriptions = request.form.getlist('resp_description[]')
        for i, role in enumerate(resp_roles):
            if role.strip():
                responsibilities.append({
                    'role': role,
                    'description': resp_descriptions[i] if i < len(resp_descriptions) else ''
                })
        
        risk_names = request.form.getlist('risk_name[]')
        risk_descriptions = request.form.getlist('risk_description[]')
        risk_mitigations = request.form.getlist('risk_mitigation[]')
        for i, risk_name in enumerate(risk_names):
            if risk_name.strip():
                risks.append({
                    'name': risk_name,
                    'description': risk_descriptions[i] if i < len(risk_descriptions) else '',
                    'mitigation': risk_mitigations[i] if i < len(risk_mitigations) else ''
                })
        
        process.inputs = inputs if inputs else None
        process.outputs = outputs if outputs else None
        process.responsibilities = responsibilities if responsibilities else None
        process.risks = risks if risks else None
        process.updated_at = datetime.utcnow()
        
        # Update norms association
        process.norms.clear()
        norm_ids = request.form.getlist('norm_ids')
        if norm_ids:
            norms = Norm.query.filter(Norm.id.in_(norm_ids)).all()
            process.norms.extend(norms)
        
        db.session.commit()
        flash('Processo atualizado com sucesso!', 'success')
        return redirect(url_for('processes.view', id=id))
    
    norms = Norm.query.filter_by(is_active=True).all()
    return render_template('processes/edit.html', process=process, norms=norms)

@processes_bp.route('/matrix')
@login_required
def matrix():
    """Matriz de processos por norma"""
    processes = Process.query.all()
    norms = Norm.query.filter_by(is_active=True).all()
    
    matrix_data = []
    for process in processes:
        process_data = {
            'process': process,
            'norm_compliance': {}
        }
        
        for norm in norms:
            is_compliant = norm in process.norms
            process_data['norm_compliance'][norm.id] = is_compliant
        
        matrix_data.append(process_data)
    
    return render_template('processes/matrix.html', matrix_data=matrix_data, norms=norms)

@processes_bp.route('/api/process-data/<int:id>')
@login_required
def process_api(id):
    """API endpoint para dados do processo"""
    process = Process.query.get_or_404(id)
    
    data = {
        'id': process.id,
        'name': process.name,
        'code': process.code,
        'description': process.description,
        'inputs': process.inputs or [],
        'outputs': process.outputs or [],
        'responsibilities': process.responsibilities or [],
        'risks': process.risks or [],
        'norms': [{'id': n.id, 'name': n.name, 'code': n.code} for n in process.norms]
    }
    
    return jsonify(data)
