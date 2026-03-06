
"""
Modèles de base de données pour les demandes de récupération de TVA
"""

from sqlalchemy import Column, String, Float, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from backend.database.base import Base

class VATClaimStatus(str, Enum):
    """Statuts des demandes de récupération de TVA"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class VATClaim(Base):
    """Modèle demande de récupération de TVA"""
    __tablename__ = "vat_claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Informations de base
    claim_number = Column(String(100), unique=True, nullable=False, index=True)
    target_country = Column(String(2), nullable=False)  # Code pays ISO 3166-1 alpha-2
    company_vat_number = Column(String(50), nullable=False)

    # Période de la demande
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Montants
    total_recoverable = Column(Float, default=0.0, nullable=False)
    total_approved = Column(Float, default=0.0, nullable=False)
    total_rejected = Column(Float, default=0.0, nullable=False)

    # Statut et validation
    status = Column(SQLEnum(VATClaimStatus), default=VATClaimStatus.DRAFT, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    submitted_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Référence externe
    external_reference = Column(String(100), nullable=True)  # Référence de l'autorité fiscale

    # Documents
    forms_generated = Column(JSON, nullable=True)  # Liste des formulaires générés
    forms_submitted = Column(JSON, nullable=True)  # Liste des formulaires soumis

    # Notes et commentaires
    notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Relations
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="vat_claims")
    submitter = relationship("User", foreign_keys=[submitted_by])
    approver = relationship("User", foreign_keys=[approved_by])
    invoices = relationship("Invoice", back_populates="vat_claim")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<VATClaim(id={self.id}, claim_number={self.claim_number}, status={self.status})>"

    def to_dict(self):
        """Convertit la demande en dictionnaire"""
        return {
            "id": self.id,
            "claim_number": self.claim_number,
            "target_country": self.target_country,
            "company_vat_number": self.company_vat_number,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "total_recoverable": self.total_recoverable,
            "total_approved": self.total_approved,
            "total_rejected": self.total_rejected,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "submitted_by": self.submitted_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "external_reference": self.external_reference,
            "forms_generated": self.forms_generated,
            "forms_submitted": self.forms_submitted,
            "notes": self.notes,
            "rejection_reason": self.rejection_reason,
            "company_id": self.company_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def calculate_totals(self) -> None:
        """Calcule les totaux de la demande"""
        total_recoverable = 0.0
        total_approved = 0.0
        total_rejected = 0.0

        for invoice in self.invoices:
            if invoice.is_recoverable():
                total_recoverable += invoice.get_recoverable_amount()

                if invoice.status == InvoiceStatus.APPROVED:
                    total_approved += invoice.get_recoverable_amount()
                elif invoice.status == InvoiceStatus.REJECTED:
                    total_rejected += invoice.get_recoverable_amount()

        self.total_recoverable = total_recoverable
        self.total_approved = total_approved
        self.total_rejected = total_rejected

    def submit(self, user_id: str) -> None:
        """
        Soumet la demande

        Args:
            user_id: ID de l'utilisateur qui soumet
        """
        if self.status != VATClaimStatus.DRAFT:
            raise ValueError("Seules les demandes en brouillon peuvent être soumises")

        # Calculer les totaux avant soumission
        self.calculate_totals()

        self.status = VATClaimStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        self.submitted_by = user_id

        # Générer le numéro de demande
        if not self.claim_number:
            self.claim_number = f"VAT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    def approve(self, user_id: str) -> None:
        """
        Approuve la demande

        Args:
            user_id: ID de l'utilisateur qui approuve
        """
        if self.status != VATClaimStatus.SUBMITTED and self.status != VATClaimStatus.PROCESSING:
            raise ValueError("Seules les demandes soumises ou en traitement peuvent être approuvées")

        self.status = VATClaimStatus.APPROVED
        self.approved_at = datetime.utcnow()
        self.approved_by = user_id

    def reject(self, user_id: str, reason: str) -> None:
        """
        Rejette la demande

        Args:
            user_id: ID de l'utilisateur qui rejette
            reason: Raison du rejet
        """
        if self.status != VATClaimStatus.SUBMITTED and self.status != VATClaimStatus.PROCESSING:
            raise ValueError("Seules les demandes soumises ou en traitement peuvent être rejetées")

        self.status = VATClaimStatus.REJECTED
        self.approved_at = datetime.utcnow()
        self.approved_by = user_id
        self.rejection_reason = reason

    def cancel(self) -> None:
        """Annule la demande"""
        if self.status not in [VATClaimStatus.DRAFT, VATClaimStatus.SUBMITTED]:
            raise ValueError("Seules les demandes en brouillon ou soumises peuvent être annulées")

        self.status = VATClaimStatus.CANCELLED

    def complete(self) -> None:
        """Marque la demande comme terminée"""
        if self.status != VATClaimStatus.APPROVED:
            raise ValueError("Seules les demandes approuvées peuvent être marquées comme terminées")

        self.status = VATClaimStatus.COMPLETED
