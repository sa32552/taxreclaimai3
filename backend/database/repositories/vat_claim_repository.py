
"""
Repository pour les demandes de récupération TVA
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.database.models.vat_claim import VATClaim, VATClaimStatus
from backend.database.base import get_db

class VATClaimRepository:
    """Repository pour les opérations CRUD sur les demandes de récupération TVA"""

    def __init__(self, db: Session):
        """
        Initialise le repository

        Args:
            db: Session de base de données
        """
        self.db = db

    def create(self, claim: VATClaim) -> VATClaim:
        """
        Crée une nouvelle demande de récupération TVA

        Args:
            claim: Demande à créer

        Returns:
            Demande créée
        """
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def get_by_id(self, claim_id: str) -> Optional[VATClaim]:
        """
        Récupère une demande par son ID

        Args:
            claim_id: ID de la demande

        Returns:
            Demande ou None si non trouvée
        """
        return self.db.query(VATClaim).filter(VATClaim.id == claim_id).first()

    def get_by_claim_number(self, claim_number: str) -> Optional[VATClaim]:
        """
        Récupère une demande par son numéro

        Args:
            claim_number: Numéro de la demande

        Returns:
            Demande ou None si non trouvée
        """
        return self.db.query(VATClaim).filter(VATClaim.claim_number == claim_number).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[VATClaimStatus] = None
    ) -> List[VATClaim]:
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
        query = self.db.query(VATClaim)

        if company_id:
            query = query.filter(VATClaim.company_id == company_id)

        if status:
            query = query.filter(VATClaim.status == status)

        return query.order_by(VATClaim.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, claim: VATClaim) -> VATClaim:
        """
        Met à jour une demande

        Args:
            claim: Demande à mettre à jour

        Returns:
            Demande mise à jour
        """
        claim.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def delete(self, claim_id: str) -> bool:
        """
        Supprime une demande

        Args:
            claim_id: ID de la demande

        Returns:
            True si supprimée, False sinon
        """
        claim = self.get_by_id(claim_id)
        if not claim:
            return False

        self.db.delete(claim)
        self.db.commit()
        return True

    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[VATClaimStatus] = None
    ) -> List[VATClaim]:
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
        query = self.db.query(VATClaim).filter(VATClaim.company_id == company_id)

        if status:
            query = query.filter(VATClaim.status == status)

        return query.order_by(VATClaim.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_country(
        self,
        country: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[VATClaim]:
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
        query = self.db.query(VATClaim).filter(VATClaim.target_country == country)

        if company_id:
            query = query.filter(VATClaim.company_id == company_id)

        return query.order_by(VATClaim.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_status(
        self,
        status: VATClaimStatus,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[VATClaim]:
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
        query = self.db.query(VATClaim).filter(VATClaim.status == status)

        if company_id:
            query = query.filter(VATClaim.company_id == company_id)

        return query.order_by(VATClaim.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[VATClaim]:
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
        query = self.db.query(VATClaim).filter(
            and_(
                VATClaim.created_at >= start_date,
                VATClaim.created_at <= end_date
            )
        )

        if company_id:
            query = query.filter(VATClaim.company_id == company_id)

        return query.order_by(VATClaim.created_at.desc()).offset(skip).limit(limit).all()

    def search(
        self,
        query: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[VATClaim]:
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
            VATClaim.claim_number.ilike(search_pattern),
            VATClaim.external_reference.ilike(search_pattern)
        ]

        db_query = self.db.query(VATClaim).filter(or_(*filters))

        if company_id:
            db_query = db_query.filter(VATClaim.company_id == company_id)

        return db_query.order_by(VATClaim.created_at.desc()).offset(skip).limit(limit).all()

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
        query = self.db.query(VATClaim).filter(VATClaim.company_id == company_id)

        if start_date:
            query = query.filter(VATClaim.created_at >= start_date)

        if end_date:
            query = query.filter(VATClaim.created_at <= end_date)

        claims = query.all()

        total_recoverable = sum(claim.total_recoverable for claim in claims)
        total_approved = sum(claim.total_approved for claim in claims)
        total_rejected = sum(claim.total_rejected for claim in claims)

        status_counts = {}
        for status in VATClaimStatus:
            status_counts[status.value] = sum(
                1 for claim in claims if claim.status == status
            )

        return {
            "total_claims": len(claims),
            "total_recoverable": total_recoverable,
            "total_approved": total_approved,
            "total_rejected": total_rejected,
            "success_rate": (len(claims) - len([c for c in claims if c.status == VATClaimStatus.REJECTED])) / len(claims) * 100 if claims else 0,
            "status_counts": status_counts,
            "average_processing_time": self._calculate_average_processing_time(claims)
        }

    def _calculate_average_processing_time(self, claims: List[VATClaim]) -> float:
        """
        Calcule le temps moyen de traitement des demandes

        Args:
            claims: Liste des demandes

        Returns:
            Temps moyen de traitement en jours
        """
        completed_claims = [
            c for c in claims 
            if c.status in [VATClaimStatus.APPROVED, VATClaimStatus.COMPLETED]
            and c.submitted_at and c.approved_at
        ]

        if not completed_claims:
            return 0.0

        total_time = sum(
            (c.approved_at - c.submitted_at).days 
            for c in completed_claims
        )

        return total_time / len(completed_claims)

    def get_pending_claims(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[VATClaim]:
        """
        Récupère les demandes en attente

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de demandes à sauter
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes en attente
        """
        query = self.db.query(VATClaim).filter(
            VATClaim.status == VATClaimStatus.SUBMITTED
        )

        if company_id:
            query = query.filter(VATClaim.company_id == company_id)

        return query.order_by(VATClaim.submitted_at.asc()).offset(skip).limit(limit).all()

    def get_claims_needing_action(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[VATClaim]:
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

        query = self.db.query(VATClaim).filter(
            and_(
                VATClaim.status == VATClaimStatus.SUBMITTED,
                VATClaim.submitted_at < cutoff_date
            )
        )

        if company_id:
            query = query.filter(VATClaim.company_id == company_id)

        return query.order_by(VATClaim.submitted_at.asc()).offset(skip).limit(limit).all()

    def get_recent_claims(
        self,
        company_id: str,
        days: int = 30,
        limit: int = 10
    ) -> List[VATClaim]:
        """
        Récupère les demandes récentes

        Args:
            company_id: ID de l'entreprise
            days: Nombre de jours à considérer
            limit: Nombre maximum de demandes à retourner

        Returns:
            Liste des demandes récentes
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return self.db.query(VATClaim).filter(
            and_(
                VATClaim.company_id == company_id,
                VATClaim.created_at >= cutoff_date
            )
        ).order_by(VATClaim.created_at.desc()).limit(limit).all()
