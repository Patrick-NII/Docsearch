#!/usr/bin/env python3
"""
DocSearch - Assistant IA de Lecture de Document
Point d'entrée de l'application
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.append(str(Path(__file__).parent))

from config import Config
from document_loader import DocumentLoader
from text_splitter import TextSplitter
from vector_store import VectorStore
from rag_chain import RAGChain
from qa_interface import QAInterface
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    print("🔍 Vérification des dépendances...")
    
    try:
        import streamlit
        import langchain
        import chromadb
        import PyPDF2
        import sentence_transformers
        print("✅ Dépendances OK")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        return False

def check_ollama():
    """Vérifie qu'Ollama est disponible"""
    print("🔑 Vérification d'Ollama...")
    
    try:
        from langchain_community.llms import Ollama
        # Test simple de connexion
        llm = Ollama(model="llama2")
        print("✅ Ollama disponible")
        return True
    except Exception as e:
        print(f"⚠️ Ollama non disponible: {e}")
        print("💡 Installez Ollama et téléchargez un modèle avec: ollama pull llama2")
        return False

def setup_directories():
    """Crée les répertoires nécessaires"""
    Path(Config.SOURCE_DIR).mkdir(exist_ok=True)
    Path(Config.VECTOR_DB_PATH).mkdir(exist_ok=True)

def load_documents():
    """Charge et indexe les documents"""
    print("📄 Chargement des documents...")
    
    # Charger les documents
    loader = DocumentLoader()
    documents = loader.load_documents(Config.SOURCE_DIR)
    
    if not documents:
        print("⚠️ Aucun document trouvé dans le dossier 'source/'")
        print("💡 Placez vos fichiers PDF ou TXT dans le dossier 'source/'")
        return None, None
    
    print(f"📄 {len(documents)} document(s) trouvé(s)")
    
    # Découper en chunks
    splitter = TextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    
    # Indexer dans la base vectorielle
    vector_store = VectorStore(Config.VECTOR_DB_PATH)
    vector_store.add_chunks(chunks)
    
    return vector_store, chunks

def main():
    """Fonction principale"""
    print("🚀 Assistant IA de Lecture de Document")
    print("=" * 50)
    
    # Vérifications préliminaires
    if not check_dependencies():
        return
    
    # Charger la configuration
    Config.load_config()
    
    # Vérifier Ollama
    if not check_ollama():
        print("⚠️ L'application peut fonctionner sans Ollama, mais certaines fonctionnalités seront limitées")
    
    # Créer les répertoires
    setup_directories()
    
    # Charger les documents
    vector_store, chunks = load_documents()
    
    if vector_store is None:
        print("❌ Impossible de charger les documents")
        return
    
    print("\n🎯 Lancement de l'application...")
    print("🌐 L'application sera accessible à l'adresse: http://localhost:8501")
    print("🛑 Appuyez sur Ctrl+C pour arrêter l'application")
    print("=" * 50)
    
    # Créer la chaîne RAG
    rag_chain = RAGChain(vector_store)
    
    # Créer l'interface
    interface = QAInterface(rag_chain)
    
    # Lancer l'interface Streamlit
    interface.run()

if __name__ == "__main__":
    main() 