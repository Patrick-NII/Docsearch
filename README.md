# DocSearch AI – Assistant IA de Lecture de Documents

Un assistant intelligent capable de répondre à des questions sur des documents PDF ou texte en utilisant l'intelligence artificielle générative et la recherche sémantique (RAG).

## 🎯 Objectif

Ce projet vise à construire un agent IA accessible via une API qui permet d'interroger le contenu d'un document en langage naturel, comme si l'IA avait réellement lu le fichier. Il répond avec pertinence et citations, et garde le contexte conversationnel.

## ✨ Fonctionnalités

### 🔐 Authentification & Multi-utilisateur
- **Système d'authentification JWT** sécurisé
- **Inscription et connexion** utilisateurs
- **Gestion des rôles** (utilisateur, administrateur)
- **Isolation des données** par utilisateur
- **Sessions utilisateur** avec expiration automatique
- **Gestion des profils** (modification, changement de mot de passe)

### 📄 Gestion des Documents
- Analyse de fichiers PDF, Word, Excel, CSV, images avec OCR
- **Upload de documents** via interface web
- **Sessions de documents** temporaires
- **Isolation par utilisateur** des documents et historiques
- **Documents partagés** entre utilisateurs
- **Recherche sémantique** (via ChromaDB et embeddings OpenAI)

### 💬 Chat & Conversation
- **Chat avec les documents** via API REST
- **Mémoire conversationnelle** persistante
- **Historique des conversations** par utilisateur
- **Citations des sources** dans les réponses
- **Interface web moderne** avec React/Next.js

### 🏗️ Architecture Technique
- **Backend FastAPI** avec authentification JWT
- **Base de données SQLite** avec SQLAlchemy
- **Frontend Next.js** avec interface moderne
- **Vector Store ChromaDB** pour la recherche sémantique
- **Déploiement Docker** prêt pour la production

## 🚀 Installation et Configuration

### Prérequis

- Python 3.8+
- Node.js 18+
- Docker (optionnel)

### Installation Locale

1. **Cloner le projet**
```bash
git clone https://github.com/Patrick-NII/DocSearch.git
cd DocSearch
```

2. **Configuration Backend**
```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
cp .env.example .env
# Éditer .env avec vos clés API OpenAI
```

3. **Configuration Frontend**
```bash
cd frontend
npm install
```

4. **Initialiser la Base de Données**
```bash
# Créer les tables
python models.py

# Créer un utilisateur administrateur
python create_admin.py
```

5. **Lancer l'Application**
```bash
# Terminal 1 - Backend
source venv/bin/activate
python api_server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

L'application sera disponible sur :
- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 🔐 Authentification

### Créer un Compte Administrateur

```bash
python create_admin.py
```

Suivez les instructions pour créer votre premier compte administrateur.

### Endpoints d'Authentification

- `POST /auth/register` - Inscription d'un nouvel utilisateur
- `POST /auth/login` - Connexion utilisateur
- `GET /auth/me` - Informations de l'utilisateur actuel
- `PUT /auth/me` - Mise à jour du profil
- `POST /auth/change-password` - Changement de mot de passe

### Utilisation avec l'API

```bash
# 1. Inscription
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user123",
    "password": "password123",
    "full_name": "John Doe"
  }'

# 2. Connexion
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# 3. Utiliser le token pour les requêtes authentifiées
curl -X POST "http://localhost:8000/ask" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"question": "Votre question ici"}'
```

## 📊 Fonctionnalités Avancées

### Gestion des Sessions
- Chaque upload de document crée une nouvelle session
- Les questions utilisent les documents de la session active
- Possibilité de basculer entre sessions
- Nettoyage automatique des sessions expirées

### Isolation des Données
- Chaque utilisateur voit uniquement ses propres documents
- Historique de conversation isolé par utilisateur
- Sessions de documents séparées par utilisateur
- Possibilité de partager des documents (fonctionnalité à venir)

### Interface d'Administration
- Gestion des utilisateurs (activation/désactivation)
- Attribution des droits administrateur
- Statistiques d'utilisation
- Monitoring des sessions

## 🏗️ Architecture

```
DocSearch/
├── api_server.py           # Serveur FastAPI principal
├── auth.py                 # Système d'authentification JWT
├── auth_routes.py          # Routes d'authentification
├── models.py               # Modèles SQLAlchemy
├── rag_chain.py            # Chaîne RAG avec mémoire
├── vector_store.py         # Gestion de la base vectorielle
├── document_loader.py      # Chargeur de documents multi-format
├── config.py               # Configuration de l'application
├── create_admin.py         # Script de création d'admin
├── frontend/               # Interface Next.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx    # Page principale
│   │   │   └── layout.tsx  # Layout de l'application
│   │   └── components/     # Composants React
│   └── package.json
├── vector_db/              # Base de données vectorielle
├── source/                 # Documents permanents
└── requirements.txt        # Dépendances Python
```

## 🔧 Configuration

### Variables d'Environnement (.env)

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# JWT
JWT_SECRET_KEY=your_jwt_secret_key_here

# Base de données
DATABASE_URL=sqlite:///./docsearch.db

# Serveur
HOST=0.0.0.0
PORT=8000
```

## 🚀 Déploiement

### Déploiement Local avec Docker

```bash
# Construire et lancer avec Docker Compose
docker-compose up --build -d
```

### Déploiement sur AWS EC2

1. **Créer une instance EC2**
2. **Installer Docker**
3. **Cloner le projet**
4. **Configurer les variables d'environnement**
5. **Lancer avec Docker Compose**

```bash
# Sur l'instance EC2
git clone https://github.com/Patrick-NII/DocSearch.git
cd DocSearch
# Configurer .env
docker-compose up --build -d
```

## 📈 Pistes d'Amélioration

### Fonctionnalités Prévues
- [ ] **Versioning des documents** avec historique des versions
- [ ] **Annotations et commentaires** sur les documents
- [ ] **Recherche avancée** avec filtres et tags
- [ ] **Export des conversations** en PDF/Word
- [ ] **Notifications en temps réel** avec WebSockets
- [ ] **Analytics et métriques** d'utilisation
- [ ] **Intégration avec des services cloud** (Google Drive, Dropbox)
- [ ] **API GraphQL** pour des requêtes plus flexibles

### Améliorations Techniques
- [ ] **Base de données PostgreSQL** pour la production
- [ ] **Cache Redis** pour les performances
- [ ] **Tests automatisés** (unitaires et d'intégration)
- [ ] **CI/CD pipeline** avec GitHub Actions
- [ ] **Monitoring et logging** avancés
- [ ] **Backup automatique** des données

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation API sur `/docs`
- Vérifier les logs du serveur pour le debugging

---

**DocSearch AI** - Transformez vos documents en connaissances intelligentes ! 🚀

