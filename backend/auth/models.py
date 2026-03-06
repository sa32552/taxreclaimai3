
"""
Modèles de données pour l'authentification et l'autorisation
"""

from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

class UserRole(str, Enum):
    """Rôles utilisateurs"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class Permission(str, Enum):
    """Permissions granulaires"""
    # Factures
    INVOICE_READ = "invoice:read"
    INVOICE_WRITE = "invoice:write"
    INVOICE_DELETE = "invoice:delete"
    INVOICE_APPROVE = "invoice:approve"

    # Récupération TVA
    VAT_RECOVERY_READ = "vat_recovery:read"
    VAT_RECOVERY_WRITE = "vat_recovery:write"
    VAT_RECOVERY_APPROVE = "vat_recovery:approve"

    # Formulaires
    FORM_READ = "form:read"
    FORM_WRITE = "form:write"
    FORM_DELETE = "form:delete"
    FORM_APPROVE = "form:approve"

    # Utilisateurs
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"

    # Entreprise
    COMPANY_READ = "company:read"
    COMPANY_WRITE = "company:write"
    COMPANY_DELETE = "company:delete"

    # Rapports
    REPORT_READ = "report:read"
    REPORT_WRITE = "report:write"
    REPORT_EXPORT = "report:export"

    # Système
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_AUDIT = "system:audit"

class UserBase(BaseModel):
    """Modèle de base pour un utilisateur"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False
    two_factor_enabled: bool = False

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError('Le numéro de téléphone doit contenir uniquement des chiffres')
        return v

class UserCreate(UserBase):
    """Modèle pour la création d'un utilisateur"""
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(char.islower() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(char.isdigit() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v

class UserUpdate(BaseModel):
    """Modèle pour la mise à jour d'un utilisateur"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None

class UserInDB(UserBase):
    """Modèle d'utilisateur en base de données"""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    permissions: List[Permission] = []
    company_id: Optional[str] = None

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    """Modèle de réponse utilisateur (sans données sensibles)"""
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    created_at: datetime
    last_login: Optional[datetime]
    permissions: List[Permission]

    class Config:
        orm_mode = True

class Token(BaseModel):
    """Modèle de token JWT"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenPayload(BaseModel):
    """Payload du token JWT"""
    sub: str  # ID utilisateur
    email: str
    role: UserRole
    permissions: List[Permission]
    company_id: Optional[str] = None
    exp: datetime
    iat: datetime

class TwoFactorSetup(BaseModel):
    """Modèle pour la configuration du 2FA"""
    secret: str
    qr_code_url: str
    backup_codes: List[str]

class TwoFactorVerify(BaseModel):
    """Modèle pour la vérification du 2FA"""
    code: str = Field(..., min_length=6, max_length=6)
    remember_device: bool = False

class PasswordReset(BaseModel):
    """Modèle pour la réinitialisation du mot de passe"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Modèle pour la confirmation de réinitialisation du mot de passe"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def validate_new_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(char.islower() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(char.isdigit() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v

class ChangePassword(BaseModel):
    """Modèle pour le changement de mot de passe"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def validate_new_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(char.islower() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(char.isdigit() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v

class LoginRequest(BaseModel):
    """Modèle de demande de connexion"""
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None
    remember_me: bool = False
