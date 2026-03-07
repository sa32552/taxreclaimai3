
# Déploiement de TAXRECLAIMAI sur Vercel avec Supabase

## Vue d'Ensemble

Ce guide vous explique comment déployer TAXRECLAIMAI sur Vercel en utilisant Supabase comme base de données et GitHub pour le déploiement continu.

## Architecture de Déploiement

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GitHub    │────▶│   Vercel    │────▶│  Supabase   │
│   (Code)    │     │  (Hébergement)│  │  (Base de   │
│             │     │             │     │  données)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Étape 1: Préparation du Dépôt GitHub

### 1.1 Structure du Projet

Assurez-vous que votre projet a cette structure :

```
taxreclaimai/
├── backend/
│   ├── supabase_client.py          # Configuration Supabase
│   ├── supabase_auth.py            # Authentification Supabase
│   ├── supabase_storage.py          # Storage Supabase
│   ├── supabase_edge_functions.py   # Edge Functions Supabase
│   ├── supabase_schema.sql          # Schema SQL Supabase
│   ├── supabase_routes.py           # Routes API Supabase
│   ├── main_supabase.py             # API principale v3.0
│   └── requirements_supabase.txt     # Dépendances Python Supabase
├── frontend/                        # Frontend React
├── .env.example_supabase           # Variables d'environnement Supabase
├── vercel.json                     # Configuration Vercel
└── README.md                        # Documentation
```

### 1.2 Fichiers de Configuration

Créez le fichier `vercel.json` à la racine :

```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/main_supabase.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/backend/main_supabase.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

## Étape 2: Configuration de Supabase

### 2.1 Création du Projet Supabase

1. Allez sur https://supabase.com
2. Créez un nouveau projet
3. Notez l'URL et les clés API

### 2.2 Configuration de la Base de Données

1. Allez dans l'éditeur SQL Supabase
2. Copiez et collez le contenu de `backend/supabase_schema.sql`
3. Exécutez le script

### 2.3 Configuration du Storage

1. Allez dans Storage > Buckets
2. Créez les buckets nécessaires :
   - `invoices`
   - `forms`
   - `temp`

## Étape 3: Configuration de Vercel

### 3.1 Connexion à GitHub

1. Allez sur https://vercel.com
2. Connectez-vous avec votre compte GitHub
3. Importez votre dépôt GitHub

### 3.2 Configuration du Projet

1. Configurez les variables d'environnement :
   - Allez dans Settings > Environment Variables
   - Ajoutez les variables suivantes :
     ```
     SUPABASE_URL=https://nevyttqdnanrmxsjozjd.supabase.co
     SUPABASE_ANON_KEY=sb_publishable_XQugS3Pj77HcKIX-qelwZQ_k7vp7JhJ
     SUPABASE_SERVICE_ROLE_KEY=votre_clé_service
     SECRET_KEY=votre_secret_key
     JWT_SECRET_KEY=votre_jwt_secret
     ```

2. Configurez les domaines personnalisés si nécessaire

## Étape 4: Configuration du Frontend

### 4.1 Installation des Dépendances

```bash
cd frontend
npm install
```

### 4.2 Configuration Supabase

Créez un fichier `src/supabase.js` :

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://nevyttqdnanrmxsjozjd.supabase.co'
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'sb_publishable_XQugS3Pj77HcKIX-qelwZQ_k7vp7JhJ'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 4.3 Configuration de Build

Ajoutez un fichier `vercel.json` dans le dossier frontend :

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "env": {
    "REACT_APP_SUPABASE_URL": "@supabase_url",
    "REACT_APP_SUPABASE_ANON_KEY": "@supabase_anon_key"
  }
}
```

## Étape 5: Déploiement Automatique

### 5.1 Configuration du Workflow GitHub

Créez le fichier `.github/workflows/deploy.yml` :

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install Dependencies
      run: |
        cd backend
        pip install -r requirements_supabase.txt

    - name: Run Tests
      run: |
        cd backend
        python -m pytest

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        vercel-args: '--prod'
```

### 5.2 Configuration des Secrets GitHub

1. Allez dans votre dépôt GitHub > Settings > Secrets
2. Ajoutez les secrets suivants :
   - `VERCEL_TOKEN`: Votre token Vercel
   - `ORG_ID`: ID de votre organisation Vercel
   - `PROJECT_ID`: ID de votre projet Vercel

## Étape 6: Test du Déploiement

### 6.1 Déploiement Initial

1. Poussez votre code sur GitHub :
```bash
git add .
git commit -m "Initial Supabase configuration"
git push origin main
```

2. Vérifiez le déploiement sur Vercel

### 6.2 Tests

1. Testez l'API :
```bash
curl https://votre-app.vercel.app/api/health
```

2. Testez le frontend :
   - Allez sur https://votre-app.vercel.app
   - Testez l'enregistrement et la connexion

## Étape 7: Maintenance

### 7.1 Mises à Jour

Pour mettre à jour l'application :

1. Modifiez votre code
2. Poussez sur GitHub
3. Vercel déploiera automatiquement

### 7.2 Monitoring

1. Surveillez les performances sur Vercel
2. Vérifiez les logs Supabase
3. Configurez les alertes si nécessaire

## Problèmes Courants et Solutions

### Problème 1: Erreur de Connexion Supabase

**Solution**:
- Vérifiez les variables d'environnement
- Assurez-vous que la base de données est accessible

### Problème 2: Échec du Build

**Solution**:
- Vérifiez les dépendances dans requirements_supabase.txt
- Assurez-vous que Python 3.11 est bien configuré

### Problème 3: Erreur d'Authentification

**Solution**:
- Vérifiez les clés Supabase
- Assurez-vous que les politiques RLS sont correctes

## Ressources Utiles

- [Documentation Vercel](https://vercel.com/docs)
- [Documentation Supabase](https://supabase.com/docs)
- [GitHub Actions](https://github.com/features/actions)
