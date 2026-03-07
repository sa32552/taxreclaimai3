import React, { useState } from 'react';
import { supabase } from '../supabase';
import { LogIn, UserPlus, Mail, Lock, ShieldCheck, Building2, ArrowRight, Info, AlertCircle } from 'lucide-react';

const Login = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({ 
          email, 
          password,
          options: {
            data: {
              company_name: companyName,
              role: 'expert_tva'
            }
          }
        });
        if (error) throw error;
        setSuccess('Inscription réussie ! Veuillez vérifier vos spams pour le mail de confirmation. Si vous ne recevez rien, vous pouvez désactiver la confirmation email dans le dashboard Supabase.');
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoMode = async () => {
    setLoading(true);
    // Note: Pour une démo, on essaye de se connecter à un compte générique ou on informe
    setError("Mode Démo : Veuillez désactiver 'Confirm Email' dans Supabase > Authentication > Settings pour un accès direct sans email.");
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-slate-50">
      {/* Côté Gauche - Visuel & Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-700 to-indigo-900 p-12 text-white flex-col justify-between relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-20 -mr-20 w-96 h-96 bg-white opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-96 h-96 bg-primary-400 opacity-10 rounded-full blur-3xl"></div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-12">
            <div className="p-2 bg-white/10 backdrop-blur-md rounded-lg border border-white/20">
              <ShieldCheck className="h-8 w-8 text-white" />
            </div>
            <span className="text-2xl font-black tracking-tighter">TAXRECLAIMAI</span>
          </div>
          
          <h1 className="text-5xl font-black mb-6 leading-tight">
            L'Intelligence Artificielle au service de votre <span className="text-primary-300">Conformité TVA</span>.
          </h1>
          <p className="text-xl text-primary-100 max-w-lg mb-8">
            Optimisez vos récupérations fiscales internationales avec une précision de 99.8%. 
            Automatisez, Signez, Récupérez.
          </p>
          
          <div className="space-y-4">
            <div className="flex items-center gap-4 bg-white/5 backdrop-blur-sm p-4 rounded-xl border border-white/10">
              <div className="h-10 w-10 rounded-full bg-primary-500/20 flex items-center justify-center">
                <Building2 className="h-5 w-5 text-primary-300" />
              </div>
              <div>
                <p className="font-bold">Déploiement Mondial</p>
                <p className="text-sm text-primary-200">Support de 193 pays et juridictions.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10 pt-12 border-t border-white/10 text-primary-200 text-sm flex justify-between items-center">
          <p>© 2026 TaxReclaimAI - Enterprise Grade Solution</p>
          <div className="flex gap-4">
            <span>eIDAS Compliant</span>
            <span>GDPR Ready</span>
          </div>
        </div>
      </div>

      {/* Côté Droit - Formulaire */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12">
        <div className="max-w-md w-full">
          <div className="text-center lg:text-left mb-10">
            <h2 className="text-3xl font-black text-slate-900 mb-2">
              {isSignUp ? 'Bienvenue à bord' : 'Bon retour parmi nous'}
            </h2>
            <p className="text-slate-500">
              {isSignUp ? 'Gérez vos demandes de TVA en quelques clics.' : 'Accédez à votre cockpit de pilotage fiscal.'}
            </p>
          </div>

          <form className="space-y-5" onSubmit={handleAuth}>
            {isSignUp && (
              <div className="animate-in fade-in slide-in-from-top-2">
                <label className="block text-sm font-bold text-slate-700 mb-1.5 ml-1">Nom de l'entreprise</label>
                <div className="relative group">
                  <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 group-focus-within:text-primary-500 transition-colors" />
                  <input
                    type="text"
                    required
                    className="w-full pl-12 pr-4 py-3.5 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all outline-none shadow-sm"
                    placeholder="Ex: Global Tech SARL"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1.5 ml-1">Adresse Email Professionnelle</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 group-focus-within:text-primary-500 transition-colors" />
                <input
                  type="email"
                  required
                  className="w-full pl-12 pr-4 py-3.5 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all outline-none shadow-sm"
                  placeholder="nom@entreprise.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5 ml-1">
                <label className="block text-sm font-bold text-slate-700">Mot de passe</label>
                {!isSignUp && (
                  <button type="button" className="text-xs font-bold text-primary-600 hover:text-primary-700">Oublié ?</button>
                )}
              </div>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 group-focus-within:text-primary-500 transition-colors" />
                <input
                  type="password"
                  required
                  className="w-full pl-12 pr-4 py-3.5 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all outline-none shadow-sm"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {error && (
              <div className="flex gap-3 bg-red-50 border border-red-100 p-4 rounded-xl text-red-700 text-sm animate-shake">
                <AlertCircle className="h-5 w-5 shrink-0" />
                <p className="font-medium">{error}</p>
              </div>
            )}

            {success && (
              <div className="flex gap-3 bg-blue-50 border border-blue-100 p-4 rounded-xl text-blue-700 text-sm animate-in fade-in zoom-in-95">
                <Info className="h-5 w-5 shrink-0" />
                <p className="font-medium">{success}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-4 rounded-xl shadow-lg shadow-slate-200 transition-all flex items-center justify-center gap-2 group disabled:opacity-50"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  {isSignUp ? <UserPlus className="h-5 w-5" /> : <LogIn className="h-5 w-5" />}
                  <span>{isSignUp ? "Créer mon Compte" : "Se Connecter"}</span>
                  <ArrowRight className="h-4 w-4 opacity-50 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-slate-100 text-center">
            <button
              onClick={() => { setIsSignUp(!isSignUp); setError(null); setSuccess(null); }}
              className="text-slate-600 font-medium hover:text-primary-600 transition-colors"
            >
              {isSignUp ? 
                <span>Déjà membre ? <strong>Connectez-vous</strong></span> : 
                <span>Nouveau ici ? <strong>Créez un compte gratuitement</strong></span>
              }
            </button>
          </div>
          
          <div className="mt-6 flex justify-center">
            <button 
              onClick={handleDemoMode}
              className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 border border-slate-200 px-3 py-1.5 rounded-full hover:bg-slate-50 transition-all"
            >
              <ShieldCheck className="h-3 w-3" />
              Accès Démo Rapide (Bypass Email)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
