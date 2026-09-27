import { useState, useEffect } from 'react';
import { getTemplates } from '../services/api';
import { FileText } from 'lucide-react';

export default function Templates() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTemplates()
      .then((res) => setTemplates(res.data.results || res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const statusColors = {
    APPROVED: 'bg-green-100 text-green-700',
    PENDING: 'bg-yellow-100 text-yellow-700',
    REJECTED: 'bg-red-100 text-red-700',
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Message Templates</h2>
      <p className="text-sm text-gray-500 mb-6">
        These templates must be approved by Meta before you can use them in broadcasts.
        Templates with {'{{1}}'}, {'{{2}}'} etc. are filled with dynamic values when sending.
      </p>

      {loading ? (
        <p className="text-gray-400 text-center py-8">Loading...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((t) => (
            <div key={t.id} className="bg-white rounded-xl shadow-sm border p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <FileText size={18} className="text-green-600" />
                  <h3 className="font-semibold text-gray-800">{t.name}</h3>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${statusColors[t.status]}`}>{t.status}</span>
              </div>
              <div className="bg-green-50 rounded-lg p-4 mb-3 border border-green-100">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{t.body_text}</p>
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>Meta: <code className="bg-gray-100 px-1 rounded">{t.meta_template_name}</code></span>
                <span>Lang: {t.language}</span>
                <span>Params: {t.param_count}</span>
                <span>Category: {t.category}</span>
              </div>
              {t.sample_params?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs text-gray-400 mb-1">Sample values:</p>
                  <div className="flex flex-wrap gap-1">
                    {t.sample_params.map((p, i) => (
                      <span key={i} className="text-xs bg-gray-100 px-2 py-1 rounded">{'{{' + (i + 1) + '}}'}: {p}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
