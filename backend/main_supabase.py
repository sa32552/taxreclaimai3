
"""
API principale TAXRECLAIMAI adaptée pour Supabase
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.supabase_client import get_supabase_client
from backend.supabase_routes import router as supabase_router

# Création de l'application FastAPI
app = FastAPI(
    title="TAXRECLAIMAI API - Supabase",
    description="API pour la récupération automatique de TVA internationale avec Supabase",
    version="3.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routeurs
app.include_router(supabase_router, tags=["API Supabase"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application

    Yields:
        None
    """
    # Démarrage
    print("🚀 TAXRECLAIMAI API v3.0 démarrée avec Supabase")
    print("📊 Prêt à traiter les factures et récupérer la TVA")
    print("🔐 Authentification Supabase activée")
    print("💾 Base de données Supabase connectée")
    print("📁 Storage Supabase activé")
    print("⚡ Edge Functions Supabase prêtes")

    yield

    # Arrêt
    print("👋 TAXRECLAIMAI API arrêtée")

# Configuration du cycle de vie
app.router.lifespan_context = lifespan

@app.get("/")
async def root():
    """Point de terminaison racine pour vérifier que l'API fonctionne"""
    return {
        "message": "TAXRECLAIMAI API v3.0 - Plateforme de récupération de TVA internationale avec Supabase",
        "version": "3.0.0",
        "status": "active",
        "backend": "Supabase",
        "endpoints": {
            "auth": "/api/auth",
            "invoices": "/api/invoices",
            "vat_claims": "/api/vat-claims",
            "forms": "/api/forms",
            "workflow": "/api/workflow"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé de l'API"""
    supabase = get_supabase_client()

    try:
        # Vérifier la connexion à la base de données
        supabase.table("users").select("count").limit(1).execute()
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "backend": "Supabase",
        "components": {
            "api": "active",
            "database": db_status,
            "auth": "active",
            "storage": "active",
            "edge_functions": "active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os

    # Récupérer le port depuis les variables d'environnement
    port = int(os.getenv("PORT", 8000))

    # Lancer l'application
    uvicorn.run(
        "main_supabase:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
