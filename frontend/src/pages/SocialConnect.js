import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';

const SocialConnect = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('whatsapp'); // 'whatsapp' or 'telegram'
  const [sessionId, setSessionId] = useState(null);
  const [qrCode, setQrCode] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, initializing, qr_ready, connected, extracting, completed, failed
  const [error, setError] = useState(null);

  // Poll for status updates
  useEffect(() => {
    let interval;
    if (sessionId && status !== 'completed' && status !== 'failed') {
      interval = setInterval(async () => {
        try {
          const apiPrefix = activeTab === 'whatsapp' ? '/api/whatsapp' : '/api/telegram';
          const res = await axios.get(`${apiPrefix}/session/${sessionId}/status`);
          
          if (res.data.status !== status) {
            setStatus(res.data.status);
          }
          if (res.data.qr) {
            setQrCode(res.data.qr);
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [sessionId, status, activeTab]);

  const startSession = async () => {
    setStatus('initializing');
    setError(null);
    setQrCode(null);
    try {
      const apiPrefix = activeTab === 'whatsapp' ? '/api/whatsapp' : '/api/telegram';
      const res = await axios.post(`${apiPrefix}/session/start`, {
        clientNumber: user?.clientNumber || 'guest'
      });
      setSessionId(res.data.sessionId);
    } catch (err) {
      console.error("Start session error", err);
      setError(`Failed to start ${activeTab === 'whatsapp' ? 'WhatsApp' : 'Telegram'} service. Please try again.`);
      setStatus('idle');
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSessionId(null);
    setQrCode(null);
    setStatus('idle');
    setError(null);
  };

  const isWhatsApp = activeTab === 'whatsapp';
  const themeColor = isWhatsApp ? 'green' : 'blue';
  const title = isWhatsApp ? 'WhatsApp Auto-Extract' : 'Telegram Auto-Extract';
  const icon = isWhatsApp ? '📱' : '✈️';

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8 text-center">
          
          {/* Tabs */}
          <div className="flex justify-center mb-8 bg-gray-100 p-1 rounded-full inline-flex">
            <button
              onClick={() => handleTabChange('whatsapp')}
              className={`px-6 py-2 rounded-full font-medium transition-all ${
                activeTab === 'whatsapp' 
                  ? 'bg-white text-green-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              WhatsApp
            </button>
            <button
              onClick={() => handleTabChange('telegram')}
              className={`px-6 py-2 rounded-full font-medium transition-all ${
                activeTab === 'telegram' 
                  ? 'bg-white text-blue-500 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Telegram
            </button>
          </div>

          <h1 className={`text-3xl font-bold text-${themeColor}-600 mb-4 flex justify-center items-center gap-2`}>
            <span className="text-4xl">{icon}</span> {title}
          </h1>
          
          <p className="text-gray-600 mb-8">
            Connect your {isWhatsApp ? 'WhatsApp' : 'Telegram'} to securely extract and analyze chat history automatically.
            No file uploads required.
          </p>

          {status === 'idle' && (
            <button 
              onClick={startSession}
              className={`bg-${themeColor}-600 text-white text-xl font-bold py-4 px-10 rounded-full shadow-lg hover:bg-${themeColor}-700 transition transform hover:scale-105`}
            >
              Start Secure Connection
            </button>
          )}

          {status === 'initializing' && (
            <div className="flex flex-col items-center">
              <div className={`animate-spin rounded-full h-12 w-12 border-b-2 border-${themeColor}-600 mb-4`}></div>
              <p className="text-gray-500">Preparing secure environment...</p>
            </div>
          )}

          {status === 'qr_ready' && qrCode && (
            <div className="flex flex-col items-center animate-fade-in">
              <div className="bg-white p-4 rounded-lg shadow border border-gray-200 mb-4">
                <img src={qrCode} alt="QR Code" className="w-64 h-64" />
              </div>
              <div className={`text-left bg-${themeColor}-50 p-4 rounded text-sm text-gray-700 max-w-sm`}>
                <p className="font-bold mb-2">Instructions:</p>
                <ol className="list-decimal pl-4 space-y-1">
                  <li>Open {isWhatsApp ? 'WhatsApp' : 'Telegram'} on your phone</li>
                  <li>Go to <b>Settings</b> > <b>{isWhatsApp ? 'Linked Devices' : 'Devices'}</b></li>
                  <li>Tap <b>Link a Device</b> (or similar)</li>
                  <li>Scan this QR Code</li>
                </ol>
              </div>
            </div>
          )}

          {status === 'connected' && (
            <div className={`flex flex-col items-center text-${themeColor}-700`}>
              <div className="text-6xl mb-4">🔓</div>
              <h3 className="text-2xl font-bold mb-2">Device Connected!</h3>
              <p>Establishing secure channel...</p>
            </div>
          )}

          {status === 'extracting' && (
            <div className="flex flex-col items-center">
              <div className="w-full max-w-md bg-gray-200 rounded-full h-4 mb-4 overflow-hidden">
                <div className={`bg-${themeColor}-500 h-4 rounded-full animate-pulse w-full`}></div>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">Extracting Data...</h3>
              <p className="text-gray-500 text-sm">Do not close this window. This may take a few minutes.</p>
            </div>
          )}

          {status === 'completed' && (
            <div className="flex flex-col items-center">
              <div className="text-6xl mb-4">✅</div>
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Extraction Complete!</h3>
              <p className="text-gray-600 mb-6">Your data has been securely processed and added to your case file.</p>
              
              <a href="/portal" className="text-blue-600 font-bold hover:underline">
                Return to Dashboard to view report
              </a>
            </div>
          )}

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded mt-4 border border-red-200">
              {error}
            </div>
          )}
          
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default SocialConnect;
