from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import chromadb
from chromadb.config import Settings
from pathlib import Path
import hashlib
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from config import settings, get_embedding_config

logger = logging.getLogger(__name__)

class VectorStore:
    """Gestionnaire de base vectorielle moderne avec support OpenAI et local"""
    
    def __init__(self, db_path: str = None, collection_name: str = "documents"):
        self.db_path = Path(db_path or settings.VECTOR_DB_PATH)
        self.db_path.mkdir(exist_ok=True)
        self.collection_name = collection_name

        # Initialiser le client ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )

        # Initialiser les embeddings
        self._init_embeddings()
        
        # Initialiser la collection
        self._init_collection()
        
        # Session actuelle pour les uploads
        self.current_session_id = None
        self.current_upload_documents = []
    
    def _init_embeddings(self):
        """Initialise les embeddings (OpenAI ou local)"""
        try:
            if settings.OPENAI_API_KEY:
                # Utiliser OpenAI embeddings si disponible
                self.embeddings = OpenAIEmbeddings(
                    model="text-embedding-ada-002",
                    openai_api_key=settings.OPENAI_API_KEY
                )
                logger.info("Embeddings OpenAI initialisés")
            else:
                # Fallback vers Sentence Transformers local
                from langchain_community.embeddings import SentenceTransformerEmbeddings
                embedding_config = get_embedding_config()
                self.embeddings = SentenceTransformerEmbeddings(
                    model_name=embedding_config["model_name"],
                    model_kwargs=embedding_config["model_kwargs"],
                    encode_kwargs=embedding_config["encode_kwargs"]
                )
                logger.info("Embeddings locaux initialisés")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des embeddings: {e}")
            raise
    
    def _init_collection(self):
        """Initialise ou charge la collection ChromaDB"""
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Collection de documents pour RAG"}
            )
            logger.info(f"Collection '{self.collection_name}' chargée")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la collection: {e}")
            raise
    
    def start_new_session(self) -> str:
        """Démarre une nouvelle session d'upload"""
        self.current_session_id = str(uuid.uuid4())
        self.current_upload_documents = []
        logger.info(f"Nouvelle session démarrée: {self.current_session_id}")
        return self.current_session_id
    
    def add_documents(self, documents: List[Document], embeddings=None, session_id: str = None):
        """
        Ajoute des documents LangChain à la base vectorielle
        
        Args:
            documents: Liste des documents LangChain
            embeddings: Fonction d'embedding (optionnel)
            session_id: ID de session pour le suivi
        """
        if not documents:
            logger.warning("Aucun document à ajouter")
            return
        
        try:
            # Utiliser les embeddings par défaut si non fournis
            if embeddings is None:
                embeddings = self.embeddings
            
            # Ajouter des métadonnées de session si fourni
            if session_id:
                for doc in documents:
                    if not doc.metadata:
                        doc.metadata = {}
                    doc.metadata["session_id"] = session_id
                    doc.metadata["upload_date"] = datetime.now().isoformat()
            
            # Créer le vector store Chroma
            vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=embeddings
            )
            
            # Ajouter les documents
            vectorstore.add_documents(documents)
            
            # Garder une trace des documents de la session actuelle
            if session_id == self.current_session_id:
                self.current_upload_documents.extend([doc.metadata.get("filename", "unknown") for doc in documents])
            
            logger.info(f"{len(documents)} documents ajoutés à la base vectorielle")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents: {e}")
            raise
    
    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Ajoute des chunks à la base vectorielle (méthode legacy)
        
        Args:
            chunks: Liste des chunks à ajouter
        """
        if not chunks:
            logger.warning("Aucun chunk à ajouter")
            return
        
        try:
            # Convertir les chunks en documents LangChain
            documents = []
            for chunk in chunks:
                text = chunk.get("text", "")
                metadata = chunk.get("metadata", {})
                
                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata=metadata
                    )
                    documents.append(doc)
            
            # Ajouter les documents
            self.add_documents(documents)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des chunks: {e}")
            raise
    
    def search(self, query: str, n_results: int = None, session_id: str = None):
        """
        Recherche des documents similaires à une requête
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats à retourner
            session_id: Filtrer par session (optionnel)
            
        Returns:
            Liste des résultats avec scores
        """
        try:
            if n_results is None:
                n_results = settings.TOP_K_RESULTS
            
            # Utiliser ChromaDB directement pour la recherche
            where_filter = None
            if session_id:
                where_filter = {"session_id": session_id}
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return None
    
    def similarity_search(self, query: str, k: int = None, session_id: str = None) -> List[Document]:
        """
        Recherche de similarité avec retour de documents LangChain
        
        Args:
            query: Requête de recherche
            k: Nombre de résultats
            session_id: Filtrer par session (optionnel)
            
        Returns:
            Liste de documents LangChain
        """
        try:
            if k is None:
                k = settings.TOP_K_RESULTS
            
            # Créer le vector store Chroma
            vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
            # Effectuer la recherche
            if session_id:
                # Filtrer par session
                results = vectorstore.similarity_search(
                    query, 
                    k=k,
                    filter={"session_id": session_id}
                )
            else:
                results = vectorstore.similarity_search(query, k=k)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de similarité: {e}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = None, session_id: str = None) -> List[tuple]:
        """
        Recherche de similarité avec scores
        
        Args:
            query: Requête de recherche
            k: Nombre de résultats
            session_id: Filtrer par session (optionnel)
            
        Returns:
            Liste de tuples (document, score)
        """
        try:
            if k is None:
                k = settings.TOP_K_RESULTS
            
            # Créer le vector store Chroma
            vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
            # Effectuer la recherche avec scores
            if session_id:
                results = vectorstore.similarity_search_with_score(
                    query, 
                    k=k,
                    filter={"session_id": session_id}
                )
            else:
                results = vectorstore.similarity_search_with_score(query, k=k)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche avec scores: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Retourne les informations sur la collection"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "path": str(self.db_path),
                "embedding_model": "text-embedding-ada-002" if settings.OPENAI_API_KEY else settings.EMBEDDING_MODEL
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos: {e}")
            return {}
    
    def get_available_documents(self) -> List[Dict[str, Any]]:
        """Retourne la liste des documents disponibles dans la base"""
        try:
            # Récupérer tous les documents avec leurs métadonnées
            results = self.collection.get()
            
            documents = []
            if results and results.get('metadatas'):
                # Créer un dictionnaire pour éviter les doublons
                unique_docs = {}
                
                for i, metadata in enumerate(results['metadatas']):
                    if metadata:
                        filename = metadata.get('filename', 'Document inconnu')
                        file_type = metadata.get('file_type', 'Inconnu')
                        source = metadata.get('source', 'Inconnu')
                        session_id = metadata.get('session_id', 'Permanent')
                        upload_date = metadata.get('upload_date', 'Inconnu')
                        
                        # Clé unique basée sur le nom de fichier et la source
                        key = f"{filename}_{source}"
                        
                        if key not in unique_docs:
                            unique_docs[key] = {
                                "filename": filename,
                                "file_type": file_type,
                                "source": source,
                                "session_id": session_id,
                                "upload_date": upload_date,
                                "chunks_count": 1
                            }
                        else:
                            unique_docs[key]["chunks_count"] += 1
                
                documents = list(unique_docs.values())
            
            return documents
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents: {e}")
            return []
    
    def get_current_session_documents(self) -> List[str]:
        """Retourne les documents de la session actuelle"""
        return self.current_upload_documents.copy()
    
    def clear_current_session(self):
        """Vide la session actuelle (supprime les documents uploadés récemment)"""
        try:
            if self.current_session_id:
                # Supprimer les documents de la session actuelle
                self.collection.delete(where={"session_id": self.current_session_id})
                logger.info(f"Session {self.current_session_id} vidée")
                
                # Réinitialiser la session
                self.current_session_id = None
                self.current_upload_documents = []
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage de la session: {e}")
            raise
    
    def clear_collection(self):
        """Vide la collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self._init_collection()
            logger.info(f"Collection '{self.collection_name}' vidée")
        except Exception as e:
            logger.error(f"Erreur lors du vidage de la collection: {e}")
            raise
    
    def delete_documents(self, ids: List[str]):
        """
        Supprime des documents par leurs IDs
        
        Args:
            ids: Liste des IDs à supprimer
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"{len(ids)} documents supprimés")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            raise 