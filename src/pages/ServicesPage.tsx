import React, { useState, useRef } from 'react'
import './ServicesPage.css'
import BG from "../assets/services.mp4"
import Filter from "../assets/homepagefilter.png"
import NavBar from "../components/NavBar"
import Footer from "../components/Footer"
import servicesContent from "./ServicesPage.json"
import NextLevelSection from '../components/NextLevel'
import LiveChat from '../components/LiveChat'
import PayPalPayment from '../components/PayPal'
import { useLanguage } from "../components/LanguageContext";
import { useNavigate } from "react-router-dom";
import shape1 from "../assets/Ellipse 1.png"
import shape2 from "../assets/Ellipse 2.png"
import shape3 from "../assets/Ellipse 3.png"

const ServicesPage: React.FC = () => {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const content = servicesContent[language];
  const [chatOpen, setChatOpen] = useState(false)
  const [paypalOpen, setPaypalOpen] = useState(false)
  const [selectedService, setSelectedService] = useState('')
  const [selectedPrice, setSelectedPrice] = useState('')

  // Create refs for each first card title
  const sectionOneCardTitleRef = useRef<HTMLHeadingElement>(null) as React.RefObject<HTMLHeadingElement>
  const sectionTwoCardTitleRef = useRef<HTMLHeadingElement>(null) as React.RefObject<HTMLHeadingElement>
  const sectionThreeCardTitleRef = useRef<HTMLHeadingElement>(null) as React.RefObject<HTMLHeadingElement>
  const sectionFourCardTitleRef = useRef<HTMLHeadingElement>(null) as React.RefObject<HTMLHeadingElement>

  // Scroll handler
  const handleScrollToCardTitle = (ref: React.RefObject<HTMLHeadingElement>) => {
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  // Helper for currency
  const currency = language === "EN" ? "EUR" : "MDL";

  // Handle buy button click
  const handleBuyClick = (serviceName: string, price: string) => {
    setSelectedService(serviceName)
    setSelectedPrice(price.replace(/[^\d]/g, '')) // Remove non-numeric characters
    setPaypalOpen(true)
  }

  // Education button text based on language
  const getEducationButtonText = () => {
    switch(language) {
      case 'RO':
        return 'Educație';
      case 'EN':
        return 'Education';
      case 'RU':
        return 'Образование';
      default:
        return 'Educație';
    }
  }

  return (
    <div className="services-page">
      <video className="background-video" autoPlay muted loop>
        <source src={BG} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <img src={Filter} alt="Filter overlay" className="video-filter" />
      <div className="services-content">
        <LiveChat open={chatOpen} setOpen={setChatOpen} />
        <PayPalPayment 
          isOpen={paypalOpen} 
          onClose={() => setPaypalOpen(false)}
          serviceName={selectedService}
          servicePrice={selectedPrice}
          currency={currency}
        />
        <NavBar/>
        <div className="services-main-section">
          <h1 className="services-main-section-title">
            {content.services.title}
          </h1>
          <p className="services-main-section-description">
            {content.services.description}
          </p>
          <div className="services-buttons">
            <button className="services-button" onClick={() => handleScrollToCardTitle(sectionOneCardTitleRef)}>
              {content.services.button1}
            </button>
            <button className="services-button" onClick={() => handleScrollToCardTitle(sectionTwoCardTitleRef)}>
              {content.services.button2}
            </button>
            <button className="services-button" onClick={() => handleScrollToCardTitle(sectionThreeCardTitleRef)}>
              {content.services.button3}
            </button>
            <button className="services-button" onClick={() => handleScrollToCardTitle(sectionFourCardTitleRef)}>
              {content.services.button4}
            </button>
            <button className="services-button" onClick={() => navigate('/education')}>
              {getEducationButtonText()}
            </button>
          </div>
        </div>

        {/* Section One - Web Development */}
        <div className='services-content'>
        <div className="services-section1">
          <img src={shape1} className='services-shape1' />
          <img src={shape2} className='services-shape2' />
          <img src={shape3} className='services-shape3' />
          <h2 className="services-section-title" dangerouslySetInnerHTML={{ __html: content.services.sectiononetitle }}></h2>
          <p className="services-section-description">{content.services.sectiononedescription}</p>
          <div className="services-cards">
            {/* Card 1 */}
            <div className="services-card">
              <h3 className="services-card-title" ref={sectionOneCardTitleRef}>
                {content.services.sectiononecard1title}
              </h3>
              <p className="services-card-description">{content.services.sectiononecard1description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard1statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiononecard1title, content.services.sectiononecard1price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiononecard1pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiononecard1price} {currency}</span>
              </div>
            </div>
            {/* Card 2 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard2title}</h3>
              <p className="services-card-description">{content.services.sectiononecard2description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard2statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiononecard2title, content.services.sectiononecard2price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiononecard2pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiononecard2price} {currency}</span>
              </div>
            </div>
            {/* Card 3 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard3title}</h3>
              <p className="services-card-description">{content.services.sectiononecard3description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard3statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiononecard3title, content.services.sectiononecard3price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiononecard3pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiononecard3price} {currency}</span>
              </div>
            </div>
            {/* Card 4 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard4title}</h3>
              <p className="services-card-description">{content.services.sectiononecard4description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard4statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiononecard4title, content.services.sectiononecard4price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiononecard4pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiononecard4price} {currency}</span>
              </div>
            </div>
            {/* Card 5 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard5title}</h3>
              <p className="services-card-description">{content.services.sectiononecard5description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard5statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiononecard5title, content.services.sectiononecard5price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiononecard5pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiononecard5price} {currency}</span>
              </div>
            </div>
          </div>
        </div>
        </div>

        {/* Section Two - Chatbot & AI */}
        <div className="services-section">
          <img src={shape1} className='services-shape1' />
          <img src={shape2} className='services-shape2' />
          <img src={shape3} className='services-shape3' />
          <h2 className="services-section-title" dangerouslySetInnerHTML={{ __html: content.services.sectiontwotitle }}></h2>
          <p className="services-section-description">{content.services.sectiontwodescription}</p>
          <div className="services-cards">
            {/* Card 1 */}
            <div className="services-card">
              <h3 className="services-card-title" ref={sectionTwoCardTitleRef}>
                {content.services.sectiontwocard1title}
              </h3>
              <p className="services-card-description">{content.services.sectiontwocard1description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard1statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiontwocard1title, content.services.sectiontwocard1price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiontwocard1pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiontwocard1price} {currency}</span>
              </div>
            </div>
            {/* Card 2 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard2title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard2description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard2statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiontwocard2title, content.services.sectiontwocard2price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiontwocard2pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiontwocard2price} {currency}</span>
              </div>
            </div>
            {/* Card 3 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard3title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard3description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard3statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiontwocard3title, content.services.sectiontwocard3price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiontwocard3pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiontwocard3price} {currency}</span>
              </div>
            </div>
            {/* Card 4 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard4title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard4description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard4statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiontwocard4title, content.services.sectiontwocard4price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiontwocard4pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiontwocard4price} {currency}</span>
              </div>
            </div>
            {/* Card 5 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard5title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard5description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard5statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectiontwocard5title, content.services.sectiontwocard5price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectiontwocard5pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectiontwocard5price} {currency}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Section Three - Branding & Design */}
        <div className="services-section">
          <img src={shape1} className='services-shape1' />
          <img src={shape2} className='services-shape2' />
          <img src={shape3} className='services-shape3' />
          <h2 className="services-section-title" dangerouslySetInnerHTML={{ __html: content.services.sectionthreetitle }} ></h2>
          <p className="services-section-description">{content.services.sectionthreedescription}</p>
          <div className="services-cards">
            {/* Card 1 */}
            <div className="services-card">
              <h3 className="services-card-title" ref={sectionThreeCardTitleRef}>
                {content.services.sectionthreecard1title}
              </h3>
              <p className="services-card-description">{content.services.sectionthreecard1description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectionthreecard1statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectionthreecard1title, content.services.sectionthreecard1price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectionthreecard1pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectionthreecard1price} {currency}</span>
              </div>
            </div>

            {/* Card 2 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectionthreecard2title}</h3>
              <p className="services-card-description">{content.services.sectionthreecard2description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectionthreecard2statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectionthreecard2title, content.services.sectionthreecard2price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectionthreecard2pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectionthreecard2price} {currency}</span>
              </div>
            </div>

            {/* Card 3 */}
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectionthreecard3title}</h3>
              <p className="services-card-description">{content.services.sectionthreecard3description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectionthreecard3statement}</span>
              </div>
              <div className="services-card-action-row">
                <button 
                  className="services-card-button" 
                  onClick={() => handleBuyClick(content.services.sectionthreecard3title, content.services.sectionthreecard3price)}
                >
                  {content.services.cardbutton}
                </button>
                {language !== "EN" && (
                  <span className="services-card-price-strike-x">
                    <span className="services-card-price-strike-text">
                      {content.services.sectionthreecard3pricereal} {currency}
                    </span>
                  </span>
                )}
                <span className="services-card-price">{content.services.sectionthreecard3price} {currency}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Section Four - Packages */}
        <div className="services-section">
          <h2 className="services-section-title">{content.services.sectionfourtitle}</h2>
          <div className="package-cards">
            {/* Package Card 1 - Startup Light */}
            <div className="package-card">
              <h3 className="package-card-title" ref={sectionFourCardTitleRef}>
                {content.services.sectionfourcard1title}
              </h3>
              <div className="package-services">
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard1service1}</span>
                </div>
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard1service2}</span>
                </div>
              </div>
              <div className="package-pricing">
                <div
                  className={
                    "package-price1" +
                    (language === "EN"
                      ? " package-price1-en"
                      : language === "RU"
                      ? " package-price1-ru"
                      : "")
                  }
                >
                  {content.services.sectionfourcard1price}
                  <span className="package-price-currency"> {language === "EN" ? "EUR" : "MDL"}</span>
                </div>
                {language !== "EN" && (
                  <div className="package-discount1">{content.services.sectionfourcard1discount}</div>
                )}
              </div>
              <button 
                className="package-card-button" 
                onClick={() => handleBuyClick(content.services.sectionfourcard1title, content.services.sectionfourcard1price)}
              >
                {content.services.sectionfourcardbutton}
              </button>
            </div>

            {/* Package Card 2 - Business Smart */}
            <div className="package-card">
              <h3 className="package-card-title">{content.services.sectionfourcard2title}</h3>
              <div className="package-services">
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard2service1}</span>
                </div>
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard2service2}</span>
                </div>
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard2service3}</span>
                </div>
              </div>
              <div className="package-pricing">
                <div
                  className={
                    "package-price2" +
                    (language === "EN"
                      ? " package-price2-en"
                      : language === "RU"
                      ? " package-price2-ru"
                      : "")
                  }
                >
                  {content.services.sectionfourcard2price}
                  <span className="package-price-currency"> {language === "EN" ? "EUR" : "MDL"}</span>
                </div>
                {language !== "EN" && (
                  <div className="package-discount2">{content.services.sectionfourcard2discount}</div>
                )}
              </div>
              <button 
                className="package-card-button" 
                onClick={() => handleBuyClick(content.services.sectionfourcard2title, content.services.sectionfourcard2price)}
              >
                {content.services.sectionfourcardbutton}
              </button>
            </div>

            {/* Package Card 3 - Enterprise Complete */}
            <div className="package-card">
              <h3 className="package-card-title">{content.services.sectionfourcard3title}</h3>
              <div className="package-services">
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard3service1}</span>
                </div>
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard3service2}</span>
                </div>
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard3service3}</span>
                </div>
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard3service4}</span>
                </div>
                <div className="package-service">
                  <span className="checkmark">✓</span>
                  <span>{content.services.sectionfourcard3service5}</span>
                </div>
              </div>
              <div className="package-pricing">
                <div
                  className={
                    "package-price3" +
                    (language === "EN"
                      ? " package-price3-en"
                      : language === "RU"
                      ? " package-price3-ru"
                      : "")
                  }
                >
                  {content.services.sectionfourcard3price}
                  <span className="package-price-currency">
                    {language === "EN" ? " EUR" : " MDL"}
                  </span>
                </div>
                {language !== "EN" && (
                  <div className="package-discount3">{content.services.sectionfourcard3discount}</div>
                )}
              </div>
              <button 
                className="package-card-button" 
                onClick={() => handleBuyClick(content.services.sectionfourcard3title, content.services.sectionfourcard3price)}
              >
                {content.services.sectionfourcardbutton}
              </button>
            </div>
          </div>
        </div>
        <NextLevelSection
          title={content.services.sectionfourtitle1}
          buttonText={content.services.sectionfourbutton}
        />
        <Footer />
    </div>
    </div>
  )
}

export default ServicesPage