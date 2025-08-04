import { useLanguage } from '../components/LanguageContext';
import NavBar from '../components/NavBar';
import Footer from '../components/Footer';
import privacyContent from './PrivacyPolicyPage.json';
import './PrivacyPolicyPage.css';

const PrivacyPolicyPage = () => {
  const { language } = useLanguage();
  const content = privacyContent[language];

  return (
    <div className="privacy-policy-page">
      <NavBar />
      
      <div className="privacy-policy-container">
        <div className="privacy-policy-content">
          <h1 className="privacy-policy-title">{content.title}</h1>
          <p className="privacy-policy-last-updated">{content.lastUpdated}</p>
          
          <div className="privacy-policy-intro">
            <p>{content.intro}</p>
          </div>

          {/* Data Collected Section */}
          <section className="privacy-policy-section">
            <h2>{content.dataCollected.title}</h2>
            <p>{content.dataCollected.description}</p>
            <ul>
              {content.dataCollected.types.map((type, index) => (
                <li key={index}>{type}</li>
              ))}
            </ul>
          </section>

          {/* Purpose Section */}
          <section className="privacy-policy-section">
            <h2>{content.purpose.title}</h2>
            <p>{content.purpose.description}</p>
            <ul>
              {content.purpose.purposes.map((purpose, index) => (
                <li key={index}>{purpose}</li>
              ))}
            </ul>
          </section>

          {/* Legal Basis Section */}
          <section className="privacy-policy-section">
            <h2>{content.legalBasis.title}</h2>
            <p>{content.legalBasis.description}</p>
            <ul>
              {content.legalBasis.bases.map((basis, index) => (
                <li key={index}>{basis}</li>
              ))}
            </ul>
          </section>

          {/* Disclosure Section */}
          <section className="privacy-policy-section">
            <h2>{content.disclosure.title}</h2>
            <p>{content.disclosure.description}</p>
            <ul>
              {content.disclosure.parties.map((party, index) => (
                <li key={index}>{party}</li>
              ))}
            </ul>
          </section>

          {/* Protection Section */}
          <section className="privacy-policy-section">
            <h2>{content.protection.title}</h2>
            <p>{content.protection.description}</p>
            <ul>
              {content.protection.measures.map((measure, index) => (
                <li key={index}>{measure}</li>
              ))}
            </ul>
          </section>

          {/* Retention Section */}
          <section className="privacy-policy-section">
            <h2>{content.retention.title}</h2>
            <p>{content.retention.description}</p>
            <ul>
              {content.retention.periods.map((period, index) => (
                <li key={index}>{period}</li>
              ))}
            </ul>
          </section>

          {/* User Rights Section */}
          <section className="privacy-policy-section">
            <h2>{content.rights.title}</h2>
            <p>{content.rights.description}</p>
            <ul>
              {content.rights.userRights.map((right, index) => (
                <li key={index}>{right}</li>
              ))}
            </ul>
          </section>

          {/* Contact Section */}
          <section className="privacy-policy-section">
            <h2>{content.contact.title}</h2>
            <p>{content.contact.description}</p>
            <div className="privacy-policy-contact">
              <p><strong>{content.contact.company}</strong></p>
              <p>{content.contact.email}</p>
              <p>{content.contact.phone}</p>
              <p>{content.contact.dpo}</p>
            </div>
          </section>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default PrivacyPolicyPage;