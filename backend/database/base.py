
"""
Module de base de données avec la classe Base SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuration de la base de données
# En production, utiliser PostgreSQL ou MySQL via Back4App
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./taxreclaim.db"  # Base de données locale pour le développement
)

# Créer le moteur de base de données
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Mettre à True pour voir les requêtes SQL
)

# Créer la session de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer la classe de base pour les modèles
Base = declarative_base()

def get_db():
    """
    Crée et gère une session de base de données

    Yields:
        Session de base de données
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialise la base de données en créant toutes les tables
    """
    from backend.database.models.user import User
    from backend.database.models.company import Company
    from backend.database.models.invoice import Invoice
    from backend.database.models.vat_claim import VATClaim
    from backend.database.models.form import Form

    Base.metadata.create_all(bind=engine)
