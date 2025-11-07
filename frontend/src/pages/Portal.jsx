import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import { LogOut, Upload, FileText, Download, User, Calendar } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Portal = () => {
  const { language } = useLanguage();
  const { user, token, logout, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login');
    }
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (user && token) {
      fetchDocuments();
    }
  }, [user, token]);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API}/portal/documents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      toast.error(
        language === 'de' ? 'Fehler beim Laden der Dokumente' : 'Failed to load documents'
      );
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleFileSelect = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error(
        language === 'de' ? 'Keine Datei ausgewählt' : 'No file selected'
      );
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      await axios.post(`${API}/portal/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      });

      toast.success(
        language === 'de' ? 'Dokument erfolgreich hochgeladen' : 'Document uploaded successfully'
      );
      
      setSelectedFile(null);
      fetchDocuments();
    } catch (error) {
      toast.error(
        language === 'de' ? 'Upload fehlgeschlagen' : 'Upload failed',
        { description: error.response?.data?.detail || error.message }
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (documentNumber, fileName) => {
    try {
      const response = await axios.get(`${API}/documents/${documentNumber}/download`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success(
        language === 'de' ? 'Download gestartet' : 'Download started'
      );
    } catch (error) {
      toast.error(
        language === 'de' ? 'Download fehlgeschlagen' : 'Download failed'
      );
    }
  };

  const handleLogout = () => {
    logout();
    toast.success(
      language === 'de' ? 'Erfolgreich abgemeldet' : 'Successfully logged out'
    );
    navigate('/');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(language === 'de' ? 'de-DE' : 'en-US');
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            {language === 'de' ? 'Laden...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">SC</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  {language === 'de' ? 'Kundenportal' : 'Client Portal'}
                </h1>
                <p className="text-sm text-gray-600">
                  {user.firstName} {user.lastName}
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              onClick={handleLogout}
              className="flex items-center space-x-2"
            >
              <LogOut className="w-4 h-4" />
              <span>{language === 'de' ? 'Abmelden' : 'Logout'}</span>
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* User Info Card */}
        <Card className="mb-8 border-2">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <CardTitle>{language === 'de' ? 'Mein Konto' : 'My Account'}</CardTitle>
                <CardDescription>{user.email}</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">{language === 'de' ? 'Mandantennummer' : 'Client Number'}</p>
                <p className="font-semibold">{user.clientNumber}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">{language === 'de' ? 'Name' : 'Name'}</p>
                <p className="font-semibold">{user.firstName} {user.lastName}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Upload Section */}
        <Card className="mb-8 border-2">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <Upload className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <CardTitle>{language === 'de' ? 'Dokument hochladen' : 'Upload Document'}</CardTitle>
                <CardDescription>
                  {language === 'de' ? 'Laden Sie Ihre Dokumente hoch' : 'Upload your documents'}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4">
              <Input
                type="file"
                onChange={handleFileSelect}
                className="flex-1"
              />
              <Button
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                className="bg-green-600 hover:bg-green-700"
              >
                {uploading ? (
                  language === 'de' ? 'Hochladen...' : 'Uploading...'
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    {language === 'de' ? 'Hochladen' : 'Upload'}
                  </>
                )}
              </Button>
            </div>
            {selectedFile && (
              <p className="mt-2 text-sm text-gray-600">
                {language === 'de' ? 'Ausgewählte Datei:' : 'Selected file:'} {selectedFile.name}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Documents List */}
        <Card className="border-2">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <CardTitle>{language === 'de' ? 'Meine Dokumente' : 'My Documents'}</CardTitle>
                <CardDescription>
                  {documents.length} {language === 'de' ? 'Dokument(e)' : 'document(s)'}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {loadingDocs ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">
                  {language === 'de' ? 'Dokumente laden...' : 'Loading documents...'}
                </p>
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>{language === 'de' ? 'Keine Dokumente vorhanden' : 'No documents yet'}</p>
              </div>
            ) : (
              <div className="space-y-3">
                {documents.map((doc) => (
                  <div
                    key={doc.documentNumber}
                    className="flex items-center justify-between p-4 border-2 rounded-lg hover:border-blue-500 transition-colors"
                  >
                    <div className="flex items-center space-x-3 flex-1">
                      <FileText className="w-8 h-8 text-blue-600" />
                      <div>
                        <p className="font-medium">{doc.fileName}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {formatDate(doc.uploadedAt)}
                          </span>
                          <span>{formatFileSize(doc.fileSize)}</span>
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                            {doc.documentNumber}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleDownload(doc.documentNumber, doc.fileName)}
                      variant="outline"
                      size="sm"
                      className="ml-4"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      {language === 'de' ? 'Download' : 'Download'}
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Portal;
