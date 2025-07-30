import React from "react";
import { useNavigate } from "react-router-dom";
import "../pages/HomePage.css"

interface NextLevelSectionProps {
  title: string;
  buttonText: string;
}

const NextLevelSection: React.FC<NextLevelSectionProps> = ({ title, buttonText }) => {
  const navigate = useNavigate();

  return (
    <div className="homepage-section-four">
      <h3 className="homepage-section-one-title" dangerouslySetInnerHTML={{ __html: title }} />
      <button
        className="homepage-section-four-button"
        onClick={() => navigate("/contacts")}
      >
        {buttonText}
      </button>
    </div>
  );
};

export default NextLevelSection;