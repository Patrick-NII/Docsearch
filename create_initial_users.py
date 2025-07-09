#!/usr/bin/env python3
"""
Script pour créer les utilisateurs initiaux de DocSearch AI
"""

import sys
import os
import secrets
import string
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SessionLocal, User
from auth import AuthManager

def generate_secure_password(length=12):
    """Génère un mot de passe sécurisé"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def create_initial_users():
    """Crée les utilisateurs initiaux"""
    
    print("👥 Création des utilisateurs initiaux de DocSearch AI")
    print("=" * 60)
    
    # Liste des utilisateurs à créer
    users_data = [
        {
            "email": "patrick@docsearch.ai",
            "username": "patrick_admin",
            "full_name": "Patrick NII",
            "is_admin": True,
            "description": "Administrateur principal"
        },
        {
            "email": "alice@docsearch.ai",
            "username": "alice_dev",
            "full_name": "Alice Martin",
            "is_admin": False,
            "description": "Développeuse"
        },
        {
            "email": "bob@docsearch.ai",
            "username": "bob_analyst",
            "full_name": "Bob Johnson",
            "is_admin": False,
            "description": "Analyste de données"
        },
        {
            "email": "carol@docsearch.ai",
            "username": "carol_researcher",
            "full_name": "Carol Smith",
            "is_admin": False,
            "description": "Chercheuse"
        },
        {
            "email": "david@docsearch.ai",
            "username": "david_manager",
            "full_name": "David Wilson",
            "is_admin": False,
            "description": "Manager de projet"
        }
    ]
    
    created_users = []
    
    try:
        db = SessionLocal()
        
        for user_data in users_data:
            # Générer un mot de passe sécurisé
            password = generate_secure_password()
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = AuthManager.get_user_by_email(db, user_data["email"])
            if existing_user:
                print(f"⚠️  Utilisateur {user_data['email']} existe déjà, ignoré")
                continue
            
            existing_username = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_username:
                print(f"⚠️  Username {user_data['username']} existe déjà, ignoré")
                continue
            
            # Créer l'utilisateur
            hashed_password = AuthManager.get_password_hash(password)
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=hashed_password,
                full_name=user_data["full_name"],
                is_admin=user_data["is_admin"],
                is_active=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            created_users.append({
                "user": user,
                "password": password,
                "description": user_data["description"]
            })
            
            print(f"✅ {user_data['description']} créé:")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Mot de passe: {password}")
            print(f"   Admin: {user.is_admin}")
            print()
        
        # Afficher le résumé
        print("📋 RÉSUMÉ DES UTILISATEURS CRÉÉS")
        print("=" * 60)
        print(f"Total créé: {len(created_users)} utilisateurs")
        print()
        
        for i, user_info in enumerate(created_users, 1):
            user = user_info["user"]
            print(f"{i}. {user_info['description']}")
            print(f"   👤 {user.full_name}")
            print(f"   📧 {user.email}")
            print(f"   🔑 {user.username}")
            print(f"   🔒 Mot de passe: {user_info['password']}")
            print(f"   👑 Admin: {'Oui' if user.is_admin else 'Non'}")
            print()
        
        print("💡 CONSEILS D'UTILISATION")
        print("=" * 60)
        print("1. Connectez-vous avec l'email et le mot de passe généré")
        print("2. Changez votre mot de passe après la première connexion")
        print("3. Le compte Patrick a les droits administrateur")
        print("4. Les autres comptes sont des utilisateurs standard")
        print()
        print("🔗 URLs d'accès:")
        print("- Frontend: http://localhost:3000")
        print("- API Docs: http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des utilisateurs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_users() 