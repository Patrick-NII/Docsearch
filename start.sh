#!/bin/bash

# 🧠 DocSearch AI - Script de démarrage
# Lance le backend et le frontend automatiquement

echo "🚀 Démarrage de DocSearch AI..."
echo "================================"

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier que Node.js est installé
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier que les dépendances sont installées
if [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
    echo "📦 Installation des dépendances Python..."
    pip install -r requirements.txt
fi

# Vérifier que le fichier .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env manquant !"
    echo "📝 Création d'un fichier .env de base..."
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Modèle GPT
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# Base vectorielle
VECTOR_DB_PATH=./vector_db
COLLECTION_NAME=docsearch_documents

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# API
API_TOKEN=dev-secret-token
API_HOST=0.0.0.0
API_PORT=8000
EOF
    echo "⚠️  IMPORTANT: Modifiez le fichier .env avec votre clé OpenAI !"
fi

# Vérifier que les dépendances frontend sont installées
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installation des dépendances frontend..."
    cd frontend
    npm install
    cd ..
fi

# Fonction pour arrêter proprement
cleanup() {
    echo ""
    echo "🛑 Arrêt des serveurs..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Démarrer le backend
echo "🔧 Démarrage du backend FastAPI..."
python api_server.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "⏳ Attente du démarrage du backend..."
sleep 5

# Vérifier que le backend fonctionne
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend démarré sur http://localhost:8000"
else
    echo "❌ Erreur: Le backend n'a pas démarré correctement"
    exit 1
fi

# Démarrer le frontend
echo "🌐 Démarrage du frontend Next.js..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Attendre que le frontend soit prêt
echo "⏳ Attente du démarrage du frontend..."
sleep 10

# Vérifier que le frontend fonctionne
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend démarré sur http://localhost:3000"
else
    echo "❌ Erreur: Le frontend n'a pas démarré correctement"
    exit 1
fi

echo ""
echo "🎉 DocSearch AI est prêt !"
echo "================================"
echo "🌐 Interface web: http://localhost:3000"
echo "🔧 API Backend: http://localhost:8000"
echo "📖 Documentation API: http://localhost:8000/docs"
echo ""
echo "💡 Utilisation:"
echo "   1. Ouvrez http://localhost:3000"
echo "   2. Upload un document"
echo "   3. Posez une question"
echo ""
echo "🛑 Appuyez sur Ctrl+C pour arrêter les serveurs"

# Attendre indéfiniment
wait 