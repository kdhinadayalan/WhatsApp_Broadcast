import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getBroadcastDetail, getBroadcastRecipients, sendBroadcast, retryFailedMessages } from '../services/api';
import { Send, RefreshCw, CheckCircle, Eye, AlertCircle, Clock } from 'lucide-react';
import toast from 'react-hot-toast';

export default function BroadcastDetail() {
  const { id } = useParams();
  const [broadcast, setBroadcast] = useState(null);
  const [recipients, setRecipients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  const fetchData = () => {
    Promise.all([
      getBroadcastDetail(id),
      getBroadcastRecipients(id, statusFilter ? { status: statusFilter } : {}),
    ])
      .then(([bRes, rRes]) => {
        setBroadcast(bRes.data);
        setRecipients(rRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [id, statusFilter]);

  // Auto-refresh if sending
  useEffect(() => {
    if (broadcast?.status === 'SENDING') {
      const interval = setInterval(fetchData, 5000);
      return () => clearInterval(interval);
    }
  }, [broadcast?.status]);

  const handleSend = () => {
    sendBroadcast(id)
      .then(() => { toast.success('Broadcast started!'); fetchData(); })
      .catch((err) => toast.error(err.response?.data?.error || 'Failed'));
  };

  const handleRetry = () => {
    retryFailedMessages(id)
      .then((res) => { toast.success(res.data.message); fetchData(); })
      .catch(() => toast.error('Retry failed'));
  };

  if (loading) return <div className="text-center py-20 text-gray-400">Loading...</div>;
  if (!broadcast) return <div className="text-center py-20 text-red-500">Broadcast not found</div>;

  const progress = broadcast.total_recipients > 0
    ? Math.round(((broadcast.sent_count + broadcast.failed_count) / broadcast.total_recipients) * 100)
    : 0;

  const statusIcons = {
    PENDING: <Clock size={14} className="text-gray-400" />,
    SENT: <Send size={14} className="text-blue-500" />,
    DELIVERED: <CheckCircle size={14} className="text-green-500" />,
    READ: <Eye size={14} className="text-purple-500" />,
    FAILED: <AlertCircle size={14} className="text-red-500" />,
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">{broadcast.title}</h2>
      <p className="text-sm text-gray-500 mb-6">
        Template: {broadcast.template?.name} | Created: {new Date(broadcast.created_at).toLocaleString()}
      </p>

      {/* Stats */}
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <span className={`text-xs font-medium px-3 py-1 rounded-full ${
            broadcast.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
            broadcast.status === 'SENDING' ? 'bg-blue-100 text-blue-700' :
            broadcast.status === 'FAILED' ? 'bg-red-100 text-red-700' :
            'bg-gray-100 text-gray-600'
          }`}>{broadcast.status}</span>
          <div className="flex gap-2">
            {broadcast.status === 'DRAFT' && (
              <button onClick={handleSend} className="flex items-center gap-1 bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700">
                <Send size={14} /> Send Now
              </button>
            )}
            {broadcast.failed_count > 0 && (
              <button onClick={handleRetry} className="flex items-center gap-1 bg-orange-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-orange-600">
                <RefreshCw size={14} /> Retry Failed ({broadcast.failed_count})
              </button>
            )}
            <button onClick={fetchData} className="flex items-center gap-1 border px-3 py-2 rounded-lg text-sm hover:bg-gray-50">
              <RefreshCw size={14} /> Refresh
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div className="bg-green-500 h-3 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {/* Counters */}
        <div className="grid grid-cols-5 gap-4">
          {[
            { label: 'Total', value: broadcast.total_recipients, color: 'text-gray-700' },
            { label: 'Sent', value: broadcast.sent_count, color: 'text-blue-600' },
            { label: 'Delivered', value: broadcast.delivered_count, color: 'text-green-600' },
            { label: 'Read', value: broadcast.read_count, color: 'text-purple-600' },
            { label: 'Failed', value: broadcast.failed_count, color: 'text-red-600' },
          ].map((s) => (
            <div key={s.label} className="text-center">
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-gray-500">{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recipients Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="px-4 py-3 border-b flex items-center justify-between">
          <h3 className="font-semibold text-gray-700">Recipients</h3>
          <select className="border rounded-lg px-3 py-1 text-sm"
            value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Status</option>
            <option value="PENDING">Pending</option>
            <option value="SENT">Sent</option>
            <option value="DELIVERED">Delivered</option>
            <option value="READ">Read</option>
            <option value="FAILED">Failed</option>
          </select>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Name</th>
              <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Phone</th>
              <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Role</th>
              <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Status</th>
              <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Error</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {recipients.length === 0 ? (
              <tr><td colSpan="5" className="text-center py-6 text-gray-400">{broadcast.status === 'DRAFT' ? 'Send the broadcast to see recipients' : 'No recipients'}</td></tr>
            ) : (
              recipients.map((r, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-sm font-medium text-gray-700">{r.contact_name}</td>
                  <td className="px-4 py-2 text-sm text-gray-500">{r.contact_phone}</td>
                  <td className="px-4 py-2 text-sm text-gray-500">{r.contact_role}</td>
                  <td className="px-4 py-2">
                    <span className="flex items-center gap-1">
                      {statusIcons[r.status]}
                      <span className="text-xs">{r.status}</span>
                    </span>
                  </td>
                  <td className="px-4 py-2 text-xs text-red-500">{r.error_message || '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
