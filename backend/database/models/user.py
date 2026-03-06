
"""
Modèles de base de données pour les utilisateurs
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from backend.database.base import Base

class UserRole(str, Enum):
    """Rôles utilisateurs"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class User(Base):
    """Modèle utilisateur"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(255), nullable=True)
    backup_codes = Column(Text, nullable=True)

    # Compteur de tentatives de connexion échouées
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relations
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="users")

    # Méthodes
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "role": self.role.value if isinstance(self.role, Enum) else self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "two_factor_enabled": self.two_factor_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "company_id": self.company_id
        }

    def has_permission(self, permission: str) -> bool:
        """
        Vérifie si l'utilisateur a une permission spécifique

        Args:
            permission: Permission à vérifier

        Returns:
            True si l'utilisateur a la permission, False sinon
        """
        # En production, cette méthode vérifierait les permissions
        # dans la table user_permissions ou dans le cache
        from backend.auth.rbac import rbac_manager
        from backend.auth.models import Permission

        try:
            perm = Permission(permission)
            return rbac_manager.has_permission(
                self.role if isinstance(self.role, UserRole) else UserRole(self.role),
                [],  # À remplacer par les permissions de l'utilisateur
                perm
            )
        except ValueError:
            return False

    def is_locked(self) -> bool:
        """
        Vérifie si le compte est verrouillé

        Returns:
            True si le compte est verrouillé, False sinon
        """
        if not self.locked_until:
            return False

        return datetime.utcnow() < self.locked_until

    def unlock(self) -> None:
        """Déverrouille le compte"""
        self.failed_login_attempts = 0
        self.locked_until = None

    def increment_failed_attempts(self, max_attempts: int = 5, lockout_minutes: int = 30) -> bool:
        """
        Incrémente les tentatives de connexion échouées

        Args:
            max_attempts: Nombre maximum de tentatives avant verrouillage
            lockout_minutes: Durée du verrouillage en minutes

        Returns:
            True si le compte a été verrouillé, False sinon
        """
        self.failed_login_attempts += 1

        if self.failed_login_attempts >= max_attempts:
            self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
            return True

        return False

    def reset_failed_attempts(self) -> None:
        """Réinitialise les tentatives de connexion échouées"""
        self.failed_login_attempts = 0
        self.locked_until = None
