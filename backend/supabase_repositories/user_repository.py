
"""
Repository Supabase pour les utilisateurs
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.supabase_client import get_supabase_client

class SupabaseUserRepository:
    """Repository Supabase pour les opérations CRUD sur les utilisateurs"""

    def __init__(self):
        """Initialise le repository"""
        self.supabase = get_supabase_client()

    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un nouvel utilisateur

        Args:
            user_data: Données de l'utilisateur

        Returns:
            Utilisateur créé
        """
        response = self.supabase.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un utilisateur par son ID

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        response = self.supabase.table("users").select("*").eq("id", user_id).single().execute()
        return response.data if response.data else None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un utilisateur par son email

        Args:
            email: Email de l'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        response = self.supabase.table("users").select("*").eq("email", email).single().execute()
        return response.data if response.data else None

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Récupère tous les utilisateurs

        Args:
            skip: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner
            active_only: Filtrer uniquement les utilisateurs actifs

        Returns:
            Liste des utilisateurs
        """
        query = self.supabase.table("users").select("*")

        if active_only:
            query = query.eq("is_active", True)

        response = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def update(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour un utilisateur

        Args:
            user_id: ID de l'utilisateur
            user_data: Nouvelles données

        Returns:
            Utilisateur mis à jour ou None
        """
        user_data["updated_at"] = datetime.utcnow().isoformat()

        response = self.supabase.table("users").update(user_data).eq("id", user_id).execute()
        return response.data[0] if response.data else None

    def delete(self, user_id: str) -> bool:
        """
        Supprime un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si supprimé, False sinon
        """
        response = self.supabase.table("users").delete().eq("id", user_id).execute()
        return response.data is not None

    def get_by_role(
        self,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les utilisateurs par rôle

        Args:
            role: Rôle à filtrer
            skip: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner

        Returns:
            Liste des utilisateurs avec le rôle spécifié
        """
        response = self.supabase.table("users").select("*").eq("role", role).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les utilisateurs par entreprise

        Args:
            company_id: ID de l'entreprise
            skip: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner

        Returns:
            Liste des utilisateurs de l'entreprise
        """
        response = self.supabase.table("users").select("*").eq("company_id", company_id).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return response.data if response.data else []

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Recherche des utilisateurs

        Args:
            query: Terme de recherche
            skip: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner

        Returns:
            Liste des utilisateurs correspondant à la recherche
        """
        search_pattern = f"%{query}%"

        response = self.supabase.table("users").select("*").or_(
            ("email", "ilike", search_pattern),
            ("first_name", "ilike", search_pattern),
            ("last_name", "ilike", search_pattern)
        ).range(skip, skip + limit - 1).order("created_at", desc=True).execute()

        return response.data if response.data else []

    def get_locked_accounts(self) -> List[Dict[str, Any]]:
        """
        Récupère les comptes verrouillés

        Returns:
            Liste des comptes verrouillés
        """
        response = self.supabase.table("users").select("*").not_("locked_until", "is", "null").gt("locked_until", datetime.utcnow().isoformat()).execute()
        return response.data if response.data else []

    def unlock_account(self, user_id: str) -> bool:
        """
        Déverrouille un compte

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si déverrouillé, False sinon
        """
        response = self.supabase.table("users").update({
            "failed_login_attempts": 0,
            "locked_until": None
        }).eq("id", user_id).execute()

        return response.data is not None

    def update_last_login(self, user_id: str) -> bool:
        """
        Met à jour la dernière connexion d'un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si mis à jour, False sinon
        """
        response = self.supabase.table("users").update({
            "last_login": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()

        return response.data is not None

    def increment_failed_attempts(
        self,
        user_id: str,
        max_attempts: int = 5,
        lockout_minutes: int = 30
    ) -> bool:
        """
        Incrémente les tentatives de connexion échouées

        Args:
            user_id: ID de l'utilisateur
            max_attempts: Nombre maximum de tentatives
            lockout_minutes: Durée du verrouillage

        Returns:
            True si le compte a été verrouillé, False sinon
        """
        # Récupérer l'utilisateur actuel
        user = self.get_by_id(user_id)
        if not user:
            return False

        # Incrémenter les tentatives
        new_attempts = user.get("failed_login_attempts", 0) + 1
        update_data = {"failed_login_attempts": new_attempts}

        # Verrouiller le compte si nécessaire
        is_locked = False
        if new_attempts >= max_attempts:
            is_locked = True
            lockout_time = datetime.utcnow() + timedelta(minutes=lockout_minutes)
            update_data["locked_until"] = lockout_time.isoformat()

        # Mettre à jour
        response = self.supabase.table("users").update(update_data).eq("id", user_id).execute()

        return is_locked and response.data is not None

    def reset_failed_attempts(self, user_id: str) -> bool:
        """
        Réinitialise les tentatives de connexion échouées

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si réinitialisé, False sinon
        """
        response = self.supabase.table("users").update({
            "failed_login_attempts": 0,
            "locked_until": None
        }).eq("id", user_id).execute()

        return response.data is not None

    def get_inactive_users(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Récupère les utilisateurs inactifs

        Args:
            days: Nombre de jours d'inactivité

        Returns:
            Liste des utilisateurs inactifs
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        response = self.supabase.table("users").select("*").lt("last_login", cutoff_date.isoformat()).execute()
        return response.data if response.data else []

    def count_by_role(self, role: str) -> int:
        """
        Compte les utilisateurs par rôle

        Args:
            role: Rôle à compter

        Returns:
            Nombre d'utilisateurs avec le rôle spécifié
        """
        response = self.supabase.table("users").select("id", count="exact").eq("role", role).execute()
        return response.count if hasattr(response, "count") else 0

    def count_by_company(self, company_id: str) -> int:
        """
        Compte les utilisateurs par entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Nombre d'utilisateurs de l'entreprise
        """
        response = self.supabase.table("users").select("id", count="exact").eq("company_id", company_id).eq("is_active", True).execute()
        return response.count if hasattr(response, "count") else 0
