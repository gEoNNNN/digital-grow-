import React, { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import './PayPal.css';

interface PayPalPaymentProps {
  isOpen: boolean;
  onClose: () => void;
  serviceName?: string;
  servicePrice?: string;
  currency?: string;
}

// Define the language type
type Language = 'RO' | 'EN' | 'RU';

// Define proper types for the content structure
interface PartialPaymentOptions {
  [key: string]: string;
}

interface ServiceContent {
  title: string;
  selectService: string;
  selectPlaceholder: string;
  enterAmount: string;
  amountPlaceholder: string;
  payButton: string;
  serviceError: string;
  amountError: string;
  partialPaymentLabel: string;
  partialPaymentOptions: PartialPaymentOptions;
  services: string[];
}

const PayPalPayment: React.FC<PayPalPaymentProps> = ({
  isOpen,
  onClose,
  serviceName = '',
  servicePrice = '',
  currency = 'MDL'
}) => {
  const { language } = useLanguage();
  const [selectedService, setSelectedService] = useState(serviceName);
  const [amount, setAmount] = useState(servicePrice);
  const [serviceError, setServiceError] = useState(false);
  const [amountError, setAmountError] = useState(false);
  const [exchangeRate, setExchangeRate] = useState(18); // Default fallback rate
  const [isLoadingRate, setIsLoadingRate] = useState(false);
  const [partialPayment, setPartialPayment] = useState(100); // Default to full payment (100%)
  const [originalAmount, setOriginalAmount] = useState('');

  // Fetch exchange rate from Moldova National Bank API
  const fetchExchangeRate = async () => {
    setIsLoadingRate(true);
    try {
      // Moldova National Bank API for USD to MDL rate
      const response = await fetch('https://bnm.md/ro/official_exchange_rates?get_xml=1');
      const xmlText = await response.text();
      
      // Parse XML to get USD rate
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
      const usdRate = xmlDoc.querySelector('Valute[CharCode="USD"] Value');
      
      if (usdRate && usdRate.textContent) {
        const rate = parseFloat(usdRate.textContent.replace(',', '.'));
        setExchangeRate(rate);
        console.log(`Updated exchange rate: 1 USD = ${rate} MDL`);
      } else {
        throw new Error('USD rate not found');
      }
    } catch (error) {
      console.warn('Failed to fetch exchange rate from BNM, using fallback APIs');
      
      // Fallback to other free APIs
      try {
        // Try exchangerate-api.com (free tier)
        const fallbackResponse = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
        const data = await fallbackResponse.json();
        
        if (data.rates && data.rates.MDL) {
          setExchangeRate(data.rates.MDL);
          console.log(`Updated exchange rate (fallback): 1 USD = ${data.rates.MDL} MDL`);
        } else {
          throw new Error('MDL rate not found in fallback API');
        }
      } catch (fallbackError) {
        console.error('All exchange rate APIs failed, using default rate:', exchangeRate);
      }
    } finally {
      setIsLoadingRate(false);
    }
  };

  // Fetch exchange rate when component mounts
  useEffect(() => {
    if (currency === 'MDL') {
      fetchExchangeRate();
    }
  }, [currency]);

  // Price mapping for each service in different languages
  const servicePrices: Record<Language, Record<string, string>> = {
    RO: {
      "Landing Page One-Page": "5500",
      "Site Corporate (3-5 pagini)": "10000",
      "Site Multilingv Complex": "20000",
      "Magazin Online (E-commerce)": "30000",
      "Întreținere Lunară": "2000",
      "ChatBot Simplu": "7000",
      "ChatBot Instagram": "7000",
      "ChatBot Messenger": "7000",
      "ChatBot Inteligent (GPT-4) + CRM": "18000",
      "Implementare CRM": "10000",
      "Logo Profesional": "3500",
      "Actualizare Logo (Refresh)": "2000",
      "Materiale Promoționale": "350",
      "Startup Light":"5000",
      "Business Smart":"10000",
      "Enterprise Complete":"20000",
      
    },
    EN: {
      "One-Page Landing Page": "430",
      "Business Website (3-5 pages)": "760",
      "Multilingual Complex Website": "1520",
      "E-commerce Store": "2280",
      "Monthly Maintenance": "101",
      "Basic Chatbot": "506",
      "Instagram Chatbot": "506",
      "Messenger Chatbot": "506",
      "AI Chatbot (GPT-4) + CRM": "1266",
      "CRM Implementation": "760",
      "Professional Logo": "253",
      "Logo Refresh": "151",
      "Promotional Materials": "25",
      "Startup Light":"455",
      "Business Smart":"962",
      "Enterprise Complete":"2532",
    },
    RU: {
      "Одностраничный Landing": "5500",
      "Корпоративный сайт (3-5 страниц)": "10000",
      "Многоязычный сайт": "20000",
      "Интернет-магазин": "30000",
      "Ежемесячная поддержка": "2000",
      "Простой ChatBot": "7000",
      "ChatBot Instagram": "7000",
      "ChatBot Messenger": "7000",
      "Умный ChatBot (GPT-4) + CRM": "18000",
      "Внедрение CRM": "10000",
      "Профессиональный логотип": "3500",
      "Обновление логотипа": "2000",
      "Промо-материалы": "350",
      "Startup Light":"5000",
      "Business Smart":"10000",
      "Enterprise Complete":"20000",
    }
  };

  const services: Record<Language, ServiceContent> = {
    RO: {
      title: "💼 Plată Servicii",
      selectService: "Alege serviciul:",
      selectPlaceholder: "-- Selectează un serviciu --",
      enterAmount: "Suma",
      amountPlaceholder: "Preț automat",
      payButton: "💳 Plătește cu PayPal",
      serviceError: "Te rugăm să selectezi un serviciu.",
      amountError: "Te rugăm să introduci o sumă validă (mai mare decât 0).",
      partialPaymentLabel: "Plătește doar o parte:",
      partialPaymentOptions: {
        10: "10% - Avans mic",
        20: "20% - Avans standard", 
        30: "30% - Avans mare",
        50: "50% - Jumătate",
        90: "90% - Aproape totul",
        100: "100% - Plata completă"
      },
      services: [
        "Landing Page One-Page",
        "Site Corporate (3-5 pagini)",
        "Site Multilingv Complex",
        "Magazin Online (E-commerce)",
        "Întreținere Lunară",
        "ChatBot Simplu",
        "ChatBot Instagram",
        "ChatBot Messenger",
        "ChatBot Inteligent (GPT-4) + CRM",
        "Implementare CRM",
        "Logo Profesional",
        "Actualizare Logo (Refresh)",
        "Materiale Promoționale",
        "Startup Light",
        "Business Smart",
        "Enterprise Complete"
      ]
    },
    EN: {
      title: "💼 Service Payment",
      selectService: "Choose service:",
      selectPlaceholder: "-- Select a service --",
      enterAmount: "Amount",
      amountPlaceholder: "Auto price",
      payButton: "💳 Pay with PayPal",
      serviceError: "Please select a service.",
      amountError: "Please enter a valid amount (greater than 0).",
      partialPaymentLabel: "Pay just a part:",
      partialPaymentOptions: {
        10: "10% - Small advance",
        20: "20% - Standard advance",
        30: "30% - Large advance", 
        50: "50% - Half payment",
        90: "90% - Almost everything",
        100: "100% - Full payment"
      },
      services: [
        "One-Page Landing Page",
        "Business Website (3-5 pages)",
        "Multilingual Complex Website",
        "E-commerce Store",
        "Monthly Maintenance",
        "Basic Chatbot",
        "Instagram Chatbot",
        "Messenger Chatbot",
        "AI Chatbot (GPT-4) + CRM",
        "CRM Implementation",
        "Professional Logo",
        "Logo Refresh",
        "Promotional Materials",
        "Startup Light",
        "Business Smart",
        "Enterprise Complete"
      ]
    },
    RU: {
      title: "💼 Оплата Услуг",
      selectService: "Выберите услугу:",
      selectPlaceholder: "-- Выберите услугу --",
      enterAmount: "Сумма",
      amountPlaceholder: "Автоцена",
      payButton: "💳 Оплатить через PayPal",
      serviceError: "Пожалуйста, выберите услугу.",
      amountError: "Пожалуйста, введите действительную сумму (больше 0).",
      partialPaymentLabel: "Оплатить только часть:",
      partialPaymentOptions: {
        10: "10% - Небольшой аванс",
        20: "20% - Стандартный аванс",
        30: "30% - Большой аванс",
        50: "50% - Половина",
        90: "90% - Почти всё",
        100: "100% - Полная оплата"
      },
      services: [
        "Одностраничный Landing",
        "Корпоративный сайт (3-5 страниц)",
        "Многоязычный сайт",
        "Интернет-магазин",
        "Ежемесячная поддержка",
        "Простой ChatBot",
        "ChatBot Instagram",
        "ChatBot Messenger",
        "Умный ChatBot (GPT-4) + CRM",
        "Внедрение CRM",
        "Профессиональный логотип",
        "Обновление логотипа",
        "Промо-материалы",
        "Startup Light",
        "Business Smart",
        "Enterprise Complete"
      ]
    }
  };

  const currentLanguage = language as Language;
  const content = services[currentLanguage];

  // Update amount when service is selected
  useEffect(() => {
    if (selectedService && servicePrices[currentLanguage]?.[selectedService]) {
      const baseAmount = servicePrices[currentLanguage][selectedService];
      setOriginalAmount(baseAmount);
      // Calculate partial payment
      const partialAmount = Math.round((Number(baseAmount) * partialPayment) / 100);
      setAmount(partialAmount.toString());
    }
  }, [selectedService, language, currentLanguage, partialPayment]);

  const handleServiceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const service = e.target.value;
    setSelectedService(service);
    
    // Auto-populate price based on selected service
    if (service && servicePrices[currentLanguage]?.[service]) {
      const baseAmount = servicePrices[currentLanguage][service];
      setOriginalAmount(baseAmount);
      // Calculate partial payment
      const partialAmount = Math.round((Number(baseAmount) * partialPayment) / 100);
      setAmount(partialAmount.toString());
      setAmountError(false); // Clear any previous errors
    } else {
      setAmount('');
      setOriginalAmount('');
    }
  };

  const handlePartialPaymentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const percentage = Number(e.target.value);
    setPartialPayment(percentage);
    
    // Recalculate amount based on new percentage
    if (originalAmount) {
      const partialAmount = Math.round((Number(originalAmount) * percentage) / 100);
      setAmount(partialAmount.toString());
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    // Basic validation
    if (!selectedService) {
      setServiceError(true);
      e.preventDefault();
      return;
    } else {
      setServiceError(false);
    }

    // Validate amount exists and is valid
    if (!amount || isNaN(Number(amount)) || Number(amount) <= 0) {
      setAmountError(true);
      e.preventDefault();
      return;
    } else {
      setAmountError(false);
    }

    // Convert currency and amount for PayPal compatibility
    let paypalCurrency = currency;
    let paypalAmount = amount;

    // PayPal doesn't support MDL, so convert to USD using real exchange rate
    if (currency === 'MDL') {
      paypalCurrency = 'USD';
      // Convert MDL to USD using current exchange rate
      paypalAmount = (Number(amount) / exchangeRate).toFixed(2);
    }

    // Create and submit PayPal form programmatically
    const form = document.createElement('form');
    form.action = 'https://www.paypal.com/cgi-bin/webscr';
    form.method = 'post';
    form.target = '_blank';

    // PayPal form fields
    const paymentType = partialPayment === 100 ? '' : ` (${partialPayment}% payment)`;
    const fields = {
      'cmd': '_xclick',
      'business': 'digitalgrow.moldova@gmail.com',
      'item_name': selectedService + paymentType + (currency === 'MDL' ? ` (${amount} MDL)` : ''),
      'amount': paypalAmount,
      'currency_code': paypalCurrency,
      'return': `${window.location.origin}/payment-success`,
      'cancel_return': `${window.location.origin}/payment-cancel`,
      'notify_url': `${window.location.origin}/payment-notify`
    };

    // Add hidden inputs to form
    Object.entries(fields).forEach(([key, value]) => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = value;
      form.appendChild(input);
    });

    // Submit form to PayPal
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);

    // Prevent default form submission
    e.preventDefault();

    // Close modal
    setTimeout(() => {
      onClose();
    }, 100);
  };

  if (!isOpen) return null;

  return (
    <div className="paypal-overlay">
      <div className="paypal-modal">
        <button className="paypal-close" onClick={onClose}>×</button>
        <form 
          className="paypal-form" 
          onSubmit={handleSubmit}
        >
          <h2 className="paypal-title">{content.title}</h2>
          
          <label className="paypal-label">{content.selectService}</label>
          <select
            value={selectedService}
            onChange={handleServiceChange}
            className={`paypal-select ${serviceError ? 'error' : ''}`}
            required
          >
            <option value="">{content.selectPlaceholder}</option>
            {content.services.map((service: string) => (
              <option key={service} value={service}>
                {service}
              </option>
            ))}
          </select>
          {serviceError && <div className="paypal-error">{content.serviceError}</div>}
          
          {/* Partial Payment Section */}
          {originalAmount && (
            <div className="paypal-partial-section">
              <label className="paypal-label paypal-partial-label">
                {content.partialPaymentLabel}
              </label>
              <select
                value={partialPayment}
                onChange={handlePartialPaymentChange}
                className="paypal-select paypal-partial-select"
              >
                {Object.entries(content.partialPaymentOptions).map(([percentage, label]) => (
                  <option key={percentage} value={percentage}>
                    {String(label)}
                  </option>
                ))}
              </select>
              
              {partialPayment !== 100 && (
                <div className="paypal-partial-info">
                  <span className="paypal-partial-total">
                    Total: {originalAmount} {currency}
                  </span>
                  <span className="paypal-partial-paying">
                    Paying: {amount} {currency} ({partialPayment}%)
                  </span>
                  <span className="paypal-partial-remaining">
                    Remaining: {Number(originalAmount) - Number(amount)} {currency}
                  </span>
                </div>
              )}
            </div>
          )}
          
          <label className="paypal-label">
            {content.enterAmount} ({currency})
            {currency === 'MDL' && amount && (
              <span style={{fontSize: '0.8em', color: '#666', display: 'block'}}>
                {isLoadingRate ? (
                  'Loading exchange rate...'
                ) : (
                  `PayPal will charge ~$${(Number(amount) / exchangeRate).toFixed(2)} USD (Rate: 1 USD = ${exchangeRate} MDL)`
                )}
              </span>
            )}
          </label>
          <input
            type="text"
            value={amount}
            readOnly
            placeholder={content.amountPlaceholder}
            className={`paypal-input paypal-input-readonly ${amountError ? 'error' : ''}`}
          />
          {amountError && <div className="paypal-error">{content.amountError}</div>}
          
          <button type="submit" className="paypal-button" disabled={isLoadingRate}>
            {isLoadingRate ? 'Loading...' : content.payButton}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PayPalPayment;