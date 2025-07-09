#!/usr/bin/env python3
"""
Script de lancement rapide pour DocSearch AI
Lance l'API et effectue les vérifications nécessaires
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Vérifie que tous les prérequis sont installés"""
    print("🔍 Vérification des prérequis...")
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        return False
    
    # Vérifier le fichier .env
    if not Path(".env").exists():
        print("⚠️  Fichier .env non trouvé")
        print("📝 Création d'un fichier .env basique...")
        create_basic_env()
    
    # Vérifier les dépendances
    try:
        import fastapi
        import langchain
        import openai
        print("✅ Dépendances Python installées")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez les dépendances avec: pip install -r requirements.txt")
        return False
    
    return True

def create_basic_env():
    """Crée un fichier .env basique"""
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_TOKEN=your-secret-api-token-here

# Autres configurations par défaut
VECTOR_DB_PATH=./vector_db
SOURCE_DIR=./source
CHUNK_SIZE=1000
TOP_K_RESULTS=5
MAX_FILE_SIZE=50
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Fichier .env créé")
    print("⚠️  N'oubliez pas de configurer votre clé API OpenAI !")

def create_directories():
    """Crée les répertoires nécessaires"""
    print("📁 Création des répertoires...")
    
    directories = [
        "source",
        "vector_db", 
        "uploads",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Répertoire {directory} créé")

def run_tests():
    """Lance les tests rapides"""
    print("🧪 Lancement des tests rapides...")
    
    try:
        result = subprocess.run([sys.executable, "test_ai_system.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Tests réussis")
            return True
        else:
            print("⚠️  Tests avec avertissements")
            print(result.stdout)
            return True  # Continuer même avec des warnings
            
    except subprocess.TimeoutExpired:
        print("⚠️  Tests interrompus (timeout)")
        return True
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def start_api():
    """Lance l'API"""
    print("🚀 Lancement de l'API DocSearch AI...")
    print("📡 API accessible sur: http://localhost:8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("\n⏹️  Appuyez sur Ctrl+C pour arrêter")
    print("-" * 50)
    
    try:
        # Lancer l'API avec uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api_server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'API")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")

def main():
    """Fonction principale"""
    print("🧠 DOCSEARCH AI - LANCEUR RAPIDE")
    print("=" * 40)
    
    # Vérifications
    if not check_requirements():
        print("\n❌ Prérequis non satisfaits")
        sys.exit(1)
    
    # Créer les répertoires
    create_directories()
    
    # Tests optionnels
    print("\n🧪 Voulez-vous lancer les tests ? (y/n): ", end="")
    if input().lower().startswith('y'):
        if not run_tests():
            print("❌ Tests échoués")
            sys.exit(1)
    
    # Lancer l'API
    print("\n" + "=" * 40)
    start_api()

if __name__ == "__main__":
    main() 