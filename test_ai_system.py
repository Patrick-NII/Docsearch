#!/usr/bin/env python3
"""
Script de test et démonstration du système IA DocSearch
Teste toutes les fonctionnalités : chargement de documents, RAG, API
"""

import os
import sys
import logging
from pathlib import Path
import json

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from document_loader import AdvancedDocumentLoader
from vector_store import VectorStore
from rag_chain import ModernRAGChain

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_document_loader():
    """Test du chargeur de documents"""
    print("\n" + "="*50)
    print("TEST DU CHARGEUR DE DOCUMENTS")
    print("="*50)
    
    try:
        # Initialiser le chargeur
        loader = AdvancedDocumentLoader()
        print("✅ Chargeur de documents initialisé")
        
        # Charger les documents du répertoire source
        documents = loader.load_documents()
        print(f"✅ {len(documents)} documents chargés")
        
        # Afficher les détails des documents
        for i, doc in enumerate(documents):
            metadata = doc.get("metadata", {})
            print(f"  📄 Document {i+1}: {metadata.get('filename', 'Inconnu')}")
            print(f"     Type: {metadata.get('file_type', 'Inconnu')}")
            print(f"     Taille: {metadata.get('file_size', 0)} bytes")
            print(f"     Texte: {len(doc.get('text', ''))} caractères")
            print()
        
        return documents
        
    except Exception as e:
        print(f"❌ Erreur lors du test du chargeur: {e}")
        return []

def test_vector_store():
    """Test de la base vectorielle"""
    print("\n" + "="*50)
    print("TEST DE LA BASE VECTORIELLE")
    print("="*50)
    
    try:
        # Initialiser la base vectorielle
        vector_store = VectorStore()
        print("✅ Base vectorielle initialisée")
        
        # Afficher les informations de la collection
        info = vector_store.get_collection_info()
        print(f"✅ Collection: {info.get('name', 'N/A')}")
        print(f"   Documents: {info.get('count', 0)}")
        print(f"   Modèle d'embedding: {info.get('embedding_model', 'N/A')}")
        
        return vector_store
        
    except Exception as e:
        print(f"❌ Erreur lors du test de la base vectorielle: {e}")
        return None

def test_rag_chain(documents, vector_store):
    """Test de la chaîne RAG"""
    print("\n" + "="*50)
    print("TEST DE LA CHAÎNE RAG")
    print("="*50)
    
    try:
        # Initialiser la chaîne RAG
        rag_chain = ModernRAGChain(vector_store)
        print("✅ Chaîne RAG initialisée")
        
        # Afficher les statistiques
        stats = rag_chain.get_stats()
        print(f"✅ Modèle: {stats.get('model', 'N/A')}")
        print(f"   Embedding: {stats.get('embedding_model', 'N/A')}")
        print(f"   Chunk size: {stats.get('chunk_size', 'N/A')}")
        print(f"   Top K: {stats.get('top_k', 'N/A')}")
        
        # Traiter les documents si disponibles
        if documents:
            print(f"\n📚 Traitement de {len(documents)} documents...")
            success = rag_chain.process_documents(documents)
            if success:
                print("✅ Documents traités avec succès")
                
                # Mettre à jour les stats
                stats = rag_chain.get_stats()
                print(f"   Documents dans la base: {stats.get('vector_store_documents', 0)}")
            else:
                print("❌ Erreur lors du traitement des documents")
        
        return rag_chain
        
    except Exception as e:
        print(f"❌ Erreur lors du test de la chaîne RAG: {e}")
        return None

def test_question_answering(rag_chain):
    """Test des questions-réponses"""
    print("\n" + "="*50)
    print("TEST DES QUESTIONS-RÉPONSES")
    print("="*50)
    
    if not rag_chain:
        print("❌ Chaîne RAG non disponible")
        return
    
    # Questions de test
    test_questions = [
        "Quel est le sujet principal de ce document ?",
        "Peux-tu me donner un résumé ?",
        "Y a-t-il des informations importantes à retenir ?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🤔 Question {i}: {question}")
        print("-" * 40)
        
        try:
            result = rag_chain.ask_question(question)
            
            print(f"📝 Réponse: {result.get('answer', 'Aucune réponse')}")
            print(f"🔍 Mode: {result.get('mode', 'N/A')}")
            
            sources = result.get('sources', [])
            if sources:
                print(f"📚 Sources ({len(sources)}):")
                for j, source in enumerate(sources, 1):
                    print(f"   {j}. {source.get('filename', 'Inconnu')}")
                    print(f"      Type: {source.get('file_type', 'Inconnu')}")
                    print(f"      Extrait: {source.get('text', '')[:100]}...")
            else:
                print("📚 Aucune source trouvée")
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement de la question: {e}")

def test_chat_history(rag_chain):
    """Test de l'historique de conversation"""
    print("\n" + "="*50)
    print("TEST DE L'HISTORIQUE DE CONVERSATION")
    print("="*50)
    
    if not rag_chain:
        print("❌ Chaîne RAG non disponible")
        return
    
    try:
        # Récupérer l'historique
        history = rag_chain.get_chat_history()
        print(f"✅ Historique récupéré: {len(history)} échanges")
        
        if history:
            print("\n📜 Historique:")
            for i, exchange in enumerate(history, 1):
                print(f"  {i}. Q: {exchange.get('question', 'N/A')}")
                print(f"     A: {exchange.get('answer', 'N/A')[:100]}...")
                print()
        else:
            print("📜 Aucun historique disponible")
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'historique: {e}")

def test_api_endpoints():
    """Test des endpoints API"""
    print("\n" + "="*50)
    print("TEST DES ENDPOINTS API")
    print("="*50)
    
    try:
        import requests
        
        # URL de base (à adapter selon votre configuration)
        base_url = "http://localhost:8000"
        
        # Test de l'endpoint racine
        print("🔗 Test de l'endpoint racine...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Endpoint racine accessible")
            print(f"   Réponse: {response.json()}")
        else:
            print(f"❌ Erreur endpoint racine: {response.status_code}")
        
        # Test de l'endpoint health
        print("\n🔗 Test de l'endpoint health...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Endpoint health accessible")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'N/A')}")
            print(f"   Services: {health_data.get('services', {})}")
        else:
            print(f"❌ Erreur endpoint health: {response.status_code}")
            
    except ImportError:
        print("⚠️  Module requests non installé, test API ignoré")
    except Exception as e:
        print(f"❌ Erreur lors du test API: {e}")

def create_sample_documents():
    """Crée des documents d'exemple pour les tests"""
    print("\n" + "="*50)
    print("CRÉATION DE DOCUMENTS D'EXEMPLE")
    print("="*50)
    
    # Créer le répertoire source s'il n'existe pas
    source_dir = Path(settings.SOURCE_DIR)
    source_dir.mkdir(exist_ok=True)
    
    # Document texte d'exemple
    sample_text = """DocSearch AI - Assistant Intelligent de Documents

DocSearch AI est un système d'intelligence artificielle avancé conçu pour analyser et interroger des documents de manière intelligente.

Fonctionnalités principales:
- Lecture de documents PDF, images, Word, Excel
- Extraction de texte via OCR pour les images
- Recherche sémantique dans les documents
- Réponses intelligentes basées sur le contenu
- Historique de conversation

Technologies utilisées:
- LangChain pour la chaîne RAG
- OpenAI GPT pour la génération de réponses
- ChromaDB pour la base vectorielle
- FastAPI pour l'interface API

Ce système permet aux utilisateurs de poser des questions naturelles sur leurs documents et d'obtenir des réponses précises et contextuelles."""
    
    # Créer le fichier texte
    text_file = source_dir / "presentation.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print(f"✅ Document d'exemple créé: {text_file}")
    
    # Créer un fichier CSV d'exemple
    csv_content = """Nom,Age,Ville,Profession
Jean Dupont,30,Paris,Développeur
Marie Martin,25,Lyon,Designer
Pierre Durand,35,Marseille,Manager
Sophie Bernard,28,Toulouse,Analyste"""
    
    csv_file = source_dir / "utilisateurs.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    print(f"✅ Fichier CSV d'exemple créé: {csv_file}")

def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE DES TESTS DU SYSTÈME IA DOCSEARCH")
    print("="*60)
    
    # Vérifier la configuration
    print(f"🔧 Configuration:")
    print(f"   Modèle OpenAI: {settings.OPENAI_MODEL}")
    print(f"   API Key configurée: {'✅' if settings.OPENAI_API_KEY else '❌'}")
    print(f"   Répertoire source: {settings.SOURCE_DIR}")
    print(f"   Base vectorielle: {settings.VECTOR_DB_PATH}")
    
    # Créer des documents d'exemple si le répertoire source est vide
    source_dir = Path(settings.SOURCE_DIR)
    if not source_dir.exists() or not list(source_dir.glob("*")):
        create_sample_documents()
    
    # Tests
    documents = test_document_loader()
    vector_store = test_vector_store()
    rag_chain = test_rag_chain(documents, vector_store)
    
    if rag_chain:
        test_question_answering(rag_chain)
        test_chat_history(rag_chain)
    
    test_api_endpoints()
    
    print("\n" + "="*60)
    print("✅ TESTS TERMINÉS")
    print("="*60)
    
    print("\n📋 PROCHAINES ÉTAPES:")
    print("1. Configurez votre clé API OpenAI dans le fichier .env")
    print("2. Lancez l'API avec: python api_server.py")
    print("3. Testez les endpoints avec curl ou Postman")
    print("4. Intégrez avec votre frontend Next.js")

if __name__ == "__main__":
    main() 