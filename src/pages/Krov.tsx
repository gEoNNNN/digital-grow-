import React, { useEffect, useState } from "react";
import "./ProjectsPage.css";
import projectsContent from "./ProjectsPage.json";
import { useNavigate } from "react-router-dom";
import client from "../assets/Marcel.png";
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

const Krov: React.FC = () => {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const [showVideoPopup, setShowVideoPopup] = useState(false);

  // Safely get project data with proper typing
  const projectData = projectsContent[language as keyof typeof projectsContent];
  const project = projectData?.projects?.[0] as Project | undefined;

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
    const videoId = "EuKHNcY53sA";
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

  // Scroll listener to show video popup when near bottom
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // Calculate how close to bottom (80% of the way down)
      const scrollPercentage = (scrollTop + windowHeight) / documentHeight;
      
      if (scrollPercentage > 0.8) {
        setShowVideoPopup(true);
      } else {
        setShowVideoPopup(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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
              <span className="project-client-name">{project.clientname || "Marcel Papuc"}</span>
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
        </div>
      </div>
      
      {/* Video Popup */}
      <div className={`project-video-popup ${showVideoPopup ? 'visible' : ''}`}>
        <div className="project-video-popup-content">
          <button
            className="project-video-close-btn"
            onClick={() => {
              setShowVideoPopup(false);
              // Force video to stop by reloading the iframe
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
      
      <Footer />
    </div>
  );
};

export default Krov;