import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ArrowLeft, Video, VideoOff, Mic, MicOff } from 'lucide-react';

const VideoCall = () => {
  const { language } = useLanguage();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const jitsiContainerRef = useRef(null);
  const [jitsiApi, setJitsiApi] = useState(null);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  
  const roomName = searchParams.get('room') || `safechild-${user?.clientNumber || 'guest'}`;

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    // Load Jitsi Meet External API
    const loadJitsiScript = () => {
      const script = document.createElement('script');
      script.src = 'https://meet.jit.si/external_api.js';
      script.async = true;
      script.onload = () => initializeJitsi();
      document.body.appendChild(script);
    };

    const initializeJitsi = () => {
      if (window.JitsiMeetExternalAPI && jitsiContainerRef.current) {
        const domain = 'meet.jit.si';
        const options = {
          roomName: roomName,
          width: '100%',
          height: '100%',
          parentNode: jitsiContainerRef.current,
          userInfo: {
            displayName: `${user.firstName} ${user.lastName}`,
            email: user.email
          },
          configOverwrite: {
            startWithAudioMuted: false,
            startWithVideoMuted: false,
            enableWelcomePage: false,
            prejoinPageEnabled: false,
          },
          interfaceConfigOverwrite: {
            TOOLBAR_BUTTONS: [
              'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
              'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
              'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
              'videoquality', 'filmstrip', 'feedback', 'stats', 'shortcuts',
              'tileview', 'download', 'help', 'mute-everyone'
            ],
            SHOW_JITSI_WATERMARK: false,
            SHOW_WATERMARK_FOR_GUESTS: false,
          }
        };

        const api = new window.JitsiMeetExternalAPI(domain, options);
        setJitsiApi(api);

        // Event listeners
        api.addEventListener('videoConferenceJoined', () => {
          console.log('Video conference joined');
        });

        api.addEventListener('videoConferenceLeft', () => {
          console.log('Video conference left');
          navigate('/portal');
        });
      }
    };

    // Check if script already loaded
    if (window.JitsiMeetExternalAPI) {
      initializeJitsi();
    } else {
      loadJitsiScript();
    }

    return () => {
      if (jitsiApi) {
        jitsiApi.dispose();
      }
    };
  }, [user, roomName, navigate]);

  const toggleVideo = () => {
    if (jitsiApi) {
      jitsiApi.executeCommand('toggleVideo');
      setVideoEnabled(!videoEnabled);
    }
  };

  const toggleAudio = () => {
    if (jitsiApi) {
      jitsiApi.executeCommand('toggleAudio');
      setAudioEnabled(!audioEnabled);
    }
  };

  const endCall = () => {
    if (jitsiApi) {
      jitsiApi.executeCommand('hangup');
    }
    navigate('/portal');
  };

  return (
    <div className="fixed inset-0 bg-gray-900">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-50 bg-black/50 backdrop-blur-sm">\n        <div className=\"container mx-auto px-4 py-3\">\n          <div className=\"flex items-center justify-between\">\n            <div className=\"flex items-center space-x-4\">\n              <Button\n                variant=\"ghost\"\n                onClick={endCall}\n                className=\"text-white hover:bg-white/10\"\n              >\n                <ArrowLeft className=\"w-4 h-4 mr-2\" />\n                {language === 'de' ? 'Beenden' : 'End Call'}\n              </Button>\n              <div className=\"text-white\">\n                <p className=\"text-sm opacity-75\">\n                  {language === 'de' ? 'Video-Konsultation' : 'Video Consultation'}\n                </p>\n                <p className=\"text-xs opacity-60\">Room: {roomName}</p>\n              </div>\n            </div>\n\n            <div className=\"flex items-center space-x-2\">\n              <Button\n                variant=\"ghost\"\n                size=\"icon\"\n                onClick={toggleVideo}\n                className={`text-white hover:bg-white/10 ${\n                  !videoEnabled ? 'bg-red-500 hover:bg-red-600' : ''\n                }`}\n              >\n                {videoEnabled ? (\n                  <Video className=\"w-5 h-5\" />\n                ) : (\n                  <VideoOff className=\"w-5 h-5\" />\n                )}\n              </Button>\n              <Button\n                variant=\"ghost\"\n                size=\"icon\"\n                onClick={toggleAudio}\n                className={`text-white hover:bg-white/10 ${\n                  !audioEnabled ? 'bg-red-500 hover:bg-red-600' : ''\n                }`}\n              >\n                {audioEnabled ? (\n                  <Mic className=\"w-5 h-5\" />\n                ) : (\n                  <MicOff className=\"w-5 h-5\" />\n                )}\n              </Button>\n            </div>\n          </div>\n        </div>\n      </div>\n\n      {/* Jitsi Container */}\n      <div ref={jitsiContainerRef} className=\"w-full h-full\" />\n    </div>\n  );\n};\n\nexport default VideoCall;\n"}, {"path": "/app/frontend/src/pages/BookConsultation.jsx", "content": "import React, { useState } from 'react';\nimport { useNavigate } from 'react-router-dom';\nimport { useAuth } from '../contexts/AuthContext';\nimport { useLanguage } from '../contexts/LanguageContext';\nimport { Button } from '../components/ui/button';\nimport { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';\nimport { toast } from 'sonner';\nimport { Video, CreditCard, Calendar, Clock, CheckCircle } from 'lucide-react';\nimport axios from 'axios';\n\nconst BACKEND_URL = process.env.REACT_APP_BACKEND_URL;\nconst API = `${BACKEND_URL}/api`;\n\nconst BookConsultation = () => {\n  const { language } = useLanguage();\n  const { user, token } = useAuth();\n  const navigate = useNavigate();\n  const [loading, setLoading] = useState(false);\n\n  const handleBookConsultation = async () => {\n    if (!user) {\n      navigate('/login');\n      return;\n    }\n\n    setLoading(true);\n    try {\n      const response = await axios.post(\n        `${API}/payment/create-checkout`,\n        {},\n        { headers: { Authorization: `Bearer ${token}` } }\n      );\n\n      if (response.data.success && response.data.url) {\n        // Redirect to Stripe Checkout\n        window.location.href = response.data.url;\n      }\n    } catch (error) {\n      toast.error(\n        language === 'de' ? 'Fehler beim Erstellen der Buchung' : 'Failed to create booking',\n        { description: error.response?.data?.detail || error.message }\n      );\n    } finally {\n      setLoading(false);\n    }\n  };\n\n  const handleStartFreeCall = () => {\n    if (!user) {\n      navigate('/login');\n      return;\n    }\n    navigate(`/video-call?room=safechild-${user.clientNumber}`);\n  };\n\n  return (\n    <div className=\"min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 py-12\">\n      <div className=\"container mx-auto px-4\">\n        <div className=\"text-center mb-12\">\n          <h1 className=\"text-4xl font-bold text-gray-900 mb-4\">\n            {language === 'de' ? 'Beratung buchen' : 'Book Consultation'}\n          </h1>\n          <p className=\"text-xl text-gray-600\">\n            {language === 'de' \n              ? 'Wählen Sie Ihre bevorzugte Konsultationsoption' \n              : 'Choose your preferred consultation option'}\n          </p>\n        </div>\n\n        <div className=\"grid md:grid-cols-2 gap-8 max-w-5xl mx-auto\">\n          {/* Free Video Call */}\n          <Card className=\"border-2 hover:border-green-500 hover:shadow-xl transition-all\">\n            <CardHeader className=\"text-center\">\n              <div className=\"w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4\">\n                <Video className=\"w-10 h-10 text-green-600\" />\n              </div>\n              <CardTitle className=\"text-2xl\">\n                {language === 'de' ? 'Kostenloser Video-Anruf' : 'Free Video Call'}\n              </CardTitle>\n              <CardDescription className=\"text-lg\">\n                {language === 'de' ? 'Schnelle Erstberatung' : 'Quick Initial Consultation'}\n              </CardDescription>\n            </CardHeader>\n            <CardContent>\n              <div className=\"space-y-4 mb-6\">\n                <div className=\"flex items-center space-x-3\">\n                  <CheckCircle className=\"w-5 h-5 text-green-600\" />\n                  <span>{language === 'de' ? '15 Minuten Beratung' : '15 minutes consultation'}</span>\n                </div>\n                <div className=\"flex items-center space-x-3\">\n                  <CheckCircle className=\"w-5 h-5 text-green-600\" />\n                  <span>{language === 'de' ? 'Sofort verfügbar' : 'Available immediately'}</span>\n                </div>\n                <div className=\"flex items-center space-x-3\">\n                  <CheckCircle className=\"w-5 h-5 text-green-600\" />\n                  <span>{language === 'de' ? 'Keine Zahlung erforderlich' : 'No payment required'}</span>\n                </div>\n              </div>\n              <div className=\"text-center mb-4\">\n                <div className=\"text-4xl font-bold text-green-600\">€0</div>\n                <p className=\"text-sm text-gray-600\">{language === 'de' ? 'Kostenlos' : 'Free'}</p>\n              </div>\n              <Button\n                onClick={handleStartFreeCall}\n                className=\"w-full bg-green-600 hover:bg-green-700 text-lg py-6\"\n              >\n                <Video className=\"w-5 h-5 mr-2\" />\n                {language === 'de' ? 'Jetzt starten' : 'Start Now'}\n              </Button>\n            </CardContent>\n          </Card>\n\n          {/* Paid Consultation */}\n          <Card className=\"border-2 border-blue-500 hover:shadow-xl transition-all relative\">\n            <div className=\"absolute top-0 right-0 bg-blue-600 text-white px-4 py-1 rounded-bl-lg text-sm font-medium\">\n              {language === 'de' ? 'Empfohlen' : 'Recommended'}\n            </div>\n            <CardHeader className=\"text-center\">\n              <div className=\"w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4\">\n                <Calendar className=\"w-10 h-10 text-blue-600\" />\n              </div>\n              <CardTitle className=\"text-2xl\">\n                {language === 'de' ? 'Ausführliche Beratung' : 'Comprehensive Consultation'}\n              </CardTitle>\n              <CardDescription className=\"text-lg\">\n                {language === 'de' ? 'Detaillierte rechtliche Analyse' : 'Detailed legal analysis'}\n              </CardDescription>\n            </CardHeader>\n            <CardContent>\n              <div className=\"space-y-4 mb-6\">\n                <div className=\"flex items-center space-x-3\">\n                  <CheckCircle className=\"w-5 h-5 text-blue-600\" />\n                  <span>{language === 'de' ? '60 Minuten Beratung' : '60 minutes consultation'}</span>\n                </div>\n                <div className=\"flex items-center space-x-3\">\n                  <CheckCircle className=\"w-5 h-5 text-blue-600\" />\n                  <span>{language === 'de' ? 'Fallanalyse & Strategie' : 'Case analysis & strategy'}</span>\n                </div>\n                <div className=\"flex items-center space-x-3\">\n                  <CheckCircle className=\"w-5 h-5 text-blue-600\" />\n                  <span>{language === 'de' ? 'Schriftlicher Bericht' : 'Written report'}</span>\n                </div>\n                <div className=\"flex items-center space-x-3\">\n                  <CheckCircle className=\"w-5 h-5 text-blue-600\" />\n                  <span>{language === 'de' ? 'Follow-up Support' : 'Follow-up support'}</span>\n                </div>\n              </div>\n              <div className=\"text-center mb-4\">\n                <div className=\"text-4xl font-bold text-blue-600\">€150</div>\n                <p className=\"text-sm text-gray-600\">{language === 'de' ? 'Einmalige Zahlung' : 'One-time payment'}</p>\n              </div>\n              <Button\n                onClick={handleBookConsultation}\n                disabled={loading}\n                className=\"w-full bg-blue-600 hover:bg-blue-700 text-lg py-6\"\n              >\n                <CreditCard className=\"w-5 h-5 mr-2\" />\n                {loading \n                  ? (language === 'de' ? 'Lädt...' : 'Loading...') \n                  : (language === 'de' ? 'Jetzt buchen' : 'Book Now')}\n              </Button>\n            </CardContent>\n          </Card>\n        </div>\n\n        {/* Info Section */}\n        <Card className=\"mt-12 max-w-3xl mx-auto border-2\">\n          <CardContent className=\"p-8\">\n            <h3 className=\"text-xl font-bold mb-4\">\n              {language === 'de' ? 'Wie funktioniert es?' : 'How does it work?'}\n            </h3>\n            <div className=\"space-y-4\">\n              <div className=\"flex items-start space-x-3\">\n                <div className=\"w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0\">\n                  <span className=\"font-bold text-blue-600\">1</span>\n                </div>\n                <div>\n                  <p className=\"font-medium\">\n                    {language === 'de' ? 'Option wählen' : 'Choose option'}\n                  </p>\n                  <p className=\"text-sm text-gray-600\">\n                    {language === 'de' \n                      ? 'Wählen Sie zwischen kostenlosem Anruf oder ausführlicher Beratung'\n                      : 'Choose between free call or comprehensive consultation'}\n                  </p>\n                </div>\n              </div>\n              <div className=\"flex items-start space-x-3\">\n                <div className=\"w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0\">\n                  <span className=\"font-bold text-blue-600\">2</span>\n                </div>\n                <div>\n                  <p className=\"font-medium\">\n                    {language === 'de' ? 'Zahlung (falls zutreffend)' : 'Payment (if applicable)'}\n                  </p>\n                  <p className=\"text-sm text-gray-600\">\n                    {language === 'de' \n                      ? 'Sichere Zahlung über Stripe für bezahlte Beratungen'\n                      : 'Secure payment via Stripe for paid consultations'}\n                  </p>\n                </div>\n              </div>\n              <div className=\"flex items-start space-x-3\">\n                <div className=\"w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0\">\n                  <span className=\"font-bold text-blue-600\">3</span>\n                </div>\n                <div>\n                  <p className=\"font-medium\">\n                    {language === 'de' ? 'Video-Konsultation' : 'Video consultation'}\n                  </p>\n                  <p className=\"text-sm text-gray-600\">\n                    {language === 'de' \n                      ? 'Treffen Sie unsere Experten per Video-Anruf'\n                      : 'Meet our experts via video call'}\n                  </p>\n                </div>\n              </div>\n            </div>\n          </CardContent>\n        </Card>\n      </div>\n    </div>\n  );\n};\n\nexport default BookConsultation;\n"}]