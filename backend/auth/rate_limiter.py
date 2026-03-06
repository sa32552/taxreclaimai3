
"""
Module de rate limiting pour protéger contre les attaques par force brute
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, status, Request
from collections import defaultdict
import time

class RateLimiter:
    """Gestionnaire de rate limiting"""

    def __init__(
        self,
        max_requests: int = 5,
        window_seconds: int = 60,
        cleanup_interval_seconds: int = 300
    ):
        """
        Initialise le gestionnaire de rate limiting

        Args:
            max_requests: Nombre maximum de requêtes autorisées
            window_seconds: Fenêtre de temps en secondes
            cleanup_interval_seconds: Intervalle de nettoyage en secondes
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.cleanup_interval_seconds = cleanup_interval_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.last_cleanup = time.time()

    def _cleanup_old_requests(self) -> None:
        """Nettoie les anciennes requêtes"""
        current_time = time.time()

        # Nettoyer périodiquement
        if current_time - self.last_cleanup > self.cleanup_interval_seconds:
            cutoff_time = current_time - self.window_seconds

            for key in list(self.requests.keys()):
                # Filtrer les requêtes récentes
                self.requests[key] = [
                    req_time for req_time in self.requests[key]
                    if req_time > cutoff_time
                ]

                # Supprimer les clés vides
                if not self.requests[key]:
                    del self.requests[key]

            self.last_cleanup = current_time

    def is_allowed(self, key: str) -> bool:
        """
        Vérifie si une requête est autorisée

        Args:
            key: Clé d'identification (IP, email, etc.)

        Returns:
            True si la requête est autorisée, False sinon
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Nettoyer les anciennes requêtes
        self._cleanup_old_requests()

        # Filtrer les requêtes récentes
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff_time
        ]

        # Vérifier si le nombre de requêtes est inférieur à la limite
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(current_time)
            return True

        return False

    def get_remaining_requests(self, key: str) -> int:
        """
        Récupère le nombre de requêtes restantes

        Args:
            key: Clé d'identification

        Returns:
            Nombre de requêtes restantes
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Filtrer les requêtes récentes
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff_time
        ]

        return max(0, self.max_requests - len(self.requests[key]))

    def get_reset_time(self, key: str) -> Optional[datetime]:
        """
        Récupère le moment de réinitialisation du rate limit

        Args:
            key: Clé d'identification

        Returns:
            Moment de réinitialisation ou None
        """
        if not self.requests[key]:
            return None

        # La première requête + la fenêtre de temps
        first_request = min(self.requests[key])
        return datetime.fromtimestamp(first_request + self.window_seconds)

# Rate limiters globaux
login_rate_limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 tentatives en 5 minutes
password_reset_rate_limiter = RateLimiter(max_requests=3, window_seconds=3600)  # 3 demandes en 1 heure
api_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)  # 100 requêtes par minute

async def check_rate_limit(
    request: Request,
    rate_limiter: RateLimiter,
    key_prefix: str = "rate_limit"
) -> None:
    """
    Vérifie le rate limit et lève une exception si dépassé

    Args:
        request: Requête HTTP
        rate_limiter: Rate limiter à utiliser
        key_prefix: Préfixe de la clé

    Raises:
        HTTPException: Si le rate limit est dépassé
    """
    # Utiliser l'IP comme clé
    client_ip = request.client.host if request.client else "unknown"
    key = f"{key_prefix}:{client_ip}"

    if not rate_limiter.is_allowed(key):
        reset_time = rate_limiter.get_reset_time(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de requêtes. Réessayez plus tard.",
            headers={
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": reset_time.isoformat() if reset_time else ""
            }
        )

    # Ajouter les headers de rate limit
    remaining = rate_limiter.get_remaining_requests(key)
    reset_time = rate_limiter.get_reset_time(key)

    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(rate_limiter.max_requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": reset_time.isoformat() if reset_time else ""
    }
