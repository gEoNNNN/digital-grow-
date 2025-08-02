import { createContext, useContext, useState, useEffect, type ReactNode } from "react";

type LanguageCode = "RO" | "EN" | "RU";
interface LanguageContextProps {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
}

const LanguageContext = createContext<LanguageContextProps | undefined>(undefined);

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("useLanguage must be used within LanguageProvider");
  return context;
};

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguageState] = useState<LanguageCode>(() => {
    return (localStorage.getItem("language") as LanguageCode) || "RO";
  });

  useEffect(() => {
    localStorage.setItem("language", language);
  }, [language]);

  const setLanguage = (lang: LanguageCode) => {
    setLanguageState(lang);
    localStorage.setItem("language", lang);
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};