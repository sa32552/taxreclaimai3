
-- ====================================================================
-- SCHEMA DE BASE TAXRECLAIMAI - ORDRE DE CRÉATION OPTIMISÉ
-- ====================================================================

-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Table des entreprises (Indépendante)
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    vat_number VARCHAR(50) UNIQUE NOT NULL,
    country CHAR(2) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    subscription_plan VARCHAR(50) DEFAULT 'free' NOT NULL,
    max_users INTEGER DEFAULT 5 NOT NULL,
    max_invoices_per_month INTEGER DEFAULT 100 NOT NULL,
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 3. Table des utilisateurs (Dépend de companies)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'user' NOT NULL CHECK (role IN ('admin', 'manager', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    two_factor_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);

-- 4. Table des demandes de récupération TVA (Dépend de users et companies)
CREATE TABLE IF NOT EXISTS vat_claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_number VARCHAR(100) UNIQUE NOT NULL,
    target_country CHAR(2) NOT NULL,
    company_vat_number VARCHAR(50) NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    total_recoverable DECIMAL(12,2) DEFAULT 0.0 NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    submitted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    is_locked BOOLEAN DEFAULT FALSE NOT NULL, -- Verrouillage légal anti-suppression
    archived_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 5. Table des factures (Dépend de users, companies et vat_claims)
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(100) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    supplier VARCHAR(255) NOT NULL,
    country CHAR(2) NOT NULL,
    amount_ht DECIMAL(12,2) NOT NULL,
    vat_amount DECIMAL(12,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    currency CHAR(3) DEFAULT 'EUR' NOT NULL,
    status VARCHAR(20) DEFAULT 'uploaded' NOT NULL,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    vat_claim_id UUID REFERENCES vat_claims(id) ON DELETE SET NULL,
    extraction_confidence DECIMAL(3,2) DEFAULT 0.0,
    original_file_path TEXT,
    is_locked BOOLEAN DEFAULT FALSE NOT NULL, -- Verrouillage légal
    archived_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Index unique pour la détection automatique des doublons
CREATE UNIQUE INDEX IF NOT EXISTS idx_invoices_duplicate_check 
ON invoices (company_id, supplier, invoice_number, total_amount);

-- 6. Table des notifications (Dépend de users)
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(20) DEFAULT 'unread',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 7. Table des formulaires (Dépend de companies et vat_claims)
CREATE TABLE IF NOT EXISTS forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_type VARCHAR(50) NOT NULL,
    file_path TEXT,
    status VARCHAR(20) DEFAULT 'ready' NOT NULL, -- ready, generating, error, signed
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    vat_claim_id UUID REFERENCES vat_claims(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 8. Table des signatures numériques (Dépend de forms et users)
CREATE TABLE IF NOT EXISTS digital_signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID NOT NULL REFERENCES forms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    signature_hash TEXT NOT NULL,
    signed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 9. Table des preuves de paiement (Bank Statements / Receipts)
CREATE TABLE IF NOT EXISTS payment_proofs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_path TEXT NOT NULL,
    payment_date TIMESTAMP WITH TIME ZONE,
    amount DECIMAL(12,2) NOT NULL,
    currency CHAR(3) DEFAULT 'EUR' NOT NULL,
    reference TEXT, -- Numero de virement, libellé
    supplier_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'unmatched' NOT NULL, -- unmatched, matched, partial
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 10. Table de liaison Invoice <-> Payment Proof
CREATE TABLE IF NOT EXISTS invoice_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    payment_proof_id UUID NOT NULL REFERENCES payment_proofs(id) ON DELETE CASCADE,
    matched_amount DECIMAL(12,2) NOT NULL,
    matching_confidence DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 9. Table des audits logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Index pour la performance
CREATE INDEX IF NOT EXISTS idx_invoices_company ON invoices(company_id);
CREATE INDEX IF NOT EXISTS idx_vat_claims_company ON vat_claims(company_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
