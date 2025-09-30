from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Document, DocumentFolder, DocumentVersion, DocumentAttachment, DocumentRead, DocumentStatus, Norm, ElectronicSignature, SignatureType, db
from audit_service import AuditService
import os
from datetime import datetime

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/')
@login_required
def index():
    """Lista todos os documentos com filtros"""
    status_filter = request.args.get('status')
    folder_id = request.args.get('folder')
    search = request.args.get('search')
    
    query = Document.query
    
    if status_filter:
        query = query.filter_by(status=DocumentStatus(status_filter))
    
    if folder_id:
        query = query.filter_by(folder_id=folder_id)
    
    if search:
        query = query.filter(Document.title.contains(search))
    
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Items per page for documents

    documents_pagination = query.order_by(Document.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    folders = DocumentFolder.query.all()

    return render_template('documents/index.html', documents_pagination=documents_pagination, folders=folders)

@documents_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Criar novo documento - coração do sistema"""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content', '')  # Rich text from editor
        code = request.form.get('code')
        category = request.form.get('category')
        folder_id = request.form.get('folder_id')
        status = request.form.get('status', 'draft')
        norm_ids = request.form.getlist('norm_ids')

        document = Document(
            title=title,
            content=content,
            code=code,
            category=category,
            folder_id=folder_id if folder_id else None,
            created_by_id=current_user.id,
            status=DocumentStatus(status)
        )
        
        db.session.add(document)
        db.session.flush()  # Get the document ID

        # Associate with norms
        if norm_ids:
            norms = Norm.query.filter(Norm.id.in_(norm_ids)).all()
            document.norms.extend(norms)

        # Create initial version
        version = DocumentVersion(
            document_id=document.id,
            version='1.0',
            content=content,
            created_by_id=current_user.id,
            change_notes='Versão inicial'
        )
        db.session.add(version)

        db.session.commit()

        # Log da criação do documento
        AuditService.log_document_operation(
            document,
            'create',
            details={'initial_version': '1.0', 'norms_count': len(norm_ids) if norm_ids else 0}
        )

        flash('Documento criado com sucesso!', 'success')
        return redirect(url_for('documents.edit', id=document.id))
    
    # GET request - show create form
    folders = DocumentFolder.query.all()
    norms = Norm.query.filter_by(is_active=True).all()
    
    return render_template('documents/create.html', folders=folders, norms=norms)

@documents_bp.route('/<int:id>')
@login_required
def view(id):
    """Visualizar documento"""
    document = Document.query.get_or_404(id)
    
    # Record document read
    read_record = DocumentRead.query.filter_by(
        document_id=id, 
        user_id=current_user.id
    ).first()
    
    if not read_record:
        read_record = DocumentRead(
            document_id=id,
            user_id=current_user.id
        )
        db.session.add(read_record)
        db.session.commit()
    
    return render_template('documents/view.html', document=document)

@documents_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editor completo de documentos - CORAÇÃO DO SISTEMA"""
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if document.created_by_id != current_user.id and current_user.role.value not in ['admin', 'manager']:
        flash('Sem permissão para editar este documento.', 'error')
        return redirect(url_for('documents.view', id=id))
    
    if request.method == 'POST':
        # Update document
        document.title = request.form['title']
        document.content = request.form.get('content', '')  # Rich HTML content
        document.code = request.form.get('code')
        document.category = request.form.get('category')
        document.folder_id = request.form.get('folder_id') if request.form.get('folder_id') else None
        
        # Handle version increment
        if request.form.get('create_new_version') == 'true':
            # Parse current version and increment
            current_version = document.version or '1.0'
            try:
                major, minor = map(int, current_version.split('.'))
                if request.form.get('version_type') == 'major':
                    new_version = f"{major + 1}.0"
                else:
                    new_version = f"{major}.{minor + 1}"
            except:
                new_version = '1.1'
            
            document.version = new_version
            
            # Create version record
            version = DocumentVersion(
                document_id=document.id,
                version=new_version,
                content=document.content,
                created_by_id=current_user.id,
                change_notes=request.form.get('change_notes', '')
            )
            db.session.add(version)
        
        # Update norms association
        document.norms.clear()
        norm_ids = request.form.getlist('norm_ids')
        if norm_ids:
            norms = Norm.query.filter(Norm.id.in_(norm_ids)).all()
            document.norms.extend(norms)
        
        db.session.commit()
        flash('Documento atualizado com sucesso!', 'success')
        return redirect(url_for('documents.view', id=id))
    
    # GET request - show editor
    folders = DocumentFolder.query.all()
    norms = Norm.query.filter_by(is_active=True).all()
    
    return render_template('documents/edit.html', document=document, folders=folders, norms=norms)

@documents_bp.route('/<int:id>/workflow/<action>', methods=['POST'])
@login_required
def workflow_action(id, action):
    """Gerenciar workflow do documento: redação → revisão → publicação → leitura"""
    document = Document.query.get_or_404(id)
    
    if action == 'submit_for_review':
        if document.status == DocumentStatus.DRAFT:
            document.status = DocumentStatus.REVIEW
            reviewer_id = request.form.get('reviewer_id')
            if reviewer_id:
                document.reviewed_by_id = reviewer_id
            document.review_deadline = datetime.strptime(request.form['review_deadline'], '%Y-%m-%d').date() if request.form.get('review_deadline') else None
            flash('Documento enviado para revisão!', 'success')
        
    elif action == 'approve':
        if document.status == DocumentStatus.REVIEW and current_user.id == document.reviewed_by_id:
            document.status = DocumentStatus.PUBLISHED
            document.published_by_id = current_user.id
            document.published_at = datetime.utcnow()
            flash('Documento aprovado e publicado!', 'success')
    
    elif action == 'reject':
        if document.status == DocumentStatus.REVIEW and current_user.id == document.reviewed_by_id:
            document.status = DocumentStatus.DRAFT
            rejection_reason = request.form.get('rejection_reason', '')
            flash(f'Documento rejeitado. Motivo: {rejection_reason}', 'warning')
    
    elif action == 'archive':
        document.status = DocumentStatus.ARCHIVED
        flash('Documento arquivado.', 'info')
    
    db.session.commit()
    return redirect(url_for('documents.view', id=id))

@documents_bp.route('/<int:id>/confirm-read', methods=['POST'])
@login_required
def confirm_read(id):
    """Confirmar leitura do documento"""
    read_record = DocumentRead.query.filter_by(
        document_id=id,
        user_id=current_user.id
    ).first()
    
    if read_record:
        read_record.confirmed = True
        read_record.confirmation_date = datetime.utcnow()
        db.session.commit()
        flash('Leitura confirmada!', 'success')
    
    return redirect(url_for('documents.view', id=id))

@documents_bp.route('/<int:id>/upload-attachment', methods=['POST'])
@login_required
def upload_attachment(id):
    """Upload de anexos para documentos"""
    document = Document.query.get_or_404(id)
    
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('documents.edit', id=id))
    
    @documents_bp.route('/upload-image', methods=['POST'])
    @login_required
    def upload_image():
        """Upload de imagens para o editor TinyMCE"""
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Arquivo sem nome'}), 400
    
        if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            filename = secure_filename(file.filename)
            # Create unique filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
    
            # Save file
            upload_folder = current_app.config['UPLOAD_FOLDER']
            image_path = os.path.join(upload_folder, 'images')
            os.makedirs(image_path, exist_ok=True)
            full_file_path = os.path.join(image_path, unique_filename)
            file.save(full_file_path)
    
            # Return URL for TinyMCE
            image_url = f"/static/uploads/images/{unique_filename}"
            return jsonify({'location': image_url})
    
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    def allowed_file(filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('documents.edit', id=id))
    
    if file:
        filename = secure_filename(file.filename)
        # Create unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Save file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', str(id))
        os.makedirs(file_path, exist_ok=True)
        full_file_path = os.path.join(file_path, unique_filename)
        file.save(full_file_path)
        
        # Create database record
        attachment = DocumentAttachment(
            document_id=id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=full_file_path,
            file_size=os.path.getsize(full_file_path),
            uploaded_by_id=current_user.id
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        flash('Anexo carregado com sucesso!', 'success')

    return redirect(url_for('documents.edit', id=id))

# ==================== ELECTRONIC SIGNATURES ====================

@documents_bp.route('/<int:id>/sign/<signature_type>', methods=['GET', 'POST'])
@login_required
def sign_document(id, signature_type):
    """Assinar documento eletronicamente"""
    document = Document.query.get_or_404(id)

    # Validate signature type
    try:
        sig_type = SignatureType(signature_type)
    except ValueError:
        flash('Tipo de assinatura inválido.', 'error')
        return redirect(url_for('documents.view', id=id))

    # Check permissions based on signature type
    if sig_type == SignatureType.APPROVAL and document.status != DocumentStatus.REVIEW:
        flash('Documento deve estar em revisão para aprovação.', 'error')
        return redirect(url_for('documents.view', id=id))

    if sig_type == SignatureType.REVIEW and document.status != DocumentStatus.REVIEW:
        flash('Documento deve estar em revisão para ser revisado.', 'error')
        return redirect(url_for('documents.view', id=id))

    if sig_type == SignatureType.PUBLICATION and document.status != DocumentStatus.REVIEW:
        flash('Documento deve estar em revisão para publicação.', 'error')
        return redirect(url_for('documents.view', id=id))

    # Check if user already signed this type
    existing_signature = ElectronicSignature.query.filter_by(
        document_id=id,
        user_id=current_user.id,
        signature_type=sig_type
    ).first()

    if existing_signature:
        flash('Você já assinou este documento neste contexto.', 'warning')
        return redirect(url_for('documents.view', id=id))

    if request.method == 'POST':
        # Obter certificado do formulário (em produção, viria de um repositório seguro)
        certificate_pem = request.form.get('certificate_pem', '')
        private_key_pem = request.form.get('private_key_pem', '')  # Apenas para teste

        # Create electronic signature
        signature = ElectronicSignature(
            document_id=id,
            user_id=current_user.id,
            signature_type=sig_type,
            context=f"Assinatura de {sig_type.value} - {document.title} v{document.version}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            certificate_info={
                'user_id': current_user.id,
                'user_name': current_user.full_name,
                'user_email': current_user.email,
                'timestamp': datetime.utcnow().isoformat(),
                'has_certificate': bool(certificate_pem)
            }
        )

        # Preparar conteúdo para assinatura
        content_to_sign = f"{document.title}{document.content}{document.version}{current_user.id}{datetime.utcnow().isoformat()}"

        # Assinar com certificado se disponível
        if certificate_pem:
            success = signature.sign_with_certificate(content_to_sign, certificate_pem, private_key_pem)
            if not success:
                flash('Erro na assinatura digital. Verifique o certificado.', 'error')
                return redirect(url_for('documents.view', id=id))
        else:
            # Fallback para assinatura simples (não legalmente válida)
            signature.signature_data = signature.generate_signature_hash(content_to_sign)
            signature.validation_status = 'pending'
            flash('Assinatura realizada sem certificado digital. Para validade legal, use certificado ICP-Brasil.', 'warning')

        db.session.add(signature)

        # Log da operação de assinatura
        AuditService.log_signature_operation(
            signature,
            'sign',
            details={
                'document_title': document.title,
                'document_version': document.version,
                'signature_type': sig_type.value,
                'has_certificate': bool(certificate_pem)
            }
        )

        # Update document status based on signature type
        if sig_type == SignatureType.APPROVAL:
            document.status = DocumentStatus.PUBLISHED
            document.published_by_id = current_user.id
            document.published_at = datetime.utcnow()

            # Send notification to document creator
            try:
                from email_service import notification_service
                notification_service.send_notification(
                    user_id=document.created_by_id,
                    event_type='document_approved',
                    context_data={
                        'document_title': document.title,
                        'document_code': document.code,
                        'document_version': document.version,
                        'approved_by': current_user.full_name,
                        'document_url': url_for('documents.view', id=document.id, _external=True)
                    },
                    priority='high'
                )
            except Exception as e:
                print(f"Warning: Could not send document approval notification: {e}")

            flash('Documento aprovado e publicado com sucesso!', 'success')

        elif sig_type == SignatureType.REVIEW:
            document.reviewed_by_id = current_user.id
            flash('Documento revisado com sucesso!', 'success')

        db.session.commit()

        return redirect(url_for('documents.view', id=id))

    return render_template('documents/sign.html', document=document, signature_type=sig_type)

@documents_bp.route('/<int:id>/signatures')
@login_required
def document_signatures(id):
    """Ver histórico de assinaturas do documento"""
    document = Document.query.get_or_404(id)

    signatures = ElectronicSignature.query.filter_by(document_id=id).order_by(
        ElectronicSignature.signed_at.desc()
    ).all()

    return render_template('documents/signatures.html', document=document, signatures=signatures)

@documents_bp.route('/<int:id>/verify-signatures')
@login_required
def verify_signatures(id):
    """Verificar validade das assinaturas do documento"""
    document = Document.query.get_or_404(id)

    signatures = ElectronicSignature.query.filter_by(document_id=id).all()
    verification_results = []

    for signature in signatures:
        content_to_verify = f"{document.title}{document.content}{document.version}{signature.user_id}{signature.signed_at.isoformat()}"
        is_valid = signature.verify_signature(content_to_verify)

        verification_results.append({
            'signature': signature,
            'is_valid': is_valid,
            'expected_hash': signature.generate_signature_hash(content_to_verify),
            'actual_hash': signature.signature_data
        })

    return render_template('documents/verify_signatures.html',
                         document=document,
                         verification_results=verification_results)

@documents_bp.route('/api/signatures/<int:id>')
@login_required
def signatures_api(id):
    """API para obter assinaturas de um documento"""
    signatures = ElectronicSignature.query.filter_by(document_id=id).order_by(
        ElectronicSignature.signed_at.desc()
    ).all()

    return jsonify([sig.to_dict() for sig in signatures])