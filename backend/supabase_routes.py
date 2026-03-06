
"""
Routes API adaptées pour Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from backend.supabase_client import get_supabase_client
from backend.auth.supabase_auth import SupabaseAuthService
from backend.supabase_storage import storage_service
from backend.auth.models import UserResponse, Token
from backend.workflow.approval_engine import ApprovalEngine
from backend.workflow.validation_pipeline import ValidationPipeline
from backend.workflow.change_tracker import ChangeTracker
from backend.workflow.notification_engine import NotificationEngine
from backend.workflow.signature_manager import SignatureManager

# Créer le routeur
router = APIRouter(prefix="/api", tags=["API Supabase"])

# Configuration de sécurité
security = HTTPBearer(auto_error=False)

# Initialisation des services
auth_service = SupabaseAuthService()
approval_engine = ApprovalEngine()
validation_pipeline = ValidationPipeline()
change_tracker = ChangeTracker()
notification_engine = NotificationEngine()
signature_manager = SignatureManager()

# Modèles de données
class RegisterRequest(BaseModel):
    """Modèle de demande d'enregistrement"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "user"

class LoginRequest(BaseModel):
    """Modèle de demande de connexion"""
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    """Modèle de demande de rafraîchissement de token"""
    refresh_token: str

class InvoiceData(BaseModel):
    """Modèle de données de facture"""
    invoice_number: str
    date: str
    supplier: str
    country: str
    vat_number: Optional[str] = None
    amount_ht: float
    vat_amount: float
    total_amount: float
    currency: str = "EUR"
    language: Optional[str] = None

class VATClaimRequest(BaseModel):
    """Modèle de demande de récupération TVA"""
    target_country: str
    company_vat: str
    invoices: List[InvoiceData]

# Dépendance pour obtenir l'utilisateur actuel
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserResponse:
    """
    Récupère l'utilisateur actuel à partir du token

    Args:
        credentials: Credentials d'authentification

    Returns:
        Utilisateur actuel

    Raises:
        HTTPException: Si l'authentification échoue
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'utilisateur: {str(e)}"
        )

# Routes d'authentification
@router.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Enregistre un nouvel utilisateur

    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    - **first_name**: Prénom
    - **last_name**: Nom
    - **phone**: Numéro de téléphone (optionnel)
    - **role**: Rôle (défaut: user)
    """
    try:
        result = await auth_service.register(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            role=request.role
        )
        return {
            "message": "Utilisateur enregistré avec succès",
            "user": result["user"],
            "session": result["session"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )

@router.post("/auth/login", response_model=dict)
async def login(request: LoginRequest):
    """
    Authentifie un utilisateur

    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    """
    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password
        )
        return {
            "message": "Connexion réussie",
            "user": result["user"],
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la connexion: {str(e)}"
        )

@router.post("/auth/logout")
async def logout(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Déconnecte l'utilisateur actuel
    """
    try:
        # Dans une implémentation complète, on utiliserait le token
        return {"message": "Déconnexion réussie"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la déconnexion: {str(e)}"
        )

@router.post("/auth/refresh", response_model=dict)
async def refresh_token(request: RefreshTokenRequest):
    """
    Rafraîchit le token d'accès

    - **refresh_token**: Token de rafraîchissement
    """
    try:
        result = await auth_service.refresh_token(request.refresh_token)
        return {
            "message": "Token rafraîchi avec succès",
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "expires_in": result["expires_in"],
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du rafraîchissement: {str(e)}"
        )

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur actuel
    """
    return current_user

# Routes de factures
@router.post("/invoices/upload")
async def upload_invoice(
    files: List[UploadFile] = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Télécharge et traite des factures

    - **files**: Liste des fichiers PDF/JPG/PNG à traiter
    """
    try:
        # Télécharger les fichiers vers Supabase Storage
        upload_results = await storage_service.upload_batch(
            files=files,
            bucket="invoices",
            folder="uploads",
            user_id=current_user.id
        )

        # En production, on traiterait les fichiers avec OCR ici
        # Pour l'instant, on retourne les résultats de l'upload
        return {
            "message": f"{len(files)} facture(s) téléchargée(s) avec succès",
            "files": upload_results,
            "processed": False  # À implémenter avec OCR
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du téléchargement: {str(e)}"
        )

@router.post("/invoices/validate")
async def validate_invoice(
    invoice_data: InvoiceData,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Valide une facture avec le pipeline de validation

    - **invoice_data**: Données de la facture
    """
    try:
        # Valider les données
        validation_results = validation_pipeline.validate(invoice_data.dict())

        # Enregistrer dans Supabase
        supabase = get_supabase_client()

        invoice_record = supabase.table("invoices").insert({
            "invoice_number": invoice_data.invoice_number,
            "date": invoice_data.date,
            "supplier": invoice_data.supplier,
            "country": invoice_data.country,
            "vat_number": invoice_data.vat_number,
            "amount_ht": invoice_data.amount_ht,
            "vat_amount": invoice_data.vat_amount,
            "total_amount": invoice_data.total_amount,
            "currency": invoice_data.currency,
            "language": invoice_data.language,
            "status": "uploaded",
            "company_id": current_user.id,  # À adapter avec multi-tenancy
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

        return {
            "message": "Facture validée et enregistrée",
            "validation_results": [v.to_dict() for v in validation_results],
            "invoice_id": invoice_record.data[0]["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la validation: {str(e)}"
        )

# Routes de récupération TVA
@router.post("/vat-claims")
async def create_vat_claim(
    request: VATClaimRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Crée une demande de récupération TVA

    - **target_country**: Pays cible
    - **company_vat**: Numéro de TVA de l'entreprise
    - **invoices**: Liste des factures
    """
    try:
        # Calculer le montant total récupérable
        total_recoverable = sum(
            invoice.vat_amount * 0.8  # 80% récupérable en moyenne
            for invoice in request.invoices
        )

        # Créer la demande dans Supabase
        supabase = get_supabase_client()

        claim_record = supabase.table("vat_claims").insert({
            "target_country": request.target_country,
            "company_vat_number": request.company_vat,
            "period_start": datetime.utcnow().replace(day=1, hour=0, minute=0, second=0).isoformat(),
            "period_end": datetime.utcnow().replace(hour=23, minute=59, second=59).isoformat(),
            "total_recoverable": total_recoverable,
            "total_approved": 0.0,
            "total_rejected": 0.0,
            "status": "draft",
            "company_id": current_user.id,  # À adapter avec multi-tenancy
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

        claim_id = claim_record.data[0]["id"]

        # Créer un workflow d'approbation
        workflow = approval_engine.create_workflow(
            entity_type="vat_claim",
            entity_id=claim_id,
            requester_id=current_user.id,
            requester_name=f"{current_user.first_name} {current_user.last_name}",
            required_levels=["level_1", "level_2"]
        )

        # Envoyer une notification
        notification_engine.send_notification(
            user_id=current_user.id,
            notification_type="vat_claim_submitted",
            title="Demande de récupération TVA créée",
            message=f"Une demande de récupération TVA de {total_recoverable:.2f} EUR a été créée pour {request.target_country}",
            priority="normal",
            entity_type="vat_claim",
            entity_id=claim_id,
            action_url=f"/vat-claims/{claim_id}"
        )

        return {
            "message": "Demande de récupération TVA créée avec succès",
            "claim_id": claim_id,
            "total_recoverable": total_recoverable,
            "workflow_id": workflow.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la demande: {str(e)}"
        )

# Routes de dashboard
@router.get("/dashboard")
async def get_dashboard(current_user: UserResponse = Depends(get_current_user)):
    """
    Récupère les données du dashboard
    """
    try:
        supabase = get_supabase_client()

        # Récupérer les statistiques des factures
        invoices = supabase.table("invoices").select("*").eq("company_id", current_user.id).execute()

        # Récupérer les statistiques des demandes TVA
        vat_claims = supabase.table("vat_claims").select("*").eq("company_id", current_user.id).execute()

        # Calculer les KPIs
        total_invoices = len(invoices.data) if invoices.data else 0
        total_vat = sum(inv.get("vat_amount", 0) for inv in invoices.data) if invoices.data else 0
        total_recoverable = sum(claim.get("total_recoverable", 0) for claim in vat_claims.data) if vat_claims.data else 0

        return {
            "total_invoices": total_invoices,
            "total_vat": total_vat,
            "total_recoverable": total_recoverable,
            "total_claims": len(vat_claims.data) if vat_claims.data else 0,
            "roi": round(total_recoverable / (total_recoverable * 0.125), 2) if total_recoverable > 0 else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du dashboard: {str(e)}"
        )

# Routes de workflow
@router.get("/workflow/approvals/{workflow_id}")
async def get_approval_workflow(
    workflow_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Récupère un workflow d'approbation

    - **workflow_id**: ID du workflow
    """
    try:
        workflow = approval_engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow non trouvé"
            )

        return workflow.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du workflow: {str(e)}"
        )

@router.post("/workflow/approvals/{workflow_id}/approve")
async def approve_workflow_step(
    workflow_id: str,
    comment: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Approuve une étape d'un workflow

    - **workflow_id**: ID du workflow
    - **comment**: Commentaire de l'approbateur
    """
    try:
        approval_engine.approve_step(workflow_id, current_user.id, comment)

        # Récupérer le workflow mis à jour
        workflow = approval_engine.get_workflow(workflow_id)

        # Envoyer une notification
        notification_engine.send_notification(
            user_id=workflow.requester_id,
            notification_type="workflow_approved",
            title="Étape approuvée",
            message=f"Votre workflow pour {workflow.entity_type} {workflow.entity_id} a été approuvé",
            priority="normal",
            entity_type=workflow.entity_type,
            entity_id=workflow.entity_id,
            action_url=f"/workflow/approvals/{workflow.id}"
        )

        return {
            "message": "Étape approuvée avec succès",
            "workflow_id": workflow_id,
            "status": workflow.status.value
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'approbation: {str(e)}"
        )

@router.post("/workflow/approvals/{workflow_id}/reject")
async def reject_workflow_step(
    workflow_id: str,
    reason: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Rejette une étape d'un workflow

    - **workflow_id**: ID du workflow
    - **reason**: Raison du rejet
    """
    try:
        approval_engine.reject_step(workflow_id, current_user.id, reason)

        # Récupérer le workflow mis à jour
        workflow = approval_engine.get_workflow(workflow_id)

        # Envoyer une notification
        notification_engine.send_notification(
            user_id=workflow.requester_id,
            notification_type="workflow_rejected",
            title="Étape rejetée",
            message=f"Votre workflow pour {workflow.entity_type} {workflow.entity_id} a été rejeté: {reason}",
            priority="high",
            entity_type=workflow.entity_type,
            entity_id=workflow.entity_id,
            action_url=f"/workflow/approvals/{workflow.id}"
        )

        return {
            "message": "Étape rejetée avec succès",
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "rejection_reason": reason
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du rejet: {str(e)}"
        )
