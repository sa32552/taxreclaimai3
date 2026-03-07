
"""
Module de signature numérique pour le workflow
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import hashlib
import json

class SignatureType(str, Enum):
    """Types de signatures"""
    APPROVAL = "approval"
    REJECTION = "rejection"
    SUBMISSION = "submission"
    ACCEPTANCE = "acceptance"

class SignatureStatus(str, Enum):
    """Statuts des signatures"""
    VALID = "valid"
    INVALID = "invalid"
    REVOKED = "revoked"
    EXPIRED = "expired"

class DigitalSignature:
    """Signature numérique"""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        signature_type: SignatureType,
        signer_id: str,
        signer_name: str,
        signer_role: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise une signature numérique

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            signature_type: Type de signature
            signer_id: ID du signataire
            signer_name: Nom du signataire
            signer_role: Rôle du signataire
            data: Données supplémentaires
        """
        self.id = str(uuid.uuid4())
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.signature_type = signature_type
        self.signer_id = signer_id
        self.signer_name = signer_name
        self.signer_role = signer_role
        self.data = data or {}
        self.created_at = datetime.utcnow()
        self.status = SignatureStatus.VALID
        self.revoked_at: Optional[datetime] = None
        self.revoked_by: Optional[str] = None
        self.revoked_reason: Optional[str] = None

    def revoke(self, revoked_by: str, reason: str) -> None:
        """
        Révoque la signature

        Args:
            revoked_by: ID de l'utilisateur qui révoque
            reason: Raison de la révocation
        """
        if self.status != SignatureStatus.VALID:
            raise ValueError("Seules les signatures valides peuvent être révoquées")

        self.status = SignatureStatus.REVOKED
        self.revoked_at = datetime.utcnow()
        self.revoked_by = revoked_by
        self.revoked_reason = reason

    def is_valid(self) -> bool:
        """
        Vérifie si la signature est valide

        Returns:
            True si la signature est valide, False sinon
        """
        return self.status == SignatureStatus.VALID

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la signature en dictionnaire

        Returns:
            Dictionnaire représentant la signature
        """
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "signature_type": self.signature_type.value,
            "signer_id": self.signer_id,
            "signer_name": self.signer_name,
            "signer_role": self.signer_role,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revoked_by": self.revoked_by,
            "revoked_reason": self.revoked_reason
        }

    def generate_hash(self) -> str:
        """
        Génère un hash de la signature

        Returns:
            Hash SHA-256 de la signature
        """
        signature_data = {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "signature_type": self.signature_type.value,
            "signer_id": self.signer_id,
            "signer_name": self.signer_name,
            "signer_role": self.signer_role,
            "created_at": self.created_at.isoformat(),
            "data": self.data
        }

        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()

    @staticmethod
    def hash_file(file_path: str) -> str:
        """
        Génère un hash SHA-256 d'un fichier réel.
        Utilisé pour garantir l'intégrité du formulaire PDF final.
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Lire par blocs pour gérer les fichiers volumineux
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            return f"error_hashing_file: {str(e)}"

class SignatureManager:
    """Gestionnaire de signatures numériques"""

    def __init__(self):
        """Initialise le gestionnaire de signatures"""
        self.signatures: Dict[str, DigitalSignature] = {}
        self.entity_signatures: Dict[str, List[str]] = {}

    def create_signature(
        self,
        entity_type: str,
        entity_id: str,
        signature_type: SignatureType,
        signer_id: str,
        signer_name: str,
        signer_role: str,
        data: Optional[Dict[str, Any]] = None
    ) -> DigitalSignature:
        """
        Crée une nouvelle signature

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            signature_type: Type de signature
            signer_id: ID du signataire
            signer_name: Nom du signataire
            signer_role: Rôle du signataire
            data: Données supplémentaires

        Returns:
            Signature créée
        """
        signature = DigitalSignature(
            entity_type=entity_type,
            entity_id=entity_id,
            signature_type=signature_type,
            signer_id=signer_id,
            signer_name=signer_name,
            signer_role=signer_role,
            data=data
        )

        # Enregistrer la signature
        self.signatures[signature.id] = signature

        # Ajouter la signature à l'entité
        entity_key = f"{entity_type}:{entity_id}"
        if entity_key not in self.entity_signatures:
            self.entity_signatures[entity_key] = []

        self.entity_signatures[entity_key].append(signature.id)

        return signature

    def get_signature(self, signature_id: str) -> Optional[DigitalSignature]:
        """
        Récupère une signature par son ID

        Args:
            signature_id: ID de la signature

        Returns:
            Signature ou None si non trouvée
        """
        return self.signatures.get(signature_id)

    def get_entity_signatures(
        self,
        entity_type: str,
        entity_id: str,
        signature_type: Optional[SignatureType] = None
    ) -> List[DigitalSignature]:
        """
        Récupère les signatures d'une entité

        Args:
            entity_type: Type d'entité
            entity_id: ID de l'entité
            signature_type: Type de signature (optionnel)

        Returns:
            Liste des signatures
        """
        entity_key = f"{entity_type}:{entity_id}"
        signature_ids = self.entity_signatures.get(entity_key, [])

        signatures = [self.signatures[sid] for sid in signature_ids if sid in self.signatures]

        # Filtrer par type si spécifié
        if signature_type:
            signatures = [s for s in signatures if s.signature_type == signature_type]

        # Trier par date décroissante
        signatures = sorted(signatures, key=lambda s: s.created_at, reverse=True)

        return signatures

    def revoke_signature(
        self,
        signature_id: str,
        revoked_by: str,
        reason: str
    ) -> None:
        """
        Révoque une signature

        Args:
            signature_id: ID de la signature
            revoked_by: ID de l'utilisateur qui révoque
            reason: Raison de la révocation
        """
        signature = self.get_signature(signature_id)
        if not signature:
            raise ValueError("Signature non trouvée")

        signature.revoke(revoked_by, reason)

    def verify_signature(
        self,
        signature_id: str,
        expected_hash: Optional[str] = None
    ) -> bool:
        """
        Vérifie une signature

        Args:
            signature_id: ID de la signature
            expected_hash: Hash attendu (optionnel)

        Returns:
            True si la signature est valide, False sinon
        """
        signature = self.get_signature(signature_id)
        if not signature:
            return False

        # Vérifier que la signature est valide
        if not signature.is_valid():
            return False

        # Vérifier le hash si fourni
        if expected_hash:
            signature_hash = signature.generate_hash()
            return signature_hash == expected_hash

        return True

    def get_signer_signatures(
        self,
        signer_id: str,
        entity_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[DigitalSignature]:
        """
        Récupère les signatures d'un signataire

        Args:
            signer_id: ID du signataire
            entity_type: Type d'entité (optionnel)
            limit: Nombre maximum de signatures à retourner

        Returns:
            Liste des signatures
        """
        signatures = []

        for signature in self.signatures.values():
            if signature.signer_id == signer_id:
                if entity_type is None or signature.entity_type == entity_type:
                    signatures.append(signature)

        # Trier par date décroissante
        signatures = sorted(signatures, key=lambda s: s.created_at, reverse=True)

        # Appliquer la limite si spécifiée
        if limit and len(signatures) > limit:
            signatures = signatures[:limit]

        return signatures

# Instance globale du gestionnaire de signatures
signature_manager = SignatureManager()
