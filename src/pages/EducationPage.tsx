import React, { useState, useRef } from 'react'
import './EducationPage.css'
import BG from "../assets/services.mp4"
import Filter from "../assets/homepagefilter.png"
import NavBar from "../components/NavBar"
import LiveChat from '../components/LiveChat'
import Footer from '../components/Footer'
import educationContent from "./EducationPage.json"
import { useLanguage } from "../components/LanguageContext";

// Add type definitions
interface EpisodeData {
  [key: string]: string;
}

interface ClassData {
  [key: string]: EpisodeData;
}

interface EducationContent {
  education: {
    title: string;
    description: string;
    button1: string;
    button2: string;
    sectionTitle: string;
    sectionTitle2: string;
    episodesTitle: string;
    classesTitle: string;
    classes: {
      [key: string]: string;
    };
    episodes: ClassData;
    episodeDescriptions?: ClassData;
    episodeDescriptions2?: ClassData; 
  };
}

const EducationPage: React.FC = () => {
  const { language } = useLanguage();
  const content = educationContent[language as keyof typeof educationContent] as EducationContent;
  const [chatOpen, setChatOpen] = useState(false);
  
  // State for Section 1 (Mathematics)
  const [selectedClass, setSelectedClass] = useState<string>('1');
  const [selectedEpisode, setSelectedEpisode] = useState<string>('1');
  const [isClassDropdownOpen, setIsClassDropdownOpen] = useState(false);

  // State for Section 2 (Romanian Language)
  const [selectedClass2, setSelectedClass2] = useState<string>('1');
  const [selectedEpisode2, setSelectedEpisode2] = useState<string>('1');
  const [isClassDropdownOpen2, setIsClassDropdownOpen2] = useState(false);

  // Video popup states
  const [videoPopupOpen, setVideoPopupOpen] = useState(false);
  const [videoPopupUrl, setVideoPopupUrl] = useState<string>('');
  const [videoPopupTitle, setVideoPopupTitle] = useState<string>('');

  // Check if device is mobile
  const [isMobile] = useState(() => window.innerWidth <= 768);

  // Create refs for each section
  const section1Ref = useRef<HTMLDivElement>(null);
  const section2Ref = useRef<HTMLDivElement>(null);

  // Scroll handler functions
  const scrollToSection1 = () => {
    section1Ref.current?.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start' 
    });
  };

  const scrollToSection2 = () => {
    section2Ref.current?.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start' 
    });
  };

  // Fallback descriptions for episodes without specific descriptions
  const getFallbackDescription = (language: string) => {
    const fallbackTexts = {
      RO: "Această lecție este în curs de pregătire. Revenim în curând cu conținut educațional de calitate!",
      EN: "This lesson is currently in preparation. We'll be back soon with quality educational content!",
      RU: "Этот урок находится в разработке. Скоро мы вернемся с качественным образовательным контентом!"
    };
    return fallbackTexts[language as keyof typeof fallbackTexts] || fallbackTexts.RO;
  };

  // Get description for Section 1 (Mathematics)
  const getEpisodeDescription = (classNum: string, episodeNum: string) => {
    return content.education.episodeDescriptions?.[classNum]?.[episodeNum] || getFallbackDescription(language);
  };

  // Get description for Section 2 (Romanian Language)
  const getEpisodeDescription2 = (classNum: string, episodeNum: string) => {
    return content.education.episodeDescriptions2?.[classNum]?.[episodeNum] || getFallbackDescription(language);
  };

  // Sample video URLs - replace with your actual video URLs
  const getVideoUrl = (classNum: string, episodeNum: string): string | null => {
    const videoUrls: { [key: string]: { [key: string]: string } } = {
      '1': {
        '1': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '2': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '3': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '4': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '5': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '6': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '7': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '8': 'https://www.youtube.com/embed/dQw4w9WgXcQ'
      },
      '2': {
        '1': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '2': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '3': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '4': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '5': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '6': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '7': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '8': 'https://www.youtube.com/embed/dQw4w9WgXcQ'
      },
      '3': {
        '1': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '2': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '3': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '4': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '5': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '6': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '7': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '8': 'https://www.youtube.com/embed/dQw4w9WgXcQ'
      },
      '4': {
        '1': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '2': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '3': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '4': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '5': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '6': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '7': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        '8': 'https://www.youtube.com/embed/dQw4w9WgXcQ'
      }
    };
    
    return videoUrls[classNum]?.[episodeNum] || null;
  };

  // Handle video click for fullscreen popup
  const handleVideoClick = (classNum: string, episodeNum: string, section: string) => {
    if (!isMobile) {
      const videoUrl = getVideoUrl(classNum, episodeNum);
      if (videoUrl) {
        setVideoPopupUrl(videoUrl);
        setVideoPopupTitle(`${section} - Class ${classNum} - Episode ${episodeNum}`);
        setVideoPopupOpen(true);
      }
    }
  };

  // Close video popup
  const closeVideoPopup = () => {
    setVideoPopupOpen(false);
    setVideoPopupUrl('');
    setVideoPopupTitle('');
  };

  // Handlers for Section 1
  const handleClassSelect = (classNum: string) => {
    setSelectedClass(classNum);
    setSelectedEpisode('1');
    setIsClassDropdownOpen(false);
  };

  const handleEpisodeSelect = (episodeNum: string) => {
    setSelectedEpisode(episodeNum);
  };

  // Handlers for Section 2
  const handleClassSelect2 = (classNum: string) => {
    setSelectedClass2(classNum);
    setSelectedEpisode2('1');
    setIsClassDropdownOpen2(false);
  };

  const handleEpisodeSelect2 = (episodeNum: string) => {
    setSelectedEpisode2(episodeNum);
  };

  const currentVideoUrl = getVideoUrl(selectedClass, selectedEpisode);
  const currentEpisodes = content.education.episodes[selectedClass] || {};

  const currentVideoUrl2 = getVideoUrl(selectedClass2, selectedEpisode2);
  const currentEpisodes2 = content.education.episodes[selectedClass2] || {};

  return (
    <div className="education-page">
      <video className="background-video" autoPlay muted loop>
        <source src={BG} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <img src={Filter} alt="Filter overlay" className="video-filter" />
      
      {/* Fullscreen Video Popup */}
      {videoPopupOpen && (
        <div className="education-video-popup" onClick={closeVideoPopup}>
          <div className="education-video-popup-content" onClick={e => e.stopPropagation()}>
            <button
              className="education-video-close-btn"
              onClick={closeVideoPopup}
              aria-label="Close video"
            >
              ×
            </button>
            <iframe
              src={videoPopupUrl}
              className="education-video-popup-iframe"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title={videoPopupTitle}
            />
          </div>
        </div>
      )}

      <div className="education-content">
        <LiveChat open={chatOpen} setOpen={setChatOpen} />
        <NavBar/>
        
        {/* Main Section */}
        <div className="education-main-section">
          <h1 className="education-main-section-title">
            {content.education.title}
          </h1>
          <p className="education-main-section-description">
            {content.education.description}
          </p>
          <div className="education-buttons">
            <button className="education-button" onClick={scrollToSection1}>
              {content.education.button1}
            </button>
            <button className="education-button" onClick={scrollToSection2}>
              {content.education.button2}
            </button>
          </div>
        </div>

        {/* Section 1 - Mathematics */}
        <div className="education-classes-section" ref={section1Ref}>
          <div className="education-section-header">
            <div className="education-main-class-dropdown">
              <button
                className="education-main-class-dropdown-button"
                onClick={() => setIsClassDropdownOpen(!isClassDropdownOpen)}
              >
                <span>{content.education.classes[selectedClass]}</span>
                <span>{isClassDropdownOpen ? '▲' : '▼'}</span>
              </button>
              {isClassDropdownOpen && (
                <div className="education-main-class-dropdown-menu">
                  {Object.entries(content.education.classes).map(([classNum, className]) => (
                    <button
                      key={classNum}
                      className="education-main-class-dropdown-item"
                      onClick={() => handleClassSelect(classNum)}
                    >
                      {className}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <h2 className="education-section-main-title">
              {content.education.sectionTitle}
            </h2>
          </div>
          
          <div className="education-content-container">
            <div className="education-video-section">
              <div className="education-video-container">
                {currentVideoUrl ? (
                  isMobile ? (
                    <iframe
                      src={currentVideoUrl}
                      className="education-video"
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      title={`Class ${selectedClass} - Episode ${selectedEpisode}`}
                    />
                  ) : (
                    <div 
                      className="education-video-preview"
                      onClick={() => handleVideoClick(selectedClass, selectedEpisode, content.education.sectionTitle)}
                    >
                      <div className="education-video-play-overlay">
                        <div className="education-video-play-button">▶</div>
                        <p className="education-video-play-text">Click to play fullscreen</p>
                      </div>
                      <iframe
                        src={currentVideoUrl}
                        className="education-video"
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        title={`Class ${selectedClass} - Episode ${selectedEpisode}`}
                        style={{ pointerEvents: 'none' }}
                      />
                    </div>
                  )
                ) : (
                  <div className="education-video-placeholder">
                    Select a class and episode to watch
                  </div>
                )}
              </div>
            </div>

            <div className="education-controls-section">
              <div className="education-episodes-section">
                <h3 className="education-section-title">
                  {content.education.episodesTitle}
                </h3>
                
                <div className="education-episodes-numbers">
                  {Object.keys(currentEpisodes).map((episodeNum) => (
                    <button
                      key={episodeNum}
                      className={`education-episode-number-button ${selectedEpisode === episodeNum ? 'active' : ''}`}
                      onClick={() => handleEpisodeSelect(episodeNum)}
                    >
                      {episodeNum}
                    </button>
                  ))}
                </div>

                <div className="education-episode-description">
                  <p>{getEpisodeDescription(selectedClass, selectedEpisode)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Section 2 - Romanian Language */}
        <div className="education-classes-section2" ref={section2Ref}>
          <div className="education-section-header">
            <div className="education-main-class-dropdown">
              <button
                className="education-main-class-dropdown-button"
                onClick={() => setIsClassDropdownOpen2(!isClassDropdownOpen2)}
              >
                <span>{content.education.classes[selectedClass2]}</span>
                <span>{isClassDropdownOpen2 ? '▲' : '▼'}</span>
              </button>
              {isClassDropdownOpen2 && (
                <div className="education-main-class-dropdown-menu">
                  {Object.entries(content.education.classes).map(([classNum, className]) => (
                    <button
                      key={classNum}
                      className="education-main-class-dropdown-item"
                      onClick={() => handleClassSelect2(classNum)}
                    >
                      {className}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <h2 className="education-section-main-title">
              {content.education.sectionTitle2}
            </h2>
          </div>
          
          <div className="education-content-container">
            <div className="education-video-section">
              <div className="education-video-container">
                {currentVideoUrl2 ? (
                  isMobile ? (
                    <iframe
                      src={currentVideoUrl2}
                      className="education-video"
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      title={`Class ${selectedClass2} - Episode ${selectedEpisode2}`}
                    />
                  ) : (
                    <div 
                      className="education-video-preview"
                      onClick={() => handleVideoClick(selectedClass2, selectedEpisode2, content.education.sectionTitle2)}
                    >
                      <div className="education-video-play-overlay">
                        <div className="education-video-play-button">▶</div>
                        <p className="education-video-play-text">Click to play fullscreen</p>
                      </div>
                      <iframe
                        src={currentVideoUrl2}
                        className="education-video"
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        title={`Class ${selectedClass2} - Episode ${selectedEpisode2}`}
                        style={{ pointerEvents: 'none' }}
                      />
                    </div>
                  )
                ) : (
                  <div className="education-video-placeholder">
                    Select a class and episode to watch
                  </div>
                )}
              </div>
            </div>

            <div className="education-controls-section">
              <div className="education-episodes-section">
                <h3 className="education-section-title">
                  {content.education.episodesTitle}
                </h3>
                
                <div className="education-episodes-numbers">
                  {Object.keys(currentEpisodes2).map((episodeNum) => (
                    <button
                      key={episodeNum}
                      className={`education-episode-number-button ${selectedEpisode2 === episodeNum ? 'active' : ''}`}
                      onClick={() => handleEpisodeSelect2(episodeNum)}
                    >
                      {episodeNum}
                    </button>
                  ))}
                </div>

                <div className="education-episode-description">
                  <p>{getEpisodeDescription2(selectedClass2, selectedEpisode2)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <Footer />
      </div>
    </div>
  )
}

export default EducationPage