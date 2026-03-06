
"""
Routes API pour le workflow
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from backend.workflow.approval_engine import ApprovalEngine, ApprovalLevel
from backend.workflow.validation_pipeline import ValidationPipeline, ValidationResult
from backend.workflow.change_tracker import ChangeTracker, ChangeType
from backend.workflow.notification_engine import NotificationEngine, NotificationType, NotificationPriority
from backend.workflow.signature_manager import SignatureManager, SignatureType
from backend.auth.middleware import get_current_user, require_permissions
from backend.auth.models import Permission

# Créer le routeur
router = APIRouter(prefix="/api/workflow", tags=["Workflow"])

# Initialisation des moteurs
approval_engine = ApprovalEngine()
validation_pipeline = ValidationPipeline()
change_tracker = ChangeTracker()
notification_engine = NotificationEngine()
signature_manager = SignatureManager()

# Modèles de données
class ApprovalRequest(BaseModel):
    """Modèle de demande d'approbation"""
    entity_type: str
    entity_id: str
    required_levels: List[ApprovalLevel] = [ApprovalLevel.LEVEL_1]
    comment: Optional[str] = None

class ValidationRequest(BaseModel):
    """Modèle de demande de validation"""
    entity_type: str
    entity_id: str
    data: dict

class NotificationRequest(BaseModel):
    """Modèle de demande de notification"""
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    action_url: Optional[str] = None
    data: Optional[dict] = None

class SignatureRequest(BaseModel):
    """Modèle de demande de signature"""
    entity_type: str
    entity_id: str
    signature_type: SignatureType
    data: Optional[dict] = None

@router.post("/approvals")
async def create_approval_workflow(
    request: ApprovalRequest,
    current_user = Depends(get_current_user)
):
    """
    Crée un workflow d'approbation

    - **entity_type**: Type d'entité
    - **entity_id**: ID de l'entité
    - **required_levels**: Liste des niveaux d'approbation requis
    - **comment**: Commentaire optionnel

    Returns:
        Workflow d'approbation créé
    """
    try:
        workflow = approval_engine.create_workflow(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            requester_id=current_user.sub,
            requester_name=f"{current_user.first_name} {current_user.last_name}",
            required_levels=request.required_levels
        )

        # Envoyer une notification
        notification_engine.send_notification(
            user_id=current_user.sub,
            notification_type=NotificationType.WORKFLOW_APPROVAL_REQUIRED,
            title="Workflow d'approbation créé",
            message=f"Un workflow d'approbation a été créé pour {request.entity_type} {request.entity_id}",
            priority=NotificationPriority.NORMAL,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            action_url=f"/workflow/approvals/{workflow.id}"
        )

        return {
            "workflow_id": workflow.id,
            "status": "created",
            "required_levels": [level.value for level in request.required_levels],
            "current_level": request.required_levels[0].value if request.required_levels else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du workflow: {str(e)}"
        )

@router.get("/approvals/{workflow_id}")
async def get_approval_workflow(
    workflow_id: str,
    current_user = Depends(get_current_user)
):
    """
    Récupère un workflow d'approbation

    - **workflow_id**: ID du workflow

    Returns:
        Workflow d'approbation
    """
    try:
        workflow = approval_engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow non trouvé"
            )

        return workflow.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du workflow: {str(e)}"
        )

@router.post("/approvals/{workflow_id}/approve")
async def approve_workflow_step(
    workflow_id: str,
    comment: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Approuve une étape d'un workflow

    - **workflow_id**: ID du workflow
    - **comment**: Commentaire de l'approbateur

    Returns:
        Workflow mis à jour
    """
    try:
        approval_engine.approve_step(workflow_id, current_user.sub, comment)

        # Récupérer le workflow mis à jour
        workflow = approval_engine.get_workflow(workflow_id)

        # Envoyer une notification
        notification_engine.send_notification(
            user_id=workflow.requester_id,
            notification_type=NotificationType.WORKFLOW_APPROVED,
            title="Étape approuvée",
            message=f"Votre workflow pour {workflow.entity_type} {workflow.entity_id} a été approuvé",
            priority=NotificationPriority.NORMAL,
            entity_type=workflow.entity_type,
            entity_id=workflow.entity_id,
            action_url=f"/workflow/approvals/{workflow.id}"
        )

        return {
            "workflow_id": workflow.id,
            "status": workflow.status.value,
            "current_level": workflow.required_levels[workflow.current_level_index].value if workflow.current_level_index < len(workflow.required_levels) else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'approbation: {str(e)}"
        )

@router.post("/approvals/{workflow_id}/reject")
async def reject_workflow_step(
    workflow_id: str,
    reason: str,
    current_user = Depends(get_current_user)
):
    """
    Rejette une étape d'un workflow

    - **workflow_id**: ID du workflow
    - **reason**: Raison du rejet

    Returns:
        Workflow mis à jour
    """
    try:
        approval_engine.reject_step(workflow_id, current_user.sub, reason)

        # Récupérer le workflow mis à jour
        workflow = approval_engine.get_workflow(workflow_id)

        # Envoyer une notification
        notification_engine.send_notification(
            user_id=workflow.requester_id,
            notification_type=NotificationType.WORKFLOW_REJECTED,
            title="Étape rejetée",
            message=f"Votre workflow pour {workflow.entity_type} {workflow.entity_id} a été rejeté: {reason}",
            priority=NotificationPriority.HIGH,
            entity_type=workflow.entity_type,
            entity_id=workflow.entity_id,
            action_url=f"/workflow/approvals/{workflow.id}"
        )

        return {
            "workflow_id": workflow.id,
            "status": workflow.status.value,
            "rejection_reason": reason
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du rejet: {str(e)}"
        )

@router.post("/validate")
async def validate_entity(
    request: ValidationRequest,
    current_user = Depends(get_current_user)
):
    """
    Valide une entité avec le pipeline de validation

    - **entity_type**: Type d'entité
    - **entity_id**: ID de l'entité
    - **data**: Données à valider

    Returns:
        Résultats de validation
    """
    try:
        validation_results = validation_pipeline.validate(request.data)

        # Enregistrer les résultats dans le suivi des modifications
        for result in validation_results:
            if not result.is_passed:
                change_tracker.track_change(
                    entity_type=request.entity_type,
                    entity_id=request.entity_id,
                    change_type=ChangeType.UPDATE,
                    user_id=current_user.sub,
                    user_name=f"{current_user.first_name} {current_user.last_name}",
                    changes={
                        "validation_rule": result.rule_id,
                        "validation_message": result.message,
                        "validation_severity": result.severity.value
                    }
                )

        return {
            "entity_type": request.entity_type,
            "entity_id": request.entity_id,
            "validation_results": [result.to_dict() for result in validation_results],
            "total_errors": len([r for r in validation_results if not r.is_passed]),
            "critical_errors": len([r for r in validation_results if not r.is_passed and r.severity.value in ["error", "critical"]])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la validation: {str(e)}"
        )

@router.post("/notifications/send")
async def send_notification(
    request: NotificationRequest,
    current_user = Depends(require_permissions(Permission.SYSTEM_ADMIN))
):
    """
    Envoie une notification à un utilisateur

    - **user_id**: ID de l'utilisateur destinataire
    - **notification_type**: Type de notification
    - **title**: Titre de la notification
    - **message**: Message de la notification
    - **priority**: Priorité de la notification
    - **entity_type**: Type d'entité concernée
    - **entity_id**: ID de l'entité concernée
    - **action_url**: URL pour l'action liée
    - **data**: Données supplémentaires

    Returns:
        Notification créée
    """
    try:
        notification = notification_engine.send_notification(
            user_id=request.user_id,
            notification_type=request.notification_type,
            title=request.title,
            message=request.message,
            priority=request.priority,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            action_url=request.action_url,
            data=request.data
        )

        return {
            "notification_id": notification.id,
            "status": "sent",
            "user_id": request.user_id,
            "type": request.notification_type.value
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'envoi de la notification: {str(e)}"
        )

@router.get("/notifications/{user_id}")
async def get_user_notifications(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """
    Récupère les notifications d'un utilisateur

    - **user_id**: ID de l'utilisateur
    - **status**: Statut des notifications (optionnel)
    - **limit**: Nombre maximum de notifications à retourner

    Returns:
        Liste des notifications
    """
    try:
        notifications = notification_engine.get_user_notifications(
            user_id=user_id,
            status=status,
            limit=limit
        )

        return {
            "user_id": user_id,
            "notifications": [n.to_dict() for n in notifications],
            "total_count": len(notifications)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des notifications: {str(e)}"
        )

@router.post("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """
    Marque une notification comme lue

    - **notification_id**: ID de la notification

    Returns:
        Notification mise à jour
    """
    try:
        notification_engine.mark_as_read(notification_id)

        return {
            "notification_id": notification_id,
            "status": "marked_as_read"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du marquage de la notification: {str(e)}"
        )

@router.post("/signatures")
async def create_signature(
    request: SignatureRequest,
    current_user = Depends(get_current_user)
):
    """
    Crée une signature numérique

    - **entity_type**: Type d'entité
    - **entity_id**: ID de l'entité
    - **signature_type**: Type de signature
    - **data**: Données supplémentaires

    Returns:
        Signature créée
    """
    try:
        signature = signature_manager.create_signature(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            signature_type=request.signature_type,
            signer_id=current_user.sub,
            signer_name=f"{current_user.first_name} {current_user.last_name}",
            signer_role=current_user.role.value,
            data=request.data
        )

        # Enregistrer dans le suivi des modifications
        change_tracker.track_change(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            change_type=ChangeType.UPDATE,
            user_id=current_user.sub,
            user_name=f"{current_user.first_name} {current_user.last_name}",
            changes={
                "signature_type": request.signature_type.value,
                "signature_id": signature.id
            }
        )

        return {
            "signature_id": signature.id,
            "entity_type": request.entity_type,
            "entity_id": request.entity_id,
            "signature_type": request.signature_type.value,
            "created_at": signature.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la signature: {str(e)}"
        )

@router.get("/signatures/{entity_type}/{entity_id}")
async def get_entity_signatures(
    entity_type: str,
    entity_id: str,
    signature_type: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Récupère les signatures d'une entité

    - **entity_type**: Type d'entité
    - **entity_id**: ID de l'entité
    - **signature_type**: Type de signature (optionnel)

    Returns:
        Liste des signatures
    """
    try:
        sig_type = SignatureType(signature_type) if signature_type else None
        signatures = signature_manager.get_entity_signatures(
            entity_type=entity_type,
            entity_id=entity_id,
            signature_type=sig_type
        )

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "signatures": [s.to_dict() for s in signatures],
            "total_count": len(signatures)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des signatures: {str(e)}"
        )
