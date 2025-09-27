from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    AUDITOR = "auditor"
    REVIEWER = "reviewer"

class DocumentStatus(Enum):
    DRAFT = "draft"        # Redigindo
    REVIEW = "review"      # Em revisão
    PUBLISHED = "published" # Publicado
    ARCHIVED = "archived"   # Arquivado

class AuditType(Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relacionamentos
    created_documents = db.relationship('Document', foreign_keys='Document.created_by_id', backref='creator', lazy='dynamic')
    assigned_audits = db.relationship('Audit', foreign_keys='Audit.assigned_auditor_id', backref='assigned_auditor', lazy='dynamic')

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos many-to-many com usuários
    members = db.relationship('User', secondary='team_members', backref='teams')

# Tabela de associação para Team-User
team_members = db.Table('team_members',
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Norm(db.Model):
    __tablename__ = 'norms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False)  # Ex: ISO9001, ONA, RDC
    description = db.Column(db.Text)
    version = db.Column(db.String(50))
    effective_date = db.Column(db.Date)
    review_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Custom fields (JSON for flexibility)
    custom_fields = db.Column(db.JSON)

class DocumentFolder(db.Model):
    __tablename__ = 'document_folders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('document_folders.id'))
    path = db.Column(db.String(500))  # Full path for easy querying
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship
    children = db.relationship('DocumentFolder', backref=db.backref('parent', remote_side=[id]))

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), unique=True)  # Código do documento
    content = db.Column(db.Text)  # Rich text content from editor
    version = db.Column(db.String(50), default='1.0')
    status = db.Column(db.Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    
    # Workflow fields
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    published_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    review_deadline = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    effective_date = db.Column(db.Date)
    review_date = db.Column(db.Date)
    
    # Organization
    folder_id = db.Column(db.Integer, db.ForeignKey('document_folders.id'))
    category = db.Column(db.String(100))
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Electronic signature
    signature_required = db.Column(db.Boolean, default=False)
    signature_data = db.Column(db.JSON)  # Digital signature info
    
    # Relacionamentos
    folder = db.relationship('DocumentFolder', backref='documents')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by_id])
    publisher = db.relationship('User', foreign_keys=[published_by_id])
    
    # Many-to-many with norms
    norms = db.relationship('Norm', secondary='document_norms', backref='documents')

# Tabela de associação Document-Norm
document_norms = db.Table('document_norms',
    db.Column('document_id', db.Integer, db.ForeignKey('documents.id'), primary_key=True),
    db.Column('norm_id', db.Integer, db.ForeignKey('norms.id'), primary_key=True)
)

class DocumentVersion(db.Model):
    __tablename__ = 'document_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)  # Snapshot of content
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    change_notes = db.Column(db.Text)
    
    # Relacionamentos
    document = db.relationship('Document', backref='versions')
    created_by = db.relationship('User')

class DocumentAttachment(db.Model):
    __tablename__ = 'document_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    document = db.relationship('Document', backref='attachments')
    uploaded_by = db.relationship('User')

class DocumentRead(db.Model):
    __tablename__ = 'document_reads'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)  # User confirmed reading
    confirmation_date = db.Column(db.DateTime)
    
    # Relacionamentos
    document = db.relationship('Document', backref='reads')
    user = db.relationship('User', backref='document_reads')

class Audit(db.Model):
    __tablename__ = 'audits'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    audit_type = db.Column(db.Enum(AuditType), nullable=False)
    norm_id = db.Column(db.Integer, db.ForeignKey('norms.id'))
    
    # Audit details
    location = db.Column(db.String(255))
    planned_date = db.Column(db.Date)
    actual_date = db.Column(db.Date)
    assigned_auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status and progress
    status = db.Column(db.String(50), default='planned')  # planned, in_progress, completed, cancelled
    progress_percentage = db.Column(db.Integer, default=0)
    
    # Content
    objectives = db.Column(db.Text)
    scope = db.Column(db.Text)
    findings = db.Column(db.Text)
    conclusion = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    norm = db.relationship('Norm', backref='audits')
    responsible = db.relationship('User', foreign_keys=[responsible_id])

class NonConformity(db.Model):
    __tablename__ = 'non_conformities'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50))  # minor, major, critical
    requirement = db.Column(db.String(255))  # Which norm requirement
    
    # Status
    status = db.Column(db.String(50), default='open')  # open, in_progress, resolved, closed
    
    # Dates
    identified_date = db.Column(db.Date, default=datetime.utcnow().date())
    target_resolution_date = db.Column(db.Date)
    actual_resolution_date = db.Column(db.Date)
    
    # Responsible
    identified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    audit = db.relationship('Audit', backref='non_conformities')
    identified_by = db.relationship('User', foreign_keys=[identified_by_id])
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])

class Process(db.Model):
    __tablename__ = 'processes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    
    # Process mapping fields (tabular structure from spec)
    inputs = db.Column(db.JSON)  # List of inputs
    outputs = db.Column(db.JSON)  # List of outputs
    responsibilities = db.Column(db.JSON)  # List of responsible parties
    risks = db.Column(db.JSON)  # List of identified risks
    
    # Flowchart attachment
    flowchart_path = db.Column(db.String(500))  # Path to flowchart file
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many with norms
    norms = db.relationship('Norm', secondary='process_norms', backref='processes')

# Tabela de associação Process-Norm
process_norms = db.Table('process_norms',
    db.Column('process_id', db.Integer, db.ForeignKey('processes.id'), primary_key=True),
    db.Column('norm_id', db.Integer, db.ForeignKey('norms.id'), primary_key=True)
)

class ImprovementStatus(Enum):
    PLAN = "plan"        # Planejar
    DO = "do"           # Executar
    CHECK = "check"     # Verificar
    ACT = "act"         # Agir
    COMPLETED = "completed"

class NotificationType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    URGENT = "urgent"

class CIPAMeeting(db.Model):
    """Reuniões da Comissão Interna de Prevenção de Acidentes (CIPA)"""
    __tablename__ = 'cipa_meetings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    meeting_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    agenda = db.Column(db.Text)
    minutes = db.Column(db.Text)  # Ata da reunião
    decisions = db.Column(db.Text)
    next_meeting_date = db.Column(db.DateTime)

    # Participantes
    chairperson_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    secretary_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Status e controle
    status = db.Column(db.String(50), default='scheduled')  # scheduled, in_progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    chairperson = db.relationship('User', foreign_keys=[chairperson_id])
    secretary = db.relationship('User', foreign_keys=[secretary_id])
    attendees = db.relationship('User', secondary='cipa_attendees', backref='cipa_meetings')

# Tabela de associação CIPA-Participantes
cipa_attendees = db.Table('cipa_attendees',
    db.Column('cipa_meeting_id', db.Integer, db.ForeignKey('cipa_meetings.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class ImprovementCycle(db.Model):
    """Ciclos de Melhoria (PDCA)"""
    __tablename__ = 'improvement_cycles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # qualidade, segurança, eficiência, etc.

    # PDCA phases
    plan_description = db.Column(db.Text)
    do_description = db.Column(db.Text)
    check_description = db.Column(db.Text)
    act_description = db.Column(db.Text)

    # Status e progresso
    current_phase = db.Column(db.Enum(ImprovementStatus), default=ImprovementStatus.PLAN)
    status = db.Column(db.String(50), default='active')  # active, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical

    # Datas
    start_date = db.Column(db.Date, default=datetime.utcnow().date())
    target_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)

    # Responsáveis
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Métricas
    baseline_metric = db.Column(db.String(255))  # Métrica inicial
    target_metric = db.Column(db.String(255))    # Meta
    actual_metric = db.Column(db.String(255))    # Resultado alcançado

    # Relacionamentos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = db.relationship('User', foreign_keys=[created_by_id])
    responsible = db.relationship('User', foreign_keys=[responsible_id])

class Notification(db.Model):
    """Sistema de Notificações"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(NotificationType), default=NotificationType.INFO)

    # Destinatários
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))  # Para notificações de equipe

    # Controle de leitura
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    # Metadados
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    category = db.Column(db.String(100))  # sistema, documento, auditoria, etc.
    action_url = db.Column(db.String(500))  # Link para ação

    # Relacionamentos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Data de expiração

    recipient = db.relationship('User', backref='notifications')
    team = db.relationship('Team', backref='notifications')

class OperationalEvent(db.Model):
    """Eventos Operacionais para Kanban"""
    __tablename__ = 'operational_events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # manutenção, calibração, inspeção, etc.

    # Kanban columns
    status = db.Column(db.String(50), default='todo')  # todo, in_progress, review, done

    # Prioridade e urgência
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    due_date = db.Column(db.DateTime)

    # Responsáveis
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relacionamentos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])

class EmailTemplate(db.Model):
    """Templates de e-mail para notificações do QMS"""
    __tablename__ = 'email_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nome do template
    subject = db.Column(db.String(255), nullable=False)  # Assunto do e-mail
    body_html = db.Column(db.Text, nullable=False)  # Corpo HTML
    body_text = db.Column(db.Text)  # Corpo texto plano (opcional)
    event_type = db.Column(db.String(50), nullable=False)  # Tipo de evento (document_approved, capa_created, etc.)

    # Controle de versão
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)

    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def render_subject(self, context=None):
        """Renderiza o assunto com contexto"""
        if context:
            return self.subject.format(**context)
        return self.subject

    def render_body_html(self, context=None):
        """Renderiza o corpo HTML com contexto"""
        if context:
            return self.body_html.format(**context)
        return self.body_html

    def render_body_text(self, context=None):
        """Renderiza o corpo texto com contexto"""
        if self.body_text and context:
            return self.body_text.format(**context)
        elif self.body_text:
            return self.body_text
        # Fallback: converter HTML para texto
        import re
        text = re.sub(r'<[^>]+>', '', self.body_html)
        return text.strip()

class EmailQueue(db.Model):
    """Fila de e-mails para envio assíncrono"""
    __tablename__ = 'email_queue'

    id = db.Column(db.Integer, primary_key=True)

    # Destinatários
    to_email = db.Column(db.String(255), nullable=False)
    to_name = db.Column(db.String(255))
    cc_emails = db.Column(db.JSON)  # Lista de e-mails CC
    bcc_emails = db.Column(db.JSON)  # Lista de e-mails BCC

    # Conteúdo
    subject = db.Column(db.String(255), nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    body_text = db.Column(db.Text)

    # Controle de envio
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed, cancelled
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent

    # Tentativas de envio
    max_retries = db.Column(db.Integer, default=3)
    retry_count = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime)
    next_attempt = db.Column(db.DateTime)

    # Metadados
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'))
    event_type = db.Column(db.String(50))  # Tipo de evento que gerou o e-mail
    context_data = db.Column(db.JSON)  # Dados do contexto para reenvio

    # Logs
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)

    # Relacionamentos
    template = db.relationship('EmailTemplate', backref='queued_emails')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def mark_sent(self):
        """Marca e-mail como enviado"""
        self.status = 'sent'
        self.sent_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error_message=None):
        """Marca e-mail como falha"""
        self.status = 'failed'
        self.error_message = error_message
        self.last_attempt = datetime.utcnow()
        self.retry_count += 1

        # Calcular próximo tentativa (exponential backoff)
        if self.retry_count < self.max_retries:
            delay_minutes = 2 ** self.retry_count  # 2, 4, 8 minutos
            self.next_attempt = datetime.utcnow() + timedelta(minutes=delay_minutes)
            self.status = 'pending'
        else:
            self.status = 'failed'

        self.updated_at = datetime.utcnow()

class NotificationPreference(db.Model):
    """Preferências de notificação por usuário"""
    __tablename__ = 'notification_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Tipos de notificação
    email_enabled = db.Column(db.Boolean, default=True)
    whatsapp_enabled = db.Column(db.Boolean, default=False)  # Para futuro

    # Eventos específicos
    document_notifications = db.Column(db.Boolean, default=True)  # Novos documentos, aprovações
    audit_notifications = db.Column(db.Boolean, default=True)    # Auditorias, NCs
    capa_notifications = db.Column(db.Boolean, default=True)     # CAPA updates
    operational_notifications = db.Column(db.Boolean, default=True)  # CIPA, melhorias
    system_notifications = db.Column(db.Boolean, default=True)   # Avisos do sistema

    # Frequência
    frequency = db.Column(db.String(20), default='immediate')  # immediate, daily, weekly

    # Relacionamento
    user = db.relationship('User', backref='notification_preferences')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SignatureType(Enum):
    """Tipos de assinatura"""
    APPROVAL = "approval"      # Aprovação de documento
    REVIEW = "review"         # Revisão de documento
    PUBLICATION = "publication" # Publicação de documento
    READING = "reading"       # Confirmação de leitura
    CAPA_APPROVAL = "capa_approval"  # Aprovação de CAPA
    CAPA_IMPLEMENTATION = "capa_implementation"  # Implementação de CAPA
    CAPA_VERIFICATION = "capa_verification"  # Verificação de CAPA

class ElectronicSignature(db.Model):
    """Assinatura Eletrônica Digital"""
    __tablename__ = 'electronic_signatures'

    id = db.Column(db.Integer, primary_key=True)

    # Relacionamentos
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    capa_id = db.Column(db.Integer, db.ForeignKey('capa.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Tipo e contexto
    signature_type = db.Column(db.Enum(SignatureType), nullable=False)
    context = db.Column(db.String(255))  # Ex: "Aprovação versão 1.2"

    # Dados da assinatura
    signature_data = db.Column(db.Text, nullable=False)  # Dados criptográficos
    certificate_info = db.Column(db.JSON)  # Info do certificado digital
    ip_address = db.Column(db.String(45))  # IPv4/IPv6
    user_agent = db.Column(db.Text)  # Browser/device info

    # Status e validação
    is_valid = db.Column(db.Boolean, default=True)
    validation_message = db.Column(db.Text)
    revocation_reason = db.Column(db.Text)

    # Timestamps
    signed_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Data de expiração da assinatura
    revoked_at = db.Column(db.DateTime)

    # Relacionamentos
    document = db.relationship('Document', backref='signatures')
    capa = db.relationship('CAPA', backref='signatures')
    user = db.relationship('User', backref='signatures')

    def generate_signature_hash(self, content: str) -> str:
        """Gera hash criptográfico do conteúdo para assinatura"""
        import hashlib
        return hashlib.sha256(f"{content}{self.signed_at.isoformat()}{self.user_id}".encode()).hexdigest()

    def verify_signature(self, content: str) -> bool:
        """Verifica se a assinatura é válida"""
        expected_hash = self.generate_signature_hash(content)
        return self.signature_data == expected_hash

    def to_dict(self):
        """Converte para dicionário para API/JSON"""
        return {
            'id': self.id,
            'signature_type': self.signature_type.value,
            'context': self.context,
            'user': {
                'id': self.user.id,
                'full_name': self.user.full_name,
                'role': self.user.role.value
            },
            'signed_at': self.signed_at.isoformat(),
            'is_valid': self.is_valid,
            'ip_address': self.ip_address
        }

class CAPAStatus(Enum):
    """Status do CAPA"""
    DRAFT = "draft"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class CAPAType(Enum):
    """Tipo de ação: Corretiva ou Preventiva"""
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"

class CAPA(db.Model):
    """Plano de Ação Corretiva e Preventiva (CAPA)"""
    __tablename__ = 'capa'

    id = db.Column(db.Integer, primary_key=True)
    non_conformity_id = db.Column(db.Integer, db.ForeignKey('non_conformities.id'), nullable=False)

    # Tipo e identificação
    capa_type = db.Column(db.Enum(CAPAType), nullable=False)
    reference_number = db.Column(db.String(50), unique=True)  # Ex: CAPA-2025-001

    # 5W2H - What, Why, Who, When, How, How Much
    what = db.Column(db.Text, nullable=False)  # O que será feito
    why = db.Column(db.Text, nullable=False)  # Por que será feito
    who = db.Column(db.Text, nullable=False)  # Quem fará
    when = db.Column(db.Date, nullable=False)  # Quando será feito
    how = db.Column(db.Text, nullable=False)  # Como será feito
    how_much = db.Column(db.Text)  # Quanto custará (opcional)

    # Status e controle
    status = db.Column(db.Enum(CAPAStatus), default=CAPAStatus.DRAFT)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical

    # Aprovação
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)

    # Implementação
    implemented_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    implemented_at = db.Column(db.DateTime)
    implementation_notes = db.Column(db.Text)

    # Verificação de efetividade
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    verification_method = db.Column(db.Text)  # Como verificar se foi efetivo
    verification_result = db.Column(db.Text)  # Resultado da verificação
    effectiveness_rating = db.Column(db.Integer)  # 1-5 escala de efetividade

    # Datas de controle
    target_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    verification_date = db.Column(db.Date)

    # Responsáveis
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relacionamentos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    non_conformity = db.relationship('NonConformity', backref='capa_plans')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    responsible = db.relationship('User', foreign_keys=[responsible_id])
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    implemented_by = db.relationship('User', foreign_keys=[implemented_by_id])
    verified_by = db.relationship('User', foreign_keys=[verified_by_id])

    def generate_reference_number(self):
        """Gera número de referência único para o CAPA"""
        year = datetime.utcnow().year
        # Conta CAPAs do ano atual
        count = CAPA.query.filter(
            CAPA.created_at >= datetime(year, 1, 1),
            CAPA.created_at < datetime(year + 1, 1, 1)
        ).count() + 1
        self.reference_number = f"CAPA-{year}-{count:03d}"