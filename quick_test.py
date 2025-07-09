#!/usr/bin/env python3
"""
Test rapide de DocSearch AI
Vérifie que le système fonctionne correctement
"""

import requests
import json

def quick_test():
    """Test rapide du système"""
    print("🧪 Test rapide DocSearch AI")
    print("=" * 40)
    
    # Configuration
    API_URL = "http://localhost:8000"
    API_TOKEN = "dev-secret-token"
    
    try:
        # Test 1: Santé du système
        print("1️⃣ Test de santé...")
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Système en ligne: {data['status']}")
            print(f"   🤖 OpenAI configuré: {data['openai_configured']}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return False
        
        # Test 2: Upload d'un document de test
        print("\n2️⃣ Test d'upload...")
        test_content = "Ceci est un document de test pour DocSearch AI."
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        with open("test.txt", "rb") as f:
            files = {"files": f}
            headers = {"Authorization": f"Bearer {API_TOKEN}"}
            response = requests.post(f"{API_URL}/upload", files=files, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Document uploadé avec succès")
        else:
            print(f"   ❌ Erreur upload: {response.status_code}")
            return False
        
        # Test 3: Pose de question
        print("\n3️⃣ Test de question...")
        data = {"question": "Que contient ce document ?"}
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{API_URL}/ask", json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Réponse reçue: {result['answer'][:50]}...")
            if result.get('sources'):
                print(f"   📚 Sources: {len(result['sources'])} document(s)")
        else:
            print(f"   ❌ Erreur question: {response.status_code}")
            return False
        
        print("\n🎉 Tous les tests sont passés !")
        print("🌐 Ouvrez http://localhost:3000 pour utiliser l'interface web")
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
        import os
        if os.path.exists("test.txt"):
            os.remove("test.txt")

if __name__ == "__main__":
    quick_test() 