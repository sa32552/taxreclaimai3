
import { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  CheckCircle, 
  Globe,
  Clock
} from 'lucide-react';
import axios from 'axios';
import { supabase } from '../supabase';

interface FormInfo {
  country_code: string;
  country_name: string;
  form_type: string;
  form_name: string;
  invoice_count: number;
  total_amount: number;
  status: 'ready' | 'generating' | 'error' | 'signed';
}

const Forms = () => {
  const [forms, setForms] = useState<FormInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [signing, setSigning] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadForms = async () => {
      try {
        const { data: supabaseForms, error: fetchError } = await supabase
          .from('forms')
          .select('*')
          .order('created_at', { ascending: false });
          
        if (fetchError) throw fetchError;
        
        const mappedForms: FormInfo[] = (supabaseForms || []).map((f: any) => ({
          country_code: f.form_type.split('_')[0] || 'FR',
          country_name: 'Vérifié par IA',
          form_type: f.form_type,
          form_name: `Déclaration de TVA Récupérable`,
          invoice_count: 0,
          total_amount: 0,
          status: f.status || 'ready'
        }));
        
        setForms(mappedForms);
      } catch (err: any) {
        setError('Erreur de synchronisation avec le Cloud Fiscale');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadForms();
  }, []);

  const handleSignAndSubmit = async (formId: string, formType: string) => {
    setSigning(formType);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      await axios.post(`/api/forms/${formId}/sign`, {}, {
        headers: { 'Authorization': `Bearer ${session?.access_token}` }
      });
      
      alert(`✅ Formulaire ${formType} signé avec succès et envoyé officiellement.`);
      window.location.reload();
    } catch (err: any) {
      setError("Erreur lors de la signature numérique : " + err.message);
    } finally {
      setSigning(null);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
        <div className="h-12 w-12 border-4 border-slate-100 border-t-primary-600 rounded-full animate-spin" />
        <p className="text-slate-400 font-medium">Accès au coffre-fort fiscal...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-20">
      <div className="animate-in fade-in slide-in-from-left-4 duration-700">
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Coffre-fort <span className="text-primary-600">Fiscal</span></h1>
        <p className="text-slate-500 font-medium mt-2">Dépôts officiels et documents certifiés eIDAS.</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-2xl flex items-center gap-3 animate-in fade-in zoom-in-95">
          <Clock className="h-5 w-5 text-red-500" />
          <span className="font-bold">{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6">
        {forms.map((form: any, i) => (
          <div key={i} className="group card hover:border-primary-200 transition-all duration-300 animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: `${i * 100}ms` }}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="flex items-center gap-6">
                <div className="h-16 w-16 bg-slate-50 rounded-2xl flex items-center justify-center group-hover:bg-primary-50 transition-colors">
                  <FileText className="h-8 w-8 text-slate-400 group-hover:text-primary-600 transition-colors" />
                </div>
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-black text-slate-900 leading-none">{form.form_name}</h3>
                    <span className="px-3 py-1 bg-slate-900 text-[10px] font-black text-white rounded-full uppercase tracking-widest">{form.form_type}</span>
                  </div>
                  <div className="flex items-center gap-6 mt-3">
                    <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4 text-slate-300" />
                        <span className="text-sm font-bold text-slate-500">{form.country_code}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <CheckCircle className={`h-4 w-4 ${form.status === 'signed' ? 'text-emerald-500' : 'text-slate-300'}`} />
                        <span className="text-sm font-bold text-slate-500 uppercase tracking-tighter">
                            {form.status === 'signed' ? 'Officiellement Signé' : 'En attente de signature'}
                        </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button className="p-3 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-all">
                  <Download className="h-5 w-5 text-slate-600" />
                </button>
                {form.status !== 'signed' ? (
                  <button 
                    onClick={() => handleSignAndSubmit(form.id, form.form_type)}
                    disabled={signing === form.form_type}
                    className="px-6 py-3 bg-primary-600 hover:bg-primary-500 text-white font-black text-xs uppercase tracking-[0.2em] rounded-xl transition-all shadow-lg shadow-primary-200 disabled:opacity-50"
                  >
                    {signing === form.form_type ? 'Signature IA...' : 'Signer & Envoyer'}
                  </button>
                ) : (
                  <div className="px-6 py-3 bg-emerald-50 text-emerald-700 font-black text-xs uppercase tracking-[0.2em] rounded-xl border border-emerald-100 flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    Transmis
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {forms.length === 0 && (
          <div className="card text-center py-20 border-dashed border-2 border-slate-200 bg-slate-50/50">
            <div className="h-20 w-20 bg-white rounded-full flex items-center justify-center mx-auto shadow-xl shadow-slate-200 mb-6">
              <Clock className="h-10 w-10 text-slate-300 animate-pulse" />
            </div>
            <h3 className="text-xl font-black text-slate-900">Aucun document prêt</h3>
            <p className="text-slate-500 font-medium max-w-xs mx-auto mt-2">Dès que vos analyses IA seront terminées, vos formulaires apparaîtront ici.</p>
          </div>
        )}
      </div>

      {/* Footer Info Premium */}
      <div className="mt-12 p-8 bg-gradient-to-br from-slate-900 to-indigo-900 rounded-3xl text-white overflow-hidden relative">
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="max-w-md">
                <h3 className="text-2xl font-black tracking-tight mb-2">Conformité eIDAS & RGPD</h3>
                <p className="text-indigo-200 font-medium opacity-80">Chaque signature effectuée sur cette plateforme est légalement contraignante et archivée de manière immuable sur notre infrastructure cloud sécurisée.</p>
            </div>
            <div className="flex gap-4">
                <div className="px-4 py-2 bg-white/10 rounded-xl backdrop-blur-md border border-white/10 text-[10px] font-black uppercase tracking-widest text-white">Certifié SSL 256-bit</div>
                <div className="px-4 py-2 bg-white/10 rounded-xl backdrop-blur-md border border-white/10 text-[10px] font-black uppercase tracking-widest text-white">IA Compliant</div>
            </div>
        </div>
        <div className="absolute -right-20 -bottom-20 h-64 w-64 bg-primary-500/20 rounded-full blur-[100px]" />
      </div>
    </div>
  );
};

export default Forms;
