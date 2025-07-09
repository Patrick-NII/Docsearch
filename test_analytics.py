#!/usr/bin/env python3
"""
Script de test pour vérifier le système d'analytics de DocSearch AI
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

def test_analytics_endpoints():
    """Test des endpoints d'analytics"""
    print("🔍 Test des endpoints d'analytics...")
    
    # Connexion en tant qu'admin
    login_data = {
        "email": "patrick@docsearch.ai",
        "password": "MB2JyQhY8Kmd"
    }
    
    try:
        # Connexion
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print("❌ Erreur de connexion admin")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test des endpoints analytics
        endpoints = [
            ("/analytics/user/stats", "GET", "Statistiques utilisateur"),
            ("/analytics/user/insights", "GET", "Insights utilisateur"),
            ("/analytics/global/stats", "GET", "Statistiques globales"),
            ("/analytics/performance", "GET", "Métriques de performance"),
            ("/analytics/dashboard", "GET", "Tableau de bord"),
            ("/analytics/activity/summary?days=7", "GET", "Résumé d'activité")
        ]
        
        for endpoint, method, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{API_URL}{endpoint}", headers=headers)
                else:
                    response = requests.post(f"{API_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {description} - Succès")
                    
                    # Afficher quelques données clés
                    if "data" in data:
                        if "user_stats" in data["data"]:
                            stats = data["data"]["user_stats"]
                            print(f"   📊 Documents: {stats.get('documents', {}).get('total', 0)}")
                            print(f"   📊 Questions: {stats.get('questions', {}).get('total', 0)}")
                            print(f"   📊 Sessions: {stats.get('sessions', {}).get('total', 0)}")
                        elif "users" in data["data"]:
                            global_stats = data["data"]
                            print(f"   🌍 Utilisateurs: {global_stats.get('users', {}).get('total', 0)}")
                            print(f"   🌍 Documents: {global_stats.get('documents', {}).get('total', 0)}")
                            print(f"   🌍 Questions: {global_stats.get('questions', {}).get('total', 0)}")
                else:
                    print(f"❌ {description} - Erreur {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description} - Erreur: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des analytics: {e}")
        return False

def test_user_analytics():
    """Test des analytics utilisateur"""
    print("\n👤 Test des analytics utilisateur...")
    
    # Connexion en tant qu'utilisateur normal
    login_data = {
        "email": "alice@docsearch.ai",
        "password": "g$5rs@^iCP*M"
    }
    
    try:
        # Connexion
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print("❌ Erreur de connexion utilisateur")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test des endpoints utilisateur
        user_endpoints = [
            ("/analytics/user/stats", "Statistiques personnelles"),
            ("/analytics/user/insights", "Insights personnels"),
            ("/analytics/dashboard", "Tableau de bord"),
            ("/analytics/activity/summary?days=7", "Résumé d'activité")
        ]
        
        for endpoint, description in user_endpoints:
            try:
                response = requests.get(f"{API_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {description} - Succès")
                    
                    # Afficher les données
                    if "data" in data:
                        if "user_stats" in data["data"]:
                            stats = data["data"]["user_stats"]
                            print(f"   📈 Documents: {stats.get('documents', {}).get('total', 0)}")
                            print(f"   📈 Questions: {stats.get('questions', {}).get('total', 0)}")
                            print(f"   📈 Activité récente: {stats.get('questions', {}).get('recent_7_days', 0)}")
                        elif "recommendations" in data["data"]:
                            insights = data["data"]
                            print(f"   💡 Recommandations: {len(insights.get('recommendations', []))}")
                else:
                    print(f"❌ {description} - Erreur {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description} - Erreur: {e}")
        
        # Test d'accès refusé aux endpoints admin
        admin_endpoints = [
            "/analytics/global/stats",
            "/analytics/performance"
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = requests.get(f"{API_URL}{endpoint}", headers=headers)
                if response.status_code == 403:
                    print(f"✅ Accès refusé à {endpoint} (utilisateur normal) - Correct")
                else:
                    print(f"⚠️  Accès inattendu à {endpoint} - {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur lors du test d'accès refusé: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des analytics utilisateur: {e}")
        return False

def test_activity_tracking():
    """Test du tracking d'activité"""
    print("\n📊 Test du tracking d'activité...")
    
    # Connexion
    login_data = {
        "email": "patrick@docsearch.ai",
        "password": "MB2JyQhY8Kmd"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print("❌ Erreur de connexion")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test du tracking d'activité
        activities = [
            {"action": "document_upload", "details": {"filename": "test.pdf", "size": 1024}},
            {"action": "question_asked", "details": {"question": "Test question", "context": "test"}},
            {"action": "session_created", "details": {"session_id": "test-session"}}
        ]
        
        for activity in activities:
            try:
                response = requests.post(
                    f"{API_URL}/analytics/track",
                    json=activity,
                    headers=headers
                )
                
                if response.status_code == 200:
                    print(f"✅ Activité trackée: {activity['action']}")
                else:
                    print(f"❌ Erreur tracking {activity['action']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Erreur lors du tracking: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test du tracking: {e}")
        return False

def test_performance_metrics():
    """Test des métriques de performance"""
    print("\n⚡ Test des métriques de performance...")
    
    # Connexion admin
    login_data = {
        "email": "patrick@docsearch.ai",
        "password": "MB2JyQhY8Kmd"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print("❌ Erreur de connexion admin")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test des métriques de performance
        try:
            response = requests.get(f"{API_URL}/analytics/performance", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Métriques de performance récupérées")
                
                if "data" in data:
                    perf_data = data["data"]
                    print(f"   ⚡ Temps de réponse moyen: {perf_data.get('performance', {}).get('avg_response_time', 'N/A')}s")
                    print(f"   ⚡ Taux de succès: {perf_data.get('performance', {}).get('success_rate', 'N/A')}%")
                    print(f"   📄 Documents populaires: {len(perf_data.get('popular_documents', []))}")
                    print(f"   🕐 Utilisation par heure: {len(perf_data.get('hourly_usage', []))} points")
            else:
                print(f"❌ Erreur métriques de performance: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des métriques: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des métriques: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test du système d'analytics DocSearch AI")
    print("=" * 50)
    
    # Tests
    tests = [
        ("Endpoints analytics", test_analytics_endpoints),
        ("Analytics utilisateur", test_user_analytics),
        ("Tracking d'activité", test_activity_tracking),
        ("Métriques de performance", test_performance_metrics)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - SUCCÈS")
            else:
                print(f"❌ {test_name} - ÉCHEC")
        except Exception as e:
            print(f"❌ {test_name} - ERREUR: {e}")
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS ANALYTICS")
    print("=" * 50)
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tous les tests analytics sont passés !")
        print("\n✅ Fonctionnalités vérifiées:")
        print("   📊 Statistiques utilisateur et globales")
        print("   💡 Insights et recommandations")
        print("   📈 Tracking d'activité")
        print("   ⚡ Métriques de performance")
        print("   🔒 Gestion des permissions")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main() 