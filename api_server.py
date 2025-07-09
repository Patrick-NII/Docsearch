from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
import base64
from pathlib import Path
from sqlalchemy.orm import Session

from config import settings
from document_loader import AdvancedDocumentLoader
from vector_store import VectorStore
from rag_chain import ModernRAGChain
from models import get_db, User, Document, ChatHistory
from auth import get_current_user, get_current_active_user, get_current_admin_user
from auth_routes import router as auth_router
from analytics_routes import router as analytics_router
from document_management_routes import router as document_management_router
from advanced_document_routes import router as advanced_document_router

# Configuration du logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DocSearch AI API",
    description="API pour l'analyse de documents avec IA et authentification JWT",
    version="2.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes d'authentification
app.include_router(auth_router)

# Inclure les routes d'analytics
app.include_router(analytics_router)

# Inclure les routes de gestion avancée des documents
app.include_router(document_management_router)

# Inclure les routes de gestion avancée des documents (versioning, annotations, partage)
app.include_router(advanced_document_router)

# Variables globales pour les instances
document_loader = None
vector_store = None
rag_chain = None

# Modèles Pydantic
class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    question: str
    mode: str
    context: str

class UploadResponse(BaseModel):
    message: str
    documents_processed: int
    documents: List[Dict[str, Any]]
    session_id: Optional[str] = None

class StatsResponse(BaseModel):
    model: str
    embedding_model: str
    chunk_size: int
    top_k: int
    has_vector_store: bool
    memory_messages: int
    vector_store_documents: Optional[int] = None
    available_documents: Optional[int] = None
    current_session_id: Optional[str] = None
    user_documents_count: int
    user_sessions_count: int

class ChatHistoryResponse(BaseModel):
    history: List[Dict[str, str]]

class DocumentInfo(BaseModel):
    filename: str
    file_type: str
    source: str
    session_id: str
    upload_date: str
    chunks_count: int
    user_id: Optional[int] = None

class DocumentsListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_count: int

class UserStatsResponse(BaseModel):
    user_id: int
    username: str
    email: str
    documents_count: int
    sessions_count: int
    is_admin: bool
    is_active: bool

def init_services():
    """Initialise les services (document loader, vector store, RAG chain)"""
    global document_loader, vector_store, rag_chain
    
    try:
        # Initialiser le chargeur de documents
        document_loader = AdvancedDocumentLoader()
        logger.info("Document loader initialisé")
        
        # Initialiser la base vectorielle
        vector_store = VectorStore()
        logger.info("Vector store initialisé")
        
        # Initialiser la chaîne RAG
        rag_chain = ModernRAGChain(vector_store)
        logger.info("RAG chain initialisée")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des services: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    logger.info("Démarrage de l'API DocSearch AI")
    init_services()

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "DocSearch AI API",
        "version": "2.0.0",
        "status": "running",
        "features": ["JWT Authentication", "Multi-user support", "Document analysis", "RAG chat"]
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    try:
        # Vérifier les services
        services_status = {
            "document_loader": document_loader is not None,
            "vector_store": vector_store is not None,
            "rag_chain": rag_chain is not None
        }
        
        return {
            "status": "healthy",
            "services": services_status,
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "auth_enabled": True
        }
    except Exception as e:
        logger.error(f"Erreur lors du health check: {e}")
        raise HTTPException(status_code=500, detail="Service non disponible")

@app.post("/upload", response_model=UploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload et traitement de documents (authentifié)"""
    try:
        if not document_loader or not rag_chain:
            raise HTTPException(status_code=500, detail="Services non initialisés")
        
        # Démarrer une nouvelle session pour cet upload
        session_id = rag_chain.start_new_session()
        
        processed_documents = []
        
        for file in files:
            # Vérifier la taille du fichier
            if file.size > settings.MAX_FILE_SIZE * 1024 * 1024:  # Convertir en bytes
                raise HTTPException(
                    status_code=400, 
                    detail=f"Fichier {file.filename} trop volumineux (max {settings.MAX_FILE_SIZE}MB)"
                )
            
            # Vérifier le format
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.SUPPORTED_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Format non supporté: {file_ext}"
                )
            
            # Lire le contenu du fichier
            content = await file.read()
            
            # Convertir en base64 pour le traitement
            base64_content = base64.b64encode(content).decode('utf-8')
            
            # Traiter le document
            doc = document_loader.load_from_base64(base64_content, file.filename)
            if doc:
                # Ajouter les métadonnées utilisateur
                doc["metadata"]["user_id"] = current_user.id
                doc["metadata"]["username"] = current_user.username
                processed_documents.append(doc)
                
                # Enregistrer le document en base de données
                db_document = Document(
                    filename=file.filename,
                    file_type=file_ext,
                    file_size=file.size,
                    session_id=session_id,
                    user_id=current_user.id
                )
                db.add(db_document)
                
                logger.info(f"Document traité: {file.filename} (utilisateur: {current_user.username})")
        
        if processed_documents:
            # Traiter les documents de manière synchrone
            success = rag_chain.process_documents(processed_documents, session_id)
            if not success:
                logger.error("Erreur lors du traitement des documents")
                raise HTTPException(status_code=500, detail="Erreur lors du traitement des documents")
            
            db.commit()
            
            return UploadResponse(
                message=f"{len(processed_documents)} document(s) traité(s) avec succès",
                documents_processed=len(processed_documents),
                documents=[{"filename": doc["metadata"]["filename"], "type": doc["metadata"]["file_type"]} for doc in processed_documents],
                session_id=session_id
            )
        else:
            raise HTTPException(status_code=400, detail="Aucun document valide à traiter")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'upload: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

async def process_documents_background(documents: List[Dict[str, Any]], session_id: str):
    """Traitement asynchrone des documents (pour référence)"""
    try:
        if rag_chain:
            success = rag_chain.process_documents(documents, session_id)
            if success:
                logger.info(f"Documents traités en arrière-plan: {len(documents)}")
            else:
                logger.error("Erreur lors du traitement en arrière-plan")
    except Exception as e:
        logger.error(f"Erreur lors du traitement en arrière-plan: {e}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Poser une question (authentifié)"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=500, detail="Service RAG non initialisé")
        
        # Obtenir la réponse
        result = rag_chain.ask_question(request.question)
        
        # Enregistrer l'historique en base de données
        chat_entry = ChatHistory(
            user_id=current_user.id,
            question=request.question,
            answer=result["answer"],
            sources=str(result["sources"]),
            session_id=rag_chain.current_session_id
        )
        db.add(chat_entry)
        db.commit()
        
        logger.info(f"Question traitée pour {current_user.username}: {request.question[:50]}...")
        
        return QuestionResponse(
            answer=result["answer"],
            sources=result["sources"],
            question=request.question,
            mode=result["mode"],
            context=result["context"]
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la question: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/documents", response_model=DocumentsListResponse)
async def get_available_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtenir la liste des documents disponibles (authentifié)"""
    try:
        if not vector_store:
            raise HTTPException(status_code=500, detail="Vector store non initialisé")
        
        # Obtenir les documents du vector store
        vector_docs = vector_store.get_available_documents()
        
        # Filtrer par utilisateur (sauf pour les admins)
        if not current_user.is_admin:
            vector_docs = [doc for doc in vector_docs if doc.get("user_id") == current_user.id]
        
        # Obtenir les documents de la base de données
        db_documents = db.query(Document).filter(Document.user_id == current_user.id).all()
        
        # Combiner les informations
        documents = []
        for doc in vector_docs:
            documents.append(DocumentInfo(
                filename=doc["filename"],
                file_type=doc["file_type"],
                source=doc["source"],
                session_id=doc["session_id"],
                upload_date=doc.get("upload_date", "N/A"),
                chunks_count=doc["chunks_count"],
                user_id=doc.get("user_id")
            ))
        
        return DocumentsListResponse(
            documents=documents,
            total_count=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des documents: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtenir l'historique de conversation (authentifié)"""
    try:
        # Obtenir l'historique de la base de données
        db_history = db.query(ChatHistory).filter(
            ChatHistory.user_id == current_user.id
        ).order_by(ChatHistory.created_at.desc()).limit(50).all()
        
        # Formater l'historique
        history = []
        for entry in reversed(db_history):  # Inverser pour avoir l'ordre chronologique
            history.append({
                "question": entry.question,
                "answer": entry.answer,
                "timestamp": entry.created_at.isoformat(),
                "session_id": entry.session_id if entry.session_id is not None else "Permanent"
            })
        
        return ChatHistoryResponse(history=history)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Effacer l'historique de conversation (authentifié)"""
    try:
        # Effacer l'historique de la base de données
        db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
        db.commit()
        
        # Effacer la mémoire de la chaîne RAG
        if rag_chain:
            rag_chain.clear_memory()
        
        logger.info(f"Historique effacé pour {current_user.username}")
        return {"message": "Historique effacé avec succès"}
        
    except Exception as e:
        logger.error(f"Erreur lors de l'effacement de l'historique: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.delete("/session")
async def clear_current_session(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Effacer la session actuelle (authentifié)"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=500, detail="Service RAG non initialisé")
        
        # Effacer la session du vector store
        if rag_chain.current_session_id:
            vector_store.clear_current_session()
            rag_chain.clear_current_session()
        
        # Effacer les documents de la session en base de données
        if rag_chain.current_session_id:
            db.query(Document).filter(
                Document.session_id == rag_chain.current_session_id,
                Document.user_id == current_user.id
            ).delete()
            db.commit()
        
        logger.info(f"Session effacée pour {current_user.username}")
        return {"message": "Session effacée avec succès"}
        
    except Exception as e:
        logger.error(f"Erreur lors de l'effacement de la session: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques (authentifié)"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=500, detail="Service RAG non initialisé")
        
        # Statistiques de base
        stats = rag_chain.get_stats()
        
        # Statistiques utilisateur
        user_documents_count = db.query(Document).filter(Document.user_id == current_user.id).count()
        user_sessions_count = db.query(Document.session_id).filter(
            Document.user_id == current_user.id
        ).distinct().count()
        
        stats["user_documents_count"] = user_documents_count
        stats["user_sessions_count"] = user_sessions_count
        
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.delete("/clear-all")
async def clear_all_documents(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Effacer tous les documents (admin uniquement)"""
    try:
        if not vector_store:
            raise HTTPException(status_code=500, detail="Vector store non initialisé")
        
        # Effacer tous les documents du vector store
        vector_store.clear_all_documents()
        
        # Effacer tous les documents de la base de données
        db.query(Document).delete()
        db.query(ChatHistory).delete()
        db.commit()
        
        # Effacer la mémoire de la chaîne RAG
        if rag_chain:
            rag_chain.clear_memory()
        
        logger.info(f"Tous les documents effacés par {current_user.username}")
        return {"message": "Tous les documents effacés avec succès"}
        
    except Exception as e:
        logger.error(f"Erreur lors de l'effacement de tous les documents: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/users/stats", response_model=List[UserStatsResponse])
async def get_users_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques de tous les utilisateurs (admin uniquement)"""
    try:
        users = db.query(User).all()
        stats = []
        
        for user in users:
            documents_count = db.query(Document).filter(Document.user_id == user.id).count()
            sessions_count = db.query(Document.session_id).filter(
                Document.user_id == user.id
            ).distinct().count()
            
            stats.append(UserStatsResponse(
                user_id=user.id,
                username=user.username,
                email=user.email,
                documents_count=documents_count,
                sessions_count=sessions_count,
                is_admin=user.is_admin,
                is_active=user.is_active
            ))
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats utilisateurs: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    ) 