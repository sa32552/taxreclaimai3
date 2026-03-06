
"""
Modèles de base de données pour les formulaires
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from backend.database.base import Base

class FormType(str, Enum):
    """Types de formulaires"""
    CA3 = "CA3"  # France
    USt1V = "USt1V"  # Allemagne
    VA = "VA"  # Italie
    FORM303 = "303"  # Espagne
    VAT65A = "VAT65A"  # Royaume-Uni
    OB = "OB"  # Pays-Bas
    FORM71604 = "71.604"  # Belgique
    U21 = "U21"  # Autriche
    FORM833 = "833"  # Suisse
    VAT_UE = "VAT-UE"  # Pologne
    SKV4632 = "SKV 4632"  # Suède
    VAT55 = "VAT 55"  # Danemark
    VAT811 = "VAT 811"  # Finlande
    RF1032 = "RF-1032"  # Norvège
    IVA54 = "IVA54"  # Portugal
    F2 = "F2"  # Grèce
    VAT66 = "VAT66"  # Irlande
    FORM770 = "770"  # Luxembourg
    # ... et ainsi de suite pour les 47 formulaires

class FormStatus(str, Enum):
    """Statuts des formulaires"""
    DRAFT = "draft"
    GENERATED = "generated"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class Form(Base):
    """Modèle formulaire"""
    __tablename__ = "forms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Informations de base
    form_number = Column(String(100), unique=True, nullable=False, index=True)
    form_type = Column(SQLEnum(FormType), nullable=False)
    country = Column(String(2), nullable=False)  # Code pays ISO 3166-1 alpha-2

    # Période
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Données du formulaire
    form_data = Column(JSON, nullable=False)  # Données du formulaire pré-remplies

    # Fichiers
    pdf_path = Column(String(500), nullable=True)
    xml_path = Column(String(500), nullable=True)

    # Statut et validation
    status = Column(SQLEnum(FormStatus), default=FormStatus.DRAFT, nullable=False)
    generated_at = Column(DateTime, nullable=True)
    generated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    submitted_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Référence externe
    external_reference = Column(String(100), nullable=True)  # Référence de l'autorité fiscale

    # Notes et commentaires
    notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Relations
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    vat_claim_id = Column(String(36), ForeignKey("vat_claims.id"), nullable=True)
    generator = relationship("User", foreign_keys=[generated_by])
    submitter = relationship("User", foreign_keys=[submitted_by])
    approver = relationship("User", foreign_keys=[approved_by])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Form(id={self.id}, form_number={self.form_number}, form_type={self.form_type})>"

    def to_dict(self):
        """Convertit le formulaire en dictionnaire"""
        return {
            "id": self.id,
            "form_number": self.form_number,
            "form_type": self.form_type.value if isinstance(self.form_type, Enum) else self.form_type,
            "country": self.country,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "form_data": self.form_data,
            "pdf_path": self.pdf_path,
            "xml_path": self.xml_path,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "generated_by": self.generated_by,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "submitted_by": self.submitted_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "external_reference": self.external_reference,
            "notes": self.notes,
            "rejection_reason": self.rejection_reason,
            "company_id": self.company_id,
            "vat_claim_id": self.vat_claim_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def generate(self, user_id: str) -> None:
        """
        Génère le formulaire

        Args:
            user_id: ID de l'utilisateur qui génère le formulaire
        """
        if self.status != FormStatus.DRAFT:
            raise ValueError("Seuls les formulaires en brouillon peuvent être générés")

        self.status = FormStatus.GENERATED
        self.generated_at = datetime.utcnow()
        self.generated_by = user_id

        # Générer le numéro de formulaire
        if not self.form_number:
            self.form_number = f"FORM-{self.form_type.value}-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    def submit(self, user_id: str) -> None:
        """
        Soumet le formulaire

        Args:
            user_id: ID de l'utilisateur qui soumet le formulaire
        """
        if self.status != FormStatus.GENERATED:
            raise ValueError("Seuls les formulaires générés peuvent être soumis")

        self.status = FormStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        self.submitted_by = user_id

    def approve(self, user_id: str) -> None:
        """
        Approuve le formulaire

        Args:
            user_id: ID de l'utilisateur qui approuve le formulaire
        """
        if self.status != FormStatus.SUBMITTED:
            raise ValueError("Seuls les formulaires soumis peuvent être approuvés")

        self.status = FormStatus.APPROVED
        self.approved_at = datetime.utcnow()
        self.approved_by = user_id

    def reject(self, user_id: str, reason: str) -> None:
        """
        Rejette le formulaire

        Args:
            user_id: ID de l'utilisateur qui rejette le formulaire
            reason: Raison du rejet
        """
        if self.status != FormStatus.SUBMITTED:
            raise ValueError("Seuls les formulaires soumis peuvent être rejetés")

        self.status = FormStatus.REJECTED
        self.approved_at = datetime.utcnow()
        self.approved_by = user_id
        self.rejection_reason = reason

    def archive(self) -> None:
        """Archive le formulaire"""
        if self.status not in [FormStatus.APPROVED, FormStatus.REJECTED]:
            raise ValueError("Seuls les formulaires approuvés ou rejetés peuvent être archivés")

        self.status = FormStatus.ARCHIVED
