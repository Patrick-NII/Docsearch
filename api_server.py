from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
import base64
from pathlib import Path

from config import settings
from document_loader import AdvancedDocumentLoader
from vector_store import VectorStore
from rag_chain import ModernRAGChain

# Configuration du logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DocSearch AI API",
    description="API pour l'analyse de documents avec IA",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sécurité
security = HTTPBearer()

# Modèles Pydantic
class QuestionRequest(BaseModel):
    question: str
    user_id: Optional[str] = None

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

class ChatHistoryResponse(BaseModel):
    history: List[Dict[str, str]]

class DocumentInfo(BaseModel):
    filename: str
    file_type: str
    source: str
    session_id: str
    upload_date: str
    chunks_count: int

class DocumentsListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_count: int

# Variables globales pour les instances
document_loader = None
vector_store = None
rag_chain = None

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Vérifie le token d'authentification"""
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalide")
    return credentials.credentials

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
        
        # NOTE: Les documents du dossier source ne sont plus chargés automatiquement
        # Ils doivent être chargés explicitement via l'endpoint /load-documents
        
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
        "version": "1.0.0",
        "status": "running"
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
            "openai_configured": bool(settings.OPENAI_API_KEY)
        }
    except Exception as e:
        logger.error(f"Erreur lors du health check: {e}")
        raise HTTPException(status_code=500, detail="Service non disponible")

@app.post("/upload", response_model=UploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    token: str = Depends(get_token)
):
    """Upload et traitement de documents"""
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
                processed_documents.append(doc)
                logger.info(f"Document traité: {file.filename}")
        
        if processed_documents:
            # Traiter les documents de manière synchrone pour éviter les problèmes de timing
            success = rag_chain.process_documents(processed_documents, session_id)
            if not success:
                logger.error("Erreur lors du traitement des documents")
                raise HTTPException(status_code=500, detail="Erreur lors du traitement des documents")
            logger.info(f"Documents traités: {len(processed_documents)} (session: {session_id})")
        
        return UploadResponse(
            message=f"{len(processed_documents)} documents traités avec succès",
            documents_processed=len(processed_documents),
            documents=[{
                "filename": doc["metadata"]["filename"],
                "file_type": doc["metadata"]["file_type"],
                "file_size": doc["metadata"]["file_size"]
            } for doc in processed_documents],
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

async def process_documents_background(documents: List[Dict[str, Any]], session_id: str):
    """Traitement des documents en arrière-plan"""
    try:
        if rag_chain:
            success = rag_chain.process_documents(documents, session_id)
            if success:
                logger.info(f"Documents traités en arrière-plan: {len(documents)} (session: {session_id})")
            else:
                logger.error("Erreur lors du traitement en arrière-plan")
    except Exception as e:
        logger.error(f"Erreur lors du traitement en arrière-plan: {e}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    token: str = Depends(get_token)
):
    """Pose une question à l'IA"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=500, detail="Service RAG non initialisé")
        
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question vide")
        
        # Obtenir la réponse
        result = rag_chain.ask_question(request.question)
        
        return QuestionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la question: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

@app.get("/documents", response_model=DocumentsListResponse)
async def get_available_documents(token: str = Depends(get_token)):
    """Récupère la liste des documents disponibles"""
    try:
        if not vector_store:
            raise HTTPException(status_code=500, detail="Vector store non initialisé")
        
        documents = vector_store.get_available_documents()
        
        return DocumentsListResponse(
            documents=[DocumentInfo(**doc) for doc in documents],
            total_count=len(documents)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des documents: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@app.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(token: str = Depends(get_token)):
    """Récupère l'historique de conversation"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=500, detail="Service RAG non initialisé")
        
        history = rag_chain.get_chat_history()
        return ChatHistoryResponse(history=history)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@app.delete("/history")
async def clear_chat_history(token: str = Depends(get_token)):
    """Efface l'historique de conversation"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=500, detail="Service RAG non initialisé")
        
        rag_chain.clear_memory()
        return {"message": "Historique effacé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'effacement de l'historique: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'effacement: {str(e)}")

@app.delete("/session")
async def clear_current_session(token: str = Depends(get_token)):
    """Efface la session actuelle (documents uploadés récemment)"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=500, detail="Service RAG non initialisé")
        
        rag_chain.clear_current_session()
        return {"message": "Session actuelle effacée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'effacement de la session: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'effacement: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats(token: str = Depends(get_token)):
    """Récupère les statistiques du système"""
    try:
        if not rag_chain:
            raise HTTPException(status_code=500, detail="Service RAG non initialisé")
        
        stats = rag_chain.get_stats()
        return StatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@app.delete("/clear-all")
async def clear_all_documents(token: str = Depends(get_token)):
    """Efface tous les documents de la base vectorielle"""
    try:
        if not vector_store:
            raise HTTPException(status_code=500, detail="Vector store non initialisé")
        
        # Effacer la collection complète
        vector_store.clear_collection()
        
        # Réinitialiser la session RAG
        if rag_chain:
            rag_chain.current_session_id = None
        
        return {"message": "Tous les documents ont été supprimés de la base vectorielle"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'effacement de tous les documents: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'effacement: {str(e)}")

@app.post("/load-documents")
async def load_existing_documents(token: str = Depends(get_token)):
    """Charge les documents existants du répertoire source"""
    try:
        if not document_loader or not rag_chain:
            raise HTTPException(status_code=500, detail="Services non initialisés")
        
        # Charger les documents du répertoire source
        documents = document_loader.load_documents()
        
        if documents:
            # Traiter les documents (sans session = documents permanents)
            success = rag_chain.process_documents(documents)
            if success:
                return {
                    "message": f"{len(documents)} documents chargés avec succès",
                    "documents_loaded": len(documents)
                }
            else:
                raise HTTPException(status_code=500, detail="Erreur lors du traitement des documents")
        else:
            return {
                "message": "Aucun document trouvé dans le répertoire source",
                "documents_loaded": 0
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du chargement des documents: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    ) 