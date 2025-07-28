import React from 'react'
import './ServicesPage.css'
import BG from "../assets/services.mp4"
import Filter from "../assets/homepagefilter.png"
import NavBar from "../components/NavBar"
import Footer from "../components/Footer"
import servicesContent from "./ServicesPage.json"
import NextLevelSection from '../components/NextLevel'

const ServicesPage: React.FC = () => {
  const currentLanguage = 'RO'
  const content = servicesContent[currentLanguage]

  return (
    <div className="services-page">
      <video className="background-video" autoPlay muted loop>
        <source src={BG} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <img src={Filter} alt="Filter overlay" className="video-filter" />
      <div className="services-content">
        <div className="portfolio-bg-fade"></div>
        <NavBar/>
        <div className="services-main-section">
          <h1 className="services-main-section-title">
            {content.services.title}
          </h1>
          <p className="services-main-section-description">
            {content.services.description}
          </p>
          
          <div className="services-buttons">
            <button className="services-button">
              {content.services.button1}
            </button>
            <button className="services-button">
              {content.services.button2}
            </button>
            <button className="services-button">
              {content.services.button3}
            </button>
            <button className="services-button">
              {content.services.button4}
            </button>
          </div>
        </div>

        {/* Section One - Web Development */}
        <div className="services-section">
          <h2 className="services-section-title" dangerouslySetInnerHTML={{ __html: content.services.sectiononetitle }}></h2>
          <p className="services-section-description">{content.services.sectiononedescription}</p>
          
          <div className="services-cards">
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard1title}</h3>
              <p className="services-card-description">{content.services.sectiononecard1description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard1statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard2title}</h3>
              <p className="services-card-description">{content.services.sectiononecard2description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard2statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard3title}</h3>
              <p className="services-card-description">{content.services.sectiononecard3description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard3statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard4title}</h3>
              <p className="services-card-description">{content.services.sectiononecard4description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard4statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiononecard5title}</h3>
              <p className="services-card-description">{content.services.sectiononecard5description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiononecard5statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>
          </div>
        </div>

        {/* Section Two - Chatbot & AI */}
        <div className="services-section">
          <h2 className="services-section-title" dangerouslySetInnerHTML={{ __html: content.services.sectiontwotitle }}></h2>
          <p className="services-section-description">{content.services.sectiontwodescription}</p>
          
          <div className="services-cards">
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard1title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard1description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard1statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard2title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard2description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard2statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard3title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard3description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard3statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard4title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard4description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard4statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectiontwocard5title}</h3>
              <p className="services-card-description">{content.services.sectiontwocard5description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectiontwocard5statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>
          </div>
        </div>

        {/* Section Three - Branding & Design */}
        <div className="services-section">
          <h2 className="services-section-title" dangerouslySetInnerHTML={{ __html: content.services.sectionthreetitle }} ></h2>
          <p className="services-section-description">{content.services.sectionthreedescription}</p>
          
          <div className="services-cards">
            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectionthreecard1title}</h3>
              <p className="services-card-description">{content.services.sectionthreecard1description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectionthreecard1statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectionthreecard2title}</h3>
              <p className="services-card-description">{content.services.sectionthreecard2description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectionthreecard2statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectionthreecard3title}</h3>
              <p className="services-card-description">{content.services.sectionthreecard3description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectionthreecard3statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>

            <div className="services-card">
              <h3 className="services-card-title">{content.services.sectionthreecard4title}</h3>
              <p className="services-card-description">{content.services.sectionthreecard4description}</p>
              <div className="services-card-statement">
                <span className="checkmark">✓</span>
                <span>{content.services.sectionthreecard4statement}</span>
              </div>
              <button className="services-card-button">{content.services.cardbutton}</button>
            </div>
          </div>
        </div>

        {/* Section Four - Package Offers */}
        <div className="services-section">
          <h2 className="services-section-title">{content.services.sectionfourtitle}</h2>
          
          <div className="package-cards">
            {/* Package Card 1 - Startup Light */}
            <div className="package-card">
              <h3 className="package-card-title">{content.services.sectionfourcard1title}</h3>
              
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
                <div className="package-price1">
                  {content.services.sectionfourcard1price}
                  <span className="package-price-currency"> MDL</span>
                </div>
                <div className="package-discount1">{content.services.sectionfourcard1discount}</div>
              </div>

              <button className="package-card-button">{content.services.sectionfourcardbutton}</button>
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
                <div className="package-price2">
                  {content.services.sectionfourcard2price}
                  <span className="package-price-currency"> MDL</span>
                </div>
                <div className="package-discount2">{content.services.sectionfourcard2discount}</div>
              </div>

              <button className="package-card-button">{content.services.sectionfourcardbutton}</button>
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
                <div className="package-price3">
                  {content.services.sectionfourcard3price}
                  <span className="package-price-currency"> MDL</span>
                </div>
                <div className="package-discount3">{content.services.sectionfourcard3discount}</div>
              </div>

              <button className="package-card-button">{content.services.sectionfourcardbutton}</button>
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