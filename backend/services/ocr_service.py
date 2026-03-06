
"""
Service OCR pour l'extraction des données des factures
"""

import os
import io
import base64
from typing import Dict, List, Optional, Union
from PIL import Image
import pytesseract
import PyPDF2
import pdf2image
import cv2
import numpy as np
from datetime import datetime

from supabase_client import get_supabase_client

class OCRService:
    """
    Service pour l'extraction de données des documents via OCR
    """

    def __init__(self):
        self.supabase = get_supabase_client()

        # Configuration de Tesseract
        self.tesseract_config = {
            'lang': 'fra+eng',  # Support français et anglais
            'oem': 3,  # Mode LSTM OCR Engine
            'psm': 6,  # Mode de segmentation de page
        }

    async def extract_from_file(self, file_path: str) -> Dict:
        """
        Extrait les données d'un fichier (PDF ou image)

        Args:
            file_path: Chemin du fichier à traiter

        Returns:
            Dictionnaire contenant les données extraites
        """
        try:
            # Déterminer le type de fichier
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.pdf':
                return await self._extract_from_pdf(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                return await self._extract_from_image(file_path)
            else:
                raise ValueError(f"Format de fichier non supporté: {file_extension}")

        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction OCR: {str(e)}")

    async def _extract_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extrait les données d'un fichier PDF

        Args:
            pdf_path: Chemin du fichier PDF

        Returns:
            Dictionnaire contenant les données extraites
        """
        try:
            # Convertir le PDF en images
            images = pdf2image.convert_from_path(pdf_path)

            # Traiter chaque page
            all_text = ""
            all_data = []

            for i, image in enumerate(images):
                # Convertir l'image en tableau numpy
                img_array = np.array(image)

                # Prétraitement de l'image
                processed_img = self._preprocess_image(img_array)

                # Extraction du texte
                text = pytesseract.image_to_string(
                    processed_img,
                    lang=self.tesseract_config['lang'],
                    config=f'--oem {self.tesseract_config["oem"]} --psm {self.tesseract_config["psm"]}'
                )

                all_text += f"

--- Page {i+1} ---

{text}"

                # Extraction structurée des données
                page_data = await self._extract_structured_data(text, page=i+1)
                all_data.extend(page_data)

            # Combiner les données de toutes les pages
            combined_data = self._combine_page_data(all_data)

            return {
                'raw_text': all_text,
                'structured_data': combined_data,
                'extraction_date': datetime.now().isoformat(),
                'pages_count': len(images)
            }

        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction du PDF: {str(e)}")

    async def _extract_from_image(self, image_path: str) -> Dict:
        """
        Extrait les données d'un fichier image

        Args:
            image_path: Chemin du fichier image

        Returns:
            Dictionnaire contenant les données extraites
        """
        try:
            # Charger l'image
            image = Image.open(image_path)

            # Convertir en tableau numpy
            img_array = np.array(image)

            # Prétraitement de l'image
            processed_img = self._preprocess_image(img_array)

            # Extraction du texte
            text = pytesseract.image_to_string(
                processed_img,
                lang=self.tesseract_config['lang'],
                config=f'--oem {self.tesseract_config["oem"]} --psm {self.tesseract_config["psm"]}'
            )

            # Extraction structurée des données
            structured_data = await self._extract_structured_data(text)

            return {
                'raw_text': text,
                'structured_data': structured_data,
                'extraction_date': datetime.now().isoformat(),
                'pages_count': 1
            }

        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction de l'image: {str(e)}")

    def _preprocess_image(self, img_array: np.ndarray) -> np.ndarray:
        """
        Prétraite une image pour améliorer l'OCR

        Args:
            img_array: Tableau numpy de l'image

        Returns:
            Image prétraitée
        """
        try:
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

            # Binarisation adaptative
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # Réduction du bruit
            denoised = cv2.medianBlur(binary, 3)

            return denoised

        except Exception as e:
            print(f"Erreur lors du prétraitement de l'image: {str(e)}")
            return img_array

    async def _extract_structured_data(self, text: str, page: int = 1) -> List[Dict]:
        """
        Extrait les données structurées du texte

        Args:
            text: Texte extrait par OCR
            page: Numéro de page

        Returns:
            Liste de données structurées
        """
        structured_data = []

        try:
            # Patterns pour l'extraction
            patterns = {
                'invoice_number': [
                    r'facture\s*n[°\s:]+([A-Z0-9-]+)',
                    r'invoice\s*n[°\s:]+([A-Z0-9-]+)',
                    r'n[°\s:]+([A-Z0-9-]+)\s*facture',
                ],
                'invoice_date': [
                    r'date\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                    r'facture\s*du\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                    r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                ],
                'supplier': [
                    r'fournisseur\s*:?\s*([A-Z][a-zA-Z\s&]+)',
                    r'supplier\s*:?\s*([A-Z][a-zA-Z\s&]+)',
                    r'([A-Z][a-zA-Z\s&]+)\s*s\.?a\.?',
                ],
                'vat_number': [
                    r'tva\s*:?\s*([A-Z]{2}[0-9A-Z]+)',
                    r'vat\s*:?\s*([A-Z]{2}[0-9A-Z]+)',
                    r'n[°\s:]+tva\s*:?\s*([A-Z]{2}[0-9A-Z]+)',
                ],
                'total_amount': [
                    r'total\s*:?\s*([0-9]+[.,][0-9]{2})',
                    r'montant\s*total\s*:?\s*([0-9]+[.,][0-9]{2})',
                    r'€\s*([0-9]+[.,][0-9]{2})',
                ],
                'vat_amount': [
                    r'tva\s*:?\s*([0-9]+[.,][0-9]{2})',
                    r'vat\s*:?\s*([0-9]+[.,][0-9]{2})',
                    r'montant\s*tva\s*:?\s*([0-9]+[.,][0-9]{2})',
                ],
                'vat_rate': [
                    r'taux\s*tva\s*:?\s*([0-9]+[.,]?\d*)\s*%',
                    r'vat\s*rate\s*:?\s*([0-9]+[.,]?\d*)\s*%',
                    r'([0-9]+[.,]?\d*)\s*%\s*tva',
                ],
            }

            # Extraire les données pour chaque pattern
            extracted_data = {
                'page': page,
                'confidence': 0.0,  # Sera calculé plus tard
            }

            for field, field_patterns in patterns.items():
                for pattern in field_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        extracted_data[field] = match.group(1).strip()
                        break

            # Calculer un score de confiance basé sur le nombre de champs extraits
            confidence = sum(1 for key in patterns.keys() if key in extracted_data) / len(patterns)
            extracted_data['confidence'] = confidence

            # Ajouter aux données structurées si la confiance est suffisante
            if confidence > 0.3:  # Seuil de confiance minimum
                structured_data.append(extracted_data)

            return structured_data

        except Exception as e:
            print(f"Erreur lors de l'extraction structurée: {str(e)}")
            return []

    def _combine_page_data(self, all_data: List[Dict]) -> Dict:
        """
        Combine les données extraites de plusieurs pages

        Args:
            all_data: Liste de données par page

        Returns:
            Données combinées
        """
        if not all_data:
            return {}

        # Prendre les données de la première page comme base
        combined = all_data[0].copy()

        # Pour les pages suivantes, ne garder que les champs manquants
        for page_data in all_data[1:]:
            for key, value in page_data.items():
                if key not in combined or not combined[key]:
                    combined[key] = value

        # Nettoyer les données
        for key in ['page', 'confidence']:
            if key in combined:
                del combined[key]

        # Calculer la confiance moyenne
        avg_confidence = sum(data.get('confidence', 0) for data in all_data) / len(all_data)
        combined['confidence'] = avg_confidence

        return combined

    async def process_invoice(self, file_path: str) -> Dict:
        """
        Traite une facture complète avec OCR et validation

        Args:
            file_path: Chemin du fichier de la facture

        Returns:
            Données de la facture traitées et validées
        """
        try:
            # Extraire les données via OCR
            ocr_result = await self.extract_from_file(file_path)
            structured_data = ocr_result['structured_data']

            # Valider et normaliser les données
            validated_data = self._validate_invoice_data(structured_data)

            # Enregistrer les résultats dans Supabase
            result = self.supabase.table("ocr_results").insert({
                'file_path': file_path,
                'raw_text': ocr_result['raw_text'],
                'structured_data': structured_data,
                'validated_data': validated_data,
                'confidence': validated_data.get('confidence', 0),
                'processed_at': datetime.now().isoformat()
            }).execute()

            return {
                'success': True,
                'invoice_data': validated_data,
                'ocr_confidence': validated_data.get('confidence', 0),
                'ocr_result_id': result.data[0]['id']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _validate_invoice_data(self, data: Dict) -> Dict:
        """
        Valide et normalise les données de facture

        Args:
            data: Données brutes extraites par OCR

        Returns:
            Données validées et normalisées
        """
        validated = data.copy()

        try:
            # Normaliser le numéro de facture
            if 'invoice_number' in validated:
                validated['invoice_number'] = validated['invoice_number'].upper().strip()

            # Normaliser la date
            if 'invoice_date' in validated:
                date_str = validated['invoice_date']
                # Tenter différents formats de date
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d']:
                    try:
                        validated['invoice_date'] = datetime.strptime(date_str, fmt).date().isoformat()
                        break
                    except ValueError:
                        continue

            # Normaliser les montants
            for amount_field in ['total_amount', 'vat_amount']:
                if amount_field in validated:
                    amount_str = validated[amount_field].replace(',', '.')
                    validated[amount_field] = float(amount_str)

            # Normaliser le taux de TVA
            if 'vat_rate' in validated:
                rate_str = validated['vat_rate'].replace(',', '.')
                validated['vat_rate'] = float(rate_str)

            # Calculer le montant HT si manquant
            if 'total_amount' in validated and 'vat_amount' in validated and 'amount_ht' not in validated:
                validated['amount_ht'] = validated['total_amount'] - validated['vat_amount']

            # Calculer le montant de TVA si manquant
            if 'total_amount' in validated and 'amount_ht' in validated and 'vat_amount' not in validated:
                validated['vat_amount'] = validated['total_amount'] - validated['amount_ht']

            # Calculer le taux de TVA si manquant
            if 'amount_ht' in validated and 'vat_amount' in validated and 'vat_rate' not in validated:
                if validated['amount_ht'] > 0:
                    validated['vat_rate'] = (validated['vat_amount'] / validated['amount_ht']) * 100

            return validated

        except Exception as e:
            print(f"Erreur lors de la validation des données: {str(e)}")
            return data

# Instance du service OCR
ocr_service = OCRService()
