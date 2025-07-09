from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Configuration de la base de données
DATABASE_URL = "sqlite:///./docsearch.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """Modèle utilisateur"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relations
    documents = relationship("Document", back_populates="owner")
    sessions = relationship("UserSession", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")

class Document(Base):
    """Modèle document avec propriétaire"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    session_id = Column(String, nullable=True)  # Pour les sessions temporaires
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Propriétaire
    is_public = Column(Boolean, default=False)  # Documents partagés
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    owner = relationship("User", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    annotations = relationship("DocumentAnnotation", back_populates="document", cascade="all, delete-orphan")
    shares = relationship("DocumentShare", back_populates="document", cascade="all, delete-orphan")
    
    # Relation many-to-many avec les tags
    tags = relationship("DocumentTag", secondary="document_tags_association", back_populates="documents")

class UserSession(Base):
    """Modèle session utilisateur"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relations
    user = relationship("User", back_populates="sessions")

class ChatHistory(Base):
    """Modèle historique de chat par utilisateur"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="chat_history")

# Modèles pour le versioning, annotations et partage

class DocumentVersion(Base):
    """Modèle version de document"""
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)  # Hash SHA-256
    file_size = Column(Integer, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    metadata_json = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relations
    document = relationship("Document", back_populates="versions")
    uploader = relationship("User", foreign_keys=[uploaded_by])  # Utilisateur ayant uploadé la version
    deleted_by_user = relationship("User", foreign_keys=[deleted_by])  # Utilisateur ayant supprimé la version

class DocumentAnnotation(Base):
    """Modèle annotation de document"""
    __tablename__ = "document_annotations"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    annotation_type = Column(String, default="note")  # note, highlight, comment
    position = Column(Text, nullable=True)  # JSON string pour position
    metadata_json = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    document = relationship("Document", back_populates="annotations")
    user = relationship("User")

class DocumentTag(Base):
    """Modèle tag de document"""
    __tablename__ = "document_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, default="#3B82F6")  # Couleur hexadécimale
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    documents = relationship("Document", secondary="document_tags_association", back_populates="tags")

# Table d'association pour les tags
class DocumentTagAssociation(Base):
    """Table d'association document-tag"""
    __tablename__ = "document_tags_association"
    
    document_id = Column(Integer, ForeignKey("documents.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("document_tags.id"), primary_key=True)

class DocumentShare(Base):
    """Modèle partage de document"""
    __tablename__ = "document_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with = Column(Integer, ForeignKey("users.id"), nullable=False)
    permissions = Column(Text, nullable=False)  # JSON string ["read", "write", "comment"]
    expires_at = Column(DateTime, nullable=True)
    message = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relations
    document = relationship("Document", back_populates="shares")
    owner = relationship("User", foreign_keys=[owner_id])
    shared_user = relationship("User", foreign_keys=[shared_with])

# Créer les tables
def create_tables():
    """Crée toutes les tables de la base de données"""
    Base.metadata.create_all(bind=engine)

# Fonction pour obtenir la session DB
def get_db():
    """Obtient une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Créer les tables au démarrage
if __name__ == "__main__":
    create_tables()
    print("✅ Tables de base de données créées avec succès!") 