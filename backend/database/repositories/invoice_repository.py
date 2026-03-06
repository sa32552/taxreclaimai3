
"""
Repository pour les factures
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.database.models.invoice import Invoice, InvoiceStatus
from backend.database.base import get_db

class InvoiceRepository:
    """Repository pour les opérations CRUD sur les factures"""

    def __init__(self, db: Session):
        """
        Initialise le repository

        Args:
            db: Session de base de données
        """
        self.db = db

    def create(self, invoice: Invoice) -> Invoice:
        """
        Crée une nouvelle facture

        Args:
            invoice: Facture à créer

        Returns:
            Facture créée
        """
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """
        Récupère une facture par son ID

        Args:
            invoice_id: ID de la facture

        Returns:
            Facture ou None si non trouvée
        """
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """
        Récupère une facture par son numéro

        Args:
            invoice_number: Numéro de facture

        Returns:
            Facture ou None si non trouvée
        """
        return self.db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[InvoiceStatus] = None
    ) -> List[Invoice]:
        """
        Récupère toutes les factures

        Args:
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner
            company_id: Filtrer par entreprise
            status: Filtrer par statut

        Returns:
            Liste des factures
        """
        query = self.db.query(Invoice)

        if company_id:
            query = query.filter(Invoice.company_id == company_id)

        if status:
            query = query.filter(Invoice.status == status)

        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, invoice: Invoice) -> Invoice:
        """
        Met à jour une facture

        Args:
            invoice: Facture à mettre à jour

        Returns:
            Facture mise à jour
        """
        invoice.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def delete(self, invoice_id: str) -> bool:
        """
        Supprime une facture

        Args:
            invoice_id: ID de la facture

        Returns:
            True si supprimée, False sinon
        """
        invoice = self.get_by_id(invoice_id)
        if not invoice:
            return False

        self.db.delete(invoice)
        self.db.commit()
        return True

    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[InvoiceStatus] = None
    ) -> List[Invoice]:
        """
        Récupère les factures d'une entreprise

        Args:
            company_id: ID de l'entreprise
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner
            status: Filtrer par statut

        Returns:
            Liste des factures de l'entreprise
        """
        query = self.db.query(Invoice).filter(Invoice.company_id == company_id)

        if status:
            query = query.filter(Invoice.status == status)

        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_supplier(
        self,
        supplier: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Récupère les factures par fournisseur

        Args:
            supplier: Nom du fournisseur
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures du fournisseur
        """
        query = self.db.query(Invoice).filter(Invoice.supplier == supplier)

        if company_id:
            query = query.filter(Invoice.company_id == company_id)

        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_country(
        self,
        country: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Récupère les factures par pays

        Args:
            country: Code pays ISO 3166-1 alpha-2
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures du pays
        """
        query = self.db.query(Invoice).filter(Invoice.country == country)

        if company_id:
            query = query.filter(Invoice.company_id == company_id)

        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Récupère les factures par plage de dates

        Args:
            start_date: Date de début
            end_date: Date de fin
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de factures à sauter
            limit: Number maximum de factures à retourner

        Returns:
            Liste des factures dans la plage de dates
        """
        query = self.db.query(Invoice).filter(
            and_(
                Invoice.date >= start_date,
                Invoice.date <= end_date
            )
        )

        if company_id:
            query = query.filter(Invoice.company_id == company_id)

        return query.order_by(Invoice.date.desc()).offset(skip).limit(limit).all()

    def get_recoverable_invoices(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Récupère les factures éligibles à la récupération de TVA

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures éligibles
        """
        query = self.db.query(Invoice).filter(
            and_(
                Invoice.status == InvoiceStatus.PROCESSED,
                Invoice.vat_amount > 0,
                Invoice.extraction_confidence >= 0.9
            )
        )

        if company_id:
            query = query.filter(Invoice.company_id == company_id)

        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_status(
        self,
        status: InvoiceStatus,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Récupère les factures par statut

        Args:
            status: Statut des factures
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures avec le statut spécifié
        """
        query = self.db.query(Invoice).filter(Invoice.status == status)

        if company_id:
            query = query.filter(Invoice.company_id == company_id)

        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def search(
        self,
        query: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Recherche des factures

        Args:
            query: Terme de recherche
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures correspondant à la recherche
        """
        search_pattern = f"%{query}%"

        filters = [
            Invoice.invoice_number.ilike(search_pattern),
            Invoice.supplier.ilike(search_pattern)
        ]

        db_query = self.db.query(Invoice).filter(or_(*filters))

        if company_id:
            db_query = db_query.filter(Invoice.company_id == company_id)

        return db_query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def get_statistics(
        self,
        company_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques des factures

        Args:
            company_id: ID de l'entreprise
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)

        Returns:
            Dictionnaire avec les statistiques
        """
        query = self.db.query(Invoice).filter(Invoice.company_id == company_id)

        if start_date:
            query = query.filter(Invoice.date >= start_date)

        if end_date:
            query = query.filter(Invoice.date <= end_date)

        invoices = query.all()

        total_amount = sum(invoice.total_amount for invoice in invoices)
        total_vat = sum(invoice.vat_amount for invoice in invoices)
        recoverable_vat = sum(invoice.get_recoverable_amount() for invoice in invoices)

        status_counts = {}
        for status in InvoiceStatus:
            status_counts[status.value] = sum(
                1 for invoice in invoices if invoice.status == status
            )

        return {
            "total_invoices": len(invoices),
            "total_amount": total_amount,
            "total_vat": total_vat,
            "recoverable_vat": recoverable_vat,
            "status_counts": status_counts,
            "average_confidence": sum(
                invoice.extraction_confidence for invoice in invoices
            ) / len(invoices) if invoices else 0
        }

    def get_recent_invoices(
        self,
        company_id: str,
        days: int = 30,
        limit: int = 10
    ) -> List[Invoice]:
        """
        Récupère les factures récentes

        Args:
            company_id: ID de l'entreprise
            days: Nombre de jours à considérer
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures récentes
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return self.db.query(Invoice).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.created_at >= cutoff_date
            )
        ).order_by(Invoice.created_at.desc()).limit(limit).all()

    def count_by_status(
        self,
        status: InvoiceStatus,
        company_id: Optional[str] = None
    ) -> int:
        """
        Compte les factures par statut

        Args:
            status: Statut des factures
            company_id: ID de l'entreprise (optionnel)

        Returns:
            Nombre de factures avec le statut spécifié
        """
        query = self.db.query(Invoice).filter(Invoice.status == status)

        if company_id:
            query = query.filter(Invoice.company_id == company_id)

        return query.count()

    def count_by_company(self, company_id: str) -> int:
        """
        Compte les factures d'une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Nombre de factures de l'entreprise
        """
        return self.db.query(Invoice).filter(
            Invoice.company_id == company_id
        ).count()
