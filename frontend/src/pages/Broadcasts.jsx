import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getBroadcasts } from '../services/api';
import { Eye, Send } from 'lucide-react';

export default function Broadcasts() {
  const [broadcasts, setBroadcasts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getBroadcasts()
      .then((res) => setBroadcasts(res.data.results || res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const statusColors = {
    DRAFT: 'bg-gray-100 text-gray-600',
    QUEUED: 'bg-yellow-100 text-yellow-700',
    SENDING: 'bg-blue-100 text-blue-700',
    COMPLETED: 'bg-green-100 text-green-700',
    FAILED: 'bg-red-100 text-red-700',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Broadcasts</h2>
        <Link to="/broadcast/new"
          className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
          <Send size={18} /> New Broadcast
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Title</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Template</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Recipients</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Delivery</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {loading ? (
              <tr><td colSpan="7" className="text-center py-8 text-gray-400">Loading...</td></tr>
            ) : broadcasts.length === 0 ? (
              <tr><td colSpan="7" className="text-center py-8 text-gray-400">No broadcasts yet. Create your first one!</td></tr>
            ) : (
              broadcasts.map((b) => (
                <tr key={b.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-800">{b.title}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{b.template_name}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${statusColors[b.status]}`}>{b.status}</span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{b.total_recipients}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: `${b.delivery_rate || 0}%` }} />
                      </div>
                      <span className="text-xs text-gray-500">{b.delivery_rate || 0}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{new Date(b.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <Link to={`/broadcasts/${b.id}`} className="text-green-600 hover:text-green-800">
                      <Eye size={16} />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
