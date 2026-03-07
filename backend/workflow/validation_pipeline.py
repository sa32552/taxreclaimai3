
"""
Pipeline de validation des factures
"""

from typing import List, Dict, Optional, Callable, Any, Tuple
from datetime import datetime
from enum import Enum
import uuid

class ValidationSeverity(str, Enum):
    """Sévérité des validations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationResult:
    """Résultat d'une validation"""

    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        severity: ValidationSeverity,
        message: str,
        is_passed: bool,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise un résultat de validation

        Args:
            rule_id: ID de la règle
            rule_name: Nom de la règle
            severity: Sévérité de la validation
            message: Message de validation
            is_passed: Indique si la validation est passée
            details: Détails supplémentaires
        """
        self.id = str(uuid.uuid4())
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.severity = severity
        self.message = message
        self.is_passed = is_passed
        self.details = details or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le résultat en dictionnaire

        Returns:
            Dictionnaire représentant le résultat
        """
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "is_passed": self.is_passed,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class ValidationRule:
    """Règle de validation"""

    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        description: str,
        severity: ValidationSeverity,
        validator: Callable[[Dict[str, Any]], ValidationResult],
        is_critical: bool = False
    ):
        """
        Initialise une règle de validation

        Args:
            rule_id: ID de la règle
            rule_name: Nom de la règle
            description: Description de la règle
            severity: Sévérité par défaut
            validator: Fonction de validation
            is_critical: Indique si la règle est critique
        """
        self.id = rule_id
        self.name = rule_name
        self.description = description
        self.severity = severity
        self.validator = validator
        self.is_critical = is_critical

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Valide les données

        Args:
            data: Données à valider

        Returns:
            Résultat de la validation
        """
        return self.validator(data)

class ValidationPipeline:
    """Pipeline de validation des factures"""

    def __init__(self):
        """Initialise le pipeline de validation"""
        self.rules: List[ValidationRule] = []
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Initialise les règles de validation par défaut"""
        from backend.services.vies_service import ViesService
        # Règle 1: Vérification du numéro de facture
        self.add_rule(ValidationRule(
            rule_id="invoice_number_required",
            rule_name="Numéro de facture requis",
            description="Vérifie que le numéro de facture est présent",
            severity=ValidationSeverity.ERROR,
            validator=lambda data: ValidationResult(
                rule_id="invoice_number_required",
                rule_name="Numéro de facture requis",
                severity=ValidationSeverity.ERROR,
                message="Le numéro de facture est requis" if not data.get("invoice_number") else "Numéro de facture valide",
                is_passed=bool(data.get("invoice_number"))
            ),
            is_critical=True
        ))

        # Règle 2: Vérification de la date
        self.add_rule(ValidationRule(
            rule_id="date_required",
            rule_name="Date de facture requise",
            description="Vérifie que la date de facture est présente et valide",
            severity=ValidationSeverity.ERROR,
            validator=lambda data: self._validate_date(data),
            is_critical=True
        ))

        # Règle 3: Vérification du fournisseur
        self.add_rule(ValidationRule(
            rule_id="supplier_required",
            rule_name="Fournisseur requis",
            description="Vérifie que le fournisseur est présent",
            severity=ValidationSeverity.ERROR,
            validator=lambda data: ValidationResult(
                rule_id="supplier_required",
                rule_name="Fournisseur requis",
                severity=ValidationSeverity.ERROR,
                message="Le fournisseur est requis" if not data.get("supplier") else "Fournisseur valide",
                is_passed=bool(data.get("supplier"))
            ),
            is_critical=True
        ))

        # Règle 4: Vérification des montants
        self.add_rule(ValidationRule(
            rule_id="amounts_valid",
            rule_name="Montants valides",
            description="Vérifie que les montants sont valides et cohérents",
            severity=ValidationSeverity.ERROR,
            validator=lambda data: self._validate_amounts(data),
            is_critical=True
        ))

        # Règle 5: Vérification du pays
        self.add_rule(ValidationRule(
            rule_id="country_valid",
            rule_name="Pays valide",
            description="Vérifie que le pays est valide",
            severity=ValidationSeverity.WARNING,
            validator=lambda data: ValidationResult(
                rule_id="country_valid",
                rule_name="Pays valide",
                severity=ValidationSeverity.WARNING,
                message="Le pays est requis et doit être un code ISO 3166-1 alpha-2" if not data.get("country") or len(data.get("country", "")) != 2 else "Pays valide",
                is_passed=bool(data.get("country") and len(data.get("country", "")) == 2)
            )
        ))

        # Règle 6: Vérification de la devise
        self.add_rule(ValidationRule(
            rule_id="currency_valid",
            rule_name="Devise valide",
            description="Vérifie que la devise est valide",
            severity=ValidationSeverity.WARNING,
            validator=lambda data: ValidationResult(
                rule_id="currency_valid",
                rule_name="Devise valide",
                severity=ValidationSeverity.WARNING,
                message="La devise est requise et doit être un code ISO 4217" if not data.get("currency") or len(data.get("currency", "")) != 3 else "Devise valide",
                is_passed=bool(data.get("currency") and len(data.get("currency", "")) == 3)
            )
        ))

        # Règle 7: Vérification de la confiance de l'extraction
        self.add_rule(ValidationRule(
            rule_id="extraction_confidence",
            rule_name="Confiance de l'extraction",
            description="Vérifie que la confiance de l'extraction est suffisante",
            severity=ValidationSeverity.WARNING,
            validator=lambda data: ValidationResult(
                rule_id="extraction_confidence",
                rule_name="Confiance de l'extraction",
                severity=ValidationSeverity.WARNING,
                message=f"La confiance de l'extraction est de {data.get('extraction_confidence', 0)*100:.1f}%. Un minimum de 90% est recommandé." if data.get('extraction_confidence', 0) < 0.9 else "Confiance de l'extraction suffisante",
                is_passed=data.get('extraction_confidence', 0) >= 0.9,
                details={"confidence": data.get('extraction_confidence', 0)}
            )
        ))

        # Règle 8: Vérification du numéro de TVA du fournisseur
        self.add_rule(ValidationRule(
            rule_id="supplier_vat_format",
            rule_name="Format du numéro de TVA du fournisseur",
            description="Vérifie le format du numéro de TVA du fournisseur",
            severity=ValidationSeverity.INFO,
            validator=lambda data: self._validate_vat_number(data)
        ))

        # Règle 9: Vérification VIES (Conformité EU)
        self.add_rule(ValidationRule(
            rule_id="vies_compliance",
            rule_name="Conformité VIES européenne",
            description="Vérifie que le numéro de TVA est actif dans le système VIES",
            severity=ValidationSeverity.ERROR,
            validator=lambda data: self._validate_vies(data),
            is_critical=False
        ))

    def _validate_date(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Valide la date de la facture

        Args:
            data: Données de la facture

        Returns:
            Résultat de la validation
        """
        date_str = data.get("date")

        if not date_str:
            return ValidationResult(
                rule_id="date_required",
                rule_name="Date de facture requise",
                severity=ValidationSeverity.ERROR,
                message="La date de facture est requise",
                is_passed=False
            )

        try:
            date = datetime.fromisoformat(date_str) if isinstance(date_str, str) else date_str

            # Vérifier que la date n'est pas dans le futur
            if date > datetime.utcnow():
                return ValidationResult(
                    rule_id="date_required",
                    rule_name="Date de facture requise",
                    severity=ValidationSeverity.WARNING,
                    message="La date de facture est dans le futur",
                    is_passed=False,
                    details={"date": date_str}
                )

            # Vérifier que la date n'est pas trop ancienne (plus de 5 ans)
            five_years_ago = datetime.utcnow().replace(year=datetime.utcnow().year - 5)
            if date < five_years_ago:
                return ValidationResult(
                    rule_id="date_required",
                    rule_name="Date de facture requise",
                    severity=ValidationSeverity.WARNING,
                    message="La date de facture est antérieure à 5 ans",
                    is_passed=False,
                    details={"date": date_str}
                )

            return ValidationResult(
                rule_id="date_required",
                rule_name="Date de facture requise",
                severity=ValidationSeverity.ERROR,
                message="Date de facture valide",
                is_passed=True,
                details={"date": date_str}
            )
        except Exception:
            return ValidationResult(
                rule_id="date_required",
                rule_name="Date de facture requise",
                severity=ValidationSeverity.ERROR,
                message="Format de date invalide",
                is_passed=False,
                details={"date": date_str}
            )

    def _validate_amounts(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Valide les montants de la facture

        Args:
            data: Données de la facture

        Returns:
            Résultat de la validation
        """
        amount_ht = data.get("amount_ht")
        vat_amount = data.get("vat_amount")
        total_amount = data.get("total_amount")

        # Vérifier que les montants sont présents
        if amount_ht is None or vat_amount is None or total_amount is None:
            return ValidationResult(
                rule_id="amounts_valid",
                rule_name="Montants valides",
                severity=ValidationSeverity.ERROR,
                message="Tous les montants sont requis (HT, TVA, TTC)",
                is_passed=False
            )

        # Vérifier que les montants sont positifs
        if amount_ht < 0 or vat_amount < 0 or total_amount < 0:
            return ValidationResult(
                rule_id="amounts_valid",
                rule_name="Montants valides",
                severity=ValidationSeverity.ERROR,
                message="Les montants doivent être positifs",
                is_passed=False,
                details={"amount_ht": amount_ht, "vat_amount": vat_amount, "total_amount": total_amount}
            )

        # Vérifier que HT + TVA = TTC (avec une tolérance de 0.01)
        expected_total = amount_ht + vat_amount
        if abs(total_amount - expected_total) > 0.01:
            return ValidationResult(
                rule_id="amounts_valid",
                rule_name="Montants valides",
                severity=ValidationSeverity.WARNING,
                message=f"Incohérence: HT ({amount_ht}) + TVA ({vat_amount}) ≠ TTC ({total_amount})",
                is_passed=False,
                details={"amount_ht": amount_ht, "vat_amount": vat_amount, "total_amount": total_amount, "expected_total": expected_total}
            )

        return ValidationResult(
            rule_id="amounts_valid",
            rule_name="Montants valides",
            severity=ValidationSeverity.ERROR,
            message="Montants valides",
            is_passed=True,
            details={"amount_ht": amount_ht, "vat_amount": vat_amount, "total_amount": total_amount}
        )

    def _validate_vat_number(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Valide le format du numéro de TVA

        Args:
            data: Données de la facture

        Returns:
            Résultat de la validation
        """
        vat_number = data.get("supplier_vat_number")

        if not vat_number:
            return ValidationResult(
                rule_id="supplier_vat_format",
                rule_name="Format du numéro de TVA du fournisseur",
                severity=ValidationSeverity.INFO,
                message="Numéro de TVA du fournisseur non fourni",
                is_passed=True,
                details={"vat_number": vat_number}
            )

        # Vérifier le format basique (2 lettres + 8-12 caractères alphanumériques)
        import re
        pattern = r'^[A-Z]{2}[A-Z0-9]{8,12}$'

        if not re.match(pattern, vat_number.upper()):
            return ValidationResult(
                rule_id="supplier_vat_format",
                rule_name="Format du numéro de TVA du fournisseur",
                severity=ValidationSeverity.WARNING,
                message="Format de numéro de TVA invalide. Attendu: XXXXXXXXXXXXX (2 lettres + 8-12 caractères alphanumériques)",
                is_passed=False,
                details={"vat_number": vat_number}
            )

        return ValidationResult(
            rule_id="supplier_vat_format",
            rule_name="Format du numéro de TVA du fournisseur",
            severity=ValidationSeverity.INFO,
            message="Numéro de TVA du fournisseur valide",
            is_passed=True,
            details={"vat_number": vat_number}
        )

    def _validate_vies(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Valide le numéro de TVA via VIES
        """
        from backend.services.vies_service import ViesService
        
        vat_number = data.get("vat_number") or data.get("supplier_vat_number")
        if not vat_number:
            return ValidationResult(
                rule_id="vies_compliance",
                rule_name="Conformité VIES européenne",
                severity=ValidationSeverity.WARNING,
                message="Numéro de TVA manquant pour vérification VIES",
                is_passed=False
            )
            
        is_valid, message = ViesService.validate_format(vat_number)
        
        return ValidationResult(
            rule_id="vies_compliance",
            rule_name="Conformité VIES européenne",
            severity=ValidationSeverity.ERROR if not is_valid else ValidationSeverity.INFO,
            message=f"VIES: {message}",
            is_passed=is_valid,
            details={"vat_number": vat_number, "vies_message": message}
        )

    def add_rule(self, rule: ValidationRule) -> None:
        """
        Ajoute une règle de validation

        Args:
            rule: Règle à ajouter
        """
        self.rules.append(rule)

    def remove_rule(self, rule_id: str) -> bool:
        """
        Supprime une règle de validation

        Args:
            rule_id: ID de la règle à supprimer

        Returns:
            True si la règle a été supprimée, False sinon
        """
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                self.rules.pop(i)
                return True
        return False

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationResult]]:
        """
        Valide les données avec toutes les règles

        Args:
            data: Données à valider

        Returns:
            Tuple (est_valide, résultats)
        """
        results = []

        for rule in self.rules:
            result = rule.validate(data)
            results.append(result)

        # Vérifier si toutes les règles critiques sont passées
        is_valid = all(
            result.is_passed
            for result in results
            if result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
        )

        return is_valid, results

    def get_rules(self) -> List[ValidationRule]:
        """
        Récupère toutes les règles de validation

        Returns:
            Liste des règles
        """
        return self.rules.copy()

    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """
        Récupère une règle par son ID

        Args:
            rule_id: ID de la règle

        Returns:
            Règle ou None si non trouvée
        """
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
