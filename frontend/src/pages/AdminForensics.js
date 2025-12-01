import React, { useEffect, useState } from 'react';
import { adminService, forensicService } from '../lib/api';
import Header from '../components/Header';
import Footer from '../components/Footer';

const AdminForensics = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Magic Link Creator State
  const [showMagicModal, setShowMagicModal] = useState(false);
  const [targetClient, setTargetClient] = useState('');
  const [generatedLink, setGeneratedLink] = useState(null);
  const [requestTypes, setRequestTypes] = useState({
    photos: true,
    documents: true,
    whatsapp: true,
    telegram: true
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await adminService.getAllCases();
      setCases(res.cases || []);
    } catch (err) {
      console.error("Failed to load forensics cases", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateLink = async () => {
    if (!targetClient) {
      alert("Please enter a Client Number.");
      return;
    }

    const types = Object.keys(requestTypes).filter(k => requestTypes[k]);
    try {
      const res = await adminService.createMagicLink(targetClient, types);
      // In production, this domain should be dynamic
      const fullLink = `${window.location.origin}/upload-request/${res.token}`;
      setGeneratedLink(fullLink);
    } catch (err) {
      console.error("Failed to create link", err);
      alert("Error creating link.");
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedLink);
    alert("Link copied to clipboard!");
  };

  const downloadReport = async (caseId, format) => {
    try {
      const response = await forensicService.downloadReport(caseId, format);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SafeChild_Report_${caseId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download failed", err);
      alert("Failed to download report.");
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Forensic Evidence Manager</h1>
            <p className="text-gray-600">Manage digital evidence, requests, and reports</p>
          </div>
          <button 
            onClick={() => { setShowMagicModal(true); setGeneratedLink(null); }}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg shadow-md flex items-center gap-2"
          >
            <span>✨</span> Create Request Link
          </button>
        </div>

        {/* Case List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h2 className="font-bold text-gray-700">All Cases ({cases.length})</h2>
            <button onClick={loadData} className="text-blue-600 text-sm hover:underline">Refresh</button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-100 text-gray-600 text-xs uppercase">
                <tr>
                  <th className="px-6 py-3">Case ID</th>
                  <th className="px-6 py-3">Client</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {cases.map((c) => (
                  <tr key={c.case_id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 font-mono text-sm text-blue-900">{c.case_id}</td>
                    <td className="px-6 py-4 text-gray-800 font-medium">{c.client_number}</td>
                    <td className="px-6 py-4 text-gray-500 text-sm">{c.analysis_type || 'Unknown'}</td>
                    <td className="px-6 py-4">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="px-6 py-4 text-gray-500 text-sm">
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      {c.status === 'completed' ? (
                        <>
                          <button onClick={() => downloadReport(c.case_id, 'pdf')} className="text-red-600 hover:text-red-800 text-sm font-medium">PDF</button>
                          <span className="text-gray-300">|</span>
                          <button onClick={() => downloadReport(c.case_id, 'txt')} className="text-gray-600 hover:text-gray-800 text-sm font-medium">Log</button>
                        </>
                      ) : (
                        <span className="text-gray-400 text-sm italic">Processing...</span>
                      )}
                    </td>
                  </tr>
                ))}
                {cases.length === 0 && !loading && (
                  <tr>
                    <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                      No forensic cases found. Create a request to get started.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Magic Link Modal */}
        {showMagicModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 animate-fade-in-up">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-gray-800">Create Evidence Request</h3>
                <button onClick={() => setShowMagicModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
              </div>

              {!generatedLink ? (
                <>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Client Number / ID</label>
                    <input 
                      type="text" 
                      value={targetClient}
                      onChange={(e) => setTargetClient(e.target.value)}
                      placeholder="e.g. SC2025..."
                      className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>

                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Requested Evidence Types</label>
                    <div className="space-y-2">
                      {Object.keys(requestTypes).map(type => (
                        <label key={type} className="flex items-center space-x-2 cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={requestTypes[type]} 
                            onChange={(e) => setRequestTypes({...requestTypes, [type]: e.target.checked})}
                            className="rounded text-blue-600 focus:ring-blue-500" 
                          />
                          <span className="capitalize text-gray-700">{type}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <button 
                    onClick={handleCreateLink}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition"
                  >
                    Generate Magic Link
                  </button>
                </>
              ) : (
                <div className="text-center">
                  <div className="bg-green-50 text-green-800 p-4 rounded-lg mb-4">
                    <p className="font-bold mb-1">Link Generated Successfully!</p>
                    <p className="text-xs">Send this link to your client via WhatsApp or Email.</p>
                  </div>
                  
                  <div className="bg-gray-100 p-3 rounded border border-gray-300 break-all text-sm font-mono mb-4 text-gray-600 select-all">
                    {generatedLink}
                  </div>

                  <button 
                    onClick={copyToClipboard}
                    className="w-full bg-gray-800 hover:bg-gray-900 text-white font-bold py-3 rounded-lg mb-2 transition"
                  >
                    Copy Link
                  </button>
                  <button 
                    onClick={() => { setGeneratedLink(null); setShowMagicModal(false); }}
                    className="w-full text-gray-500 hover:text-gray-700 py-2 text-sm"
                  >
                    Close
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

      </main>
      <Footer />
    </div>
  );
};

const StatusBadge = ({ status }) => {
  const styles = {
    completed: 'bg-green-100 text-green-800',
    processing: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800',
    pending: 'bg-gray-100 text-gray-600'
  };
  
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status] || styles.pending}`}>
      {status.toUpperCase()}
    </span>
  );
};

export default AdminForensics;
