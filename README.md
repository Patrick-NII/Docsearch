# DocSearch AI - Assistant IA pour Documents

Une plateforme moderne et sophistiquée d'analyse et de recherche dans vos documents avec intelligence artificielle, dotée d'une interface utilisateur futuriste et de fonctionnalités avancées.

## 🎨 **Design System Moderne & Futuriste**

### **Palette de Couleurs Sophistiquée**
- **Primaire** : Dégradés bleu-violet (#667eea → #764ba2)
- **Secondaire** : Accents cyan (#00d4ff)
- **Neutre** : Gris sophistiqué (#1a1a2e, #16213e)
- **Background** : Dégradés sombres avec effets de particules

### **Typographie Moderne**
- **Police principale** : Inter (Google Fonts)
- **Titres** : Poppins (futuriste)
- **Code** : JetBrains Mono

### **Effets Visuels Avancés**
- **Glassmorphism** : Effets de verre avec backdrop blur
- **Animations fluides** : Transitions CSS3, keyframes personnalisées
- **Ombres dynamiques** : Effets de profondeur et de profondeur
- **Bordures animées** : Focus states avec gradients

## 🚀 **Fonctionnalités UX/UI Avancées**

### **1. Gestion des Documents Révolutionnaire**
- **Grid/List view** toggle avec animations
- **Document cards** cliquables avec preview intégrée
- **Visualiseur de documents** modal (PDF, images, texte)
- **Drag & drop** pour réorganiser
- **Filtres visuels** (type, date, taille)
- **Sélection multiple** avec indicateurs visuels

### **2. Chat Conversationnel Moderne**
- **Bubbles de conversation** avec avatars personnalisés
- **Horodatage** élégant et relatif
- **Ordre chronologique** correct (nouvelles en bas)
- **Typing indicators** animés
- **Message status** (envoyé, lu, etc.)
- **Réponses avec sources** visuelles et pliables

### **3. Composants UI Sophistiqués**
- **Boutons** : Glassmorphism avec hover effects, variants multiples
- **Inputs** : Bordures animées, focus states, validation visuelle
- **Cards** : Effets de profondeur, ombres dynamiques
- **Modals** : Backdrop blur, animations fluides

### **4. Dashboard Analytics Visuel**
- **Graphiques interactifs** (Chart.js)
- **Métriques animées** avec compteurs
- **Filtres temporels** élégants
- **KPI cards** avec animations et transitions

## 🛠 **Architecture Technique**

### **Frontend (Next.js 15)**
- **Framework** : Next.js avec App Router
- **Styling** : Tailwind CSS + CSS Variables
- **État** : React Context + Hooks
- **HTTP** : Axios avec intercepteurs
- **Animations** : CSS3 + Framer Motion

### **Backend (FastAPI)**
- **Framework** : FastAPI avec async/await
- **Base de données** : SQLite avec SQLAlchemy
- **Authentification** : JWT avec refresh tokens
- **IA/LLM** : LangChain + OpenAI GPT
- **Vector Store** : ChromaDB avec embeddings

### **IA & RAG**
- **Modèle** : GPT-3.5-turbo / GPT-4
- **Embeddings** : OpenAI text-embedding-ada-002
- **RAG Chain** : ConversationalRetrievalChain
- **Mémoire** : ConversationBufferMemory
- **Sessions** : Isolation par utilisateur

## 📦 **Installation & Démarrage**

### **Prérequis**
```bash
# Python 3.11+
# Node.js 18+
# OpenAI API Key
```

### **Backend**
```bash
# Cloner le projet
git clone <repository>
cd Docsearch

# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Dépendances
pip install -r requirements.txt

# Variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# Base de données
python -c "from models import create_tables; create_tables()"

# Utilisateurs initiaux
python create_users.py

# Démarrer le serveur
python api_server.py
```

### **Frontend**
```bash
cd frontend

# Dépendances
npm install

# Variables d'environnement
cp .env.local.example .env.local
# Éditer .env.local avec l'URL de l'API

# Démarrer le serveur de développement
npm run dev
```

## 🔐 **Authentification**

### **Comptes de Démonstration**
- **Admin** : `patrick@docsearch.ai` / `MB2JyQhY8Kmd`
- **Utilisateur** : `alice@docsearch.ai` / `g$5rs@^iCP*M`

### **Fonctionnalités d'Auth**
- JWT avec refresh automatique
- Sessions persistantes
- Gestion des rôles (admin/utilisateur)
- Protection des routes

## 📊 **Fonctionnalités Avancées**

### **Gestion des Documents**
- **Multi-format** : PDF, DOCX, TXT, images (avec OCR)
- **Versioning** : Historique des versions
- **Annotations** : Tags et commentaires
- **Partage** : Permissions et expiration
- **Collections** : Organisation thématique

### **Analytics & Insights**
- **Statistiques utilisateur** : Documents, questions, sessions
- **Analytics globaux** : Métriques système (admin)
- **Activité temporelle** : Tendances sur 7/14/30 jours
- **Recommandations** : Suggestions personnalisées

### **Conversation IA**
- **Mémoire contextuelle** : Historique des conversations
- **Sources citées** : Références aux documents
- **Contexte intelligent** : Sélection automatique des documents
- **Sessions isolées** : Séparation par upload

## 🎯 **Roadmap & Améliorations**

### **Phase 1 - Core Features** ✅
- [x] Authentification JWT
- [x] Upload multi-format
- [x] Chat RAG basique
- [x] Interface moderne

### **Phase 2 - Advanced UX** ✅
- [x] Design system futuriste
- [x] Composants UI sophistiqués
- [x] Gestion documents interactive
- [x] Chat conversationnel avancé

### **Phase 3 - Analytics & Insights** 🚧
- [ ] Graphiques interactifs
- [ ] Métriques avancées
- [ ] Export de données
- [ ] Rapports automatisés

### **Phase 4 - Collaboration** 📋
- [ ] Partage de documents
- [ ] Commentaires collaboratifs
- [ ] Notifications temps réel
- [ ] API publique

## 🤝 **Contribution**

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 **Licence**

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 **Support**

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation technique
- Contacter l'équipe de développement

---

**DocSearch AI** - Transformez vos documents en intelligence conversationnelle 🚀

