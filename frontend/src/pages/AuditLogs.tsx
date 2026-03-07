
import React, { useEffect, useState } from 'react';
import { supabase } from '../supabase';
import { Shield, Clock, User, HardDrive, Info } from 'lucide-react';

interface AuditLog {
  id: string;
  table_name: string;
  record_id: string;
  action: string;
  old_data: any;
  new_data: any;
  user_email: string;
  ip_address: string;
  created_at: string;
}

const AuditLogs = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const { data, error } = await supabase
          .from('audit_logs')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) throw error;
        setLogs(data || []);
      } catch (err: any) {
        setError(err.message || "Erreur lors du chargement des logs d'audit");
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, []);

  const getActionColor = (action: string) => {
    switch (action) {
      case 'INSERT': return 'bg-green-100 text-green-700 border-green-200';
      case 'UPDATE': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'DELETE': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Journal d'Audit & Sécurité</h1>
          <p className="text-slate-500">Traçabilité complète des actions effectuées sur la plateforme.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-lg border border-primary-100 text-primary-700">
          <Shield className="h-5 w-5" />
          <span className="font-semibold italic font-serif">Niveau Critique</span>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-start gap-3">
          <Info className="h-5 w-5 mt-0.5 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">Action</th>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">Table</th>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">Utilisateur</th>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">ID Enregistrement</th>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">Horodatage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    Chargement des logs d'audit...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    Aucun événement d'audit enregistré pour le moment.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getActionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <HardDrive className="h-4 w-4 text-slate-400" />
                        <span className="text-sm text-slate-700 uppercase">{log.table_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-slate-400" />
                        <span className="text-sm text-slate-600">{log.user_email || 'Système (Auto)'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded text-slate-500">
                        {log.record_id.split('-')[0]}...
                      </code>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-slate-500">
                        <Clock className="h-4 w-4" />
                        <span className="text-sm">
                          {new Date(log.created_at).toLocaleString('fr-FR')}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;
