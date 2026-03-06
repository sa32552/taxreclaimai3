
"""
Repository Supabase pour les demandes de récupération TVA
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.supabase_client import get_supabase_client

class SupabaseVATClaimRepository:
    """Repository Supabase pour les opérations CRUD sur les demandes de récupération TVA"""

    def __init__(self):
        """Initialise le repository"""
        self.supabase = get_supabase_client()

    def create(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une nouvelle demande de récupération TVA

        Args:
            claim_data: Données de la demande

        Returns:
            Demande créée
        """
        response = self.supabase.table("vat_claims").insert(claim_data).execute()
        return response.data[0] if response.data else None

    def get_by_id(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une demande par son ID

        Args:
            claim_id: ID de la demande

        Returns:
            Demande ou None si non trouvée
        """
        response = self.supabase.table("vat_claims").select("*").eq("id", claim_id).single().execute()
        return response.data if response.data else None

    def get_by_claim_number(self, claim_number: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une demande par son numéro

        Args:
            claim_number: Numéro de la demande

        Returns:
            Demande ou None si non trouvée
        """
        response = self.supabase.table("vat_claims").select("*").eq("claim_number", claim_number).single().execute()
        return response.data if response.data else None

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère toutes les demandes

        Args:
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner
            company_id: Filtrer par entreprise
            status: Filtrer par statut

        Returns:
            Liste des demandes
        """
        query = self.supabase.table("vat_claims").select("*")

        if company_id:
            query = query.eq("company_id", company_id)

        if status:
            query = query.eq("status", status)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def update(self, claim_id: str, claim_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour une demande

        Args:
            claim_id: ID de la demande
            claim_data: Nouvelles données

        Returns:
            Demande mise à jour ou None
        """
        claim_data["updated_at"] = datetime.utcnow().isoformat()

        response = self.supabase.table("vat_claims").update(claim_data).eq("id", claim_id).execute()
        return response.data[0] if response.data else None

    def delete(self, claim_id: str) -> bool:
        """
        Supprime une demande

        Args:
            claim_id: ID de la demande

        Returns:
            True si supprimée, False sinon
        """
        response = self.supabase.table("vat_claims").delete().eq("id", claim_id).execute()
        return response.data is not None

    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère les demandes d'une entreprise

        Args:
            company_id: ID de l'entreprise
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner
            status: Filtrer par statut

        Returns:
            Liste des demandes de l'entreprise
        """
        query = self.supabase.table("vat_claims").select("*").eq("company_id", company_id)

        if status:
            query = query.eq("status", status)

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
        Récupère les demandes par pays

        Args:
            country: Code pays ISO 3166-1 alpha-2
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes pour le pays
        """
        query = self.supabase.table("vat_claims").select("*").eq("target_country", country)

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
        Récupère les demandes par statut

        Args:
            status: Statut des demandes
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes avec le statut spécifié
        """
        query = self.supabase.table("vat_claims").select("*").eq("status", status)

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
        Récupère les demandes par plage de dates

        Args:
            start_date: Date de début
            end_date: Date de fin
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes dans la plage de dates
        """
        query = self.supabase.table("vat_claims").select("*").gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat())

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
        Recherche des demandes

        Args:
            query: Terme de recherche
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes correspondant à la recherche
        """
        search_pattern = f"%{query}%"

        filters = [
            ("claim_number", "ilike", search_pattern),
            ("external_reference", "ilike", search_pattern)
        ]

        db_query = self.supabase.table("vat_claims").select("*").or_(*filters)

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
        Récupère les statistiques des demandes

        Args:
            company_id: ID de l'entreprise
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)

        Returns:
            Dictionnaire avec les statistiques
        """
        query = self.supabase.table("vat_claims").select("*").eq("company_id", company_id)

        if start_date:
            query = query.gte("created_at", start_date.isoformat())

        if end_date:
            query = query.lte("created_at", end_date.isoformat())

        response = query.execute()
        claims = response.data if response.data else []

        total_recoverable = sum(claim.get("total_recoverable", 0) for claim in claims)
        total_approved = sum(claim.get("total_approved", 0) for claim in claims)
        total_rejected = sum(claim.get("total_rejected", 0) for claim in claims)

        status_counts = {}
        for claim in claims:
            status = claim.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_claims": len(claims),
            "total_recoverable": total_recoverable,
            "total_approved": total_approved,
            "total_rejected": total_rejected,
            "success_rate": (len(claims) - len([c for c in claims if c.get("status") == "rejected"])) / len(claims) * 100 if claims else 0,
            "status_counts": status_counts,
            "average_processing_time": self._calculate_average_processing_time(claims)
        }

    def _calculate_average_processing_time(self, claims: List[Dict[str, Any]]) -> float:
        """
        Calcule le temps moyen de traitement des demandes

        Args:
            claims: Liste des demandes

        Returns:
            Temps moyen de traitement en jours
        """
        completed_claims = [
            c for c in claims 
            if c.get("status") in ["approved", "completed"]
            and c.get("submitted_at") and c.get("approved_at")
        ]

        if not completed_claims:
            return 0.0

        total_time = sum(
            (
                datetime.fromisoformat(c["approved_at"]) - datetime.fromisoformat(c["submitted_at"])
            ).days 
            for c in completed_claims
        )

        return total_time / len(completed_claims)

    def get_pending_claims(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les demandes en attente

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes en attente
        """
        query = self.supabase.table("vat_claims").select("*").eq("status", "submitted")

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.range(skip, skip + limit - 1).order("submitted_at", asc=True).execute()
        return response.data if response.data else []

    def get_claims_needing_action(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les demandes nécessitant une action

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes nécessitant une action
        """
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        query = self.supabase.table("vat_claims").select("*").eq("status", "submitted").lt("submitted_at", cutoff_date.isoformat())

        if company_id:
            query = query.eq("company_id", company_id)

        response = query.range(skip, skip + limit - 1).order("submitted_at", asc=True).execute()
        return response.data if response.data else []

    def submit(self, claim_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Soumet une demande

        Args:
            claim_id: ID de la demande
            user_id: ID de l'utilisateur qui soumet

        Returns:
            Demande soumise ou None
        """
        # Générer un numéro de demande
        claim_number = f"VAT-{datetime.utcnow().strftime('%Y%m%d')}-{claim_id[:8].upper()}"

        update_data = {
            "claim_number": claim_number,
            "status": "submitted",
            "submitted_at": datetime.utcnow().isoformat(),
            "submitted_by": user_id,
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(claim_id, update_data)

    def approve(self, claim_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Approuve une demande

        Args:
            claim_id: ID de la demande
            user_id: ID de l'utilisateur qui approuve

        Returns:
            Demande approuvée ou None
        """
        update_data = {
            "status": "approved",
            "approved_at": datetime.utcnow().isoformat(),
            "approved_by": user_id,
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(claim_id, update_data)

    def reject(self, claim_id: str, user_id: str, reason: str) -> Optional[Dict[str, Any]]:
        """
        Rejette une demande

        Args:
            claim_id: ID de la demande
            user_id: ID de l'utilisateur qui rejette
            reason: Raison du rejet

        Returns:
            Demande rejetée ou None
        """
        update_data = {
            "status": "rejected",
            "approved_at": datetime.utcnow().isoformat(),
            "approved_by": user_id,
            "rejection_reason": reason,
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(claim_id, update_data)

    def cancel(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Annule une demande

        Args:
            claim_id: ID de la demande

        Returns:
            Demande annulée ou None
        """
        update_data = {
            "status": "cancelled",
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(claim_id, update_data)

    def complete(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Marque une demande comme terminée

        Args:
            claim_id: ID de la demande

        Returns:
            Demande terminée ou None
        """
        update_data = {
            "status": "completed",
            "updated_at": datetime.utcnow().isoformat()
        }

        return self.update(claim_id, update_data)
