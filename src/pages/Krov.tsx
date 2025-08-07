import React from "react";
import "./ProjectsPage.css";
import projectsContent from "./ProjectsPage.json";
import { useNavigate } from "react-router-dom";
import client from "../assets/Marcel.png";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import { useLanguage } from "../components/LanguageContext";

const Krov: React.FC = () => {
  const { language } = useLanguage();
  const project = projectsContent[language].projects[0];
  const navigate = useNavigate();

  // Type guard to check if project has the required properties
  const hasProjectDetails = (proj: any): proj is {
    title: string;
    description: string;
    sectiononetitle: string;
    sectiononepoint1: string;
    sectiononepoint2: string;
    sectiononepoint3: string;
    sectiononepoint4: string;
    sectitwonetitle: string;
    sectitwonepoint1: string;
    sectithreenetitle: string;
    sectithreenepoint1: string;
    sectithreenepoint2: string;
    feedbacktext: string;
  } => {
    return proj && 
           typeof proj.sectiononetitle === 'string' &&
           typeof proj.sectiononepoint1 === 'string' &&
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
                <li>{project.sectiononepoint4}</li>
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
              <span className="project-client-name">Marcel Papuc</span>
            </div>
            <p className="project-feedback-text">{project.feedbacktext}</p>
          </div>
          
          {/* YouTube Video */}
          <div className="project-video-section">
            <iframe
              src={getYouTubeVideoUrl(language)}
              className="project-video"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title="Project Video"
            />
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default Krov;