import os
from dotenv import load_dotenv
import logging

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class Config:
    """Configuration de l'application"""
    
    # Chemins
    SOURCE_DIR = "./source"
    VECTOR_DB_PATH = "./vector_db"
    
    # Configuration des embeddings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Configuration du modèle de génération
    LLM_MODEL = "llama2"  # Modèle Ollama par défaut
    
    # Configuration du découpage de texte
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Configuration de la recherche
    SEARCH_RESULTS = 5
    
    @classmethod
    def load_config(cls):
        """Charge la configuration depuis les variables d'environnement"""
        try:
            # Variables d'environnement optionnelles
            if os.getenv("OPENAI_API_KEY"):
                logger.info("Clé API OpenAI trouvée")
            
            logger.info("Configuration chargée depuis .env")
            return cls
            
        except Exception as e:
            logger.warning(f"Erreur lors du chargement de la configuration: {e}")
            return cls 