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