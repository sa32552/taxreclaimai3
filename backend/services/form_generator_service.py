
"""
Service de génération de formulaires fiscaux
"""

import os
import io
import base64
from typing import Dict, List, Optional, Union
from datetime import datetime, date
from jinja2 import Environment, FileSystemLoader
import pdfkit
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors

from supabase_client import get_supabase_client
from config.global_tax_regulations import COUNTRY_TAX_REGULATIONS

class FormGeneratorService:
    """
    Service pour la génération de formulaires fiscaux
    """

    def __init__(self):
        self.supabase = get_supabase_client()

        # Configuration du générateur PDF
        self.pdf_config = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }

        # Initialiser l'environnement Jinja2
        self.template_env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=True
        )

    async def generate_vat_form(self, 
                               country_code: str, 
                               form_type: str, 
                               period_data: Dict, 
                               company_data: Dict,
                               invoices_data: List[Dict]) -> Dict:
        """
        Génère un formulaire de TVA pour un pays et une période spécifiques

        Args:
            country_code: Code du pays (ex: 'FR', 'DE', 'GB')
            form_type: Type de formulaire (ex: 'FR_3310_CA3', 'DE_UST_VA')
            period_data: Données de la période (début, fin, etc.)
            company_data: Données de l'entreprise
            invoices_data: Liste des factures à inclure

        Returns:
            Dictionnaire contenant le formulaire généré et ses métadonnées
        """
        try:
            # Récupérer la réglementation fiscale du pays
            tax_regulation = COUNTRY_TAX_REGULATIONS.get(country_code)

            if not tax_regulation:
                raise ValueError(f"Pays non supporté: {country_code}")

            # Vérifier que le type de formulaire est valide pour ce pays
            if form_type not in tax_regulation.form_types:
                raise ValueError(f"Type de formulaire non valide pour {country_code}: {form_type}")

            # Calculer les totaux
            totals = self._calculate_vat_totals(invoices_data)

            # Préparer les données pour le template
            template_data = {
                'company': company_data,
                'period': period_data,
                'invoices': invoices_data,
                'totals': totals,
                'form_type': form_type,
                'country_code': country_code,
                'generation_date': datetime.now().strftime('%d/%m/%Y'),
                'currency': tax_regulation.currency,
                'vat_rates': tax_regulation.vat_rates
            }

            # Générer le PDF
            pdf_content = await self._generate_pdf(form_type, template_data)

            # Sauvegarder le formulaire dans Supabase Storage
            file_name = f"{form_type}_{period_data.get('period_id', datetime.now().strftime('%Y%m%d'))}.pdf"
            file_path = await self._save_form_to_storage(pdf_content, file_name, country_code)

            # Enregistrer les métadonnées dans Supabase
            form_record = self.supabase.table("forms").insert({
                'form_type': form_type,
                'country_code': country_code,
                'period_id': period_data.get('period_id'),
                'company_id': company_data.get('id'),
                'file_path': file_path,
                'status': 'generated',
                'total_vat_amount': totals.get('total_vat', 0),
                'total_net_amount': totals.get('total_net', 0),
                'total_gross_amount': totals.get('total_gross', 0),
                'invoice_count': len(invoices_data),
                'generated_at': datetime.now().isoformat()
            }).execute()

            return {
                'success': True,
                'form_id': form_record.data[0]['id'],
                'file_path': file_path,
                'form_type': form_type,
                'totals': totals,
                'invoice_count': len(invoices_data)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_vat_totals(self, invoices_data: List[Dict]) -> Dict:
        """
        Calcule les totaux de TVA à partir des factures

        Args:
            invoices_data: Liste des factures

        Returns:
            Dictionnaire des totaux calculés
        """
        totals = {
            'total_net': 0.0,
            'total_vat': 0.0,
            'total_gross': 0.0,
            'vat_by_rate': {}
        }

        for invoice in invoices_data:
            net_amount = float(invoice.get('amount_ht', 0))
            vat_amount = float(invoice.get('vat_amount', 0))
            gross_amount = float(invoice.get('total_amount', 0))
            vat_rate = str(invoice.get('vat_rate', 0))

            # Ajouter aux totaux généraux
            totals['total_net'] += net_amount
            totals['total_vat'] += vat_amount
            totals['total_gross'] += gross_amount

            # Ajouter aux totaux par taux de TVA
            if vat_rate not in totals['vat_by_rate']:
                totals['vat_by_rate'][vat_rate] = {
                    'net_amount': 0.0,
                    'vat_amount': 0.0,
                    'gross_amount': 0.0,
                    'invoice_count': 0
                }

            totals['vat_by_rate'][vat_rate]['net_amount'] += net_amount
            totals['vat_by_rate'][vat_rate]['vat_amount'] += vat_amount
            totals['vat_by_rate'][vat_rate]['gross_amount'] += gross_amount
            totals['vat_by_rate'][vat_rate]['invoice_count'] += 1

        return totals

    async def _generate_pdf(self, form_type: str, template_data: Dict) -> bytes:
        """
        Génère un PDF à partir d'un template

        Args:
            form_type: Type de formulaire
            template_data: Données pour le template

        Returns:
            Contenu du PDF en bytes
        """
        try:
            # Charger le template approprié
            template = self.template_env.get_template(f"{form_type}.html")

            # Rendre le template avec les données
            html_content = template.render(**template_data)

            # Convertir en PDF
            pdf_content = pdfkit.from_string(html_content, False, options=self.pdf_config)

            return pdf_content

        except Exception as e:
            # Si le template HTML n'existe pas, utiliser la génération directe avec ReportLab
            return await self._generate_pdf_with_reportlab(form_type, template_data)

    async def _generate_pdf_with_reportlab(self, form_type: str, template_data: Dict) -> bytes:
        """
        Génère un PDF directement avec ReportLab

        Args:
            form_type: Type de formulaire
            template_data: Données pour le formulaire

        Returns:
            Contenu du PDF en bytes
        """
        buffer = io.BytesIO()

        # Créer le document PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        # Contenu du document
        story = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['h1']
        normal_style = styles['Normal']

        # En-tête
        title = Paragraph(f"Formulaire de TVA: {form_type}", title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # Informations de l'entreprise
        company_data = template_data.get('company', {})
        company_info = [
            ['Entreprise:', company_data.get('name', '')],
            ['Adresse:', company_data.get('address', '')],
            ['Numéro TVA:', company_data.get('vat_number', '')],
        ]

        company_table = Table(company_info, colWidths=[2*inch, 4*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(company_table)
        story.append(Spacer(1, 12))

        # Période
        period_data = template_data.get('period', {})
        period_info = [
            ['Période:', f"{period_data.get('start_date', '')} au {period_data.get('end_date', '')}"],
        ]

        period_table = Table(period_info, colWidths=[2*inch, 4*inch])
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(period_table)
        story.append(Spacer(1, 12))

        # Détails des factures
        invoices = template_data.get('invoices', [])
        totals = template_data.get('totals', {})

        # Tableau des totaux par taux de TVA
        vat_by_rate = totals.get('vat_by_rate', {})
        if vat_by_rate:
            vat_headers = [['Taux TVA', 'Montant HT', 'Montant TVA', 'Montant TTC', 'Nombre de factures']]
            vat_rows = []

            for rate, rate_data in vat_by_rate.items():
                vat_rows.append([
                    f"{rate}%",
                    f"{rate_data['net_amount']:.2f}",
                    f"{rate_data['vat_amount']:.2f}",
                    f"{rate_data['gross_amount']:.2f}",
                    str(rate_data['invoice_count'])
                ])

            # Ligne des totaux
            vat_rows.append([
                'TOTAL',
                f"{totals.get('total_net', 0):.2f}",
                f"{totals.get('total_vat', 0):.2f}",
                f"{totals.get('total_gross', 0):.2f}",
                str(len(invoices))
            ])

            vat_table_data = vat_headers + vat_rows

            vat_table = Table(vat_table_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            vat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.grey),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(vat_table)
            story.append(Spacer(1, 12))

        # Pied de page
        footer_text = f"Généré le {template_data.get('generation_date', '')} par TAXRECLAIMAI"
        footer = Paragraph(footer_text, normal_style)
        story.append(Spacer(1, 24))
        story.append(footer)

        # Construire le PDF
        doc.build(story)

        # Récupérer le contenu du PDF
        pdf_content = buffer.getvalue()
        buffer.close()

        return pdf_content

    async def _save_form_to_storage(self, pdf_content: bytes, file_name: str, country_code: str) -> str:
        """
        Sauvegarde un formulaire PDF dans Supabase Storage

        Args:
            pdf_content: Contenu du PDF
            file_name: Nom du fichier
            country_code: Code du pays

        Returns:
            Chemin du fichier dans le storage
        """
        try:
            # Déterminer le bucket en fonction du pays
            bucket = f"forms-{country_code.lower()}"

            # Créer le dossier si nécessaire
            folder = f"{datetime.now().strftime('%Y/%m')}"

            # Chemin complet du fichier
            file_path = f"{folder}/{file_name}"

            # Encoder le contenu en base64
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

            # Uploader vers Supabase Storage
            self.supabase.storage.from_(bucket).upload(
                path=file_path,
                file=pdf_base64,
                file_options={'content-type': 'application/pdf'}
            )

            return file_path

        except Exception as e:
            raise Exception(f"Erreur lors de la sauvegarde du formulaire: {str(e)}")

    async def get_form(self, form_id: str) -> Dict:
        """
        Récupère un formulaire par son ID

        Args:
            form_id: ID du formulaire

        Returns:
            Données du formulaire
        """
        try:
            # Récupérer les métadonnées
            result = self.supabase.table("forms").select("*").eq("id", form_id).execute()

            if not result.data:
                raise ValueError("Formulaire non trouvé")

            form_data = result.data[0]

            # Récupérer le fichier PDF
            country_code = form_data.get('country_code', '').lower()
            bucket = f"forms-{country_code}"
            file_path = form_data.get('file_path', '')

            if file_path:
                file_result = self.supabase.storage.from_(bucket).download(file_path)
                form_data['pdf_content'] = file_result

            return form_data

        except Exception as e:
            raise Exception(f"Erreur lors de la récupération du formulaire: {str(e)}")

    async def list_forms(self, company_id: str, limit: int = 50, offset: int = 0) -> Dict:
        """
        Liste les formulaires d'une entreprise

        Args:
            company_id: ID de l'entreprise
            limit: Nombre maximum de résultats
            offset: Décalage pour la pagination

        Returns:
            Liste des formulaires
        """
        try:
            # Récupérer les formulaires
            result = self.supabase.table("forms")                .select("*")                .eq("company_id", company_id)                .order("generated_at", desc=True)                .range(offset, offset + limit - 1)                .execute()

            return {
                'forms': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            raise Exception(f"Erreur lors de la liste des formulaires: {str(e)}")

    async def update_form_status(self, form_id: str, status: str) -> Dict:
        """
        Met à jour le statut d'un formulaire

        Args:
            form_id: ID du formulaire
            status: Nouveau statut

        Returns:
            Résultat de la mise à jour
        """
        try:
            # Mettre à jour le statut
            result = self.supabase.table("forms")                .update({
                    "status": status,
                    "updated_at": datetime.now().isoformat()
                })                .eq("id", form_id)                .execute()

            if not result.data:
                raise ValueError("Formulaire non trouvé")

            return {
                'success': True,
                'form': result.data[0]
            }

        except Exception as e:
            raise Exception(f"Erreur lors de la mise à jour du statut: {str(e)}")

    async def delete_form(self, form_id: str) -> Dict:
        """
        Supprime un formulaire

        Args:
            form_id: ID du formulaire

        Returns:
            Résultat de la suppression
        """
        try:
            # Récupérer les informations du formulaire
            form_result = self.supabase.table("forms").select("*").eq("id", form_id).execute()

            if not form_result.data:
                raise ValueError("Formulaire non trouvé")

            form_data = form_result.data[0]

            # Supprimer le fichier du storage
            country_code = form_data.get('country_code', '').lower()
            bucket = f"forms-{country_code}"
            file_path = form_data.get('file_path', '')

            if file_path:
                self.supabase.storage.from_(bucket).remove([file_path])

            # Supprimer l'enregistrement de la base de données
            self.supabase.table("forms").delete().eq("id", form_id).execute()

            return {
                'success': True,
                'message': 'Formulaire supprimé avec succès'
            }

        except Exception as e:
            raise Exception(f"Erreur lors de la suppression du formulaire: {str(e)}")
