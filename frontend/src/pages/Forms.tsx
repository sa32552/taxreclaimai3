
import { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  CheckCircle, 
  AlertCircle,
  Clock,
  Globe
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
  status: 'ready' | 'generating' | 'error';
}

const Forms = () => {
  const [forms, setForms] = useState<FormInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedForms, setSelectedForms] = useState<Set<string>>(new Set());

  useEffect(() => {
    const loadForms = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        const response = await axios.get('/api/forms', {
          headers: { 'Authorization': `Bearer ${session?.access_token}` }
        });
        
        const mappedForms: FormInfo[] = response.data.map((f: any) => ({
          country_code: f.target_country || 'FR',
          country_name: f.target_country || 'France',
          form_type: f.form_type,
          form_name: `VAT Return ${f.form_type}`,
          invoice_count: 0,
          total_amount: f.total_amount || 0,
          status: f.status
        }));
        
        setForms(mappedForms);
      } catch (err) {
        setError('Erreur lors du chargement des formulaires Supabase');
        console.error('Error loading forms:', err);
      }
    };

    loadForms();
  }, []);

  const handleSelectForm = (formId: string) => {
    setSelectedForms(prev => {
      const newSet = new Set(prev);
      if (newSet.has(formId)) {
        newSet.delete(formId);
      } else {
        newSet.add(formId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedForms.size === forms.length && forms.length > 0) {
      setSelectedForms(new Set());
    } else {
      setSelectedForms(new Set(forms.map(f => f.form_type)));
    }
  };

  const handleGenerateForms = async () => {
    if (selectedForms.size === 0) {
      setError('Veuillez sélectionner au moins un formulaire');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      const { data: claims } = await supabase.from('vat_claims').select('id').limit(1);
      
      if (!claims || claims.length === 0) {
        throw new Error("Aucune demande de récupération TVA trouvée. Créez-en une d'abord.");
      }

      await axios.post(`/api/forms/generate?claim_id=${claims[0].id}`, {}, {
        headers: { 'Authorization': `Bearer ${session?.access_token}` }
      });

      alert('Formulaire généré avec succès dans Supabase Storage !');
      window.location.reload();
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la génération des formulaires');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadForm = async (formType: string) => {
    try {
      // Simuler un appel API pour télécharger le formulaire
      const response = await axios.get(`/api/download_forms/${formType}`, {
        responseType: 'blob'
      });

      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${formType}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Erreur lors du téléchargement du formulaire');
      console.error('Error downloading form:', err);
    }
  };

  const handleDownloadAll = async () => {
    try {
      // Simuler un appel API pour télécharger tous les formulaires
      const response = await axios.get('/api/download_forms/all', {
        responseType: 'blob'
      });

      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'vat_forms.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Erreur lors du téléchargement des formulaires');
      console.error('Error downloading forms:', err);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Formulaires de remboursement TVA</h1>
        <p className="text-slate-600 mt-1">Générez et téléchargez vos formulaires de remboursement TVA</p>
      </div>

      {/* Message d'erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Liste des formulaires */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">
            Formulaires disponibles ({forms.length})
          </h2>
          <div className="flex space-x-2">
            <button
              onClick={handleSelectAll}
              className="btn btn-secondary"
            >
              {selectedForms.size === forms.length ? 'Désélectionner tout' : 'Sélectionner tout'}
            </button>
            <button
              onClick={handleGenerateForms}
              disabled={loading || selectedForms.size === 0}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Génération en cours...' : 'Générer les formulaires'}
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {forms.map((form) => (
            <div
              key={form.form_type}
              className={`flex items-center justify-between p-4 rounded-lg border transition-colors ${
                selectedForms.has(form.form_type)
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center space-x-4">
                <input
                  type="checkbox"
                  checked={selectedForms.has(form.form_type)}
                  onChange={() => handleSelectForm(form.form_type)}
                  className="h-4 w-4 text-primary-600 rounded border-slate-300 focus:ring-primary-500"
                />

                <div className="p-2 bg-slate-100 rounded-lg">
                  <FileText className="h-5 w-5 text-slate-600" />
                </div>

                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-semibold text-slate-900">
                      {form.form_name}
                    </h3>
                    <span className="badge badge-success">
                      {form.form_type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 mt-1">
                    <div className="flex items-center space-x-1">
                      <Globe className="h-4 w-4 text-slate-400" />
                      <span className="text-sm text-slate-600">{form.country_name}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <FileText className="h-4 w-4 text-slate-400" />
                      <span className="text-sm text-slate-600">{form.invoice_count} factures</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-sm font-medium text-slate-900">
                        {formatCurrency(form.total_amount)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                {form.status === 'ready' && (
                  <button
                    onClick={() => handleDownloadForm(form.form_type)}
                    className="btn btn-secondary"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Télécharger
                  </button>
                )}
                {form.status === 'generating' && (
                  <div className="flex items-center space-x-2 text-sm text-slate-600">
                    <Clock className="h-4 w-4 animate-spin" />
                    <span>Génération...</span>
                  </div>
                )}
                {form.status === 'error' && (
                  <div className="flex items-center space-x-2 text-sm text-red-600">
                    <AlertCircle className="h-4 w-4" />
                    <span>Erreur</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {forms.length > 0 && (
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleDownloadAll}
              className="btn btn-primary"
            >
              <Download className="h-4 w-4 mr-2" />
              Télécharger tous les formulaires (ZIP)
            </button>
          </div>
        )}
      </div>

      {/* Informations */}
      <div className="card">
        <h3 className="text-sm font-semibold text-slate-900 mb-2">
          Informations sur les formulaires
        </h3>
        <ul className="text-sm text-slate-600 space-y-1">
          <li>• 47 formulaires de remboursement TVA pour 193 pays</li>
          <li>• Formulaires conformes aux normes eIDAS</li>
          <li>• Pré-remplis automatiquement avec vos données</li>
          <li>• Disponibles en plusieurs langues selon le pays</li>
          <li>• Téléchargement en ZIP pour tous les formulaires</li>
        </ul>
      </div>
    </div>
  );
};

export default Forms;
