import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';
import BG from "../assets/0723.mp4"
import './HomePage.css'  // Using the same CSS as homepage
import NavBar from "../components/NavBar"
import Filter from "../assets/homepagefilter.png"
import homepageContent from "./Homepage.json"  // Using the same JSON as homepage
import iconoferta from "../assets/homepageoferta.svg"
import section1card1 from "../assets/homepagesection1card1.jpg"
import section1card2 from "../assets/homepagesection1card2.jpg"
import section1card3 from "../assets/homepagesection1card3.jpg"
import section1card4 from "../assets/homepagesection1card4.jpg"
import section2card1 from "../assets/sectiontwocard1.svg"
import section2card2 from "../assets/sectiontwocard2.svg"
import section2card3 from "../assets/sectiontwocard3.svg"
import Footer from "../components/Footer"
import NextLevelSection from "../components/NextLevel";
import marcel from "../assets/Marcel.png"
import otherClient from "../assets/lumetalogo.svg" 
// import LiveChatFeedback from "../components/Livechatfeedback"  // Using feedback chat instead
import LiveChatWrapper from "../components/LiveChatWrapper";
import { useLanguage } from "../components/LanguageContext";
import shape1 from "../assets/Ellipse 1.png"
import shape2 from "../assets/Ellipse 2.png"
import shape3 from "../assets/Ellipse 3.png"

const FeedbackPage = () => {
  const { language, setLanguage } = useLanguage();
  const navigate = useNavigate();

  

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const lang = params.get("lang");
    const email = params.get("email");

    const allowedLangs = ["RO", "RU", "EN"] as const;

    // verifică parametrii
    if (!lang || !email) {
      navigate("/"); // redirect dacă lipsesc
      return;
    }

    const upperLang = lang.toUpperCase();
    if (allowedLangs.includes(upperLang as typeof allowedLangs[number])) {
      setLanguage(upperLang as typeof allowedLangs[number]);
    } else {
      navigate("/"); // redirect dacă lang nu e valid
    }
  }, [setLanguage, navigate]);

  const content = homepageContent[language] 
  const [chatOpen, setChatOpen] = useState(true) 
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

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

  const feedbacks = [
    {
      name: content.hero.marcel,
      photo: marcel,
      feedback: content.hero.feedback,
      video: getYouTubeVideoUrl(language),
      button: content.hero.feedbackbutton,
      showVideoButton: true // Marcel has video button
    },
    {
      name: content.hero.lumeata,
      photo: otherClient,
      feedback: content.hero.lumetafeedback,
      video: getYouTubeVideoUrl(language),
      button: content.hero.feedbackbutton,
      showVideoButton: false // Lumea Ta doesn't have video button
    }
  ];

  const [currentFeedback, setCurrentFeedback] = useState(0);
  const [videoOpen, setVideoOpen] = useState(false);

  return (
    <div className="homepage">
      <video className="background-video" autoPlay muted loop>
        <source src={BG} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <img src={Filter} alt="Filter overlay" className="video-filter" />
      
      <div className="homepage-content">
        <NavBar/>
        <LiveChatWrapper open={chatOpen} setOpen={setChatOpen} />
      
        <div className="homepage-main-section">
          <h1 className="homepage-main-section-title">
            {content.hero.title1}
          </h1>
          <h1 className="homepage-main-section-title">
            {content.hero.title2}
          </h1>
          <h1 className="homepage-main-section-description">
            {content.hero.description}
          </h1>
          <button 
            className={`homepage-main-section-button${language === "RU" ? " homepage-main-section-button-ru" : ""}`}
            onClick={() => setChatOpen(true)}>
            <img src={iconoferta}/>
            {content.hero.primaryButton}
          </button>
        </div>

        <div className="homepage-section-one">
          <img src={shape1} className="homepage-section-one-shape" />
          <div className="homepage-section-one-content">
            <h3 className="homepage-section-one-title" dangerouslySetInnerHTML={{ __html: content.hero.sectiononetitle }} />
            <div className="homepage-section-one-cards">
              <div className={`homepage-section-one-card${language === "RU" ? " homepage-section-one-card-ru" : ""}`}>
                <h3>{content.hero.sectiononecard1title}</h3>
                <p>{content.hero.sectiononecard1description}</p>
                <button
                  className={`homepage-section-one-card-button${language === "RU" ? " homepage-section-one-card-button-ru" : ""}`}
                  onClick={() => setChatOpen(true)}
                >
                  {content.hero.sectiononebutton}
                </button>
                <img src={section1card1}/>
              </div>
              <div className={`homepage-section-one-card${language === "RU" ? " homepage-section-one-card-ru" : ""}`}>
                <h3>{content.hero.sectiononecard2title}</h3>
                <p>{content.hero.sectiononecard2description}</p>
                <button
                  className={`homepage-section-one-card-button${language === "RU" ? " homepage-section-one-card-button-ru" : ""}`}
                  onClick={() => setChatOpen(true)}
                >
                  {content.hero.sectiononebutton}
                </button>
                <img src={section1card2}/>
              </div>
              <div className={`homepage-section-one-card${language === "RU" ? " homepage-section-one-card-ru" : ""}`}>
                <h3>{content.hero.sectiononecard3title}</h3>
                <p>{content.hero.sectiononecard3description}</p>
                <button
                  className={`homepage-section-one-card-button${language === "RU" ? " homepage-section-one-card-button-ru" : ""}`}
                  onClick={() => setChatOpen(true)}
                >
                  {content.hero.sectiononebutton}
                </button>
                <img src={section1card3}/>
              </div>
              <div className={`homepage-section-one-card${language === "RU" ? " homepage-section-one-card-ru" : ""}`}>
                <h3>{content.hero.sectiononecard4title}</h3>
                <p>{content.hero.sectiononecard4description}</p>
                <button
                  className={`homepage-section-one-card-button${language === "RU" ? " homepage-section-one-card-button-ru" : ""}`}
                  onClick={() => setChatOpen(true)}
                >
                  {content.hero.sectiononebutton}
                </button>
                <img src={section1card4}/>
              </div>
            </div>
          </div>
        </div>
          
        <div className="homepage-section-two">
          <img src={shape2} className="homepage-section-two-shape" />
          <img src={shape3} className="homepage-section-two-shape2" />
          <div className="homepage-section-two-content">
            <h3 className="homepage-section-one-title" dangerouslySetInnerHTML={{ __html: content.hero.sectiontwotitle }} />
            <div className="homepage-section-two-cards">
              <div className="homepage-section-two-card">
                <img src={section2card1} alt="Soluții integrate"/>
                <h3 className={["EN", "RU"].includes(language) ? "homepage-section-two-card-title-enru" : ""}>
                  {content.hero.sectiontwocard1title}
                </h3>
                <p className={["EN", "RU"].includes(language) ? "homepage-section-two-card-desc-enru" : ""}>
                  {content.hero.sectiontwocard1description}
                </p>
              </div>
              <div className="homepage-section-two-card">
                <img src={section2card2} alt="Suport rapid"/>
                <h3 className={["EN", "RU"].includes(language) ? "homepage-section-two-card-title-enru" : ""}>
                  {content.hero.sectiontwocard2title}
                </h3>
                <p className={["EN", "RU"].includes(language) ? "homepage-section-two-card-desc-enru" : ""}>
                  {content.hero.sectiontwocard2description}
                </p>
              </div>
              <div className="homepage-section-two-card">
                <img src={section2card3} alt="Calitate garantată"/>
                <h3 className={["EN", "RU"].includes(language) ? "homepage-section-two-card-title-enru" : ""}>
                  {content.hero.sectiontwocard3title}
                </h3>
                <p className={["EN", "RU"].includes(language) ? "homepage-section-two-card-desc-enru" : ""}>
                  {content.hero.sectiontwocard3description}
                </p>
              </div>
            </div>
          </div>
        </div> 

        <div className="homepage-section-three">
          <h1 className="homepage-section-three-title">
            {content.hero.sectionthreetitle}
          </h1>
          <div className="homepage-section-three-content">
            {/* Left: Client photo and name */}
            <div className="homepage-client-photo">
              <img src={feedbacks[currentFeedback].photo} alt={feedbacks[currentFeedback].name} />
              <span className="homepage-client-name">{feedbacks[currentFeedback].name}</span>
            </div>

            {/* Right: Feedback and button */}
            <div className="homepage-feedback-block">
              <p className="homepage-feedback-text">{feedbacks[currentFeedback].feedback}</p>
              {feedbacks[currentFeedback].showVideoButton && (
                <button
                  className="homepage-section-one-card-button-video"
                  onClick={() => setVideoOpen(true)}
                >
                  {feedbacks[currentFeedback].button}
                </button>
              )}
              {/* Video Popup */}
              {videoOpen && feedbacks[currentFeedback].showVideoButton && (
                <div
                  className="homepage-video-popup"
                  onClick={() => setVideoOpen(false)}
                >
                  <button
                    className="homepage-video-close-btn"
                    onClick={e => {
                      e.stopPropagation();
                      setVideoOpen(false);
                    }}
                    aria-label="Close video"
                  >
                    ×
                  </button>
                  <iframe
                    src={feedbacks[currentFeedback].video}
                    className="homepage-video"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    title="Project Video"
                    onClick={e => e.stopPropagation()}
                  />
                </div>
              )}
              {/* White rectangles for switching */}
              <div className="homepage-feedback-switcher">
                <div
                  className={`feedback-switch-rect${currentFeedback === 0 ? " active" : ""}`}
                  onClick={() => setCurrentFeedback(0)}
                />
                <div
                  className={`feedback-switch-rect${currentFeedback === 1 ? " active" : ""}`}
                  onClick={() => setCurrentFeedback(1)}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="homepage-section-five">
          <NextLevelSection
            title={
              language === "EN" && isMobile
                ? content.hero.sectionfourtitlemobile
                : content.hero.sectionfourtitle
            }
            buttonText={content.hero.sectionfourbutton}
          />
          <Footer />
        </div>
      </div>
    </div>
  )
}

export default FeedbackPage