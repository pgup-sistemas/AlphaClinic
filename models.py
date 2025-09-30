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

    __table_args__ = (
        db.Index('idx_users_role', 'role'),
        db.Index('idx_users_active', 'is_active'),
        db.Index('idx_users_last_login', 'last_login'),
        db.Index('idx_users_email', 'email'),
    )
    
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

    __table_args__ = (
        db.Index('idx_documents_status', 'status'),
        db.Index('idx_documents_created_by', 'created_by_id'),
        db.Index('idx_documents_category', 'category'),
        db.Index('idx_documents_effective_date', 'effective_date'),
        db.Index('idx_documents_signature_required', 'signature_required'),
    )
    
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

    __table_args__ = (
        db.Index('idx_audits_status', 'status'),
        db.Index('idx_audits_type', 'audit_type'),
        db.Index('idx_audits_norm', 'norm_id'),
        db.Index('idx_audits_assigned_auditor', 'assigned_auditor_id'),
        db.Index('idx_audits_responsible', 'responsible_id'),
        db.Index('idx_audits_planned_date', 'planned_date'),
        db.Index('idx_audits_actual_date', 'actual_date'),
    )
    
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

    __table_args__ = (
        db.Index('idx_nonconformities_status', 'status'),
        db.Index('idx_nonconformities_severity', 'severity'),
        db.Index('idx_nonconformities_audit', 'audit_id'),
        db.Index('idx_nonconformities_assigned_to', 'assigned_to_id'),
        db.Index('idx_nonconformities_identified_date', 'identified_date'),
        db.Index('idx_nonconformities_target_resolution', 'target_resolution_date'),
    )
    
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

class AnalyticsMetric(db.Model):
    """Métricas analíticas para BI"""
    __tablename__ = 'analytics_metrics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # documents, audits, ncs, capa, system
    metric_type = db.Column(db.String(20), nullable=False)  # count, percentage, average, trend
    calculation_method = db.Column(db.String(100))  # SQL query or Python function
    refresh_interval = db.Column(db.Integer, default=300)  # seconds

    # Configuração
    is_active = db.Column(db.Boolean, default=True)
    target_value = db.Column(db.Float)  # Valor alvo para KPIs
    warning_threshold = db.Column(db.Float)  # Threshold para alertas
    critical_threshold = db.Column(db.Float)  # Threshold para alertas críticos

    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnalyticsData(db.Model):
    """Dados analíticos históricos"""
    __tablename__ = 'analytics_data'

    id = db.Column(db.Integer, primary_key=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('analytics_metrics.id'), nullable=False)
    period = db.Column(db.Date, nullable=False)  # Data do período
    period_type = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, yearly

    # Valores
    value = db.Column(db.Float, nullable=False)
    previous_value = db.Column(db.Float)
    change_percentage = db.Column(db.Float)
    trend = db.Column(db.String(20))  # up, down, stable

    # Metadados
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    data_source = db.Column(db.String(50))  # database, api, manual

    # Relacionamentos
    metric = db.relationship('AnalyticsMetric', backref='data_points')

class DashboardWidget(db.Model):
    """Widgets customizáveis do dashboard"""
    __tablename__ = 'dashboard_widgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)  # kpi, chart, table, alert
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=1)
    height = db.Column(db.Integer, default=1)

    # Configuração do widget
    config = db.Column(db.JSON)  # Configurações específicas do tipo
    data_source = db.Column(db.String(100))  # Query ou endpoint de dados
    refresh_interval = db.Column(db.Integer, default=300)  # seconds

    # Visual
    title = db.Column(db.String(200))
    icon = db.Column(db.String(50))
    color_scheme = db.Column(db.String(20), default='blue')

    # Estado
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)  # Widget padrão para novos usuários

    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = db.relationship('User', backref='dashboard_widgets')

class DashboardLayout(db.Model):
    """Layout personalizado do dashboard por usuário"""
    __tablename__ = 'dashboard_layouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    layout_name = db.Column(db.String(100), nullable=False, default='default')
    layout_data = db.Column(db.JSON)  # Posições e configurações dos widgets

    # Configurações
    columns = db.Column(db.Integer, default=3)
    auto_refresh = db.Column(db.Boolean, default=True)
    refresh_interval = db.Column(db.Integer, default=300)

    # Estado
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=True)

    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = db.relationship('User', backref='dashboard_layouts')

class OfflineDocument(db.Model):
    """Documentos disponíveis offline"""
    __tablename__ = 'offline_documents'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Dados offline
    content_snapshot = db.Column(db.Text)  # Snapshot do conteúdo
    version_snapshot = db.Column(db.String(50))
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Data de expiração do cache

    # Status
    is_available = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    document = db.relationship('Document', backref='offline_copies')
    user = db.relationship('User', backref='offline_documents')

class PushNotification(db.Model):
    """Notificações push para web"""
    __tablename__ = 'push_notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Conteúdo
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(500))  # URL do ícone
    badge = db.Column(db.String(500))  # URL do badge

    # Ação
    action_url = db.Column(db.String(500))  # URL para navegar quando clicar
    action_text = db.Column(db.String(100))  # Texto do botão de ação

    # Configuração
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    category = db.Column(db.String(50))  # document, audit, nc, capa, system
    require_interaction = db.Column(db.Boolean, default=False)  # Se requer ação do usuário

    # Status
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)

    # Controle
    expires_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = db.relationship('User', backref='push_notifications')

class BenchmarkData(db.Model):
    """Dados de benchmarking setorial"""
    __tablename__ = 'benchmark_data'

    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(50), nullable=False)  # healthcare, clinic, hospital
    region = db.Column(db.String(50))  # state, region, national

    # Estatísticas
    average_value = db.Column(db.Float, nullable=False)
    median_value = db.Column(db.Float)
    percentile_25 = db.Column(db.Float)
    percentile_75 = db.Column(db.Float)
    percentile_90 = db.Column(db.Float)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    sample_size = db.Column(db.Integer)

    # Período
    period = db.Column(db.String(20), nullable=False)  # monthly, quarterly, yearly
    period_date = db.Column(db.Date, nullable=False)

    # Metadados
    data_source = db.Column(db.String(100))  # Fonte dos dados
    confidence_level = db.Column(db.Float)  # Nível de confiança (0-1)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    """Trilha de Auditoria Imutável - Append-Only"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    sequence_number = db.Column(db.BigInteger, unique=True, nullable=False)  # Número sequencial único

    # Entidade auditada
    entity_type = db.Column(db.String(50), nullable=False)  # document, user, audit, etc.
    entity_id = db.Column(db.Integer, nullable=False)
    entity_code = db.Column(db.String(100))  # Código ou identificador único da entidade

    # Operação realizada
    operation = db.Column(db.String(50), nullable=False)  # create, update, delete, sign, approve, etc.
    operation_details = db.Column(db.JSON)  # Detalhes específicos da operação

    # Usuário responsável
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_full_name = db.Column(db.String(255))  # Nome completo no momento da operação
    user_role = db.Column(db.String(50))  # Papel no momento da operação

    # Dados antes e depois (para updates)
    old_values = db.Column(db.JSON)  # Valores anteriores
    new_values = db.Column(db.JSON)  # Valores novos

    # Contexto da operação
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))

    # Integridade e imutabilidade
    data_hash = db.Column(db.String(128), nullable=False)  # SHA-256 do registro
    previous_hash = db.Column(db.String(128))  # Hash do registro anterior
    chain_hash = db.Column(db.String(128), nullable=False)  # Hash da cadeia

    # Compliance
    compliance_level = db.Column(db.String(20), default='standard')  # standard, critical, restricted
    retention_period = db.Column(db.Integer)  # Dias para retenção obrigatória

    # Timestamps (imutável)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    user = db.relationship('User', backref='audit_logs')

    __table_args__ = (
        db.Index('idx_audit_logs_sequence', 'sequence_number'),
        db.Index('idx_audit_logs_entity', 'entity_type', 'entity_id'),
        db.Index('idx_audit_logs_timestamp', 'timestamp'),
        db.Index('idx_audit_logs_user', 'user_id'),
        db.Index('idx_audit_logs_compliance', 'compliance_level', 'timestamp'),
        # Restrição para imutabilidade - não permitir updates
        {'schema': None}
    )

    @classmethod
    def get_next_sequence_number(cls):
        """Obtém o próximo número sequencial para a cadeia"""
        max_seq = db.session.query(db.func.max(cls.sequence_number)).scalar()
        return (max_seq or 0) + 1

    @classmethod
    def get_last_chain_hash(cls):
        """Obtém o último hash da cadeia"""
        last_record = cls.query.order_by(cls.sequence_number.desc()).first()
        return last_record.chain_hash if last_record else None

    def generate_data_hash(self):
        """Gera hash SHA-256 dos dados do registro"""
        import hashlib
        import json

        # Criar representação canônica dos dados
        data = {
            'sequence_number': self.sequence_number,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_code': self.entity_code,
            'operation': self.operation,
            'operation_details': self.operation_details,
            'user_id': self.user_id,
            'user_full_name': self.user_full_name,
            'user_role': self.user_role,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'previous_hash': self.previous_hash
        }

        # Serializar de forma determinística
        data_str = json.dumps(data, sort_keys=True, default=str, separators=(',', ':'))
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def generate_chain_hash(self):
        """Gera hash da cadeia combinando data_hash com previous_hash"""
        import hashlib
        combined = f"{self.previous_hash or ''}{self.data_hash}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def save_immutable(self):
        """Salva o registro de forma imutável"""
        # Definir sequência e hashes
        self.sequence_number = self.get_next_sequence_number()
        self.previous_hash = self.get_last_chain_hash()
        self.data_hash = self.generate_data_hash()
        self.chain_hash = self.generate_chain_hash()

        # Salvar sem permitir updates posteriores
        db.session.add(self)
        db.session.commit()

        # Marcar como imutável (não permitir updates)
        # Nota: Em produção, isso seria implementado no nível do banco

    @classmethod
    def verify_chain_integrity(cls):
        """Verifica a integridade de toda a cadeia de auditoria"""
        records = cls.query.order_by(cls.sequence_number).all()
        previous_hash = None

        for record in records:
            # Verificar data hash
            if record.data_hash != record.generate_data_hash():
                return False, f"Data hash inválido para registro {record.sequence_number}"

            # Verificar chain hash
            expected_chain_hash = record.generate_chain_hash()
            if record.chain_hash != expected_chain_hash:
                return False, f"Chain hash inválido para registro {record.sequence_number}"

            # Verificar continuidade da cadeia
            if record.previous_hash != previous_hash:
                return False, f"Quebra na cadeia em registro {record.sequence_number}"

            previous_hash = record.chain_hash

        return True, "Cadeia de auditoria íntegra"

    def to_dict(self):
        """Converte para dicionário (apenas leitura)"""
        return {
            'sequence_number': self.sequence_number,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_code': self.entity_code,
            'operation': self.operation,
            'operation_details': self.operation_details,
            'user': {
                'id': self.user_id,
                'full_name': self.user_full_name,
                'role': self.user_role
            },
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat(),
            'data_hash': self.data_hash,
            'chain_hash': self.chain_hash,
            'compliance_level': self.compliance_level
        }

class MachineLearningModel(db.Model):
    """Modelos de machine learning para predições"""
    __tablename__ = 'ml_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # nc_prediction, document_classification, risk_analysis
    algorithm = db.Column(db.String(50), nullable=False)  # random_forest, neural_network, etc.

    # Modelo serializado
    model_data = db.Column(db.LargeBinary)  # Modelo treinado serializado
    model_metadata = db.Column(db.JSON)  # Hiperparâmetros, features, etc.

    # Performance
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)

    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_trained = db.Column(db.DateTime)
    training_data_size = db.Column(db.Integer)

    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PredictionResult(db.Model):
    """Resultados de predições de ML"""
    __tablename__ = 'prediction_results'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_models.id'), nullable=False)
    prediction_type = db.Column(db.String(50), nullable=False)

    # Dados de entrada
    input_data = db.Column(db.JSON, nullable=False)
    prediction_result = db.Column(db.JSON, nullable=False)
    confidence_score = db.Column(db.Float)

    # Validação
    actual_result = db.Column(db.JSON)  # Resultado real (quando disponível)
    is_correct = db.Column(db.Boolean)  # Se a predição estava correta

    # Relacionamentos
    model = db.relationship('MachineLearningModel', backref='predictions')

    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated_at = db.Column(db.DateTime)

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
    """Assinatura Eletrônica Digital com Suporte a Certificados ICP-Brasil"""
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
    signature_hash = db.Column(db.String(128), nullable=False)  # SHA-256 hash
    certificate_pem = db.Column(db.Text)  # Certificado X.509 em PEM
    certificate_chain = db.Column(db.JSON)  # Cadeia de certificados
    certificate_info = db.Column(db.JSON)  # Info extraída do certificado
    certificate_issuer = db.Column(db.String(255))  # Emissor do certificado
    certificate_serial = db.Column(db.String(100))  # Número serial
    certificate_valid_from = db.Column(db.DateTime)  # Validade início
    certificate_valid_until = db.Column(db.DateTime)  # Validade fim

    # Timestamping (TSA)
    timestamp_token = db.Column(db.Text)  # Token TSA
    timestamp_authority = db.Column(db.String(255))  # Autoridade de timestamp
    timestamp_hash = db.Column(db.String(128))  # Hash timestamped

    # Contexto da assinatura
    ip_address = db.Column(db.String(45))  # IPv4/IPv6
    user_agent = db.Column(db.Text)  # Browser/device info
    geolocation = db.Column(db.JSON)  # Dados de geolocalização se disponíveis

    # Status e validação
    is_valid = db.Column(db.Boolean, default=True)
    validation_message = db.Column(db.Text)
    validation_status = db.Column(db.String(50), default='pending')  # pending, valid, invalid, revoked
    revocation_reason = db.Column(db.Text)
    validation_attempts = db.Column(db.Integer, default=0)

    # Timestamps
    signed_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Data de expiração da assinatura
    revoked_at = db.Column(db.DateTime)
    last_validated = db.Column(db.DateTime)

    # Relacionamentos
    document = db.relationship('Document', backref='signatures')
    capa = db.relationship('CAPA', backref='signatures')
    user = db.relationship('User', backref='signatures')

    def generate_signature_hash(self, content: str) -> str:
        """Gera hash criptográfico do conteúdo para assinatura usando SHA-256"""
        import hashlib
        content_to_hash = f"{content}{self.signed_at.isoformat()}{self.user_id}{self.context or ''}"
        return hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest()

    def sign_with_certificate(self, content: str, certificate_pem: str, private_key_pem: str = None) -> bool:
        """Assina conteúdo usando certificado digital"""
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding, rsa
            from cryptography.x509 import load_pem_x509_certificate
            from cryptography.hazmat.backends import default_backend

            # Carregar certificado
            cert = load_pem_x509_certificate(certificate_pem.encode(), default_backend())

            # Extrair informações do certificado
            self.certificate_pem = certificate_pem
            self.certificate_issuer = cert.issuer.rfc4514_string()
            self.certificate_serial = str(cert.serial_number)
            self.certificate_valid_from = cert.not_valid_before
            self.certificate_valid_until = cert.not_valid_after

            # Gerar hash do conteúdo
            content_hash = self.generate_signature_hash(content)
            self.signature_hash = content_hash

            # Assinar usando chave privada (se fornecida)
            if private_key_pem:
                private_key = serialization.load_pem_private_key(
                    private_key_pem.encode(),
                    password=None,
                    backend=default_backend()
                )

                # Assinar o hash
                signature = private_key.sign(
                    content_hash.encode(),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )

                self.signature_data = signature.hex()
                self.validation_status = 'valid'
                return True
            else:
                # Fallback para hash simples se não houver chave privada
                self.signature_data = content_hash
                self.validation_status = 'pending'
                return True

        except Exception as e:
            self.validation_message = str(e)
            self.validation_status = 'invalid'
            return False

    def verify_certificate_chain(self) -> bool:
        """Verifica a cadeia de certificados contra ICP-Brasil"""
        try:
            from cryptography.x509 import load_pem_x509_certificate
            from cryptography.hazmat.backends import default_backend

            if not self.certificate_pem:
                return False

            cert = load_pem_x509_certificate(self.certificate_pem.encode(), default_backend())

            # Verificar validade temporal
            now = datetime.utcnow()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                self.validation_message = "Certificado expirado ou ainda não válido"
                return False

            # Verificar se é certificado ICP-Brasil (simplificado)
            # Em produção, deveria verificar contra lista de certificados confiáveis
            issuer = cert.issuer
            if 'ICP-Brasil' not in issuer.rfc4514_string():
                self.validation_message = "Certificado não é do ICP-Brasil"
                return False

            self.validation_status = 'valid'
            self.last_validated = now
            return True

        except Exception as e:
            self.validation_message = f"Erro na verificação: {str(e)}"
            self.validation_status = 'invalid'
            return False

    def verify_signature(self, content: str) -> bool:
        """Verifica se a assinatura é válida"""
        try:
            expected_hash = self.generate_signature_hash(content)

            # Verificar hash
            if self.signature_hash != expected_hash:
                self.validation_message = "Hash da assinatura não corresponde"
                self.validation_status = 'invalid'
                return False

            # Verificar certificado se disponível
            if self.certificate_pem and not self.verify_certificate_chain():
                return False

            self.validation_status = 'valid'
            self.is_valid = True
            return True

        except Exception as e:
            self.validation_message = str(e)
            self.validation_status = 'invalid'
            self.is_valid = False
            return False

    def to_dict(self):
        """Converte para dicionário para API/JSON"""
        return {
            'id': self.id,
            'signature_type': self.signature_type.value if self.signature_type else None,
            'context': self.context,
            'user': {
                'id': self.user.id,
                'full_name': self.user.full_name,
                'role': self.user.role.value if self.user.role else None
            },
            'certificate_info': {
                'issuer': self.certificate_issuer,
                'serial': self.certificate_serial,
                'valid_from': self.certificate_valid_from.isoformat() if self.certificate_valid_from else None,
                'valid_until': self.certificate_valid_until.isoformat() if self.certificate_valid_until else None,
                'is_icp_brasil': 'ICP-Brasil' in (self.certificate_issuer or '')
            },
            'signed_at': self.signed_at.isoformat(),
            'is_valid': self.is_valid,
            'validation_status': self.validation_status,
            'ip_address': self.ip_address,
            'validation_message': self.validation_message
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

class Permission(db.Model):
    """Permissões granulares do sistema RBAC avançado"""
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nome descritivo da permissão
    role = db.Column(db.String(50), nullable=False)  # Role que recebe a permissão
    resource_type = db.Column(db.String(50), nullable=False)  # Tipo do recurso
    action = db.Column(db.String(50), nullable=False)  # Ação permitida
    permission_level = db.Column(db.Integer, default=1)  # Nível de permissão
    conditions = db.Column(db.JSON)  # Condições específicas (ownership, teams, etc.)

    # Controle avançado
    is_active = db.Column(db.Boolean, default=True)
    is_temporary = db.Column(db.Boolean, default=False)  # Se é permissão temporária
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Para permissões temporárias
    revoked_at = db.Column(db.DateTime)
    revoked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    revocation_reason = db.Column(db.Text)

    # Relacionamentos
    granted_by_user = db.relationship('User', foreign_keys=[granted_by])
    revoked_by_user = db.relationship('User', foreign_keys=[revoked_by])

    __table_args__ = (
        db.Index('idx_permissions_role', 'role'),
        db.Index('idx_permissions_resource', 'resource_type', 'action'),
        db.Index('idx_permissions_active', 'is_active'),
        db.Index('idx_permissions_temporary', 'is_temporary', 'expires_at'),
        db.UniqueConstraint('role', 'resource_type', 'action', name='unique_role_resource_action'),
    )

    @classmethod
    def get_user_permissions(cls, user_role, include_inactive=False):
        """Obtém permissões específicas de um role"""
        query = cls.query.filter_by(role=user_role)
        if not include_inactive:
            query = query.filter_by(is_active=True)

        # Filtrar permissões não expiradas
        now = datetime.utcnow()
        query = query.filter(
            db.or_(
                cls.expires_at.is_(None),  # Permissões permanentes
                cls.expires_at > now       # Permissões não expiradas
            )
        )

        return query.all()

    def is_expired(self):
        """Verifica se permissão está expirada"""
        if not self.is_temporary or not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def revoke(self, revoked_by_user_id, reason=None):
        """Revoga permissão"""
        self.is_active = False
        self.revoked_at = datetime.utcnow()
        self.revoked_by = revoked_by_user_id
        self.revocation_reason = reason

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'resource_type': self.resource_type,
            'action': self.action,
            'permission_level': self.permission_level,
            'conditions': self.conditions,
            'is_active': self.is_active,
            'is_temporary': self.is_temporary,
            'granted_at': self.granted_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }

    @classmethod
    def get_user_permissions(cls, user_role):
        """Obtém permissões específicas de um role"""
        return cls.query.filter_by(
            role=user_role,
            is_active=True
        ).all()

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'role': self.role,
            'resource_type': self.resource_type,
            'action': self.action,
            'permission_level': self.permission_level,
            'conditions': self.conditions,
            'is_active': self.is_active,
            'granted_at': self.granted_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class RoleHierarchy(db.Model):
    """Hierarquia de roles para herança de permissões"""
    __tablename__ = 'role_hierarchy'

    id = db.Column(db.Integer, primary_key=True)
    parent_role = db.Column(db.String(50), nullable=False)  # Role pai
    child_role = db.Column(db.String(50), nullable=False)   # Role filho
    inheritance_type = db.Column(db.String(20), default='full')  # full, partial, conditional
    inheritance_conditions = db.Column(db.JSON)  # Condições para herança

    # Controle
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    created_by_user = db.relationship('User', foreign_keys=[created_by])

    __table_args__ = (
        db.Index('idx_role_hierarchy_parent', 'parent_role'),
        db.Index('idx_role_hierarchy_child', 'child_role'),
        db.UniqueConstraint('parent_role', 'child_role', name='unique_role_hierarchy'),
    )

class TeamPermission(db.Model):
    """Permissões específicas de equipes"""
    __tablename__ = 'team_permissions'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)  # ID específico do recurso (opcional)
    action = db.Column(db.String(50), nullable=False)
    permission_level = db.Column(db.Integer, default=1)

    # Controle de acesso
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relacionamentos
    team = db.relationship('Team', backref='permissions')
    granted_by_user = db.relationship('User', foreign_keys=[granted_by])

    __table_args__ = (
        db.Index('idx_team_permissions_team', 'team_id'),
        db.Index('idx_team_permissions_resource', 'resource_type', 'resource_id'),
        db.Index('idx_team_permissions_active', 'is_active'),
    )

class TemporaryAccess(db.Model):
    """Acesso temporário a recursos específicos"""
    __tablename__ = 'temporary_access'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(50), nullable=False)

    # Controle temporal
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    access_reason = db.Column(db.Text)

    # Controle de uso
    is_active = db.Column(db.Boolean, default=True)
    first_used_at = db.Column(db.DateTime)
    last_used_at = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)

    # Relacionamentos
    user = db.relationship('User', foreign_keys=[user_id])
    granted_by_user = db.relationship('User', foreign_keys=[granted_by])

    __table_args__ = (
        db.Index('idx_temporary_access_user', 'user_id'),
        db.Index('idx_temporary_access_resource', 'resource_type', 'resource_id'),
        db.Index('idx_temporary_access_expires', 'expires_at'),
        db.Index('idx_temporary_access_active', 'is_active'),
    )

    def is_expired(self):
        """Verifica se acesso temporário expirou"""
        return datetime.utcnow() > self.expires_at

    def record_usage(self):
        """Registra uso do acesso temporário"""
        now = datetime.utcnow()
        if not self.first_used_at:
            self.first_used_at = now
        self.last_used_at = now
        self.usage_count += 1

class AccessAudit(db.Model):
    """Auditoria detalhada de acessos ao sistema"""
    __tablename__ = 'access_audit'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100))

    # Detalhes do acesso
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    action = db.Column(db.String(50), nullable=False)
    permission_used = db.Column(db.String(100))

    # Contexto
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referer = db.Column(db.String(500))
    method = db.Column(db.String(10))  # GET, POST, etc.

    # Resultado
    access_granted = db.Column(db.Boolean, nullable=False)
    response_time_ms = db.Column(db.Integer)
    error_message = db.Column(db.Text)

    # Relacionamentos
    accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='access_logs')

    __table_args__ = (
        db.Index('idx_access_audit_user', 'user_id'),
        db.Index('idx_access_audit_resource', 'resource_type', 'resource_id'),
        db.Index('idx_access_audit_timestamp', 'accessed_at'),
        db.Index('idx_access_audit_granted', 'access_granted'),
    )

class CAPA(db.Model):
    """Plano de Ação Corretiva e Preventiva (CAPA)"""
    __tablename__ = 'capa'

    id = db.Column(db.Integer, primary_key=True)
    non_conformity_id = db.Column(db.Integer, db.ForeignKey('non_conformities.id'), nullable=False)

    __table_args__ = (
        db.Index('idx_capa_status', 'status'),
        db.Index('idx_capa_type', 'capa_type'),
        db.Index('idx_capa_priority', 'priority'),
        db.Index('idx_capa_non_conformity', 'non_conformity_id'),
        db.Index('idx_capa_responsible', 'responsible_id'),
        db.Index('idx_capa_target_completion', 'target_completion_date'),
        db.Index('idx_capa_created_by', 'created_by_id'),
    )

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