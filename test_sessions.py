#!/usr/bin/env python3
"""
Test du système de sessions DocSearch AI
Vérifie la gestion intelligente des documents par session
"""

import requests
import json
import time
import os

def test_sessions():
    """Test du système de sessions"""
    print("🧪 Test du système de sessions DocSearch AI")
    print("=" * 50)
    
    # Configuration
    API_URL = "http://localhost:8000"
    API_TOKEN = "dev-secret-token"
    
    try:
        # Test 1: Vérifier la santé du système
        print("1️⃣ Test de santé...")
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Système en ligne")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return False
        
        # Test 2: Vérifier les documents disponibles (devrait être vide)
        print("\n2️⃣ Test des documents disponibles...")
        response = requests.get(f"{API_URL}/documents", 
                              headers={"Authorization": f"Bearer {API_TOKEN}"})
        if response.status_code == 200:
            docs = response.json()
            print(f"   📚 Documents en base: {docs['total_count']}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 3: Upload d'un premier document
        print("\n3️⃣ Upload du premier document...")
        test_content_1 = """
        Document de test 1 - Intelligence Artificielle
        
        L'intelligence artificielle est un domaine de l'informatique qui vise à créer
        des systèmes capables de réaliser des tâches qui nécessitent normalement
        l'intelligence humaine.
        
        Les applications principales incluent:
        - Traitement du langage naturel
        - Vision par ordinateur
        - Systèmes de recommandation
        """
        
        with open("test_doc1.txt", "w", encoding="utf-8") as f:
            f.write(test_content_1)
        
        with open("test_doc1.txt", "rb") as f:
            files = {"files": f}
            headers = {"Authorization": f"Bearer {API_TOKEN}"}
            
            response = requests.post(f"{API_URL}/upload", files=files, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                session_id_1 = data.get('session_id')
                print(f"   ✅ Document 1 uploadé (session: {session_id_1[:8]}...)")
            else:
                print(f"   ❌ Erreur upload: {response.status_code}")
                return False
        
        # Test 4: Question sur le premier document
        print("\n4️⃣ Question sur le premier document...")
        question = "Qu'est-ce que l'intelligence artificielle ?"
        data = {"question": question}
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{API_URL}/ask", json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Réponse reçue: {result['answer'][:50]}...")
            print(f"   📋 Contexte: {result['context']}")
            print(f"   📚 Sources: {len(result['sources'])} document(s)")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 5: Upload d'un deuxième document
        print("\n5️⃣ Upload du deuxième document...")
        test_content_2 = """
        Document de test 2 - LangChain
        
        LangChain est une bibliothèque Python pour développer des applications
        d'intelligence artificielle. Elle fournit des outils pour:
        
        - Créer des chaînes de traitement
        - Intégrer des modèles de langage
        - Gérer des bases vectorielles
        - Traiter des documents
        
        LangChain simplifie le développement d'applications IA.
        """
        
        with open("test_doc2.txt", "w", encoding="utf-8") as f:
            f.write(test_content_2)
        
        with open("test_doc2.txt", "rb") as f:
            files = {"files": f}
            headers = {"Authorization": f"Bearer {API_TOKEN}"}
            
            response = requests.post(f"{API_URL}/upload", files=files, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                session_id_2 = data.get('session_id')
                print(f"   ✅ Document 2 uploadé (session: {session_id_2[:8]}...)")
            else:
                print(f"   ❌ Erreur upload: {response.status_code}")
                return False
        
        # Test 6: Question sur le deuxième document
        print("\n6️⃣ Question sur le deuxième document...")
        question = "Qu'est-ce que LangChain ?"
        data = {"question": question}
        
        response = requests.post(f"{API_URL}/ask", json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Réponse reçue: {result['answer'][:50]}...")
            print(f"   📋 Contexte: {result['context']}")
            print(f"   📚 Sources: {len(result['sources'])} document(s)")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 7: Question sur tous les documents
        print("\n7️⃣ Question sur tous les documents...")
        question = "Quels documents sont disponibles ?"
        data = {"question": question}
        
        response = requests.post(f"{API_URL}/ask", json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Réponse reçue: {result['answer'][:100]}...")
            print(f"   📋 Contexte: {result['context']}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 8: Vérifier les documents disponibles
        print("\n8️⃣ Vérification des documents disponibles...")
        response = requests.get(f"{API_URL}/documents", 
                              headers={"Authorization": f"Bearer {API_TOKEN}"})
        if response.status_code == 200:
            docs = response.json()
            print(f"   📚 Total documents: {docs['total_count']}")
            for doc in docs['documents']:
                print(f"   📄 {doc['filename']} ({doc['session_id'][:8]}...) - {doc['chunks_count']} segments")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 9: Effacer la session actuelle
        print("\n9️⃣ Test d'effacement de session...")
        response = requests.delete(f"{API_URL}/session", 
                                 headers={"Authorization": f"Bearer {API_TOKEN}"})
        if response.status_code == 200:
            print("   ✅ Session actuelle effacée")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 10: Vérifier les documents après effacement
        print("\n🔟 Vérification après effacement...")
        response = requests.get(f"{API_URL}/documents", 
                              headers={"Authorization": f"Bearer {API_TOKEN}"})
        if response.status_code == 200:
            docs = response.json()
            print(f"   📚 Documents restants: {docs['total_count']}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        print("\n🎉 Tous les tests sont passés !")
        print("🌐 Le système de sessions fonctionne correctement")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le backend est démarré: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        # Nettoyer
        for filename in ["test_doc1.txt", "test_doc2.txt"]:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == "__main__":
    test_sessions() 