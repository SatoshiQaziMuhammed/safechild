import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

// Simple API call without auth headers
const api = axios.create({ baseURL: '/api' });

const MagicUpload = () => {
  const { token } = useParams();
  const [requestInfo, setRequestInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const res = await api.get(`/requests/${token}`);
        setRequestInfo(res.data);
      } catch (err) {
        setError("This link is invalid or has expired.");
      } finally {
        setLoading(false);
      }
    };
    fetchInfo();
  }, [token]);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
      // Auto upload could happen here, but better let them confirm
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post(`/requests/${token}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (p) => {
          const percent = Math.round((p.loaded * 100) / p.total);
          setProgress(percent);
        }
      });
      setUploadStatus('success');
      setFile(null); // Reset for next file
    } catch (err) {
      console.error(err);
      setUploadStatus('error');
    }
  };

  if (loading) return <div className="flex h-screen items-center justify-center text-xl">Loading secure link...</div>;
  if (error) return <div className="flex h-screen items-center justify-center text-red-600 font-bold text-xl">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg max-w-lg w-full text-center">
        {/* Logo Placeholder */}
        <div className="mb-6 flex justify-center">
             <div className="bg-blue-900 text-white font-bold p-3 rounded text-xl">SAFECHILD</div>
        </div>

        <h1 className="text-2xl font-bold text-gray-800 mb-2">Hello, {requestInfo.clientName}</h1>
        <p className="text-gray-600 mb-8">
          Your lawyer has requested the following files. Please tap the button below to upload directly from your device.
        </p>

        {uploadStatus === 'success' ? (
          <div className="bg-green-50 border border-green-200 p-6 rounded-lg mb-6">
            <div className="text-green-600 text-5xl mb-4">✓</div>
            <h3 className="text-xl font-bold text-green-800 mb-2">Upload Successful!</h3>
            <p className="text-green-700 mb-4">Your file has been securely sent to your lawyer.</p>
            <button 
              onClick={() => { setUploadStatus('idle'); setProgress(0); }}
              className="bg-green-600 text-white py-2 px-6 rounded-full font-bold hover:bg-green-700 transition"
            >
              Upload Another File
            </button>
          </div>
        ) : (
          <>
            <div className="space-y-4 mb-8">
              {/* Giant Upload Button */}
              <label className={`block w-full border-4 border-dashed rounded-xl p-8 cursor-pointer transition
                  ${file ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}
              `}>
                 <input type="file" onChange={handleFileChange} className="hidden" />
                 
                 {!file ? (
                   <>
                     <div className="text-6xl mb-4 text-blue-500">📷</div>
                     <span className="text-xl font-bold text-gray-700 block">Tap here to Select File</span>
                     <span className="text-sm text-gray-500 block mt-2">Photos, Videos, or Documents</span>
                   </>
                 ) : (
                   <>
                     <div className="text-4xl mb-2 text-blue-600">📄</div>
                     <span className="font-bold text-gray-800 block break-all">{file.name}</span>
                     <span className="text-sm text-gray-500 block">{(file.size/1024/1024).toFixed(2)} MB</span>
                   </>
                 )}
              </label>
            </div>

            {file && uploadStatus !== 'uploading' && (
              <button 
                onClick={handleUpload}
                className="w-full bg-blue-600 text-white text-xl font-bold py-4 rounded-lg shadow-lg hover:bg-blue-700 transition transform hover:scale-105"
              >
                SEND FILE NOW ➤
              </button>
            )}

            {uploadStatus === 'uploading' && (
              <div className="w-full">
                <div className="flex justify-between text-sm font-medium text-gray-700 mb-1">
                  <span>Uploading securely...</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div className="bg-blue-600 h-4 rounded-full transition-all" style={{width: `${progress}%`}}></div>
                </div>
              </div>
            )}
            
            {uploadStatus === 'error' && (
               <div className="text-red-600 mt-4 font-bold">Upload failed. Please try again.</div>
            )}
          </>
        )}

        <div className="mt-8 text-xs text-gray-400">
          SECURE ENCRYPTED CONNECTION • SAFECHILD LEGAL
        </div>
      </div>
    </div>
  );
};

export default MagicUpload;
