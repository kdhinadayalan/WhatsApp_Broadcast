import { useState, useEffect } from 'react';
import {
  BookOpen, Plus, Search, Edit2, Trash2, FileText, CheckCircle2,
  RefreshCw, Upload, FileUp, HelpCircle, Layers, Sparkles
} from 'lucide-react';
import toast from 'react-hot-toast';
import {
  getKnowledgeCategories, getKnowledgeItems, createKnowledgeItem,
  updateKnowledgeItem, deleteKnowledgeItem, getFAQs, createFAQ,
  updateFAQ, deleteFAQ, getKnowledgeDocuments, uploadKnowledgeDocument,
  deleteKnowledgeDocument, syncOpenClawAgent, getAIAssistantStats
} from '../services/api';

export default function KnowledgeBase() {
  const [activeTab, setActiveTab] = useState('items'); // 'items', 'faqs', 'documents'
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  // Items State
  const [items, setItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [itemModalOpen, setItemModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [itemForm, setItemForm] = useState({ category: '', title: '', content: '', tags: '', is_active: true, priority: 10 });

  // FAQs State
  const [faqs, setFaqs] = useState([]);
  const [faqSearch, setFaqSearch] = useState('');
  const [faqModalOpen, setFaqModalOpen] = useState(false);
  const [editingFaq, setEditingFaq] = useState(null);
  const [faqForm, setFaqForm] = useState({ category: '', question: '', answer: '', keywords: '', is_active: true, priority: 10 });

  // Documents State
  const [documents, setDocuments] = useState([]);
  const [docModalOpen, setDocModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [docTitle, setDocTitle] = useState('');
  const [docCategory, setDocCategory] = useState('');

  useEffect(() => {
    loadCategoriesAndStats();
  }, []);

  useEffect(() => {
    if (activeTab === 'items') loadItems();
    if (activeTab === 'faqs') loadFAQs();
    if (activeTab === 'documents') loadDocuments();
  }, [activeTab, selectedCategory, searchQuery, faqSearch]);

  const loadCategoriesAndStats = async () => {
    try {
      const [catsRes, statsRes] = await Promise.all([
        getKnowledgeCategories(),
        getAIAssistantStats()
      ]);
      setCategories(catsRes.data.results || catsRes.data || []);
      setStats(statsRes.data);
    } catch (err) {
      toast.error('Failed to load categories');
    }
  };

  const loadItems = async () => {
    setLoading(true);
    try {
      const params = {};
      if (selectedCategory) params.category = selectedCategory;
      if (searchQuery) params.search = searchQuery;
      const res = await getKnowledgeItems(params);
      setItems(res.data.results || res.data || []);
    } catch (err) {
      toast.error('Failed to load knowledge items');
    } finally {
      setLoading(false);
    }
  };

  const loadFAQs = async () => {
    setLoading(true);
    try {
      const params = {};
      if (faqSearch) params.search = faqSearch;
      const res = await getFAQs(params);
      setFaqs(res.data.results || res.data || []);
    } catch (err) {
      toast.error('Failed to load FAQs');
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const res = await getKnowledgeDocuments();
      setDocuments(res.data.results || res.data || []);
    } catch (err) {
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleSyncAgent = async () => {
    setSyncing(true);
    try {
      const res = await syncOpenClawAgent();
      toast.success(res.data.message || 'Knowledge synchronized to OpenClaw agent!');
      loadCategoriesAndStats();
    } catch (err) {
      toast.error('Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  // Item Actions
  const handleSaveItem = async (e) => {
    e.preventDefault();
    try {
      if (editingItem) {
        await updateKnowledgeItem(editingItem.id, itemForm);
        toast.success('Knowledge item updated!');
      } else {
        await createKnowledgeItem(itemForm);
        toast.success('Knowledge item added!');
      }
      setItemModalOpen(false);
      setEditingItem(null);
      loadItems();
      loadCategoriesAndStats();
    } catch (err) {
      toast.error('Failed to save item');
    }
  };

  const handleDeleteItem = async (id) => {
    if (!window.confirm('Are you sure you want to delete this knowledge entry?')) return;
    try {
      await deleteKnowledgeItem(id);
      toast.success('Item deleted');
      loadItems();
      loadCategoriesAndStats();
    } catch (err) {
      toast.error('Delete failed');
    }
  };

  // FAQ Actions
  const handleSaveFAQ = async (e) => {
    e.preventDefault();
    try {
      if (editingFaq) {
        await updateFAQ(editingFaq.id, faqForm);
        toast.success('FAQ updated!');
      } else {
        await createFAQ(faqForm);
        toast.success('FAQ created!');
      }
      setFaqModalOpen(false);
      setEditingFaq(null);
      loadFAQs();
      loadCategoriesAndStats();
    } catch (err) {
      toast.error('Failed to save FAQ');
    }
  };

  const handleDeleteFAQ = async (id) => {
    if (!window.confirm('Delete this FAQ?')) return;
    try {
      await deleteFAQ(id);
      toast.success('FAQ deleted');
      loadFAQs();
    } catch (err) {
      toast.error('Delete failed');
    }
  };

  // Document Upload
  const handleUploadDoc = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      toast.error('Please choose a file');
      return;
    }
    const formData = new FormData();
    formData.append('title', docTitle || selectedFile.name);
    formData.append('file', selectedFile);
    if (docCategory) formData.append('category', docCategory);

    try {
      await uploadKnowledgeDocument(formData);
      toast.success('Document uploaded & text extracted successfully!');
      setDocModalOpen(false);
      setSelectedFile(null);
      setDocTitle('');
      loadDocuments();
      loadCategoriesAndStats();
    } catch (err) {
      toast.error('Document upload failed');
    }
  };

  const handleDeleteDoc = async (id) => {
    if (!window.confirm('Delete this document?')) return;
    try {
      await deleteKnowledgeDocument(id);
      toast.success('Document deleted');
      loadDocuments();
    } catch (err) {
      toast.error('Delete failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BookOpen className="text-green-700" size={26} />
            College Knowledge Base (RAG)
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Authoritative source of truth for the WhatsApp AI Assistant and OpenClaw agent.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSyncAgent}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium shadow-sm transition-all"
          >
            <RefreshCw size={16} className={syncing ? 'animate-spin text-green-700' : 'text-gray-500'} />
            {syncing ? 'Syncing...' : 'Sync to OpenClaw'}
          </button>

          {activeTab === 'items' && (
            <button
              onClick={() => {
                setEditingItem(null);
                setItemForm({ category: categories[0]?.id || '', title: '', content: '', tags: '', is_active: true, priority: 10 });
                setItemModalOpen(true);
              }}
              className="flex items-center gap-2 px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 text-sm font-medium shadow-sm"
            >
              <Plus size={16} />
              Add Knowledge Item
            </button>
          )}

          {activeTab === 'faqs' && (
            <button
              onClick={() => {
                setEditingFaq(null);
                setFaqForm({ category: categories[0]?.id || '', question: '', answer: '', keywords: '', is_active: true, priority: 10 });
                setFaqModalOpen(true);
              }}
              className="flex items-center gap-2 px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 text-sm font-medium shadow-sm"
            >
              <Plus size={16} />
              Add FAQ
            </button>
          )}

          {activeTab === 'documents' && (
            <button
              onClick={() => {
                setSelectedFile(null);
                setDocTitle('');
                setDocCategory(categories[0]?.id || '');
                setDocModalOpen(true);
              }}
              className="flex items-center gap-2 px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 text-sm font-medium shadow-sm"
            >
              <Upload size={16} />
              Upload PDF / Document
            </button>
          )}
        </div>
      </div>

      {/* KPI Metric Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Knowledge Items</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_knowledge_items}</p>
            </div>
            <div className="p-3 bg-green-50 text-green-700 rounded-lg">
              <Layers size={22} />
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Configured FAQs</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_faqs}</p>
            </div>
            <div className="p-3 bg-blue-50 text-blue-700 rounded-lg">
              <HelpCircle size={22} />
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Indexed Documents</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_documents}</p>
            </div>
            <div className="p-3 bg-purple-50 text-purple-700 rounded-lg">
              <FileText size={22} />
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Agent Accuracy</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.answered_percentage || 100}%</p>
            </div>
            <div className="p-3 bg-amber-50 text-amber-700 rounded-lg">
              <Sparkles size={22} />
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('items')}
          className={`py-3 px-5 text-sm font-medium border-b-2 flex items-center gap-2 ${
            activeTab === 'items'
              ? 'border-green-700 text-green-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Layers size={18} />
          Knowledge Items ({stats?.total_knowledge_items || items.length})
        </button>

        <button
          onClick={() => setActiveTab('faqs')}
          className={`py-3 px-5 text-sm font-medium border-b-2 flex items-center gap-2 ${
            activeTab === 'faqs'
              ? 'border-green-700 text-green-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <HelpCircle size={18} />
          FAQs ({stats?.total_faqs || faqs.length})
        </button>

        <button
          onClick={() => setActiveTab('documents')}
          className={`py-3 px-5 text-sm font-medium border-b-2 flex items-center gap-2 ${
            activeTab === 'documents'
              ? 'border-green-700 text-green-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <FileText size={18} />
          Documents & Circulars ({stats?.total_documents || documents.length})
        </button>
      </div>

      {/* TAB 1: KNOWLEDGE ITEMS */}
      {activeTab === 'items' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search knowledge items by title, tags, or content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-50 text-gray-600 border-b">
                  <tr>
                    <th className="px-6 py-3 font-semibold">Title & Category</th>
                    <th className="px-6 py-3 font-semibold">Content Preview</th>
                    <th className="px-6 py-3 font-semibold">Tags</th>
                    <th className="px-6 py-3 font-semibold">Status</th>
                    <th className="px-6 py-3 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {loading ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-8 text-center text-gray-500">Loading knowledge items...</td>
                    </tr>
                  ) : items.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-8 text-center text-gray-500">No knowledge items found.</td>
                    </tr>
                  ) : (
                    items.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <p className="font-semibold text-gray-900">{item.title}</p>
                          <span className="inline-block mt-1 px-2 py-0.5 text-xs rounded bg-green-50 text-green-700 font-medium">
                            {item.category_name}
                          </span>
                        </td>
                        <td className="px-6 py-4 max-w-md">
                          <p className="text-gray-600 text-xs line-clamp-2 whitespace-pre-line">{item.content}</p>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-1">
                            {item.tags?.split(',').slice(0, 3).map((t, i) => (
                              <span key={i} className="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                                {t.trim()}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                            item.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                          }`}>
                            {item.is_active ? 'Active' : 'Draft'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => {
                                setEditingItem(item);
                                setItemForm({
                                  category: item.category,
                                  title: item.title,
                                  content: item.content,
                                  tags: item.tags || '',
                                  is_active: item.is_active,
                                  priority: item.priority || 10
                                });
                                setItemModalOpen(true);
                              }}
                              className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                              title="Edit item"
                            >
                              <Edit2 size={16} />
                            </button>
                            <button
                              onClick={() => handleDeleteItem(item.id)}
                              className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                              title="Delete item"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: FAQS */}
      {activeTab === 'faqs' && (
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search FAQs by question or answer..."
              value={faqSearch}
              onChange={(e) => setFaqSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {loading ? (
              <div className="col-span-2 text-center py-8 text-gray-500">Loading FAQs...</div>
            ) : faqs.length === 0 ? (
              <div className="col-span-2 text-center py-8 text-gray-500">No FAQs found.</div>
            ) : (
              faqs.map((faq) => (
                <div key={faq.id} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <span className="text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-medium">
                        {faq.category_name || 'General'}
                      </span>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => {
                            setEditingFaq(faq);
                            setFaqForm({
                              category: faq.category || '',
                              question: faq.question,
                              answer: faq.answer,
                              keywords: faq.keywords || '',
                              is_active: faq.is_active,
                              priority: faq.priority || 10
                            });
                            setFaqModalOpen(true);
                          }}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 size={15} />
                        </button>
                        <button
                          onClick={() => handleDeleteFAQ(faq.id)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </div>
                    <h3 className="font-semibold text-gray-900 mt-2 text-sm">{faq.question}</h3>
                    <p className="text-gray-600 text-xs mt-2 leading-relaxed whitespace-pre-line bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                      {faq.answer}
                    </p>
                  </div>
                  {faq.keywords && (
                    <p className="text-[11px] text-gray-400 mt-3 truncate">
                      Keywords: {faq.keywords}
                    </p>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* TAB 3: DOCUMENTS */}
      {activeTab === 'documents' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {documents.length === 0 ? (
              <div className="col-span-3 text-center py-12 bg-white rounded-xl border border-gray-200 text-gray-500">
                <FileUp className="mx-auto text-gray-400 mb-2" size={32} />
                No circulars or brochures uploaded yet. Click "Upload PDF / Document" above to index documents for RAG.
              </div>
            ) : (
              documents.map((doc) => (
                <div key={doc.id} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-50 text-purple-700 uppercase">
                        {doc.file_type || 'PDF'}
                      </span>
                      <button
                        onClick={() => handleDeleteDoc(doc.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                    <h4 className="font-semibold text-gray-900 mt-2 text-sm truncate" title={doc.title}>
                      {doc.title}
                    </h4>
                    <p className="text-xs text-gray-500 mt-1">Category: {doc.category_name || 'General'}</p>
                    <div className="mt-3 p-2 bg-gray-50 rounded border text-[11px] text-gray-600 max-h-24 overflow-y-auto">
                      <p className="font-medium text-gray-700 mb-1">Parsed Text Sample:</p>
                      {doc.extracted_text ? doc.extracted_text.slice(0, 200) + '...' : 'No text extracted'}
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t text-[11px] text-gray-400 flex items-center justify-between">
                    <span>Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}</span>
                    <span className="text-green-600 font-medium flex items-center gap-1">
                      <CheckCircle2 size={12} /> Indexed
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* MODAL: ITEM EDIT / CREATE */}
      {itemModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl space-y-4">
            <h2 className="text-lg font-bold text-gray-900">
              {editingItem ? 'Edit Knowledge Item' : 'Add Knowledge Item'}
            </h2>
            <form onSubmit={handleSaveItem} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Category</label>
                <select
                  required
                  value={itemForm.category}
                  onChange={(e) => setItemForm({ ...itemForm, category: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm bg-white"
                >
                  <option value="">Select Category</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. MCA HOD & Faculty Details"
                  value={itemForm.title}
                  onChange={(e) => setItemForm({ ...itemForm, title: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Content (Markdown / Facts)</label>
                <textarea
                  required
                  rows={5}
                  placeholder="Enter detailed facts, bullet points, names, dates, or fees..."
                  value={itemForm.content}
                  onChange={(e) => setItemForm({ ...itemForm, content: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Keywords / Search Tags</label>
                <input
                  type="text"
                  placeholder="mca, hod, faculty, muralidharan (comma-separated)"
                  value={itemForm.tags}
                  onChange={(e) => setItemForm({ ...itemForm, tags: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="item_active"
                  checked={itemForm.is_active}
                  onChange={(e) => setItemForm({ ...itemForm, is_active: e.target.checked })}
                  className="rounded text-green-700"
                />
                <label htmlFor="item_active" className="text-sm text-gray-700">Active (Visible to AI)</label>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setItemModalOpen(false)}
                  className="px-4 py-2 border rounded-lg text-sm text-gray-600 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-700 text-white rounded-lg text-sm font-medium hover:bg-green-800"
                >
                  Save Knowledge Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: FAQ EDIT / CREATE */}
      {faqModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl space-y-4">
            <h2 className="text-lg font-bold text-gray-900">
              {editingFaq ? 'Edit FAQ' : 'Add New FAQ'}
            </h2>
            <form onSubmit={handleSaveFAQ} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Category</label>
                <select
                  value={faqForm.category}
                  onChange={(e) => setFaqForm({ ...faqForm, category: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm bg-white"
                >
                  <option value="">General</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Question</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Who is the HOD of MCA?"
                  value={faqForm.question}
                  onChange={(e) => setFaqForm({ ...faqForm, question: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Answer</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Concise, student-friendly answer..."
                  value={faqForm.answer}
                  onChange={(e) => setFaqForm({ ...faqForm, answer: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Search Keywords</label>
                <input
                  type="text"
                  placeholder="mca hod, head of department, muralidharan"
                  value={faqForm.keywords}
                  onChange={(e) => setFaqForm({ ...faqForm, keywords: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setFaqModalOpen(false)}
                  className="px-4 py-2 border rounded-lg text-sm text-gray-600 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-700 text-white rounded-lg text-sm font-medium hover:bg-green-800"
                >
                  Save FAQ
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: DOCUMENT UPLOAD */}
      {docModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h2 className="text-lg font-bold text-gray-900">Upload Knowledge Document</h2>
            <p className="text-xs text-gray-500">
              Upload circulars, prospectuses, or fee schedules (PDF/TXT/MD). Text will be automatically extracted and indexed for RAG.
            </p>
            <form onSubmit={handleUploadDoc} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Document Title</label>
                <input
                  type="text"
                  placeholder="e.g. MCA Prospectus 2026"
                  value={docTitle}
                  onChange={(e) => setDocTitle(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Category</label>
                <select
                  value={docCategory}
                  onChange={(e) => setDocCategory(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg text-sm bg-white"
                >
                  <option value="">General</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Choose File</label>
                <input
                  type="file"
                  required
                  accept=".pdf,.txt,.md"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  className="w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setDocModalOpen(false)}
                  className="px-4 py-2 border rounded-lg text-sm text-gray-600 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-700 text-white rounded-lg text-sm font-medium hover:bg-green-800"
                >
                  Upload & Index
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
