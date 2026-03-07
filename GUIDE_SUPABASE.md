
# Guide d'Installation et Configuration Supabase

## Étape 1: Création et Configuration du Projet Supabase

### 1.1 Créer un compte Supabase
1. Allez sur https://supabase.com
2. Cliquez sur "Start your project"
3. Connectez-vous avec votre compte GitHub, Google ou créez un compte
4. Cliquez sur "New Project"

### 1.2 Configuration du projet
1. Nommez votre projet: `taxreclaimai`
2. Choisissez une région proche de vos utilisateurs (ex: Europe)
3. Créez un mot de passe fort pour la base de données
4. Cliquez sur "Create new project"

### 1.3 Récupérer les informations de connexion
1. Une fois le projet créé, allez dans "Settings" > "Database"
2. Notez les informations suivantes:
   - Connection string
   - API URL (dans "Settings" > "API")
   - Anon key
   - Service role key

## Étape 2: Configuration de la Base de Données

### 2.1 Exécuter le schema SQL
1. Allez dans "Table Editor" dans votre dashboard Supabase
2. Cliquez sur "SQL" dans le menu
3. Copiez et collez le contenu du fichier `supabase_schema.sql`
4. Cliquez sur "Run" pour exécuter le script

### 2.2 Activer l'extension UUID
1. Allez dans "Database" > "Extensions"
2. Cherchez "uuid-ossp"
3. Activez l'extension
4. Répétez pour "pgcrypto"

## Étape 3: Configuration de l'Authentification

### 3.1 Configurer les providers
1. Allez dans "Authentication" > "Settings"
2. Activez les providers souhaités (Google, GitHub, etc.)
3. Configurez les clés API si nécessaire

### 3.2 Configurer les templates d'email
1. Allez dans "Authentication" > "Email Templates"
2. Personnalisez les templates de confirmation et réinitialisation
3. Testez avec votre adresse email

## Étape 4: Configuration du Storage

### 4.1 Créer les buckets
1. Allez dans "Storage" > "Buckets"
2. Créez les buckets suivants:
   - `invoices` (pour les factures)
   - `forms` (pour les formulaires)
   - `temp` (pour les fichiers temporaires)

### 4.2 Configurer les permissions
1. Pour chaque bucket, allez dans "Settings"
2. Configurez les politiques RLS (Row Level Security)
3. Exemple pour le bucket `invoices`:
```sql
-- Permettre aux utilisateurs authentifiés de lire leurs propres fichiers
CREATE POLICY "Users can view own invoices" ON storage.objects
FOR SELECT USING (bucket_id = 'invoices' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Permettre aux utilisateurs authentifiés d'uploader leurs propres fichiers
CREATE POLICY "Users can upload invoices" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'invoices' AND auth.uid()::text = (storage.foldername(name))[1]);
```

## Étape 5: Configuration des Edge Functions

### 5.1 Créer les Edge Functions
1. Allez dans "Edge Functions" dans votre dashboard
2. Cliquez sur "New Function"
3. Créez les fonctions suivantes:
   - `ocr_process` (traitement OCR)
   - `pdf_generate` (génération PDF)
   - `vat_calculate` (calcul TVA)
   - `email_send` (envoi emails)
   - `batch_process` (traitement par lots)

### 5.2 Code des Edge Functions
1. Pour chaque fonction, copiez le code correspondant depuis le dossier `supabase_edge_functions`
2. Collez le code dans l'éditeur Supabase
3. Cliquez sur "Deploy"

## Étape 6: Configuration de l'Application

### 6.1 Variables d'environnement
1. Copiez `.env.example_supabase` vers `.env`
2. Remplacez les valeurs par vos credentials Supabase:
```bash
# Configuration Supabase
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_ANON_KEY=votre-clé-anon
SUPABASE_SERVICE_ROLE_KEY=votre-clé-service

# Clés secrètes
SECRET_KEY=votre-secret-key-ici
JWT_SECRET_KEY=votre-jwt-secret-ici
```

### 6.2 Installation des dépendances
1. Installez les dépendances Python:
```bash
pip install -r requirements_supabase.txt
```

### 6.3 Initialisation de la base de données
1. Exécutez ce script pour initialiser la base de données:
```python
from backend.supabase_client import get_supabase_client
from backend.supabase_schema import create_tables

supabase = get_supabase_client()
create_tables(supabase)
```

## Étape 7: Tests et Déploiement

### 7.1 Tests locaux
1. Lancez l'application en mode développement:
```bash
cd backend
uvicorn main_supabase:app --reload
```

2. Testez les endpoints avec Postman ou curl:
```bash
# Test de santé
curl http://localhost:8000/health

# Test d'enregistrement
curl -X POST http://localhost:8000/api/auth/register   -H "Content-Type: application/json"   -d '{"email": "test@example.com", "password": "password123", "first_name": "Test", "last_name": "User"}'
```

### 7.2 Déploiement sur Railway
1. Connectez votre dépôt GitHub à Railway
2. Configurez les variables d'environnement dans Railway
3. Déployez en un clic

## Étape 8: Configuration du Frontend

### 8.1 Installation des dépendances
```bash
cd frontend
npm install
```

### 8.2 Configuration Supabase
1. Créez un fichier `src/supabase.js`:
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://votre-projet.supabase.co'
const supabaseAnonKey = 'votre-clé-anon'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 8.3 Lancement du frontend
```bash
npm run dev
```

## Étape 9: Vérifications Finales

### 9.1 Vérifier l'authentification
1. Testez l'enregistrement et la connexion
2. Vérifiez le 2FA
3. Testez la réinitialisation de mot de passe

### 9.2 Vérifier le storage
1. Testez l'upload de fichiers
2. Vérifiez les permissions RLS
3. Testez le téléchargement

### 9.3 Vérifier les Edge Functions
1. Testez le traitement OCR
2. Vérifiez la génération de PDF
3. Testez l'envoi d'emails

## Dépannage

### Problèmes courants

#### Erreur de connexion à la base de données
- Vérifiez l'URL de connexion
- Vérifiez que la base de données est en ligne
- Testez avec pgAdmin

#### Erreur d'authentification
- Vérifiez les clés API
- Vérifiez les templates d'email
- Testez avec différents providers

#### Erreur de storage
- Vérifiez les politiques RLS
- Vérifiez les permissions des buckets
- Testez avec différents fichiers

#### Erreur d'Edge Functions
- Vérifiez les logs dans le dashboard
- Testez les fonctions individuellement
- Vérifiez les variables d'environnement

## Ressources Utiles

- [Documentation Supabase](https://supabase.com/docs)
- [Dashboard Supabase](https://app.supabase.com)
- [Guide de démarrage rapide](https://supabase.com/docs/guides/getting-started)
