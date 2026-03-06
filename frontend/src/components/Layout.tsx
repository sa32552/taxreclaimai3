
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Calculator, 
  FileText, 
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Téléverser', href: '/upload', icon: UploadCloud },
    { name: 'Récupération TVA', href: '/vat-recovery', icon: Calculator },
    { name: 'Formulaires', href: '/forms', icon: FileText },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar pour mobile */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-slate-900/50" onClick={() => setSidebarOpen(false)}></div>
        <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-xl">
          <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200">
            <span className="text-xl font-bold text-primary-600">TAXRECLAIMAI</span>
            <button onClick={() => setSidebarOpen(false)} className="text-slate-400 hover:text-slate-500">
              <X className="h-6 w-6" />
            </button>
          </div>
          <nav className="mt-6">
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
        </div>
      </div>

      {/* Sidebar pour desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:w-64 lg:bg-white lg:shadow-lg lg:flex lg:flex-col">
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
        <div className="p-6 border-t border-slate-200">
          <div className="text-xs text-slate-500">
            © 2023 TAXRECLAIMAI
          </div>
        </div>
      </div>

      {/* Contenu principal */}
      <div className="lg:pl-64">
        {/* Header mobile */}
        <div className="lg:hidden flex items-center justify-between h-16 px-4 bg-white border-b border-slate-200">
          <button onClick={() => setSidebarOpen(true)} className="text-slate-400 hover:text-slate-500">
            <Menu className="h-6 w-6" />
          </button>
          <span className="text-lg font-bold text-primary-600">TAXRECLAIMAI</span>
          <div className="w-6"></div>
        </div>

        {/* Contenu de la page */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
