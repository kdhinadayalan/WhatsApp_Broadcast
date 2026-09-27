import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardStats } from '../services/api';
import { Users, Send, CheckCircle, Eye, AlertCircle, Plus } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then((res) => setStats(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-20 text-gray-500">Loading dashboard...</div>;
  if (!stats) return <div className="text-center py-20 text-red-500">Failed to load dashboard</div>;

  const statCards = [
    { label: 'Total Contacts', value: stats.total_contacts, icon: Users, color: 'bg-blue-500' },
    { label: 'Messages Sent', value: stats.total_sent, icon: Send, color: 'bg-green-500' },
    { label: 'Delivered', value: stats.total_delivered, icon: CheckCircle, color: 'bg-emerald-500' },
    { label: 'Read', value: stats.total_read, icon: Eye, color: 'bg-purple-500' },
    { label: 'Failed', value: stats.total_failed, icon: AlertCircle, color: 'bg-red-500' },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
        <Link
          to="/broadcast/new"
          className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
        >
          <Plus size={18} /> New Broadcast
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="bg-white rounded-xl shadow-sm p-4 border">
              <div className={`inline-flex p-2 rounded-lg ${card.color} text-white mb-2`}>
                <Icon size={20} />
              </div>
              <p className="text-2xl font-bold text-gray-800">{card.value?.toLocaleString() || 0}</p>
              <p className="text-sm text-gray-500">{card.label}</p>
            </div>
          );
        })}
      </div>

      {/* Contacts by Role */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm p-6 border">
          <h3 className="font-semibold text-gray-700 mb-4">Contacts by Role</h3>
          <div className="space-y-3">
            {stats.contacts_by_role?.map((item) => (
              <div key={item.role} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{item.role}</span>
                <span className="bg-green-100 text-green-700 text-sm font-medium px-3 py-1 rounded-full">
                  {item.count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Broadcasts */}
        <div className="bg-white rounded-xl shadow-sm p-6 border">
          <h3 className="font-semibold text-gray-700 mb-4">Recent Broadcasts</h3>
          {stats.recent_broadcasts?.length === 0 ? (
            <p className="text-sm text-gray-400">No broadcasts yet</p>
          ) : (
            <div className="space-y-3">
              {stats.recent_broadcasts?.map((b) => (
                <Link
                  key={b.id}
                  to={`/broadcasts/${b.id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-700">{b.title}</p>
                    <p className="text-xs text-gray-400">{new Date(b.created_at).toLocaleDateString()}</p>
                  </div>
                  <StatusBadge status={b.status} />
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const colors = {
    DRAFT: 'bg-gray-100 text-gray-600',
    QUEUED: 'bg-yellow-100 text-yellow-700',
    SENDING: 'bg-blue-100 text-blue-700',
    COMPLETED: 'bg-green-100 text-green-700',
    FAILED: 'bg-red-100 text-red-700',
  };
  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full ${colors[status] || 'bg-gray-100'}`}>
      {status}
    </span>
  );
}
