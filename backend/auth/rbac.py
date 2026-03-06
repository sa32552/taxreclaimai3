
"""
Module de gestion des rôles et permissions (RBAC)
"""

from typing import List, Dict, Set
from fastapi import HTTPException, status
from backend.auth.models import UserRole, Permission

# Mapping des rôles vers leurs permissions par défaut
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        # Toutes les permissions
        Permission.INVOICE_READ,
        Permission.INVOICE_WRITE,
        Permission.INVOICE_DELETE,
        Permission.INVOICE_APPROVE,
        Permission.VAT_RECOVERY_READ,
        Permission.VAT_RECOVERY_WRITE,
        Permission.VAT_RECOVERY_APPROVE,
        Permission.FORM_READ,
        Permission.FORM_WRITE,
        Permission.FORM_DELETE,
        Permission.FORM_APPROVE,
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.COMPANY_READ,
        Permission.COMPANY_WRITE,
        Permission.COMPANY_DELETE,
        Permission.REPORT_READ,
        Permission.REPORT_WRITE,
        Permission.REPORT_EXPORT,
        Permission.SYSTEM_ADMIN,
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_AUDIT,
    },
    UserRole.MANAGER: {
        # Permissions de gestion
        Permission.INVOICE_READ,
        Permission.INVOICE_WRITE,
        Permission.INVOICE_APPROVE,
        Permission.VAT_RECOVERY_READ,
        Permission.VAT_RECOVERY_WRITE,
        Permission.VAT_RECOVERY_APPROVE,
        Permission.FORM_READ,
        Permission.FORM_WRITE,
        Permission.FORM_APPROVE,
        Permission.USER_READ,
        Permission.COMPANY_READ,
        Permission.COMPANY_WRITE,
        Permission.REPORT_READ,
        Permission.REPORT_WRITE,
        Permission.REPORT_EXPORT,
    },
    UserRole.USER: {
        # Permissions utilisateur standard
        Permission.INVOICE_READ,
        Permission.INVOICE_WRITE,
        Permission.VAT_RECOVERY_READ,
        Permission.VAT_RECOVERY_WRITE,
        Permission.FORM_READ,
        Permission.FORM_WRITE,
        Permission.REPORT_READ,
        Permission.REPORT_EXPORT,
    },
    UserRole.VIEWER: {
        # Permissions en lecture seule
        Permission.INVOICE_READ,
        Permission.VAT_RECOVERY_READ,
        Permission.FORM_READ,
        Permission.REPORT_READ,
    },
}

class RBACManager:
    """Gestionnaire de contrôle d'accès basé sur les rôles"""

    def __init__(self):
        """Initialise le gestionnaire RBAC"""
        self.role_permissions = ROLE_PERMISSIONS

    def get_role_permissions(self, role: UserRole) -> Set[Permission]:
        """
        Récupère les permissions d'un rôle

        Args:
            role: Rôle utilisateur

        Returns:
            Ensemble des permissions du rôle
        """
        return self.role_permissions.get(role, set())

    def has_permission(
        self,
        user_role: UserRole,
        user_permissions: List[Permission],
        required_permission: Permission
    ) -> bool:
        """
        Vérifie si un utilisateur a une permission spécifique

        Args:
            user_role: Rôle de l'utilisateur
            user_permissions: Liste des permissions de l'utilisateur
            required_permission: Permission requise

        Returns:
            True si l'utilisateur a la permission, False sinon
        """
        # Vérifier si la permission est dans les permissions de l'utilisateur
        if required_permission in user_permissions:
            return True

        # Vérifier si la permission est dans les permissions du rôle
        role_perms = self.get_role_permissions(user_role)
        return required_permission in role_perms

    def has_any_permission(
        self,
        user_role: UserRole,
        user_permissions: List[Permission],
        required_permissions: List[Permission]
    ) -> bool:
        """
        Vérifie si un utilisateur a au moins une des permissions requises

        Args:
            user_role: Rôle de l'utilisateur
            user_permissions: Liste des permissions de l'utilisateur
            required_permissions: Liste des permissions requises

        Returns:
            True si l'utilisateur a au moins une permission, False sinon
        """
        return any(
            self.has_permission(user_role, user_permissions, perm)
            for perm in required_permissions
        )

    def has_all_permissions(
        self,
        user_role: UserRole,
        user_permissions: List[Permission],
        required_permissions: List[Permission]
    ) -> bool:
        """
        Vérifie si un utilisateur a toutes les permissions requises

        Args:
            user_role: Rôle de l'utilisateur
            user_permissions: Liste des permissions de l'utilisateur
            required_permissions: Liste des permissions requises

        Returns:
            True si l'utilisateur a toutes les permissions, False sinon
        """
        return all(
            self.has_permission(user_role, user_permissions, perm)
            for perm in required_permissions
        )

    def require_permission(
        self,
        user_role: UserRole,
        user_permissions: List[Permission],
        required_permission: Permission
    ) -> None:
        """
        Vérifie si un utilisateur a une permission et lève une exception sinon

        Args:
            user_role: Rôle de l'utilisateur
            user_permissions: Liste des permissions de l'utilisateur
            required_permission: Permission requise

        Raises:
            HTTPException: Si l'utilisateur n'a pas la permission
        """
        if not self.has_permission(user_role, user_permissions, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission requise: {required_permission.value}"
            )

    def require_any_permission(
        self,
        user_role: UserRole,
        user_permissions: List[Permission],
        required_permissions: List[Permission]
    ) -> None:
        """
        Vérifie si un utilisateur a au moins une des permissions requises

        Args:
            user_role: Rôle de l'utilisateur
            user_permissions: Liste des permissions de l'utilisateur
            required_permissions: Liste des permissions requises

        Raises:
            HTTPException: Si l'utilisateur n'a aucune des permissions
        """
        if not self.has_any_permission(user_role, user_permissions, required_permissions):
            required_perms_str = ", ".join([p.value for p in required_permissions])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Au moins une des permissions suivantes est requise: {required_perms_str}"
            )

    def require_all_permissions(
        self,
        user_role: UserRole,
        user_permissions: List[Permission],
        required_permissions: List[Permission]
    ) -> None:
        """
        Vérifie si un utilisateur a toutes les permissions requises

        Args:
            user_role: Rôle de l'utilisateur
            user_permissions: Liste des permissions de l'utilisateur
            required_permissions: Liste des permissions requises

        Raises:
            HTTPException: Si l'utilisateur n'a pas toutes les permissions
        """
        if not self.has_all_permissions(user_role, user_permissions, required_permissions):
            required_perms_str = ", ".join([p.value for p in required_permissions])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Toutes les permissions suivantes sont requises: {required_perms_str}"
            )

    def add_permission_to_role(self, role: UserRole, permission: Permission) -> None:
        """
        Ajoute une permission à un rôle

        Args:
            role: Rôle à modifier
            permission: Permission à ajouter
        """
        if role not in self.role_permissions:
            self.role_permissions[role] = set()

        self.role_permissions[role].add(permission)

    def remove_permission_from_role(self, role: UserRole, permission: Permission) -> None:
        """
        Supprime une permission d'un rôle

        Args:
            role: Rôle à modifier
            permission: Permission à supprimer
        """
        if role in self.role_permissions and permission in self.role_permissions[role]:
            self.role_permissions[role].remove(permission)

    def get_all_permissions(self) -> List[Permission]:
        """
        Récupère toutes les permissions disponibles

        Returns:
            Liste de toutes les permissions
        """
        return list(Permission)

# Instance globale du gestionnaire RBAC
rbac_manager = RBACManager()
