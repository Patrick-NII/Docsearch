#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur initial
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SessionLocal, User
from auth import AuthManager

def create_admin_user():
    """Crée un utilisateur administrateur initial"""
    
    print("🔐 Création d'un utilisateur administrateur")
    print("=" * 50)
    
    # Demander les informations
    email = input("Email: ").strip()
    username = input("Nom d'utilisateur: ").strip()
    password = input("Mot de passe (min 8 caractères): ").strip()
    full_name = input("Nom complet (optionnel): ").strip() or None
    
    # Validation
    if not email or not username or not password:
        print("❌ Tous les champs obligatoires doivent être remplis")
        return
    
    if len(password) < 8:
        print("❌ Le mot de passe doit contenir au moins 8 caractères")
        return
    
    if not email or '@' not in email:
        print("❌ Email invalide")
        return
    
    try:
        db = SessionLocal()
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = AuthManager.get_user_by_email(db, email)
        if existing_user:
            print(f"❌ Un utilisateur avec l'email {email} existe déjà")
            return
        
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            print(f"❌ Le nom d'utilisateur {username} est déjà pris")
            return
        
        # Créer l'utilisateur admin
        hashed_password = AuthManager.get_password_hash(password)
        admin_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_admin=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Utilisateur administrateur créé avec succès!")
        print(f"   Email: {admin_user.email}")
        print(f"   Username: {admin_user.username}")
        print(f"   Admin: {admin_user.is_admin}")
        print(f"   Actif: {admin_user.is_active}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 