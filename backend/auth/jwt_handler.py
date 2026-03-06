
"""
Module de gestion des tokens JWT
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from backend.auth.models import TokenPayload, UserRole, Permission

# Configuration JWT
SECRET_KEY = "votre-secret-key-a-changer-en-production"  # À remplacer par une variable d'environnement
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class JWTHandler:
    """Gestionnaire de tokens JWT"""

    def __init__(
        self,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM,
        access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = REFRESH_TOKEN_EXPIRE_DAYS
    ):
        """
        Initialise le gestionnaire JWT

        Args:
            secret_key: Clé secrète pour signer les tokens
            algorithm: Algorithme de signature
            access_token_expire_minutes: Durée de validité du token d'accès
            refresh_token_expire_days: Durée de validité du token de rafraîchissement
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: UserRole,
        permissions: list[Permission],
        company_id: Optional[str] = None
    ) -> str:
        """
        Crée un token d'accès

        Args:
            user_id: ID de l'utilisateur
            email: Email de l'utilisateur
            role: Rôle de l'utilisateur
            permissions: Liste des permissions de l'utilisateur
            company_id: ID de l'entreprise (optionnel)

        Returns:
            Token d'accès JWT
        """
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode = {
            "sub": user_id,
            "email": email,
            "role": role,
            "permissions": [p.value for p in permissions],
            "company_id": company_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(
        self,
        user_id: str,
        email: str
    ) -> str:
        """
        Crée un token de rafraîchissement

        Args:
            user_id: ID de l'utilisateur
            email: Email de l'utilisateur

        Returns:
            Token de rafraîchissement JWT
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenPayload:
        """
        Décode et vérifie un token JWT

        Args:
            token: Token JWT à décoder

        Returns:
            Payload du token

        Raises:
            HTTPException: Si le token est invalide ou expiré
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Vérifier que le token est du bon type
            token_type = payload.get("type")
            if token_type not in ["access", "refresh"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Type de token invalide"
                )

            # Créer le payload typé
            return TokenPayload(
                sub=payload.get("sub"),
                email=payload.get("email"),
                role=payload.get("role"),
                permissions=[Permission(p) for p in payload.get("permissions", [])],
                company_id=payload.get("company_id"),
                exp=payload.get("exp"),
                iat=payload.get("iat")
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token invalide: {str(e)}"
            )

    def verify_token(self, token: str) -> bool:
        """
        Vérifie si un token est valide

        Args:
            token: Token JWT à vérifier

        Returns:
            True si le token est valide, False sinon
        """
        try:
            self.decode_token(token)
            return True
        except HTTPException:
            return False

    def extract_user_id(self, token: str) -> str:
        """
        Extrait l'ID utilisateur d'un token

        Args:
            token: Token JWT

        Returns:
            ID de l'utilisateur
        """
        payload = self.decode_token(token)
        return payload.sub

# Instance globale du gestionnaire JWT
jwt_handler = JWTHandler()
