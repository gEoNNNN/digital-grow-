import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from '../src/pages/HomePage'
import './index.css'
import ServicesPage from './pages/ServicesPage'
import Portfolio from './pages/Potrfolio'
import AboutUsPage from './pages/AboutUsPage'
import ContactsPage from './pages/ContactsPage'
import ScrollToTop from '../src/components/Scroll'
import Picolino from './pages/Picolino'
import Krov from './pages/Krov'
import LumeaTa from './pages/LumeaTa'
import { ThemeProvider } from "./components/ThemeContext";
import Inwork from './pages/Inwork'
import { LanguageProvider } from "./components/LanguageContext"
import PrivacyPolicyPage from './pages/PrivacyPolicyPage'
import CookiePolicyPage from './pages/CookiePolicyPage';
import TermsAndConditionsPage from './pages/TermsAndConditionsPage';
import CookieBanner from './components/CookieBanner';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="App">
          <ScrollToTop />
          <LanguageProvider>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/services" element={<ServicesPage />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/aboutus" element={<AboutUsPage />} />
              <Route path="/contacts" element={<ContactsPage />} />
              <Route path="/picolino" element={<Picolino />} />
              <Route path="/krov" element={<Krov />} />
              <Route path="/lumeata" element={<LumeaTa />} />
              <Route path="/inwork" element={<Inwork />} />
              <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
              <Route path="/cookie-policy" element={<CookiePolicyPage />} />
              <Route path="/terms-and-conditions" element={<TermsAndConditionsPage />} />
            </Routes>
            <CookieBanner />
          </LanguageProvider>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App