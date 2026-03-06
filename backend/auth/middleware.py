
"""
Middleware d'authentification et d'autorisation
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.auth.jwt_handler import jwt_handler
from backend.auth.rbac import rbac_manager
from backend.auth.models import TokenPayload, Permission, UserRole

# Configuration de la sécurité HTTP
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenPayload:
    """
    Récupère l'utilisateur actuel à partir du token JWT

    Args:
        request: Requête HTTP
        credentials: Credentials d'authentification HTTP

    Returns:
        Payload du token JWT

    Raises:
        HTTPException: Si l'authentification échoue
    """
    # Vérifier si le token est dans les cookies
    token = request.cookies.get("access_token")

    # Sinon, vérifier dans le header Authorization
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié. Token manquant.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt_handler.decode_token(token)
        return payload
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenPayload]:
    """
    Récupère l'utilisateur actuel de manière optionnelle

    Args:
        request: Requête HTTP
        credentials: Credentials d'authentification HTTP

    Returns:
        Payload du token JWT ou None
    """
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None

def require_permissions(*permissions: Permission):
    """
    Décorateur pour exiger des permissions spécifiques

    Args:
        *permissions: Liste des permissions requises

    Returns:
        Dépendance FastAPI
    """
    async def check_permissions(
        current_user: TokenPayload = Depends(get_current_user)
    ) -> TokenPayload:
        """
        Vérifie si l'utilisateur a les permissions requises

        Args:
            current_user: Utilisateur actuel

        Returns:
            Utilisateur actuel

        Raises:
            HTTPException: Si l'utilisateur n'a pas les permissions
        """
        user_role = current_user.role
        user_permissions = current_user.permissions

        # Vérifier toutes les permissions requises
        rbac_manager.require_all_permissions(
            user_role,
            user_permissions,
            list(permissions)
        )

        return current_user

    return check_permissions

def require_any_permission(*permissions: Permission):
    """
    Décorateur pour exiger au moins une permission parmi plusieurs

    Args:
        *permissions: Liste des permissions possibles

    Returns:
        Dépendance FastAPI
    """
    async def check_any_permission(
        current_user: TokenPayload = Depends(get_current_user)
    ) -> TokenPayload:
        """
        Vérifie si l'utilisateur a au moins une des permissions

        Args:
            current_user: Utilisateur actuel

        Returns:
            Utilisateur actuel

        Raises:
            HTTPException: Si l'utilisateur n'a aucune des permissions
        """
        user_role = current_user.role
        user_permissions = current_user.permissions

        # Vérifier au moins une permission
        rbac_manager.require_any_permission(
            user_role,
            user_permissions,
            list(permissions)
        )

        return current_user

    return check_any_permission

def require_role(*roles: UserRole):
    """
    Décorateur pour exiger un rôle spécifique

    Args:
        *roles: Liste des rôles acceptés

    Returns:
        Dépendance FastAPI
    """
    async def check_role(
        current_user: TokenPayload = Depends(get_current_user)
    ) -> TokenPayload:
        """
        Vérifie si l'utilisateur a un des rôles requis

        Args:
            current_user: Utilisateur actuel

        Returns:
            Utilisateur actuel

        Raises:
            HTTPException: Si l'utilisateur n'a pas le rôle requis
        """
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle requis: {', '.join([r.value for r in roles])}"
            )

        return current_user

    return check_role

def require_admin():
    """
    Décorateur pour exiger le rôle administrateur

    Returns:
        Dépendance FastAPI
    """
    return require_role(UserRole.ADMIN)

def require_manager():
    """
    Décorateur pour exiger le rôle manager ou supérieur

    Returns:
        Dépendance FastAPI
    """
    return require_role(UserRole.ADMIN, UserRole.MANAGER)
