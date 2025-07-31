import React from 'react'
import './AboutUsPage.css'
import BG from "../assets/aboutus.mp4"
import Filter from "../assets/homepagefilter.png"
import NavBar from "../components/NavBar"
import Footer from "../components/Footer"
import aboutUsContent from "./AboutUsPage.json"
import aboutus1 from "../assets/aboutus1.jpg"
import aboutus2 from "../assets/aboutus2.jpg"
import aboutus3 from "../assets/aboutus3.jpg"
import icon1 from "../assets/icon1.svg"
import icon2 from "../assets/icon2.svg"
import icon3 from "../assets/icon3.svg"
import icon4 from "../assets/icon4.svg"
import icon5 from "../assets/icon5.svg"
import { useTheme } from "../components/ThemeContext";
import icon1Light from "../assets/icon1dark.svg"
import icon2Light from "../assets/icon2dark.svg"
import icon3Light from "../assets/icon3dark.svg"
import icon4Light from "../assets/icon4dark.svg"
import icon5Light from "../assets/icon5dark.svg"
import LiveChat from '../components/LiveChat'

const AboutUsPage: React.FC = () => {
  const currentLanguage = 'RO'
  const content = aboutUsContent[currentLanguage]
  const { theme } = useTheme();

  return (
    <div className="aboutus-page">
      <video className="background-video" autoPlay muted loop>
        <source src={BG} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <img src={Filter} alt="Filter overlay" className="video-filter" />
      <div className="aboutus-content">
        <div className="portfolio-bg-fade"></div>
        <LiveChat/>
        <NavBar/>
        <div className="aboutus-main-section">
          <h1 className="aboutus-main-section-title">
            {content.aboutus.title}
          </h1>
          <p className="aboutus-main-section-description">
            {content.aboutus.description}
          </p>
        </div>

        {/* Mission Section */}
        <div className="aboutus-section">
          <h2 className="aboutus-section-title1">{content.aboutus.missiontitle}</h2>
          <p className="aboutus-section-description">{content.aboutus.missiondescription}</p>
        </div>

        {/* Story Section */}
        <div className="aboutus-section">
          <h2 className="aboutus-section-title">{content.aboutus.section1title}</h2>
          
          {/* Story Item 1 - Image left, text right */}
          <div className="story-item">
            <div className="story-image">
              <img src={aboutus1} alt="DigitalGrow Story 1" />
            </div>
            <div className="story-text">
              <p>{content.aboutus.section1description1}</p>
            </div>
          </div>

          {/* Story Item 2 - Text left, image right */}
          <div className="story-item story-item-reverse">
            <div className="story-image">
              <img src={aboutus2} alt="DigitalGrow Story 2" />
            </div>
            <div className="story-text">
              <p>{content.aboutus.section1description2}</p>
            </div>
          </div>

          {/* Story Item 3 - Image left, text right */}
          <div className="story-item">
            <div className="story-image">
              <img src={aboutus3} alt="DigitalGrow Story 3" />
            </div>
            <div className="story-text">
              <p>{content.aboutus.section1description3}</p>
            </div>
          </div>
        </div>

        {/* Icons Section */}
        <div className="aboutus-section">
          <div className="aboutus-icons">
            <div className="aboutus-icon">
              <img src={theme === "light" ? icon1Light : icon1} alt="Digital" />
              <p>{content.aboutus.icon1}</p>
            </div>
            <div className="aboutus-icon">
              <img src={theme === "light" ? icon2Light : icon2} alt="Creștere" />
              <p>{content.aboutus.icon2}</p>
            </div>
            <div className="aboutus-icon">
              <img src={theme === "light" ? icon3Light : icon3} alt="Design" />
              <p>{content.aboutus.icon3}</p>
            </div>
            <div className="aboutus-icon">
              <img src={theme === "light" ? icon4Light : icon4} alt="Parteneriat" />
              <p>{content.aboutus.icon4}</p>
            </div>
            <div className="aboutus-icon">
              <img src={theme === "light" ? icon5Light : icon5} alt="Strategie" />
              <p>{content.aboutus.icon5}</p>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="aboutus-section">
          <div className="aboutus-stats">
            <div className="aboutus-stat">
              <div className="stat-value">{content.aboutus.item1value}</div>
              <div className="stat-label">{content.aboutus.item1list}</div>
            </div>
            <div className="aboutus-stat">
              <div className="stat-value">{content.aboutus.item2value}</div>
              <div className="stat-label">{content.aboutus.item2list}</div>
            </div>
            <div className="aboutus-stat">
              <div className="stat-value">{content.aboutus.item3value}</div>
              <div className="stat-label">{content.aboutus.item3list}</div>
            </div>
          </div>
        </div>

        <Footer />
      </div>
    </div>
  )
}

export default AboutUsPage