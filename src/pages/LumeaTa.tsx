import React, { useEffect, useState } from "react";
import "./ProjectsPage.css";
import projectsContent from "./ProjectsPage.json";
import { useNavigate } from "react-router-dom";
import client from "../assets/lumetalogo.svg"
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import { useLanguage } from "../components/LanguageContext";
import lumeata from "../assets/lumea ta.png"

const LumeaTa: React.FC = () => {
  const { language } = useLanguage();
  const project = projectsContent[language].projects[2];
  const navigate = useNavigate();
  const [showImagePopup, setShowImagePopup] = useState(false);

  // Detect mobile device
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Type guard to check if project has the required properties
  const hasProjectDetails = (proj: any): proj is {
    title: string;
    description: string;
    sectiononetitle?: string;
    sectiononepoint1?: string;
    sectiononepoint2?: string;
    sectiononepoint3?: string;
    sectiononepoint4?: string;
    sectitwonetitle?: string;
    sectitwonepoint1?: string;
    sectithreenetitle?: string;
    sectithreenepoint1?: string;
    sectithreenepoint2?: string;
    feedbacktext?: string;
    link?: string;
  } => {
    return proj && 
           typeof proj.title === 'string' &&
           typeof proj.description === 'string';
  };

  // Scroll listener to show image popup when near bottom (desktop only)
  useEffect(() => {
    if (isMobile) return;
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollPercentage = (scrollTop + windowHeight) / documentHeight;
      setShowImagePopup(scrollPercentage > 0.8);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isMobile]);

  if (!hasProjectDetails(project)) {
    return (
      <div className="project-page">
        <NavBar />
        <div className="project-container">
          <button className="project-back-button" onClick={() => navigate("/portfolio")}>
            &larr; Back to Portfolio
          </button>
          <div className="project-content-wrapper">
            <h1 className="project-name">Project details not available</h1>
            <p>This project's detailed information is not available.</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="project-page">
      <NavBar />
      <div className="project-container">
        <div className="project-content-wrapper">
          {/* Project Name */}
          <h1 className="project-name">{project.title}</h1>
          
          {/* Project Description */}
          <div className="project-description-section">
            <p className="project-description-text" dangerouslySetInnerHTML={{ __html: project.description }}></p>
          </div>
          
          {/* Project Information Lists */}
          {(project.sectiononetitle || project.sectitwonetitle || project.sectithreenetitle) && (
            <div className="project-info-sections">
              {project.sectiononetitle && (
                <div className="project-info-section">
                  <h3>{project.sectiononetitle}</h3>
                  <ul>
                    {project.sectiononepoint1 && <li>{project.sectiononepoint1}</li>}
                    {project.sectiononepoint2 && <li>{project.sectiononepoint2}</li>}
                    {project.sectiononepoint3 && <li>{project.sectiononepoint3}</li>}
                    {project.sectiononepoint4 && <li>{project.sectiononepoint4}</li>}
                  </ul>
                </div>
              )}
              
              {project.sectitwonetitle && (
                <div className="project-info-section">
                  <h3>{project.sectitwonetitle}</h3>
                  <ul>
                    {project.sectitwonepoint1 && <li>{project.sectitwonepoint1}</li>}
                  </ul>
                </div>
              )}
              
              {project.sectithreenetitle && (
                <div className="project-info-section">
                  <h3>{project.sectithreenetitle}</h3>
                  <ul>
                    {project.sectithreenepoint1 && <li>{project.sectithreenepoint1}</li>}
                    {project.sectithreenepoint2 && <li>{project.sectithreenepoint2}</li>}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          {/* Client Feedback - only show if feedbacktext exists */}
          {project.feedbacktext && (
            <div className="project-feedback-section">
              <h3>Client Feedback</h3>
              <div className="project-client-info">
                <img src={client} alt="Client" className="project-client-image" />
                <span className="project-client-name">Lumea Ta Team</span>
              </div>
              <p className="project-feedback-text">{project.feedbacktext}</p>
            </div>
          )}
          
          {/* Website Link Section */}
          {project.link && (
            <div className="project-link-section">
              <h3>Visit Website</h3>
              <a 
                href={project.link} 
                target="_blank" 
                rel="noopener noreferrer"
                className="project-website-link"
              >
                {project.link}
              </a>
            </div>
          )}
        </div>
      </div>
      
      {/* Image Section - mobile: inline, desktop: popup */}
      {isMobile ? (
        <div className="project-video-section">
          <img
            src={lumeata}
            alt="Lumea Ta Project Screenshot"
            className="project-video"
            style={{ width: "100%", height: "auto", borderRadius: "2vw", background: "#000" }}
          />
        </div>
      ) : (
        <div className={`project-image-popup ${showImagePopup ? 'visible' : ''}`}>
          <div className="project-image-popup-content">
            <button
              className="project-video-close-btn"
              onClick={() => setShowImagePopup(false)}
              aria-label="Close image"
            >
              ×
            </button>
            <img
              src={lumeata}
              alt="Lumea Ta Project Screenshot"
              className="project-image-popup-img"
            />
          </div>
        </div>
      )}
      
      <Footer />
    </div>
  );
};

export default LumeaTa;