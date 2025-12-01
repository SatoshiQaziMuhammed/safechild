import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { forensicService, paymentService } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';

const ForensicAnalysis = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, completed, failed
  const [currentCase, setCurrentCase] = useState(null);
  const [error, setError] = useState(null);
  const [paymentProcessing, setPaymentProcessing] = useState(false);

  useEffect(() => {
    // Poll for status if processing
    let interval;
    if (status === 'processing' && currentCase) {
      interval = setInterval(async () => {
        try {
          const caseStatus = await forensicService.getCaseStatus(currentCase.case_id);
          if (caseStatus.status === 'completed') {
            setStatus('completed');
            clearInterval(interval);
          } else if (caseStatus.status === 'failed') {
            setStatus('failed');
            setError(caseStatus.error || 'Analysis failed');
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Status check failed", err);
        }
      }, 5000); // Check every 5 seconds
    }
    return () => clearInterval(interval);
  }, [status, currentCase]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setStatus('uploading');
    setUploadProgress(0);

    try {
      const result = await forensicService.uploadEvidence(file, (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percentCompleted);
      });

      setCurrentCase(result);
      setStatus('processing');
    } catch (err) {
      console.error("Upload error", err);
      setStatus('failed');
      setError(err.response?.data?.detail || "Upload failed. Please try again.");
    }
  };

  const handlePayment = async () => {
    if (!currentCase) return;

    setPaymentProcessing(true);
    try {
      // Mock Payment
      await paymentService.processPayment(currentCase.case_id, {
        method: 'credit_card_mock',
        token: 'tok_visa_mock'
      });
      
      // Update local state to reflect payment (in a real app, backend would update case status)
      // Here we assume successful payment unlocks the report immediately
      alert("Payment successful! Report is now available.");
      setPaymentProcessing(false);
      
      // Force refresh status (or just navigate to a "Case Details" page)
    } catch (err) {
      console.error("Payment failed", err);
      alert("Payment failed. Please try again.");
      setPaymentProcessing(false);
    }
  };

  const downloadReport = async (format) => {
    if (!currentCase) return;
    try {
      const response = await forensicService.downloadReport(currentCase.case_id, format);
      
      // Create a link and click it to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SafeChild_Report_${currentCase.case_id}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download failed", err);
      setError("Failed to download report.");
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">Forensic Analysis Upload</h1>
          
          {/* Upload Section */}
          {status === 'idle' && (
            <div className="mb-8">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <input 
                  type="file" 
                  onChange={handleFileChange} 
                  className="hidden" 
                  id="file-upload"
                  accept=".db,.tar,.gz,.zip,.ab,.jpg,.jpeg,.png,.pdf,.doc,.docx,.txt"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-gray-500 mb-2">
                    <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <p className="text-sm">Click to select file or drag and drop</p>
                    <p className="text-xs text-gray-400 mt-1">
                      Supported: Forensic Backups (.db, .tar, .ab) AND Documents/Media (.pdf, .jpg, .png, .docx)
                    </p>
                  </div>
                </label>
                {file && (
                  <div className="mt-4 p-2 bg-blue-50 text-blue-700 rounded">
                    Selected: {file.name} ({(file.size / (1024*1024)).toFixed(2)} MB)
                  </div>
                )}
              </div>
              
              <button
                onClick={handleUpload}
                disabled={!file}
                className={`mt-4 w-full py-2 px-4 rounded font-medium text-white 
                  ${!file ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
              >
                Secure Upload & Analyze
              </button>
            </div>
          )}

          {/* Progress Section */}
          {status === 'uploading' && (
            <div className="mb-8">
              <h3 className="text-lg font-medium text-gray-700 mb-2">Uploading Securely...</h3>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div 
                  className="bg-blue-600 h-4 rounded-full transition-all duration-300" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-right text-sm text-gray-500 mt-1">{uploadProgress}%</p>
            </div>
          )}

          {/* Processing Section */}
          {status === 'processing' && (
            <div className="mb-8 text-center py-10">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <h3 className="text-xl font-medium text-gray-800">Analyzing Evidence...</h3>
              <p className="text-gray-500 mt-2">This may take several minutes. You will be notified when complete.</p>
              <p className="text-sm text-gray-400 mt-4">Case ID: {currentCase?.case_id}</p>
            </div>
          )}

          {/* Completed / Payment Section */}
          {status === 'completed' && (
            <div className="mb-8">
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-bold text-green-800 mb-2">Analysis Complete!</h3>
                <p className="text-green-700">
                  Your forensic report is ready. The file integrity has been verified (SHA-256).
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-6">
                <h4 className="font-bold text-gray-800 mb-4">Unlock Full Report</h4>
                <div className="flex justify-between items-center mb-4">
                  <span className="text-gray-600">Forensic Analysis Fee</span>
                  <span className="text-xl font-bold text-gray-900">€99.00</span>
                </div>
                
                <button
                  onClick={handlePayment}
                  disabled={paymentProcessing}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded flex justify-center items-center"
                >
                  {paymentProcessing ? (
                    <span className="animate-pulse">Processing Payment...</span>
                  ) : (
                    <>
                      <span>Pay Securely (Mock)</span>
                      <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </>
                  )}
                </button>
              </div>

              {/* Download Links (Visible after payment logic - simplified here to always show for demo) */}
              <div className="mt-8">
                 <h4 className="font-bold text-gray-800 mb-2">Downloads (Demo Mode: Always Open)</h4>
                 <div className="flex gap-4">
                    <button 
                      onClick={() => downloadReport('pdf')}
                      className="flex-1 bg-gray-800 text-white py-2 rounded hover:bg-gray-700"
                    >
                      Download PDF Report
                    </button>
                    <button 
                      onClick={() => downloadReport('txt')}
                      className="flex-1 bg-white border border-gray-300 text-gray-700 py-2 rounded hover:bg-gray-50"
                    >
                      Download Text Log
                    </button>
                 </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mt-4">
              <strong className="font-bold">Error: </strong>
              <span className="block sm:inline">{error}</span>
            </div>
          )}

        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default ForensicAnalysis;
