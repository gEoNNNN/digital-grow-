import React, { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useNavigate } from 'react-router-dom';
import './CookieBanner.css';

const CookieBanner = () => {
  const [isVisible, setIsVisible] = useState(false);
  const { language } = useLanguage();
  const navigate = useNavigate();

  const content = {
    RO: {
      message: "Acest site folosește cookie-uri pentru a vă oferi cea mai bună experiență.",
      acceptAll: "Accept toate cookie-urile",
      rejectNonEssential: "Refuz neesențialele",
      learnMore: "Aflați mai multe despre politica noastră privind cookie-urile",
      here: "aici"
    },
    EN: {
      message: "This website uses cookies to provide you with the best experience.",
      acceptAll: "Accept all cookies",
      rejectNonEssential: "Reject non-essential",
      learnMore: "Learn more about our cookie policy",
      here: "here"
    },
    RU: {
      message: "Этот сайт использует файлы cookie для предоставления вам наилучшего опыта.",
      acceptAll: "Принять все cookie",
      rejectNonEssential: "Отклонить необязательные",
      learnMore: "Узнайте больше о нашей политике использования cookie",
      here: "здесь"
    }
  };

  const currentContent = content[language as keyof typeof content];

  useEffect(() => {
    // Clear localStorage for testing - remove this line after testing
    // localStorage.removeItem('cookieConsent');
    
    // Check if user has already made a choice
    const cookieChoice = localStorage.getItem('cookieConsent');
    console.log('Cookie choice from localStorage:', cookieChoice); // Debug log
    
    if (!cookieChoice) {
      console.log('No cookie choice found, showing banner'); // Debug log
      // Show banner after a short delay for better UX
      setTimeout(() => {
        setIsVisible(true);
      }, 1000);
    } else {
      console.log('Cookie choice found, not showing banner'); // Debug log
    }
  }, []);

  const handleAcceptAll = () => {
    console.log('Accept all clicked'); // Debug log
    localStorage.setItem('cookieConsent', 'accepted');
    localStorage.setItem('cookiePreferences', JSON.stringify({
      necessary: true,
      analytical: true,
      functional: true
    }));
    setIsVisible(false);
  };

  const handleRejectNonEssential = () => {
    console.log('Reject non-essential clicked'); // Debug log
    localStorage.setItem('cookieConsent', 'rejected');
    localStorage.setItem('cookiePreferences', JSON.stringify({
      necessary: true,
      analytical: false,
      functional: false
    }));
    setIsVisible(false);
  };

  const handleLearnMore = () => {
    navigate('/cookie-policy');
  };

  console.log('CookieBanner render - isVisible:', isVisible); // Debug log

  if (!isVisible) {
    return null;
  }

  return (
    <div className="cookie-banner">
      <div className="cookie-banner-content">
        <div className="cookie-banner-text">
          <p className="cookie-banner-message">
            {currentContent.message}
          </p>
          <p className="cookie-banner-learn-more">
            {currentContent.learnMore}{' '}
            <button 
              className="cookie-banner-link"
              onClick={handleLearnMore}
            >
              {currentContent.here}
            </button>
            .
          </p>
        </div>
        
        <div className="cookie-banner-buttons">
          <button 
            className="cookie-banner-btn cookie-banner-btn-accept"
            onClick={handleAcceptAll}
          >
            {currentContent.acceptAll}
          </button>
          <button 
            className="cookie-banner-btn cookie-banner-btn-reject"
            onClick={handleRejectNonEssential}
          >
            {currentContent.rejectNonEssential}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CookieBanner;