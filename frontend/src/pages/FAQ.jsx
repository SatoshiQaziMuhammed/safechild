import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../translations';
import { mockFAQs } from '../mock';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../components/ui/accordion';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { MessageCircle } from 'lucide-react';

const FAQ = () => {
  const { language } = useLanguage();

  return (
    <div className="min-h-screen bg-gray-50 py-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            {t(language, 'faqTitle')}
          </h1>
          <p className="text-xl text-gray-600">
            {t(language, 'faqSubtitle')}
          </p>
        </div>

        {/* FAQ Accordion */}
        <Card className="border-2 mb-12">
          <CardContent className="p-6">
            <Accordion type="single" collapsible className="w-full">
              {mockFAQs.map((faq, index) => (
                <AccordionItem key={faq.id} value={`item-${faq.id}`}>
                  <AccordionTrigger className="text-left text-lg font-semibold hover:text-blue-600">
                    {faq.question[language]}
                  </AccordionTrigger>
                  <AccordionContent className="text-base text-gray-700 leading-relaxed">
                    {faq.answer[language]}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </CardContent>
        </Card>

        {/* Contact CTA */}
        <Card className="bg-gradient-to-r from-blue-600 to-blue-800 text-white border-0">
          <CardContent className="p-12 text-center">
            <MessageCircle className="w-16 h-16 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4">
              {language === 'de' 
                ? 'Noch Fragen?' 
                : 'Still Have Questions?'}
            </h2>
            <p className="text-lg mb-8 opacity-90">
              {language === 'de'
                ? 'Unser Team steht Ihnen gerne für eine persönliche Beratung zur Verfügung.'
                : 'Our team is happy to provide you with personal advice.'}
            </p>
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8">
              {t(language, 'heroButton')}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default FAQ;
