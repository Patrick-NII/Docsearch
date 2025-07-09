#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration frontend-backend avec authentification JWT
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test de santé du backend"""
    print("🔍 Test de santé du backend...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Backend opérationnel")
            return True
        else:
            print(f"❌ Backend non opérationnel: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion au backend: {e}")
        return False

def test_frontend_health():
    """Test de santé du frontend"""
    print("🔍 Test de santé du frontend...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("✅ Frontend opérationnel")
            return True
        else:
            print(f"❌ Frontend non opérationnel: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion au frontend: {e}")
        return False

def test_authentication_flow():
    """Test du flux d'authentification"""
    print("\n🔐 Test du flux d'authentification...")
    
    # Test de connexion avec un utilisateur existant
    login_data = {
        "email": "patrick@docsearch.ai",
        "password": "MB2JyQhY8Kmd"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user")
            
            print("✅ Connexion réussie")
            print(f"   Utilisateur: {user['username']} ({user['email']})")
            print(f"   Admin: {user['is_admin']}")
            print(f"   Token: {token[:20]}...")
            
            # Test de récupération du profil avec le token
            headers = {"Authorization": f"Bearer {token}"}
            profile_response = requests.get(f"{API_URL}/auth/me", headers=headers)
            
            if profile_response.status_code == 200:
                print("✅ Récupération du profil réussie")
                return True
            else:
                print(f"❌ Erreur lors de la récupération du profil: {profile_response.status_code}")
                return False
                
        else:
            print(f"❌ Erreur de connexion: {response.status_code}")
            print(f"   Détail: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test d'authentification: {e}")
        return False

def test_protected_endpoints():
    """Test des endpoints protégés"""
    print("\n🔒 Test des endpoints protégés...")
    
    # Connexion pour obtenir un token
    login_data = {
        "email": "alice@docsearch.ai",
        "password": "g$5rs@^iCP*M"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print("❌ Impossible de se connecter pour tester les endpoints protégés")
            return False
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test des endpoints protégés
        endpoints = [
            ("/stats", "GET"),
            ("/documents", "GET"),
            ("/history", "GET")
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{API_URL}{endpoint}", headers=headers)
                else:
                    response = requests.post(f"{API_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - Accès autorisé")
                else:
                    print(f"❌ {endpoint} - Erreur {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - Erreur: {e}")
        
        # Test d'accès sans token (doit échouer)
        try:
            response = requests.get(f"{API_URL}/stats")
            if response.status_code == 401:
                print("✅ Protection des endpoints fonctionnelle (401 sans token)")
            else:
                print(f"⚠️  Endpoint non protégé: /stats retourne {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur lors du test de protection: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des endpoints protégés: {e}")
        return False

def test_admin_endpoints():
    """Test des endpoints administrateur"""
    print("\n👑 Test des endpoints administrateur...")
    
    # Connexion en tant qu'admin
    login_data = {
        "email": "patrick@docsearch.ai",
        "password": "MB2JyQhY8Kmd"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print("❌ Impossible de se connecter en tant qu'admin")
            return False
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test des endpoints admin
        admin_endpoints = [
            ("/users/stats", "GET"),
            ("/users", "GET")
        ]
        
        for endpoint, method in admin_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{API_URL}{endpoint}", headers=headers)
                else:
                    response = requests.post(f"{API_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - Accès admin autorisé")
                else:
                    print(f"❌ {endpoint} - Erreur {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - Erreur: {e}")
        
        # Test d'accès admin avec un compte non-admin (doit échouer)
        user_login_data = {
            "email": "alice@docsearch.ai",
            "password": "g$5rs@^iCP*M"
        }
        
        user_response = requests.post(f"{API_URL}/auth/login", json=user_login_data)
        if user_response.status_code == 200:
            user_token = user_response.json()["access_token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            
            try:
                response = requests.get(f"{API_URL}/users/stats", headers=user_headers)
                if response.status_code == 403:
                    print("✅ Protection des endpoints admin fonctionnelle (403 pour non-admin)")
                else:
                    print(f"⚠️  Endpoint admin non protégé: /users/stats retourne {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur lors du test de protection admin: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des endpoints admin: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test d'intégration frontend-backend avec authentification JWT")
    print("=" * 60)
    
    # Tests de santé
    backend_ok = test_backend_health()
    frontend_ok = test_frontend_health()
    
    if not backend_ok:
        print("\n❌ Backend non disponible. Assurez-vous qu'il est démarré sur http://localhost:8000")
        return
    
    if not frontend_ok:
        print("\n⚠️  Frontend non disponible. Assurez-vous qu'il est démarré sur http://localhost:3000")
        print("   Le test continuera avec le backend uniquement.")
    
    # Tests d'authentification
    auth_ok = test_authentication_flow()
    protected_ok = test_protected_endpoints()
    admin_ok = test_admin_endpoints()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    tests = [
        ("Backend", backend_ok),
        ("Frontend", frontend_ok),
        ("Authentification", auth_ok),
        ("Endpoints protégés", protected_ok),
        ("Endpoints admin", admin_ok)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'intégration fonctionne correctement.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main() 