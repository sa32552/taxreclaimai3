
-- ====================================================================
-- ADVANCED SECURITY & AUDIT SYSTEM FOR TAXRECLAIMAI
-- ====================================================================

-- 1. ACTIVER LE ROW LEVEL SECURITY (RLS) SUR TOUTES LES TABLES
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE vat_claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE digital_signatures ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_workflows ENABLE ROW LEVEL SECURITY;

-- 2. FONCTION UTILITAIRE POUR RÉCUPÉRER LE COMPANY_ID DE L'UTILISATEUR ACTUEL
CREATE OR REPLACE FUNCTION get_my_company_id()
RETURNS UUID AS $$
BEGIN
  RETURN (SELECT company_id FROM public.users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. POLITIQUES DE SÉCURITÉ POUR 'users'
CREATE POLICY "Les utilisateurs voient leur propre profil" 
ON users FOR SELECT 
USING (auth.uid() = id);

CREATE POLICY "Les managers voient les utilisateurs de leur entreprise" 
ON users FOR SELECT 
USING (
  (SELECT role FROM public.users WHERE id = auth.uid()) IN ('admin', 'manager') 
  AND company_id = (SELECT company_id FROM public.users WHERE id = auth.uid())
);

-- 4. POLITIQUES DE SÉCURITÉ POUR 'companies'
CREATE POLICY "Les utilisateurs voient leur propre entreprise" 
ON companies FOR SELECT 
USING (id = get_my_company_id());

-- 5. POLITIQUES DE SÉCURITÉ POUR 'invoices' (Isolation par entreprise)
CREATE POLICY "Accès restreint aux factures de l'entreprise" 
ON invoices FOR ALL 
USING (company_id = get_my_company_id());

-- 6. POLITIQUES DE SÉCURITÉ POUR 'vat_claims'
CREATE POLICY "Accès restreint aux demandes TVA de l'entreprise" 
ON vat_claims FOR ALL 
USING (company_id = get_my_company_id());

-- 7. POLITIQUES DE SÉCURITÉ POUR 'forms'
CREATE POLICY "Accès restreint aux formulaires de l'entreprise" 
ON forms FOR ALL 
USING (company_id = get_my_company_id());

-- 8. SYSTÈME D'AUDIT AVANCÉ
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    action TEXT NOT NULL, -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    user_id UUID REFERENCES users(id),
    user_email TEXT,
    ip_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fonction de déclenchement pour l'audit automatique
CREATE OR REPLACE FUNCTION process_audit_log()
RETURNS TRIGGER AS $$
DECLARE
    current_user_email TEXT;
BEGIN
    SELECT email INTO current_user_email FROM public.users WHERE id = auth.uid();

    IF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_data, user_id, user_email)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, to_jsonb(NEW), auth.uid(), current_user_email);
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data, user_id, user_email)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, to_jsonb(OLD), to_jsonb(NEW), auth.uid(), current_user_email);
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, user_id, user_email)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, to_jsonb(OLD), auth.uid(), current_user_email);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Application des triggers d'audit sur les tables critiques
CREATE TRIGGER audit_invoices_trigger AFTER INSERT OR UPDATE OR DELETE ON invoices FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_vat_claims_trigger AFTER INSERT OR UPDATE OR DELETE ON vat_claims FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_forms_trigger AFTER INSERT OR UPDATE OR DELETE ON forms FOR EACH ROW EXECUTE FUNCTION process_audit_log();

-- 9. SYSTÈME DE NOTIFICATION TEMPS RÉEL (Trigger)
CREATE OR REPLACE FUNCTION notify_ocr_complete()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.status = 'processing' AND NEW.status = 'processed') THEN
        INSERT INTO notifications (user_id, type, title, message, priority, entity_type, entity_id)
        VALUES (
            (SELECT id FROM users WHERE company_id = NEW.company_id AND role = 'manager' LIMIT 1),
            'OCR_COMPLETE',
            'Traitement terminé',
            'La facture ' || NEW.invoice_number || ' a été traitée avec succès par l''IA.',
            'normal',
            'invoice',
            NEW.id
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trigger_notify_ocr AFTER UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION notify_ocr_complete();
