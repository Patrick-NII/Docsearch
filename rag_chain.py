from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate
import logging
from typing import List, Dict, Any, Optional
import os
import re

from config import settings, get_model_config, get_embedding_config, get_rag_config

logger = logging.getLogger(__name__)

class ModernRAGChain:
    """Chaîne RAG moderne avec support GPT et fonctionnalités avancées"""
    
    def __init__(self, vector_store=None):
        """
        Initialise la chaîne RAG moderne
        
        Args:
            vector_store: Instance de VectorStore (optionnel)
        """
        self.vector_store = vector_store
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Configuration
        self.model_config = get_model_config()
        self.embedding_config = get_embedding_config()
        self.rag_config = get_rag_config()
        
        # Session actuelle
        self.current_session_id = None
        
        # Initialiser les modèles
        self._init_models()
        
        # Créer la chaîne RAG
        self._create_chain()
    
    def _init_models(self):
        """Initialise les modèles LLM et embeddings"""
        try:
            # Vérifier la clé API OpenAI
            if not self.model_config["api_key"]:
                raise ValueError("Clé API OpenAI manquante. Définissez OPENAI_API_KEY dans .env")
            
            # Initialiser le modèle GPT
            self.llm = ChatOpenAI(
                model=self.model_config["model"],
                temperature=self.model_config["temperature"],
                max_tokens=self.model_config["max_tokens"],
                openai_api_key=self.model_config["api_key"]
            )
            
            # Initialiser les embeddings
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=self.model_config["api_key"]
            )
            
            logger.info(f"Modèle GPT initialisé: {self.model_config['model']}")
            logger.info("Embeddings OpenAI initialisés")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des modèles: {e}")
            raise
    
    def _create_retriever(self, session_id: str = None):
        """Crée un retriever à partir de la base vectorielle"""
        if not self.vector_store:
            raise ValueError("Vector store non initialisé")
        
        return Chroma(
            client=self.vector_store.client,
            collection_name=self.vector_store.collection_name,
            embedding_function=self.embeddings
        ).as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": self.rag_config["top_k"],
                "filter": {"session_id": session_id} if session_id else None
            }
        )
    
    def _create_prompt_template(self):
        """Crée un template de prompt personnalisé"""
        template = """Tu es un assistant IA spécialisé dans l'analyse de documents. 
        Tu dois répondre aux questions de l'utilisateur en te basant uniquement sur les documents fournis.
        
        Contexte des documents:
        {context}
        
        Historique de conversation:
        {chat_history}
        
        Question: {question}
        
        Instructions:
        1. Réponds uniquement en te basant sur les informations des documents
        2. Si l'information n'est pas dans les documents, dis-le clairement
        3. Cite les sources pertinentes quand c'est possible
        4. Sois précis et concis
        5. Réponds en français
        6. Si on te demande quels documents tu as, liste-les clairement
        
        Réponse:"""
        
        return PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=template
        )
    
    def _create_chain(self, session_id: str = None):
        """Crée la chaîne de conversation RAG"""
        try:
            if self.vector_store:
                retriever = self._create_retriever(session_id)
                prompt_template = self._create_prompt_template()
                
                self.chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=retriever,
                    memory=self.memory,
                    return_source_documents=True,
                    verbose=False,
                    combine_docs_chain_kwargs={"prompt": prompt_template}
                )
                
                logger.info(f"Chaîne RAG initialisée avec vector store (session: {session_id or 'toutes'})")
            else:
                logger.warning("Chaîne RAG initialisée sans vector store (mode conversation uniquement)")
                self.chain = None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la chaîne: {e}")
            raise
    
    def start_new_session(self) -> str:
        """Démarre une nouvelle session d'upload"""
        if self.vector_store:
            session_id = self.vector_store.start_new_session()
            self.current_session_id = session_id
            logger.info(f"Nouvelle session RAG démarrée: {session_id}")
            return session_id
        return None
    
    def _detect_context_intent(self, question: str) -> Dict[str, Any]:
        """Détecte l'intention de la question pour déterminer le contexte"""
        question_lower = question.lower()
        
        # Questions sur les documents disponibles
        document_queries = [
            "quels documents", "quels fichiers", "quelles sont les documents",
            "liste des documents", "documents disponibles", "fichiers disponibles",
            "que contient ta base", "base de données", "documents en base",
            "qu'est-ce que tu as", "quels sont les documents"
        ]
        
        # Questions sur le contexte actuel
        current_context_queries = [
            "dans ce document", "dans ce fichier", "dans l'upload",
            "dans le document uploadé", "dans le fichier uploadé"
        ]
        
        # Questions sur les documents permanents
        permanent_context_queries = [
            "dans les documents permanents", "dans la base", "dans feuillet-pauvre",
            "dans le document source", "dans les anciens documents"
        ]
        
        # Vérifier les intentions
        for query in document_queries:
            if query in question_lower:
                return {
                    "intent": "list_documents",
                    "context": "all_documents",
                    "session_id": None
                }
        
        for query in current_context_queries:
            if query in question_lower:
                return {
                    "intent": "current_context",
                    "context": "current_session",
                    "session_id": self.current_session_id
                }
        
        for query in permanent_context_queries:
            if query in question_lower:
                return {
                    "intent": "question",
                    "context": "permanent_documents",
                    "session_id": None
                }
        
        # LOGIQUE PRIORITAIRE : Si on a une session active, l'utiliser par défaut
        if self.current_session_id:
            return {
                "intent": "question",
                "context": "current_session",
                "session_id": self.current_session_id
            }
        else:
            # Sinon, utiliser tous les documents
            return {
                "intent": "question",
                "context": "all_documents",
                "session_id": None
            }
    
    def process_documents(self, documents: List[Dict[str, Any]], session_id: str = None) -> bool:
        """
        Traite et indexe les documents dans la base vectorielle
        
        Args:
            documents: Liste des documents à traiter
            session_id: ID de session pour le suivi
            
        Returns:
            True si succès, False sinon
        """
        try:
            if not self.vector_store:
                logger.error("Vector store non initialisé")
                return False
            
            # Créer les documents LangChain
            langchain_docs = []
            for doc in documents:
                if doc.get("text") and doc.get("metadata"):
                    langchain_doc = Document(
                        page_content=doc["text"],
                        metadata=doc["metadata"]
                    )
                    langchain_docs.append(langchain_doc)
            
            if not langchain_docs:
                logger.warning("Aucun document valide à traiter")
                return False
            
            # Découper les documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.rag_config["chunk_size"],
                chunk_overlap=self.rag_config["chunk_overlap"],
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            split_docs = text_splitter.split_documents(langchain_docs)
            logger.info(f"Documents découpés en {len(split_docs)} chunks")
            
            # Ajouter à la base vectorielle avec session_id
            self.vector_store.add_documents(split_docs, self.embeddings, session_id)
            logger.info(f"{len(split_docs)} chunks ajoutés à la base vectorielle")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des documents: {e}")
            return False
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Pose une question et retourne la réponse
        
        Args:
            question: Question de l'utilisateur
            
        Returns:
            Dictionnaire contenant la réponse et les sources
        """
        try:
            # Détecter l'intention et le contexte
            context_info = self._detect_context_intent(question)
            
            # Gérer les questions sur les documents disponibles
            if context_info["intent"] == "list_documents":
                return self._handle_document_listing()
            
            # Recréer la chaîne avec le bon contexte
            self._create_chain(context_info["session_id"])
            
            if not self.chain:
                # Mode conversation sans documents
                response = self.llm.invoke(question)
                return {
                    "answer": response.content,
                    "sources": [],
                    "question": question,
                    "mode": "conversation_only",
                    "context": context_info["context"]
                }
            
            # Mode RAG avec documents
            result = self.chain({"question": question})
            
            # Extraire la réponse et les sources
            answer = result.get("answer", "")
            source_documents = result.get("source_documents", [])
            
            # Formater les sources
            sources = []
            for doc in source_documents:
                metadata = doc.metadata
                sources.append({
                    "text": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "source": metadata.get("source", "Inconnu"),
                    "filename": metadata.get("filename", "Inconnu"),
                    "file_type": metadata.get("file_type", "Inconnu"),
                    "page": metadata.get("page", "N/A"),
                    "session_id": metadata.get("session_id", "Permanent")
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "question": question,
                "mode": "rag_with_documents",
                "context": context_info["context"]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la question: {e}")
            return {
                "answer": f"Erreur lors du traitement de votre question: {str(e)}",
                "sources": [],
                "question": question,
                "mode": "error",
                "context": "unknown"
            }
    
    def _handle_document_listing(self) -> Dict[str, Any]:
        """Gère la demande de liste des documents disponibles"""
        try:
            if not self.vector_store:
                return {
                    "answer": "Aucune base de documents disponible.",
                    "sources": [],
                    "question": "Quels documents sont disponibles ?",
                    "mode": "document_listing",
                    "context": "all_documents"
                }
            
            documents = self.vector_store.get_available_documents()
            
            if not documents:
                answer = "Aucun document n'est actuellement disponible dans ma base de données."
            else:
                answer = "Voici les documents disponibles dans ma base de données :\n\n"
                
                # Grouper par session
                sessions = {}
                for doc in documents:
                    session_id = doc.get("session_id", "Permanent")
                    if session_id not in sessions:
                        sessions[session_id] = []
                    sessions[session_id].append(doc)
                
                # Afficher par session
                for session_id, docs in sessions.items():
                    if session_id == "Permanent":
                        answer += "📚 **Documents permanents :**\n"
                    else:
                        answer += f"📄 **Documents de la session actuelle :**\n"
                    
                    for doc in docs:
                        answer += f"• **{doc['filename']}** ({doc['file_type']}) - {doc['chunks_count']} segments\n"
                    
                    answer += "\n"
                
                answer += "Vous pouvez me poser des questions sur n'importe lequel de ces documents !"
            
            return {
                "answer": answer,
                "sources": [],
                "question": "Quels documents sont disponibles ?",
                "mode": "document_listing",
                "context": "all_documents"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la liste des documents: {e}")
            return {
                "answer": f"Erreur lors de la récupération de la liste des documents: {str(e)}",
                "sources": [],
                "question": "Quels documents sont disponibles ?",
                "mode": "error",
                "context": "all_documents"
            }
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Retourne l'historique de conversation formaté"""
        try:
            messages = self.memory.chat_memory.messages if hasattr(self.memory, 'chat_memory') else []
            history = []
            
            for i in range(0, len(messages), 2):
                if i + 1 < len(messages):
                    history.append({
                        "question": messages[i].content,
                        "answer": messages[i + 1].content
                    })
            
            return history
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def clear_memory(self):
        """Efface la mémoire de conversation"""
        try:
            self.memory.clear()
            logger.info("Mémoire de conversation effacée")
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement de la mémoire: {e}")
    
    def clear_current_session(self):
        """Efface la session actuelle"""
        try:
            if self.vector_store and self.current_session_id:
                self.vector_store.clear_current_session()
                self.current_session_id = None
                logger.info("Session actuelle effacée")
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement de la session: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la chaîne RAG"""
        try:
            stats = {
                "model": self.model_config["model"],
                "embedding_model": "text-embedding-ada-002",
                "chunk_size": self.rag_config["chunk_size"],
                "top_k": self.rag_config["top_k"],
                "has_vector_store": self.vector_store is not None,
                "memory_messages": len(self.memory.chat_memory.messages) if hasattr(self.memory, 'chat_memory') else 0,
                "current_session_id": self.current_session_id
            }
            
            if self.vector_store:
                try:
                    collection = self.vector_store.client.get_collection(self.vector_store.collection_name)
                    stats["vector_store_documents"] = collection.count()
                    stats["available_documents"] = len(self.vector_store.get_available_documents())
                except:
                    stats["vector_store_documents"] = 0
                    stats["available_documents"] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {} 