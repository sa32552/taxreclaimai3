
"""
Repository pour les utilisateurs
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.database.models.user import User, UserRole
from backend.database.base import get_db

class UserRepository:
    """Repository pour les opérations CRUD sur les utilisateurs"""

    def __init__(self, db: Session):
        """
        Initialise le repository

        Args:
            db: Session de base de données
        """
        self.db = db

    def create(self, user: User) -> User:
        """
        Crée un nouvel utilisateur

        Args:
            user: Utilisateur à créer

        Returns:
            Utilisateur créé
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Récupère un utilisateur par son ID

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email

        Args:
            email: Email de l'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[User]:
        """
        Récupère tous les utilisateurs

        Args:
            skip: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner
            active_only: Filtrer uniquement les utilisateurs actifs

        Returns:
            Liste des utilisateurs
        """
        query = self.db.query(User)

        if active_only:
            query = query.filter(User.is_active == True)

        return query.offset(skip).limit(limit).all()

    def update(self, user: User) -> User:
        """
        Met à jour un utilisateur

        Args:
            user: Utilisateur à mettre à jour

        Returns:
            Utilisateur mis à jour
        """
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> bool:
        """
        Supprime un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si supprimé, False sinon
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Récupère les utilisateurs par rôle

        Args:
            role: Rôle à filtrer
            skip: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner

        Returns:
            Liste des utilisateurs avec le rôle spécifié
        """
        return self.db.query(User).filter(
            User.role == role
        ).offset(skip).limit(limit).all()

    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Récupère les utilisateurs par entreprise

        Args:
            company_id: ID de l'entreprise
            skip: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs à retourner

        Returns:
            Liste des utilisateurs de l'entreprise
        """
        return self.db.query(User).filter(
            User.company_id == company_id
        ).offset(skip).limit(limit).all()

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
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

        return self.db.query(User).filter(
            or_(
                User.email.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern)
            )
        ).offset(skip).limit(limit).all()

    def get_locked_accounts(self) -> List[User]:
        """
        Récupère les comptes verrouillés

        Returns:
            Liste des comptes verrouillés
        """
        return self.db.query(User).filter(
            User.locked_until.isnot(None),
            User.locked_until > datetime.utcnow()
        ).all()

    def unlock_account(self, user_id: str) -> bool:
        """
        Déverrouille un compte

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si déverrouillé, False sinon
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.unlock()
        self.db.commit()
        return True

    def update_last_login(self, user_id: str) -> bool:
        """
        Met à jour la dernière connexion d'un utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si mis à jour, False sinon
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.last_login = datetime.utcnow()
        self.db.commit()
        return True

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
        user = self.get_by_id(user_id)
        if not user:
            return False

        is_locked = user.increment_failed_attempts(max_attempts, lockout_minutes)
        self.db.commit()
        return is_locked

    def reset_failed_attempts(self, user_id: str) -> bool:
        """
        Réinitialise les tentatives de connexion échouées

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si réinitialisé, False sinon
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.reset_failed_attempts()
        self.db.commit()
        return True

    def get_inactive_users(self, days: int = 90) -> List[User]:
        """
        Récupère les utilisateurs inactifs

        Args:
            days: Nombre de jours d'inactivité

        Returns:
            Liste des utilisateurs inactifs
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return self.db.query(User).filter(
            User.last_login < cutoff_date
        ).all()

    def count_by_role(self, role: UserRole) -> int:
        """
        Compte les utilisateurs par rôle

        Args:
            role: Rôle à compter

        Returns:
            Nombre d'utilisateurs avec le rôle spécifié
        """
        return self.db.query(User).filter(
            User.role == role
        ).count()

    def count_by_company(self, company_id: str) -> int:
        """
        Compte les utilisateurs par entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Nombre d'utilisateurs de l'entreprise
        """
        return self.db.query(User).filter(
            User.company_id == company_id,
            User.is_active == True
        ).count()
