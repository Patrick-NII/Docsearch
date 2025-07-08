# DocSearch – Assistant IA de Lecture de Documents

Un assistant intelligent capable de répondre à des questions sur des documents PDF ou texte en utilisant l’intelligence artificielle générative et la recherche sémantique (RAG).

## Objectif

Ce projet vise à construire un agent IA accessible via une API qui permet d’interroger le contenu d’un document en langage naturel, comme si l’IA avait réellement lu le fichier. Il répond avec pertinence et citations, et garde le contexte conversationnel.

## Fonctionnalités

- Analyse de fichiers PDF
- Envoi de documents via une interface Swagger (FastAPI)
- Chat avec le document via une API POST `/chat`
- Mémoire conversationnelle pour le contexte
- Recherche sémantique (via FAISS et embeddings OpenAI)
- Hébergement cloud avec Docker + EC2
- Architecture extensible (prévue pour intégrer une interface web ou mobile)

## Architecture technique

```
ai_doc_chatbot_api/
├── main.py                 # API FastAPI
├── Dockerfile              # Image Docker de l'app
├── docker-compose.yml      # Orchestration du conteneur
├── requirements.txt        # Dépendances
├── .env                    # Variables d'environnement (clé API OpenAI)
└── static/                 # Fichiers HTML statiques (upload simple)
```

## Déploiement sur AWS EC2 avec Docker

### Étapes réalisées

1. Création d'une instance EC2 sous Ubuntu avec ports ouverts pour SSH (22) et HTTP (8000)
2. Installation de Docker & docker-compose
3. Transfert du projet via SCP depuis le Mac local (avec clé PEM)
4. Création d’une image Docker avec :
   ```bash
   docker-compose up --build -d
   ```
5. Mise à jour des permissions et debug réseau (groupes de sécurité)
6. Test de l’API sur `http://<ec2>:8000/docs`

## Problèmes rencontrés et résolution

| Problème                        | Solution                                                             |
|--------------------------------|----------------------------------------------------------------------|
| `pypdf not found`              | Ajout de `pypdf` dans `requirements.txt`                            |
| `tiktoken not found`           | Nécessaire pour `OpenAIEmbeddings` – Ajouté à `requirements.txt`    |
| `Invalid OpenAI API key`       | Mauvais chargement de `.env`, corrigé via `os.environ` dans `main`  |
| Swagger UI inaccessible        | Port 8000 non exposé dans les règles de sécurité AWS – corrigé      |
| Clé PEM inaccessible ou perdue | Génération d'une nouvelle paire, mise à jour dans EC2               |
| Ancienne version de l’app      | Suppression manuelle de l’ancien dossier avant re-déploiement       |
| Fichier ZIP mal structuré      | Correction du chemin `ai_doc_chatbot_api 2/`                         |

## Installation locale (optionnel)

### Prérequis

- Python 3.8+
- virtualenv ou conda

```bash
git clone https://github.com/Patrick-NII/DocSearch.git
cd ai_doc_chatbot_api
pip install -r requirements.txt
python main.py
```

API disponible sur `http://localhost:8000/docs`

## Utilisation via Swagger UI

1. Accéder à `/docs`  
2. Envoyer un PDF via l’endpoint `POST /upload/`  
3. Poser une question via `POST /chat/`

## Exemple

```bash
POST /upload/ → dojo_week11.pdf
POST /chat/  → "Quels sont les objectifs de la semaine 11 ?"
```

Réponse :

```json
{
  "answer": "Les objectifs de la semaine 11 sont...",
  "source_documents": [
    "dojo_week11.pdf - page 2"
  ]
}
```

## Conclusion et perspectives

Ce projet constitue une base solide pour un assistant documentaire IA :

- API fonctionnelle
- Déploiement cloud automatisé
- Support des erreurs courantes
- Code prêt à intégrer une interface frontend (Web ou mobile)

### Pistes d’amélioration

- Gestion multi-documents
- Vector store persistante
- Authentification API
- Interface de chat en temps réel
- Export des conversations

