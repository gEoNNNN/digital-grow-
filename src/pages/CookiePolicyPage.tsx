import { useLanguage } from '../components/LanguageContext';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import cookieContent from './CookiePolicyPage.json';
import './CookiePolicyPage.css';

const CookiePolicyPage = () => {
  const { language } = useLanguage();
  const content = cookieContent[language as keyof typeof cookieContent];

  // Add error handling in case content is undefined
  if (!content) {
    return (
      <div className="cookie-policy-page">
        <NavBar />
        <div className="cookie-policy-container">
          <div className="cookie-policy-content">
            <h1>Cookie Policy</h1>
            <p>Content not available for this language.</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="cookie-policy-page">
      <NavBar />
      
      <div className="cookie-policy-container">
        <div className="cookie-policy-content">
          <h1 className="cookie-policy-title">{content.title}</h1>
          <p className="cookie-policy-last-updated">{content.lastUpdated}</p>
          
          <div className="cookie-policy-intro">
            <p>{content.intro}</p>
          </div>

          {/* What are cookies Section */}
          <section className="cookie-policy-section">
            <h2>{content.whatAreCookies.title}</h2>
            <p>{content.whatAreCookies.description}</p>
            <ul>
              {content.whatAreCookies.types.map((type, index) => (
                <li key={index}>{type}</li>
              ))}
            </ul>
          </section>

          {/* Cookie Types Section */}
          <section className="cookie-policy-section">
            <h2>{content.cookieTypes.title}</h2>
            
            {/* Necessary Cookies */}
            <div className="cookie-type-subsection">
              <h3>{content.cookieTypes.necessary.title}</h3>
              <p>{content.cookieTypes.necessary.description}</p>
              <ul>
                {content.cookieTypes.necessary.examples.map((example, index) => (
                  <li key={index}>{example}</li>
                ))}
              </ul>
            </div>

            {/* Analytical Cookies */}
            <div className="cookie-type-subsection">
              <h3>{content.cookieTypes.analytical.title}</h3>
              <p>{content.cookieTypes.analytical.description}</p>
              <ul>
                {content.cookieTypes.analytical.examples.map((example, index) => (
                  <li key={index}>{example}</li>
                ))}
              </ul>
            </div>

            {/* Functional Cookies */}
            <div className="cookie-type-subsection">
              <h3>{content.cookieTypes.functional.title}</h3>
              <p>{content.cookieTypes.functional.description}</p>
              <ul>
                {content.cookieTypes.functional.examples.map((example, index) => (
                  <li key={index}>{example}</li>
                ))}
              </ul>
            </div>
          </section>

          {/* Control Section */}
          <section className="cookie-policy-section">
            <h2>{content.control.title}</h2>
            <p>{content.control.description}</p>
            <ul>
              {content.control.methods.map((method, index) => (
                <li key={index}>{method}</li>
              ))}
            </ul>
            <div className="cookie-browser-instructions">
              <p><strong>{content.control.browserInstructions}</strong></p>
            </div>
          </section>

          {/* Consent Section */}
          <section className="cookie-policy-section">
            <h2>{content.consent.title}</h2>
            <p>{content.consent.description}</p>
            <ul>
              {content.consent.rights.map((right, index) => (
                <li key={index}>{right}</li>
              ))}
            </ul>
          </section>

          {/* Contact Section */}
          <section className="cookie-policy-section">
            <h2>{content.contact.title}</h2>
            <p>{content.contact.description}</p>
            <div className="cookie-policy-contact">
              <p><strong>{content.contact.company}</strong></p>
              <p>{content.contact.email}</p>
              <p>{content.contact.phone}</p>
            </div>
          </section>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default CookiePolicyPage;