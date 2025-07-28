import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from '../src/pages/HomePage'
import './index.css'
import ServicesPage from './pages/ServicesPage'
import Portfolio from './pages/Potrfolio'
import AboutUsPage from './pages/AboutUsPage'
import ContactsPage from './pages/ContactsPage'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/aboutus" element={<AboutUsPage />} />
          <Route path="/contacts" element={<ContactsPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App