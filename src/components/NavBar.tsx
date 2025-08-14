import { useState } from 'react'
import { Link } from 'react-router-dom'
import './Navbar.css'
import logo from "../assets/logo.svg"
import darkmodeicon from "../assets/darknomeicon.svg"
import lightmodeicon from "../assets/darkmodeicon.svg"
import bg from "../assets/navbarfilter.png"
import hamburgerIcon from "../assets/hamburger.svg" // Add a hamburger icon SVG to your assets
import { useTheme } from "./ThemeContext";
import { useLanguage } from "./LanguageContext";

type LanguageCode = 'RO' | 'EN' | 'RU'

interface Language {
  code: LanguageCode
  name: string
}

interface Translations {
  home: string
  services: string
  portfolio: string
  about: string
  contact: string
  education: string
}

const NavBar = () => {
  //const [currentLanguage, setCurrentLanguage] = useState<LanguageCode>('RO')
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false)
  const { toggleTheme, theme } = useTheme();
  const { language, setLanguage } = useLanguage();

  const languages: Record<LanguageCode, Language> = {
    RO: { code: 'RO', name: 'Română' },
    EN: { code: 'EN', name: 'English' },
    RU: { code: 'RU', name: 'Русский' }
  }

  const translations: Record<LanguageCode, Translations> = {
    RO: {
      home: 'Acasa',
      services: 'Servicii',
      portfolio: 'Portofoliu',
      about: 'Despre noi',
      contact: 'Contacte',
      education: 'Educație'
    },
    EN: {
      home: 'Home',
      services: 'Services',
      portfolio: 'Portfolio',
      about: 'About us',
      contact: 'Contact',
      education: 'Education'
    },
    RU: {
      home: 'Главная',
      services: 'Услуги',
      portfolio: 'Портфолио',
      about: 'О нас',
      contact: 'Контакты',
      education: 'Образование'
    }
  }

  const currentLanguage = language;

  const handleLanguageChange = (langCode: LanguageCode): void => {
    setLanguage(langCode);
    setIsDropdownOpen(false);
    
    // Close mobile menu after 0.5 seconds if it's open
    if (mobileMenuOpen) {
      setTimeout(() => {
        setMobileMenuOpen(false);
      }, 500);
    }
  };

  const handleThemeToggle = (): void => {
    toggleTheme();
    
    // Close mobile menu after 0.5 seconds if it's open
    if (mobileMenuOpen) {
      setTimeout(() => {
        setMobileMenuOpen(false);
      }, 500);
    }
  };

  const currentTranslations = translations[currentLanguage]

  return (
    <nav className="navbar" style={{ backgroundImage: `url(${bg})` }}>
      <div className="navbar-container">
        <a href="#" className="navbar-logo">
          <img src={logo} alt="Logo"/>
        </a>
        {/* Hamburger icon for mobile */}
        <button
          className="navbar-hamburger"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <img src={hamburgerIcon} alt="Menu" />
        </button>
        <ul className={`navbar-menu${mobileMenuOpen ? ' open' : ''}`}>
          {mobileMenuOpen && (
            <li className="navbar-close-x">
              <button
                className="navbar-close-x-btn"
                onClick={() => setMobileMenuOpen(false)}
                aria-label="Close menu"
              >
                ×
              </button>
            </li>
          )}
          <li className="navbar-item">
            <Link to="/" className="navbar-link">
              {currentTranslations.home}
            </Link>
          </li>
          <li className="navbar-item">
            <Link to="/services" className="navbar-link">
              {currentTranslations.services}
            </Link>
          </li>
          <li className="navbar-item">
            <Link to="/portfolio" className="navbar-link">
              {currentTranslations.portfolio}
            </Link>
          </li>
          <li className="navbar-item">
            <Link to="/education" className="navbar-link">
              {currentTranslations.education}
            </Link>
          </li>
          <li className="navbar-item">
            <Link to="/aboutus" className="navbar-link">
              {currentTranslations.about}
            </Link>
          </li>
          <li className="navbar-item">
            <Link to="/contacts" className="navbar-link">
              {currentTranslations.contact}
            </Link>
          </li>
          <li className="navbar-item language-dropdown">
            <button 
              className="navbar-link language-button"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              {currentLanguage} ▼
            </button>
            {isDropdownOpen && (
              <div className="dropdown-menu">
                {Object.values(languages).map((lang) => (
                  <button
                    key={lang.code}
                    className={`dropdown-item ${currentLanguage === lang.code ? 'active' : ''}`}
                    onClick={() => handleLanguageChange(lang.code)}
                  >
                    {lang.code} - {lang.name}
                  </button>
                ))}
              </div>
            )}
          </li>
          {/* NEW: Theme toggle button for mobile menu */}
          {mobileMenuOpen && (
            <li className="navbar-item">
              <button
                className="navbar-theme-mobile"
                onClick={handleThemeToggle}
                aria-label="Toggle theme"
              >
                <img src={theme === "light" ? lightmodeicon : darkmodeicon} alt="Toggle theme" />
              </button>
            </li>
          )}
        </ul>
        {/* Desktop theme button (remains outside the menu) */}
        <button className="navbar-theme" onClick={toggleTheme} aria-label="Toggle theme">
          <img src={theme === "light" ? lightmodeicon : darkmodeicon} alt="Toggle theme" />
        </button>
      </div>
    </nav>
  )
}

export default NavBar
