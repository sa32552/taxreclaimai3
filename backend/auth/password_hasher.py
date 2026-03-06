
"""
Module de gestion des mots de passe avec hachage bcrypt
"""

import bcrypt
from typing import Union

class PasswordHasher:
    """Gestionnaire de hachage des mots de passe"""

    def __init__(self, rounds: int = 12):
        """
        Initialise le gestionnaire de hachage

        Args:
            rounds: Nombre de rounds pour le hachage bcrypt (défaut: 12)
        """
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        """
        Hache un mot de passe

        Args:
            password: Mot de passe en clair

        Returns:
            Mot de passe haché
        """
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie un mot de passe

        Args:
            plain_password: Mot de passe en clair
            hashed_password: Mot de passe haché

        Returns:
            True si le mot de passe est correct, False sinon
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    def is_password_strong(self, password: str) -> tuple[bool, str]:
        """
        Vérifie la force d'un mot de passe

        Args:
            password: Mot de passe à vérifier

        Returns:
            Tuple (est_fort, message_erreur)
        """
        if len(password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères"

        if len(password) > 100:
            return False, "Le mot de passe ne peut pas dépasser 100 caractères"

        if not any(char.isupper() for char in password):
            return False, "Le mot de passe doit contenir au moins une majuscule"

        if not any(char.islower() for char in password):
            return False, "Le mot de passe doit contenir au moins une minuscule"

        if not any(char.isdigit() for char in password):
            return False, "Le mot de passe doit contenir au moins un chiffre"

        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            return False, "Le mot de passe doit contenir au moins un caractère spécial"

        return True, ""

# Instance globale du gestionnaire de hachage
password_hasher = PasswordHasher()
