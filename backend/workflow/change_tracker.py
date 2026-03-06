
"""
Module de suivi des modifications pour le versioning
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import json
import uuid

class ChangeType(str, Enum):
    """Types de modifications"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    SUBMIT = "submit"
    ARCHIVE = "archive"
    RESTORE = "restore"

class Change:
    """Modification d'une entité"""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        change_type: ChangeType,
        user_id: str,
        user_name: str,
        changes: Dict[str, Any],
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialise une modification

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            change_type: Type de modification
            user_id: ID de l'utilisateur
            user_name: Nom de l'utilisateur
            changes: Détail des modifications
            previous_values: Valeurs précédentes
            new_values: Nouvelles valeurs
            timestamp: Timestamp de la modification
        """
        self.id = str(uuid.uuid4())
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.change_type = change_type
        self.user_id = user_id
        self.user_name = user_name
        self.changes = changes
        self.previous_values = previous_values or {}
        self.new_values = new_values or {}
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la modification en dictionnaire

        Returns:
            Dictionnaire représentant la modification
        """
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "change_type": self.change_type.value,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "changes": self.changes,
            "previous_values": self.previous_values,
            "new_values": self.new_values,
            "timestamp": self.timestamp.isoformat()
        }

class ChangeTracker:
    """Suivi des modifications"""

    def __init__(self):
        """Initialise le suivi des modifications"""
        self.changes: Dict[str, List[Change]] = {}

    def track_change(
        self,
        entity_type: str,
        entity_id: str,
        change_type: ChangeType,
        user_id: str,
        user_name: str,
        changes: Dict[str, Any],
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> Change:
        """
        Enregistre une modification

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            change_type: Type de modification
            user_id: ID de l'utilisateur
            user_name: Nom de l'utilisateur
            changes: Détail des modifications
            previous_values: Valeurs précédentes
            new_values: Nouvelles valeurs

        Returns:
            Modification enregistrée
        """
        change = Change(
            entity_type=entity_type,
            entity_id=entity_id,
            change_type=change_type,
            user_id=user_id,
            user_name=user_name,
            changes=changes,
            previous_values=previous_values,
            new_values=new_values
        )

        # Ajouter la modification à l'historique de l'entité
        entity_key = f"{entity_type}:{entity_id}"
        if entity_key not in self.changes:
            self.changes[entity_key] = []

        self.changes[entity_key].append(change)
        return change

    def get_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: Optional[int] = None
    ) -> List[Change]:
        """
        Récupère l'historique des modifications d'une entité

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            limit: Nombre maximum de modifications à retourner

        Returns:
            Liste des modifications
        """
        entity_key = f"{entity_type}:{entity_id}"
        changes = self.changes.get(entity_key, [])

        # Trier par timestamp décroissant
        changes = sorted(changes, key=lambda c: c.timestamp, reverse=True)

        # Appliquer la limite si spécifiée
        if limit and len(changes) > limit:
            changes = changes[:limit]

        return changes

    def get_latest_change(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[Change]:
        """
        Récupère la modification la plus récente d'une entité

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité

        Returns:
            Modification la plus récente ou None
        """
        history = self.get_history(entity_type, entity_id, limit=1)
        return history[0] if history else None

    def get_changes_by_type(
        self,
        entity_type: str,
        entity_id: str,
        change_type: ChangeType,
        limit: Optional[int] = None
    ) -> List[Change]:
        """
        Récupère les modifications d'un type spécifique pour une entité

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            change_type: Type de modification
            limit: Nombre maximum de modifications à retourner

        Returns:
            Liste des modifications du type spécifié
        """
        history = self.get_history(entity_type, entity_id)
        filtered = [c for c in history if c.change_type == change_type]

        # Appliquer la limite si spécifiée
        if limit and len(filtered) > limit:
            filtered = filtered[:limit]

        return filtered

    def get_changes_by_user(
        self,
        user_id: str,
        entity_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Change]:
        """
        Récupère les modifications effectuées par un utilisateur

        Args:
            user_id: ID de l'utilisateur
            entity_type: Type d'entité (optionnel)
            limit: Nombre maximum de modifications à retourner

        Returns:
            Liste des modifications
        """
        all_changes = []

        for entity_key, changes in self.changes.items():
            key_entity_type = entity_key.split(":")[0]

            # Filtrer par type d'entité si spécifié
            if entity_type and key_entity_type != entity_type:
                continue

            # Filtrer par utilisateur
            user_changes = [c for c in changes if c.user_id == user_id]
            all_changes.extend(user_changes)

        # Trier par timestamp décroissant
        all_changes = sorted(all_changes, key=lambda c: c.timestamp, reverse=True)

        # Appliquer la limite si spécifiée
        if limit and len(all_changes) > limit:
            all_changes = all_changes[:limit]

        return all_changes

    def get_changes_between_dates(
        self,
        start_date: datetime,
        end_date: datetime,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> List[Change]:
        """
        Récupère les modifications entre deux dates

        Args:
            start_date: Date de début
            end_date: Date de fin
            entity_type: Type d'entité (optionnel)
            entity_id: ID de l'entité (optionnel)

        Returns:
            Liste des modifications
        """
        filtered_changes = []

        for entity_key, changes in self.changes.items():
            key_entity_type, key_entity_id = entity_key.split(":")

            # Filtrer par type d'entité si spécifié
            if entity_type and key_entity_type != entity_type:
                continue

            # Filtrer par ID d'entité si spécifié
            if entity_id and key_entity_id != entity_id:
                continue

            # Filtrer par date
            date_filtered = [
                c for c in changes
                if start_date <= c.timestamp <= end_date
            ]
            filtered_changes.extend(date_filtered)

        # Trier par timestamp décroissant
        filtered_changes = sorted(filtered_changes, key=lambda c: c.timestamp, reverse=True)

        return filtered_changes

    def export_history(
        self,
        entity_type: str,
        entity_id: str,
        format: str = "json"
    ) -> str:
        """
        Exporte l'historique des modifications d'une entité

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            format: Format d'export (json, csv)

        Returns:
            Données exportées
        """
        history = self.get_history(entity_type, entity_id)

        if format == "json":
            return json.dumps([c.to_dict() for c in history], indent=2)
        elif format == "csv":
            # Créer un CSV simple
            lines = ["id,entity_type,entity_id,change_type,user_id,user_name,timestamp"]

            for change in history:
                lines.append(
                    f"{change.id},{change.entity_type},{change.entity_id},"
                    f"{change.change_type.value},{change.user_id},{change.user_name},"
                    f"{change.timestamp.isoformat()}"
                )

            return "
".join(lines)
        else:
            raise ValueError(f"Format non supporté: {format}")

# Instance globale du suivi des modifications
change_tracker = ChangeTracker()
