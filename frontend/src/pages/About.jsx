import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../translations';
import { mockLawyers } from '../mock';
import { Card, CardContent } from '../components/ui/card';
import { GraduationCap, Briefcase } from 'lucide-react';

const About = () => {
  const { language } = useLanguage();

  return (
    <div className="min-h-screen bg-gray-50 py-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            {t(language, 'aboutTitle')}
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t(language, 'aboutSubtitle')}
          </p>
        </div>

        {/* Description */}
        <div className="max-w-4xl mx-auto mb-20">
          <Card className="border-2">
            <CardContent className="p-8">
              <p className="text-lg text-gray-700 leading-relaxed">
                {t(language, 'aboutDescription')}
              </p>
              <div className="mt-8 grid md:grid-cols-3 gap-6">
                <div className="text-center p-6 bg-blue-50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">8</div>
                  <div className="text-sm text-gray-700">
                    {language === 'de' ? 'Spezialisierte Anwälte' : 'Specialized Lawyers'}
                  </div>
                </div>
                <div className="text-center p-6 bg-blue-50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">PhD</div>
                  <div className="text-sm text-gray-700">
                    {language === 'de' ? 'Mindestqualifikation' : 'Minimum Qualification'}
                  </div>
                </div>
                <div className="text-center p-6 bg-blue-50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">35+</div>
                  <div className="text-sm text-gray-700">
                    {language === 'de' ? 'Länder Weltweit' : 'Countries Worldwide'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Team Section */}
        <div className="mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
            {t(language, 'teamTitle')}
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {mockLawyers.map((lawyer) => (
              <Card key={lawyer.id} className="overflow-hidden hover:shadow-xl transition-all duration-300 border-2 hover:border-blue-500">
                <div className="aspect-square overflow-hidden">
                  <img
                    src={lawyer.image}
                    alt={lawyer.name}
                    className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                  />
                </div>
                <CardContent className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-1">
                    {lawyer.name}
                  </h3>
                  <div className="text-sm text-blue-600 font-semibold mb-4">
                    {lawyer.specialization[language]}
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-start space-x-2">
                      <GraduationCap className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-600">
                        {lawyer.education[language]}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Briefcase className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      <span className="text-sm text-gray-600">
                        {lawyer.experience[language]}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Values Section */}
        <div className="mt-20 bg-gradient-to-br from-blue-50 to-white rounded-2xl p-12">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            {language === 'de' ? 'Unsere Werte' : 'Our Values'}
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {language === 'de' ? 'Kinderwohl zuerst' : 'Children First'}
              </h3>
              <p className="text-gray-600">
                {language === 'de'
                  ? 'Das Wohl und die Rechte der Kinder stehen im Mittelpunkt unserer Arbeit.'
                  : 'The wellbeing and rights of children are at the heart of our work.'}
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {language === 'de' ? 'Expertise' : 'Expertise'}
              </h3>
              <p className="text-gray-600">
                {language === 'de'
                  ? 'Hochqualifizierte Anwälte mit akademischer Exzellenz und praktischer Erfahrung.'
                  : 'Highly qualified lawyers with academic excellence and practical experience.'}
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {language === 'de' ? 'Transparenz' : 'Transparency'}
              </h3>
              <p className="text-gray-600">
                {language === 'de'
                  ? 'Klare Kommunikation und vollständige Transparenz in allen Prozessen.'
                  : 'Clear communication and complete transparency in all processes.'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
