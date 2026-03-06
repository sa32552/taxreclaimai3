
"""
Module d'escalade automatique pour le workflow
"""

from typing import List, Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

class EscalationLevel(str, Enum):
    """Niveaux d'escalade"""
    LEVEL_1 = "level_1"  # Premier niveau (manager)
    LEVEL_2 = "level_2"  # Deuxième niveau (director)
    LEVEL_3 = "level_3"  # Troisième niveau (VP)
    LEVEL_4 = "level_4"  # Quatrième niveau (C-level)

class EscalationStatus(str, Enum):
    """Statuts d'escalade"""
    PENDING = "pending"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"

class EscalationRule:
    """Règle d'escalade"""

    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        description: str,
        entity_type: str,
        escalation_levels: List[EscalationLevel],
        time_to_escalate: Dict[EscalationLevel, int],  # en heures
        escalation_action: Optional[Callable[[str, EscalationLevel], None]] = None
    ):
        """
        Initialise une règle d'escalade

        Args:
            rule_id: ID de la règle
            rule_name: Nom de la règle
            description: Description de la règle
            entity_type: Type d'entité
            escalation_levels: Liste des niveaux d'escalade
            time_to_escalate: Temps avant escalade par niveau (en heures)
            escalation_action: Action à exécuter lors de l'escalade
        """
        self.id = rule_id
        self.name = rule_name
        self.description = description
        self.entity_type = entity_type
        self.escalation_levels = escalation_levels
        self.time_to_escalate = time_to_escalate
        self.escalation_action = escalation_action

class Escalation:
    """Escalade"""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        current_level: EscalationLevel,
        escalated_from: Optional[EscalationLevel] = None,
        reason: Optional[str] = None,
        escalated_by: Optional[str] = None
    ):
        """
        Initialise une escalade

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            current_level: Niveau actuel
            escalated_from: Niveau précédent
            reason: Raison de l'escalade
            escalated_by: ID de l'utilisateur qui a escaladé
        """
        self.id = str(uuid.uuid4())
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.current_level = current_level
        self.escalated_from = escalated_from
        self.reason = reason
        self.escalated_by = escalated_by
        self.created_at = datetime.utcnow()
        self.status = EscalationStatus.ESCALATED
        self.resolved_at: Optional[datetime] = None
        self.resolved_by: Optional[str] = None

    def resolve(self, resolved_by: str) -> None:
        """
        Résout l'escalade

        Args:
            resolved_by: ID de l'utilisateur qui résout
        """
        if self.status != EscalationStatus.ESCALATED:
            raise ValueError("Seules les escalades en cours peuvent être résolues")

        self.status = EscalationStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = resolved_by

    def cancel(self) -> None:
        """Annule l'escalade"""
        if self.status != EscalationStatus.ESCALATED:
            raise ValueError("Seules les escalades en cours peuvent être annulées")

        self.status = EscalationStatus.CANCELLED

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'escalade en dictionnaire

        Returns:
            Dictionnaire représentant l'escalade
        """
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "current_level": self.current_level.value,
            "escalated_from": self.escalated_from.value if self.escalated_from else None,
            "reason": self.reason,
            "escalated_by": self.escalated_by,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by
        }

class EscalationEngine:
    """Moteur d'escalade automatique"""

    def __init__(self):
        """Initialise le moteur d'escalade"""
        self.rules: Dict[str, EscalationRule] = {}
        self.escalations: Dict[str, List[Escalation]] = {}
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Initialise les règles d'escalade par défaut"""
        # Règle d'escalade pour les factures en attente d'approbation
        self.add_rule(EscalationRule(
            rule_id="invoice_approval_escalation",
            rule_name="Escalade d'approbation de facture",
            description="Escalade automatique des factures en attente d'approbation",
            entity_type="invoice",
            escalation_levels=[
                EscalationLevel.LEVEL_1,
                EscalationLevel.LEVEL_2,
                EscalationLevel.LEVEL_3
            ],
            time_to_escalate={
                EscalationLevel.LEVEL_1: 24,  # 24 heures
                EscalationLevel.LEVEL_2: 48,  # 48 heures
                EscalationLevel.LEVEL_3: 72   # 72 heures
            }
        ))

        # Règle d'escalade pour les demandes de récupération TVA
        self.add_rule(EscalationRule(
            rule_id="vat_claim_escalation",
            rule_name="Escalade de demande de récupération TVA",
            description="Escalade automatique des demandes de récupération TVA en attente",
            entity_type="vat_claim",
            escalation_levels=[
                EscalationLevel.LEVEL_1,
                EscalationLevel.LEVEL_2,
                EscalationLevel.LEVEL_3
            ],
            time_to_escalate={
                EscalationLevel.LEVEL_1: 48,  # 48 heures
                EscalationLevel.LEVEL_2: 96,  # 96 heures
                EscalationLevel.LEVEL_3: 144  # 144 heures (6 jours)
            }
        ))

    def add_rule(self, rule: EscalationRule) -> None:
        """
        Ajoute une règle d'escalade

        Args:
            rule: Règle d'escalade
        """
        self.rules[rule.id] = rule

    def get_rule(self, rule_id: str) -> Optional[EscalationRule]:
        """
        Récupère une règle par son ID

        Args:
            rule_id: ID de la règle

        Returns:
            Règle ou None si non trouvée
        """
        return self.rules.get(rule_id)

    def create_escalation(
        self,
        entity_type: str,
        entity_id: str,
        current_level: EscalationLevel,
        escalated_from: Optional[EscalationLevel] = None,
        reason: Optional[str] = None,
        escalated_by: Optional[str] = None
    ) -> Escalation:
        """
        Crée une nouvelle escalade

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            current_level: Niveau actuel
            escalated_from: Niveau précédent
            reason: Raison de l'escalade
            escalated_by: ID de l'utilisateur qui a escaladé

        Returns:
            Escalade créée
        """
        escalation = Escalation(
            entity_type=entity_type,
            entity_id=entity_id,
            current_level=current_level,
            escalated_from=escalated_from,
            reason=reason,
            escalated_by=escalated_by
        )

        # Ajouter l'escalade à l'historique de l'entité
        entity_key = f"{entity_type}:{entity_id}"
        if entity_key not in self.escalations:
            self.escalations[entity_key] = []

        self.escalations[entity_key].append(escalation)
        return escalation

    def get_escalations(
        self,
        entity_type: str,
        entity_id: str,
        status: Optional[EscalationStatus] = None
    ) -> List[Escalation]:
        """
        Récupère les escalades d'une entité

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            status: Statut des escalades (optionnel)

        Returns:
            Liste des escalades
        """
        entity_key = f"{entity_type}:{entity_id}"
        escalations = self.escalations.get(entity_key, [])

        # Filtrer par statut si spécifié
        if status:
            escalations = [e for e in escalations if e.status == status]

        # Trier par date décroissante
        escalations = sorted(escalations, key=lambda e: e.created_at, reverse=True)

        return escalations

    def get_current_escalation(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[Escalation]:
        """
        Récupère l'escalade actuelle d'une entité

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité

        Returns:
            Escalade actuelle ou None
        """
        escalations = self.get_escalations(entity_type, entity_id, EscalationStatus.ESCALATED)
        return escalations[0] if escalations else None

    def resolve_escalation(
        self,
        escalation_id: str,
        resolved_by: str
    ) -> None:
        """
        Résout une escalade

        Args:
            escalation_id: ID de l'escalade
            resolved_by: ID de l'utilisateur qui résout
        """
        for entity_escalations in self.escalations.values():
            for escalation in entity_escalations:
                if escalation.id == escalation_id:
                    escalation.resolve(resolved_by)
                    return

        raise ValueError("Escalade non trouvée")

    def cancel_escalation(self, escalation_id: str) -> None:
        """
        Annule une escalade

        Args:
            escalation_id: ID de l'escalade
        """
        for entity_escalations in self.escalations.values():
            for escalation in entity_escalations:
                if escalation.id == escalation_id:
                    escalation.cancel()
                    return

        raise ValueError("Escalade non trouvée")

    def check_pending_escalations(self) -> List[Escalation]:
        """
        Vérifie les escalades en attente et les escalade si nécessaire

        Returns:
            Liste des escalades créées
        """
        new_escalations = []

        for entity_key, escalations in self.escalations.items():
            entity_type, entity_id = entity_key.split(":")

            # Trouver la règle applicable
            rule = None
            for r in self.rules.values():
                if r.entity_type == entity_type:
                    rule = r
                    break

            if not rule:
                continue

            # Trouver l'escalade actuelle
            current_escalation = None
            for escalation in escalations:
                if escalation.status == EscalationStatus.ESCALATED:
                    current_escalation = escalation
                    break

            if not current_escalation:
                continue

            # Vérifier si le temps d'escalade est atteint
            time_since_creation = datetime.utcnow() - current_escalation.created_at
            hours_since_creation = time_since_creation.total_seconds() / 3600

            # Trouver le niveau suivant
            current_level_index = rule.escalation_levels.index(current_escalation.current_level)

            if current_level_index < len(rule.escalation_levels) - 1:
                next_level = rule.escalation_levels[current_level_index + 1]
                time_to_escalate = rule.time_to_escalate.get(next_level, 24)

                if hours_since_creation >= time_to_escalate:
                    # Escalader au niveau suivant
                    new_escalation = self.create_escalation(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        current_level=next_level,
                        escalated_from=current_escalation.current_level,
                        reason=f"Escalade automatique après {hours_since_creation:.1f} heures",
                        escalated_by="system"
                    )

                    new_escalations.append(new_escalation)

                    # Exécuter l'action d'escalade si définie
                    if rule.escalation_action:
                        rule.escalation_action(entity_id, next_level)

        return new_escalations

# Instance globale du moteur d'escalade
escalation_engine = EscalationEngine()
