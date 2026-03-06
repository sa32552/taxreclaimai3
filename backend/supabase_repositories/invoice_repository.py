
"""
Repository Supabase pour les factures
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.supabase_client import get_supabase_client

class SupabaseInvoiceRepository:
    """Repository Supabase pour les opérations CRUD sur les factures"""

    def __init__(self):
        """Initialise le repository"""
        self.supabase = get_supabase_client()

    def create(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une nouvelle facture

        Args:
            invoice_data: Données de la facture

        Returns:
            Facture créée
        """
        response = self.supabase.table("invoices").insert(invoice_data).execute()
        return response.data[0] if response.data else None

    def get_by_id(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une facture par son ID

        Args:
            invoice_id: ID de la facture

        Returns:
            Facture ou None si non trouvée
        """
        response = self.supabase.table("invoices").select("*").eq("id", invoice_id).single().execute()
        return response.data if response.data else None

    def get_by_number(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une facture par son numéro

        Args:
            invoice_number: Numéro de la facture

        Returns:
            Facture ou None si non trouvée
        """
        response = self.supabase.table("invoices").select("*").eq("invoice_number", invoice_number).single().execute()
        return response.data if response.data else None

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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
        query = self.supabase.table("invoices").select("*")

        if company_id:
            query = query.eq("company_id", company_id)

        if status:
            query = query.eq("status", status)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def update(self, invoice_id: str, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour une facture

        Args:
            invoice_id: ID de la facture
            invoice_data: Nouvelles données

        Returns:
            Facture mise à jour ou None
        """
        invoice_data["updated_at"] = datetime.utcnow().isoformat()

        response = self.supabase.table("invoices").update(invoice_data).eq("id", invoice_id).execute()
        return response.data[0] if response.data else None

    def delete(self, invoice_id: str) -> bool:
        """
        Supprime une facture

        Args:
            invoice_id: ID de la facture

        Returns:
            True si supprimée, False sinon
        """
        response = self.supabase.table("invoices").delete().eq("id", invoice_id).execute()
        return response.data is not None

    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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
        query = self.supabase.table("invoices").select("*").eq("company_id", company_id)

        if status:
            query = query.eq("status", status)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_by_supplier(
        self,
        supplier: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
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
        query = self.supabase.table("invoices").select("*").eq("supplier", supplier)

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_by_country(
        self,
        country: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
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
        query = self.supabase.table("invoices").select("*").eq("country", country)

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les factures par plage de dates

        Args:
            start_date: Date de début
            end_date: Date de fin
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures dans la plage de dates
        """
        query = self.supabase.table("invoices").select("*").gte("date", start_date.isoformat()).lte("date", end_date.isoformat())

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.range(skip, skip + limit - 1).order("date", desc=True).execute()
        return response.data if response.data else []

    def get_recoverable_invoices(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les factures éligibles à la récupération de TVA

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de factures à sauter
            limit: Nombre maximum de factures à retourner

        Returns:
            Liste des factures éligibles
        """
        query = self.supabase.table("invoices").select("*").eq("status", "processed").gt("vat_amount", 0).gte("extraction_confidence", 0.9)

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_by_status(
        self,
        status: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
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
        query = self.supabase.table("invoices").select("*").eq("status", status)

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def search(
        self,
        query: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
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
            ("invoice_number", "ilike", search_pattern),
            ("supplier", "ilike", search_pattern)
        ]

        db_query = self.supabase.table("invoices").select("*").or_(*filters)

        if company_id:
            db_query = db_query.eq("company_id", company_id)

        response = db_query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

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
        query = self.supabase.table("invoices").select("*").eq("company_id", company_id)

        if start_date:
            query = query.gte("date", start_date.isoformat())

        if end_date:
            query = query.lte("date", end_date.isoformat())

        response = query.execute()
        invoices = response.data if response.data else []

        total_amount = sum(invoice.get("total_amount", 0) for invoice in invoices)
        total_vat = sum(invoice.get("vat_amount", 0) for invoice in invoices)

        status_counts = {}
        for invoice in invoices:
            status = invoice.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_invoices": len(invoices),
            "total_amount": total_amount,
            "total_vat": total_vat,
            "status_counts": status_counts,
            "average_confidence": sum(
                invoice.get("extraction_confidence", 0) for invoice in invoices
            ) / len(invoices) if invoices else 0
        }

    def get_recent_invoices(
        self,
        company_id: str,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
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

        response = self.supabase.table("invoices").select("*").eq("company_id", company_id).gte("created_at", cutoff_date.isoformat()).limit(limit).order("created_at", desc=True).execute()
        return response.data if response.data else []
