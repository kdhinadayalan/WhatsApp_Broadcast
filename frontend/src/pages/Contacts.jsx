import { useState, useEffect } from 'react';
import { getContacts, createContact, deleteContact } from '../services/api';
import { Plus, Search, Trash2, X } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', phone_number: '', role: 'STUDENT', department: '', email: '', enrollment_no: '' });

  const fetchContacts = () => {
    setLoading(true);
    const params = {};
    if (search) params.search = search;
    if (roleFilter) params.role = roleFilter;
    getContacts(params)
      .then((res) => setContacts(res.data.results || res.data))
      .catch(() => toast.error('Failed to load contacts'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchContacts(); }, [search, roleFilter]);

  const handleCreate = (e) => {
    e.preventDefault();
    createContact(form)
      .then(() => {
        toast.success('Contact created!');
        setShowForm(false);
        setForm({ name: '', phone_number: '', role: 'STUDENT', department: '', email: '', enrollment_no: '' });
        fetchContacts();
      })
      .catch((err) => toast.error(err.response?.data?.phone_number?.[0] || 'Failed to create contact'));
  };

  const handleDelete = (id, name) => {
    if (!confirm(`Delete contact "${name}"?`)) return;
    deleteContact(id)
      .then(() => { toast.success('Contact deleted'); fetchContacts(); })
      .catch(() => toast.error('Failed to delete'));
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Contacts</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
        >
          {showForm ? <X size={18} /> : <Plus size={18} />}
          {showForm ? 'Cancel' : 'Add Contact'}
        </button>
      </div>

      {/* Add Contact Form */}
      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl shadow-sm p-6 border mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Name *" required
              value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Phone (e.g. 919876543210) *" required
              value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
            <select className="border rounded-lg px-3 py-2 text-sm"
              value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="STUDENT">Student</option>
              <option value="STAFF">Staff</option>
              <option value="HOD">HOD</option>
              <option value="PARENT">Parent</option>
              <option value="OTHER">Other</option>
            </select>
            <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Department"
              value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
            <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Email"
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Enrollment No"
              value={form.enrollment_no} onChange={(e) => setForm({ ...form, enrollment_no: e.target.value })} />
          </div>
          <button type="submit" className="mt-4 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">
            Save Contact
          </button>
        </form>
      )}

      {/* Filters */}
      <div className="flex gap-4 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
          <input className="w-full border rounded-lg pl-9 pr-3 py-2 text-sm" placeholder="Search contacts..."
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select className="border rounded-lg px-3 py-2 text-sm"
          value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
          <option value="">All Roles</option>
          <option value="STUDENT">Student</option>
          <option value="STAFF">Staff</option>
          <option value="HOD">HOD</option>
          <option value="PARENT">Parent</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Phone</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Department</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {loading ? (
              <tr><td colSpan="6" className="text-center py-8 text-gray-400">Loading...</td></tr>
            ) : contacts.length === 0 ? (
              <tr><td colSpan="6" className="text-center py-8 text-gray-400">No contacts found</td></tr>
            ) : (
              contacts.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-800">{c.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{c.phone_number}</td>
                  <td className="px-4 py-3"><RoleBadge role={c.role} /></td>
                  <td className="px-4 py-3 text-sm text-gray-600">{c.department || '-'}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${c.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {c.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => handleDelete(c.id, c.name)} className="text-red-400 hover:text-red-600">
                      <Trash2 size={16} />
                    </button>
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

function RoleBadge({ role }) {
  const colors = {
    STUDENT: 'bg-blue-100 text-blue-700',
    STAFF: 'bg-purple-100 text-purple-700',
    HOD: 'bg-orange-100 text-orange-700',
    PARENT: 'bg-teal-100 text-teal-700',
    OTHER: 'bg-gray-100 text-gray-700',
  };
  return <span className={`text-xs font-medium px-2 py-1 rounded-full ${colors[role] || 'bg-gray-100'}`}>{role}</span>;
}
