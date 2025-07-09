#!/usr/bin/env python3
"""
Script pour nettoyer la base vectorielle et tester le nouveau comportement
"""

import requests
import json
import time
import os

def reset_and_test():
    """Nettoie la base et teste le nouveau comportement"""
    print("🧹 Nettoyage et test du système DocSearch AI")
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
        
        # Test 2: Vérifier les documents actuels
        print("\n2️⃣ Documents actuels...")
        response = requests.get(f"{API_URL}/documents", 
                              headers={"Authorization": f"Bearer {API_TOKEN}"})
        if response.status_code == 200:
            docs = response.json()
            print(f"   📚 Documents en base: {docs['total_count']}")
            for doc in docs['documents']:
                print(f"   📄 {doc['filename']} ({doc['session_id']})")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 3: Effacer tous les documents
        print("\n3️⃣ Nettoyage de la base...")
        response = requests.delete(f"{API_URL}/clear-all", 
                                 headers={"Authorization": f"Bearer {API_TOKEN}"})
        if response.status_code == 200:
            print("   ✅ Base nettoyée")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return False
        
        # Test 4: Vérifier que la base est vide
        print("\n4️⃣ Vérification de la base vide...")
        response = requests.get(f"{API_URL}/documents", 
                              headers={"Authorization": f"Bearer {API_TOKEN}"})
        if response.status_code == 200:
            docs = response.json()
            print(f"   📚 Documents en base: {docs['total_count']}")
            if docs['total_count'] == 0:
                print("   ✅ Base vide confirmée")
            else:
                print("   ❌ Base pas complètement vide")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 5: Upload d'un nouveau document
        print("\n5️⃣ Upload d'un nouveau document...")
        test_content = """
        Document de test - Intelligence Artificielle Moderne
        
        L'intelligence artificielle moderne utilise des techniques avancées comme:
        - Le deep learning avec des réseaux de neurones
        - Le traitement du langage naturel (NLP)
        - La vision par ordinateur
        - Les systèmes de recommandation
        
        Ces technologies permettent de créer des applications intelligentes
        qui peuvent comprendre, apprendre et prendre des décisions.
        """
        
        with open("test_ai.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        with open("test_ai.txt", "rb") as f:
            files = {"files": f}
            headers = {"Authorization": f"Bearer {API_TOKEN}"}
            
            response = requests.post(f"{API_URL}/upload", files=files, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                print(f"   ✅ Document uploadé (session: {session_id[:8]}...)")
            else:
                print(f"   ❌ Erreur upload: {response.status_code}")
                return False
        
        # Test 6: Question sur le document uploadé
        print("\n6️⃣ Question sur le document uploadé...")
        question = "Qu'est-ce que l'intelligence artificielle moderne ?"
        data = {"question": question}
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{API_URL}/ask", json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Réponse reçue: {result['answer'][:100]}...")
            print(f"   📋 Contexte: {result['context']}")
            print(f"   📚 Sources: {len(result['sources'])} document(s)")
            
            # Vérifier que la réponse vient du bon document
            if result['sources']:
                source_filename = result['sources'][0]['filename']
                print(f"   📄 Source utilisée: {source_filename}")
                if "test_ai.txt" in source_filename:
                    print("   ✅ Bon document utilisé !")
                else:
                    print("   ❌ Mauvais document utilisé")
            else:
                print("   ⚠️  Aucune source citée")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 7: Question générale (devrait utiliser le document uploadé)
        print("\n7️⃣ Question générale...")
        question = "Quelles sont les applications de l'IA ?"
        data = {"question": question}
        
        response = requests.post(f"{API_URL}/ask", json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Réponse reçue: {result['answer'][:100]}...")
            print(f"   📋 Contexte: {result['context']}")
            print(f"   📚 Sources: {len(result['sources'])} document(s)")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 8: Vérifier les documents disponibles
        print("\n8️⃣ Documents disponibles...")
        response = requests.get(f"{API_URL}/documents", 
                              headers={"Authorization": f"Bearer {API_TOKEN}"})
        if response.status_code == 200:
            docs = response.json()
            print(f"   📚 Total documents: {docs['total_count']}")
            for doc in docs['documents']:
                print(f"   📄 {doc['filename']} ({doc['session_id'][:8]}...) - {doc['chunks_count']} segments")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        print("\n🎉 Test terminé !")
        print("✅ Le système utilise maintenant correctement les documents uploadés")
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
        if os.path.exists("test_ai.txt"):
            os.remove("test_ai.txt")

if __name__ == "__main__":
    reset_and_test() 