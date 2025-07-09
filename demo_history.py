#!/usr/bin/env python3
"""
Démonstration de l'historique conversationnel avec DocSearch AI
"""

import requests
import json
import time

API_URL = "http://localhost:8000"
API_TOKEN = "dev-secret-token"

def demo_conversation_history():
    """Démonstration complète de l'historique conversationnel"""
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🎭 Démonstration de l'historique conversationnel")
    print("=" * 60)
    
    # 1. Conversation initiale
    print("\n1️⃣ Conversation initiale:")
    print("-" * 30)
    
    conversation_1 = [
        "Bonjour ! Pouvez-vous vous présenter ?",
        "Quels types de documents pouvez-vous analyser ?",
        "Comment fonctionne votre système de recherche ?"
    ]
    
    for i, question in enumerate(conversation_1, 1):
        print(f"\n🤔 Question {i}: {question}")
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question},
                headers=headers
            )
            if response.status_code == 200:
                result = response.json()
                print(f"💬 Réponse: {result.get('answer', '')[:150]}...")
                print(f"📚 Sources: {len(result.get('sources', []))}")
                print(f"🏷️ Contexte: {result.get('context', 'N/A')}")
            else:
                print(f"❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        time.sleep(1)
    
    # 2. Vérifier l'historique
    print("\n\n2️⃣ Vérification de l'historique:")
    print("-" * 30)
    try:
        response = requests.get(f"{API_URL}/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            print(f"📝 Historique actuel: {len(history.get('history', []))} entrées")
            for i, entry in enumerate(history.get('history', []), 1):
                print(f"   {i}. Q: {entry.get('question', 'N/A')[:50]}...")
                print(f"      A: {entry.get('answer', 'N/A')[:80]}...")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 3. Continuer la conversation avec référence au contexte
    print("\n\n3️⃣ Conversation avec contexte:")
    print("-" * 30)
    
    conversation_2 = [
        "Peux-tu me rappeler ce que tu viens de dire sur ton fonctionnement ?",
        "En te basant sur notre conversation précédente, que sais-tu de moi ?",
        "Peux-tu résumer notre échange jusqu'à présent ?"
    ]
    
    for i, question in enumerate(conversation_2, 1):
        print(f"\n🤔 Question {i}: {question}")
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question},
                headers=headers
            )
            if response.status_code == 200:
                result = response.json()
                print(f"💬 Réponse: {result.get('answer', '')[:200]}...")
                print(f"📚 Sources: {len(result.get('sources', []))}")
                print(f"🏷️ Contexte: {result.get('context', 'N/A')}")
            else:
                print(f"❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        time.sleep(1)
    
    # 4. Vérifier l'historique final
    print("\n\n4️⃣ Historique final:")
    print("-" * 30)
    try:
        response = requests.get(f"{API_URL}/history", headers=headers)
        if response.status_code == 200:
            history = response.json()
            print(f"📝 Historique final: {len(history.get('history', []))} entrées")
            print("📊 Résumé de la conversation:")
            for i, entry in enumerate(history.get('history', []), 1):
                print(f"   {i}. {entry.get('question', 'N/A')[:60]}...")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 5. Statistiques du système
    print("\n\n5️⃣ Statistiques du système:")
    print("-" * 30)
    try:
        response = requests.get(f"{API_URL}/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"🧠 Modèle: {stats.get('model', 'N/A')}")
            print(f"📊 Messages en mémoire: {stats.get('memory_messages', 0)}")
            print(f"📚 Documents disponibles: {stats.get('available_documents', 0)}")
            print(f"🔗 Session active: {stats.get('current_session_id', 'Aucune')}")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Démonstration terminée !")
    print("\n💡 Fonctionnalités testées:")
    print("   • Conservation de l'historique conversationnel")
    print("   • Référence au contexte précédent")
    print("   • Mémoire persistante entre les questions")
    print("   • Statistiques du système")
    print("\n🌐 Testez maintenant l'interface web sur http://localhost:3001")

if __name__ == "__main__":
    demo_conversation_history() 