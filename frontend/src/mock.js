export const mockLawyers = [
  {
    id: 1,
    name: 'Dr. jur. Anna Müller',
    title: 'Dr. jur.',
    specialization: { de: 'Haager Übereinkommen', en: 'Hague Convention' },
    education: { de: 'Promotion in Internationalem Familienrecht, Universität Amsterdam', en: 'PhD in International Family Law, University of Amsterdam' },
    experience: { de: '15 Jahre Erfahrung', en: '15 years experience' },
    image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop'
  },
  {
    id: 2,
    name: 'Dr. jur. Michael Schmidt',
    title: 'Dr. jur.',
    specialization: { de: 'Internationale Kindesentführung', en: 'International Child Abduction' },
    education: { de: 'Promotion in Völkerrecht, Universität Heidelberg', en: 'PhD in International Law, University of Heidelberg' },
    experience: { de: '12 Jahre Erfahrung', en: '12 years experience' },
    image: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&h=400&fit=crop'
  },
  {
    id: 3,
    name: 'Dr. jur. Sarah van der Berg',
    title: 'Dr. jur.',
    specialization: { de: 'Sorgerechtsberatung', en: 'Custody Rights Consultation' },
    education: { de: 'Promotion in Familienrecht, Universität Leiden', en: 'PhD in Family Law, Leiden University' },
    experience: { de: '10 Jahre Erfahrung', en: '10 years experience' },
    image: 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=400&h=400&fit=crop'
  },
  {
    id: 4,
    name: 'Dr. jur. Thomas Weber',
    title: 'Dr. jur.',
    specialization: { de: 'EU-Familienrecht', en: 'EU Family Law' },
    education: { de: 'Promotion in Europäischem Recht, Universität München', en: 'PhD in European Law, University of Munich' },
    experience: { de: '14 Jahre Erfahrung', en: '14 years experience' },
    image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop'
  },
  {
    id: 5,
    name: 'Dr. jur. Laura Hoffmann',
    title: 'Dr. jur.',
    specialization: { de: 'Grenzüberschreitende Streitigkeiten', en: 'Cross-Border Disputes' },
    education: { de: 'Promotion in Zivilprozessrecht, Universität Wien', en: 'PhD in Civil Procedure, University of Vienna' },
    experience: { de: '11 Jahre Erfahrung', en: '11 years experience' },
    image: 'https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=400&h=400&fit=crop'
  },
  {
    id: 6,
    name: 'Dr. jur. Robert Klein',
    title: 'Dr. jur.',
    specialization: { de: 'Internationales Privatrecht', en: 'Private International Law' },
    education: { de: 'Promotion in Internationalem Privatrecht, Universität Zürich', en: 'PhD in Private International Law, University of Zurich' },
    experience: { de: '13 Jahre Erfahrung', en: '13 years experience' },
    image: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=400&fit=crop'
  },
  {
    id: 7,
    name: 'Dr. jur. Emma de Vries',
    title: 'Dr. jur.',
    specialization: { de: 'Kinderrechte', en: 'Children\'s Rights' },
    education: { de: 'Promotion in Kinderrechten, Universität Utrecht', en: 'PhD in Children\'s Rights, Utrecht University' },
    experience: { de: '9 Jahre Erfahrung', en: '9 years experience' },
    image: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop'
  },
  {
    id: 8,
    name: 'Dr. jur. David Richter',
    title: 'Dr. jur.',
    specialization: { de: 'Mediation & Streitbeilegung', en: 'Mediation & Dispute Resolution' },
    education: { de: 'Promotion in Mediation, Universität Berlin', en: 'PhD in Mediation, University of Berlin' },
    experience: { de: '16 Jahre Erfahrung', en: '16 years experience' },
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop'
  }
];

export const mockFAQs = [
  {
    id: 1,
    question: { 
      de: 'Was ist das Haager Übereinkommen?', 
      en: 'What is the Hague Convention?' 
    },
    answer: { 
      de: 'Das Haager Übereinkommen über die zivilrechtlichen Aspekte internationaler Kindesentführung ist ein multilateraler Vertrag, der den prompten Rückführung von Kindern regelt, die unrechtmäßig in einen anderen Vertragsstaat verbracht oder dort zurückgehalten wurden.',
      en: 'The Hague Convention on the Civil Aspects of International Child Abduction is a multilateral treaty that provides an expeditious method to return children who have been wrongfully removed or retained in a contracting state.'
    }
  },
  {
    id: 2,
    question: { 
      de: 'Wie lange dauert ein internationaler Sorgerechtsfall?', 
      en: 'How long does an international custody case take?' 
    },
    answer: { 
      de: 'Die Dauer variiert je nach Komplexität des Falls und den beteiligten Ländern. Im Durchschnitt dauert ein Fall zwischen 6 und 18 Monaten. Wir arbeiten daran, den Prozess so schnell wie möglich abzuschließen.',
      en: 'The duration varies depending on the complexity of the case and the countries involved. On average, a case takes between 6 and 18 months. We work to complete the process as quickly as possible.'
    }
  },
  {
    id: 3,
    question: { 
      de: 'Was sind meine Rechte als Elternteil?', 
      en: 'What are my rights as a parent?' 
    },
    answer: { 
      de: 'Als Elternteil haben Sie das Recht auf Kontakt zu Ihrem Kind, unabhängig davon, in welchem Land sich das Kind befindet. Unsere Anwälte helfen Ihnen, diese Rechte international durchzusetzen.',
      en: 'As a parent, you have the right to contact with your child, regardless of which country the child is in. Our lawyers help you enforce these rights internationally.'
    }
  },
  {
    id: 4,
    question: { 
      de: 'Welche Dokumente benötige ich?', 
      en: 'What documents do I need?' 
    },
    answer: { 
      de: 'Typischerweise benötigen Sie Geburtsurkunden, Sorgerechtsbeschlüsse, Reisedokumente und jegliche Kommunikation mit dem anderen Elternteil. Wir beraten Sie gerne im Detail während der Erstberatung.',
      en: 'Typically, you need birth certificates, custody orders, travel documents, and any communication with the other parent. We will advise you in detail during the initial consultation.'
    }
  },
  {
    id: 5,
    question: { 
      de: 'Was kostet eine rechtliche Vertretung?', 
      en: 'How much does legal representation cost?' 
    },
    answer: { 
      de: 'Die Kosten variieren je nach Komplexität des Falls. Wir bieten eine kostenlose Erstberatung an und erstellen dann einen transparenten Kostenvoranschlag für Ihren spezifischen Fall.',
      en: 'Costs vary depending on the complexity of the case. We offer a free initial consultation and then provide a transparent cost estimate for your specific case.'
    }
  }
];

export const mockStats = {
  cases: '250+',
  lawyers: '8',
  countries: '35+',
  experience: '15+'
};

// Mock client numbers for testing
export const mockClientNumbers = ['SC2025001', 'SC2025002', 'SC2025003'];

// Mock file numbers for testing
export const mockFileNumbers = ['DOC2025001', 'DOC2025002', 'DOC2025003'];
