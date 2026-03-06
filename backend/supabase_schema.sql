
-- Schema SQL pour Supabase

-- Extensions requises
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'user' NOT NULL CHECK (role IN ('admin', 'manager', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    two_factor_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    two_factor_secret VARCHAR(255),
    backup_codes TEXT,
    failed_login_attempts INTEGER DEFAULT 0 NOT NULL,
    locked_until TIMESTAMP,
    company_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL
);

-- Index pour les utilisateurs
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_company ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Table des entreprises
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

-- Index pour les entreprises
CREATE INDEX IF NOT EXISTS idx_companies_vat_number ON companies(vat_number);
CREATE INDEX IF NOT EXISTS idx_companies_country ON companies(country);
CREATE INDEX IF NOT EXISTS idx_companies_active ON companies(is_active);
CREATE INDEX IF NOT EXISTS idx_companies_subscription ON companies(subscription_plan);

-- Table des factures
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(100) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    supplier VARCHAR(255) NOT NULL,
    supplier_vat_number VARCHAR(50),
    country CHAR(2) NOT NULL,
    amount_ht DECIMAL(12,2) NOT NULL,
    vat_amount DECIMAL(12,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    currency CHAR(3) DEFAULT 'EUR' NOT NULL,
    language VARCHAR(5),
    extraction_confidence DECIMAL(3,2) DEFAULT 0.0 NOT NULL,
    extraction_data JSONB,
    status VARCHAR(20) DEFAULT 'uploaded' NOT NULL CHECK (status IN ('uploaded', 'processing', 'processed', 'approved', 'rejected', 'archived')),
    validated_at TIMESTAMP WITH TIME ZONE,
    validated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    original_file_path VARCHAR(500),
    processed_file_path VARCHAR(500),
    company_id UUID NOT NULL,
    vat_claim_id UUID REFERENCES vat_claims(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT fk_invoice_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT fk_invoice_validator FOREIGN KEY (validated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Index pour les factures
CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_company ON invoices(company_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_country ON invoices(country);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(date);
CREATE INDEX IF NOT EXISTS idx_invoices_supplier ON invoices(supplier);
CREATE INDEX IF NOT EXISTS idx_invoices_vat_claim ON invoices(vat_claim_id);

-- Table des demandes de récupération TVA
CREATE TABLE IF NOT EXISTS vat_claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_number VARCHAR(100) UNIQUE NOT NULL,
    target_country CHAR(2) NOT NULL,
    company_vat_number VARCHAR(50) NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    total_recoverable DECIMAL(12,2) DEFAULT 0.0 NOT NULL,
    total_approved DECIMAL(12,2) DEFAULT 0.0 NOT NULL,
    total_rejected DECIMAL(12,2) DEFAULT 0.0 NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL CHECK (status IN ('draft', 'submitted', 'processing', 'approved', 'rejected', 'completed', 'cancelled')),
    submitted_at TIMESTAMP WITH TIME ZONE,
    submitted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    external_reference VARCHAR(100),
    forms_generated JSONB,
    forms_submitted JSONB,
    notes TEXT,
    rejection_reason TEXT,
    company_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT fk_vat_claim_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT fk_vat_claim_submitter FOREIGN KEY (submitted_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_vat_claim_approver FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Index pour les demandes TVA
CREATE INDEX IF NOT EXISTS idx_vat_claims_number ON vat_claims(claim_number);
CREATE INDEX IF NOT EXISTS idx_vat_claims_company ON vat_claims(company_id);
CREATE INDEX IF NOT EXISTS idx_vat_claims_status ON vat_claims(status);
CREATE INDEX IF NOT EXISTS idx_vat_claims_country ON vat_claims(target_country);
CREATE INDEX IF NOT EXISTS idx_vat_claims_period ON vat_claims(period_start, period_end);

-- Table des formulaires
CREATE TABLE IF NOT EXISTS forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_number VARCHAR(100) UNIQUE NOT NULL,
    form_type VARCHAR(20) NOT NULL CHECK (form_type IN ('CA3', 'USt1V', 'VA', '303', 'VAT65A', 'OB', '71.604', 'U21', '833', 'VAT-UE', 'SKV4632', 'VAT55', 'VAT811', 'RF1032', 'IVA54', 'F2', 'VAT66', '770')),
    country CHAR(2) NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    form_data JSONB NOT NULL,
    pdf_path VARCHAR(500),
    xml_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft' NOT NULL CHECK (status IN ('draft', 'generated', 'submitted', 'approved', 'rejected', 'archived')),
    generated_at TIMESTAMP WITH TIME ZONE,
    generated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    submitted_at TIMESTAMP WITH TIME ZONE,
    submitted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    external_reference VARCHAR(100),
    notes TEXT,
    rejection_reason TEXT,
    company_id UUID NOT NULL,
    vat_claim_id UUID REFERENCES vat_claims(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT fk_form_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT fk_form_generator FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_form_submitter FOREIGN KEY (submitted_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_form_approver FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_form_vat_claim FOREIGN KEY (vat_claim_id) REFERENCES vat_claims(id) ON DELETE SET NULL
);

-- Index pour les formulaires
CREATE INDEX IF NOT EXISTS idx_forms_number ON forms(form_number);
CREATE INDEX IF NOT EXISTS idx_forms_company ON forms(company_id);
CREATE INDEX IF NOT EXISTS idx_forms_status ON forms(status);
CREATE INDEX IF NOT EXISTS idx_forms_type ON forms(form_type);
CREATE INDEX IF NOT EXISTS idx_forms_country ON forms(country);
CREATE INDEX IF NOT EXISTS idx_forms_vat_claim ON forms(vat_claim_id);

-- Table des signatures numériques
CREATE TABLE IF NOT EXISTS digital_signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    signature_type VARCHAR(20) NOT NULL CHECK (signature_type IN ('approval', 'rejection', 'submission', 'acceptance')),
    signer_id UUID NOT NULL,
    signer_name VARCHAR(100) NOT NULL,
    signer_role VARCHAR(50) NOT NULL,
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    status VARCHAR(20) DEFAULT 'valid' NOT NULL CHECK (status IN ('valid', 'invalid', 'revoked', 'expired')),
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by UUID REFERENCES users(id) ON DELETE SET NULL,
    revoked_reason TEXT
);

-- Index pour les signatures
CREATE INDEX IF NOT EXISTS idx_signatures_entity ON digital_signatures(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_signatures_signer ON digital_signatures(signer_id);
CREATE INDEX IF NOT EXISTS idx_signatures_status ON digital_signatures(status);

-- Table des notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal' NOT NULL CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    entity_type VARCHAR(50),
    entity_id UUID,
    action_url VARCHAR(500),
    data JSONB,
    status VARCHAR(20) DEFAULT 'unread' NOT NULL CHECK (status IN ('unread', 'read', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE,
    archived_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour les notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at);

-- Table des modifications (audit trail)
CREATE TABLE IF NOT EXISTS changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    change_type VARCHAR(20) NOT NULL CHECK (change_type IN ('create', 'update', 'delete', 'approve', 'reject', 'submit', 'archive', 'restore')),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    user_name VARCHAR(100) NOT NULL,
    changes JSONB NOT NULL,
    previous_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT fk_change_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Index pour les modifications
CREATE INDEX IF NOT EXISTS idx_changes_entity ON changes(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_changes_user ON changes(user_id);
CREATE INDEX IF NOT EXISTS idx_changes_type ON changes(change_type);
CREATE INDEX IF NOT EXISTS idx_changes_created ON changes(created_at);

-- Table des workflows d'approbation
CREATE TABLE IF NOT EXISTS approval_workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    requester_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    requester_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    current_level VARCHAR(20),
    required_levels JSONB NOT NULL,
    steps JSONB,
    completed_at TIMESTAMP WITH TIME ZONE,
    comments JSONB,

    CONSTRAINT fk_workflow_requester FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Index pour les workflows
CREATE INDEX IF NOT EXISTS idx_workflows_entity ON approval_workflows(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_workflows_requester ON approval_workflows(requester_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON approval_workflows(status);

-- Fonction pour mettre à jour le timestamp updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour mettre à jour updated_at automatiquement
CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_vat_claims_updated_at BEFORE UPDATE ON vat_claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_forms_updated_at BEFORE UPDATE ON forms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
