import React, { useEffect, useRef, useState } from "react";
import "./ProjectsPage.css";
import projectsContent from "./ProjectsPage.json";
import client from "../assets/Marcel.png";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import { useLanguage } from "../components/LanguageContext";

const Picolino: React.FC = () => {
  const { language } = useLanguage();
  const project = projectsContent[language].projects[1]; // Make sure this is the correct index for Picolino
  const videoRef = useRef<HTMLDivElement>(null);
  const [isVideoVisible, setIsVideoVisible] = useState(false);

  // More flexible type guard - only require basic properties
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
  } => {
    return proj && 
           typeof proj.title === 'string' &&
           typeof proj.description === 'string';
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

  // Intersection Observer for video animation
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVideoVisible(true);
          }
        });
      },
      {
        threshold: 0.3,
        rootMargin: '0px 0px -100px 0px'
      }
    );

    if (videoRef.current) {
      observer.observe(videoRef.current);
    }

    return () => {
      if (videoRef.current) {
        observer.unobserve(videoRef.current);
      }
    };
  }, []);

  // Add debugging
  console.log('Picolino project:', project);
  console.log('Has project details:', hasProjectDetails(project));

  if (!hasProjectDetails(project)) {
    return (
      <div className="project-page">
        <NavBar />
        <div className="project-container">
          <div className="project-content-wrapper">
            <h1 className="project-name">Project details not available</h1>
            <p>This project's detailed information is not available.</p>
            <p>Debug info: {JSON.stringify(project)}</p>
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
          
          {/* Project Information Lists - Only show if sections exist */}
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
          
          {/* Client Feedback - Only show if feedbacktext exists */}
          {project.feedbacktext && (
            <div className="project-feedback-section">
              <h3>Client Feedback</h3>
              <div className="project-client-info">
                <img src={client} alt="Client" className="project-client-image" />
                <span className="project-client-name">Picolino Team</span>
              </div>
              <p className="project-feedback-text">{project.feedbacktext}</p>
            </div>
          )}
          
          {/* YouTube Video with Animation */}
          <div 
            ref={videoRef}
            className={`project-video-section ${isVideoVisible ? 'video-visible' : ''}`}
          >
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

export default Picolino;