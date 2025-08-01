import React from "react";
import { useNavigate } from "react-router-dom";
import "./Inwork.css";

const Inwork: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="inwork-page">
      <div className="inwork-content">
        <h1 className="inwork-title">Pagina în lucru</h1>
        <p className="inwork-desc">
          Această pagină este în curs de dezvoltare.<br />
          Revenim în curând cu noutăți!
        </p>
        <div className="inwork-loader">
          <span />
          <span />
          <span />
        </div>
        <button
          className="inwork-back-btn"
          onClick={() => navigate("/")}
        >
          Înapoi la pagina principală
        </button>
      </div>
    </div>
  );
};

export default Inwork;