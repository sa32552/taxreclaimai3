
"""
Service métier pour les factures
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models.invoice import Invoice, InvoiceStatus
from backend.database.repositories.invoice_repository import InvoiceRepository
from backend.workflow.validation_pipeline import ValidationPipeline, ValidationResult
from backend.workflow.change_tracker import ChangeTracker, ChangeType
from backend.workflow.notification_engine import NotificationEngine, NotificationType, NotificationPriority

class InvoiceService:
    """Service métier pour les factures"""

    def __init__(
        self,
        db: Session,
        validation_pipeline: Optional[ValidationPipeline] = None,
        change_tracker: Optional[ChangeTracker] = None,
        notification_engine: Optional[NotificationEngine] = None
    ):
        """
        Initialise le service

        Args:
            db: Session de base de données
            validation_pipeline: Pipeline de validation (optionnel)
            change_tracker: Suivi des modifications (optionnel)
            notification_engine: Moteur de notifications (optionnel)
        """
        self.db = db
        self.invoice_repository = InvoiceRepository(db)
        self.validation_pipeline = validation_pipeline or ValidationPipeline()
        self.change_tracker = change_tracker or ChangeTracker()
        self.notification_engine = notification_engine or NotificationEngine()

    def check_duplicates(self, invoice_data: Dict[str, Any]) -> List[Invoice]:
        """
        Recherche des doublons potentiels (même fournisseur, numero, montant, entreprise)
        """
        company_id = invoice_data.get("company_id")
        supplier = invoice_data.get("supplier")
        invoice_number = invoice_data.get("invoice_number")
        total_amount = invoice_data.get("total_amount")
        
        if not all([company_id, supplier, invoice_number, total_amount]):
            return []
            
        return self.invoice_repository.get_all(
            company_id=company_id,
            filters={
                "supplier": supplier,
                "invoice_number": invoice_number,
                "total_amount": total_amount
            }
        )

    def create_invoice(
        self,
        invoice_data: Dict[str, Any],
        user_id: str,
        user_name: str
    ) -> Invoice:
        """
        Crée une nouvelle facture

        Args:
            invoice_data: Données de la facture
            user_id: ID de l'utilisateur qui crée
            user_name: Nom de l'utilisateur qui crée

        Returns:
            Facture créée

        Raises:
            ValueError: Si les données sont invalides
        """
        # Valider les données
        validation_results = self.validation_pipeline.validate(invoice_data)

        # Vérifier les erreurs critiques
        critical_errors = [
            v for v in validation_results
            if not v.is_passed and v.severity in ["error", "critical"]
        ]

        if critical_errors:
            error_messages = [v.message for v in critical_errors]
            raise ValueError(f"Erreurs de validation: {', '.join(error_messages)}")

        # Détection automatique des doublons
        existing_invoices = self.check_duplicates(invoice_data)
        if existing_invoices:
            raise ValueError(f"DOUBLON DÉTECTÉ : La facture {invoice_data.get('invoice_number')} du fournisseur {invoice_data.get('supplier')} existe déjà pour un montant de {invoice_data.get('total_amount')} {invoice_data.get('currency')}.")

        # Créer la facture
        invoice = Invoice(
            invoice_number=invoice_data.get("invoice_number", ""),
            date=datetime.fromisoformat(invoice_data["date"]) if isinstance(invoice_data["date"], str) else invoice_data["date"],
            supplier=invoice_data.get("supplier", ""),
            supplier_vat_number=invoice_data.get("supplier_vat_number", ""),
            country=invoice_data.get("country", ""),
            amount_ht=invoice_data.get("amount_ht", 0.0),
            vat_amount=invoice_data.get("vat_amount", 0.0),
            total_amount=invoice_data.get("total_amount", 0.0),
            currency=invoice_data.get("currency", "EUR"),
            language=invoice_data.get("language", "FR"),
            extraction_confidence=invoice_data.get("extraction_confidence", 0.98),
            extraction_data=invoice_data.get("extraction_data", {}),
            status=InvoiceStatus.UPLOADED,
            company_id=invoice_data.get("company_id")
        )

        # Sauvegarder la facture
        created_invoice = self.invoice_repository.create(invoice)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="invoice",
            entity_id=created_invoice.id,
            change_type=ChangeType.CREATE,
            user_id=user_id,
            user_name=user_name,
            changes={"data": invoice_data}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.INVOICE_UPLOADED,
            title=f"Facture {created_invoice.invoice_number} créée",
            message=f"Une nouvelle facture a été créée: {created_invoice.supplier} - {created_invoice.total_amount:.2f} {created_invoice.currency}",
            priority=NotificationPriority.NORMAL,
            entity_type="invoice",
            entity_id=created_invoice.id,
            action_url=f"/invoices/{created_invoice.id}"
        )

        return created_invoice

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """
        Récupère une facture par son ID

        Args:
            invoice_id: ID de la facture

        Returns:
            Facture ou None si non trouvée
        """
        return self.invoice_repository.get_by_id(invoice_id)

    def get_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[InvoiceStatus] = None
    ) -> List[Invoice]:
        """
        Récupère les factures

        Args:
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner
            company_id: Filtrer par entreprise
            status: Filtrer par statut

        Returns:
            Liste des factures
        """
        return self.invoice_repository.get_all(
            skip=skip,
            limit=limit,
            company_id=company_id,
            status=status
        )

    def update_invoice(
        self,
        invoice_id: str,
        invoice_data: Dict[str, Any],
        user_id: str,
        user_name: str
    ) -> Optional[Invoice]:
        """
        Met à jour une facture

        Args:
            invoice_id: ID de la facture
            invoice_data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            user_name: Nom de l'utilisateur qui met à jour

        Returns:
            Facture mise à jour ou None

        Raises:
            ValueError: Si les données sont invalides
        """
        # Récupérer la facture existante
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return None

        # Vérifier si la facture est verrouillée (Archivage Légal)
        if getattr(invoice, 'is_locked', False):
            raise ValueError(f"CONFORMITÉ : Impossible de modifier la facture {invoice.invoice_number} car elle est verrouillée pour archivage fiscal (Période fermée).")

        # Valider les nouvelles données
        validation_results = self.validation_pipeline.validate(invoice_data)

        # Vérifier les erreurs critiques
        critical_errors = [
            v for v in validation_results
            if not v.is_passed and v.severity in ["error", "critical"]
        ]

        if critical_errors:
            error_messages = [v.message for v in critical_errors]
            raise ValueError(f"Erreurs de validation: {', '.join(error_messages)}")

        # Sauvegarder les anciennes valeurs
        previous_values = invoice.to_dict()

        # Mettre à jour les champs
        if "invoice_number" in invoice_data:
            invoice.invoice_number = invoice_data["invoice_number"]
        if "date" in invoice_data:
            invoice.date = datetime.fromisoformat(invoice_data["date"]) if isinstance(invoice_data["date"], str) else invoice_data["date"]
        if "supplier" in invoice_data:
            invoice.supplier = invoice_data["supplier"]
        if "supplier_vat_number" in invoice_data:
            invoice.supplier_vat_number = invoice_data["supplier_vat_number"]
        if "country" in invoice_data:
            invoice.country = invoice_data["country"]
        if "amount_ht" in invoice_data:
            invoice.amount_ht = invoice_data["amount_ht"]
        if "vat_amount" in invoice_data:
            invoice.vat_amount = invoice_data["vat_amount"]
        if "total_amount" in invoice_data:
            invoice.total_amount = invoice_data["total_amount"]
        if "currency" in invoice_data:
            invoice.currency = invoice_data["currency"]
        if "language" in invoice_data:
            invoice.language = invoice_data["language"]
        if "extraction_confidence" in invoice_data:
            invoice.extraction_confidence = invoice_data["extraction_confidence"]
        if "extraction_data" in invoice_data:
            invoice.extraction_data = invoice_data["extraction_data"]

        # Sauvegarder les modifications
        updated_invoice = self.invoice_repository.update(invoice)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="invoice",
            entity_id=updated_invoice.id,
            change_type=ChangeType.UPDATE,
            user_id=user_id,
            user_name=user_name,
            changes={"new_data": invoice_data, "old_data": previous_values}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.INVOICE_PROCESSED,
            title=f"Facture {updated_invoice.invoice_number} mise à jour",
            message=f"La facture a été mise à jour: {updated_invoice.supplier} - {updated_invoice.total_amount:.2f} {updated_invoice.currency}",
            priority=NotificationPriority.NORMAL,
            entity_type="invoice",
            entity_id=updated_invoice.id,
            action_url=f"/invoices/{updated_invoice.id}"
        )

        return updated_invoice

    def delete_invoice(
        self,
        invoice_id: str,
        user_id: str,
        user_name: str
    ) -> bool:
        """
        Supprime une facture

        Args:
            invoice_id: ID de la facture
            user_id: ID de l'utilisateur qui supprime
            user_name: Nom de l'utilisateur qui supprime

        Returns:
            True si supprimée, False sinon
        """
        # Récupérer la facture
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return False

        # Vérifier si la facture est verrouillée (Archivage Légal)
        if getattr(invoice, 'is_locked', False):
            raise ValueError(f"CRITIQUE : Toute suppression est interdite pour les documents archivés légalement (Facture {invoice.invoice_number}).")

        # Supprimer la facture
        deleted = self.invoice_repository.delete(invoice_id)

        if deleted:
            # Enregistrer le suivi des modifications
            self.change_tracker.track_change(
                entity_type="invoice",
                entity_id=invoice_id,
                change_type=ChangeType.DELETE,
                user_id=user_id,
                user_name=user_name,
                changes={"deleted_invoice": invoice.to_dict()}
            )

        return deleted

    def process_invoice(
        self,
        invoice_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[Invoice]:
        """
        Traite une facture (extraction OCR et validation)

        Args:
            invoice_id: ID de la facture
            user_id: ID de l'utilisateur qui traite
            user_name: Nom de l'utilisateur qui traite

        Returns:
            Facture traitée ou None
        """
        # Récupérer la facture
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return None

        # Simuler le traitement (en production, utiliserait pdf_processor)
        invoice.status = InvoiceStatus.PROCESSED
        invoice.validated_at = datetime.utcnow()
        invoice.validated_by = user_id

        # Sauvegarder les modifications
        processed_invoice = self.invoice_repository.update(invoice)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="invoice",
            entity_id=processed_invoice.id,
            change_type=ChangeType.UPDATE,
            user_id=user_id,
            user_name=user_name,
            changes={"status": "PROCESSED"}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.INVOICE_PROCESSED,
            title=f"Facture {processed_invoice.invoice_number} traitée",
            message=f"La facture a été traitée avec succès: {processed_invoice.supplier} - {processed_invoice.total_amount:.2f} {processed_invoice.currency}",
            priority=NotificationPriority.NORMAL,
            entity_type="invoice",
            entity_id=processed_invoice.id,
            action_url=f"/invoices/{processed_invoice.id}"
        )

        return processed_invoice

    def approve_invoice(
        self,
        invoice_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[Invoice]:
        """
        Approuve une facture

        Args:
            invoice_id: ID de la facture
            user_id: ID de l'utilisateur qui approuve
            user_name: Nom de l'utilisateur qui approuve

        Returns:
            Facture approuvée ou None
        """
        # Récupérer la facture
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return None

        # Approuver la facture
        invoice.approve(user_id)

        # Sauvegarder les modifications
        approved_invoice = self.invoice_repository.update(invoice)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="invoice",
            entity_id=approved_invoice.id,
            change_type=ChangeType.APPROVE,
            user_id=user_id,
            user_name=user_name,
            changes={"status": "APPROVED"}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.INVOICE_APPROVED,
            title=f"Facture {approved_invoice.invoice_number} approuvée",
            message=f"La facture a été approuvée: {approved_invoice.supplier} - {approved_invoice.total_amount:.2f} {approved_invoice.currency}",
            priority=NotificationPriority.NORMAL,
            entity_type="invoice",
            entity_id=approved_invoice.id,
            action_url=f"/invoices/{approved_invoice.id}"
        )

        return approved_invoice

    def reject_invoice(
        self,
        invoice_id: str,
        user_id: str,
        user_name: str,
        reason: str
    ) -> Optional[Invoice]:
        """
        Rejette une facture

        Args:
            invoice_id: ID de la facture
            user_id: ID de l'utilisateur qui rejette
            user_name: Nom de l'utilisateur qui rejette
            reason: Raison du rejet

        Returns:
            Facture rejetée ou None
        """
        # Récupérer la facture
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return None

        # Rejeter la facture
        invoice.reject(user_id)

        # Sauvegarder les modifications
        rejected_invoice = self.invoice_repository.update(invoice)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="invoice",
            entity_id=rejected_invoice.id,
            change_type=ChangeType.REJECT,
            user_id=user_id,
            user_name=user_name,
            changes={"status": "REJECTED", "reason": reason}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.INVOICE_REJECTED,
            title=f"Facture {rejected_invoice.invoice_number} rejetée",
            message=f"La facture a été rejetée: {rejected_invoice.supplier} - Raison: {reason}",
            priority=NotificationPriority.HIGH,
            entity_type="invoice",
            entity_id=rejected_invoice.id,
            action_url=f"/invoices/{rejected_invoice.id}"
        )

        return rejected_invoice

    def get_recoverable_invoices(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Récupère les factures éligibles à la récupération de TVA

        Args:
            company_id: ID de l'entreprise
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures éligibles
        """
        return self.invoice_repository.get_recoverable_invoices(
            company_id=company_id,
            skip=skip,
            limit=limit
        )

    def get_invoice_statistics(
        self,
        company_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques des factures

        Args:
            company_id: ID de l'entreprise
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)

        Returns:
            Dictionnaire avec les statistiques
        """
        return self.invoice_repository.get_statistics(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date
        )
