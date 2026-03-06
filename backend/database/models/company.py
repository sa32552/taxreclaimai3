
"""
Modèles de base de données pour les entreprises
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.database.base import Base

class Company(Base):
    """Modèle entreprise"""
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    vat_number = Column(String(50), unique=True, nullable=False, index=True)
    country = Column(String(2), nullable=False)  # Code pays ISO 3166-1 alpha-2
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    subscription_plan = Column(String(50), default="free", nullable=False)  # free, pro, enterprise
    max_users = Column(Integer, default=5, nullable=False)
    max_invoices_per_month = Column(Integer, default=100, nullable=False)

    # Configuration personnalisée
    settings = Column(JSON, nullable=True)  # Configuration spécifique à l'entreprise

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relations
    users = relationship("User", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    vat_claims = relationship("VATClaim", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, vat_number={self.vat_number})>"

    def to_dict(self):
        """Convertit l'entreprise en dictionnaire"""
        return {
            "id": self.id,
            "name": self.name,
            "vat_number": self.vat_number,
            "country": self.country,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "phone": self.phone,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "subscription_plan": self.subscription_plan,
            "max_users": self.max_users,
            "max_invoices_per_month": self.max_invoices_per_month,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def can_add_user(self) -> bool:
        """
        Vérifie si l'entreprise peut ajouter un utilisateur

        Returns:
            True si l'entreprise peut ajouter un utilisateur, False sinon
        """
        if not self.is_active:
            return False

        current_user_count = len([u for u in self.users if u.is_active])
        return current_user_count < self.max_users

    def get_user_count(self) -> int:
        """
        Récupère le nombre d'utilisateurs actifs

        Returns:
            Nombre d'utilisateurs actifs
        """
        return len([u for u in self.users if u.is_active])

    def is_subscription_active(self) -> bool:
        """
        Vérifie si l'abonnement de l'entreprise est actif

        Returns:
            True si l'abonnement est actif, False sinon
        """
        return self.is_active and self.is_verified

    def get_setting(self, key: str, default=None):
        """
        Récupère une configuration spécifique

        Args:
            key: Clé de la configuration
            default: Valeur par défaut

        Returns:
            Valeur de la configuration ou la valeur par défaut
        """
        if not self.settings:
            return default

        return self.settings.get(key, default)

    def set_setting(self, key: str, value):
        """
        Définit une configuration spécifique

        Args:
            key: Clé de la configuration
            value: Valeur de la configuration
        """
        if not self.settings:
            self.settings = {}

        self.settings[key] = value
