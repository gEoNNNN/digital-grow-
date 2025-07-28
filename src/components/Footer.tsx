import React from 'react'
import './Footer.css'
import facebook from '../assets/facebook.svg'
import linkedin from '../assets/li.svg'
import telegram from '../assets/telegram.svg'
import wa from "../assets/wa.svg"
import instagram from '../assets/insta.svg'
import tiktok from "../assets/tt.svg"
import viber from "../assets/viber.svg"

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
  const currentLanguage: LanguageCode = 'RO'

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
      description: 'Stay connected with DigitalGrow for ideas, projects and digital news.',
      contacte: 'Contact',
      srl: "DigitalGrow S.R.L.",
      email: "digitalgrow.moldova@gmail.com",
      copyright: '© 2025 DigitalGrow. All rights reserved.',
      navbar: "Quick navigation",
      nav1: "Home",
      nav2: "Services",
      nav3: "Portfolio",
      nav4: "About us",
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

  const currentTranslations = footerTranslations[currentLanguage]

  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Left section - 60% (Social Media) */}
        <div className="footer-left">
          <h3 className="c">{currentTranslations.title}</h3>
          <p className="footer-description">{currentTranslations.description}</p>
          
          <div className="footer-social-icons">
            <a href="#" className="social-link">
              <img src={facebook} alt="Facebook" />
            </a>
            <a href="#" className="social-link">
              <img src={instagram} alt="Instagram" />
            </a>
            <a href="#" className="social-link">
              <img src={linkedin} alt="LinkedIn" />
            </a>
            <a href="#" className="social-link">
              <img src={telegram} alt="Telegram" />
            </a>
            <a href="#" className="social-link">
              <img src={tiktok} alt="TikTok" />
            </a>
            <a href="#" className="social-link">
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
              <li><a href="/">{currentTranslations.nav1}</a></li>
              <li><a href="/services">{currentTranslations.nav2}</a></li>
              <li><a href="/portfolio">{currentTranslations.nav3}</a></li>
              <li><a href="/about">{currentTranslations.nav4}</a></li>
              <li><a href="/contact">{currentTranslations.nav5}</a></li>
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