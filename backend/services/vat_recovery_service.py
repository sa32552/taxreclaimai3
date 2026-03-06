
"""
Service métier pour la récupération TVA
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database.models.vat_claim import VATClaim, VATClaimStatus
from backend.database.models.invoice import Invoice, InvoiceStatus
from backend.database.repositories.vat_claim_repository import VATClaimRepository
from backend.database.repositories.invoice_repository import InvoiceRepository
from backend.workflow.approval_engine import ApprovalEngine, ApprovalLevel
from backend.workflow.change_tracker import ChangeTracker, ChangeType
from backend.workflow.notification_engine import NotificationEngine, NotificationType, NotificationPriority

class VATRecoveryService:
    """Service métier pour la récupération TVA"""

    def __init__(
        self,
        db: Session,
        approval_engine: Optional[ApprovalEngine] = None,
        change_tracker: Optional[ChangeTracker] = None,
        notification_engine: Optional[NotificationEngine] = None
    ):
        """
        Initialise le service

        Args:
            db: Session de base de données
            approval_engine: Moteur d'approbation (optionnel)
            change_tracker: Suivi des modifications (optionnel)
            notification_engine: Moteur de notifications (optionnel)
        """
        self.db = db
        self.vat_claim_repository = VATClaimRepository(db)
        self.invoice_repository = InvoiceRepository(db)
        self.approval_engine = approval_engine or ApprovalEngine()
        self.change_tracker = change_tracker or ChangeTracker()
        self.notification_engine = notification_engine or NotificationEngine()

    def create_vat_claim(
        self,
        user_id: str,
        user_name: str,
        target_country: str,
        company_vat: str,
        invoices: List[Dict[str, Any]],
        require_approval: bool = True
    ) -> VATClaim:
        """
        Crée une nouvelle demande de récupération TVA

        Args:
            user_id: ID de l'utilisateur qui crée
            user_name: Nom de l'utilisateur qui crée
            target_country: Pays cible
            company_vat: Numéro de TVA de l'entreprise
            invoices: Liste des factures
            require_approval: Indique si une approbation est requise

        Returns:
            Demande de récupération TVA créée
        """
        # Calculer le montant total récupérable
        total_recoverable = sum(
            invoice.get("vat_amount", 0) * 0.8  # 80% récupérable en moyenne
            for invoice in invoices
        )

        # Calculer la période (mois en cours)
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Créer la demande
        claim = VATClaim(
            claim_number="",  # Sera généré lors de la soumission
            target_country=target_country,
            company_vat_number=company_vat,
            period_start=period_start,
            period_end=period_end,
            total_recoverable=total_recoverable,
            total_approved=0.0,
            total_rejected=0.0,
            status=VATClaimStatus.DRAFT,
            company_id=invoices[0].get("company_id") if invoices else None
        )

        # Sauvegarder la demande
        created_claim = self.vat_claim_repository.create(claim)

        # Créer un workflow d'approbation si requis
        if require_approval:
            workflow = self.approval_engine.create_workflow(
                entity_type="vat_claim",
                entity_id=created_claim.id,
                requester_id=user_id,
                requester_name=user_name,
                required_levels=[ApprovalLevel.LEVEL_1, ApprovalLevel.LEVEL_2]
            )

            # Envoyer une notification aux approbateurs
            self.notification_engine.send_bulk_notification(
                user_ids=["manager_id", "director_id"],  # À remplacer par les IDs réels
                notification_type=NotificationType.WORKFLOW_APPROVAL_REQUIRED,
                title=f"Demande de récupération TVA à approuver",
                message=f"Une nouvelle demande de récupération TVA de {total_recoverable:.2f} EUR pour {target_country} nécessite votre approbation",
                priority=NotificationPriority.HIGH,
                entity_type="vat_claim",
                entity_id=created_claim.id,
                action_url=f"/vat-claims/{created_claim.id}/approve"
            )
        else:
            # Soumettre automatiquement la demande
            created_claim.submit(user_id)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="vat_claim",
            entity_id=created_claim.id,
            change_type=ChangeType.CREATE,
            user_id=user_id,
            user_name=user_name,
            changes={
                "target_country": target_country,
                "company_vat": company_vat,
                "invoice_count": len(invoices),
                "total_recoverable": total_recoverable,
                "require_approval": require_approval
            }
        )

        # Envoyer une notification au demandeur
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.VAT_CLAIM_SUBMITTED,
            title="Demande de récupération TVA créée",
            message=f"Votre demande de récupération TVA de {total_recoverable:.2f} EUR pour {target_country} a été créée",
            priority=NotificationPriority.NORMAL,
            entity_type="vat_claim",
            entity_id=created_claim.id,
            action_url=f"/vat-claims/{created_claim.id}"
        )

        return created_claim

    def get_vat_claim(self, claim_id: str) -> Optional[VATClaim]:
        """
        Récupère une demande de récupération TVA

        Args:
            claim_id: ID de la demande

        Returns:
            Demande ou None si non trouvée
        """
        return self.vat_claim_repository.get_by_id(claim_id)

    def get_vat_claims(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[VATClaimStatus] = None
    ) -> List[VATClaim]:
        """
        Récupère les demandes de récupération TVA

        Args:
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner
            company_id: Filtrer par entreprise
            status: Filtrer par statut

        Returns:
            Liste des demandes
        """
        return self.vat_claim_repository.get_all(
            skip=skip,
            limit=limit,
            company_id=company_id,
            status=status
        )

    def submit_vat_claim(
        self,
        claim_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[VATClaim]:
        """
        Soumet une demande de récupération TVA

        Args:
            claim_id: ID de la demande
            user_id: ID de l'utilisateur qui soumet
            user_name: Nom de l'utilisateur qui soumet

        Returns:
            Demande soumise ou None
        """
        # Récupérer la demande
        claim = self.get_vat_claim(claim_id)
        if not claim:
            return None

        # Soumettre la demande
        claim.submit(user_id)

        # Sauvegarder les modifications
        submitted_claim = self.vat_claim_repository.update(claim)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="vat_claim",
            entity_id=submitted_claim.id,
            change_type=ChangeType.SUBMIT,
            user_id=user_id,
            user_name=user_name,
            changes={}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.VAT_CLAIM_SUBMITTED,
            title="Demande de récupération TVA soumise",
            message=f"Votre demande de récupération TVA {submitted_claim.claim_number} a été soumise aux autorités fiscales",
            priority=NotificationPriority.HIGH,
            entity_type="vat_claim",
            entity_id=submitted_claim.id,
            action_url=f"/vat-claims/{submitted_claim.id}"
        )

        return submitted_claim

    def approve_vat_claim(
        self,
        claim_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[VATClaim]:
        """
        Approuve une demande de récupération TVA

        Args:
            claim_id: ID de la demande
            user_id: ID de l'utilisateur qui approuve
            user_name: Nom de l'utilisateur qui approuve

        Returns:
            Demande approuvée ou None
        """
        # Récupérer la demande
        claim = self.get_vat_claim(claim_id)
        if not claim:
            return None

        # Approuver la demande
        claim.approve(user_id)

        # Sauvegarder les modifications
        approved_claim = self.vat_claim_repository.update(claim)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="vat_claim",
            entity_id=approved_claim.id,
            change_type=ChangeType.APPROVE,
            user_id=user_id,
            user_name=user_name,
            changes={}
        )

        # Envoyer une notification au demandeur
        self.notification_engine.send_notification(
            user_id=approved_claim.submitted_by,
            notification_type=NotificationType.VAT_CLAIM_APPROVED,
            title="Demande de récupération TVA approuvée",
            message=f"Votre demande de récupération TVA {approved_claim.claim_number} a été approuvée",
            priority=NotificationPriority.HIGH,
            entity_type="vat_claim",
            entity_id=approved_claim.id,
            action_url=f"/vat-claims/{approved_claim.id}"
        )

        return approved_claim

    def reject_vat_claim(
        self,
        claim_id: str,
        user_id: str,
        user_name: str,
        reason: str
    ) -> Optional[VATClaim]:
        """
        Rejette une demande de récupération TVA

        Args:
            claim_id: ID de la demande
            user_id: ID de l'utilisateur qui rejette
            user_name: Nom de l'utilisateur qui rejette
            reason: Raison du rejet

        Returns:
            Demande rejetée ou None
        """
        # Récupérer la demande
        claim = self.get_vat_claim(claim_id)
        if not claim:
            return None

        # Rejeter la demande
        claim.reject(user_id, reason)

        # Sauvegarder les modifications
        rejected_claim = self.vat_claim_repository.update(claim)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="vat_claim",
            entity_id=rejected_claim.id,
            change_type=ChangeType.REJECT,
            user_id=user_id,
            user_name=user_name,
            changes={"rejection_reason": reason}
        )

        # Envoyer une notification au demandeur
        self.notification_engine.send_notification(
            user_id=rejected_claim.submitted_by,
            notification_type=NotificationType.VAT_CLAIM_REJECTED,
            title="Demande de récupération TVA rejetée",
            message=f"Votre demande de récupération TVA {rejected_claim.claim_number} a été rejetée: {reason}",
            priority=NotificationPriority.HIGH,
            entity_type="vat_claim",
            entity_id=rejected_claim.id,
            action_url=f"/vat-claims/{rejected_claim.id}"
        )

        return rejected_claim

    def cancel_vat_claim(
        self,
        claim_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[VATClaim]:
        """
        Annule une demande de récupération TVA

        Args:
            claim_id: ID de la demande
            user_id: ID de l'utilisateur qui annule
            user_name: Nom de l'utilisateur qui annule

        Returns:
            Demande annulée ou None
        """
        # Récupérer la demande
        claim = self.get_vat_claim(claim_id)
        if not claim:
            return None

        # Annuler la demande
        claim.cancel()

        # Sauvegarder les modifications
        cancelled_claim = self.vat_claim_repository.update(claim)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="vat_claim",
            entity_id=cancelled_claim.id,
            change_type=ChangeType.CANCEL,
            user_id=user_id,
            user_name=user_name,
            changes={}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.VAT_CLAIM_SUBMITTED,
            title="Demande de récupération TVA annulée",
            message=f"Votre demande de récupération TVA {cancelled_claim.claim_number} a été annulée",
            priority=NotificationPriority.NORMAL,
            entity_type="vat_claim",
            entity_id=cancelled_claim.id,
            action_url=f"/vat-claims/{cancelled_claim.id}"
        )

        return cancelled_claim

    def get_statistics(
        self,
        company_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques de récupération TVA

        Args:
            company_id: ID de l'entreprise
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)

        Returns:
            Dictionnaire avec les statistiques
        """
        return self.vat_claim_repository.get_statistics(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date
        )

    def get_pending_claims(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[VATClaim]:
        """
        Récupère les demandes en attente

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes en attente
        """
        return self.vat_claim_repository.get_pending_claims(
            company_id=company_id,
            skip=skip,
            limit=limit
        )
