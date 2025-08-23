import React from "react";
import { useNavigate } from "react-router-dom";
import "../pages/HomePage.css"
import shape4 from "../assets/Ellipse 4.svg"


interface NextLevelSectionProps {
  title: string;
  buttonText: string;
}

const NextLevelSection: React.FC<NextLevelSectionProps> = ({ title, buttonText }) => {
  const navigate = useNavigate();

  return (
    <div className="homepage-section-four">
      <img src={shape4} className="homepage-section-four-shape" />
      <div className="homepage-section-four-content">
        <h3 className="homepage-section-one-title" dangerouslySetInnerHTML={{ __html: title }} />
        <button
          className="homepage-section-four-button"
          onClick={() => navigate("/contacts")}
        >
          {buttonText}
        </button>
      </div>
    </div>
  );
};

export default NextLevelSection;