#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration complète du système DocSearch AI
"""

import requests
import json
import time
import os

# Configuration
API_URL = "http://localhost:8000"
API_TOKEN = "dev-secret-token"

def test_health():
    """Test du endpoint de santé"""
    print("🔍 Test du endpoint de santé...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Serveur en ligne: {data}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_upload_sample():
    """Test d'upload d'un document de test"""
    print("\n📄 Test d'upload de document...")
    
    # Créer un fichier de test
    test_content = """
    Document de test pour DocSearch AI
    
    Ce document contient des informations sur l'intelligence artificielle.
    L'IA est un domaine de l'informatique qui vise à créer des systèmes capables
    de réaliser des tâches qui nécessitent normalement l'intelligence humaine.
    
    Les applications de l'IA incluent:
    - Traitement du langage naturel
    - Vision par ordinateur
    - Systèmes de recommandation
    - Automatisation des processus
    
    LangChain est une bibliothèque Python pour développer des applications IA.
    """
    
    with open("test_document.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        with open("test_document.txt", "rb") as f:
            files = {"files": f}
            headers = {"Authorization": f"Bearer {API_TOKEN}"}
            
            response = requests.post(f"{API_URL}/upload", files=files, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Document uploadé: {data}")
                return True
            else:
                print(f"❌ Erreur upload: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors de l'upload: {e}")
        return False
    finally:
        # Nettoyer le fichier de test
        if os.path.exists("test_document.txt"):
            os.remove("test_document.txt")

def test_question():
    """Test de pose de question"""
    print("\n🤔 Test de pose de question...")
    
    questions = [
        "Qu'est-ce que l'intelligence artificielle ?",
        "Quelles sont les applications de l'IA mentionnées ?",
        "Qu'est-ce que LangChain ?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            data = {"question": question}
            headers = {
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(f"{API_URL}/ask", json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Réponse: {result['answer'][:100]}...")
                if result.get('sources'):
                    print(f"📚 Sources: {len(result['sources'])} document(s)")
                return True
            else:
                print(f"❌ Erreur: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la question: {e}")
            return False

def test_conversation_history():
    """Test de l'historique de conversation"""
    print("\n💬 Test de l'historique de conversation...")
    
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(f"{API_URL}/chat/history", headers=headers)
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Historique récupéré: {len(history)} échanges")
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'historique: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test d'intégration DocSearch AI")
    print("=" * 50)
    
    # Attendre que les serveurs soient prêts
    print("⏳ Attente du démarrage des serveurs...")
    time.sleep(3)
    
    tests = [
        ("Santé du serveur", test_health),
        ("Upload de document", test_upload_sample),
        ("Pose de question", test_question),
        ("Historique de conversation", test_conversation_history)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 Résumé des tests:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests réussis")
    
    if passed == len(results):
        print("🎉 Tous les tests sont passés ! Le système fonctionne correctement.")
        print("\n🌐 Vous pouvez maintenant:")
        print("   • Ouvrir http://localhost:3000 pour l'interface web")
        print("   • Uploader des documents et poser des questions")
        print("   • Tester avec différents types de fichiers")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main() 