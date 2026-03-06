
"""
Repository pour les entreprises
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.database.models.company import Company
from backend.database.base import get_db

class CompanyRepository:
    """Repository pour les opérations CRUD sur les entreprises"""

    def __init__(self, db: Session):
        """
        Initialise le repository

        Args:
            db: Session de base de données
        """
        self.db = db

    def create(self, company: Company) -> Company:
        """
        Crée une nouvelle entreprise

        Args:
            company: Entreprise à créer

        Returns:
            Entreprise créée
        """
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get_by_id(self, company_id: str) -> Optional[Company]:
        """
        Récupère une entreprise par son ID

        Args:
            company_id: ID de l'entreprise

        Returns:
            Entreprise ou None si non trouvée
        """
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_by_vat_number(self, vat_number: str) -> Optional[Company]:
        """
        Récupère une entreprise par son numéro de TVA

        Args:
            vat_number: Numéro de TVA

        Returns:
            Entreprise ou None si non trouvée
        """
        return self.db.query(Company).filter(Company.vat_number == vat_number).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Company]:
        """
        Récupère toutes les entreprises

        Args:
            skip: Nombre d'entreprises à sauter
            limit: Nombre maximum d'entreprises à retourner
            active_only: Filtrer uniquement les entreprises actives

        Returns:
            Liste des entreprises
        """
        query = self.db.query(Company)

        if active_only:
            query = query.filter(Company.is_active == True)

        return query.offset(skip).limit(limit).all()

    def update(self, company: Company) -> Company:
        """
        Met à jour une entreprise

        Args:
            company: Entreprise à mettre à jour

        Returns:
            Entreprise mise à jour
        """
        company.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company_id: str) -> bool:
        """
        Supprime une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            True si supprimée, False sinon
        """
        company = self.get_by_id(company_id)
        if not company:
            return False

        self.db.delete(company)
        self.db.commit()
        return True

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Company]:
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

        return self.db.query(Company).filter(
            or_(
                Company.name.ilike(search_pattern),
                Company.vat_number.ilike(search_pattern),
                Company.city.ilike(search_pattern)
            )
        ).offset(skip).limit(limit).all()

    def get_by_country(
        self,
        country: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Company]:
        """
        Récupère les entreprises par pays

        Args:
            country: Code pays ISO 3166-1 alpha-2
            skip: Nombre d'entreprises à sauter
            limit: Nombre maximum d'entreprises à retourner

        Returns:
            Liste des entreprises du pays
        """
        return self.db.query(Company).filter(
            Company.country == country
        ).offset(skip).limit(limit).all()

    def get_verified_companies(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Company]:
        """
        Récupère les entreprises vérifiées

        Args:
            skip: Nombre d'entreprises à sauter
            limit: Nombre maximum d'entreprises à retourner

        Returns:
            Liste des entreprises vérifiées
        """
        return self.db.query(Company).filter(
            Company.is_verified == True,
            Company.is_active == True
        ).offset(skip).limit(limit).all()

    def get_inactive_companies(self, days: int = 90) -> List[Company]:
        """
        Récupère les entreprises inactives

        Args:
            days: Nombre de jours d'inactivité

        Returns:
            Liste des entreprises inactives
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return self.db.query(Company).filter(
            Company.updated_at < cutoff_date
        ).all()

    def count_by_subscription(self, subscription_plan: str) -> int:
        """
        Compte les entreprises par abonnement

        Args:
            subscription_plan: Type d'abonnement

        Returns:
            Nombre d'entreprises avec l'abonnement spécifié
        """
        return self.db.query(Company).filter(
            Company.subscription_plan == subscription_plan,
            Company.is_active == True
        ).count()

    def get_companies_near_user_limit(
        self,
        threshold: float = 0.9
    ) -> List[Company]:
        """
        Récupère les entreprises proches de leur limite d'utilisateurs

        Args:
            threshold: Seuil d'utilisation (défaut: 90%)

        Returns:
            Liste des entreprises proches de leur limite
        """
        companies = []

        for company in self.get_all(active_only=True):
            user_count = company.get_user_count()
            if user_count > 0 and (user_count / company.max_users) >= threshold:
                companies.append(company)

        return companies

    def get_companies_exceeding_invoice_limit(
        self,
        month: int,
        year: int
    ) -> List[Company]:
        """
        Récupère les entreprises dépassant leur limite de factures

        Args:
            month: Mois
            year: Année

        Returns:
            Liste des entreprises dépassant leur limite
        """
        # En production, cette méthode compterait les factures du mois
        # Pour l'instant, nous retournons une liste vide
        return []

    def update_subscription(
        self,
        company_id: str,
        subscription_plan: str,
        max_users: int,
        max_invoices_per_month: int
    ) -> Optional[Company]:
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
        company = self.get_by_id(company_id)
        if not company:
            return None

        company.subscription_plan = subscription_plan
        company.max_users = max_users
        company.max_invoices_per_month = max_invoices_per_month
        company.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(company)
        return company

    def verify_company(self, company_id: str) -> Optional[Company]:
        """
        Vérifie une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Entreprise vérifiée ou None
        """
        company = self.get_by_id(company_id)
        if not company:
            return None

        company.is_verified = True
        company.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(company)
        return company

    def deactivate_company(self, company_id: str) -> Optional[Company]:
        """
        Désactive une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Entreprise désactivée ou None
        """
        company = self.get_by_id(company_id)
        if not company:
            return None

        company.is_active = False
        company.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(company)
        return company

    def reactivate_company(self, company_id: str) -> Optional[Company]:
        """
        Réactive une entreprise

        Args:
            company_id: ID de l'entreprise

        Returns:
            Entreprise réactivée ou None
        """
        company = self.get_by_id(company_id)
        if not company:
            return None

        company.is_active = True
        company.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(company)
        return company
