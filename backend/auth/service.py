
"""
Service d'authentification complet
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from backend.auth.models import (
    UserCreate, UserUpdate, UserInDB, UserResponse, Token,
    TwoFactorSetup, TwoFactorVerify, PasswordReset, PasswordResetConfirm,
    ChangePassword, LoginRequest
)
from backend.auth.password_hasher import password_hasher
from backend.auth.jwt_handler import jwt_handler
from backend.auth.two_factor_auth import two_factor_auth
from backend.auth.rbac import rbac_manager, ROLE_PERMISSIONS

class AuthService:
    """Service d'authentification"""

    def __init__(self):
        """Initialise le service d'authentification"""
        # En production, ces données seraient dans la base de données
        self.users_db = {}  # {user_id: UserInDB}
        self.refresh_tokens = {}  # {refresh_token: user_id}
        self.failed_attempts = {}  # {email: {count, last_attempt}}
        self.locked_accounts = {}  # {email: locked_until}
        self.password_reset_tokens = {}  # {token: email}
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Crée un nouvel utilisateur

        Args:
            user_data: Données de l'utilisateur

        Returns:
            Utilisateur créé

        Raises:
            HTTPException: Si l'email existe déjà
        """
        # Vérifier si l'email existe déjà
        for user in self.users_db.values():
            if user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cet email est déjà utilisé"
                )

        # Hacher le mot de passe
        hashed_password = password_hasher.hash_password(user_data.password)

        # Créer l'utilisateur
        user_id = f"user_{len(self.users_db) + 1}"
        now = datetime.utcnow()

        # Récupérer les permissions du rôle
        role_permissions = rbac_manager.get_role_permissions(user_data.role)

        user = UserInDB(
            id=user_id,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role=user_data.role,
            is_active=user_data.is_active,
            is_verified=user_data.is_verified,
            two_factor_enabled=user_data.two_factor_enabled,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now,
            permissions=list(role_permissions)
        )

        # Sauvegarder l'utilisateur
        self.users_db[user_id] = user

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            last_login=user.last_login,
            permissions=user.permissions
        )

    def authenticate_user(
        self,
        email: str,
        password: str,
        two_factor_code: Optional[str] = None
    ) -> Tuple[UserInDB, Token]:
        """
        Authentifie un utilisateur

        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            two_factor_code: Code 2FA (optionnel)

        Returns:
            Tuple (utilisateur, token)

        Raises:
            HTTPException: Si l'authentification échoue
        """
        # Vérifier si le compte est verrouillé
        if email in self.locked_accounts:
            locked_until = self.locked_accounts[email]
            if datetime.utcnow() < locked_until:
                time_remaining = (locked_until - datetime.utcnow()).seconds // 60
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Compte verrouillé. Réessayez dans {time_remaining} minutes."
                )
            else:
                # Déverrouiller le compte
                del self.locked_accounts[email]
                if email in self.failed_attempts:
                    del self.failed_attempts[email]

        # Trouver l'utilisateur
        user = None
        for u in self.users_db.values():
            if u.email == email:
                user = u
                break

        if not user:
            self._record_failed_attempt(email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )

        # Vérifier le mot de passe
        if not password_hasher.verify_password(password, user.hashed_password):
            self._record_failed_attempt(email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )

        # Vérifier si le compte est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ce compte a été désactivé"
            )

        # Vérifier le 2FA si activé
        if user.two_factor_enabled:
            if not two_factor_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Code 2FA requis",
                    headers={"X-Require-2FA": "true"}
                )

            # En production, vérifier le code 2FA avec le secret de l'utilisateur
            # Ici, nous simulons la vérification
            if len(two_factor_code) != 6:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Code 2FA invalide"
                )

        # Réinitialiser les tentatives échouées
        if email in self.failed_attempts:
            del self.failed_attempts[email]

        # Mettre à jour la dernière connexion
        user.last_login = datetime.utcnow()

        # Générer les tokens
        access_token = jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            permissions=user.permissions,
            company_id=user.company_id
        )

        refresh_token = jwt_handler.create_refresh_token(
            user_id=user.id,
            email=user.email
        )

        # Sauvegarder le refresh token
        self.refresh_tokens[refresh_token] = user.id

        # Créer l'objet Token
        token = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=jwt_handler.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                two_factor_enabled=user.two_factor_enabled,
                created_at=user.created_at,
                last_login=user.last_login,
                permissions=user.permissions
            )
        )

        return user, token

    def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Rafraîchit le token d'accès

        Args:
            refresh_token: Token de rafraîchissement

        Returns:
            Nouveau token

        Raises:
            HTTPException: Si le token est invalide
        """
        # Vérifier si le refresh token existe
        if refresh_token not in self.refresh_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalide"
            )

        # Décoder le token
        payload = jwt_handler.decode_token(refresh_token)

        # Récupérer l'utilisateur
        user = self.users_db.get(payload.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur introuvable"
            )

        # Vérifier si le compte est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ce compte a été désactivé"
            )

        # Générer de nouveaux tokens
        new_access_token = jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            permissions=user.permissions,
            company_id=user.company_id
        )

        new_refresh_token = jwt_handler.create_refresh_token(
            user_id=user.id,
            email=user.email
        )

        # Mettre à jour les refresh tokens
        del self.refresh_tokens[refresh_token]
        self.refresh_tokens[new_refresh_token] = user.id

        # Créer l'objet Token
        token = Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=jwt_handler.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                two_factor_enabled=user.two_factor_enabled,
                created_at=user.created_at,
                last_login=user.last_login,
                permissions=user.permissions
            )
        )

        return token

    def setup_two_factor(self, user_id: str) -> TwoFactorSetup:
        """
        Configure l'authentification à deux facteurs pour un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Configuration 2FA

        Raises:
            HTTPException: Si l'utilisateur n'existe pas
        """
        user = self.users_db.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        # Générer la configuration 2FA
        return two_factor_auth.setup_two_factor(user.email)

    def enable_two_factor(
        self,
        user_id: str,
        secret: str,
        verification: TwoFactorVerify
    ) -> UserResponse:
        """
        Active l'authentification à deux facteurs pour un utilisateur

        Args:
            user_id: ID de l'utilisateur
            secret: Secret TOTP
            verification: Données de vérification

        Returns:
            Utilisateur mis à jour

        Raises:
            HTTPException: Si l'utilisateur n'existe pas ou si la vérification échoue
        """
        user = self.users_db.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        # Vérifier le code 2FA
        is_valid, remaining_codes = two_factor_auth.verify_two_factor(
            secret,
            [],  # Codes de secours (vide lors de l'activation)
            verification
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code 2FA invalide"
            )

        # Activer le 2FA
        user.two_factor_enabled = True
        user.updated_at = datetime.utcnow()

        # En production, sauvegarder le secret dans la base de données
        # user.two_factor_secret = secret

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            last_login=user.last_login,
            permissions=user.permissions
        )

    def disable_two_factor(self, user_id: str) -> UserResponse:
        """
        Désactive l'authentification à deux facteurs pour un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Utilisateur mis à jour

        Raises:
            HTTPException: Si l'utilisateur n'existe pas
        """
        user = self.users_db.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        # Désactiver le 2FA
        user.two_factor_enabled = False
        user.updated_at = datetime.utcnow()

        # En production, supprimer le secret de la base de données
        # user.two_factor_secret = None

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            last_login=user.last_login,
            permissions=user.permissions
        )

    def request_password_reset(self, email: str) -> None:
        """
        Envoie un email de réinitialisation de mot de passe

        Args:
            email: Email de l'utilisateur
        """
        # En production, générer un token sécurisé et l'envoyer par email
        import secrets
        token = secrets.token_urlsafe(32)
        self.password_reset_tokens[token] = {
            "email": email,
            "expires_at": datetime.utcnow() + timedelta(hours=1)
        }

        # En production, envoyer l'email avec le token
        # email_service.send_password_reset_email(email, token)

    def reset_password(self, reset_data: PasswordResetConfirm) -> None:
        """
        Réinitialise le mot de passe d'un utilisateur

        Args:
            reset_data: Données de réinitialisation

        Raises:
            HTTPException: Si le token est invalide ou expiré
        """
        # Vérifier le token
        if reset_data.token not in self.password_reset_tokens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation invalide"
            )

        token_data = self.password_reset_tokens[reset_data.token]

        # Vérifier l'expiration
        if datetime.utcnow() > token_data["expires_at"]:
            del self.password_reset_tokens[reset_data.token]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation expiré"
            )

        # Trouver l'utilisateur
        user = None
        for u in self.users_db.values():
            if u.email == token_data["email"]:
                user = u
                break

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        # Mettre à jour le mot de passe
        user.hashed_password = password_hasher.hash_password(reset_data.new_password)
        user.updated_at = datetime.utcnow()

        # Supprimer le token
        del self.password_reset_tokens[reset_data.token]

    def change_password(
        self,
        user_id: str,
        password_data: ChangePassword
    ) -> None:
        """
        Change le mot de passe d'un utilisateur

        Args:
            user_id: ID de l'utilisateur
            password_data: Données de changement de mot de passe

        Raises:
            HTTPException: Si l'utilisateur n'existe pas ou si le mot de passe actuel est incorrect
        """
        user = self.users_db.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        # Vérifier le mot de passe actuel
        if not password_hasher.verify_password(
            password_data.current_password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe actuel incorrect"
            )

        # Mettre à jour le mot de passe
        user.hashed_password = password_hasher.hash_password(password_data.new_password)
        user.updated_at = datetime.utcnow()

    def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """
        Met à jour un utilisateur

        Args:
            user_id: ID de l'utilisateur
            user_data: Données de mise à jour

        Returns:
            Utilisateur mis à jour

        Raises:
            HTTPException: Si l'utilisateur n'existe pas
        """
        user = self.users_db.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        # Mettre à jour les champs
        if user_data.email is not None:
            # Vérifier si l'email est déjà utilisé
            for u in self.users_db.values():
                if u.id != user_id and u.email == user_data.email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cet email est déjà utilisé"
                    )
            user.email = user_data.email

        if user_data.first_name is not None:
            user.first_name = user_data.first_name

        if user_data.last_name is not None:
            user.last_name = user_data.last_name

        if user_data.phone is not None:
            user.phone = user_data.phone

        if user_data.role is not None:
            user.role = user_data.role
            # Mettre à jour les permissions
            user.permissions = list(rbac_manager.get_role_permissions(user_data.role))

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        if user_data.is_verified is not None:
            user.is_verified = user_data.is_verified

        if user_data.two_factor_enabled is not None:
            user.two_factor_enabled = user_data.two_factor_enabled

        user.updated_at = datetime.utcnow()

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            last_login=user.last_login,
            permissions=user.permissions
        )

    def get_user(self, user_id: str) -> UserResponse:
        """
        Récupère un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Utilisateur

        Raises:
            HTTPException: Si l'utilisateur n'existe pas
        """
        user = self.users_db.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            last_login=user.last_login,
            permissions=user.permissions
        )

    def list_users(self) -> List[UserResponse]:
        """
        Liste tous les utilisateurs

        Returns:
            Liste des utilisateurs
        """
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                two_factor_enabled=user.two_factor_enabled,
                created_at=user.created_at,
                last_login=user.last_login,
                permissions=user.permissions
            )
            for user in self.users_db.values()
        ]

    def delete_user(self, user_id: str) -> None:
        """
        Supprime un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Raises:
            HTTPException: Si l'utilisateur n'existe pas
        """
        if user_id not in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        del self.users_db[user_id]

    def logout(self, refresh_token: str) -> None:
        """
        Déconnecte un utilisateur

        Args:
            refresh_token: Token de rafraîchissement
        """
        if refresh_token in self.refresh_tokens:
            del self.refresh_tokens[refresh_token]

    def _record_failed_attempt(self, email: str) -> None:
        """
        Enregistre une tentative de connexion échouée

        Args:
            email: Email de l'utilisateur
        """
        if email not in self.failed_attempts:
            self.failed_attempts[email] = {
                "count": 0,
                "last_attempt": None
            }

        self.failed_attempts[email]["count"] += 1
        self.failed_attempts[email]["last_attempt"] = datetime.utcnow()

        # Vérifier si le compte doit être verrouillé
        if self.failed_attempts[email]["count"] >= self.max_failed_attempts:
            locked_until = datetime.utcnow() + timedelta(minutes=self.lockout_duration_minutes)
            self.locked_accounts[email] = locked_until

# Instance globale du service d'authentification
auth_service = AuthService()
