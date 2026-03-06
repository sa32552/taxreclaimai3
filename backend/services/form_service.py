
"""
Service métier pour les formulaires
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models.form import Form, FormType, FormStatus
from backend.database.repositories.form_repository import FormRepository
from backend.workflow.signature_manager import SignatureManager, SignatureType
from backend.workflow.change_tracker import ChangeTracker, ChangeType
from backend.workflow.notification_engine import NotificationEngine, NotificationType, NotificationPriority

class FormService:
    """Service métier pour les formulaires"""

    def __init__(
        self,
        db: Session,
        signature_manager: Optional[SignatureManager] = None,
        change_tracker: Optional[ChangeTracker] = None,
        notification_engine: Optional[NotificationEngine] = None
    ):
        """
        Initialise le service

        Args:
            db: Session de base de données
            signature_manager: Gestionnaire de signatures (optionnel)
            change_tracker: Suivi des modifications (optionnel)
            notification_engine: Moteur de notifications (optionnel)
        """
        self.db = db
        self.form_repository = FormRepository(db)
        self.signature_manager = signature_manager or SignatureManager()
        self.change_tracker = change_tracker or ChangeTracker()
        self.notification_engine = notification_engine or NotificationEngine()

    def create_form(
        self,
        form_data: Dict[str, Any],
        user_id: str,
        user_name: str
    ) -> Form:
        """
        Crée un nouveau formulaire

        Args:
            form_data: Données du formulaire
            user_id: ID de l'utilisateur qui crée
            user_name: Nom de l'utilisateur qui crée

        Returns:
            Formulaire créé
        """
        # Créer le formulaire
        form = Form(
            form_number="",  # Sera généré lors de la génération
            form_type=FormType(form_data.get("form_type", "CA3")),
            country=form_data.get("country", "FR"),
            period_start=datetime.fromisoformat(form_data["period_start"]) if isinstance(form_data["period_start"], str) else form_data["period_start"],
            period_end=datetime.fromisoformat(form_data["period_end"]) if isinstance(form_data["period_end"], str) else form_data["period_end"],
            form_data=form_data.get("data", {}),
            company_id=form_data.get("company_id"),
            vat_claim_id=form_data.get("vat_claim_id")
        )

        # Sauvegarder le formulaire
        created_form = self.form_repository.create(form)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="form",
            entity_id=created_form.id,
            change_type=ChangeType.CREATE,
            user_id=user_id,
            user_name=user_name,
            changes={"form_data": form_data}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.FORM_GENERATED,
            title=f"Formulaire {created_form.form_type.value} créé",
            message=f"Un nouveau formulaire {created_form.form_type.value} a été créé pour {created_form.country}",
            priority=NotificationPriority.NORMAL,
            entity_type="form",
            entity_id=created_form.id,
            action_url=f"/forms/{created_form.id}"
        )

        return created_form

    def get_form(self, form_id: str) -> Optional[Form]:
        """
        Récupère un formulaire par son ID

        Args:
            form_id: ID du formulaire

        Returns:
            Formulaire ou None si non trouvé
        """
        return self.form_repository.get_by_id(form_id)

    def get_forms(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[FormStatus] = None
    ) -> List[Form]:
        """
        Récupère les formulaires

        Args:
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner
            company_id: Filtrer par entreprise
            status: Filtrer par statut

        Returns:
            Liste des formulaires
        """
        return self.form_repository.get_all(
            skip=skip,
            limit=limit,
            company_id=company_id,
            status=status
        )

    def generate_form(
        self,
        form_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[Form]:
        """
        Génère un formulaire (crée le PDF et signe)

        Args:
            form_id: ID du formulaire
            user_id: ID de l'utilisateur qui génère
            user_name: Nom de l'utilisateur qui génère

        Returns:
            Formulaire généré ou None
        """
        # Récupérer le formulaire
        form = self.get_form(form_id)
        if not form:
            return None

        # Générer le formulaire (en production, utiliserait form_generator)
        form.generate(user_id)

        # Signer le formulaire
        self.signature_manager.create_signature(
            entity_type="form",
            entity_id=form.id,
            signature_type=SignatureType.GENERATION,
            signer_id=user_id,
            signer_name=user_name,
            signer_role="user",
            data={"form_type": form.form_type.value}
        )

        # Sauvegarder les modifications
        generated_form = self.form_repository.update(form)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="form",
            entity_id=generated_form.id,
            change_type=ChangeType.UPDATE,
            user_id=user_id,
            user_name=user_name,
            changes={"generated": True}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.FORM_GENERATED,
            title=f"Formulaire {generated_form.form_number} généré",
            message=f"Le formulaire {generated_form.form_type.value} a été généré avec succès",
            priority=NotificationPriority.NORMAL,
            entity_type="form",
            entity_id=generated_form.id,
            action_url=f"/forms/{generated_form.id}/download"
        )

        return generated_form

    def submit_form(
        self,
        form_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[Form]:
        """
        Soumet un formulaire

        Args:
            form_id: ID du formulaire
            user_id: ID de l'utilisateur qui soumet
            user_name: Nom de l'utilisateur qui soumet

        Returns:
            Formulaire soumis ou None
        """
        # Récupérer le formulaire
        form = self.get_form(form_id)
        if not form:
            return None

        # Soumettre le formulaire
        form.submit(user_id)

        # Signer le formulaire
        self.signature_manager.create_signature(
            entity_type="form",
            entity_id=form.id,
            signature_type=SignatureType.SUBMISSION,
            signer_id=user_id,
            signer_name=user_name,
            signer_role="user",
            data={"form_type": form.form_type.value}
        )

        # Sauvegarder les modifications
        submitted_form = self.form_repository.update(form)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="form",
            entity_id=submitted_form.id,
            change_type=ChangeType.SUBMIT,
            user_id=user_id,
            user_name=user_name,
            changes={}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=user_id,
            notification_type=NotificationType.FORM_SUBMITTED,
            title=f"Formulaire {submitted_form.form_number} soumis",
            message=f"Le formulaire {submitted_form.form_type.value} a été soumis aux autorités fiscales",
            priority=NotificationPriority.HIGH,
            entity_type="form",
            entity_id=submitted_form.id,
            action_url=f"/forms/{submitted_form.id}"
        )

        return submitted_form

    def approve_form(
        self,
        form_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[Form]:
        """
        Approuve un formulaire

        Args:
            form_id: ID du formulaire
            user_id: ID de l'utilisateur qui approuve
            user_name: Nom de l'utilisateur qui approuve

        Returns:
            Formulaire approuvé ou None
        """
        # Récupérer le formulaire
        form = self.get_form(form_id)
        if not form:
            return None

        # Approuver le formulaire
        form.approve(user_id)

        # Signer le formulaire
        self.signature_manager.create_signature(
            entity_type="form",
            entity_id=form.id,
            signature_type=SignatureType.APPROVAL,
            signer_id=user_id,
            signer_name=user_name,
            signer_role="manager",
            data={"form_type": form.form_type.value}
        )

        # Sauvegarder les modifications
        approved_form = self.form_repository.update(form)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="form",
            entity_id=approved_form.id,
            change_type=ChangeType.APPROVE,
            user_id=user_id,
            user_name=user_name,
            changes={}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=approved_form.generated_by,
            notification_type=NotificationType.FORM_APPROVED,
            title=f"Formulaire {approved_form.form_number} approuvé",
            message=f"Votre formulaire {approved_form.form_type.value} a été approuvé",
            priority=NotificationPriority.HIGH,
            entity_type="form",
            entity_id=approved_form.id,
            action_url=f"/forms/{approved_form.id}"
        )

        return approved_form

    def reject_form(
        self,
        form_id: str,
        user_id: str,
        user_name: str,
        reason: str
    ) -> Optional[Form]:
        """
        Rejette un formulaire

        Args:
            form_id: ID du formulaire
            user_id: ID de l'utilisateur qui rejette
            user_name: Nom de l'utilisateur qui rejette
            reason: Raison du rejet

        Returns:
            Formulaire rejeté ou None
        """
        # Récupérer le formulaire
        form = self.get_form(form_id)
        if not form:
            return None

        # Rejeter le formulaire
        form.reject(user_id, reason)

        # Signer le formulaire
        self.signature_manager.create_signature(
            entity_type="form",
            entity_id=form.id,
            signature_type=SignatureType.REJECTION,
            signer_id=user_id,
            signer_name=user_name,
            signer_role="manager",
            data={"form_type": form.form_type.value, "reason": reason}
        )

        # Sauvegarder les modifications
        rejected_form = self.form_repository.update(form)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="form",
            entity_id=rejected_form.id,
            change_type=ChangeType.REJECT,
            user_id=user_id,
            user_name=user_name,
            changes={"rejection_reason": reason}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=rejected_form.generated_by,
            notification_type=NotificationType.FORM_REJECTED,
            title=f"Formulaire {rejected_form.form_number} rejeté",
            message=f"Votre formulaire {rejected_form.form_type.value} a été rejeté: {reason}",
            priority=NotificationPriority.HIGH,
            entity_type="form",
            entity_id=rejected_form.id,
            action_url=f"/forms/{rejected_form.id}"
        )

        return rejected_form

    def archive_form(
        self,
        form_id: str,
        user_id: str,
        user_name: str
    ) -> Optional[Form]:
        """
        Archive un formulaire

        Args:
            form_id: ID du formulaire
            user_id: ID de l'utilisateur qui archive
            user_name: Nom de l'utilisateur qui archive

        Returns:
            Formulaire archivé ou None
        """
        # Récupérer le formulaire
        form = self.get_form(form_id)
        if not form:
            return None

        # Archiver le formulaire
        form.archive()

        # Sauvegarder les modifications
        archived_form = self.form_repository.update(form)

        # Enregistrer le suivi des modifications
        self.change_tracker.track_change(
            entity_type="form",
            entity_id=archived_form.id,
            change_type=ChangeType.ARCHIVE,
            user_id=user_id,
            user_name=user_name,
            changes={}
        )

        # Envoyer une notification
        self.notification_engine.send_notification(
            user_id=archived_form.generated_by,
            notification_type=NotificationType.FORM_GENERATED,
            title=f"Formulaire {archived_form.form_number} archivé",
            message=f"Le formulaire {archived_form.form_type.value} a été archivé",
            priority=NotificationPriority.NORMAL,
            entity_type="form",
            entity_id=archived_form.id,
            action_url=f"/forms/{archived_form.id}"
        )

        return archived_form

    def get_form_statistics(
        self,
        company_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques des formulaires

        Args:
            company_id: ID de l'entreprise
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)

        Returns:
            Dictionnaire avec les statistiques
        """
        return self.form_repository.get_statistics(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date
        )

    def get_recent_forms(
        self,
        company_id: str,
        days: int = 30,
        limit: int = 10
    ) -> List[Form]:
        """
        Récupère les formulaires récents

        Args:
            company_id: ID de l'entreprise
            days: Nombre de jours à considérer
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires récents
        """
        return self.form_repository.get_recent_forms(
            company_id=company_id,
            days=days,
            limit=limit
        )

    def get_forms_needing_action(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
        """
        Récupère les formulaires nécessitant une action

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires nécessitant une action
        """
        return self.form_repository.get_forms_needing_action(
            company_id=company_id,
            skip=skip,
            limit=limit
        )
