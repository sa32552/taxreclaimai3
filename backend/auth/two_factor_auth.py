
"""
Module d'authentification à deux facteurs (2FA) avec TOTP
"""

import pyotp
import qrcode
from io import BytesIO
from base64 import b64encode
from typing import Tuple, List
from fastapi import HTTPException, status
from backend.auth.models import TwoFactorSetup, TwoFactorVerify

class TwoFactorAuth:
    """Gestionnaire d'authentification à deux facteurs"""

    def __init__(self, issuer_name: str = "TAXRECLAIMAI"):
        """
        Initialise le gestionnaire 2FA

        Args:
            issuer_name: Nom de l'émetteur (affiché dans l'app d'authentification)
        """
        self.issuer_name = issuer_name

    def generate_secret(self) -> str:
        """
        Génère un secret TOTP

        Returns:
            Secret TOTP
        """
        return pyotp.random_base32()

    def generate_qr_code(self, email: str, secret: str) -> str:
        """
        Génère un QR code pour la configuration 2FA

        Args:
            email: Email de l'utilisateur
            secret: Secret TOTP

        Returns:
            QR code en base64
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=self.issuer_name
        )

        # Générer le QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convertir en base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Génère des codes de secours

        Args:
            count: Nombre de codes à générer

        Returns:
            Liste des codes de secours
        """
        import secrets
        import string

        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.digits) for _ in range(8))
            codes.append(code)

        return codes

    def setup_two_factor(self, email: str) -> TwoFactorSetup:
        """
        Configure l'authentification à deux facteurs pour un utilisateur

        Args:
            email: Email de l'utilisateur

        Returns:
            Configuration 2FA avec secret, QR code et codes de secours
        """
        secret = self.generate_secret()
        qr_code_url = self.generate_qr_code(email, secret)
        backup_codes = self.generate_backup_codes()

        return TwoFactorSetup(
            secret=secret,
            qr_code_url=qr_code_url,
            backup_codes=backup_codes
        )

    def verify_totp(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Vérifie un code TOTP

        Args:
            secret: Secret TOTP
            code: Code à vérifier
            valid_window: Fenêtre de validité en périodes (défaut: 1)

        Returns:
            True si le code est valide, False sinon
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)

    def verify_backup_code(self, user_backup_codes: List[str], code: str) -> Tuple[bool, List[str]]:
        """
        Vérifie un code de secours

        Args:
            user_backup_codes: Liste des codes de secours de l'utilisateur
            code: Code à vérifier

        Returns:
            Tuple (est_valide, codes_restants)
        """
        if code in user_backup_codes:
            # Supprimer le code utilisé
            remaining_codes = [c for c in user_backup_codes if c != code]
            return True, remaining_codes

        return False, user_backup_codes

    def verify_two_factor(
        self,
        secret: str,
        backup_codes: List[str],
        verification: TwoFactorVerify
    ) -> Tuple[bool, Optional[List[str]]]:
        """
        Vérifie l'authentification à deux facteurs

        Args:
            secret: Secret TOTP
            backup_codes: Liste des codes de secours
            verification: Données de vérification

        Returns:
            Tuple (est_valide, codes_de_secours_restants)
        """
        # Essayer d'abord avec le code TOTP
        if self.verify_totp(secret, verification.code):
            return True, None

        # Sinon, essayer avec un code de secours
        is_valid, remaining_codes = self.verify_backup_code(backup_codes, verification.code)
        return is_valid, remaining_codes if is_valid else None

# Instance globale du gestionnaire 2FA
two_factor_auth = TwoFactorAuth()
