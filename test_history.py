#!/usr/bin/env python3
"""
Script de test pour l'historique conversationnel
"""

import requests
import json
import time

API_URL = "http://localhost:8000"
API_TOKEN = "dev-secret-token"

def test_conversation_history():
    """Teste l'historique conversationnel"""
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Test de l'historique conversationnel")
    print("=" * 50)
    
    # 1. Vérifier l'état initial
    print("\n1. État initial de l'historique:")
    try:
        response = requests.get(f"{API_URL}/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            print(f"   ✅ Historique récupéré: {len(history.get('history', []))} entrées")
            for i, entry in enumerate(history.get('history', [])):
                print(f"   - Entrée {i+1}: {entry.get('question', 'N/A')[:50]}...")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 2. Poser quelques questions pour créer un historique
    questions = [
        "Bonjour, comment allez-vous ?",
        "Quels documents sont disponibles ?",
        "Pouvez-vous me dire ce que vous savez ?"
    ]
    
    print("\n2. Création de l'historique:")
    for i, question in enumerate(questions, 1):
        print(f"\n   Question {i}: {question}")
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question},
                headers=headers
            )
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Réponse reçue: {len(result.get('answer', ''))} caractères")
                print(f"   📚 Sources: {len(result.get('sources', []))}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        time.sleep(1)  # Pause entre les questions
    
    # 3. Vérifier l'historique après les questions
    print("\n3. Historique après les questions:")
    try:
        response = requests.get(f"{API_URL}/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            print(f"   ✅ Historique mis à jour: {len(history.get('history', []))} entrées")
            for i, entry in enumerate(history.get('history', [])):
                print(f"   - Entrée {i+1}: {entry.get('question', 'N/A')[:50]}...")
                print(f"     Réponse: {entry.get('answer', 'N/A')[:100]}...")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 4. Tester l'effacement de l'historique
    print("\n4. Test d'effacement de l'historique:")
    try:
        response = requests.delete(f"{API_URL}/history", headers=headers)
        if response.status_code == 200:
            print("   ✅ Historique effacé avec succès")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 5. Vérifier que l'historique est vide
    print("\n5. Vérification de l'historique vide:")
    try:
        response = requests.get(f"{API_URL}/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            print(f"   ✅ Historique vide: {len(history.get('history', []))} entrées")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test de l'historique terminé")

if __name__ == "__main__":
    test_conversation_history() 