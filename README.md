# 📚 DocSearch - Assistant IA de Lecture de Document

Un assistant intelligent capable de répondre à des questions sur des documents PDF ou texte en utilisant l'IA générative et la recherche sémantique.

## 🎯 Objectif

Ce projet permet de créer un assistant IA qui peut analyser des documents longs (rapports, articles, livres) et répondre à des questions spécifiques en citant les passages pertinents, comme si l'IA avait lu le document pour vous.

## ✨ Fonctionnalités

- 📄 **Support multi-format** : PDF et fichiers texte (.txt)
- 🔍 **Recherche sémantique** : Compréhension du contexte et du sens
- 💬 **Interface conversationnelle** : Posez plusieurs questions de suite
- 🧠 **Mémoire conversationnelle** : L'IA garde le contexte des échanges
- 📍 **Citations sourcées** : Réponses avec références aux pages/paragraphes
- 🚀 **100% local** : Fonctionne sans quota API externe (Ollama + SentenceTransformers)
- 🎨 **Interface web moderne** : Interface Streamlit intuitive

## 🏗️ Architecture

```
DocSearch/
├── document_loader.py    # Extraction texte PDF/TXT
├── text_splitter.py      # Découpage en chunks
├── vector_store.py       # Indexation vectorielle (ChromaDB)
├── rag_chain.py          # Chaîne RAG (Retrieval + Génération)
├── qa_interface.py       # Interface utilisateur Streamlit
├── config.py            # Configuration et variables d'environnement
├── run.py               # Point d'entrée de l'application
├── requirements.txt     # Dépendances Python
└── README.md           # Documentation
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- Ollama (pour le modèle local)

### 1. Cloner le projet
```bash
git clone https://github.com/Patrick-NII/Docsearch.git
cd Docsearch
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Installer Ollama
```bash
# macOS
curl -fsSL https://ollama.com/install.sh | sh

# Ou télécharger depuis https://ollama.com/download
```

### 4. Télécharger un modèle Ollama
```bash
ollama pull llama2
```

## 🎮 Utilisation

### 1. Lancer l'application
```bash
python run.py
```

### 2. Accéder à l'interface
Ouvrez votre navigateur sur : `http://localhost:8501`

### 3. Poser des questions
- Placez vos documents PDF ou TXT dans le dossier `source/`
- Posez vos questions en langage naturel
- L'IA répondra en citant les passages pertinents

## 🔧 Configuration

### Variables d'environnement (.env)
```env
OPENAI_API_KEY=your_openai_key_here  # Optionnel (pour OpenAI)
```

### Modèles disponibles
- **Ollama** : `llama2`, `mistral`, `codellama` (recommandé)
- **HuggingFace** : Modèles locaux (optionnel)

## 🧠 Concepts techniques

### RAG (Retrieval-Augmented Generation)
1. **Extraction** : Le document est découpé en chunks
2. **Indexation** : Chaque chunk est transformé en vecteur sémantique
3. **Recherche** : Pour une question, on trouve les chunks les plus pertinents
4. **Génération** : Le LLM génère une réponse basée sur ces chunks

### Embeddings
- **Modèle** : `all-MiniLM-L6-v2` (SentenceTransformers)
- **Dimension** : 384
- **Base vectorielle** : ChromaDB (locale)

## 📊 Exemple d'utilisation

```
Question : "De quoi parle ce document ?"

Réponse : Ce document est intitulé "ACQUISITION.COM VOLUME I: 100M OFFERS" 
par Alex Hormozi. Il traite de la création d'offres commerciales si 
attractives que les clients ont l'impression d'être stupides de dire non.

Sources :
- Page 3 : Titre principal du document
- Page 5 : Informations sur l'auteur et le copyright
```

## 🎯 Critères de validation

✅ **Réponses cohérentes** : L'IA répond de façon pertinente à plusieurs questions  
✅ **Citations sourcées** : Indication des pages/paragraphes concernés  
✅ **Code propre** : Architecture modulaire et bien structurée  
✅ **Mémoire conversationnelle** : Conservation du contexte entre questions  
✅ **Interface utilisateur** : Interface web intuitive avec Streamlit  

## 🚀 Pistes d'amélioration

- [ ] Support de plusieurs documents simultanés
- [ ] Recherche plein texte (keyword matching)
- [ ] API REST avec FastAPI
- [ ] Interface de chat en temps réel
- [ ] Export des conversations
- [ ] Support de formats supplémentaires (DOCX, EPUB)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Ajouter de nouvelles fonctionnalités

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**Développé avec ❤️ pour simplifier la lecture de documents complexes** 