
"""
Modèles de base de données pour les factures
"""

from sqlalchemy import Column, String, Float, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from backend.database.base import Base

class InvoiceStatus(str, Enum):
    """Statuts des factures"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class Invoice(Base):
    """Modèle facture"""
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Informations de base
    invoice_number = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    supplier = Column(String(255), nullable=False)
    supplier_vat_number = Column(String(50), nullable=True)
    country = Column(String(2), nullable=False)  # Code pays ISO 3166-1 alpha-2

    # Montants
    amount_ht = Column(Float, nullable=False)
    vat_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)  # Code devise ISO 4217

    # Langue et extraction
    language = Column(String(5), nullable=True)  # Code langue ISO 639-1
    extraction_confidence = Column(Float, default=0.0, nullable=False)
    extraction_data = Column(JSON, nullable=True)  # Données brutes de l'OCR

    # Statut et validation
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.UPLOADED, nullable=False)
    validated_at = Column(DateTime, nullable=True)
    validated_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Fichiers
    original_file_path = Column(String(500), nullable=True)
    processed_file_path = Column(String(500), nullable=True)

    # Relations
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="invoices")
    validator = relationship("User", foreign_keys=[validated_by])

    # Récupération TVA
    vat_claim_id = Column(String(36), ForeignKey("vat_claims.id"), nullable=True)
    vat_claim = relationship("VATClaim", back_populates="invoices")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number}, status={self.status})>"

    def to_dict(self):
        """Convertit la facture en dictionnaire"""
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "date": self.date.isoformat() if self.date else None,
            "supplier": self.supplier,
            "supplier_vat_number": self.supplier_vat_number,
            "country": self.country,
            "amount_ht": self.amount_ht,
            "vat_amount": self.vat_amount,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "language": self.language,
            "extraction_confidence": self.extraction_confidence,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "validated_by": self.validated_by,
            "original_file_path": self.original_file_path,
            "processed_file_path": self.processed_file_path,
            "company_id": self.company_id,
            "vat_claim_id": self.vat_claim_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def is_recoverable(self) -> bool:
        """
        Vérifie si la facture est éligible à la récupération de TVA

        Returns:
            True si la facture est éligible, False sinon
        """
        return (
            self.status == InvoiceStatus.PROCESSED and
            self.vat_amount > 0 and
            self.extraction_confidence >= 0.9  # 90% de confiance minimum
        )

    def get_recoverable_amount(self) -> float:
        """
        Calcule le montant récupérable de TVA

        Returns:
            Montant récupérable
        """
        if not self.is_recoverable():
            return 0.0

        return self.vat_amount

    def approve(self, user_id: str) -> None:
        """
        Approuve la facture

        Args:
            user_id: ID de l'utilisateur qui approuve
        """
        self.status = InvoiceStatus.APPROVED
        self.validated_at = datetime.utcnow()
        self.validated_by = user_id

    def reject(self, user_id: str) -> None:
        """
        Rejette la facture

        Args:
            user_id: ID de l'utilisateur qui rejette
        """
        self.status = InvoiceStatus.REJECTED
        self.validated_at = datetime.utcnow()
        self.validated_by = user_id

    def archive(self) -> None:
        """Archive la facture"""
        self.status = InvoiceStatus.ARCHIVED
