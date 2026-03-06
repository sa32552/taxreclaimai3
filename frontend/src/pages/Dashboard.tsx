
import { useEffect, useState } from 'react';
import { 
  DollarSign, 
  FileText, 
  TrendingUp, 
  Globe,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';
import axios from 'axios';

interface DashboardData {
  total_recoverable: number;
  total_processed: number;
  success_rate: number;
  roi: number;
  countries: Array<{
    name: string;
    recoverable: number;
    invoices: number;
  }>;
  recent_invoices: Array<{
    id: string;
    supplier: string;
    amount: number;
    country: string;
    status: string;
  }>;
  last_updated: string;
}

const Dashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/api/dashboard');
        setData(response.data);
      } catch (err) {
        setError('Erreur lors du chargement des données du dashboard');
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
          <p className="text-red-800">{error || 'Données non disponibles'}</p>
        </div>
      </div>
    );
  }

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
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-600 mt-1">Vue d'ensemble de votre récupération de TVA</p>
      </div>

      {/* Cartes KPI */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Montant récupérable</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {formatCurrency(data.total_recoverable)}
              </p>
            </div>
            <div className="p-3 bg-primary-50 rounded-lg">
              <DollarSign className="h-6 w-6 text-primary-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
            <span className="text-green-600 font-medium">ROI {data.roi}x</span>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Factures traitées</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {data.total_processed}
              </p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <FileText className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <CheckCircle className="h-4 w-4 text-green-600 mr-1" />
            <span className="text-green-600 font-medium">
              {data.success_rate}% de succès
            </span>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Pays couverts</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {data.countries.length}
              </p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <Globe className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 text-sm text-slate-600">
            <span className="font-medium">193 pays</span> disponibles
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Dernière mise à jour</p>
              <p className="text-sm font-bold text-slate-900 mt-1">
                {new Date(data.last_updated).toLocaleString('fr-FR', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <Clock className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4 text-sm text-slate-600">
            Mise à jour automatique
          </div>
        </div>
      </div>

      {/* Section Pays */}
      <div className="card">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Récupération par pays</h2>
        <div className="space-y-4">
          {data.countries.map((country) => (
            <div key={country.name} className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-900">{country.name}</span>
                  <span className="text-sm text-slate-600">{formatCurrency(country.recoverable)}</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(country.recoverable / data.total_recoverable) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div className="ml-4 text-sm text-slate-600 whitespace-nowrap">
                {country.invoices} factures
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section Factures récentes */}
      <div className="card">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Factures récentes</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Fournisseur
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Pays
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Montant
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Statut
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {data.recent_invoices.map((invoice) => (
                <tr key={invoice.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                    {invoice.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {invoice.supplier}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {invoice.country}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {formatCurrency(invoice.amount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${
                      invoice.status === 'processed' ? 'badge-success' : 'badge-warning'
                    }`}>
                      {invoice.status === 'processed' ? 'Traité' : 'En attente'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
