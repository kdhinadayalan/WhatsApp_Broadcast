import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, FolderOpen, FileText, Send, BarChart3, BookOpen, Bot } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/contacts', label: 'Contacts', icon: Users },
  { path: '/groups', label: 'Groups', icon: FolderOpen },
  { path: '/templates', label: 'Templates', icon: FileText },
  { path: '/broadcast/new', label: 'New Broadcast', icon: Send },
  { path: '/broadcasts', label: 'Broadcasts', icon: BarChart3 },
  { path: '/knowledge-base', label: 'Knowledge Base', icon: BookOpen },
  { path: '/ai-assistant', label: 'AI WhatsApp Bot', icon: Bot },
];

export default function Layout({ children }) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navbar */}
      <header className="bg-green-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📢</span>
            <div>
              <h1 className="text-lg font-bold">NMC College</h1>
              <p className="text-xs text-green-200">WhatsApp Broadcast System</p>
            </div>
          </div>
          <div className="text-sm text-green-200">Meta WhatsApp Cloud API</div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <nav className="w-56 bg-white shadow-md min-h-[calc(100vh-64px)] border-r">
          <ul className="py-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-3 px-5 py-3 text-sm transition-colors ${
                      isActive
                        ? 'bg-green-50 text-green-700 border-r-3 border-green-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon size={18} />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
