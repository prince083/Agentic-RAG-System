import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Upload, Send, FileText, Loader2, Bot, User } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string, sources?: string[] }[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    const file = e.target.files[0];

    // 10MB Limit Check
    if (file.size > 10 * 1024 * 1024) {
      alert("File is too large! Please upload a PDF smaller than 10MB.");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_URL}/api/v1/ingest`, formData);
      const fileName = file.name || "Document";
      setMessages(prev => [...prev, { role: 'assistant', content: `✅ Successfully uploaded **${fileName}**! I have processed it.` }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: "❌ Error uploading file. Check console for details." }]);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    const userMsg = query;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setQuery('');
    setLoading(true);

    try {
      const res = await axios.post(`${API_URL}/api/v1/chat`, { message: userMsg });
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources
      }]);
    } catch (err: any) {
      console.error("Chat Error:", err);
      const errorMessage = err.response?.data?.detail || "Error: Could not get response.";
      setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ ${errorMessage}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans flex flex-col items-center p-6">
      <div className="w-full max-w-4xl flex flex-col h-[90vh]">

        {/* Header */}
        <div className="flex justify-center items-center mb-6 p-4 bg-gray-800 rounded-xl shadow-lg border border-gray-700">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Agentic RAG System
          </h1>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto bg-gray-800/50 rounded-xl border border-gray-700 p-6 mb-4 backdrop-blur-sm space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <Bot className="w-16 h-16 mb-6 text-blue-500 opacity-80" />
              <p className="text-lg mb-6 font-medium">Upload a document and start asking questions!</p>

              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".pdf"
                onChange={handleFileUpload}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl transition-all shadow-lg hover:shadow-blue-500/25 text-white font-semibold transform hover:scale-105"
              >
                {uploading ? <Loader2 className="animate-spin w-5 h-5" /> : <Upload className="w-5 h-5" />}
                Upload Document
              </button>
              <p className="mt-4 text-sm text-gray-500">
                Please ensure the file is a PDF and maintains a reasonable size (Max 10MB).
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 
                ${msg.role === 'user' ? 'bg-purple-600' : 'bg-blue-600'}`}>
                {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              <div className={`max-w-[80%] rounded-2xl p-4 shadow-lg 
                ${msg.role === 'user'
                  ? 'bg-purple-600/20 border border-purple-500/30 text-purple-100 rounded-tr-sm'
                  : 'bg-gray-700/50 border border-gray-600 text-gray-200 rounded-tl-sm'}`}>
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-gray-600/50">
                    <p className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-1">
                      <FileText className="w-3 h-3" /> Sources:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((source, idx) => (
                        <span key={idx} className="text-xs bg-gray-800 px-2 py-1 rounded border border-gray-600 text-gray-300">
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-gray-700/50 rounded-2xl p-4 border border-gray-600 flex items-center gap-2">
                <Loader2 className="animate-spin w-4 h-4 text-blue-400" />
                <span className="text-gray-400 text-sm">Thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Ask about your documents..."
            className="w-full bg-gray-800 border-2 border-gray-700 rounded-xl py-4 pl-6 pr-14 
                     text-gray-100 placeholder-gray-500 focus:border-blue-500 focus:outline-none 
                     transition-all shadow-lg"
          />
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="absolute right-2 top-2 p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 
                     disabled:cursor-not-allowed rounded-lg transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
