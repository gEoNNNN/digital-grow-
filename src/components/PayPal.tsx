import React, { useState } from 'react';
import { useLanguage } from './LanguageContext';
import './PayPal.css';

interface PayPalPaymentProps {
  isOpen: boolean;
  onClose: () => void;
  serviceName?: string;
  servicePrice?: string;
  currency?: string;
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

  const services = {
    RO: {
      title: "💼 Plată Servicii",
      selectService: "Alege serviciul:",
      selectPlaceholder: "-- Selectează un serviciu --",
      enterAmount: "Introduceți suma",
      amountPlaceholder: "Ex: 500",
      payButton: "💳 Plătește cu PayPal",
      serviceError: "Te rugăm să selectezi un serviciu.",
      amountError: "Te rugăm să introduci o sumă validă (mai mare decât 0).",
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
        "Materiale Promoționale"
      ]
    },
    EN: {
      title: "💼 Service Payment",
      selectService: "Choose service:",
      selectPlaceholder: "-- Select a service --",
      enterAmount: "Enter amount",
      amountPlaceholder: "Ex: 500",
      payButton: "💳 Pay with PayPal",
      serviceError: "Please select a service.",
      amountError: "Please enter a valid amount (greater than 0).",
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
        "Promotional Materials"
      ]
    },
    RU: {
      title: "💼 Оплата Услуг",
      selectService: "Выберите услугу:",
      selectPlaceholder: "-- Выберите услугу --",
      enterAmount: "Введите сумму",
      amountPlaceholder: "Например: 500",
      payButton: "💳 Оплатить через PayPal",
      serviceError: "Пожалуйста, выберите услугу.",
      amountError: "Пожалуйста, введите действительную сумму (больше 0).",
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
        "Промо-материалы"
      ]
    }
  };

  const content = services[language];

  const handleSubmit = (event: React.FormEvent) => {
    let valid = true;

    // Validate service
    if (!selectedService) {
      setServiceError(true);
      valid = false;
    } else {
      setServiceError(false);
    }

    // Validate amount
    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      setAmountError(true);
      valid = false;
    } else {
      setAmountError(false);
    }

    if (!valid) {
      event.preventDefault();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="paypal-overlay">
      <div className="paypal-modal">
        <button className="paypal-close" onClick={onClose}>×</button>
        
        <form 
          action="https://www.paypal.com/cgi-bin/webscr" 
          method="post" 
          target="_blank"
          onSubmit={handleSubmit}
          className="paypal-form"
        >
          <input type="hidden" name="cmd" value="_xclick" />
          <input type="hidden" name="business" value="digitalgrow.moldova@gmail.com" />
          <input type="hidden" name="currency_code" value={currency} />

          <h2 className="paypal-title">{content.title}</h2>

          {/* Service Selection */}
          <label htmlFor="service" className="paypal-label">
            {content.selectService}
          </label>
          <select 
            name="item_name" 
            id="service" 
            required
            value={selectedService}
            onChange={(e) => setSelectedService(e.target.value)}
            className="paypal-select"
          >
            <option value="">{content.selectPlaceholder}</option>
            {content.services.map((service, index) => (
              <option key={index} value={service}>{service}</option>
            ))}
          </select>
          {serviceError && (
            <div className="paypal-error">{content.serviceError}</div>
          )}

          {/* Amount Input */}
          <label htmlFor="amount" className="paypal-label">
            {content.enterAmount} ({currency}):
          </label>
          <input 
            type="number" 
            name="amount" 
            id="amount" 
            min="1" 
            step="0.01" 
            required
            placeholder={content.amountPlaceholder}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="paypal-input"
          />
          {amountError && (
            <div className="paypal-error">{content.amountError}</div>
          )}

          {/* PayPal Button */}
          <button type="submit" className="paypal-button">
            {content.payButton}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PayPalPayment;