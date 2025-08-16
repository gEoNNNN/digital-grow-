import BG from "../assets/0723.mp4"
import './HomePage.css'
import NavBar from "../components/NavBar"
import Filter from "../assets/homepagefilter.png"
import homepageContent from "./Homepage.json"
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
import otherClient1 from "../assets/photo123.jpg" 
import { useEffect, useState, useRef } from 'react'
import LiveChat from "../components/LiveChat"
import { useLanguage } from "../components/LanguageContext";
import shape1 from "../assets/Ellipse 1.png"
import shape2 from "../assets/Ellipse 2.png"
import shape3 from "../assets/Ellipse 3.png"

const HomePage = () => {
  const { language } = useLanguage();
  const content = homepageContent[language]
  const [chatOpen, setChatOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false);
  
  // Video loading state
  const videoRef = useRef<HTMLVideoElement>(null);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [videoError, setVideoError] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Handle video loading
  const handleVideoLoaded = () => {
    setVideoLoaded(true);
    setVideoError(false);
    if (videoRef.current) {
      videoRef.current.setAttribute('data-loaded', 'true');
    }
  };

  const handleVideoError = () => {
    setVideoError(true);
    console.error('Video failed to load');
  };

  const handleVideoCanPlay = () => {
    if (isMobile && videoRef.current) {
      // Ensure video plays on mobile
      videoRef.current.play().catch(console.error);
    }
  };

  // YouTube video URLs with auto-generated subtitles
  const getYouTubeVideoUrl = (lang: string) => {
    const videoId = "EuKHNcY53sA";
    const baseUrl = `https://www.youtube.com/embed/${videoId}`;

    const langMap: Record<string, string> = {
      RO: "ro",
      RU: "ru",
      EN: "en"
    };

    const ccLang = langMap[lang] || "ro";

    return `${baseUrl}?cc_load_policy=1&cc_lang_pref=${ccLang}&hl=${ccLang}&autoplay=1&modestbranding=1&rel=0`;
  };

  const getYouTubeVideoUrl1 = (lang: string) => {
    const videoId = "1vdhAAVwLpQ";
    const baseUrl = `https://www.youtube.com/embed/${videoId}`;

    const langMap: Record<string, string> = {
      RO: "ro",
      RU: "ru",
      EN: "en"
    };

    const ccLang = langMap[lang] || "ro";

    return `${baseUrl}?cc_load_policy=1&cc_lang_pref=${ccLang}&hl=${ccLang}&autoplay=1&modestbranding=1&rel=0`;
  };

  const feedbacks = [
    {
      name: content.hero.marcel,
      photo: marcel,
      feedback: content.hero.feedback,
      video: getYouTubeVideoUrl(language),
      button: content.hero.feedbackbutton,
      showVideoButton: true
    },
    {
      name: content.hero.lumeata,
      photo: otherClient,
      feedback: content.hero.lumetafeedback,
      video: getYouTubeVideoUrl(language),
      button: content.hero.feedbackbutton,
      showVideoButton: false
    },
    {
      name: content.hero.piccolino,
      photo: otherClient1,
      feedback: content.hero.piccolinofeedback,
      video: getYouTubeVideoUrl1(language),
      button: content.hero.feedbackbutton,
      showVideoButton: true
    }
  ];

  const [currentFeedback, setCurrentFeedback] = useState(0);
  const [videoOpen, setVideoOpen] = useState(false);

  // Function to handle video button click
  const handleVideoClick = () => {
    if (language === 'RO') {
      setVideoOpen(true);
    } else {
      const videoId = currentFeedback === 2 ? "1vdhAAVwLpQ" : "EuKHNcY53sA";
      const langMap: Record<string, string> = {
        EN: "en",
        RU: "ru"
      };
      const ccLang = langMap[language] || "en";
      const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}&cc_load_policy=1&cc_lang_pref=${ccLang}&hl=${ccLang}`;
      window.open(youtubeUrl, '_blank');
    }
  };

  return (
    <div className="homepage">
      {/* Video popup rendered at root level - only for RO language */}
      {videoOpen && language === 'RO' && feedbacks[currentFeedback].showVideoButton && (
        <div
          className="homepage-video-popup"
          onClick={() => setVideoOpen(false)}
          style={{ zIndex: 10000000 }}
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
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}
      
      {/* Optimized video with loading states */}
      <video 
        ref={videoRef}
        className="background-video" 
        autoPlay 
        muted 
        loop 
        playsInline
        preload={isMobile ? "metadata" : "auto"}
        onLoadedData={handleVideoLoaded}
        onError={handleVideoError}
        onCanPlay={handleVideoCanPlay}
        style={{
          opacity: videoLoaded ? 1 : 0,
          transition: 'opacity 0.5s ease'
        }}
      >
        <source src={BG} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      
      {/* Fallback background while video loads */}
      {(!videoLoaded || videoError) && (
        <div 
          className="video-loading-fallback"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100vh',
            backgroundColor: videoError ? '#1a1a1a' : '#2a2a2a',
            backgroundImage: videoError ? 'none' : 'linear-gradient(45deg, #1a1a1a, #2a2a2a)',
            backgroundSize: '200% 200%',
            animation: videoError ? 'none' : 'shimmer 2s infinite',
            zIndex: -2
          }}
        />
      )}
      
      <img src={Filter} alt="Filter overlay" className="video-filter" />
      
      {/* Background shapes */}
      <div className="homepage-content">
        <NavBar/>
        <LiveChat open={chatOpen} setOpen={setChatOpen} />
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
            <div className="homepage-client-photo">
              <img src={feedbacks[currentFeedback].photo} alt={feedbacks[currentFeedback].name} />
              <span className="homepage-client-name">{feedbacks[currentFeedback].name}</span>
            </div>
            <div className="homepage-feedback-block">
              <p className="homepage-feedback-text">{feedbacks[currentFeedback].feedback}</p>
              {feedbacks[currentFeedback].showVideoButton && (
                <button
                  className="homepage-section-one-card-button-video"
                  onClick={handleVideoClick}
                >
                  {feedbacks[currentFeedback].button}
                </button>
              )}
              <div className="homepage-feedback-switcher">
                <div
                  className={`feedback-switch-rect${currentFeedback === 0 ? " active" : ""}`}
                  onClick={() => setCurrentFeedback(0)}
                />
                <div
                  className={`feedback-switch-rect${currentFeedback === 1 ? " active" : ""}`}
                  onClick={() => setCurrentFeedback(1)}
                />
                <div
                  className={`feedback-switch-rect${currentFeedback === 2 ? " active" : ""}`}
                  onClick={() => setCurrentFeedback(2)}
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

export default HomePage