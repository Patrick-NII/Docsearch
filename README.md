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

### Utilisateurs Pré-créés

Le système inclut 5 utilisateurs pré-configurés :

| Utilisateur | Email | Username | Mot de passe | Rôle |
|-------------|-------|----------|--------------|------|
| **Patrick NII** | patrick@docsearch.ai | patrick_admin | `MB2JyQhY8Kmd` | **Administrateur** |
| Alice Martin | alice@docsearch.ai | alice_dev | `g$5rs@^iCP*M` | 👤 Utilisateur |
| Bob Johnson | bob@docsearch.ai | bob_analyst | `gB6vG$1smJVV` | 👤 Utilisateur |
| Carol Smith | carol@docsearch.ai | carol_researcher | `rQGcpWwg*6QD` | 👤 Utilisateur |
| David Wilson | david@docsearch.ai | david_manager | `wJu%xMZ%hZmf` | 👤 Utilisateur |

### Créer de Nouveaux Utilisateurs

```bash
# Créer un utilisateur administrateur
python create_admin.py

# Créer plusieurs utilisateurs
python create_initial_users.py
```

### Endpoints d'Authentification

- `POST /auth/register` - Inscription d'un nouvel utilisateur
- `POST /auth/login` - Connexion utilisateur
- `GET /auth/me` - Informations de l'utilisateur actuel
- `PUT /auth/me` - Mise à jour du profil
- `POST /auth/change-password` - Changement de mot de passe

### Endpoints Administrateur

- `GET /auth/users` - Liste de tous les utilisateurs
- `PUT /auth/users/{user_id}/toggle-status` - Activer/désactiver un utilisateur
- `PUT /auth/users/{user_id}/toggle-admin` - Donner/retirer les droits admin

### Endpoints de Gestion Avancée des Documents

#### Versioning
- `GET /documents/advanced/{document_id}/versions` - Liste des versions d'un document
- `GET /documents/advanced/versions/{version_id}` - Récupérer une version spécifique
- `POST /documents/advanced/versions/compare` - Comparer deux versions
- `POST /documents/advanced/versions/{version_id}/restore` - Restaurer une version
- `DELETE /documents/advanced/versions/{version_id}` - Supprimer une version
- `GET /documents/advanced/{document_id}/versions/statistics` - Statistiques des versions

#### Annotations
- `POST /documents/advanced/{document_id}/annotations` - Créer une annotation
- `GET /documents/advanced/{document_id}/annotations` - Liste des annotations
- `GET /documents/advanced/annotations/{annotation_id}` - Récupérer une annotation
- `PUT /documents/advanced/annotations/{annotation_id}` - Mettre à jour une annotation
- `DELETE /documents/advanced/annotations/{annotation_id}` - Supprimer une annotation
- `GET /documents/advanced/annotations/search` - Rechercher dans les annotations
- `GET /documents/advanced/annotations/statistics` - Statistiques des annotations

#### Tags
- `POST /documents/advanced/tags` - Créer un tag
- `GET /documents/advanced/tags` - Liste de tous les tags
- `GET /documents/advanced/tags/{tag_id}` - Récupérer un tag
- `PUT /documents/advanced/tags/{tag_id}` - Mettre à jour un tag
- `DELETE /documents/advanced/tags/{tag_id}` - Supprimer un tag
- `GET /documents/advanced/tags/search` - Rechercher des tags
- `GET /documents/advanced/tags/statistics` - Statistiques des tags

#### Partage
- `POST /documents/advanced/{document_id}/share` - Partager un document
- `GET /documents/advanced/shared` - Documents partagés
- `GET /documents/advanced/shares/{share_id}` - Détails d'un partage
- `PUT /documents/advanced/shares/{share_id}/permissions` - Mettre à jour les permissions
- `PUT /documents/advanced/shares/{share_id}/extend` - Prolonger l'expiration
- `DELETE /documents/advanced/shares/{share_id}` - Révoquer un partage
- `GET /documents/advanced/shares/statistics` - Statistiques des partages

### Utilisation avec l'API

```bash
# 1. Connexion avec un utilisateur existant
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patrick@docsearch.ai",
    "password": "MB2JyQhY8Kmd"
  }'

# 2. Utiliser le token pour les requêtes authentifiées
curl -X POST "http://localhost:8000/ask" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"question": "Votre question ici"}'

# 3. Upload de documents (authentifié)
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "files=@document.pdf"

# 4. Obtenir les statistiques utilisateur
curl -X GET "http://localhost:8000/stats" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test de l'Intégration

```bash
# Tester l'intégration complète
python test_auth_integration.py
```

## 📊 Fonctionnalités Avancées

### ✅ **ÉTAPE 1 : Authentification JWT et Support Multi-utilisateurs**

- **🔐 Authentification JWT complète**
  - Inscription et connexion sécurisées
  - Tokens JWT avec expiration automatique
  - Hachage des mots de passe avec bcrypt
  - Gestion des sessions utilisateur

- **👥 Support multi-utilisateurs**
  - Modèles SQLAlchemy pour utilisateurs, sessions, documents et chat
  - Isolation des données par utilisateur
  - Rôles utilisateur et administrateur
  - Gestion des profils utilisateur

- **🛡️ Sécurité renforcée**
  - Protection de tous les endpoints avec JWT
  - Endpoints administrateur séparés
  - Validation des données d'entrée
  - Gestion des erreurs d'authentification

### ✅ **ÉTAPE 2 : Intégration Backend-Authentification**

- **🔗 Intégration complète**
  - Tous les endpoints protégés par JWT
  - Isolation des données par utilisateur
  - Gestion automatique des tokens
  - Tests d'intégration automatisés

### ✅ **ÉTAPE 3 : Frontend avec Authentification**

- **🎨 Interface utilisateur moderne**
  - Composants React avec TypeScript
  - Design responsive avec Tailwind CSS
  - Formulaires de connexion et inscription
  - Gestion d'état avec Context API

- **🔐 Authentification frontend**
  - Contexte d'authentification global
  - Gestion automatique des tokens JWT
  - Protection des routes
  - Profil utilisateur avec déconnexion

- **📱 Expérience utilisateur**
  - Interface intuitive et moderne
  - Gestion des états de chargement
  - Messages d'erreur clairs
  - Navigation fluide entre connexion/inscription

### ✅ **ÉTAPE 4 : Analytics et Métriques d'Utilisation**

- **📊 Système d'analytics complet**
  - Statistiques utilisateur et globales
  - Métriques de performance en temps réel
  - Tracking d'activité utilisateur
  - Insights personnalisés et recommandations

- **📈 Tableau de bord interactif**
  - Interface moderne avec graphiques
  - Filtres par période (7, 14, 30 jours)
  - Statistiques détaillées par utilisateur
  - Vue administrateur avec métriques globales

- **🔍 Métriques avancées**
  - Types de documents les plus utilisés
  - Activité par heure de la journée
  - Documents les plus consultés
  - Taux de succès des questions IA

- **💡 Intelligence utilisateur**
  - Recommandations personnalisées
  - Questions les plus fréquentes
  - Sessions les plus actives
  - Tendances d'utilisation

### ✅ **ÉTAPE 5 : Gestion Avancée des Documents**

- **📚 Versioning des Documents**
  - Historique complet des versions de documents
  - Comparaison entre versions avec analyse des différences
  - Restauration de versions précédentes
  - Statistiques de versioning par document
  - Détection automatique des changements par hash

- **🏷️ Annotations et Tags**
  - Système d'annotations complet (highlight, comment, note)
  - Tags personnalisables avec couleurs
  - Recherche avancée dans les annotations
  - Statistiques d'utilisation des annotations
  - Positionnement précis dans les documents

- **📤 Partage de Documents**
  - Partage sécurisé entre utilisateurs
  - Permissions granulaires (read, write, comment, share)
  - Expiration automatique des partages
  - Gestion des partages actifs et expirés
  - Statistiques de partage par utilisateur

- **🔍 Fonctionnalités Avancées**
  - API REST complète pour toutes les fonctionnalités
  - Gestion des permissions et sécurité
  - Statistiques détaillées et métriques
  - Nettoyage automatique des données expirées

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
- [x] **Analytics et métriques** d'utilisation ✅
- [ ] **Versioning des documents** avec historique des versions
- [ ] **Annotations et commentaires** sur les documents
- [ ] **Recherche avancée** avec filtres et tags
- [ ] **Export des conversations** en PDF/Word
- [ ] **Notifications en temps réel** avec WebSockets
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

## [CORRECTIFS JUILLET 2024]

- Correction d'un bug sur l'API `/history` : le champ `session_id` est toujours une string ("Permanent" si None), ce qui évite les erreurs 500 côté frontend.
- Suppression du warning LangChain en utilisant `.chain.invoke({...})` au lieu de `.chain({...})` dans `rag_chain.py`.
- Création du dossier `frontend/src/app` pour la compatibilité Next.js 13+ (App Router).
- Création du dossier `frontend/public/katiopa/images` pour éviter les erreurs 404 sur les images statiques. Ajouter les images nécessaires dans ce dossier.

**Pensez à redémarrer le backend et le frontend après ces corrections.**

