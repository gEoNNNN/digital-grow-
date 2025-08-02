import React, { useState, useEffect } from 'react'
import './Portfolio.css'
import BG from "../assets/0725.mp4"
import project1 from "../assets/picolinologo.svg"
import project2 from "../assets/krovlogo.svg"
import project3 from "../assets/lumetalogo.svg"
import Filter from "../assets/homepagefilter.png"
import line from "../assets/path.png"
import NavBar from "../components/NavBar"
import Footer from "../components/Footer"
import portfolioContent from "./Portfolio.json"
import { useNavigate } from "react-router-dom"
import LiveChat from "../components/LiveChat"
import Picolino from "./Picolino" // Import the component

const Portfolio: React.FC = () => {
  const [chatOpen, setChatOpen] = useState(false);
  const [picolinoOpen, setPicolinoOpen] = useState(false); // State for popup
  const navigate = useNavigate()


  const currentLanguage = 'RO'
  const content = portfolioContent[currentLanguage]

  useEffect(() => {
    if (picolinoOpen) {
      window.scrollTo(0, 0);
    }
  }, [picolinoOpen]);

  return (
    <div className="portfolio-page">
      <video className="background-video" autoPlay muted loop>
        <source src={BG} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <img src={Filter} alt="Filter overlay" className="video-filter" />
      <div className="portfolio-content">
        <div className="portfolio-bg-fade"></div>
        <NavBar/>
        <div className="portfolio-main-section">
          <h1 className="portfolio-main-section-title">
            {content.Portofoliu.title}
          </h1>
          <p className="portfolio-main-section-description">
            {content.Portofoliu.description}
          </p>
          
          <button
            className="portfolio-main-section-button"
            onClick={() => navigate("/aboutus")}
          >
            {content.Portofoliu.mainbutton}
          </button>
        </div>

        {/* Projects Section */}
        <div className="portfolio-projects-section">
          <img src={line} alt="Background line" className="portfolio-bg-line" />
          {/* Project 1 - Piccolino (Logo left, description right) */}
          <div className="portfolio-project">
            <div className="project-content">
              <div className="project-logo">
                <img src={project1} alt="Piccolino Logo" />
              </div>
              <div className="project-info">
                <p className="project-description">
                  {content.Portofoliu.project1description}
                </p>
                <button
                  className="project-button"
                  onClick={() => setPicolinoOpen(true)}
                >
                  {content.Portofoliu.prokectbutton}
                </button>
              </div>
            </div>
          </div>

          {/* Project 2 - Krov (Description left, logo right) */}
          <div className="portfolio-project">
            <div className="project-content project-content-reverse">
              <div className="project-logo">
                <img src={project2} alt="Krov Logo" />
              </div>
              <div className="project-info">
                <p className="project-description">
                  {content.Portofoliu.prject2description}
                </p>
                <button
                  className="project-button"
                  onClick={() => navigate("/krov")}
                >
                  {content.Portofoliu.prokectbutton}
                </button>
              </div>
      
            </div>
          </div>

          {/* Project 3 - Lumeta (Logo left, description right) */}
          <div className="portfolio-project">
            <div className="project-content">
              <div className="project-logo">
                <img src={project3} alt="Lumeta Logo" />
              </div>
              <div className="project-info">
                <p className="project-description">
                  {content.Portofoliu.project3description}
                </p>
                <button
                  className="project-button"
                  onClick={() => navigate("/lumeata")}
                >
                  {content.Portofoliu.prokectbutton}
                </button>
              </div>
            </div>
          </div>
          {/* Project 4 - Call to Action */}
          <div className="portfolio-project">
            <div className="portfolio-call-section">
              <p
                className="portfolio-call-text"
                dangerouslySetInnerHTML={{ __html: content.Portofoliu.call }}
              ></p>
              <button
                className="portfolio-call-button"
                onClick={() => setChatOpen(true)}
              >
                {content.Portofoliu.callbutton}
              </button>
            </div>
          </div>
        </div>
        <Footer />
      </div>
      <LiveChat open={chatOpen} setOpen={setChatOpen} />

      {/* Piccolino Popup Modal */}
      {picolinoOpen && (
        <div className="portfolio-modal-overlay" onClick={() => setPicolinoOpen(false)}>
          <div className="portfolio-modal-content" onClick={e => e.stopPropagation()}>
            <button className="portfolio-modal-close" onClick={() => setPicolinoOpen(false)}>×</button>
            <Picolino />
          </div>
        </div>
      )}
    </div>
  )
}

export default Portfolio