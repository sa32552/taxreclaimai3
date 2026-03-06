
"""
Moteur d'approbation multi-niveaux
"""

from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
from enum import Enum
import uuid

class ApprovalStatus(str, Enum):
    """Statuts d'approbation"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class ApprovalLevel(str, Enum):
    """Niveaux d'approbation"""
    LEVEL_1 = "level_1"  # Premier niveau (manager)
    LEVEL_2 = "level_2"  # Deuxième niveau (director)
    LEVEL_3 = "level_3"  # Troisième niveau (VP)
    LEVEL_4 = "level_4"  # Quatrième niveau (C-level)

class ApprovalStep:
    """Étape d'approbation"""

    def __init__(
        self,
        level: ApprovalLevel,
        approver_id: str,
        approver_name: str,
        approver_role: str,
        status: ApprovalStatus = ApprovalStatus.PENDING,
        approved_at: Optional[datetime] = None,
        comment: Optional[str] = None
    ):
        """
        Initialise une étape d'approbation

        Args:
            level: Niveau d'approbation
            approver_id: ID de l'approbateur
            approver_name: Nom de l'approbateur
            approver_role: Rôle de l'approbateur
            status: Statut de l'approbation
            approved_at: Date d'approbation
            comment: Commentaire de l'approbateur
        """
        self.id = str(uuid.uuid4())
        self.level = level
        self.approver_id = approver_id
        self.approver_name = approver_name
        self.approver_role = approver_role
        self.status = status
        self.approved_at = approved_at
        self.comment = comment

    def approve(self, comment: Optional[str] = None) -> None:
        """
        Approuve cette étape

        Args:
            comment: Commentaire de l'approbateur
        """
        if self.status != ApprovalStatus.PENDING:
            raise ValueError(f"Cette étape a déjà été {self.status.value}")

        self.status = ApprovalStatus.APPROVED
        self.approved_at = datetime.utcnow()
        self.comment = comment

    def reject(self, comment: str) -> None:
        """
        Rejette cette étape

        Args:
            comment: Raison du rejet
        """
        if self.status != ApprovalStatus.PENDING:
            raise ValueError(f"Cette étape a déjà été {self.status.value}")

        self.status = ApprovalStatus.REJECTED
        self.approved_at = datetime.utcnow()
        self.comment = comment

    def cancel(self) -> None:
        """Annule cette étape"""
        if self.status != ApprovalStatus.PENDING:
            raise ValueError(f"Cette étape a déjà été {self.status.value}")

        self.status = ApprovalStatus.CANCELLED

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'étape en dictionnaire

        Returns:
            Dictionnaire représentant l'étape
        """
        return {
            "id": self.id,
            "level": self.level.value,
            "approver_id": self.approver_id,
            "approver_name": self.approver_name,
            "approver_role": self.approver_role,
            "status": self.status.value,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "comment": self.comment
        }

class ApprovalWorkflow:
    """Workflow d'approbation multi-niveaux"""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        requester_id: str,
        requester_name: str,
        required_levels: List[ApprovalLevel] = None
    ):
        """
        Initialise un workflow d'approbation

        Args:
            entity_type: Type d'entité (invoice, vat_claim, form, etc.)
            entity_id: ID de l'entité
            requester_id: ID du demandeur
            requester_name: Nom du demandeur
            required_levels: Liste des niveaux d'approbation requis
        """
        self.id = str(uuid.uuid4())
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.requester_id = requester_id
        self.requester_name = requester_name
        self.created_at = datetime.utcnow()
        self.status = ApprovalStatus.PENDING
        self.steps: List[ApprovalStep] = []
        self.required_levels = required_levels or [ApprovalLevel.LEVEL_1]
        self.current_level_index = 0
        self.completed_at: Optional[datetime] = None
        self.comments: List[Dict[str, Any]] = []

    def add_step(
        self,
        level: ApprovalLevel,
        approver_id: str,
        approver_name: str,
        approver_role: str
    ) -> ApprovalStep:
        """
        Ajoute une étape d'approbation

        Args:
            level: Niveau d'approbation
            approver_id: ID de l'approbateur
            approver_name: Nom de l'approbateur
            approver_role: Rôle de l'approbateur

        Returns:
            Étape d'approbation créée
        """
        step = ApprovalStep(
            level=level,
            approver_id=approver_id,
            approver_name=approver_name,
            approver_role=approver_role
        )
        self.steps.append(step)
        return step

    def get_current_step(self) -> Optional[ApprovalStep]:
        """
        Récupère l'étape actuelle

        Returns:
            Étape actuelle ou None si le workflow est terminé
        """
        if self.status != ApprovalStatus.PENDING:
            return None

        if self.current_level_index < len(self.steps):
            return self.steps[self.current_level_index]

        return None

    def approve_step(self, approver_id: str, comment: Optional[str] = None) -> None:
        """
        Approuve l'étape actuelle

        Args:
            approver_id: ID de l'approbateur
            comment: Commentaire de l'approbateur
        """
        current_step = self.get_current_step()
        if not current_step:
            raise ValueError("Aucune étape en attente d'approbation")

        if current_step.approver_id != approver_id:
            raise ValueError("Vous n'êtes pas autorisé à approuver cette étape")

        current_step.approve(comment)
        self.current_level_index += 1

        # Vérifier si toutes les étapes sont complétées
        if self.current_level_index >= len(self.steps):
            self.status = ApprovalStatus.APPROVED
            self.completed_at = datetime.utcnow()

        # Ajouter le commentaire
        if comment:
            self.comments.append({
                "step_id": current_step.id,
                "level": current_step.level.value,
                "approver_id": approver_id,
                "comment": comment,
                "timestamp": datetime.utcnow().isoformat()
            })

    def reject_step(self, approver_id: str, comment: str) -> None:
        """
        Rejette l'étape actuelle

        Args:
            approver_id: ID de l'approbateur
            comment: Raison du rejet
        """
        current_step = self.get_current_step()
        if not current_step:
            raise ValueError("Aucune étape en attente d'approbation")

        if current_step.approver_id != approver_id:
            raise ValueError("Vous n'êtes pas autorisé à rejeter cette étape")

        current_step.reject(comment)
        self.status = ApprovalStatus.REJECTED
        self.completed_at = datetime.utcnow()

        # Ajouter le commentaire
        self.comments.append({
            "step_id": current_step.id,
            "level": current_step.level.value,
            "approver_id": approver_id,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat()
        })

    def cancel(self) -> None:
        """Annule le workflow"""
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("Seuls les workflows en attente peuvent être annulés")

        self.status = ApprovalStatus.CANCELLED
        self.completed_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le workflow en dictionnaire

        Returns:
            Dictionnaire représentant le workflow
        """
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "requester_id": self.requester_id,
            "requester_name": self.requester_name,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "current_level": self.required_levels[self.current_level_index].value if self.current_level_index < len(self.required_levels) else None,
            "required_levels": [level.value for level in self.required_levels],
            "steps": [step.to_dict() for step in self.steps],
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "comments": self.comments
        }

class ApprovalEngine:
    """Moteur d'approbation"""

    def __init__(self):
        """Initialise le moteur d'approbation"""
        self.workflows: Dict[str, ApprovalWorkflow] = {}

    def create_workflow(
        self,
        entity_type: str,
        entity_id: str,
        requester_id: str,
        requester_name: str,
        required_levels: List[ApprovalLevel] = None
    ) -> ApprovalWorkflow:
        """
        Crée un nouveau workflow d'approbation

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            requester_id: ID du demandeur
            requester_name: Nom du demandeur
            required_levels: Liste des niveaux d'approbation requis

        Returns:
            Workflow d'approbation créé
        """
        workflow = ApprovalWorkflow(
            entity_type=entity_type,
            entity_id=entity_id,
            requester_id=requester_id,
            requester_name=requester_name,
            required_levels=required_levels
        )

        self.workflows[workflow.id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[ApprovalWorkflow]:
        """
        Récupère un workflow par son ID

        Args:
            workflow_id: ID du workflow

        Returns:
            Workflow ou None si non trouvé
        """
        return self.workflows.get(workflow_id)

    def get_workflow_by_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[ApprovalWorkflow]:
        """
        Récupère un workflow par entité

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité

        Returns:
            Workflow ou None si non trouvé
        """
        for workflow in self.workflows.values():
            if workflow.entity_type == entity_type and workflow.entity_id == entity_id:
                return workflow

        return None

    def approve_step(
        self,
        workflow_id: str,
        approver_id: str,
        comment: Optional[str] = None
    ) -> None:
        """
        Approuve une étape d'un workflow

        Args:
            workflow_id: ID du workflow
            approver_id: ID de l'approbateur
            comment: Commentaire de l'approbateur
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError("Workflow non trouvé")

        workflow.approve_step(approver_id, comment)

    def reject_step(
        self,
        workflow_id: str,
        approver_id: str,
        comment: str
    ) -> None:
        """
        Rejette une étape d'un workflow

        Args:
            workflow_id: ID du workflow
            approver_id: ID de l'approbateur
            comment: Raison du rejet
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError("Workflow non trouvé")

        workflow.reject_step(approver_id, comment)

    def cancel_workflow(self, workflow_id: str) -> None:
        """
        Annule un workflow

        Args:
            workflow_id: ID du workflow
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError("Workflow non trouvé")

        workflow.cancel()

    def get_pending_workflows_for_user(
        self,
        user_id: str
    ) -> List[ApprovalWorkflow]:
        """
        Récupère les workflows en attente pour un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Liste des workflows en attente
        """
        pending_workflows = []

        for workflow in self.workflows.values():
            if workflow.status == ApprovalStatus.PENDING:
                current_step = workflow.get_current_step()
                if current_step and current_step.approver_id == user_id:
                    pending_workflows.append(workflow)

        return pending_workflows

    def get_completed_workflows_for_user(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[ApprovalWorkflow]:
        """
        Récupère les workflows complétés pour un utilisateur

        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum de résultats

        Returns:
            Liste des workflows complétés
        """
        completed_workflows = []

        for workflow in self.workflows.values():
            if workflow.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
                # Vérifier si l'utilisateur a participé au workflow
                user_participated = any(
                    step.approver_id == user_id
                    for step in workflow.steps
                )

                if user_participated:
                    completed_workflows.append(workflow)

        # Trier par date de complétion (plus récent en premier)
        completed_workflows.sort(
            key=lambda w: w.completed_at or datetime.min,
            reverse=True
        )

        return completed_workflows[:limit]

# Instance globale du moteur d'approbation
approval_engine = ApprovalEngine()
