from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import logging

logger = logging.getLogger(__name__)

class RAGChain:
    """Chaîne RAG pour la génération de réponses"""
    
    def __init__(self, vector_store):
        """
        Initialise la chaîne RAG
        
        Args:
            vector_store: Instance de VectorStore
        """
        self.vector_store = vector_store
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialiser les modèles
        self._init_models()
        
        # Créer la chaîne RAG
        self._create_chain()
    
    def _init_models(self):
        """Initialise le modèle local pour la génération de texte"""
        try:
            # Utilise Ollama pour le modèle local
            self.llm = Ollama(model="llama2")
            logger.info("Modèle Ollama local initialisé")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du modèle: {e}")
            raise
    
    def _create_retriever(self):
        """Crée un retriever natif LangChain à partir de la collection ChromaDB"""
        return Chroma(
            client=self.vector_store.client,
            collection_name=self.vector_store.collection_name,
            embedding_function=self.vector_store.embeddings
        ).as_retriever()
    
    def _create_chain(self):
        """Crée la chaîne de conversation RAG"""
        try:
            retriever = self._create_retriever()
            
            self.chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=self.memory,
                return_source_documents=True,
                verbose=False
            )
            
            logger.info("Chaîne RAG initialisée")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la chaîne: {e}")
            raise
    
    def ask_question(self, question: str) -> dict:
        """
        Pose une question et retourne la réponse
        
        Args:
            question: Question de l'utilisateur
            
        Returns:
            Dictionnaire contenant la réponse et les sources
        """
        try:
            # Obtenir la réponse via la chaîne RAG
            result = self.chain({"question": question})
            
            # Extraire la réponse et les sources
            answer = result.get("answer", "")
            source_documents = result.get("source_documents", [])
            
            # Formater les sources
            sources = []
            for doc in source_documents:
                metadata = doc.metadata
                sources.append({
                    "text": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "source": metadata.get("source", "Inconnu"),
                    "page": metadata.get("estimated_page", "N/A"),
                    "filename": metadata.get("filename", "Inconnu")
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "question": question
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la question: {e}")
            return {
                "answer": f"Erreur lors du traitement de votre question: {str(e)}",
                "sources": [],
                "question": question
            }
    
    def get_chat_history(self) -> list:
        """Retourne l'historique de conversation"""
        return self.memory.chat_memory.messages if hasattr(self.memory, 'chat_memory') else []
    
    def clear_memory(self):
        """Efface la mémoire de conversation"""
        self.memory.clear()
        logger.info("Mémoire de conversation effacée") 