import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Calculator, 
  FileText, 
  Menu,
  X,
  LogOut,
  Settings,
  Shield
} from 'lucide-react';
import { supabase } from '../supabase';
import NotificationBell from './NotificationBell';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const getUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user || null);
    };
    getUser();

    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setUser(session?.user || null);
      }
    );

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Factures', href: '/upload', icon: UploadCloud },
    { name: 'Récupération TVA', href: '/vat-recovery', icon: Calculator },
    { name: 'Formulaires', href: '/forms', icon: FileText },
    { name: 'Audit & Sécurité', href: '/audit-logs', icon: Shield },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar mobile */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-slate-900/50" onClick={() => setSidebarOpen(false)}></div>
        <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-xl flex flex-col">
          <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200">
            <span className="text-xl font-bold text-primary-600">TAXRECLAIMAI</span>
            <button onClick={() => setSidebarOpen(false)} className="text-slate-400 hover:text-slate-500">
              <X className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 mt-6">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-600 border-r-4 border-primary-600'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="h-5 w-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          
          {user && (
            <div className="p-4 border-t border-slate-200 bg-slate-50">
              <div className="flex items-center space-x-3 mb-4">
                <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold">
                  {user.email?.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 truncate">{user.email}</p>
                  <p className="text-xs text-slate-500 truncate">Premium Account</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="w-full flex items-center px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <LogOut className="h-4 w-4 mr-3" />
                Déconnexion
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Sidebar desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:w-64 lg:bg-white lg:shadow-sm lg:flex lg:flex-col border-r border-slate-200">
        <div className="flex items-center h-16 px-6 border-b border-slate-200">
          <span className="text-xl font-bold text-primary-600">TAXRECLAIMAI</span>
        </div>
        <nav className="flex-1 mt-6">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-600 border-r-4 border-primary-600'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <item.icon className="h-5 w-5 mr-3" />
                {item.name}
              </Link>
            );
          })}
        </nav>
        
        {user && (
          <div className="p-4 border-t border-slate-200">
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-slate-50 cursor-pointer mb-2">
              <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-xs font-bold">
                {user.email?.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-900 truncate">{user.email}</p>
                <p className="text-[10px] text-slate-500 truncate">SaaS Pro Plan</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4">
              <button 
                title="Paramètres"
                className="flex items-center justify-center p-2 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <Settings className="h-5 w-5" />
              </button>
              <button
                title="Déconnexion"
                onClick={handleLogout}
                className="flex items-center justify-center p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="lg:pl-64">
        {/* Top Header Desktop */}
        <header className="hidden lg:flex h-16 bg-white border-b border-slate-200 items-center justify-between px-8 sticky top-0 z-10 shadow-sm/50">
          <div className="flex items-center gap-4 text-slate-500 text-sm">
            <span className="font-medium text-slate-900 capitalize">
              {location.pathname.replace('/', '').replace('-', ' ') || 'Dashboard'}
            </span>
            <span className="text-slate-300">/</span>
            <span className="text-xs text-slate-400">Entreprise: {user?.user_metadata?.company_name || 'Vérification...'}</span>
          </div>
          <div className="flex items-center gap-6">
            <div className="h-4 w-px bg-slate-200" />
            <NotificationBell />
            <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
              <div className="text-right">
                <p className="text-xs font-bold text-slate-900">{user?.email?.split('@')[0]}</p>
                <p className="text-[10px] text-primary-600 font-medium tracking-wider uppercase">Compte Expert</p>
              </div>
              <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-lg shadow-primary-200">
                {user?.email?.charAt(0).toUpperCase()}
              </div>
            </div>
          </div>
        </header>

        {/* Top Header Mobile */}
        <header className="lg:hidden flex h-16 bg-white border-b border-slate-200 items-center justify-between px-4 sticky top-0 z-10">
          <button 
            onClick={() => setSidebarOpen(true)}
            className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition-colors"
          >
            <Menu className="h-6 w-6" />
          </button>
          <span className="text-lg font-bold text-primary-600">TAXRECLAIMAI</span>
          <NotificationBell />
        </header>

        <main className="p-4 lg:p-8 max-w-[1400px] mx-auto animate-in fade-in slide-in-from-bottom-2 duration-500">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
