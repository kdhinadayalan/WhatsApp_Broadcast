import { useState, useEffect, useRef } from 'react';
import {
  Bot, Send, Sparkles, Clock, CheckCheck, RefreshCw,
  Search, ShieldCheck, Database, MessageSquare, AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import { simulateAIChat, getInquiryLogs } from '../services/api';

const SAMPLE_QUESTIONS = [
  "Who is the HOD of MCA?",
  "What is the college address?",
  "What are the MCA subjects?",
  "When does the semester start?",
  "What is the exam fee?",
  "What documents are required for admission?",
  "Tell me about the college departments.",
  "What are the college timings?",
  "Who won the 1994 FIFA world cup?", // To test zero hallucination fallback
];

export default function AIAssistantTest() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Hello! 🎓 I am the *NMC College WhatsApp AI Assistant*.\n\nYou can ask me anything about college admissions, MCA subjects, HODs, fees, semester dates, timings, or rules!',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [studentPhone, setStudentPhone] = useState('919876543210');
  const [loading, setLoading] = useState(false);
  const [latestResult, setLatestResult] = useState(null);

  // Inquiry Logs State
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadInquiries();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadInquiries = async () => {
    setLogsLoading(true);
    try {
      const res = await getInquiryLogs({ page_size: 15 });
      setLogs(res.data.results || res.data || []);
    } catch (err) {
      // quiet fail
    } finally {
      setLogsLoading(false);
    }
  };

  const handleSend = async (questionText = null) => {
    const query = (questionText || inputQuestion).trim();
    if (!query) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
      timestamp: timeStr,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuestion('');
    setLoading(true);

    try {
      const res = await simulateAIChat({
        question: query,
        phone_number: studentPhone,
      });

      const data = res.data;
      setLatestResult(data);

      const botMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.answer,
        status: data.status,
        intent: data.intent,
        latency_ms: data.latency_ms,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
      loadInquiries();
    } catch (err) {
      toast.error('Failed to get response from AI assistant');
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: "I don't have this information currently. Please contact the college office for the correct details.",
          status: 'FALLBACK',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Bot className="text-green-700" size={28} />
            WhatsApp AI Assistant Simulator
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Test student questions with OpenClaw & College RAG knowledge retrieval in real time.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-lg border text-xs text-gray-600">
            <ShieldCheck size={16} className="text-green-600" />
            <span>Strict Zero-Hallucination Guardrail Active</span>
          </div>
          <button
            onClick={loadInquiries}
            className="p-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm shadow-sm"
            title="Refresh Inquiries"
          >
            <RefreshCw size={16} className={logsLoading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Main Simulator & Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT: WhatsApp Mock Screen (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden h-[620px]">
          {/* WhatsApp Header */}
          <div className="bg-emerald-800 text-white px-4 py-3 flex items-center justify-between shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-emerald-600 border border-emerald-400 flex items-center justify-center text-lg">
                🎓
              </div>
              <div>
                <h3 className="font-semibold text-sm leading-tight">NMC College Assistant</h3>
                <p className="text-xs text-emerald-200 flex items-center gap-1.5 mt-0.5">
                  <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                  online • Powered by OpenClaw
                </p>
              </div>
            </div>

            <div className="text-right">
              <span className="text-[11px] bg-emerald-900/60 px-2 py-1 rounded text-emerald-200 border border-emerald-700">
                Test No: +{studentPhone}
              </span>
            </div>
          </div>

          {/* WhatsApp Message Body */}
          <div className="flex-1 p-4 overflow-y-auto bg-[#efeae2] space-y-3">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 shadow-sm text-sm relative ${
                    msg.sender === 'user'
                      ? 'bg-[#d9fdd3] text-gray-900 rounded-tr-none'
                      : 'bg-white text-gray-900 rounded-tl-none border border-gray-100'
                  }`}
                >
                  <p className="whitespace-pre-line leading-relaxed text-xs sm:text-sm">{msg.text}</p>

                  <div className="flex items-center justify-end gap-1.5 mt-1.5 pt-1 text-[10px] text-gray-400">
                    {msg.latency_ms && (
                      <span className="text-[10px] text-gray-400 font-mono">
                        {msg.latency_ms}ms
                      </span>
                    )}
                    <span>{msg.timestamp}</span>
                    {msg.sender === 'user' && (
                      <CheckCheck size={14} className="text-blue-500" />
                    )}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl px-4 py-2 text-xs text-gray-500 shadow-sm flex items-center gap-2">
                  <span className="animate-spin text-green-700">⚙️</span>
                  <span>AI Assistant is analyzing knowledge base...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Question Chips */}
          <div className="bg-gray-100 px-3 py-2 border-t border-gray-200 overflow-x-auto flex gap-2 whitespace-nowrap scrollbar-none">
            <span className="text-[11px] font-semibold text-gray-500 self-center uppercase pr-1">Try:</span>
            {SAMPLE_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                disabled={loading}
                className="px-2.5 py-1 bg-white border border-gray-300 rounded-full text-xs text-gray-700 hover:bg-green-50 hover:text-green-800 hover:border-green-300 transition-colors shadow-2xs"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-gray-50 border-t flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Ask any college question (e.g. Who is HOD of MCA?)..."
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              disabled={loading}
              className="flex-1 px-4 py-2.5 bg-white border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              type="submit"
              disabled={loading || !inputQuestion.trim()}
              className="p-2.5 bg-green-700 text-white rounded-xl hover:bg-green-800 disabled:opacity-50 transition-colors shadow-sm"
            >
              <Send size={18} />
            </button>
          </form>
        </div>

        {/* RIGHT: Retrieved Context & RAG Inspector (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col bg-white rounded-2xl border border-gray-200 shadow-sm p-5 h-[620px] overflow-hidden">
          <div className="flex items-center justify-between border-b pb-3">
            <h3 className="font-bold text-gray-900 text-sm flex items-center gap-2">
              <Database className="text-green-700" size={18} />
              RAG Knowledge Inspection
            </h3>
            {latestResult && (
              <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                latestResult.status === 'ANSWERED' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {latestResult.status}
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto mt-4 space-y-4 pr-1">
            {!latestResult ? (
              <div className="text-center py-16 text-gray-400 text-xs">
                <Sparkles className="mx-auto text-gray-300 mb-2" size={32} />
                Send a question in the chat to see real-time Knowledge Base sources retrieved by the RAG engine.
              </div>
            ) : (
              <>
                <div className="bg-gray-50 p-3 rounded-xl border border-gray-100 space-y-2">
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Detected Intent:</span>
                    <span className="font-semibold text-gray-900">{latestResult.intent || 'General'}</span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Response Latency:</span>
                    <span className="font-semibold text-gray-900">{latestResult.latency_ms} ms</span>
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                    Retrieved Sources ({latestResult.sources?.length || 0})
                  </h4>
                  <div className="space-y-2">
                    {latestResult.sources?.map((s, idx) => (
                      <div key={idx} className="p-3 bg-green-50/50 rounded-lg border border-green-200 text-xs">
                        <div className="flex items-center justify-between font-semibold text-green-900">
                          <span>{s.title}</span>
                          <span className="text-[10px] bg-green-200 text-green-900 px-1.5 py-0.5 rounded">
                            Score: {s.score}
                          </span>
                        </div>
                        <p className="text-[11px] text-green-700 mt-1">Category: {s.category}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                    Grounded Context Supplied to OpenClaw
                  </h4>
                  <pre className="p-3 bg-gray-900 text-green-400 text-[11px] rounded-lg overflow-x-auto whitespace-pre-wrap font-mono leading-relaxed max-h-48 border border-gray-800">
                    {latestResult.retrieved_context}
                  </pre>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Inquiry Logs Section */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <MessageSquare className="text-green-700" size={20} />
              Recent WhatsApp & Simulator Inquiries
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Live audit trail of student questions, AI responses, and fallback trigger rate.
            </p>
          </div>
          <button
            onClick={loadInquiries}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-gray-50 hover:bg-gray-100 rounded-lg border font-medium text-gray-600"
          >
            <RefreshCw size={14} className={logsLoading ? 'animate-spin' : ''} />
            Refresh Logs
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-600 border-b">
              <tr>
                <th className="px-4 py-3 font-semibold">Phone / Student</th>
                <th className="px-4 py-3 font-semibold">Student Question</th>
                <th className="px-4 py-3 font-semibold">AI Generated Answer</th>
                <th className="px-4 py-3 font-semibold">Category</th>
                <th className="px-4 py-3 font-semibold">Status</th>
                <th className="px-4 py-3 font-semibold">Latency</th>
                <th className="px-4 py-3 font-semibold">Date & Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-6 text-center text-gray-400">
                    No inquiries recorded yet. Test a question using the chat simulator above!
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono font-medium text-gray-900">
                      +{log.phone_number}
                      {log.contact_name && (
                        <p className="text-[11px] text-gray-500 font-sans">{log.contact_name}</p>
                      )}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900 max-w-xs truncate" title={log.question}>
                      {log.question}
                    </td>
                    <td className="px-4 py-3 text-gray-600 max-w-md truncate" title={log.answer}>
                      {log.answer}
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-medium">
                        {log.detected_intent || 'General'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full font-semibold ${
                        log.status === 'ANSWERED'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-gray-500">
                      {log.latency_ms}ms
                    </td>
                    <td className="px-4 py-3 text-gray-400 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
