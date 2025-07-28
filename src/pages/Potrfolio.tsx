import React, { useState } from 'react'
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
import ProjectPopup from "../components/AboutProject"
import krov from "../assets/krob.svg"
import krovsection from "../assets/krovsection.jpg"

const Portfolio: React.FC = () => {
  const [popupOpen, setPopupOpen] = useState(false);
  const [popupData, setPopupData] = useState({ title: "", description: "" });

  const handleProjectClick = (title: string, description: string) => {
    setPopupData({ title, description });
    setPopupOpen(true);
  };

  const currentLanguage = 'RO'
  const content = portfolioContent[currentLanguage]

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
          
          <button className="portfolio-main-section-button">
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
                  onClick={() =>
                    handleProjectClick(
                      "Piccolino",
                      content.Portofoliu.project1description
                    )
                  }
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
                  onClick={() =>
                    handleProjectClick(
                      "Krov",
                      content.Portofoliu.prject2description
                    )
                  }
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
                  onClick={() =>
                    handleProjectClick(
                      "Lumeta",
                      content.Portofoliu.project3description
                    )
                  }
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
              <button className="portfolio-call-button">
                {content.Portofoliu.callbutton}
              </button>
            </div>
          </div>
        </div>
        <ProjectPopup
          open={popupOpen}
          onClose={() => setPopupOpen(false)}
          title={content.Portofoliu.title}
          description={content.Portofoliu.krovdescription}
          logo={krov}
          sectionImage={krovsection}
          sectionText={content.Portofoliu.krovimagedescription}
          sectionLists={content.Portofoliu.listkrov}
        />
        <Footer />
      </div>
    </div>
  )
}

export default Portfolio