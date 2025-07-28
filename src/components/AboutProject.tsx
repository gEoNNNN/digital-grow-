import React from "react";
import "./AboutProject.css";

interface ProjectPopupProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description: string;
}

const ProjectPopup: React.FC<ProjectPopupProps> = ({ open, onClose, title, description }) => {
  if (!open) return null;
  return (
    <div className="project-popup-overlay" onClick={onClose}>
      <div className="project-popup-content" onClick={e => e.stopPropagation()}>
        <button className="project-popup-close" onClick={onClose}>×</button>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </div>
  );
};

export default ProjectPopup;