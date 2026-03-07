import { useState, useEffect } from 'react';
import { Bell, Check, Info, AlertTriangle, AlertCircle, X, FileText } from 'lucide-react';
import { supabase } from '../supabase';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  status: 'unread' | 'read' | 'archived';
  created_at: string;
}

const NotificationBell = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();

    // S'abonner aux nouvelles notifications en temps réel
    const channel = supabase
      .channel('public:notifications')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'notifications' },
        (payload: any) => {
          const newNotification = payload.new as Notification;
          setNotifications((prev) => [newNotification, ...prev]);
          setUnreadCount((prev) => prev + 1);
          
          // Afficher un petit toast navigateur si possible ou juste mettre à jour le compteur
          if (Notification.permission === 'granted') {
            new Notification(newNotification.title, {
              body: newNotification.message,
            });
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  const fetchNotifications = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from('notifications')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(10);

      if (error) throw error;
      setNotifications(data || []);
      setUnreadCount(data?.filter((n: any) => n.status === 'unread').length || 0);
    } catch (err) {
      console.error('Erreur notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id: string) => {
    try {
      const { error } = await supabase
        .from('notifications')
        .update({ status: 'read' })
        .eq('id', id);

      if (error) throw error;
      
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, status: 'read' } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Erreur lecture notification:', err);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'normal': return 'text-blue-600 bg-blue-100';
      default: return 'text-slate-600 bg-slate-100';
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'OCR_COMPLETE': return <Check className="h-4 w-4 text-green-500" />;
      case 'OCR_ERROR': 
      case 'ocr_rejection': return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'VAT_CLAIM_APPROVED': return <Check className="h-4 w-4 text-primary-500" />;
      case 'VAT_CLAIM_REJECTED': return <X className="h-4 w-4 text-red-500" />;
      case 'auto_form_generated': return <FileText className="h-4 w-4 text-primary-500" />;
      default: return <Info className="h-4 w-4 text-slate-400" />;
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors focus:outline-none"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 z-20 bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden transform origin-top-right transition-all">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <h3 className="font-bold text-slate-900">Notifications</h3>
              <span className="text-xs font-medium text-slate-500">{unreadCount} non lues</span>
            </div>
            
            <div className="max-h-[400px] overflow-y-auto">
              {loading ? (
                <div className="p-8 text-center text-slate-400 text-sm italic">Chargement...</div>
              ) : notifications.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">Aucune notification</div>
              ) : (
                notifications.map((n) => (
                  <div 
                    key={n.id}
                    onClick={() => markAsRead(n.id)}
                    className={`p-4 border-b border-slate-50 cursor-pointer hover:bg-slate-50 transition-colors relative ${n.status === 'unread' ? 'bg-primary-50/30' : ''}`}
                  >
                    {n.status === 'unread' && (
                      <div className="absolute left-1 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary-500 rounded-full" />
                    )}
                    <div className="flex gap-3">
                      <div className={`mt-0.5 p-1.5 rounded-lg shrink-0 h-fit ${getPriorityColor(n.priority)}`}>
                        {getIcon(n.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-bold text-slate-900 truncate">{n.title}</p>
                        <p className="text-xs text-slate-600 line-clamp-2 mt-0.5">{n.message}</p>
                        <p className="text-[10px] text-slate-400 mt-2 flex items-center gap-1">
                          <AlertTriangle className="h-3 w-3" />
                          {new Date(n.created_at).toLocaleDateString('fr-FR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
            
            <div className="p-3 bg-slate-50 border-t border-slate-100 text-center">
              <button className="text-xs font-bold text-primary-600 hover:text-primary-700">
                Voir toutes les notifications
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationBell;
