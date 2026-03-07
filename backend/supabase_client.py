
"""
Module de configuration Supabase
"""

from supabase import create_client, Client
import os
from typing import Optional

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://nevyttqdnanrmxsjozjd.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", os.getenv("SUPABASE_KEY", "sb_publishable_XQugS3Pj77HcKIX-qelwZQ_k7vp7JhJ"))

# Créer le client Supabase
supabase: Client = create_client(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY
)

def get_supabase_client() -> Client:
    """
    Récupère le client Supabase

    Returns:
        Client Supabase
    """
    return supabase

def get_supabase_url() -> str:
    """
    Récupère l'URL Supabase

    Returns:
        URL Supabase
    """
    return SUPABASE_URL

def get_supabase_key() -> str:
    """
    Récupère la clé API Supabase

    Returns:
        Clé API Supabase
    """
    return SUPABASE_KEY

# Configuration de l'authentification Supabase
def get_auth_client() -> Client:
    """
    Récupère le client d'authentification Supabase

    Returns:
        Client d'authentification Supabase
    """
    return supabase.auth

# Configuration du storage Supabase
def get_storage_client() -> Client:
    """
    Récupère le client de storage Supabase

    Returns:
        Client de storage Supabase
    """
    return supabase.storage

# Configuration de la base de données Supabase
def get_db_client() -> Client:
    """
    Récupère le client de base de données Supabase

    Returns:
        Client de base de données Supabase
    """
    return supabase.table

# Configuration des Edge Functions Supabase
def get_edge_function_url(function_name: str) -> str:
    """
    Récupère l'URL d'une Edge Function Supabase

    Args:
        function_name: Nom de la fonction

    Returns:
        URL de la fonction
    """
    return f"{SUPABASE_URL}/functions/v1/{function_name}"
