import { useLanguage } from '../components/LanguageContext';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import termsContent from './TermsAndConditionsPage.json';
import './TermsAndConditionsPage.css';

const TermsAndConditionsPage = () => {
  const { language } = useLanguage();
  const content = termsContent[language as keyof typeof termsContent];

  return (
    <div className="terms-page">
      <NavBar />
      
      <div className="terms-container">
        <div className="terms-content">
          <h1 className="terms-title">{content.title}</h1>
          <p className="terms-last-updated">{content.lastUpdated}</p>
          
          <div className="terms-intro">
            <p>{content.intro}</p>
          </div>

          {/* Acceptance Section */}
          <section className="terms-section">
            <h2>{content.acceptance.title}</h2>
            <p>{content.acceptance.description}</p>
            <ul>
              {content.acceptance.terms.map((term, index) => (
                <li key={index}>{term}</li>
              ))}
            </ul>
          </section>

          {/* Payments Section */}
          <section className="terms-section">
            <h2>{content.payments.title}</h2>
            <p>{content.payments.description}</p>
            <ul>
              {content.payments.methods.map((method, index) => (
                <li key={index}>{method}</li>
              ))}
            </ul>
            
            <div className="terms-subsection">
              <h3>{content.payments.terms.title}</h3>
              <ul>
                {content.payments.terms.conditions.map((condition, index) => (
                  <li key={index}>{condition}</li>
                ))}
              </ul>
            </div>
          </section>

          {/* Refunds Section */}
          <section className="terms-section">
            <h2>{content.refunds.title}</h2>
            <p>{content.refunds.description}</p>
            <ul>
              {content.refunds.policy.map((policy, index) => (
                <li key={index}>{policy}</li>
              ))}
            </ul>
            
            <div className="terms-subsection">
              <h3>{content.refunds.exceptions.title}</h3>
              <ul>
                {content.refunds.exceptions.cases.map((exception, index) => (
                  <li key={index}>{exception}</li>
                ))}
              </ul>
            </div>
          </section>

          {/* Liability Section */}
          <section className="terms-section">
            <h2>{content.liability.title}</h2>
            <p>{content.liability.description}</p>
            <ul>
              {content.liability.limitations.map((limitation, index) => (
                <li key={index}>{limitation}</li>
              ))}
            </ul>
            
            <div className="terms-subsection">
              <h3>{content.liability.warranties.title}</h3>
              <ul>
                {content.liability.warranties.items.map((warranty, index) => (
                  <li key={index}>{warranty}</li>
                ))}
              </ul>
            </div>
          </section>

          {/* Modifications Section */}
          <section className="terms-section">
            <h2>{content.modifications.title}</h2>
            <p>{content.modifications.description}</p>
            <ul>
              {content.modifications.process.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </section>

          {/* Contact Section */}
          <section className="terms-section">
            <h2>{content.contact.title}</h2>
            <p>{content.contact.description}</p>
            <div className="terms-contact">
              <p><strong>{content.contact.company}</strong></p>
              <p>{content.contact.email}</p>
              <p>{content.contact.phone}</p>
              <p>{content.contact.legal}</p>
            </div>
          </section>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default TermsAndConditionsPage;