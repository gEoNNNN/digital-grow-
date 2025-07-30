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
import feedback from "../assets/krovfeedback.mp4"
import { useState } from 'react'
import LiveChat from "../components/LiveChat"

const HomePage = () => {
  const currentLanguage = 'RO'
  const content = homepageContent[currentLanguage]
  const [videoOpen, setVideoOpen] = useState(false)

  return (
    <div className="homepage">
      <video className="background-video" autoPlay muted loop>
        <source src={BG} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <img src={Filter} alt="Filter overlay" className="video-filter" />
      <div className="homepage-content">
        <div className="portfolio-bg-fade"></div>
        <NavBar/>
        <LiveChat/>
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
          <button className="homepage-main-section-button">
            <img src={iconoferta}/>
            {content.hero.primaryButton}
          </button>
          </div>
          <div className="homepage-section-one">
            <h3  className="homepage-section-one-title" dangerouslySetInnerHTML={{ __html: content.hero.sectiononetitle }} />
            <div className="homepage-section-one-cards">
              <div className="homepage-section-one-card">
                <h3>{content.hero.sectiononecard1title}</h3>
                <p>{content.hero.sectiononecard1description}</p>
                <button className="homepage-section-one-card-button">
                  {content.hero.sectiononebutton}
                </button>
                <img src={section1card1}/>
              </div>
              <div className="homepage-section-one-card">
                <h3>{content.hero.sectiononecard2title}</h3>
                <p>{content.hero.sectiononecard2description}</p>
                <button className="homepage-section-one-card-button">
                  {content.hero.sectiononebutton}
                </button>
                <img src={section1card2}/>
              </div>
              <div className="homepage-section-one-card">
                <h3>{content.hero.sectiononecard3title}</h3>
                <p>{content.hero.sectiononecard3description}</p>
                <button className="homepage-section-one-card-button">
                  {content.hero.sectiononebutton}
                </button>
                <img src={section1card3}/>
              </div>
              <div className="homepage-section-one-card">
                <h3>{content.hero.sectiononecard4title}</h3>
                <p>{content.hero.sectiononecard4description}</p>
                <button className="homepage-section-one-card-button">
                  {content.hero.sectiononebutton}
                </button>
                <img src={section1card4}/>
              </div>
            </div>
          </div>
          <div className="homepage-section-two">
            <h3  className="homepage-section-one-title" dangerouslySetInnerHTML={{ __html: content.hero.sectiontwotitle }} />
            <div className="homepage-section-two-cards">
              <div className="homepage-section-two-card">
                <img src={section2card1} alt="Soluții integrate"/>
                <h3>{content.hero.sectiontwocard1title}</h3>
                <p>{content.hero.sectiontwocard1description}</p>
              </div>
              <div className="homepage-section-two-card">
                <img src={section2card2} alt="Suport rapid"/>
                <h3>{content.hero.sectiontwocard2title}</h3>
                <p>{content.hero.sectiontwocard2description}</p>
              </div>
              <div className="homepage-section-two-card">
                <img src={section2card3} alt="Calitate garantată"/>
                <h3>{content.hero.sectiontwocard3title}</h3>
                <p>{content.hero.sectiontwocard3description}</p>
              </div>
            </div>
          </div>
          <div className="homepage-section-three">
            <h1 className="homepage-section-one-title">
              {content.hero.sectionthreetitle}
            </h1>
            <div className="homepage-section-three-content">
              {/* Left: Client photo and name */}
              <div className="homepage-client-photo">
                <img src={marcel} alt="Marcel Papuc" />
                <span className="homepage-client-name">{content.hero.marcel}</span>
              </div>
              {/* Right: Feedback and button */}
              <div className="homepage-feedback-block">
                <p className="homepage-feedback-text-cotation1">,,</p>
                <p className="homepage-feedback-text">{content.hero.feedback}</p>
                <p className="homepage-feedback-text-cotation2">,,</p>

                <button
                  className="homepage-section-one-card-button"
                  onClick={() => setVideoOpen(true)}
                >
                  {content.hero.feedbackbutton}
                </button>
                {/* Video Popup */}
                {videoOpen && (
                  <div
                    className="homepage-video-popup"
                    onClick={() => setVideoOpen(false)}
                  >
                    <video
                      src={feedback}
                      controls
                      autoPlay
                      className="homepage-video"
                      onClick={e => e.stopPropagation()}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
          <NextLevelSection
            title={content.hero.sectionfourtitle}
            buttonText={content.hero.sectionfourbutton}
          />
          <Footer />
        </div>
      </div>
  )
}

export default HomePage