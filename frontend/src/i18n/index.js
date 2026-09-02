import en from './en.json';
import hi from './hi.json';
import as from './as.json';
import bn from './bn.json';
import ne from './ne.json';

export const translations = {
  en,
  hi,
  as,
  bn,
  ne
};

export const languages = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'as', name: 'Assamese', native: 'অসমীয়া' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা' },
  { code: 'ne', name: 'Nepali', native: 'नेपाली' }
];

export const getTranslation = (lang, key) => {
  const dict = translations[lang] || translations.en;
  return dict[key] || translations.en[key] || key;
};
