
"""
Module de notifications internes pour le workflow
"""

from typing import List, Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

class NotificationType(str, Enum):
    """Types de notifications"""
    INVOICE_UPLOADED = "invoice_uploaded"
    INVOICE_PROCESSED = "invoice_processed"
    INVOICE_APPROVED = "invoice_approved"
    INVOICE_REJECTED = "invoice_rejected"
    VAT_CLAIM_SUBMITTED = "vat_claim_submitted"
    VAT_CLAIM_APPROVED = "vat_claim_approved"
    VAT_CLAIM_REJECTED = "vat_claim_rejected"
    FORM_GENERATED = "form_generated"
    FORM_SUBMITTED = "form_submitted"
    FORM_APPROVED = "form_approved"
    FORM_REJECTED = "form_rejected"
    WORKFLOW_APPROVAL_REQUIRED = "workflow_approval_required"
    WORKFLOW_APPROVED = "workflow_approved"
    WORKFLOW_REJECTED = "workflow_rejected"
    SYSTEM_ALERT = "system_alert"

class NotificationPriority(str, Enum):
    """Priorités des notifications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(str, Enum):
    """Statuts des notifications"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class Notification:
    """Notification"""

    def __init__(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise une notification

        Args:
            user_id: ID de l'utilisateur destinataire
            notification_type: Type de notification
            title: Titre de la notification
            message: Message de la notification
            priority: Priorité de la notification
            entity_type: Type d'entité concernée
            entity_id: ID de l'entité concernée
            action_url: URL pour l'action liée
            data: Données supplémentaires
        """
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.type = notification_type
        self.title = title
        self.message = message
        self.priority = priority
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.action_url = action_url
        self.data = data or {}
        self.status = NotificationStatus.UNREAD
        self.created_at = datetime.utcnow()
        self.read_at: Optional[datetime] = None
        self.archived_at: Optional[datetime] = None

    def mark_as_read(self) -> None:
        """Marque la notification comme lue"""
        self.status = NotificationStatus.READ
        self.read_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive la notification"""
        self.status = NotificationStatus.ARCHIVED
        self.archived_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la notification en dictionnaire

        Returns:
            Dictionnaire représentant la notification
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action_url": self.action_url,
            "data": self.data,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None
        }

class NotificationEngine:
    """Moteur de notifications"""

    def __init__(self):
        """Initialise le moteur de notifications"""
        self.notifications: Dict[str, List[Notification]] = {}
        self.handlers: Dict[NotificationType, List[Callable[[Notification], None]]] = {}

    def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Envoie une notification à un utilisateur

        Args:
            user_id: ID de l'utilisateur destinataire
            notification_type: Type de notification
            title: Titre de la notification
            message: Message de la notification
            priority: Priorité de la notification
            entity_type: Type d'entité concernée
            entity_id: ID de l'entité concernée
            action_url: URL pour l'action liée
            data: Données supplémentaires

        Returns:
            Notification créée
        """
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            entity_type=entity_type,
            entity_id=entity_id,
            action_url=action_url,
            data=data
        )

        # Ajouter la notification à l'utilisateur
        if user_id not in self.notifications:
            self.notifications[user_id] = []

        self.notifications[user_id].append(notification)

        # Appeler les handlers enregistrés pour ce type de notification
        if notification_type in self.handlers:
            for handler in self.handlers[notification_type]:
                try:
                    handler(notification)
                except Exception as e:
                    print(f"Erreur dans le handler de notification: {e}")

        return notification

    def send_bulk_notification(
        self,
        user_ids: List[str],
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        """
        Envoie une notification à plusieurs utilisateurs

        Args:
            user_ids: Liste des IDs des utilisateurs destinataires
            notification_type: Type de notification
            title: Titre de la notification
            message: Message de la notification
            priority: Priorité de la notification
            entity_type: Type d'entité concernée
            entity_id: ID de l'entité concernée
            action_url: URL pour l'action liée
            data: Données supplémentaires

        Returns:
            Liste des notifications créées
        """
        notifications = []

        for user_id in user_ids:
            notification = self.send_notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                entity_type=entity_type,
                entity_id=entity_id,
                action_url=action_url,
                data=data
            )
            notifications.append(notification)

        return notifications

    def get_user_notifications(
        self,
        user_id: str,
        status: Optional[NotificationStatus] = None,
        limit: Optional[int] = None
    ) -> List[Notification]:
        """
        Récupère les notifications d'un utilisateur

        Args:
            user_id: ID de l'utilisateur
            status: Statut des notifications à filtrer
            limit: Nombre maximum de notifications à retourner

        Returns:
            Liste des notifications
        """
        user_notifications = self.notifications.get(user_id, [])

        # Filtrer par statut si spécifié
        if status:
            user_notifications = [n for n in user_notifications if n.status == status]

        # Trier par date décroissante
        user_notifications = sorted(user_notifications, key=lambda n: n.created_at, reverse=True)

        # Appliquer la limite si spécifiée
        if limit and len(user_notifications) > limit:
            user_notifications = user_notifications[:limit]

        return user_notifications

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Récupère une notification par son ID

        Args:
            notification_id: ID de la notification

        Returns:
            Notification ou None si non trouvée
        """
        for user_notifications in self.notifications.values():
            for notification in user_notifications:
                if notification.id == notification_id:
                    return notification

        return None

    def mark_as_read(self, notification_id: str) -> None:
        """
        Marque une notification comme lue

        Args:
            notification_id: ID de la notification
        """
        notification = self.get_notification(notification_id)
        if notification:
            notification.mark_as_read()

    def mark_all_as_read(self, user_id: str) -> None:
        """
        Marque toutes les notifications d'un utilisateur comme lues

        Args:
            user_id: ID de l'utilisateur
        """
        if user_id in self.notifications:
            for notification in self.notifications[user_id]:
                notification.mark_as_read()

    def archive_notification(self, notification_id: str) -> None:
        """
        Archive une notification

        Args:
            notification_id: ID de la notification
        """
        notification = self.get_notification(notification_id)
        if notification:
            notification.archive()

    def archive_old_notifications(
        self,
        user_id: str,
        days_old: int = 30
    ) -> int:
        """
        Archive les anciennes notifications d'un utilisateur

        Args:
            user_id: ID de l'utilisateur
            days_old: Nombre de jours

        Returns:
            Nombre de notifications archivées
        """
        if user_id not in self.notifications:
            return 0

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        archived_count = 0

        for notification in self.notifications[user_id]:
            if notification.created_at < cutoff_date and notification.status != NotificationStatus.ARCHIVED:
                notification.archive()
                archived_count += 1

        return archived_count

    def register_handler(
        self,
        notification_type: NotificationType,
        handler: Callable[[Notification], None]
    ) -> None:
        """
        Enregistre un handler pour un type de notification

        Args:
            notification_type: Type de notification
            handler: Fonction de handler
        """
        if notification_type not in self.handlers:
            self.handlers[notification_type] = []

        self.handlers[notification_type].append(handler)

    def get_unread_count(self, user_id: str) -> int:
        """
        Récupère le nombre de notifications non lues d'un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Nombre de notifications non lues
        """
        if user_id not in self.notifications:
            return 0

        return sum(1 for n in self.notifications[user_id] if n.status == NotificationStatus.UNREAD)

# Instance globale du moteur de notifications
notification_engine = NotificationEngine()
