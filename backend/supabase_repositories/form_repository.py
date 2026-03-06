
"""
Repository Supabase pour les formulaires
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.supabase_client import get_supabase_client

class SupabaseFormRepository:
    """Repository Supabase pour les opérations CRUD sur les formulaires"""

    def __init__(self):
        """Initialise le repository"""
        self.supabase = get_supabase_client()

    def create(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un nouveau formulaire

        Args:
            form_data: Données du formulaire

        Returns:
            Formulaire créé
        """
        response = self.supabase.table("forms").insert(form_data).execute()
        return response.data[0] if response.data else None

    def get_by_id(self, form_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un formulaire par son ID

        Args:
            form_id: ID du formulaire

        Returns:
            Formulaire ou None si non trouvé
        """
        response = self.supabase.table("forms").select("*").eq("id", form_id).single().execute()
        return response.data if response.data else None

    def get_by_form_number(self, form_number: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un formulaire par son numéro

        Args:
            form_number: Numéro du formulaire

        Returns:
            Formulaire ou None si non trouvé
        """
        response = self.supabase.table("forms").select("*").eq("form_number", form_number).single().execute()
        return response.data if response.data else None

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère tous les formulaires

        Args:
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner
            company_id: Filtrer par entreprise
            status: Filtrer par statut

        Returns:
            Liste des formulaires
        """
        query = self.supabase.table("forms").select("*")

        if company_id:
            query = query.eq("company_id", company_id)

        if status:
            query = query.eq("status", status)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def update(self, form_id: str, form_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour un formulaire

        Args:
            form_id: ID du formulaire
            form_data: Nouvelles données

        Returns:
            Formulaire mis à jour ou None
        """
        form_data["updated_at"] = datetime.utcnow().isoformat()

        response = self.supabase.table("forms").update(form_data).eq("id", form_id).execute()
        return response.data[0] if response.data else None

    def delete(self, form_id: str) -> bool:
        """
        Supprime un formulaire

        Args:
            form_id: ID du formulaire

        Returns:
            True si supprimé, False sinon
        """
        response = self.supabase.table("forms").delete().eq("id", form_id).execute()
        return response.data is not None

    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère les formulaires d'une entreprise

        Args:
            company_id: ID de l'entreprise
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner
            status: Filtrer par statut

        Returns:
            Liste des formulaires de l'entreprise
        """
        query = self.supabase.table("forms").select("*").eq("company_id", company_id)

        if status:
            query = query.eq("status", status)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_by_type(
        self,
        form_type: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les formulaires par type

        Args:
            form_type: Type de formulaire
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires du type spécifié
        """
        query = self.supabase.table("forms").select("*").eq("form_type", form_type)

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
        Récupère les formulaires par pays

        Args:
            country: Code pays ISO 3166-1 alpha-2
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires du pays
        """
        query = self.supabase.table("forms").select("*").eq("country", country)

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_by_vat_claim(
        self,
        vat_claim_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les formulaires d'une demande de récupération TVA

        Args:
            vat_claim_id: ID de la demande de récupération TVA
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires de la demande
        """
        response = self.supabase.table("forms").select("*").eq("vat_claim_id", vat_claim_id).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_by_status(
        self,
        status: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les formulaires par statut

        Args:
            status: Statut des formulaires
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires avec le statut spécifié
        """
        query = self.supabase.table("forms").select("*").eq("status", status)

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
        Récupère les formulaires par plage de dates

        Args:
            start_date: Date de début
            end_date: Date de fin
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires dans la plage de dates
        """
        query = self.supabase.table("forms").select("*").gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat())

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
        Recherche des formulaires

        Args:
            query: Terme de recherche
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires correspondant à la recherche
        """
        search_pattern = f"%{query}%"

        filters = [
            ("form_number", "ilike", search_pattern),
            ("external_reference", "ilike", search_pattern)
        ]

        db_query = self.supabase.table("forms").select("*").or_(*filters)

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
        Récupère les statistiques des formulaires

        Args:
            company_id: ID de l'entreprise
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)

        Returns:
            Dictionnaire avec les statistiques
        """
        query = self.supabase.table("forms").select("*").eq("company_id", company_id)

        if start_date:
            query = query.gte("created_at", start_date.isoformat())

        if end_date:
            query = query.lte("created_at", end_date.isoformat())

        response = query.execute()
        forms = response.data if response.data else []

        status_counts = {}
        for form in forms:
            status = form.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        type_counts = {}
        for form in forms:
            form_type = form.get("form_type", "unknown")
            type_counts[form_type] = type_counts.get(form_type, 0) + 1

        return {
            "total_forms": len(forms),
            "status_counts": status_counts,
            "type_counts": type_counts,
            "generated_count": sum(1 for form in forms if form.get("status") == "generated"),
            "submitted_count": sum(1 for form in forms if form.get("status") == "submitted"),
            "approved_count": sum(1 for form in forms if form.get("status") == "approved")
        }

    def get_recent_forms(
        self,
        company_id: str,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Récupère les formulaires récents

        Args:
            company_id: ID de l'entreprise
            days: Nombre de jours à considérer
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires récents
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        response = self.supabase.table("forms").select("*").eq("company_id", company_id).gte("created_at", cutoff_date.isoformat()).order("created_at", desc=True).limit(limit).execute()
        return response.data if response.data else []

    def get_forms_needing_action(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les formulaires nécessitant une action

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires nécessitant une action
        """
        # En production, cette méthode retournerait les formulaires en attente
        # Pour l'instant, nous retournons une liste vide
        return []
