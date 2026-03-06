
"""
Module de storage Supabase
"""

from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException, status
import os
from datetime import datetime

from backend.supabase_client import get_storage_client

class SupabaseStorageService:
    """Service de storage Supabase"""

    def __init__(self):
        """Initialise le service de storage"""
        self.storage = get_storage_client()

    async def upload_file(
        self,
        file: UploadFile,
        bucket: str = "invoices",
        folder: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Télécharge un fichier vers Supabase Storage

        Args:
            file: Fichier à télécharger
            bucket: Bucket de destination
            folder: Dossier de destination (optionnel)
            user_id: ID de l'utilisateur (optionnel)

        Returns:
            Informations sur le fichier téléchargé

        Raises:
            HTTPException: Si le téléchargement échoue
        """
        try:
            # Créer le chemin du fichier
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"

            if folder:
                if user_id:
                    path = f"{bucket}/{folder}/{user_id}/{filename}"
                else:
                    path = f"{bucket}/{folder}/{filename}"
            else:
                if user_id:
                    path = f"{bucket}/{user_id}/{filename}"
                else:
                    path = f"{bucket}/{filename}"

            # Lire le contenu du fichier
            content = await file.read()

            # Télécharger le fichier
            self.storage.from_(bucket).upload(
                path=path,
                file=content,
                file_options={"content-type": file.content_type}
            )

            # Récupérer l'URL publique
            public_url = self.storage.from_(bucket).get_public_url(path)

            return {
                "filename": filename,
                "path": path,
                "url": public_url,
                "size": len(content),
                "content_type": file.content_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors du téléchargement: {str(e)}"
            )

    async def upload_batch(
        self,
        files: List[UploadFile],
        bucket: str = "invoices",
        folder: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Télécharge plusieurs fichiers vers Supabase Storage

        Args:
            files: Liste des fichiers à télécharger
            bucket: Bucket de destination
            folder: Dossier de destination (optionnel)
            user_id: ID de l'utilisateur (optionnel)

        Returns:
            Liste des informations sur les fichiers téléchargés

        Raises:
            HTTPException: Si le téléchargement échoue
        """
        results = []

        for file in files:
            result = await self.upload_file(file, bucket, folder, user_id)
            results.append(result)

        return results

    async def download_file(
        self,
        path: str,
        bucket: str = "invoices"
    ) -> bytes:
        """
        Télécharge un fichier depuis Supabase Storage

        Args:
            path: Chemin du fichier
            bucket: Bucket source

        Returns:
            Contenu du fichier

        Raises:
            HTTPException: Si le téléchargement échoue
        """
        try:
            response = self.storage.from_(bucket).download(path)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fichier non trouvé: {str(e)}"
            )

    async def delete_file(
        self,
        path: str,
        bucket: str = "invoices"
    ) -> Dict[str, str]:
        """
        Supprime un fichier de Supabase Storage

        Args:
            path: Chemin du fichier
            bucket: Bucket source

        Returns:
            Message de confirmation

        Raises:
            HTTPException: Si la suppression échoue
        """
        try:
            self.storage.from_(bucket).remove([path])
            return {"message": "Fichier supprimé avec succès"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la suppression: {str(e)}"
            )

    async def list_files(
        self,
        bucket: str = "invoices",
        folder: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Liste les fichiers dans Supabase Storage

        Args:
            bucket: Bucket source
            folder: Dossier (optionnel)
            user_id: ID de l'utilisateur (optionnel)

        Returns:
            Liste des fichiers

        Raises:
            HTTPException: Si la liste échoue
        """
        try:
            # Construire le chemin
            if folder and user_id:
                path = f"{folder}/{user_id}"
            elif folder:
                path = folder
            elif user_id:
                path = user_id
            else:
                path = ""

            # Lister les fichiers
            files = self.storage.from_(bucket).list(path=path)

            # Formater les résultats
            results = []
            for file in files:
                results.append({
                    "name": file.name,
                    "path": f"{path}/{file.name}" if path else file.name,
                    "size": file.metadata.get("size", 0),
                    "created_at": file.created_at,
                    "url": self.storage.from_(bucket).get_public_url(f"{path}/{file.name}" if path else file.name)
                })

            return results
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la liste: {str(e)}"
            )

    async def get_file_url(
        self,
        path: str,
        bucket: str = "invoices",
        expires_in: int = 3600
    ) -> str:
        """
        Récupère une URL signée pour un fichier

        Args:
            path: Chemin du fichier
            bucket: Bucket source
            expires_in: Durée de validité en secondes

        Returns:
            URL signée

        Raises:
            HTTPException: Si la récupération échoue
        """
        try:
            # Créer une URL signée
            signed_url = self.storage.from_(bucket).create_signed_url(
                path=path,
                expires_in=expires_in
            )

            return signed_url
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création de l'URL: {str(e)}"
            )

# Instance globale du service de storage
storage_service = SupabaseStorageService()
