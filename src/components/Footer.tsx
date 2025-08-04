import React from 'react'
import './Footer.css'
import facebook from '../assets/facebook.svg'
import linkedin from '../assets/li.svg'
import telegram from '../assets/telegram.svg'
import wa from "../assets/wa.svg"
import instagram from '../assets/insta.svg'
import tiktok from "../assets/tt.svg"
import viber from "../assets/viber.svg"
import { useNavigate } from "react-router-dom"
import { useLanguage } from "./LanguageContext"

type LanguageCode = 'RO' | 'EN' | 'RU'

interface FooterTranslations {
  title: string
  description: string
  contacte: string
  srl: string
  email: string
  copyright: string
  navbar: string
  nav1: string
  nav2: string
  nav3: string
  nav4: string
  nav5: string
}

const Footer: React.FC = () => {
  const { language } = useLanguage();
  const navigate = useNavigate()

  const footerTranslations: Record<LanguageCode, FooterTranslations> = {
    RO: {
      title: 'Urmărește-ne și pe rețelele de socializare!',
      description: 'Rămâi conectat cu DigitalGrow pentru idei, proiecte și noutăți digitale.',
      contacte: 'Contact',
      srl: "DigitalGrow S.R.L.",
      email: "digitalgrow.moldova@gmail.com",
      copyright: '© 2025 DigitalGrow. Toate drepturile rezervate.',
      navbar: "Navigare rapidă",
      nav1: "Acasă",
      nav2: "Servicii",
      nav3: "Portofoliu",
      nav4: "Despre noi",
      nav5: "Contact"
    },
    EN: {
      title: 'Follow us on social media!',
      description: 'Stay connected with DigitalGrow for fresh ideas, projects, and digital updates.',
      contacte: 'Contact',
      srl: "DigitalGrow S.R.L.",
      email: "digitalgrow.moldova@gmail.com",
      copyright: '© 2025 DigitalGrow. All rights reserved.',
      navbar: "Quick Navigation",
      nav1: "Home",
      nav2: "Services",
      nav3: "Portfolio",
      nav4: "About Us",
      nav5: "Contact"
    },
    RU: {
      title: 'Следуйте за нами в социальных сетях!',
      description: 'Оставайтесь на связи с DigitalGrow для идей, проектов и цифровых новостей.',
      contacte: 'Контакты',
      srl: "DigitalGrow S.R.L.",
      email: "digitalgrow.moldova@gmail.com",
      copyright: '© 2025 DigitalGrow. Все права защищены.',
      navbar: "Быстрая навигация",
      nav1: "Главная",
      nav2: "Услуги",
      nav3: "Портфолио",
      nav4: "О нас",
      nav5: "Контакты"
    }
  }

  const currentTranslations = footerTranslations[language]; // <-- use context language

  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Left section - 60% (Social Media) */}
        <div className="footer-left">
          <h3 className="footer-title">{currentTranslations.title}</h3>
          <p className="footer-description">{currentTranslations.description}</p>
          
          <div className="footer-social-icons">
            <a href="https://www.facebook.com/profile.php?id=61577024783785" className="social-link">
              <img src={facebook} alt="Facebook" />
            </a>
            <a href="https://www.instagram.com/digitalgrowmoldova/" className="social-link">
              <img src={instagram} alt="Instagram" />
            </a>
            <a href="https://www.linkedin.com/in/digital-grow-989768378/" className="social-link">
              <img src={linkedin} alt="LinkedIn" />
            </a>
            <a href="https://telegram.org/" className="social-link">
              <img src={telegram} alt="Telegram" />
            </a>
            <a href="https://www.tiktok.com/@digital.grow1" className="social-link">
              <img src={tiktok} alt="TikTok" />
            </a>
            <a href="https://api.whatsapp.com/qr/GLN7BY6EENJQH1?autoload=1&app_absent=0" className="social-link">
              <img src={wa} alt="WhatsApp" />
            </a>
            <a href="#" className="social-link">
              <img src={viber} alt="Viber" />
            </a>
          </div>

          <div className="footer-contact-info">
            <h4 className="footer-contact-title">{currentTranslations.contacte}</h4>
            <p className="footer-srl">{currentTranslations.srl}</p>
            <p className="footer-email">{currentTranslations.email}</p>
          </div>
        </div>

        {/* Right section - 40% (Navigation) */}
        <div className="footer-right">
          <h4 className="footer-nav-title">{currentTranslations.navbar}</h4>
          <nav className="footer-navigation">
            <ul className="footer-nav-list">
              <li>
                <button type="button" onClick={() => navigate("/")}>
                  {currentTranslations.nav1}
                </button>
              </li>
              <li>
                <button type="button" onClick={() => navigate("/services")}>
                  {currentTranslations.nav2}
                </button>
              </li>
              <li>
                <button type="button" onClick={() => navigate("/portfolio")}>
                  {currentTranslations.nav3}
                </button>
              </li>
              <li>
                <button type="button" onClick={() => navigate("/aboutus")}>
                  {currentTranslations.nav4}
                </button>
              </li>
              <li>
                <button type="button" onClick={() => navigate("/contacts")}>
                  {currentTranslations.nav5}
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p className="footer-copyright">{currentTranslations.copyright}</p>
      </div>
    </footer>
  )
}

export default Footer