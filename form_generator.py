
"""
Module de génération des formulaires de remboursement TVA
"""

import os
import zipfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# Configuration des répertoires
FORMS_DIR = Path("forms")
TEMP_DIR = Path("temp")

# Création des répertoires nécessaires
for directory in [FORMS_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Mapping des formulaires par pays
FORM_TEMPLATES = {
    'FR': {
        'name': 'France',
        'forms': ['CA3', '3519']
    },
    'DE': {
        'name': 'Allemagne',
        'forms': ['USt1V']
    },
    'IT': {
        'name': 'Italie',
        'forms': ['VA']
    },
    'ES': {
        'name': 'Espagne',
        'forms': ['303', '360']
    },
    'GB': {
        'name': 'Royaume-Uni',
        'forms': ['VAT65A']
    },
    'NL': {
        'name': 'Pays-Bas',
        'forms': ['OB']
    },
    'BE': {
        'name': 'Belgique',
        'forms': ['71.604']
    },
    'AT': {
        'name': 'Autriche',
        'forms': ['U21']
    },
    'CH': {
        'name': 'Suisse',
        'forms': ['833']
    },
    'PL': {
        'name': 'Pologne',
        'forms': ['VAT-UE']
    },
    'SE': {
        'name': 'Suède',
        'forms': ['SKV 4632']
    },
    'DK': {
        'name': 'Danemark',
        'forms': ['VAT 55']
    },
    'FI': {
        'name': 'Finlande',
        'forms': ['VAT 811']
    },
    'NO': {
        'name': 'Norvège',
        'forms': ['RF-1032']
    },
    'PT': {
        'name': 'Portugal',
        'forms': ['IVA54']
    },
    'GR': {
        'name': 'Grèce',
        'forms': ['F2']
    },
    'IE': {
        'name': 'Irlande',
        'forms': ['VAT66']
    },
    'LU': {
        'name': 'Luxembourg',
        'forms': ['770']
    },
    'CZ': {
        'name': 'République tchèque',
        'forms': ['VAT 55']
    },
    'HU': {
        'name': 'Hongrie',
        'forms': ['A60']
    },
    'RO': {
        'name': 'Roumanie',
        'forms': ['300']
    },
    'BG': {
        'name': 'Bulgarie',
        'forms': ['VAT7']
    },
    'HR': {
        'name': 'Croatie',
        'forms': ['PDV-O']
    },
    'SI': {
        'name': 'Slovénie',
        'forms': ['DP-DDV']
    },
    'SK': {
        'name': 'Slovaquie',
        'forms': ['VAT 55']
    },
    'EE': {
        'name': 'Estonie',
        'forms': ['KMD']
    },
    'LV': {
        'name': 'Lettonie',
        'forms': ['PVN1']
    },
    'LT': {
        'name': 'Lituanie',
        'forms': ['FR0606']
    },
    'CY': {
        'name': 'Chypre',
        'forms': ['VAT 59']
    },
    'MT': {
        'name': 'Malte',
        'forms': ['VAT 57']
    },
    'US': {
        'name': 'États-Unis',
        'forms': ['8849']
    },
    'CA': {
        'name': 'Canada',
        'forms': ['GST189']
    },
    'AU': {
        'name': 'Australie',
        'forms': ['F1']
    },
    'JP': {
        'name': 'Japon',
        'forms': ['3-3-2']
    },
    'KR': {
        'name': 'Corée du Sud',
        'forms': ['VAT 50']
    },
    'CN': {
        'name': 'Chine',
        'forms': ['VAT 001']
    },
    'IN': {
        'name': 'Inde',
        'forms': ['GST RFD-01']
    },
    'BR': {
        'name': 'Brésil',
        'forms': ['PER/DCOMP']
    },
    'AR': {
        'name': 'Argentine',
        'forms': ['F731']
    },
    'MX': {
        'name': 'Mexique',
        'forms': ['F5']
    },
    'ZA': {
        'name': 'Afrique du Sud',
        'forms': ['VAT 101']
    },
    'SG': {
        'name': 'Singapour',
        'forms': ['GST F5']
    },
    'HK': {
        'name': 'Hong Kong',
        'forms': ['IRD 71A']
    },
    'MY': {
        'name': 'Malaisie',
        'forms': ['GST 03']
    },
    'TH': {
        'name': 'Thaïlande',
        'forms': ['PP 36']
    },
    'ID': {
        'name': 'Indonésie',
        'forms': ['1131']
    },
    'PH': {
        'name': 'Philippines',
        'forms': ['2552M']
    },
    'VN': {
        'name': 'Vietnam',
        'forms': ['01/GTGT']
    },
    'TR': {
        'name': 'Turquie',
        'forms': ['VAT 1']
    },
    'IL': {
        'name': 'Israël',
        'forms': ['135']
    },
    'AE': {
        'name': 'Émirats arabes unis',
        'forms': ['VAT 301']
    }
}

def create_pdf_header(canvas, title, subtitle=None):
    """
    Crée l'en-tête du formulaire PDF

    Args:
        canvas: Canvas ReportLab
        title: Titre du formulaire
        subtitle: Sous-titre optionnel
    """
    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(2*cm, 27*cm, title)

    if subtitle:
        canvas.setFont("Helvetica", 12)
        canvas.drawString(2*cm, 26.5*cm, subtitle)

    # Ajouter une ligne de séparation
    canvas.setStrokeColor(colors.darkblue)
    canvas.setLineWidth(1)
    canvas.line(2*cm, 26*cm, 18*cm, 26*cm)

def create_pdf_section(canvas, title, y_position):
    """
    Crée une section dans le formulaire PDF

    Args:
        canvas: Canvas ReportLab
        title: Titre de la section
        y_position: Position verticale de la section

    Returns:
        Nouvelle position verticale après la section
    """
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(colors.darkblue)
    canvas.drawString(2*cm, y_position*cm, title)

    # Ligne de séparation
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, (y_position-0.3)*cm, 18*cm, (y_position-0.3)*cm)

    return y_position - 0.5

def create_pdf_field(canvas, label, value, x_position, y_position, width=5):
    """
    Crée un champ dans le formulaire PDF

    Args:
        canvas: Canvas ReportLab
        label: Étiquette du champ
        value: Valeur du champ
        x_position: Position horizontale
        y_position: Position verticale
        width: Largeur du champ en cm
    """
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(x_position*cm, y_position*cm, label)

    # Cadre pour la valeur
    canvas.setStrokeColor(colors.grey)
    canvas.setLineWidth(0.5)
    canvas.rect((x_position + 4)*cm, (y_position - 0.3)*cm, width*cm, 0.5*cm)

    # Valeur
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString((x_position + 4.2)*cm, (y_position - 0.1)*cm, str(value))

def create_pdf_table(canvas, data, headers, x_position, y_position, col_widths=None):
    """
    Crée un tableau dans le formulaire PDF

    Args:
        canvas: Canvas ReportLab
        data: Données du tableau
        headers: En-têtes du tableau
        x_position: Position horizontale
        y_position: Position verticale
        col_widths: Largeurs des colonnes

    Returns:
        Nouvelle position verticale après le tableau
    """
    if col_widths is None:
        col_widths = [3*cm, 4*cm, 3*cm, 3*cm]

    # Créer le tableau
    table_data = [headers] + data

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Dessiner le tableau
    table.wrapOn(canvas, 16*cm, 10*cm)
    table.drawOn(canvas, x_position*cm, y_position*cm)

    # Calculer la nouvelle position verticale
    table_height = len(data) * 0.7 + 1
    return y_position - table_height

def create_vat_form(invoices: List[Dict[str, Any]], country_code: str, company_vat: str, form_type: str) -> str:
    """
    Crée un formulaire de remboursement TVA pour un pays spécifique

    Args:
        invoices: Liste des factures à inclure dans le formulaire
        country_code: Code du pays (FR, DE, IT, etc.)
        company_vat: Numéro de TVA de l'entreprise
        form_type: Type de formulaire (CA3, USt1V, VA, etc.)

    Returns:
        Chemin vers le fichier PDF créé
    """
    # Créer un nom de fichier unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{country_code}_{form_type}_{timestamp}.pdf"
    filepath = FORMS_DIR / filename

    # Créer le document PDF
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Créer un canvas pour le PDF
    c = canvas.Canvas(str(filepath), pagesize=A4)

    # Informations sur le pays
    country_info = FORM_TEMPLATES.get(country_code, {'name': 'Pays inconnu', 'forms': []})
    country_name = country_info['name']

    # Titre du formulaire
    title = f"Formulaire de remboursement TVA - {country_name}"
    subtitle = f"Formulaire {form_type}"

    # Créer l'en-tête
    create_pdf_header(c, title, subtitle)

    # Position verticale actuelle
    y_pos = 24

    # Section 1: Informations de l'entreprise
    y_pos = create_pdf_section(c, "Informations de l'entreprise", y_pos)
    create_pdf_field(c, "Numéro de TVA:", company_vat, 2, y_pos)
    create_pdf_field(c, "Date de soumission:", datetime.now().strftime("%d/%m/%Y"), 9, y_pos)

    y_pos -= 1.5

    # Section 2: Résumé des factures
    y_pos = create_pdf_section(c, "Résumé des factures", y_pos)

    # Calculer les totaux
    total_ht = sum(invoice.get('amount_ht', 0) for invoice in invoices)
    total_vat = sum(invoice.get('vat_amount', 0) for invoice in invoices)
    total_amount = sum(invoice.get('total_amount', 0) for invoice in invoices)

    create_pdf_field(c, "Nombre de factures:", len(invoices), 2, y_pos)
    create_pdf_field(c, "Montant total HT:", f"{total_ht:.2f} EUR", 9, y_pos)

    y_pos -= 1
    create_pdf_field(c, "Montant total TVA:", f"{total_vat:.2f} EUR", 2, y_pos)
    create_pdf_field(c, "Montant total TTC:", f"{total_amount:.2f} EUR", 9, y_pos)

    y_pos -= 1.5

    # Section 3: Détail des factures
    y_pos = create_pdf_section(c, "Détail des factures", y_pos)

    # Préparer les données du tableau
    headers = ["Numéro", "Date", "Fournisseur", "Montant TVA"]
    data = []

    for invoice in invoices:
        data.append([
            invoice.get('invoice_number', ''),
            invoice.get('date', ''),
            invoice.get('supplier', '')[:20],  # Limiter la longueur du nom du fournisseur
            f"{invoice.get('vat_amount', 0):.2f} EUR"
        ])

    # Créer le tableau
    y_pos = create_pdf_table(c, data, headers, 2, y_pos)

    y_pos -= 1.5

    # Section 4: Déclaration et signature
    y_pos = create_pdf_section(c, "Déclaration et signature", y_pos)

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    declaration = "Je certifie que les informations fournies dans ce formulaire sont exactes et complètes. " \
                   "Je m'engage à fournir tous les documents justificatifs sur demande des autorités fiscales."
    c.drawString(2*cm, y_pos*cm, declaration)

    y_pos -= 2

    # Zone de signature
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.rect(12*cm, (y_pos-0.5)*cm, 5*cm, 2*cm)

    c.setFont("Helvetica", 9)
    c.drawString(12*cm, (y_pos-0.2)*cm, "Signature:")
    c.drawString(12*cm, (y_pos-2.2)*cm, "Date:")

    # Sauvegarder le PDF
    c.save()

    return str(filepath)

def generate_vat_forms(invoices: List[Dict[str, Any]], country_code: str, company_vat: str) -> List[str]:
    """
    Génère les formulaires de remboursement TVA pour un pays spécifique

    Args:
        invoices: Liste des factures à inclure dans les formulaires
        country_code: Code du pays (FR, DE, IT, etc.)
        company_vat: Numéro de TVA de l'entreprise

    Returns:
        Liste des chemins vers les fichiers PDF créés
    """
    # Vérifier si le pays est supporté
    if country_code not in FORM_TEMPLATES:
        raise ValueError(f"Pays non supporté: {country_code}")

    # Obtenir les types de formulaires pour ce pays
    form_types = FORM_TEMPLATES[country_code]['forms']

    # Générer un formulaire pour chaque type
    forms = []
    for form_type in form_types:
        form_path = create_vat_form(invoices, country_code, company_vat, form_type)
        forms.append(form_path)

    return forms

def create_zip_archive(form_paths: List[str], archive_id: str) -> str:
    """
    Crée une archive ZIP contenant les formulaires générés

    Args:
        form_paths: Liste des chemins vers les fichiers PDF
        archive_id: ID unique pour l'archive

    Returns:
        Chemin vers l'archive ZIP créée
    """
    # Créer le nom de l'archive
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"vat_forms_{archive_id}_{timestamp}.zip"
    zip_path = FORMS_DIR / zip_filename

    # Créer l'archive ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for form_path in form_paths:
            # Ajouter le fichier à l'archive avec son nom de base
            zipf.write(form_path, os.path.basename(form_path))

    return str(zip_path)

def generate_multi_country_forms(invoices_by_country: Dict[str, List[Dict[str, Any]]], company_vat: str) -> List[str]:
    """
    Génère des formulaires de remboursement TVA pour plusieurs pays

    Args:
        invoices_by_country: Dictionnaire avec les codes pays comme clés et les listes de factures comme valeurs
        company_vat: Numéro de TVA de l'entreprise

    Returns:
        Liste des chemins vers les fichiers PDF créés
    """
    all_forms = []

    for country_code, invoices in invoices_by_country.items():
        try:
            country_forms = generate_vat_forms(invoices, country_code, company_vat)
            all_forms.extend(country_forms)
        except ValueError as e:
            print(f"Erreur pour le pays {country_code}: {str(e)}")

    return all_forms
