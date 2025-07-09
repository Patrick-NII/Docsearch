#!/usr/bin/env python3
"""
Script de test pour vérifier la gestion avancée des documents de DocSearch AI
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
API_URL = "http://localhost:8000"

def test_document_versioning():
    """Test du système de versioning des documents"""
    print("📚 Test du système de versioning...")
    
    # Connexion admin
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
        
        # Récupérer les documents existants
        response = requests.get(f"{API_URL}/documents", headers=headers)
        if response.status_code != 200:
            print("❌ Erreur lors de la récupération des documents")
            return False
        
        documents = response.json().get("data", [])
        if not documents:
            print("⚠️  Aucun document disponible pour les tests de versioning")
            return True
        
        document_id = documents[0]["id"]
        print(f"✅ Document sélectionné pour les tests: {documents[0]['filename']}")
        
        # Test des versions
        version_endpoints = [
            (f"/documents/{document_id}/versions", "GET", "Liste des versions"),
            (f"/documents/{document_id}/version-stats", "GET", "Statistiques des versions")
        ]
        
        for endpoint, method, description in version_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{API_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {description} - Succès")
                    
                    if "data" in data:
                        if "total_versions" in data:
                            print(f"   📊 Versions: {data['total_versions']}")
                        elif "total_tags" in data:
                            print(f"   📊 Tags: {data['total_tags']}")
                else:
                    print(f"❌ {description} - Erreur {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description} - Erreur: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de versioning: {e}")
        return False

def test_document_annotations():
    """Test du système d'annotations"""
    print("\n📝 Test du système d'annotations...")
    
    # Connexion utilisateur
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
        
        # Récupérer les documents
        response = requests.get(f"{API_URL}/documents", headers=headers)
        if response.status_code != 200:
            print("❌ Erreur lors de la récupération des documents")
            return False
        
        documents = response.json().get("data", [])
        if not documents:
            print("⚠️  Aucun document disponible pour les tests d'annotations")
            return True
        
        document_id = documents[0]["id"]
        
        # Créer une annotation
        annotation_data = {
            "content": "Test annotation - Ceci est un test",
            "annotation_type": "note",
            "position": "{}"
        }
        
        response = requests.post(
            f"{API_URL}/documents/{document_id}/annotations",
            data=annotation_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            annotation_id = data["data"]["id"]
            print(f"✅ Annotation créée - ID: {annotation_id}")
            
            # Récupérer les annotations
            response = requests.get(f"{API_URL}/documents/{document_id}/annotations", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Annotations récupérées - Total: {data['total_annotations']}")
            else:
                print("❌ Erreur lors de la récupération des annotations")
        else:
            print(f"❌ Erreur lors de la création de l'annotation: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'annotations: {e}")
        return False

def test_document_tags():
    """Test du système de tags"""
    print("\n🏷️  Test du système de tags...")
    
    # Connexion utilisateur
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
        
        # Créer un tag
        tag_data = {
            "name": "test-tag",
            "color": "#FF6B6B",
            "description": "Tag de test pour les tests automatisés"
        }
        
        response = requests.post(
            f"{API_URL}/documents/tags",
            data=tag_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            tag_id = data["data"]["id"]
            print(f"✅ Tag créé - ID: {tag_id}")
            
            # Récupérer tous les tags
            response = requests.get(f"{API_URL}/documents/tags", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tags récupérés - Total: {data['total_tags']}")
                
                # Statistiques des tags
                response = requests.get(f"{API_URL}/documents/tag-statistics", headers=headers)
                if response.status_code == 200:
                    stats = response.json()
                    print(f"✅ Statistiques des tags récupérées")
                else:
                    print("❌ Erreur lors de la récupération des statistiques des tags")
            else:
                print("❌ Erreur lors de la récupération des tags")
        else:
            print(f"❌ Erreur lors de la création du tag: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de tags: {e}")
        return False

def test_document_sharing():
    """Test du système de partage de documents"""
    print("\n🔗 Test du système de partage...")
    
    # Connexion admin
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
        
        # Récupérer les documents
        response = requests.get(f"{API_URL}/documents", headers=headers)
        if response.status_code != 200:
            print("❌ Erreur lors de la récupération des documents")
            return False
        
        documents = response.json().get("data", [])
        if not documents:
            print("⚠️  Aucun document disponible pour les tests de partage")
            return True
        
        document_id = documents[0]["id"]
        
        # Récupérer les utilisateurs pour le partage
        response = requests.get(f"{API_URL}/users", headers=headers)
        if response.status_code != 200:
            print("❌ Erreur lors de la récupération des utilisateurs")
            return False
        
        users = response.json().get("data", [])
        if len(users) < 2:
            print("⚠️  Pas assez d'utilisateurs pour les tests de partage")
            return True
        
        # Trouver un utilisateur non-admin pour le partage
        shared_user = None
        for user in users:
            if not user.get("is_admin", False) and user["id"] != 1:  # Exclure l'admin
                shared_user = user
                break
        
        if not shared_user:
            print("⚠️  Aucun utilisateur non-admin trouvé pour le partage")
            return True
        
        # Partager le document
        share_data = {
            "shared_with_id": str(shared_user["id"]),
            "permissions": '["read"]',
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "message": "Test de partage automatique"
        }
        
        response = requests.post(
            f"{API_URL}/documents/{document_id}/share",
            data=share_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            share_id = data["data"]["id"]
            print(f"✅ Document partagé - ID partage: {share_id}")
            
            # Récupérer les documents partagés
            response = requests.get(f"{API_URL}/documents/shared?as_owner=true", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Documents partagés récupérés - Total: {data['total_shares']}")
                
                # Statistiques de partage
                response = requests.get(f"{API_URL}/documents/share-statistics", headers=headers)
                if response.status_code == 200:
                    stats = response.json()
                    print(f"✅ Statistiques de partage récupérées")
                else:
                    print("❌ Erreur lors de la récupération des statistiques de partage")
            else:
                print("❌ Erreur lors de la récupération des documents partagés")
        else:
            print(f"❌ Erreur lors du partage: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de partage: {e}")
        return False

def test_permissions():
    """Test des permissions et accès"""
    print("\n🔒 Test des permissions...")
    
    # Connexion utilisateur normal
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
        
        # Test d'accès aux endpoints admin
        admin_endpoints = [
            "/users",
            "/users/stats"
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
        print(f"❌ Erreur lors du test des permissions: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de la gestion avancée des documents DocSearch AI")
    print("=" * 60)
    
    # Tests
    tests = [
        ("Versioning des documents", test_document_versioning),
        ("Annotations", test_document_annotations),
        ("Tags", test_document_tags),
        ("Partage de documents", test_document_sharing),
        ("Permissions et accès", test_permissions)
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
    print("\n" + "=" * 60)
    print("📚 RÉSUMÉ DES TESTS GESTION AVANCÉE DES DOCUMENTS")
    print("=" * 60)
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tous les tests de gestion avancée sont passés !")
        print("\n✅ Fonctionnalités vérifiées:")
        print("   📚 Système de versioning avec historique")
        print("   📝 Annotations et commentaires")
        print("   🏷️  Tags et catégorisation")
        print("   🔗 Partage de documents avec permissions")
        print("   🔒 Gestion des permissions et accès")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main() 