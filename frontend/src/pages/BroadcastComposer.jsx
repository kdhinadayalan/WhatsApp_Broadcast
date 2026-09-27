import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getGroups, getTemplates, createBroadcast, sendBroadcast } from '../services/api';
import { Send, Save, Users } from 'lucide-react';
import toast from 'react-hot-toast';

export default function BroadcastComposer() {
  const navigate = useNavigate();
  const [groups, setGroups] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [title, setTitle] = useState('');
  const [params, setParams] = useState([]);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    getGroups().then((res) => setGroups(res.data.results || res.data));
    getTemplates({ status: 'APPROVED' }).then((res) => setTemplates(res.data.results || res.data));
  }, []);

  const handleTemplateChange = (templateId) => {
    const tmpl = templates.find((t) => t.id === parseInt(templateId));
    setSelectedTemplate(tmpl);
    if (tmpl) {
      setParams(Array(tmpl.param_count).fill(''));
    } else {
      setParams([]);
    }
  };

  const toggleGroup = (groupId) => {
    setSelectedGroups((prev) =>
      prev.includes(groupId) ? prev.filter((id) => id !== groupId) : [...prev, groupId]
    );
  };

  const totalRecipients = groups
    .filter((g) => selectedGroups.includes(g.id))
    .reduce((sum, g) => sum + (g.member_count || 0), 0);

  const getPreview = () => {
    if (!selectedTemplate) return '';
    let text = selectedTemplate.body_text;
    params.forEach((val, i) => {
      text = text.replace(`{{${i + 1}}}`, val || `{{${i + 1}}}`);
    });
    return text;
  };

  const handleSend = async (asDraft = false) => {
    if (!title.trim()) return toast.error('Please enter a broadcast title');
    if (!selectedTemplate) return toast.error('Please select a template');
    if (selectedGroups.length === 0) return toast.error('Please select at least one group');

    setSending(true);
    try {
      const res = await createBroadcast({
        title,
        template: selectedTemplate.id,
        template_params: params.filter((p) => p),
        group_ids: selectedGroups,
      });

      if (!asDraft) {
        await sendBroadcast(res.data.id);
        toast.success('Broadcast sent!');
      } else {
        toast.success('Broadcast saved as draft');
      }
      navigate('/broadcasts');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to create broadcast');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="max-w-4xl">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">📢 New Broadcast</h2>

      <div className="space-y-6">
        {/* Title */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Broadcast Title</label>
          <input className="w-full border rounded-lg px-4 py-2" placeholder="e.g. Exam Schedule Notification - Oct 2026"
            value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>

        {/* Audience */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <label className="text-sm font-medium text-gray-700">Select Audience</label>
            <span className="flex items-center gap-1 text-sm text-green-600 font-medium">
              <Users size={16} /> ~{totalRecipients} recipients
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {groups.map((g) => (
              <label key={g.id}
                className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition ${
                  selectedGroups.includes(g.id) ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'
                }`}>
                <input type="checkbox" className="accent-green-600"
                  checked={selectedGroups.includes(g.id)} onChange={() => toggleGroup(g.id)} />
                <div>
                  <p className="text-sm font-medium text-gray-700">{g.name}</p>
                  <p className="text-xs text-gray-400">{g.member_count} members</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Template Selection */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Message Template</label>
          <select className="w-full border rounded-lg px-4 py-2 mb-4"
            onChange={(e) => handleTemplateChange(e.target.value)}>
            <option value="">-- Select a template --</option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>{t.name} ({t.meta_template_name})</option>
            ))}
          </select>

          {/* Parameter inputs */}
          {selectedTemplate && selectedTemplate.param_count > 0 && (
            <div className="space-y-3 mb-4">
              <label className="text-sm font-medium text-gray-600">Fill Parameters:</label>
              {params.map((val, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-sm text-gray-500 w-16">{`{{${i + 1}}}`}</span>
                  <input className="flex-1 border rounded-lg px-3 py-2 text-sm"
                    placeholder={selectedTemplate.sample_params?.[i] || `Value for {{${i + 1}}}`}
                    value={val}
                    onChange={(e) => {
                      const newParams = [...params];
                      newParams[i] = e.target.value;
                      setParams(newParams);
                    }} />
                </div>
              ))}
            </div>
          )}

          {/* Preview */}
          {selectedTemplate && (
            <div>
              <label className="text-sm font-medium text-gray-600 mb-2 block">Preview:</label>
              <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">🏫</span>
                  <span className="text-sm font-semibold text-green-800">NMC College</span>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{getPreview()}</p>
                {selectedTemplate.footer_text && (
                  <p className="text-xs text-gray-400 mt-3">{selectedTemplate.footer_text}</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button onClick={() => handleSend(false)} disabled={sending}
            className="flex items-center gap-2 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium">
            <Send size={18} /> {sending ? 'Sending...' : 'Send Now'}
          </button>
          <button onClick={() => handleSend(true)} disabled={sending}
            className="flex items-center gap-2 bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 disabled:opacity-50">
            <Save size={18} /> Save as Draft
          </button>
        </div>
      </div>
    </div>
  );
}
