
"""
Module de gestion des règles TVA pour 193 pays
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration AI
AI_API_URL = os.getenv("AI_API_URL", "https://api.groq.com/openai/v1/chat/completions")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")

# Règles TVA par pays (échantillon représentatif pour les principaux pays)
VAT_RULES = {
    'FR': {
        'name': 'France',
        'vat_rates': {
            'standard': 20.0,
            'reduced': 10.0,
            'super_reduced': 5.5,
            'special': 2.1
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['CA3', '3519']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'DE': {
        'name': 'Allemagne',
        'vat_rates': {
            'standard': 19.0,
            'reduced': 7.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['USt1V']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'IT': {
        'name': 'Italie',
        'vat_rates': {
            'standard': 22.0,
            'reduced': 10.0,
            'super_reduced': 4.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VA']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'ES': {
        'name': 'Espagne',
        'vat_rates': {
            'standard': 21.0,
            'reduced': 10.0,
            'super_reduced': 4.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['303', '360']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'GB': {
        'name': 'Royaume-Uni',
        'vat_rates': {
            'standard': 20.0,
            'reduced': 5.0,
            'zero': 0.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT65A']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'NL': {
        'name': 'Pays-Bas',
        'vat_rates': {
            'standard': 21.0,
            'reduced': 9.0,
            'zero': 0.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['OB']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'BE': {
        'name': 'Belgique',
        'vat_rates': {
            'standard': 21.0,
            'reduced': 12.0,
            'super_reduced': 6.0,
            'zero': 0.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['71.604']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'AT': {
        'name': 'Autriche',
        'vat_rates': {
            'standard': 20.0,
            'reduced': 13.0,
            'super_reduced': 10.0,
            'special': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['U21']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'CH': {
        'name': 'Suisse',
        'vat_rates': {
            'standard': 8.1,
            'reduced': 2.5,
            'special': 3.7
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['833']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'PL': {
        'name': 'Pologne',
        'vat_rates': {
            'standard': 23.0,
            'reduced': 8.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT-UE']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'SE': {
        'name': 'Suède',
        'vat_rates': {
            'standard': 25.0,
            'reduced': 12.0,
            'zero': 0.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['SKV 4632']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'DK': {
        'name': 'Danemark',
        'vat_rates': {
            'standard': 25.0,
            'zero': 0.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT 55']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'FI': {
        'name': 'Finlande',
        'vat_rates': {
            'standard': 25.5,
            'reduced': 14.0,
            'super_reduced': 10.0,
            'zero': 0.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT 811']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'NO': {
        'name': 'Norvège',
        'vat_rates': {
            'standard': 25.0,
            'reduced': 15.0,
            'super_reduced': 12.0,
            'zero': 0.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['RF-1032']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'PT': {
        'name': 'Portugal',
        'vat_rates': {
            'standard': 23.0,
            'reduced': 13.0,
            'intermediate': 9.0,
            'super_reduced': 6.0,
            'regional': 22.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['IVA54']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'GR': {
        'name': 'Grèce',
        'vat_rates': {
            'standard': 24.0,
            'reduced': 13.0,
            'super_reduced': 6.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['F2']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'IE': {
        'name': 'Irlande',
        'vat_rates': {
            'standard': 23.0,
            'reduced': 13.5,
            'super_reduced': 9.0,
            'zero': 0.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT66']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'LU': {
        'name': 'Luxembourg',
        'vat_rates': {
            'standard': 17.0,
            'reduced': 14.0,
            'super_reduced': 8.0,
            'super_super_reduced': 3.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['770']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'CZ': {
        'name': 'République tchèque',
        'vat_rates': {
            'standard': 21.0,
            'reduced': 15.0,
            'super_reduced': 10.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT 55']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'HU': {
        'name': 'Hongrie',
        'vat_rates': {
            'standard': 27.0,
            'reduced': 18.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['A60']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'RO': {
        'name': 'Roumanie',
        'vat_rates': {
            'standard': 19.0,
            'reduced': 9.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['300']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'BG': {
        'name': 'Bulgarie',
        'vat_rates': {
            'standard': 20.0,
            'reduced': 9.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT 7']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'HR': {
        'name': 'Croatie',
        'vat_rates': {
            'standard': 25.0,
            'reduced': 13.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['PDV-O']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'SI': {
        'name': 'Slovénie',
        'vat_rates': {
            'standard': 22.0,
            'reduced': 9.5,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['DDV-O']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'SK': {
        'name': 'Slovaquie',
        'vat_rates': {
            'standard': 20.0,
            'reduced': 10.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT 7']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'EE': {
        'name': 'Estonie',
        'vat_rates': {
            'standard': 20.0,
            'reduced': 9.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['KMD']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'LV': {
        'name': 'Lettonie',
        'vat_rates': {
            'standard': 21.0,
            'reduced': 12.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['PVN']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'LT': {
        'name': 'Lituanie',
        'vat_rates': {
            'standard': 21.0,
            'reduced': 9.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['FR0607']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'CY': {
        'name': 'Chypre',
        'vat_rates': {
            'standard': 19.0,
            'reduced': 9.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT 59']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'MT': {
        'name': 'Malte',
        'vat_rates': {
            'standard': 18.0,
            'reduced': 7.0,
            'super_reduced': 5.0
        },
        'recovery_conditions': {
            'minimum_amount': 50.0,
            'time_limit_months': 6,
            'electronic_filing': True,
            'form_types': ['VAT 5']
        },
        'documentation': [
            'original_invoice',
            'proof_of_payment',
            'import_declaration',
            'vat_certificate'
        ]
    },
    'US': {
        'name': 'États-Unis',
        'vat_rates': {'standard': 0.0, 'state_tax': 'variable'},
        'recovery_conditions': {'minimum_amount': 50.0, 'time_limit_months': 6, 'electronic_filing': True, 'form_types': ['8849']},
        'documentation': ['original_invoice', 'proof_of_payment', 'import_declaration', 'vat_certificate']
    },
    'JP': {
        'name': 'Japon',
        'vat_rates': {'standard': 10.0, 'reduced': 8.0},
        'recovery_conditions': {'minimum_amount': 5000, 'time_limit_months': 6, 'electronic_filing': True, 'form_types': ['331-1']},
        'documentation': ['original_invoice', 'proof_of_payment', 'import_declaration', 'vat_certificate']
    },
    'AU': {
        'name': 'Australie',
        'vat_rates': {'standard': 10.0},
        'recovery_conditions': {'minimum_amount': 75.0, 'time_limit_months': 6, 'electronic_filing': True, 'form_types': ['GST']},
        'documentation': ['original_invoice', 'proof_of_payment', 'import_declaration', 'vat_certificate']
    },
    'CA': {
        'name': 'Canada',
        'vat_rates': {'federal': 5.0, 'provincial': 'variable'},
        'recovery_conditions': {'minimum_amount': 50.0, 'time_limit_months': 6, 'electronic_filing': True, 'form_types': ['GST65']},
        'documentation': ['original_invoice', 'proof_of_payment', 'import_declaration', 'vat_certificate']
    },
    'AE': {
        'name': 'Émirats arabes unis',
        'vat_rates': {'standard': 5.0, 'zero': 0.0},
        'recovery_conditions': {'minimum_amount': 200, 'time_limit_months': 6, 'electronic_filing': True, 'form_types': ['VAT301']},
        'documentation': ['original_invoice', 'tax_registration', 'proof_of_payment']
    },
    'SA': {
        'name': 'Arabie Saoudite',
        'vat_rates': {'standard': 15.0, 'zero': 0.0},
        'recovery_conditions': {'minimum_amount': 1000, 'time_limit_months': 12, 'electronic_filing': True, 'form_types': ['VAT']},
        'documentation': ['original_invoice', 'zatca_qr_code', 'proof_of_payment']
    },
    'CN': {
        'name': 'Chine',
        'vat_rates': {'standard': 13.0, 'reduced': 9.0, 'low': 6.0},
        'recovery_conditions': {'minimum_amount': 500, 'time_limit_months': 12, 'electronic_filing': True, 'form_types': ['VAT_RETURN']},
        'documentation': ['fapiao', 'business_license', 'tax_id']
    },
    'KR': {
        'name': 'Corée du Sud',
        'vat_rates': {'standard': 10.0, 'zero': 0.0},
        'recovery_conditions': {'minimum_amount': 30000, 'time_limit_months': 6, 'electronic_filing': True, 'form_types': ['VAT50']},
        'documentation': ['tax_invoice', 'business_cert', 'payment_proof']
    },
    'IN': {
        'name': 'Inde',
        'vat_rates': {'standard': 18.0, 'luxury': 28.0, 'reduced': 12.0, 'low': 5.0},
        'recovery_conditions': {'minimum_amount': 5000, 'time_limit_months': 24, 'electronic_filing': True, 'form_types': ['RFD-01']},
        'documentation': ['gst_invoice', 'arn_receipt', 'firc_certificate']
    },
    'BR': {
        'name': 'Brésil',
        'vat_rates': {'standard': 17.5, 'interstate': 12.0, 'export': 0.0},
        'recovery_conditions': {'minimum_amount': 100, 'time_limit_months': 60, 'electronic_filing': True, 'form_types': ['PER/DCOMP']},
        'documentation': ['nfe_xml', 'danfe', 'tax_guide']
    },
    'MX': {
        'name': 'Mexique',
        'vat_rates': {'standard': 16.0, 'border': 8.0, 'zero': 0.0},
        'recovery_conditions': {'minimum_amount': 500, 'time_limit_months': 12, 'electronic_filing': True, 'form_types': ['F324']},
        'documentation': ['cfdi_xml', 'e-signature', 'bank_statement']
    },
    'ZA': {
        'name': 'Afrique du Sud',
        'vat_rates': {'standard': 15.0, 'zero': 0.0},
        'recovery_conditions': {'minimum_amount': 500, 'time_limit_months': 12, 'electronic_filing': True, 'form_types': ['VAT201']},
        'documentation': ['tax_invoice', 'import_sads', 'payment_proof']
    },
    'SG': {
        'name': 'Singapour',
        'vat_rates': {'standard': 9.0, 'zero': 0.0},
        'recovery_conditions': {'minimum_amount': 100, 'time_limit_months': 6, 'electronic_filing': True, 'form_types': ['GST-F5']},
        'documentation': ['tax_invoice', 'export_docs', 'permits']
    }
}


def get_vat_rules(country_code: str) -> Optional[Dict[str, Any]]:
    """
    Récupère les règles TVA pour un pays donné

    Args:
        country_code: Code ISO du pays (ex: FR, DE, IT)

    Returns:
        Dictionnaire contenant les règles TVA du pays ou None si non trouvé
    """
    country_code = country_code.upper()

    if country_code in VAT_RULES:
        return VAT_RULES[country_code]

    return None


def match_vat_recovery_rules(
    invoices: List[Dict[str, Any]], 
    vat_rules: Dict[str, Any], 
    company_vat: str
) -> Dict[str, Any]:
    """
    Match les factures avec les règles TVA et calcule les montants récupérables

    Args:
        invoices: Liste des factures à traiter
        vat_rules: Règles TVA du pays cible
        company_vat: Numéro de TVA de l'entreprise

    Returns:
        Dictionnaire contenant les résultats du matching
    """
    matched_invoices = []
    rejected_invoices = []
    total_recoverable = 0.0

    recovery_conditions = vat_rules.get('recovery_conditions', {})
    minimum_amount = recovery_conditions.get('minimum_amount', 50.0)

    for invoice in invoices:
        # Vérifier si la facture est éligible au remboursement
        is_eligible = True
        rejection_reason = ""

        # Vérifier le montant minimum
        if invoice.get('vat_amount', 0) < minimum_amount:
            is_eligible = False
            rejection_reason = f"Montant TVA inférieur au minimum requis ({minimum_amount}€)"

        # Vérifier la validité du numéro de TVA du fournisseur
        supplier_vat = invoice.get('vat_number', '')
        if not supplier_vat or len(supplier_vat) < 8:
            is_eligible = False
            rejection_reason = "Numéro de TVA du fournisseur invalide ou manquant"

        if is_eligible:
            # Calculer le montant récupérable
            recoverable_amount = invoice.get('vat_amount', 0)
            total_recoverable += recoverable_amount

            matched_invoices.append({
                **invoice,
                'recoverable_amount': recoverable_amount,
                'recovery_rate': 100.0,
                'status': 'eligible'
            })
        else:
            rejected_invoices.append({
                **invoice,
                'recoverable_amount': 0.0,
                'recovery_rate': 0.0,
                'status': 'rejected',
                'rejection_reason': rejection_reason
            })

    return {
        'matched_invoices': matched_invoices,
        'rejected_invoices': rejected_invoices,
        'total_recoverable': total_recoverable,
        'recovery_rate': len(matched_invoices) / len(invoices) * 100 if invoices else 0,
        'vat_rules_applied': vat_rules
    }


def get_ai_tax_advice(country_code: str, invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Utilise l'IA pour obtenir des conseils fiscaux sur un pays spécifique."""
    if not AI_API_KEY:
        return {"error": "IA non configurée"}
        
    prompt = f"""
    En tant qu'expert en fiscalité internationale (TVA/VAT), analyse la possibilité de récupération de TVA 
    pour le pays suivant : {country_code}.
    Données des factures : {json.dumps(invoices[:5])}
    
    Réponds en JSON avec :
    - eligibility (boolean)
    - standard_rate (float)
    - deadline_months (int)
    - warning (string)
    - steps (list of strings)
    """
    
    try:
        response = requests.post(
            AI_API_URL,
            headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            },
            timeout=15
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erreur IA Tax Advice: {e}")
    return {"error": "Analyse IA échouée"}

def calculate_vat_recovery_potential(
    invoices: List[Dict[str, Any]], 
    company_vat: str
) -> Dict[str, Any]:
    """
    Calcule le potentiel de récupération TVA pour un ensemble de factures

    Args:
        invoices: Liste des factures à analyser
        company_vat: Numéro de TVA de l'entreprise

    Returns:
        Dictionnaire contenant le potentiel de récupération par pays
    """
    # Grouper les factures par pays
    invoices_by_country = {}
    for invoice in invoices:
        country = invoice.get('country', 'FR')
        if country not in invoices_by_country:
            invoices_by_country[country] = []
        invoices_by_country[country].append(invoice)

    # Calculer le potentiel pour chaque pays
    results = {}
    total_potential = 0.0

    for country, country_invoices in invoices_by_country.items():
        vat_rules = get_vat_rules(country)
        if vat_rules:
            recovery_results = match_vat_recovery_rules(
                country_invoices, 
                vat_rules, 
                company_vat
            )

            results[country] = {
                'country_name': vat_rules.get('name', country),
                'total_invoices': len(country_invoices),
                'matched_invoices': len(recovery_results['matched_invoices']),
                'recoverable_amount': recovery_results['total_recoverable'],
                'recovery_rate': recovery_results['recovery_rate'],
                'vat_rates': vat_rules.get('vat_rates', {}),
                'form_types': vat_rules.get('recovery_conditions', {}).get('form_types', [])
            }

            total_potential += recovery_results['total_recoverable']

    return {
        'by_country': results,
        'total_potential': total_potential,
        'currency': 'EUR',
        'company_vat': company_vat
    }


def get_supported_countries() -> List[Dict[str, Any]]:
    """
    Retourne la liste des pays supportés avec leurs règles TVA

    Returns:
        Liste des dictionnaires contenant les informations des pays
    """
    countries = []
    for country_code, rules in VAT_RULES.items():
        countries.append({
            'code': country_code,
            'name': rules.get('name', country_code),
            'vat_rates': rules.get('vat_rates', {}),
            'form_types': rules.get('recovery_conditions', {}).get('form_types', [])
        })

    return countries


def validate_vat_number(vat_number: str, country_code: str) -> bool:
    """
    Valide un numéro de TVA pour un pays donné

    Args:
        vat_number: Numéro de TVA à valider
        country_code: Code ISO du pays

    Returns:
        True si le numéro de TVA est valide, False sinon
    """
    if not vat_number or len(vat_number) < 8:
        return False

    # Vérifier que le préfixe du pays correspond
    if not vat_number.upper().startswith(country_code.upper()):
        return False

    # Pour une validation plus approfondie, on pourrait utiliser l'API VIES de l'UE
    # ou implémenter les algorithmes de validation spécifiques à chaque pays

    return True


def get_vat_rate(country_code: str, rate_type: str = 'standard') -> Optional[float]:
    """
    Récupère le taux de TVA pour un pays et un type de taux donnés

    Args:
        country_code: Code ISO du pays
        rate_type: Type de taux (standard, reduced, super_reduced, etc.)

    Returns:
        Taux de TVA ou None si non trouvé
    """
    vat_rules = get_vat_rules(country_code)
    if not vat_rules:
        return None

    vat_rates = vat_rules.get('vat_rates', {})
    return vat_rates.get(rate_type)


def get_recovery_deadline(country_code: str) -> Optional[int]:
    """
    Récupère le délai de remboursement TVA pour un pays

    Args:
        country_code: Code ISO du pays

    Returns:
        Délai en mois ou None si non trouvé
    """
    vat_rules = get_vat_rules(country_code)
    if not vat_rules:
        return None

    recovery_conditions = vat_rules.get('recovery_conditions', {})
    return recovery_conditions.get('time_limit_months', 6)
