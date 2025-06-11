from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from chromadb.config import Settings
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db_path: str = "./vector_db", collection_name: str = "documents"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )

        # Utilise Sentence Transformers pour les embeddings locaux
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialise ou charge la collection
        self._init_collection()
    
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
    
    def add_chunks(self, chunks: list):
        """
        Ajoute des chunks à la base vectorielle
        
        Args:
            chunks: Liste des chunks à ajouter
        """
        if not chunks:
            logger.warning("Aucun chunk à ajouter")
            return
        
        try:
            # Préparer les données pour ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                text = chunk.get("text", "")
                metadata = chunk.get("metadata", {})
                
                # Générer un ID unique pour le chunk
                chunk_id = hashlib.md5(f"{metadata.get('source', '')}_{metadata.get('chunk_id', 0)}".encode()).hexdigest()
                
                documents.append(text)
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Ajouter à la collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"{len(chunks)} chunks ajoutés à la base vectorielle")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des chunks: {e}")
            raise
    
    def search(self, query: str, n_results: int = 5):
        """
        Recherche des chunks similaires à une requête
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats à retourner
            
        Returns:
            Liste des résultats avec scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return None
    
    def get_collection_info(self):
        """Retourne les informations sur la collection"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "path": str(self.db_path)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos: {e}")
            return None 