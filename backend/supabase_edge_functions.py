
"""
Configuration des Edge Functions Supabase
"""

from typing import Dict, Any, List
import os

# Configuration de base
SUPABASE_URL = "https://nevyttqdnanrmxsjozjd.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_XQugS3Pj77HcKIX-qelwZQ_k7vp7JhJ"

# Configuration des Edge Functions
EDGE_FUNCTIONS = {
    "ocr_process": {
        "name": "ocr_process",
        "description": "Traitement OCR des factures",
        "method": "POST",
        "timeout": 300,
        "memory": 1024,  # 1GB
        "environment": {
            "TESSERACT_PATH": "/usr/bin/tesseract",
            "TESSERACT_LANGUAGES": "fra,eng,deu,ita,spa,nld,pol,swe,dan,nor,fin"
        }
    },
    "pdf_generate": {
        "name": "pdf_generate",
        "description": "Génération de formulaires PDF",
        "method": "POST",
        "timeout": 60,
        "memory": 512,  # 512MB
        "environment": {
            "REPORTLAB_TTF_DIR": "/usr/share/fonts"
        }
    },
    "vat_calculate": {
        "name": "vat_calculate",
        "description": "Calcul des montants récupérables TVA",
        "method": "POST",
        "timeout": 120,
        "memory": 512,
        "environment": {}
    },
    "email_send": {
        "name": "email_send",
        "description": "Envoi d'emails de notification",
        "method": "POST",
        "timeout": 30,
        "memory": 256,
        "environment": {
            "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
            "SMTP_USER": os.getenv("SMTP_USER"),
            "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
            "EMAIL_FROM": os.getenv("EMAIL_FROM", "noreply@taxreclaimai.com")
        }
    },
    "batch_process": {
        "name": "batch_process",
        "description": "Traitement par lots de factures",
        "method": "POST",
        "timeout": 600,  # 10 minutes
        "memory": 2048,  # 2GB
        "environment": {
            "MAX_BATCH_SIZE": "120",
            "BATCH_TIMEOUT": "300"
        }
    }
}

def get_edge_function_url(function_name: str) -> str:
    """
    Récupère l'URL d'une Edge Function

    Args:
        function_name: Nom de la fonction

    Returns:
        URL de la fonction
    """
    return f"{SUPABASE_URL}/functions/v1/{function_name}"

def get_all_edge_functions() -> Dict[str, Dict[str, Any]]:
    """
    Récupère toutes les Edge Functions

    Returns:
        Dictionnaire de toutes les fonctions
    """
    return EDGE_FUNCTIONS

def get_edge_function_config(function_name: str) -> Dict[str, Any]:
    """
    Récupère la configuration d'une Edge Function

    Args:
        function_name: Nom de la fonction

    Returns:
        Configuration de la fonction

    Raises:
        ValueError: Si la fonction n'existe pas
    """
    if function_name not in EDGE_FUNCTIONS:
        raise ValueError(f"Edge Function '{function_name}' non trouvée")

    return EDGE_FUNCTIONS[function_name]

def list_edge_functions() -> List[Dict[str, Any]]:
    """
    Liste toutes les Edge Functions

    Returns:
        Liste des fonctions avec leurs configurations
    """
    return [
        {
            "name": func["name"],
            "description": func["description"],
            "url": get_edge_function_url(func["name"]),
            "method": func["method"],
            "timeout": func["timeout"],
            "memory": func["memory"]
        }
        for func in EDGE_FUNCTIONS.values()
    ]
