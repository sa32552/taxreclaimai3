
"""
API principale TAXRECLAIMAI avec authentification intégrée
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from pathlib import Path

# Import des modules personnalisés
from pdf_processor import extract_invoice_data, process_batch_invoices
from vat_rules import get_vat_rules, match_vat_recovery_rules
from form_generator import generate_vat_forms, create_zip_archive

# Import des modules d'authentification
from backend.auth.routes import router as auth_router
from backend.auth.middleware import get_current_user, require_permissions
from backend.auth.models import Permission

# Import des modules de workflow
from backend.workflow.approval_engine import ApprovalEngine, ApprovalLevel
from backend.workflow.validation_pipeline import ValidationPipeline
from backend.workflow.change_tracker import ChangeTracker
from backend.workflow.notification_engine import NotificationEngine
from backend.workflow.signature_manager import SignatureManager

# Création de l'application FastAPI
app = FastAPI(
    title="TAXRECLAIMAI API",
    description="API pour la récupération automatique de TVA internationale",
    version="2.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Création des répertoires nécessaires
UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
FORMS_DIR = Path("forms")
TEMP_DIR = Path("temp")

for directory in [UPLOAD_DIR, PROCESSED_DIR, FORMS_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Initialisation des moteurs de workflow
approval_engine = ApprovalEngine()
validation_pipeline = ValidationPipeline()
change_tracker = ChangeTracker()
notification_engine = NotificationEngine()
signature_manager = SignatureManager()

# Enregistrement des routeurs
app.include_router(auth_router, prefix="/api/auth", tags=["Authentification"])

# Modèles de données
class InvoiceData(BaseModel):
    invoice_number: str
    date: str
    supplier: str
    country: str
    vat_number: str
    amount_ht: float
    vat_amount: float
    total_amount: float
    currency: str
    language: str

class VATRecoveryRequest(BaseModel):
    invoices: List[InvoiceData]
    target_country: str
    company_vat: str

class DashboardData(BaseModel):
    total_recoverable: float
    total_processed: int
    success_rate: float
    countries: List[dict]
    roi: float
    recent_invoices: List[dict]

@app.on_event("startup")
async def startup_event():
    """Initialisation de l'application au démarrage"""
    print("🚀 TAXRECLAIMAI API v2.0 démarrée avec succès")
    print("📊 Prêt à traiter les factures et récupérer la TVA")
    print("🔐 Authentification et workflow activés")

@app.get("/")
async def root():
    """Point de terminaison racine pour vérifier que l'API fonctionne"""
    return {
        "message": "TAXRECLAIMAI API v2.0 - Plateforme de récupération de TVA internationale",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "auth": "/api/auth",
            "upload_factures": "/upload_factures",
            "vat_recovery": "/vat_recovery",
            "dashboard": "/dashboard",
            "generate_forms": "/generate_forms",
            "workflow": "/workflow"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "modules": {
            "auth": "active",
            "workflow": "active",
            "validation": "active",
            "notifications": "active"
        }
    }

# Endpoints de factures (protégés)
@app.post("/upload_factures")
async def upload_factures(
    background_tasks,
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user)
):
    """
    Endpoint pour télécharger et traiter un lot de factures

    - **files**: Liste des fichiers PDF/JPG/PNG à traiter
    - Returns: Résultats de l'extraction OCR pour chaque facture
    """
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")

    if len(files) > 120:
        raise HTTPException(status_code=400, detail="Maximum 120 fichiers autorisés par lot")

    # Créer un ID unique pour ce lot
    batch_id = str(uuid.uuid4())
    batch_dir = UPLOAD_DIR / batch_id
    batch_dir.mkdir(exist_ok=True)

    # Sauvegarder les fichiers téléchargés
    file_paths = []
    for file in files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.pdf', '.jpg', '.jpeg', '.png']:
            raise HTTPException(
                status_code=400,
                detail=f"Format de fichier non supporté: {file.filename}"
            )

        file_path = batch_dir / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        file_paths.append(str(file_path))

    # Traiter les factures en arrière-plan
    def process_batch():
        results = process_batch_invoices(file_paths, batch_id)

        # Valider chaque facture avec le pipeline
        for invoice_data in results["invoices"]:
            validation_results = validation_pipeline.validate(invoice_data)

            # Enregistrer les résultats de validation
            for validation in validation_results:
                if not validation.is_passed and validation.severity in ["error", "critical"]:
                    # Envoyer une notification si erreur critique
                    notification_engine.send_notification(
                        user_id=current_user.sub,
                        notification_type=NotificationType.INVOICE_PROCESSED,
                        title=f"Erreur de validation - {invoice_data['invoice_number']}",
                        message=validation.message,
                        priority=NotificationPriority.HIGH,
                        entity_type="invoice",
                        entity_id=invoice_data.get('id', ''),
                        action_url=f"/invoices/{invoice_data.get('id', '')}"
                    )

        # Sauvegarder les résultats
        results_file = PROCESSED_DIR / f"{batch_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

    background_tasks.add_task(process_batch)

    return {
        "message": f"{len(files)} factures téléchargées avec succès",
        "batch_id": batch_id,
        "status": "processing",
        "estimated_time": f"{len(files) * 1.4} secondes"
    }

@app.post("/vat_recovery")
async def vat_recovery(
    request: VATRecoveryRequest,
    current_user = Depends(get_current_user)
):
    """
    Endpoint pour matcher les règles TVA et calculer les montants récupérables

    - **request**: Données des factures et pays cible
    - Returns: Résultats du matching TVA et montants récupérables
    """
    try:
        # Convertir les factures en dictionnaire
        invoices_dict = [invoice.dict() for invoice in request.invoices]

        # Obtenir les règles TVA pour le pays cible
        vat_rules = get_vat_rules(request.target_country)

        # Matcher les factures avec les règles TVA
        recovery_results = match_vat_recovery_rules(
            invoices_dict, 
            vat_rules, 
            request.company_vat
        )

        # Calculer les statistiques
        total_recoverable = sum(item["recoverable_amount"] for item in recovery_results["matched_invoices"])
        success_rate = len(recovery_results["matched_invoices"]) / len(request.invoices) * 100

        # Créer une demande de récupération TVA
        vat_claim = create_vat_claim(
            user_id=current_user.sub,
            target_country=request.target_country,
            company_vat=request.company_vat,
            invoices=recovery_results["matched_invoices"],
            total_recoverable=total_recoverable
        )

        # Envoyer une notification
        notification_engine.send_notification(
            user_id=current_user.sub,
            notification_type=NotificationType.VAT_CLAIM_SUBMITTED,
            title="Demande de récupération TVA créée",
            message=f"Une demande de récupération TVA de {total_recoverable:.2f} EUR a été créée pour {request.target_country}",
            priority=NotificationPriority.NORMAL,
            entity_type="vat_claim",
            entity_id=vat_claim.id,
            action_url=f"/vat-claims/{vat_claim.id}"
        )

        return {
            "status": "success",
            "target_country": request.target_country,
            "total_invoices": len(request.invoices),
            "matched_invoices": len(recovery_results["matched_invoices"]),
            "total_recoverable": total_recoverable,
            "currency": "EUR",
            "success_rate": round(success_rate, 2),
            "roi": round(total_recoverable / (total_recoverable * 0.125), 2),
            "vat_claim_id": vat_claim.id,
            "results": recovery_results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement TVA: {str(e)}"
        )

@app.get("/dashboard")
async def dashboard(current_user = Depends(get_current_user)):
    """
    Endpoint pour obtenir les KPI du dashboard

    - Returns: Statistiques de récupération TVA et KPI
    """
    # Récupérer les données du dashboard pour l'utilisateur
    dashboard_data = get_user_dashboard_data(current_user.sub)

    return dashboard_data

@app.post("/generate_forms")
async def generate_forms(
    request: VATRecoveryRequest,
    current_user = Depends(get_current_user)
):
    """
    Endpoint pour générer les formulaires de remboursement TVA

    - **request**: Données des factures et pays cible
    - Returns: Fichier ZIP contenant les formulaires pré-remplis
    """
    try:
        # Convertir les factures en dictionnaire
        invoices_dict = [invoice.dict() for invoice in request.invoices]

        # Générer les formulaires
        forms = generate_vat_forms(
            invoices_dict, 
            request.target_country, 
            request.company_vat
        )

        # Créer l'archive ZIP
        zip_id = str(uuid.uuid4())
        zip_path = create_zip_archive(forms, zip_id)

        # Signer chaque formulaire
        for form in forms:
            signature_manager.create_signature(
                entity_type="form",
                entity_id=form["id"],
                signature_type=SignatureType.SUBMISSION,
                signer_id=current_user.sub,
                signer_name=f"{current_user.first_name} {current_user.last_name}",
                signer_role=current_user.role.value,
                data={"form_type": form["type"]}
            )

        # Envoyer une notification
        notification_engine.send_notification(
            user_id=current_user.sub,
            notification_type=NotificationType.FORM_GENERATED,
            title="Formulaires générés avec succès",
            message=f"{len(forms)} formulaires ont été générés pour {request.target_country}",
            priority=NotificationPriority.NORMAL,
            entity_type="form_batch",
            entity_id=zip_id,
            action_url=f"/download_forms/{zip_id}"
        )

        return {
            "message": "Formulaires générés avec succès",
            "forms_count": len(forms),
            "download_url": f"/download_forms/{zip_id}",
            "expires_at": (datetime.now().timestamp() + 3600 * 24)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération des formulaires: {str(e)}"
        )

@app.get("/download_forms/{zip_id}")
async def download_forms(
    zip_id: str,
    current_user = Depends(get_current_user)
):
    """
    Endpoint pour télécharger l'archive ZIP des formulaires

    - **zip_id**: ID de l'archive ZIP
    - Returns: Fichier ZIP des formulaires
    """
    zip_path = FORMS_DIR / f"{zip_id}.zip"

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Archive non trouvée ou expirée")

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=f"vat_forms_{zip_id}.zip"
    )

# Endpoints de workflow
@app.post("/workflow/approval/create")
async def create_approval_workflow(
    entity_type: str,
    entity_id: str,
    required_levels: List[ApprovalLevel],
    current_user = Depends(require_permissions(Permission.INVOICE_APPROVE))
):
    """
    Crée un workflow d'approbation pour une entité

    - **entity_type**: Type d'entité (invoice, vat_claim, form)
    - **entity_id**: ID de l'entité
    - **required_levels**: Liste des niveaux d'approbation requis
    - Returns: Workflow d'approbation créé
    """
    workflow = approval_engine.create_workflow(
        entity_type=entity_type,
        entity_id=entity_id,
        requester_id=current_user.sub,
        requester_name=f"{current_user.first_name} {current_user.last_name}",
        required_levels=required_levels
    )

    # Envoyer une notification aux approbateurs
    notification_engine.send_bulk_notification(
        user_ids=get_approvers_for_level(required_levels[0]),
        notification_type=NotificationType.WORKFLOW_APPROVAL_REQUIRED,
        title="Nouvelle approbation requise",
        message=f"Une approbation est requise pour {entity_type} {entity_id}",
        priority=NotificationPriority.NORMAL,
        entity_type=entity_type,
        entity_id=entity_id,
        action_url=f"/workflow/{workflow.id}"
    )

    return workflow.to_dict()

@app.post("/workflow/approval/approve")
async def approve_workflow_step(
    workflow_id: str,
    current_user = Depends(require_permissions(Permission.INVOICE_APPROVE))
):
    """
    Approuve une étape d'un workflow d'approbation

    - **workflow_id**: ID du workflow
    - Returns: Workflow mis à jour
    """
    approval_engine.approve_step(workflow_id, current_user.sub)

    # Récupérer le workflow
    workflow = approval_engine.get_workflow(workflow_id)

    # Signer l'approbation
    signature_manager.create_signature(
        entity_type="workflow",
        entity_id=workflow_id,
        signature_type=SignatureType.APPROVAL,
        signer_id=current_user.sub,
        signer_name=f"{current_user.first_name} {current_user.last_name}",
        signer_role=current_user.role.value
    )

    # Envoyer une notification
    notification_engine.send_notification(
        user_id=workflow.requester_id,
        notification_type=NotificationType.WORKFLOW_APPROVED,
        title="Approbation validée",
        message=f"Votre demande d'approbation a été validée par {current_user.first_name} {current_user.last_name}",
        priority=NotificationPriority.NORMAL,
        entity_type=workflow.entity_type,
        entity_id=workflow.entity_id,
        action_url=f"/workflow/{workflow_id}"
    )

    return workflow.to_dict()

@app.post("/workflow/approval/reject")
async def reject_workflow_step(
    workflow_id: str,
    reason: str,
    current_user = Depends(require_permissions(Permission.INVOICE_APPROVE))
):
    """
    Rejette une étape d'un workflow d'approbation

    - **workflow_id**: ID du workflow
    - **reason**: Raison du rejet
    - Returns: Workflow mis à jour
    """
    approval_engine.reject_step(workflow_id, current_user.sub, reason)

    # Récupérer le workflow
    workflow = approval_engine.get_workflow(workflow_id)

    # Signer le rejet
    signature_manager.create_signature(
        entity_type="workflow",
        entity_id=workflow_id,
        signature_type=SignatureType.REJECTION,
        signer_id=current_user.sub,
        signer_name=f"{current_user.first_name} {current_user.last_name}",
        signer_role=current_user.role.value,
        data={"reason": reason}
    )

    # Envoyer une notification
    notification_engine.send_notification(
        user_id=workflow.requester_id,
        notification_type=NotificationType.WORKFLOW_REJECTED,
        title="Approbation rejetée",
        message=f"Votre demande d'approbation a été rejetée. Raison: {reason}",
        priority=NotificationPriority.HIGH,
        entity_type=workflow.entity_type,
        entity_id=workflow.entity_id,
        action_url=f"/workflow/{workflow_id}"
    )

    return workflow.to_dict()

@app.get("/workflow/history/{entity_type}/{entity_id}")
async def get_workflow_history(
    entity_type: str,
    entity_id: str,
    current_user = Depends(get_current_user)
):
    """
    Récupère l'historique des modifications d'une entité

    - **entity_type**: Type d'entité
    - **entity_id**: ID de l'entité
    - Returns: Historique des modifications
    """
    history = change_tracker.get_history(entity_type, entity_id)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "history": [change.to_dict() for change in history]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
