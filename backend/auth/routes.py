
"""
Routes d'authentification pour l'API FastAPI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from backend.auth.models import (
    UserCreate, UserUpdate, UserResponse, Token,
    TwoFactorSetup, TwoFactorVerify, PasswordReset, PasswordResetConfirm,
    ChangePassword, LoginRequest
)
from backend.auth.service import AuthService
from backend.auth.middleware import get_current_user, require_permissions
from backend.auth.models import Permission
from backend.auth.rate_limiter import check_rate_limit, login_rate_limiter, password_reset_rate_limiter

# Créer le routeur
router = APIRouter(prefix="/auth", tags=["Authentification"])

# Instance du service d'authentification
auth_service = AuthService()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request
):
    """
    Enregistre un nouvel utilisateur

    - **email**: Email de l'utilisateur
    - **password**: Mot de passe (min 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre)
    - **first_name**: Prénom
    - **last_name**: Nom
    - **phone**: Numéro de téléphone (optionnel)
    - **role**: Rôle (défaut: user)
    """
    # Vérifier le rate limit
    await check_rate_limit(request, login_rate_limiter, "register")

    try:
        user = auth_service.create_user(user_data)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    request: Request,
    response: Response
):
    """
    Authentifie un utilisateur

    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    - **two_factor_code**: Code 2FA (si activé)
    - **remember_me**: Se souvenir de l'utilisateur
    """
    # Vérifier le rate limit
    await check_rate_limit(request, login_rate_limiter, "login")

    try:
        user, token = auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password,
            two_factor_code=login_data.two_factor_code
        )

        # Définir le cookie si remember_me
        if login_data.remember_me:
            response.set_cookie(
                key="access_token",
                value=token.access_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=7 * 24 * 60 * 60  # 7 jours
            )

        return token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'authentification: {str(e)}"
        )

@router.post("/logout")
async def logout(response: Response):
    """
    Déconnecte l'utilisateur actuel
    """
    response.delete_cookie(key="access_token")
    return {"message": "Déconnexion réussie"}

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Rafraîchit le token d'accès

    - **refresh_token**: Token de rafraîchissement
    """
    try:
        token = auth_service.refresh_access_token(refresh_token)
        return token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du rafraîchissement du token: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Récupère les informations de l'utilisateur actuel
    """
    return UserResponse(
        id=current_user.sub,
        email=current_user.email,
        first_name="",  # À récupérer depuis la base de données
        last_name="",  # À récupérer depuis la base de données
        phone=None,  # À récupérer depuis la base de données
        role=current_user.role,
        is_active=True,  # À récupérer depuis la base de données
        is_verified=True,  # À récupérer depuis la base de données
        two_factor_enabled=False,  # À récupérer depuis la base de données
        created_at=current_user.iat,
        last_login=None,  # À récupérer depuis la base de données
        permissions=current_user.permissions
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user = Depends(get_current_user)
):
    """
    Met à jour les informations de l'utilisateur actuel
    """
    try:
        user = auth_service.update_user(current_user.sub, user_update)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@router.post("/me/password")
async def change_password(
    password_data: ChangePassword,
    current_user = Depends(get_current_user)
):
    """
    Change le mot de passe de l'utilisateur actuel

    - **current_password**: Mot de passe actuel
    - **new_password**: Nouveau mot de passe
    """
    try:
        auth_service.change_password(
            user_id=current_user.sub,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        return {"message": "Mot de passe changé avec succès"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du changement de mot de passe: {str(e)}"
        )

@router.post("/password/reset/request")
async def request_password_reset(
    reset_data: PasswordReset,
    request: Request
):
    """
    Demande une réinitialisation du mot de passe

    - **email**: Email de l'utilisateur
    """
    # Vérifier le rate limit
    await check_rate_limit(request, password_reset_rate_limiter, "password_reset")

    try:
        auth_service.request_password_reset(reset_data.email)
        return {"message": "Si l'email existe, un lien de réinitialisation a été envoyé"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la demande de réinitialisation: {str(e)}"
        )

@router.post("/password/reset/confirm")
async def confirm_password_reset(reset_data: PasswordResetConfirm):
    """
    Confirme la réinitialisation du mot de passe

    - **token**: Token de réinitialisation
    - **new_password**: Nouveau mot de passe
    """
    try:
        auth_service.confirm_password_reset(
            token=reset_data.token,
            new_password=reset_data.new_password
        )
        return {"message": "Mot de passe réinitialisé avec succès"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la réinitialisation du mot de passe: {str(e)}"
        )

@router.post("/2fa/setup", response_model=TwoFactorSetup)
async def setup_two_factor(
    current_user = Depends(get_current_user)
):
    """
    Configure l'authentification à deux facteurs

    Retourne le secret et le QR code pour scanner avec une app d'authentification
    """
    try:
        return auth_service.setup_two_factor(current_user.sub)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la configuration du 2FA: {str(e)}"
        )

@router.post("/2fa/enable")
async def enable_two_factor(
    secret: str,
    verification: TwoFactorVerify,
    current_user = Depends(get_current_user)
):
    """
    Active l'authentification à deux facteurs

    - **secret**: Secret TOTP
    - **code**: Code de vérification
    - **remember_device**: Se souvenir de l'appareil
    """
    try:
        user = auth_service.enable_two_factor(
            user_id=current_user.sub,
            secret=secret,
            verification=verification
        )
        return {"message": "2FA activé avec succès", "user": user}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'activation du 2FA: {str(e)}"
        )

@router.post("/2fa/disable")
async def disable_two_factor(
    current_user = Depends(get_current_user)
):
    """
    Désactive l'authentification à deux facteurs
    """
    try:
        user = auth_service.disable_two_factor(current_user.sub)
        return {"message": "2FA désactivé avec succès", "user": user}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la désactivation du 2FA: {str(e)}"
        )

@router.get("/users", response_model=list[UserResponse])
async def get_users(
    current_user = Depends(require_permissions(Permission.USER_READ))
):
    """
    Récupère la liste des utilisateurs (requiert la permission user:read)
    """
    try:
        users = auth_service.get_users()
        return users
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user = Depends(require_permissions(Permission.USER_READ))
):
    """
    Récupère un utilisateur par son ID (requiert la permission user:read)
    """
    try:
        user = auth_service.get_user(user_id)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'utilisateur: {str(e)}"
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user = Depends(require_permissions(Permission.USER_WRITE))
):
    """
    Met à jour un utilisateur (requiert la permission user:write)
    """
    try:
        user = auth_service.update_user(user_id, user_update)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user = Depends(require_permissions(Permission.USER_DELETE))
):
    """
    Supprime un utilisateur (requiert la permission user:delete)
    """
    try:
        auth_service.delete_user(user_id)
        return {"message": "Utilisateur supprimé avec succès"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression de l'utilisateur: {str(e)}"
        )
