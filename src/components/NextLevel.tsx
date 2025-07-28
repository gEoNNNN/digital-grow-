import React from "react";
import "../pages/HomePage.css"

interface NextLevelSectionProps {
  title: string;
  buttonText: string;
}

const NextLevelSection: React.FC<NextLevelSectionProps> = ({ title, buttonText }) => (
  <div className="homepage-section-four">
    <h3 className="homepage-section-one-title" dangerouslySetInnerHTML={{ __html: title }} />
    <button className="homepage-section-four-button">
      {buttonText}
    </button>
  </div>
);

export default NextLevelSection;