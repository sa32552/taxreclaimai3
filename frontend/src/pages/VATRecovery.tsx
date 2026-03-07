
import { useState } from 'react';
import { 
  Calculator, 
  CheckCircle, 
  AlertCircle,
  Globe,
  DollarSign,
  TrendingUp
} from 'lucide-react';
import axios from 'axios';

interface Invoice {
  invoice_number: string;
  date: string;
  supplier: string;
  country: string;
  vat_number: string;
  amount_ht: number;
  vat_amount: number;
  total_amount: number;
  currency: string;
  language: string;
}

interface VATRecoveryResult {
  status: string;
  target_country: string;
  total_invoices: number;
  matched_invoices: number;
  total_recoverable: number;
  currency: string;
  success_rate: number;
  roi: number;
  results: {
    matched_invoices: Array<{
      invoice: Invoice;
      recoverable_amount: number;
      vat_rate: number;
      form_type: string;
      time_limit: string;
    }>;
    unmatched_invoices: Array<{
      invoice: Invoice;
      reason: string;
    }>;
  };
}

const VATRecovery = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [targetCountry, setTargetCountry] = useState('FR');
  const [companyVat, setCompanyVat] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VATRecoveryResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAddInvoice = () => {
    const newInvoice: Invoice = {
      invoice_number: `INV-${Date.now()}`,
      date: new Date().toISOString().split('T')[0],
      supplier: '',
      country: targetCountry,
      vat_number: '',
      amount_ht: 0,
      vat_amount: 0,
      total_amount: 0,
      currency: 'EUR',
      language: 'FR'
    };
    setInvoices([...invoices, newInvoice]);
  };

  const handleRemoveInvoice = (index: number) => {
    setInvoices(invoices.filter((_, i) => i !== index));
  };

  const handleInvoiceChange = (index: number, field: keyof Invoice, value: string | number) => {
    const updatedInvoices = [...invoices];
    updatedInvoices[index] = {
      ...updatedInvoices[index],
      [field]: value
    };
    setInvoices(updatedInvoices);
  };

  const handleCalculateRecovery = async () => {
    if (invoices.length === 0 || !companyVat) {
      setError('Veuillez ajouter au moins une facture et renseigner votre numéro de TVA');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('/api/vat_recovery', {
        invoices,
        target_country: targetCountry,
        company_vat: companyVat
      });
      setResult(response.data);
    } catch (err) {
      setError('Erreur lors du calcul de la récupération de TVA');
      console.error('Error calculating VAT recovery:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const countries = [
    { code: 'FR', name: 'France' },
    { code: 'DE', name: 'Allemagne' },
    { code: 'IT', name: 'Italie' },
    { code: 'ES', name: 'Espagne' },
    { code: 'GB', name: 'Royaume-Uni' },
    { code: 'US', name: 'États-Unis' },
    { code: 'CN', name: 'Chine' },
    { code: 'JP', name: 'Japon' },
    { code: 'KR', name: 'Corée du Sud' },
    { code: 'IN', name: 'Inde' },
    { code: 'BR', name: 'Brésil' },
    { code: 'MX', name: 'Mexique' },
    { code: 'AE', name: 'Émirats arabes unis' },
    { code: 'SA', name: 'Arabie Saoudite' },
    { code: 'SG', name: 'Singapour' },
    { code: 'ZA', name: 'Afrique du Sud' },
    { code: 'AU', name: 'Australie' },
    { code: 'CA', name: 'Canada' },
    { code: 'BE', name: 'Belgique' },
    { code: 'NL', name: 'Pays-Bas' },
    { code: 'AT', name: 'Autriche' },
    { code: 'CH', name: 'Suisse' },
    { code: 'PT', name: 'Portugal' },
    { code: 'SE', name: 'Suède' },
    { code: 'DK', name: 'Danemark' },
    { code: 'FI', name: 'Finlande' },
    { code: 'NO', name: 'Norvège' }
  ];

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Récupération de TVA</h1>
        <p className="text-slate-600 mt-1">Calculez et optimisez votre récupération de TVA internationale</p>
      </div>

      {/* Formulaire principal */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Pays de récupération
            </label>
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <select
                value={targetCountry}
                onChange={(e) => setTargetCountry(e.target.value)}
                className="input pl-10"
              >
                {countries.map(country => (
                  <option key={country.code} value={country.code}>
                    {country.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Numéro de TVA de votre entreprise
            </label>
            <input
              type="text"
              value={companyVat}
              onChange={(e) => setCompanyVat(e.target.value)}
              placeholder="FR12345678901"
              className="input"
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={handleAddInvoice}
            className="btn btn-secondary"
          >
            + Ajouter une facture
          </button>
        </div>

        {/* Liste des factures */}
        {invoices.length > 0 && (
          <div className="mt-6 space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Factures ({invoices.length})</h3>

            {invoices.map((invoice, index) => (
              <div key={index} className="border border-slate-200 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Numéro de facture
                    </label>
                    <input
                      type="text"
                      value={invoice.invoice_number}
                      onChange={(e) => handleInvoiceChange(index, 'invoice_number', e.target.value)}
                      className="input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Date
                    </label>
                    <input
                      type="date"
                      value={invoice.date}
                      onChange={(e) => handleInvoiceChange(index, 'date', e.target.value)}
                      className="input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Fournisseur
                    </label>
                    <input
                      type="text"
                      value={invoice.supplier}
                      onChange={(e) => handleInvoiceChange(index, 'supplier', e.target.value)}
                      className="input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Numéro de TVA
                    </label>
                    <input
                      type="text"
                      value={invoice.vat_number}
                      onChange={(e) => handleInvoiceChange(index, 'vat_number', e.target.value)}
                      className="input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Montant HT (€)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={invoice.amount_ht}
                      onChange={(e) => handleInvoiceChange(index, 'amount_ht', parseFloat(e.target.value))}
                      className="input"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Montant TVA (€)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={invoice.vat_amount}
                      onChange={(e) => handleInvoiceChange(index, 'vat_amount', parseFloat(e.target.value))}
                      className="input"
                    />
                  </div>
                </div>

                <div className="mt-4 flex justify-end">
                  <button
                    onClick={() => handleRemoveInvoice(index)}
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Supprimer cette facture
                  </button>
                </div>
              </div>
            ))}

            <div className="mt-6">
              <button
                onClick={handleCalculateRecovery}
                disabled={loading}
                className="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Calcul en cours...' : 'Calculer la récupération de TVA'}
              </button>
            </div>
          </div>
        )}
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

      {/* Résultats */}
      {result && (
        <div className="space-y-6">
          {/* Cartes KPI */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Montant récupérable</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">
                    {formatCurrency(result.total_recoverable)}
                  </p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <DollarSign className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Factures éligibles</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">
                    {result.matched_invoices}
                  </p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Taux de succès</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">
                    {result.success_rate}%
                  </p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg">
                  <Calculator className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">ROI estimé</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">
                    {result.roi}x
                  </p>
                </div>
                <div className="p-3 bg-yellow-50 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-yellow-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Factures éligibles */}
          <div className="card">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">
              Factures éligibles ({result.results.matched_invoices.length})
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Facture
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Fournisseur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Montant TVA
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Récupérable
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      VIES Compliance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Taux
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Formulaire
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {result.results.matched_invoices.map((item, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                        {item.invoice.invoice_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {item.invoice.supplier}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {formatCurrency(item.invoice.vat_amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                        {formatCurrency(item.recoverable_amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                          VIES ACTIF
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {item.vat_rate}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {item.form_type}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Factures non éligibles */}
          {result.results.unmatched_invoices.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">
                Factures non éligibles ({result.results.unmatched_invoices.length})
              </h3>
              <div className="space-y-2">
                {result.results.unmatched_invoices.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-slate-900">
                        {item.invoice.invoice_number}
                      </p>
                      <p className="text-xs text-slate-600">
                        {item.invoice.supplier} - {formatCurrency(item.invoice.vat_amount)}
                      </p>
                    </div>
                    <div className="flex items-center text-red-600">
                      <AlertCircle className="h-5 w-5 mr-2" />
                      <span className="text-sm">{item.reason}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VATRecovery;
