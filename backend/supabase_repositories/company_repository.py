
"""
Repository Supabase pour les entreprises
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.supabase_client import get_supabase_client

class SupabaseCompanyRepository:
    """Repository Supabase pour les opérations CRUD sur les entreprises"""

    def __init__(self):
        """Initialise le repository"""
        self.supabase = get_supabase_client()

    def create(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une nouvelle entreprise

        Args:
            company_data: Données de l'entreprise

        Returns:
            Entreprise créée
        """
        response = self.supabase.table("companies").insert(company_data).execute()
        return response.data[0] if response.data else None

    def get_by_id(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une entreprise par son ID

        Args:
            company_id: ID de l'entreprise

        Returns:
            Entreprise ou None si non trouvée
        """
        response = self.supabase.table("companies").select("*").eq("id", company_id).single().execute()
        return response.data if response.data else None

    def get_by_vat_number(self, vat_number: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une entreprise par son numéro de TVA

        Args:
            vat_number: Numéro de TVA

        Returns:
            Entreprise ou None si non trouvée
        """
        response = self.supabase.table("companies").select("*").eq("vat_number", vat_number).single().execute()
        return response.data if response.data else None

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Récupère toutes les entreprises

        Args:
            skip: Nombre d'entreprises à sauter
            limit: Nombre maximum d'entreprises à retourner
            active_only: Filtrer uniquement les entreprises actives

        Returns:
            Liste des entreprises
        """
        query = self.supabase.table("companies").select("*")

        if active_only:
            query = query.eq("is_active", True)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def update(self, company_id: str, company_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour une entreprise

        Args:
            company_id: ID de l'entreprise
            company_data: Nouvelles données

        Returns:
            Entreprise mise à jour ou None
        """
        company_data["updated_at"] = datetime.utcnow().isoformat()

        response = self.supabase.table("companies").update(company_data).eq("id", company_id).execute()
        return response.data[0] if response.data else None

    def delete(self, company_id: str) -> bool:
        """
        Supprime une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            True si supprimée, False sinon
        """
        response = self.supabase.table("companies").delete().eq("id", company_id).execute()
        return response.data is not None

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Recherche des entreprises

        Args:
            query: Terme de recherche
            skip: Nombre d'entreprises à sauter
            limit: Nombre maximum d'entreprises à retourner

        Returns:
            Liste des entreprises correspondant à la recherche
        """
        search_pattern = f"%{query}%"

        response = self.supabase.table("companies").select("*").or_(
            ("name", "ilike", search_pattern),
            ("vat_number", "ilike", search_pattern),
            ("city", "ilike", search_pattern)
        ).range(skip, skip + limit - 1).order("created_at", desc=True).execute()

        return response.data if response.data else []

    def get_by_country(
        self,
        country: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les entreprises par pays

        Args:
            country: Code pays ISO 3166-1 alpha-2
            skip: Nombre d'entreprises à sauter
            limit: Nombre maximum d'entreprises à retourner

        Returns:
            Liste des entreprises du pays
        """
        response = self.supabase.table("companies").select("*").eq("country", country).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_verified_companies(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les entreprises vérifiées

        Args:
            skip: Nombre d'entreprises à sauter
            limit: Nombre maximum d'entreprises à retourner

        Returns:
            Liste des entreprises vérifiées
        """
        response = self.supabase.table("companies").select("*").eq("is_verified", True).eq("is_active", True).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_inactive_companies(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Récupère les entreprises inactives

        Args:
            days: Nombre de jours d'inactivité

        Returns:
            Liste des entreprises inactives
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        response = self.supabase.table("companies").select("*").lt("updated_at", cutoff_date.isoformat()).execute()
        return response.data if response.data else []

    def count_by_subscription(self, subscription_plan: str) -> int:
        """
        Compte les entreprises par abonnement

        Args:
            subscription_plan: Type d'abonnement

        Returns:
            Nombre d'entreprises avec l'abonnement spécifié
        """
        response = self.supabase.table("companies").select("id", count="exact").eq("subscription_plan", subscription_plan).eq("is_active", True).execute()
        return response.count if hasattr(response, "count") else 0

    def get_companies_near_user_limit(
        self,
        threshold: float = 0.9
    ) -> List[Dict[str, Any]]:
        """
        Récupère les entreprises proches de leur limite d'utilisateurs

        Args:
            threshold: Seuil d'utilisation (défaut: 90%)

        Returns:
            Liste des entreprises proches de leur limite
        """
        # En production, cette méthode compterait les utilisateurs
        # Pour l'instant, nous retournons une liste vide
        return []

    def get_companies_exceeding_invoice_limit(
        self,
        month: int,
        year: int
    ) -> List[Dict[str, Any]]:
        """
        Récupère les entreprises dépassant leur limite de factures

        Args:
            month: Mois
            year: Année

        Returns:
            Liste des entreprises dépassant leur limite
        """
        # En production, cette méthode compterait les factures
        # Pour l'instant, nous retournons une liste vide
        return []

    def update_subscription(
        self,
        company_id: str,
        subscription_plan: str,
        max_users: int,
        max_invoices_per_month: int
    ) -> Optional[Dict[str, Any]]:
        """
        Met à jour l'abonnement d'une entreprise

        Args:
            company_id: ID de l'entreprise
            subscription_plan: Nouveau type d'abonnement
            max_users: Nouveau nombre maximum d'utilisateurs
            max_invoices_per_month: Nouveau nombre maximum de factures

        Returns:
            Entreprise mise à jour ou None
        """
        update_data = {
            "subscription_plan": subscription_plan,
            "max_users": max_users,
            "max_invoices_per_month": max_invoices_per_month,
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(company_id, update_data)

    def verify_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Vérifie une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Entreprise vérifiée ou None
        """
        update_data = {
            "is_verified": True,
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(company_id, update_data)

    def deactivate_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Désactive une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Entreprise désactivée ou None
        """
        update_data = {
            "is_active": False,
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(company_id, update_data)

    def reactivate_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Réactive une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Entreprise réactivée ou None
        """
        update_data = {
            "is_active": True,
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(company_id, update_data)
