
#!/usr/bin/env python3
"""
Script d'installation automatique pour TAXRECLAIMAI avec Supabase
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description):
    """
    Exécute une commande et affiche le résultat

    Args:
        command: Commande à exécuter
        description: Description de l'opération
    """
    print(f"
🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} réussie")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}: {e.stderr}")
        return None

def create_env_file():
    """
    Crée le fichier .env à partir du template
    """
    print("
📝 Configuration des variables d'environnement...")

    # Copier le template
    if not os.path.exists('.env'):
        run_command('cp .env.example_supabase .env', 'Copie du template .env')

    # Demander les informations Supabase
    print("
Veuillez entrer vos informations Supabase:")
    supabase_url = input("URL Supabase (ex: https://nevyttqdnanrmxsjozjd.supabase.co): ")
    supabase_anon_key = input("Clé Anon Supabase: ")
    supabase_service_key = input("Clé Service Supabase: ")

    # Mettre à jour le fichier .env
    with open('.env', 'r') as f:
        content = f.read()

    content = content.replace('https://nevyttqdnanrmxsjozjd.supabase.co', supabase_url)
    content = content.replace('sb_publishable_XQugS3Pj77HcKIX-qelwZQ_k7vp7JhJ', supabase_anon_key)

    with open('.env', 'w') as f:
        f.write(content)

    print("✅ Fichier .env mis à jour")

def install_dependencies():
    """
    Installe les dépendances Python
    """
    print("
📦 Installation des dépendances...")
    run_command('pip install -r requirements_supabase.txt', 'Installation des dépendances Python')

def setup_database():
    """
    Configure la base de données Supabase
    """
    print("
💾 Configuration de la base de données...")

    # Lire le schema SQL
    with open('backend/supabase_schema.sql', 'r') as f:
        schema_sql = f.read()

    print("
⚠️  Veuillez suivre ces étapes dans le dashboard Supabase:")
    print("1. Allez dans le dashboard Supabase")
    print("2. Ouvrez l'éditeur SQL")
    print("3. Copiez et collez le contenu du fichier backend/supabase_schema.sql")
    print("4. Cliquez sur 'Run' pour exécuter le script")
    input("
Appuyez sur Entrée une fois terminé...")

def setup_storage():
    """
    Configure le storage Supabase
    """
    print("
📁 Configuration du storage...")

    print("
⚠️  Veuillez suivre ces étapes dans le dashboard Supabase:")
    print("1. Allez dans Storage > Buckets")
    print("2. Créez les buckets suivants:")
    print("   - invoices")
    print("   - forms")
    print("   - temp")
    print("3. Configurez les politiques RLS pour chaque bucket")
    input("
Appuyez sur Entrée une fois terminé...")

def setup_edge_functions():
    """
    Configure les Edge Functions Supabase
    """
    print("
⚡ Configuration des Edge Functions...")

    print("
⚠️  Veuillez suivre ces étapes dans le dashboard Supabase:")
    print("1. Allez dans Edge Functions")
    print("2. Créez les fonctions suivantes:")
    print("   - ocr_process")
    print("   - pdf_generate")
    print("   - vat_calculate")
    print("   - email_send")
    print("   - batch_process")
    print("3. Copiez le code depuis les fichiers correspondants")
    input("
Appuyez sur Entrée une fois terminé...")

def test_installation():
    """
    Teste l'installation
    """
    print("
🧪 Test de l'installation...")

    # Test de l'API
    try:
        from backend.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        # Test de connexion
        response = supabase.table("users").select("count").limit(1).execute()
        if response.data is not None:
            print("✅ Connexion à Supabase réussie")
        else:
            print("❌ Erreur de connexion à Supabase")
            return False
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

    return True

def main():
    """
    Fonction principale d'installation
    """
    print("🚀 Installation de TAXRECLAIMAI avec Supabase")
    print("=" * 50)

    # Vérifier Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ requis")
        sys.exit(1)

    # Créer les répertoires nécessaires
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    os.makedirs("forms", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Étapes d'installation
    create_env_file()
    install_dependencies()
    setup_database()
    setup_storage()
    setup_edge_functions()

    # Test de l'installation
    if test_installation():
        print("
🎉 Installation réussie !")
        print("
Prochaines étapes:")
        print("1. Lancez l'application: uvicorn main_supabase:app --reload")
        print("2. Configurez le frontend avec les credentials Supabase")
        print("3. Déployez sur Railway ou autre plateforme")
    else:
        print("
❌ Échec de l'installation")
        print("Veuillez vérifier les étapes et réessayer")

if __name__ == "__main__":
    main()
