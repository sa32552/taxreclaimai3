
"""
Repository pour les formulaires
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.database.models.form import Form, FormType, FormStatus
from backend.database.base import get_db

class FormRepository:
    """Repository pour les opérations CRUD sur les formulaires"""

    def __init__(self, db: Session):
        """
        Initialise le repository

        Args:
            db: Session de base de données
        """
        self.db = db

    def create(self, form: Form) -> Form:
        """
        Crée un nouveau formulaire

        Args:
            form: Formulaire à créer

        Returns:
            Formulaire créé
        """
        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        return form

    def get_by_id(self, form_id: str) -> Optional[Form]:
        """
        Récupère un formulaire par son ID

        Args:
            form_id: ID du formulaire

        Returns:
            Formulaire ou None si non trouvé
        """
        return self.db.query(Form).filter(Form.id == form_id).first()

    def get_by_form_number(self, form_number: str) -> Optional[Form]:
        """
        Récupère un formulaire par son numéro

        Args:
            form_number: Numéro du formulaire

        Returns:
            Formulaire ou None si non trouvé
        """
        return self.db.query(Form).filter(Form.form_number == form_number).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[str] = None,
        status: Optional[FormStatus] = None
    ) -> List[Form]:
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
        query = self.db.query(Form)

        if company_id:
            query = query.filter(Form.company_id == company_id)

        if status:
            query = query.filter(Form.status == status)

        return query.order_by(Form.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, form: Form) -> Form:
        """
        Met à jour un formulaire

        Args:
            form: Formulaire à mettre à jour

        Returns:
            Formulaire mis à jour
        """
        form.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(form)
        return form

    def delete(self, form_id: str) -> bool:
        """
        Supprime un formulaire

        Args:
            form_id: ID du formulaire

        Returns:
            True si supprimé, False sinon
        """
        form = self.get_by_id(form_id)
        if not form:
            return False

        self.db.delete(form)
        self.db.commit()
        return True

    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[FormStatus] = None
    ) -> List[Form]:
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
        query = self.db.query(Form).filter(Form.company_id == company_id)

        if status:
            query = query.filter(Form.status == status)

        return query.order_by(Form.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_type(
        self,
        form_type: FormType,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
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
        query = self.db.query(Form).filter(Form.form_type == form_type)

        if company_id:
            query = query.filter(Form.company_id == company_id)

        return query.order_by(Form.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_country(
        self,
        country: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
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
        query = self.db.query(Form).filter(Form.country == country)

        if company_id:
            query = query.filter(Form.company_id == company_id)

        return query.order_by(Form.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_vat_claim(
        self,
        vat_claim_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
        """
        Récupère les formulaires d'une demande de récupération TVA

        Args:
            vat_claim_id: ID de la demande de récupération TVA
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires de la demande
        """
        return self.db.query(Form).filter(
            Form.vat_claim_id == vat_claim_id
        ).order_by(Form.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_status(
        self,
        status: FormStatus,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
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
        query = self.db.query(Form).filter(Form.status == status)

        if company_id:
            query = query.filter(Form.company_id == company_id)

        return query.order_by(Form.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
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
        query = self.db.query(Form).filter(
            and_(
                Form.created_at >= start_date,
                Form.created_at <= end_date
            )
        )

        if company_id:
            query = query.filter(Form.company_id == company_id)

        return query.order_by(Form.created_at.desc()).offset(skip).limit(limit).all()

    def search(
        self,
        query: str,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
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
            Form.form_number.ilike(search_pattern),
            Form.external_reference.ilike(search_pattern)
        ]

        db_query = self.db.query(Form).filter(or_(*filters))

        if company_id:
            db_query = db_query.filter(Form.company_id == company_id)

        return db_query.order_by(Form.created_at.desc()).offset(skip).limit(limit).all()

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
        query = self.db.query(Form).filter(Form.company_id == company_id)

        if start_date:
            query = query.filter(Form.created_at >= start_date)

        if end_date:
            query = query.filter(Form.created_at <= end_date)

        forms = query.all()

        status_counts = {}
        for status in FormStatus:
            status_counts[status.value] = sum(
                1 for form in forms if form.status == status
            )

        type_counts = {}
        for form_type in FormType:
            type_counts[form_type.value] = sum(
                1 for form in forms if form.form_type == form_type
            )

        return {
            "total_forms": len(forms),
            "status_counts": status_counts,
            "type_counts": type_counts,
            "generated_count": sum(1 for form in forms if form.status == FormStatus.GENERATED),
            "submitted_count": sum(1 for form in forms if form.status == FormStatus.SUBMITTED),
            "approved_count": sum(1 for form in forms if form.status == FormStatus.APPROVED)
        }

    def get_recent_forms(
        self,
        company_id: str,
        days: int = 30,
        limit: int = 10
    ) -> List[Form]:
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

        return self.db.query(Form).filter(
            and_(
                Form.company_id == company_id,
                Form.created_at >= cutoff_date
            )
        ).order_by(Form.created_at.desc()).limit(limit).all()

    def get_forms_needing_action(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
        """
        Récupère les formulaires nécessitant une action

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires nécessitant une action
        """
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        query = self.db.query(Form).filter(
            and_(
                Form.status == FormStatus.GENERATED,
                Form.generated_at < cutoff_date
            )
        )

        if company_id:
            query = query.filter(Form.company_id == company_id)

        return query.order_by(Form.generated_at.asc()).offset(skip).limit(limit).all()

    def get_pending_forms(
        self,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Form]:
        """
        Récupère les formulaires en attente

        Args:
            company_id: ID de l'entreprise (optionnel)
            skip: Nombre de formulaires à sauter
            limit: Nombre maximum de formulaires à retourner

        Returns:
            Liste des formulaires en attente
        """
        query = self.db.query(Form).filter(
            Form.status == FormStatus.SUBMITTED
        )

        if company_id:
            query = query.filter(Form.company_id == company_id)

        return query.order_by(Form.submitted_at.asc()).offset(skip).limit(limit).all()
