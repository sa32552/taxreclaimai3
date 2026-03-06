
"""
Configuration mondiale des réglementations fiscales pour TAXRECLAIMAI
Ce module contient toutes les réglementations fiscales par pays et région
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class Continent(Enum):
    EUROPE = "europe"
    AMERICAS = "americas"
    ASIA = "asia"
    AFRICA = "africa"
    OCEANIA = "oceania"

class CountryTaxRegulation:
    """
    Classe représentant la réglementation fiscale d'un pays
    """
    def __init__(
        self,
        country_code: str,
        country_name: str,
        continent: Continent,
        currency: str,
        vat_rates: Dict[str, float],
        vat_thresholds: Dict[str, float],
        form_types: List[str],
        submission_deadlines: Dict[str, str],
        language_codes: List[str],
        special_rules: Dict[str, any],
        electronic_submission: bool,
        digital_signature_required: bool,
        retention_period_years: int,
        invoice_requirements: Dict[str, any],
        refund_process_days: int,
        cross_border_rules: Dict[str, any],
        updated_at: datetime
    ):
        self.country_code = country_code
        self.country_name = country_name
        self.continent = continent
        self.currency = currency
        self.vat_rates = vat_rates
        self.vat_thresholds = vat_thresholds
        self.form_types = form_types
        self.submission_deadlines = submission_deadlines
        self.language_codes = language_codes
        self.special_rules = special_rules
        self.electronic_submission = electronic_submission
        self.digital_signature_required = digital_signature_required
        self.retention_period_years = retention_period_years
        self.invoice_requirements = invoice_requirements
        self.refund_process_days = refund_process_days
        self.cross_border_rules = cross_border_rules
        self.updated_at = updated_at

# Réglementations fiscales par pays
COUNTRY_TAX_REGULATIONS = {
    # Europe
    "FR": CountryTaxRegulation(
        country_code="FR",
        country_name="France",
        continent=Continent.EUROPE,
        currency="EUR",
        vat_rates={
            "standard": 20.0,
            "reduced": 10.0,
            "super_reduced": 5.5,
            "special": 2.1
        },
        vat_thresholds={
            "registration": 85700,
            "payment": 85000
        },
        form_types=["FR_3310_CA3", "FR_3517_S", "FR_3310_CA12"],
        submission_deadlines={
            "monthly": "19th of following month",
            "quarterly": "19th of month following quarter",
            "annual": "Second working day after May 1st"
        },
        language_codes=["fr", "en"],
        special_rules={
            "reverse_charge": True,
            "intrastat_threshold": 460000,
            "european_sales_list": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=10,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_vat_number": True,
            "product_description": True,
            "tax_breakdown": True
        },
        refund_process_days=30,
        cross_border_rules={
            "eu_refund_form": "8th Directive",
            "non_eu_refund_form": "13th Directive"
        },
        updated_at=datetime(2024, 1, 1)
    ),

    "DE": CountryTaxRegulation(
        country_code="DE",
        country_name="Germany",
        continent=Continent.EUROPE,
        currency="EUR",
        vat_rates={
            "standard": 19.0,
            "reduced": 7.0
        },
        vat_thresholds={
            "registration": 22000,
            "payment": 17500
        },
        form_types=["DE_UST_VA", "DE_UST_1V"],
        submission_deadlines={
            "monthly": "10th of following month",
            "quarterly": "10th of month following quarter",
            "annual": "July 31st"
        },
        language_codes=["de", "en"],
        special_rules={
            "reverse_charge": True,
            "intrastat_threshold": 800000,
            "european_sales_list": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=10,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_vat_number": True,
            "product_description": True,
            "tax_breakdown": True
        },
        refund_process_days=30,
        cross_border_rules={
            "eu_refund_form": "8th Directive",
            "non_eu_refund_form": "13th Directive"
        },
        updated_at=datetime(2024, 1, 1)
    ),

    "GB": CountryTaxRegulation(
        country_code="GB",
        country_name="United Kingdom",
        continent=Continent.EUROPE,
        currency="GBP",
        vat_rates={
            "standard": 20.0,
            "reduced": 5.0,
            "zero": 0.0
        },
        vat_thresholds={
            "registration": 85000,
            "payment": 85000
        },
        form_types=["GB_VAT100", "GB_VAT100A"],
        submission_deadlines={
            "monthly": "Last day of second month following period end",
            "quarterly": "Last day of second month following quarter end",
            "annual": "Two months after year end"
        },
        language_codes=["en"],
        special_rules={
            "reverse_charge": True,
            "flat_rate_scheme": True,
            "annual_accounting_scheme": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=6,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_vat_number": True,
            "product_description": True,
            "tax_breakdown": True
        },
        refund_process_days=30,
        cross_border_rules={
            "eu_refund_form": "Post-Brexit arrangements",
            "non_eu_refund_form": "13th Directive equivalent"
        },
        updated_at=datetime(2024, 1, 1)
    ),

    # Amériques
    "US": CountryTaxRegulation(
        country_code="US",
        country_name="United States",
        continent=Continent.AMERICAS,
        currency="USD",
        vat_rates={
            "federal": 0.0,
            "state": "varies by state",
            "local": "varies by locality"
        },
        vat_thresholds={
            "registration": "varies by state",
            "payment": "varies by state"
        },
        form_types=["US_FORM_8849", "US_STATE_SPECIFIC"],
        submission_deadlines={
            "federal": "varies by form",
            "state": "varies by state"
        },
        language_codes=["en", "es"],
        special_rules={
            "no_federal_vat": True,
            "state_sales_tax": True,
            "nexus_rules": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=7,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_tax_id": True,
            "product_description": True,
            "tax_breakdown": True
        },
        refund_process_days=90,
        cross_border_rules={
            "import_tax": True,
            "export_exempt": True
        },
        updated_at=datetime(2024, 1, 1)
    ),

    "CA": CountryTaxRegulation(
        country_code="CA",
        country_name="Canada",
        continent=Continent.AMERICAS,
        currency="CAD",
        vat_rates={
            "gst": 5.0,
            "hst": "varies by province",
            "pst": "varies by province",
            "qst": 9.975
        },
        vat_thresholds={
            "registration": 30000,
            "payment": 30000
        },
        form_types=["CA_GST_HST_RETURN", "CA_GST189"],
        submission_deadlines={
            "monthly": "End of following month",
            "quarterly": "One month after quarter end",
            "annual": "Three months after year end"
        },
        language_codes=["en", "fr"],
        special_rules={
            "provincial_variations": True,
            "input_tax_credits": True,
            "small_supplier_exemption": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=7,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_tax_id": True,
            "product_description": True,
            "tax_breakdown": True
        },
        refund_process_days=60,
        cross_border_rules={
            "import_tax": True,
            "export_exempt": True,
            "nafta_rules": True
        },
        updated_at=datetime(2024, 1, 1)
    ),

    # Asie
    "CN": CountryTaxRegulation(
        country_code="CN",
        country_name="China",
        continent=Continent.ASIA,
        currency="CNY",
        vat_rates={
            "standard": 13.0,
            "reduced": 9.0,
            "low": 6.0,
            "export": 0.0
        },
        vat_thresholds={
            "registration": 500000,
            "payment": 500000
        },
        form_types=["CN_VAT_RETURN", "CN_SPECIAL_VAT_INVOICE"],
        submission_deadlines={
            "monthly": "15th of following month",
            "quarterly": "15th of month following quarter"
        },
        language_codes=["zh", "en"],
        special_rules={
            "golden_tax_system": True,
            "special_invoices": True,
            "small_scale_taxpayer": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=10,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_tax_id": True,
            "product_description": True,
            "tax_breakdown": True,
            "special_invoice_format": True
        },
        refund_process_days=60,
        cross_border_rules={
            "export_tax_rebates": True,
            "import_vat": True
        },
        updated_at=datetime(2024, 1, 1)
    ),

    "JP": CountryTaxRegulation(
        country_code="JP",
        country_name="Japan",
        continent=Continent.ASIA,
        currency="JPY",
        vat_rates={
            "standard": 10.0,
            "reduced": 8.0
        },
        vat_thresholds={
            "registration": 10000000,
            "payment": 10000000
        },
        form_types=["JP_CONSUMPTION_TAX_RETURN"],
        submission_deadlines={
            "monthly": "End of following month",
            "quarterly": "Two months after quarter end",
            "annual": "Two months after year end"
        },
        language_codes=["ja", "en"],
        special_rules={
            "invoice_system_2023": True,
            "qualified_invoice": True,
            "tax_exempt_enterprise": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=7,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_tax_id": True,
            "product_description": True,
            "tax_breakdown": True,
            "qualified_invoice_format": True
        },
        refund_process_days=60,
        cross_border_rules={
            "export_exempt": True,
            "import_consumption_tax": True
        },
        updated_at=datetime(2024, 1, 1)
    ),

    # Afrique
    "ZA": CountryTaxRegulation(
        country_code="ZA",
        country_name="South Africa",
        continent=Continent.AFRICA,
        currency="ZAR",
        vat_rates={
            "standard": 15.0,
            "zero": 0.0
        },
        vat_thresholds={
            "registration": 1000000,
            "payment": 1000000
        },
        form_types=["ZA_VAT201"],
        submission_deadlines={
            "monthly": "25th of following month",
            "bimonthly": "25th of second month following period",
            "six_monthly": "25th of month following period end"
        },
        language_codes=["en", "af", "zu", "xh", "nso"],
        special_rules={
            "vendor_categories": True,
            "second_hand_goods": True,
            "tourist_refund_scheme": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=5,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_tax_id": True,
            "product_description": True,
            "tax_breakdown": True,
            "vendor_declaration": True
        },
        refund_process_days=21,
        cross_border_rules={
            "export_zero_rated": True,
            "import_vat": True
        },
        updated_at=datetime(2024, 1, 1)
    ),

    # Océanie
    "AU": CountryTaxRegulation(
        country_code="AU",
        country_name="Australia",
        continent=Continent.OCEANIA,
        currency="AUD",
        vat_rates={
            "gst": 10.0
        },
        vat_thresholds={
            "registration": 75000,
            "payment": 75000
        },
        form_types=["AU_BAS", "AU_GST_RETURN"],
        submission_deadlines={
            "monthly": "21st of following month",
            "quarterly": "28th of month following quarter",
            "annual": "October 31st"
        },
        language_codes=["en"],
        special_rules={
            "gst_free": True,
            "input_taxed": True,
            "cash_basis": True
        },
        electronic_submission=True,
        digital_signature_required=True,
        retention_period_years=5,
        invoice_requirements={
            "sequential_numbering": True,
            "customer_abn": True,
            "product_description": True,
            "tax_breakdown": True
        },
        refund_process_days=14,
        cross_border_rules={
            "export_gst_free": True,
            "import_gst": True
        },
        updated_at=datetime(2024, 1, 1)
    )
}

def get_tax_regulation(country_code: str) -> Optional[CountryTaxRegulation]:
    """
    Récupère la réglementation fiscale pour un pays donné

    Args:
        country_code: Code ISO du pays

    Returns:
        CountryTaxRegulation ou None si non trouvé
    """
    return COUNTRY_TAX_REGULATIONS.get(country_code.upper())

def get_countries_by_continent(continent: Continent) -> List[CountryTaxRegulation]:
    """
    Récupère tous les pays d'un continent donné

    Args:
        continent: Continent à filtrer

    Returns:
        Liste des réglementations fiscales des pays du continent
    """
    return [
        regulation for regulation in COUNTRY_TAX_REGULATIONS.values()
        if regulation.continent == continent
    ]

def get_all_supported_countries() -> List[str]:
    """
    Récupère tous les codes pays supportés

    Returns:
        Liste des codes ISO des pays supportés
    """
    return list(COUNTRY_TAX_REGULATIONS.keys())

def get_vat_rates_by_country(country_code: str) -> Dict[str, float]:
    """
    Récupère les taux de TVA pour un pays donné

    Args:
        country_code: Code ISO du pays

    Returns:
        Dictionnaire des taux de TVA
    """
    regulation = get_tax_regulation(country_code)
    return regulation.vat_rates if regulation else {}

def get_form_types_by_country(country_code: str) -> List[str]:
    """
    Récupère les types de formulaires pour un pays donné

    Args:
        country_code: Code ISO du pays

    Returns:
        Liste des types de formulaires
    """
    regulation = get_tax_regulation(country_code)
    return regulation.form_types if regulation else []

def get_submission_deadlines_by_country(country_code: str) -> Dict[str, str]:
    """
    Récupère les délais de soumission pour un pays donné

    Args:
        country_code: Code ISO du pays

    Returns:
        Dictionnaire des délais de soumission
    """
    regulation = get_tax_regulation(country_code)
    return regulation.submission_deadlines if regulation else {}

def get_language_codes_by_country(country_code: str) -> List[str]:
    """
    Récupère les codes de langue pour un pays donné

    Args:
        country_code: Code ISO du pays

    Returns:
        Liste des codes de langue
    """
    regulation = get_tax_regulation(country_code)
    return regulation.language_codes if regulation else []
