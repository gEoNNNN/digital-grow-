import React from "react";
import "./ProjectsPage.css";
import piccolinoLogo from "../assets/picolonologopage.svg";
import piccolinoImage from "../assets/picolinoimgpage.jpg"; 
import projectsContent from "./ProjectsPage.json";
import { useNavigate } from "react-router-dom";

const Picolino: React.FC = () => {
  const currentLanguage = "RO";
  const project = projectsContent[currentLanguage].projects[1];
  const navigate = useNavigate();

  return (
    <div className="lumeata-bg">
      <div className="picolino-page">
        <button className="back-button" onClick={() => navigate("/portfolio")}>
          &larr; Înapoi la portofoliu
        </button>
        <div className="picolino-header">
          <img src={piccolinoLogo} alt="Piccolino Logo" className="picolino-logo" />
          <h1 className="picolino-title">{project.title}</h1>
        </div>
        {/* Second section: image left, description right */}
        <div className="picolino-main">
          <img className="picolino-image" src={piccolinoImage} alt="Piccolino"/>
          <p className="picolino-description" style={{ flex: "1", margin: 0 }} dangerouslySetInnerHTML={{ __html: project.description }}></p>
        </div>
        <div className="picolino-lists">
          <div className="picolino-list">
            <h2>{project.sectiononetitle}</h2>
            <ul>
              <li>{project.sectiononepoint1}</li>
              <li>{project.sectiononepoint2}</li>
              <li>{project.sectiononepoint3}</li>
              <li>{project.sectiononepoint4}</li>
            </ul>
          </div>
          <div className="picolino-list">
            <h2>{project.sectitwonetitle}</h2>
            <ul>
              <li>{project.sectitwonepoint1}</li>
            </ul>
          </div>
          <div className="picolino-list">
            <h2>{project.sectithreenetitle}</h2>
            <ul>
              <li>{project.sectithreenepoint1}</li>
              <li>{project.sectithreenepoint2}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Picolino;