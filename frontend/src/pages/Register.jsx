import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';
import { Lock, Mail, User, Phone, MapPin, Briefcase } from 'lucide-react';

const Register = () => {
  const { language } = useLanguage();
  const { register } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    phone: '',
    country: '',
    caseType: 'hague_convention'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password.length < 6) {
      toast.error(
        language === 'de' ? 'Passwort zu kurz' : 'Password too short',
        { description: language === 'de' ? 'Mindestens 6 Zeichen' : 'At least 6 characters' }
      );
      return;
    }

    setLoading(true);
    const result = await register(formData);
    
    if (result.success) {
      toast.success(
        language === 'de' ? 'Erfolgreich registriert' : 'Successfully registered'
      );
      navigate('/portal');
    } else {
      toast.error(
        language === 'de' ? 'Registrierung fehlgeschlagen' : 'Registration failed',
        { description: result.error }
      );
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {language === 'de' ? 'Konto erstellen' : 'Create Account'}
          </h1>
          <p className="text-gray-600">
            {language === 'de' ? 'Registrieren Sie sich für das Kundenportal' : 'Register for the client portal'}
          </p>
        </div>

        <Card className="border-2">
          <CardHeader>
            <CardTitle className="text-2xl">
              {language === 'de' ? 'Registrierung' : 'Registration'}
            </CardTitle>
            <CardDescription>
              {language === 'de' ? 'Füllen Sie alle Felder aus' : 'Fill in all fields'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">
                    {language === 'de' ? 'Vorname' : 'First Name'}
                  </Label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <Input
                      id="firstName"
                      value={formData.firstName}
                      onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lastName">
                    {language === 'de' ? 'Nachname' : 'Last Name'}
                  </Label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <Input
                      id="lastName"
                      value={formData.lastName}
                      onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">{language === 'de' ? 'E-Mail' : 'Email'}</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">{language === 'de' ? 'Passwort' : 'Password'}</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="pl-10"
                    required
                    minLength={6}
                  />
                </div>
                <p className="text-xs text-gray-500">
                  {language === 'de' ? 'Mindestens 6 Zeichen' : 'At least 6 characters'}
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">{language === 'de' ? 'Telefon' : 'Phone'}</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <Input
                      id="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="country">{language === 'de' ? 'Land' : 'Country'}</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-400 z-10" />
                    <Input
                      id="country"
                      value={formData.country}
                      onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="caseType">{language === 'de' ? 'Fall-Typ' : 'Case Type'}</Label>
                <Select value={formData.caseType} onValueChange={(value) => setFormData({ ...formData, caseType: value })}>
                  <SelectTrigger>
                    <Briefcase className="w-4 h-4 mr-2" />
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hague_convention">
                      {language === 'de' ? 'Haager Übereinkommen' : 'Hague Convention'}
                    </SelectItem>
                    <SelectItem value="child_abduction">
                      {language === 'de' ? 'Kindesentführung' : 'Child Abduction'}
                    </SelectItem>
                    <SelectItem value="custody_rights">
                      {language === 'de' ? 'Sorgerecht' : 'Custody Rights'}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? (
                  language === 'de' ? 'Registrierung...' : 'Registering...'
                ) : (
                  language === 'de' ? 'Konto erstellen' : 'Create Account'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                {language === 'de' ? 'Haben Sie bereits ein Konto?' : 'Already have an account?'}{' '}
                <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                  {language === 'de' ? 'Anmelden' : 'Sign In'}
                </Link>
              </p>
            </div>

            <div className="mt-4 text-center">
              <Link to="/" className="text-sm text-gray-600 hover:text-gray-900">
                ← {language === 'de' ? 'Zurück zur Startseite' : 'Back to homepage'}
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Register;
