import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import { Button } from "../components/ui/button";

const MockCheckoutSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Simulate verifying the session
    console.log("Mock Payment Success for Session:", sessionId);
    
    // Auto-redirect after 5 seconds
    const timer = setTimeout(() => {
      navigate('/portal');
    }, 5000);

    return () => clearTimeout(timer);
  }, [sessionId, navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
        <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-green-100 mb-6">
          <CheckCircle className="h-10 w-10 text-green-600" />
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Ödeme Başarılı!
        </h1>
        <p className="text-gray-500 mb-6">
          (Vakıf Desteği ile Ücretsiz İşlem)
        </p>
        
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6 text-sm text-blue-700">
          <p>İşleminiz başarıyla onaylandı.</p>
          <p className="mt-1 font-mono text-xs text-blue-500">Session ID: {sessionId}</p>
        </div>

        <p className="text-gray-600 mb-8">
          5 saniye içinde portale yönlendiriliyorsunuz...
        </p>

        <Button 
          onClick={() => navigate('/portal')}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white"
        >
          Hemen Portale Git
        </Button>
      </div>
    </div>
  );
};

export default MockCheckoutSuccess;
