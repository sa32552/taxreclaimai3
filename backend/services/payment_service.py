
"""
Service de Matching des Paiements
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

class PaymentService:
    """Service pour gérer les preuves de paiement et le matching"""

    def __init__(self, db: Session):
        self.db = db

    def upload_payment_proof(self, company_id: str, file_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enregistre une nouvelle preuve de paiement (relevé, reçu)
        """
        payment_id = str(uuid.uuid4())
        # Simulation d'insertion en DB via Supabase/SQLAlchemy
        payment_record = {
            "id": payment_id,
            "company_id": company_id,
            "file_path": file_path,
            "amount": data.get("amount"),
            "currency": data.get("currency", "EUR"),
            "payment_date": data.get("date"),
            "reference": data.get("reference"),
            "supplier_name": data.get("supplier_name"),
            "status": "unmatched"
        }
        
        # Ici on lancerait normalement le matching automatique
        matches = self.auto_match_invoice(payment_record)
        
        return {
            "payment": payment_record,
            "potential_matches": matches
        }

    def auto_match_invoice(self, payment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Algorithme de matching intelligent (IA/Heuristique)
        """
        # 1. Recherche les factures non payées de la même entreprise
        # 2. Filtre par montant exact (+/- 0.01)
        # 3. Filtre par nom de fournisseur (Fuzzy matching)
        # 4. Filtre par date (Le paiement doit être après ou proche de la facture)
        
        # Simulation de résultats
        return [
            {
                "invoice_id": "inv_123",
                "confidence": 0.95,
                "reason": "Montant exact et fournisseur correspondant"
            }
        ]

    def confirm_match(self, invoice_id: str, payment_id: str, amount: float) -> bool:
        """
        Valide manuellement ou automatiquement une liaison entre facture et paiement
        """
        # Création de l'entrée dans invoice_payments
        # Mise à jour du statut de la facture vers 'paid'
        return True
