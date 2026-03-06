
"""
Module d'authentification Supabase
"""

from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from supabase import AuthError

from backend.supabase_client import get_auth_client
from backend.auth.models import UserResponse, Token

class SupabaseAuthService:
    """Service d'authentification Supabase"""

    def __init__(self):
        """Initialise le service d'authentification"""
        self.auth = get_auth_client()

    async def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        role: str = "user"
    ) -> Dict[str, Any]:
        """
        Enregistre un nouvel utilisateur

        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            first_name: Prénom
            last_name: Nom
            phone: Numéro de téléphone (optionnel)
            role: Rôle de l'utilisateur

        Returns:
            Données de l'utilisateur créé

        Raises:
            HTTPException: Si l'enregistrement échoue
        """
        try:
            # Créer l'utilisateur dans Supabase Auth
            auth_response = self.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "role": role
                    }
                }
            })

            # Récupérer les données de l'utilisateur
            user_data = auth_response.user

            # Créer l'utilisateur dans la table users
            from backend.supabase_client import get_supabase_client
            supabase = get_supabase_client()

            user_record = supabase.table("users").insert({
                "id": user_data.id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "role": role,
                "is_active": True,
                "is_verified": user_data.email_confirmed_at is not None,
                "two_factor_enabled": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()

            return {
                "user": {
                    "id": user_data.id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "role": role,
                    "is_active": True,
                    "is_verified": user_data.email_confirmed_at is not None,
                    "two_factor_enabled": False,
                    "created_at": user_data.created_at,
                    "last_login": None,
                    "permissions": self._get_role_permissions(role)
                },
                "session": auth_response.session
            }
        except AuthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur lors de l'enregistrement: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur serveur: {str(e)}"
            )

    async def login(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authentifie un utilisateur

        Args:
            email: Email de l'utilisateur
            password: Mot de passe

        Returns:
            Données de l'utilisateur et session

        Raises:
            HTTPException: Si l'authentification échoue
        """
        try:
            # Authentifier l'utilisateur
            auth_response = self.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            # Récupérer les données de l'utilisateur
            user_data = auth_response.user

            # Récupérer les données supplémentaires depuis la table users
            from backend.supabase_client import get_supabase_client
            supabase = get_supabase_client()

            user_record = supabase.table("users").select("*").eq("id", user_data.id).single().execute()

            if not user_record.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utilisateur non trouvé"
                )

            user_info = user_record.data

            # Mettre à jour la dernière connexion
            supabase.table("users").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user_data.id).execute()

            return {
                "user": {
                    "id": user_data.id,
                    "email": user_data.email,
                    "first_name": user_info.get("first_name"),
                    "last_name": user_info.get("last_name"),
                    "phone": user_info.get("phone"),
                    "role": user_info.get("role"),
                    "is_active": user_info.get("is_active", True),
                    "is_verified": user_data.email_confirmed_at is not None,
                    "two_factor_enabled": user_info.get("two_factor_enabled", False),
                    "created_at": user_info.get("created_at"),
                    "last_login": datetime.utcnow().isoformat(),
                    "permissions": self._get_role_permissions(user_info.get("role", "user"))
                },
                "session": auth_response.session,
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token
            }
        except AuthError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Email ou mot de passe incorrect: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur serveur: {str(e)}"
            )

    async def logout(self, access_token: str) -> Dict[str, str]:
        """
        Déconnecte un utilisateur

        Args:
            access_token: Token d'accès

        Returns:
            Message de confirmation

        Raises:
            HTTPException: Si la déconnexion échoue
        """
        try:
            self.auth.sign_out(access_token)
            return {"message": "Déconnexion réussie"}
        except AuthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur lors de la déconnexion: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur serveur: {str(e)}"
            )

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Rafraîchit le token d'accès

        Args:
            refresh_token: Token de rafraîchissement

        Returns:
            Nouveaux tokens

        Raises:
            HTTPException: Si le rafraîchissement échoue
        """
        try:
            auth_response = self.auth.refresh_session(refresh_token)

            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "expires_in": auth_response.session.expires_in,
                "token_type": "bearer"
            }
        except AuthError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token invalide: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur serveur: {str(e)}"
            )

    async def get_current_user(self, access_token: str) -> UserResponse:
        """
        Récupère l'utilisateur actuel

        Args:
            access_token: Token d'accès

        Returns:
            Données de l'utilisateur

        Raises:
            HTTPException: Si la récupération échoue
        """
        try:
            # Vérifier le token
            user_response = self.auth.get_user(access_token)

            if not user_response or not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide"
                )

            user_data = user_response.user

            # Récupérer les données supplémentaires depuis la table users
            from backend.supabase_client import get_supabase_client
            supabase = get_supabase_client()

            user_record = supabase.table("users").select("*").eq("id", user_data.id).single().execute()

            if not user_record.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utilisateur non trouvé"
                )

            user_info = user_record.data

            return UserResponse(
                id=user_data.id,
                email=user_data.email,
                first_name=user_info.get("first_name"),
                last_name=user_info.get("last_name"),
                phone=user_info.get("phone"),
                role=user_info.get("role"),
                is_active=user_info.get("is_active", True),
                is_verified=user_data.email_confirmed_at is not None,
                two_factor_enabled=user_info.get("two_factor_enabled", False),
                created_at=user_info.get("created_at"),
                last_login=user_info.get("last_login"),
                permissions=self._get_role_permissions(user_info.get("role", "user"))
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur serveur: {str(e)}"
            )

    def _get_role_permissions(self, role: str) -> list:
        """
        Récupère les permissions d'un rôle

        Args:
            role: Rôle de l'utilisateur

        Returns:
            Liste des permissions
        """
        from backend.auth.models import Permission

        role_permissions = {
            "admin": [
                Permission.INVOICE_READ, Permission.INVOICE_WRITE, Permission.INVOICE_DELETE, Permission.INVOICE_APPROVE,
                Permission.VAT_RECOVERY_READ, Permission.VAT_RECOVERY_WRITE, Permission.VAT_RECOVERY_APPROVE,
                Permission.FORM_READ, Permission.FORM_WRITE, Permission.FORM_DELETE, Permission.FORM_APPROVE,
                Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE,
                Permission.COMPANY_READ, Permission.COMPANY_WRITE, Permission.COMPANY_DELETE,
                Permission.REPORT_READ, Permission.REPORT_WRITE, Permission.REPORT_EXPORT,
                Permission.SYSTEM_ADMIN, Permission.SYSTEM_CONFIG, Permission.SYSTEM_AUDIT
            ],
            "manager": [
                Permission.INVOICE_READ, Permission.INVOICE_WRITE, Permission.INVOICE_APPROVE,
                Permission.VAT_RECOVERY_READ, Permission.VAT_RECOVERY_WRITE, Permission.VAT_RECOVERY_APPROVE,
                Permission.FORM_READ, Permission.FORM_WRITE, Permission.FORM_APPROVE,
                Permission.USER_READ,
                Permission.COMPANY_READ, Permission.COMPANY_WRITE,
                Permission.REPORT_READ, Permission.REPORT_WRITE, Permission.REPORT_EXPORT
            ],
            "user": [
                Permission.INVOICE_READ, Permission.INVOICE_WRITE,
                Permission.VAT_RECOVERY_READ, Permission.VAT_RECOVERY_WRITE,
                Permission.FORM_READ, Permission.FORM_WRITE,
                Permission.REPORT_READ, Permission.REPORT_EXPORT
            ],
            "viewer": [
                Permission.INVOICE_READ,
                Permission.VAT_RECOVERY_READ,
                Permission.FORM_READ,
                Permission.REPORT_READ
            ]
        }

        return role_permissions.get(role, role_permissions["user"])

# Instance globale du service d'authentification Supabase
supabase_auth_service = SupabaseAuthService()
