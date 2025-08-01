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

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="App">
          <ScrollToTop />
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
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App