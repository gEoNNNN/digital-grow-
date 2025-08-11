import React, { useEffect, useState } from "react";
import "./ProjectsPage.css";
import projectsContent from "./ProjectsPage.json";
import { useNavigate } from "react-router-dom";
import client from "../assets/photo123.jpg";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import { useLanguage } from "../components/LanguageContext";

// Define the project type interface
interface Project {
  title: string;
  description: string;
  sectiononetitle: string;
  sectiononepoint1: string;
  sectiononepoint2: string;
  sectiononepoint3: string;
  sectiononepoint4?: string;
  sectitwonetitle: string;
  sectitwonepoint1: string;
  sectithreenetitle: string;
  sectithreenepoint1: string;
  sectithreenepoint2: string;
  feedbacktext: string;
  clientname?: string;
  link?: string;
}

const Piccolino: React.FC = () => {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const [showVideoPopup, setShowVideoPopup] = useState(false);

  // Detect mobile device
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Safely get project data with proper typing
  const projectData = projectsContent[language as keyof typeof projectsContent];
  const project = projectData?.projects?.[1] as Project | undefined;

  // Type guard to check if project has the required properties
  const hasProjectDetails = (proj: Project | undefined): proj is Project => {
    return proj !== undefined && 
           typeof proj.title === 'string' &&
           typeof proj.description === 'string' &&
           typeof proj.sectiononetitle === 'string' &&
           typeof proj.feedbacktext === 'string';
  };

  // YouTube video URLs with language-specific subtitles
  const getYouTubeVideoUrl = (lang: string) => {
    const videoId = "1vdhAAVwLpQ";
    const baseUrl = `https://www.youtube.com/embed/${videoId}`;
    
    switch (lang) {
      case "RO":
        return `${baseUrl}?cc_lang_pref=ro&cc_load_policy=1`;
      case "RU":
        return `${baseUrl}?cc_lang_pref=ru&cc_load_policy=1`;
      case "EN":
        return `${baseUrl}?cc_lang_pref=en&cc_load_policy=1`;
      default:
        return `${baseUrl}?cc_lang_pref=ro&cc_load_policy=1`;
    }
  };

  // Only show popup on desktop
  useEffect(() => {
    if (isMobile) return;
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollPercentage = (scrollTop + windowHeight) / documentHeight;
      setShowVideoPopup(scrollPercentage > 0.8);
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
          <div className="project-info-sections">
            <div className="project-info-section">
              <h3>{project.sectiononetitle}</h3>
              <ul>
                <li>{project.sectiononepoint1}</li>
                <li>{project.sectiononepoint2}</li>
                <li>{project.sectiononepoint3}</li>
                {project.sectiononepoint4 && <li>{project.sectiononepoint4}</li>}
              </ul>
            </div>
            
            <div className="project-info-section">
              <h3>{project.sectitwonetitle}</h3>
              <ul>
                <li>{project.sectitwonepoint1}</li>
              </ul>
            </div>
            
            <div className="project-info-section">
              <h3>{project.sectithreenetitle}</h3>
              <ul>
                <li>{project.sectithreenepoint1}</li>
                <li>{project.sectithreenepoint2}</li>
              </ul>
            </div>
          </div>
          
          {/* Client Feedback */}
          <div className="project-feedback-section">
            <h3>Client Feedback</h3>
            <div className="project-client-info">
              <img src={client} alt="Client" className="project-client-image" />
              <span className="project-client-name">{project.clientname || "Diana Crudu"}</span>
            </div>
            <p className="project-feedback-text">{project.feedbacktext}</p>
          </div>
          
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

          {/* Video Section - mobile: inline, desktop: popup */}
          {isMobile ? (
            <div className="project-video-section" style={{ margin: "0 0" }}>
              <iframe
                src={getYouTubeVideoUrl(language)}
                className="project-video"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                title="Project Video"
                style={{ width: "100%", height: "50vw", borderRadius: "2vw", background: "#000" }}
              />
            </div>
          ) : (
            <div className={`project-video-popup ${showVideoPopup ? 'visible' : ''}`}>
              <div className="project-video-popup-content">
                <button
                  className="project-video-close-btn"
                  onClick={() => {
                    setShowVideoPopup(false);
                    setTimeout(() => {
                      const iframe = document.querySelector('.project-video-popup-iframe') as HTMLIFrameElement;
                      if (iframe) {
                        const src = iframe.src;
                        iframe.src = '';
                        iframe.src = src;
                      }
                    }, 100);
                  }}
                  aria-label="Close video"
                >
                  ×
                </button>
                <iframe
                  src={getYouTubeVideoUrl(language)}
                  className="project-video-popup-iframe"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  title="Project Video"
                />
              </div>
            </div>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Piccolino;