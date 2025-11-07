import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../translations';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Scale, Globe, Users, Shield, FileCheck, Briefcase } from 'lucide-react';
import { Button } from '../components/ui/button';

const Services = () => {
  const { language } = useLanguage();

  const services = [
    {
      icon: Scale,
      title: t(language, 'service1Title'),
      description: t(language, 'service1Description'),
      details: language === 'de' 
        ? 'Unsere Anwälte sind Experten in der Anwendung des Haager Übereinkommens von 1980. Wir vertreten Eltern in Fällen, in denen Kinder unrechtmäßig über internationale Grenzen verbracht wurden. Mit umfassender Erfahrung in mehreren Rechtsordnungen kämpfen wir für die schnelle Rückführung Ihrer Kinder.'
        : 'Our lawyers are experts in applying the 1980 Hague Convention. We represent parents in cases where children have been wrongfully taken across international borders. With extensive experience in multiple jurisdictions, we fight for the prompt return of your children.',
    },
    {
      icon: Globe,
      title: t(language, 'service2Title'),
      description: t(language, 'service2Description'),
      details: language === 'de'
        ? 'Wenn ein Elternteil Ihr Kind ohne Ihre Zustimmung in ein anderes Land gebracht hat, können wir helfen. Wir koordinieren mit internationalen Behörden, stellen Eilanträge und arbeiten daran, Ihr Kind sicher zurückzubringen. Unser Netzwerk erstreckt sich über 35 Länder.'
        : 'If a parent has taken your child to another country without your consent, we can help. We coordinate with international authorities, file emergency applications, and work to safely return your child. Our network spans 35 countries.',
    },
    {
      icon: Users,
      title: t(language, 'service3Title'),
      description: t(language, 'service3Description'),
      details: language === 'de'
        ? 'Wir bieten umfassende Beratung zu allen Aspekten des internationalen Sorge- und Umgangsrechts. Von der ersten Beratung bis zur vollständigen Vertretung vor Gericht - wir begleiten Sie durch jeden Schritt des komplexen rechtlichen Prozesses.'
        : 'We provide comprehensive advice on all aspects of international custody and visitation rights. From initial consultation to full court representation - we guide you through every step of the complex legal process.',
    },
    {
      icon: Shield,
      title: language === 'de' ? 'Kinderschutz' : 'Child Protection',
      description: language === 'de'
        ? 'Schutz Ihres Kindes vor gefährlichen Situationen durch internationale rechtliche Maßnahmen.'
        : 'Protecting your child from dangerous situations through international legal measures.',
      details: language === 'de'
        ? 'Wenn Sie befürchten, dass Ihr Kind in Gefahr ist, können wir dringende Schutzmaßnahmen einleiten. Wir arbeiten mit Behörden zusammen, um einstweilige Verfügungen zu erwirken und die Sicherheit Ihres Kindes zu gewährleisten.'
        : 'If you fear your child is in danger, we can initiate urgent protective measures. We work with authorities to obtain restraining orders and ensure your child\'s safety.',
    },
    {
      icon: FileCheck,
      title: language === 'de' ? 'Dokumentenanalyse' : 'Document Analysis',
      description: language === 'de'
        ? 'Forensische Analyse von Kommunikation und Dokumenten zur Unterstützung Ihres Falls.'
        : 'Forensic analysis of communications and documents to support your case.',
      details: language === 'de'
        ? 'Mit Ihrer Zustimmung können wir eine detaillierte Analyse Ihrer Kommunikation durchführen. Dies hilft uns, starke Beweise für Ihren Fall zu sammeln und Ihre Position vor Gericht zu stärken.'
        : 'With your consent, we can conduct detailed analysis of your communications. This helps us gather strong evidence for your case and strengthen your position in court.',
    },
    {
      icon: Briefcase,
      title: language === 'de' ? 'Mediation' : 'Mediation',
      description: language === 'de'
        ? 'Außergerichtliche Lösungen durch professionelle Mediation und Verhandlung.'
        : 'Out-of-court solutions through professional mediation and negotiation.',
      details: language === 'de'
        ? 'Nicht jeder Fall muss vor Gericht gehen. Unsere erfahrenen Mediatoren können helfen, einvernehmliche Lösungen zu finden, die das Wohl Ihrer Kinder in den Mittelpunkt stellen.'
        : 'Not every case needs to go to court. Our experienced mediators can help find consensual solutions that prioritize your children\'s wellbeing.',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            {t(language, 'servicesTitle')}
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t(language, 'servicesSubtitle')}
          </p>
        </div>

        {/* Services Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {services.map((service, index) => {
            const Icon = service.icon;
            return (
              <Card key={index} className="border-2 hover:border-blue-500 hover:shadow-xl transition-all duration-300">
                <CardHeader>
                  <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                    <Icon className="w-8 h-8 text-blue-600" />
                  </div>
                  <CardTitle className="text-2xl mb-2">{service.title}</CardTitle>
                  <CardDescription className="text-base">
                    {service.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">{service.details}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            {language === 'de' 
              ? 'Benötigen Sie rechtliche Unterstützung?' 
              : 'Need Legal Support?'}
          </h2>
          <p className="text-lg mb-8 opacity-90 max-w-2xl mx-auto">
            {language === 'de'
              ? 'Unsere Experten stehen bereit, Ihnen zu helfen. Kontaktieren Sie uns für eine kostenlose Erstberatung.'
              : 'Our experts are ready to help you. Contact us for a free initial consultation.'}
          </p>
          <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8">
            {t(language, 'heroButton')}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Services;
