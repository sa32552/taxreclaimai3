
# Démonstration d'Installation Supabase

## Vue d'Ensemble

Voici comment installer TAXRECLAIMAI avec Supabase en utilisant notre script d'installation automatique.

## Étape 1: Préparation

1. **Ouvrez un terminal** dans le dossier du projet
2. **Vérifiez Python 3.8+**:
```bash
python --version
```

## Étape 2: Exécution du Script

1. **Lancez le script d'installation**:
```bash
python install_supabase.py
```

## Étape 3: Suivi des Instructions

Le script vous guidera à travers:

### 3.1 Configuration des Variables d'Environnement
```
📝 Configuration des variables d'environnement...

Veuillez entrer vos informations Supabase:
URL Supabase (ex: https://nevyttqdnanrmxsjozjd.supabase.co): https://nevyttqdnanrmxsjozjd.supabase.co
Clé Anon Supabase: sb_publishable_XQugS3Pj77HcKIX-qelwZQ_k7vp7JhJ
Clé Service Supabase: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3.2 Installation des Dépendances
```
📦 Installation des dépendances...
🔄 Installation des dépendances Python...
✅ Installation des dépendances Python réussie
```

### 3.3 Configuration de la Base de Données
```
💾 Configuration de la base de données...

⚠️  Veuillez suivre ces étapes dans le dashboard Supabase:
1. Allez dans le dashboard Supabase
2. Ouvrez l'éditeur SQL
3. Copiez et collez le contenu du fichier backend/supabase_schema.sql
4. Cliquez sur 'Run' pour exécuter le script

Appuyez sur Entrée une fois terminé...
```

### 3.4 Configuration du Storage
```
📁 Configuration du storage...

⚠️  Veuillez suivre ces étapes dans le dashboard Supabase:
1. Allez dans Storage > Buckets
2. Créez les buckets suivants:
   - invoices
   - forms
   - temp
3. Configurez les politiques RLS pour chaque bucket

Appuyez sur Entrée une fois terminé...
```

### 3.5 Configuration des Edge Functions
```
⚡ Configuration des Edge Functions...

⚠️  Veuillez suivre ces étapes dans le dashboard Supabase:
1. Allez dans Edge Functions
2. Créez les fonctions suivantes:
   - ocr_process
   - pdf_generate
   - vat_calculate
   - email_send
   - batch_process
3. Copiez le code depuis les fichiers correspondants

Appuyez sur Entrée une fois terminé...
```

### 3.6 Test de l'Installation
```
🧪 Test de l'installation...
✅ Connexion à Supabase réussie

🎉 Installation réussie !

Prochaines étapes:
1. Lancez l'application: uvicorn main_supabase:app --reload
2. Configurez le frontend avec les credentials Supabase
3. Déployez sur Railway ou autre plateforme
```

## Étape 4: Vérification Manuelle

### 4.1 Test de l'API

1. **Lancez l'application**:
```bash
cd backend
uvicorn main_supabase:app --reload
```

2. **Testez avec curl**:
```bash
# Test de santé
curl http://localhost:8000/health

# Test d'enregistrement
curl -X POST http://localhost:8000/api/auth/register   -H "Content-Type: application/json"   -d '{"email": "test@example.com", "password": "password123", "first_name": "Test", "last_name": "User"}'
```

### 4.2 Vérification dans le Dashboard Supabase

1. **Table Editor**: Vérifiez que les tables sont créées
2. **Authentication**: Testez l'enregistrement et la connexion
3. **Storage**: Vérifiez les buckets et les permissions
4. **Edge Functions**: Testez chaque fonction

## Étape 5: Configuration du Frontend

1. **Créez un fichier de configuration**:
```javascript
// src/supabase.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://nevyttqdnanrmxsjozjd.supabase.co'
const supabaseAnonKey = 'sb_publishable_XQugS3Pj77HcKIX-qelwZQ_k7vp7JhJ'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

2. **Installez les dépendances**:
```bash
cd frontend
npm install
```

3. **Lancez le frontend**:
```bash
npm run dev
```

## Étape 6: Déploiement

### 6.1 Sur Railway

1. **Connectez votre dépôt** à Railway
2. **Configurez les variables d'environnement**
3. **Déployez** en un clic

### 6.2 Sur Vercel

1. **Connectez votre dépôt** à Vercel
2. **Configurez les variables d'environnement**
3. **Déployez** automatiquement

## Résultat Final

Après avoir suivi ces étapes, vous aurez:

- ✅ Base de données Supabase configurée
- ✅ Authentification Supabase fonctionnelle
- ✅ Storage Supabase opérationnel
- ✅ Edge Functions Supabase déployées
- ✅ API TAXRECLAIMAI connectée à Supabase
- ✅ Frontend connecté à Supabase

Votre plateforme est maintenant **production-ready** ! 🚀
