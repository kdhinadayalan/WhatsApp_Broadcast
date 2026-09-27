import { useState, useEffect } from 'react';
import { getGroups, createGroup } from '../services/api';
import { Plus, X, Users } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Groups() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', group_type: 'CUSTOM' });

  const fetchGroups = () => {
    setLoading(true);
    getGroups()
      .then((res) => setGroups(res.data.results || res.data))
      .catch(() => toast.error('Failed to load groups'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchGroups(); }, []);

  const handleCreate = (e) => {
    e.preventDefault();
    createGroup(form)
      .then(() => { toast.success('Group created!'); setShowForm(false); setForm({ name: '', description: '', group_type: 'CUSTOM' }); fetchGroups(); })
      .catch(() => toast.error('Failed to create group'));
  };

  const typeColors = {
    ROLE: 'bg-blue-100 text-blue-700',
    DEPARTMENT: 'bg-purple-100 text-purple-700',
    CUSTOM: 'bg-gray-100 text-gray-700',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Contact Groups</h2>
        <button onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
          {showForm ? <X size={18} /> : <Plus size={18} />} {showForm ? 'Cancel' : 'New Group'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl shadow-sm p-6 border mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Group Name *" required
              value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Description"
              value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            <select className="border rounded-lg px-3 py-2 text-sm"
              value={form.group_type} onChange={(e) => setForm({ ...form, group_type: e.target.value })}>
              <option value="CUSTOM">Custom</option>
              <option value="ROLE">Role-based</option>
              <option value="DEPARTMENT">Department-based</option>
            </select>
          </div>
          <button type="submit" className="mt-4 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">Create Group</button>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {loading ? (
          <p className="text-gray-400 col-span-3 text-center py-8">Loading...</p>
        ) : groups.length === 0 ? (
          <p className="text-gray-400 col-span-3 text-center py-8">No groups found</p>
        ) : (
          groups.map((g) => (
            <div key={g.id} className="bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-800">{g.name}</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${typeColors[g.group_type]}`}>{g.group_type}</span>
              </div>
              <p className="text-sm text-gray-500 mb-3">{g.description || 'No description'}</p>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Users size={16} />
                <span>{g.member_count} members</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
