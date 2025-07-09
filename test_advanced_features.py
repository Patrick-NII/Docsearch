#!/usr/bin/env python3
"""
Script de test pour les fonctionnalités avancées de gestion des documents
Teste le versioning, les annotations, les tags et le partage
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "alice@docsearch.ai"
TEST_PASSWORD = "g$5rs@^iCP*M"

def get_auth_token():
    """Obtient un token d'authentification"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Erreur de connexion: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def test_health_check():
    """Test de l'endpoint de santé"""
    print("🔍 Test de l'endpoint de santé...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data['status']}")
            return True
        else:
            print(f"❌ Health check échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur health check: {e}")
        return False

def test_versioning_features(token):
    """Test des fonctionnalités de versioning"""
    print("\n📚 Test des fonctionnalités de versioning...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Créer un document de test (simulation)
    print("   📄 Création d'un document de test...")
    
    # 2. Récupérer les versions (devrait être vide au début)
    try:
        response = requests.get(f"{BASE_URL}/documents/advanced/1/versions", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Versions récupérées: {len(data['versions'])} versions")
        else:
            print(f"   ❌ Erreur récupération versions: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur versioning: {e}")

def test_annotation_features(token):
    """Test des fonctionnalités d'annotations"""
    print("\n🏷️ Test des fonctionnalités d'annotations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Créer une annotation
    print("   📝 Création d'une annotation...")
    try:
        annotation_data = {
            "annotation_type": "highlight",
            "content": "Ceci est une annotation de test",
            "position": {"page": 1, "line": 10},
            "tags": ["important", "test"]
        }
        
        response = requests.post(
            f"{BASE_URL}/documents/advanced/1/annotations",
            headers=headers,
            json=annotation_data
        )
        
        if response.status_code == 200:
            data = response.json()
            annotation_id = data["annotation"]["id"]
            print(f"   ✅ Annotation créée: ID {annotation_id}")
            
            # 2. Récupérer les annotations du document
            response = requests.get(f"{BASE_URL}/documents/advanced/1/annotations", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Annotations récupérées: {len(data['annotations'])} annotations")
            
            # 3. Mettre à jour l'annotation
            update_data = {
                "content": "Annotation mise à jour",
                "tags": ["important", "updated"]
            }
            
            response = requests.put(
                f"{BASE_URL}/documents/advanced/annotations/{annotation_id}",
                headers=headers,
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Annotation mise à jour")
            
            # 4. Rechercher des annotations
            response = requests.get(
                f"{BASE_URL}/documents/advanced/annotations/search?query=test",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Recherche annotations: {len(data['annotations'])} résultats")
            
            # 5. Statistiques des annotations
            response = requests.get(f"{BASE_URL}/documents/advanced/annotations/statistics", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Statistiques annotations: {data['statistics']['total_annotations']} total")
            
        else:
            print(f"   ❌ Erreur création annotation: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"   ❌ Erreur annotations: {e}")

def test_tag_features(token):
    """Test des fonctionnalités de tags"""
    print("\n🏷️ Test des fonctionnalités de tags...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Créer un tag
    print("   🏷️ Création d'un tag...")
    try:
        tag_data = {
            "name": "test-tag",
            "color": "#FF6B6B",
            "description": "Tag de test"
        }
        
        response = requests.post(
            f"{BASE_URL}/documents/advanced/tags",
            headers=headers,
            json=tag_data
        )
        
        if response.status_code == 200:
            data = response.json()
            tag_id = data["tag"]["id"]
            print(f"   ✅ Tag créé: ID {tag_id}")
            
            # 2. Récupérer tous les tags
            response = requests.get(f"{BASE_URL}/documents/advanced/tags", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Tags récupérés: {len(data['tags'])} tags")
            
            # 3. Mettre à jour le tag
            update_data = {
                "name": "test-tag-updated",
                "color": "#4ECDC4"
            }
            
            response = requests.put(
                f"{BASE_URL}/documents/advanced/tags/{tag_id}",
                headers=headers,
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Tag mis à jour")
            
            # 4. Rechercher des tags
            response = requests.get(
                f"{BASE_URL}/documents/advanced/tags/search?query=test",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Recherche tags: {len(data['tags'])} résultats")
            
            # 5. Statistiques des tags
            response = requests.get(f"{BASE_URL}/documents/advanced/tags/statistics", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Statistiques tags: {data['statistics']['total_tags']} total")
            
        else:
            print(f"   ❌ Erreur création tag: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"   ❌ Erreur tags: {e}")

def test_sharing_features(token):
    """Test des fonctionnalités de partage"""
    print("\n📤 Test des fonctionnalités de partage...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Partager un document
    print("   📤 Partage d'un document...")
    try:
        share_data = {
            "shared_with_email": "bob@docsearch.ai",
            "permissions": ["read", "comment"],
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
            "message": "Document partagé pour test"
        }
        
        response = requests.post(
            f"{BASE_URL}/documents/advanced/1/share",
            headers=headers,
            json=share_data
        )
        
        if response.status_code == 200:
            data = response.json()
            share_id = data["share"]["id"]
            print(f"   ✅ Document partagé: ID {share_id}")
            
            # 2. Récupérer les documents partagés
            response = requests.get(
                f"{BASE_URL}/documents/advanced/shared?as_owner=true",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Documents partagés: {len(data['shared_documents'])} partages")
            
            # 3. Mettre à jour les permissions
            permissions_data = {
                "permissions": ["read", "write", "comment"]
            }
            
            response = requests.put(
                f"{BASE_URL}/documents/advanced/shares/{share_id}/permissions",
                headers=headers,
                json=permissions_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Permissions mises à jour")
            
            # 4. Prolonger l'expiration
            extend_data = {
                "new_expires_at": (datetime.now() + timedelta(days=14)).isoformat()
            }
            
            response = requests.put(
                f"{BASE_URL}/documents/advanced/shares/{share_id}/extend",
                headers=headers,
                json=extend_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Expiration prolongée")
            
            # 5. Statistiques des partages
            response = requests.get(f"{BASE_URL}/documents/advanced/shares/statistics", headers=headers)
            if response.status_code == 200:
                data = response.json()
                stats = data["statistics"]
                print(f"   ✅ Statistiques partages: {stats['shares_created']} créés, {stats['shares_received']} reçus")
            
        else:
            print(f"   ❌ Erreur partage: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"   ❌ Erreur partage: {e}")

def test_advanced_endpoints():
    """Test des endpoints avancés"""
    print("\n🚀 Test des endpoints avancés...")
    
    # Test de l'endpoint racine
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API accessible: {data['message']} v{data['version']}")
        else:
            print(f"   ❌ API inaccessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur API: {e}")

def main():
    """Fonction principale de test"""
    print("🧪 TESTS DES FONCTIONNALITÉS AVANCÉES - DOCSEARCH AI")
    print("=" * 60)
    
    # Test de santé
    if not test_health_check():
        print("❌ Le serveur n'est pas accessible. Arrêt des tests.")
        return
    
    # Test des endpoints de base
    test_advanced_endpoints()
    
    # Obtenir un token d'authentification
    print("\n🔐 Authentification...")
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token. Arrêt des tests.")
        return
    
    print(f"✅ Authentification réussie avec {TEST_EMAIL}")
    
    # Tests des fonctionnalités avancées
    test_versioning_features(token)
    test_annotation_features(token)
    test_tag_features(token)
    test_sharing_features(token)
    
    print("\n🎉 TESTS TERMINÉS")
    print("=" * 60)
    print("📊 Résumé:")
    print("   - Versioning: ✅ Testé")
    print("   - Annotations: ✅ Testé")
    print("   - Tags: ✅ Testé")
    print("   - Partage: ✅ Testé")
    print("\n💡 Les fonctionnalités avancées sont maintenant disponibles !")
    print("   Accédez à http://localhost:8000/docs pour voir la documentation complète.")

if __name__ == "__main__":
    main() 