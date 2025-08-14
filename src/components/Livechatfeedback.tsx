import React, { useState, useRef, useEffect } from "react";
import "./Livechatfeedback.css";
import livechatopenbg from "../assets/Group 71feedback.png"
import closebutton from "../assets/closebutton.svg";
import sendicon from "../assets/sendicon.svg";
import chatboticon from "../assets/chatlogo.svg";
import { useLanguage } from "./LanguageContext";

type ChatMessage = {
  id: number;
  text: string;
  from: "user" | "bot";
  type?: "feedback" | "normal";
};

const initialMessages: ChatMessage[] = [
  { id: 1, text: "feedback", from: "bot", type: "feedback" }
];

interface LiveChatFeedbackProps {
  open?: boolean;
  setOpen?: (open: boolean) => void;
  onFeedbackSubmit?: (data: { emoji: string; reason: string; language: string }) => void;
}

const LiveChatFeedback: React.FC<LiveChatFeedbackProps> = ({
  open: controlledOpen,
  setOpen: setControlledOpen,
  onFeedbackSubmit
}) => {
  const { language } = useLanguage();
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = setControlledOpen || setInternalOpen;
  const [email, setEmail] = useState<string>("");

  const [visible, setVisible] = useState(false);
  // const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [feedbackStep, setFeedbackStep] = useState<"none" | "emoji" | "reason">("emoji");
  const [selectedEmoji, setSelectedEmoji] = useState("");
  const [feedbackReason, setFeedbackReason] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const emailFromUrl = urlParams.get("email") || "";
    setEmail(emailFromUrl);
  }, []);

  // Translations
  // În obiectul feedbackTranslations schimbăm doar thankYou:
  const feedbackTranslations = {
    RO: {
      question: "Cum ți s-a părut chatbot-ul?",
      disappointing: "Dezamăgitor",
      acceptable: "Acceptabil",
      excellent: "Excelent",
      reasonQuestion: "De ce ai ales această reacție?",
      placeholder: "Spune-ne motivul...",
      inputPlaceholder: "Scrie-ți mesajul aici...",
      thankYou: `
        <p><strong>🙏 Mulțumim mult pentru feedback!</strong> 😊</p>
        <p>În câteva secunde vei fi redirecționat către chatbotul nostru normal. 🕒</p>
      `,
      altText: "Deschide chat"
    },
    EN: {
      question: "How did you find our chatbot?",
      disappointing: "Disappointing",
      acceptable: "Acceptable",
      excellent: "Excellent",
      reasonQuestion: "Why did you choose this reaction?",
      placeholder: "Tell us the reason...",
      inputPlaceholder: "Type your message here...",
      thankYou: `
        <p><strong>🙏 Thank you so much for your feedback!</strong> 😊</p>
        <p>In a few seconds, you will be redirected to our normal chatbot. 🕒</p>
      `,
      altText: "Open chat"
    },
    RU: {
      question: "Как вам показался наш чат-бот?",
      disappointing: "Разочаровывающий",
      acceptable: "Приемлемый",
      excellent: "Отличный",
      reasonQuestion: "Почему вы выбрали эту реакцию?",
      placeholder: "Расскажите нам причину...",
      inputPlaceholder: "Напишите ваше сообщение здесь...",
      thankYou: `
        <p><strong>🙏 Большое спасибо за ваш отзыв!</strong> 😊</p>
        <p>Через несколько секунд вы будете перенаправлены в наш обычный чат-бот. 🕒</p>
      `,
      altText: "Открыть чат"
    }
  };
  
  

  


  const currentTranslations = feedbackTranslations[language as keyof typeof feedbackTranslations];

  // Scroll automat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (open) setVisible(true);
    else {
      const timeout = setTimeout(() => setVisible(false), 300);
      return () => clearTimeout(timeout);
    }
  }, [open]);

  const handleEmojiSelect = (emoji: string) => {
    setSelectedEmoji(emoji);
    setFeedbackStep("reason");
  };

  const handleFeedbackSubmit = async () => {
    if (feedbackReason.trim() !== "" && selectedEmoji) {
      // Adaugă mesaj local (inclusiv Thank you)
      setMessages(prev => [
        ...prev.filter(msg => msg.type !== "feedback"),
        {
          id: Date.now(),
          text: `Emoji: ${selectedEmoji} - ${
            language === "RO" ? "Motiv" : language === "EN" ? "Reason" : "Причина"
          }: ${feedbackReason}`,
          from: "user"
        },
        {
          id: Date.now() + 1,
          text: currentTranslations.thankYou,
          from: "bot"
        }
      ]);
  
      // Trimite la server
      try {
        const response = await fetch("https://digital-grow.onrender.com/feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            emoji: selectedEmoji,
            reason: feedbackReason,
            language,
            email
          })
        });
        if (!response.ok) {
          console.error("Eroare la trimiterea feedback-ului");
        }
      } catch (error) {
        console.error("Fetch error:", error);
      }
  
      // Așteaptă 5 secunde, apoi trimite semnal către părinte
      if (onFeedbackSubmit) {
        setTimeout(() => {
          onFeedbackSubmit({
            emoji: selectedEmoji,
            reason: feedbackReason,
            language
          });
        }, 7000);
      }
  
      // Reset state local
      setFeedbackReason("");
      setFeedbackStep("none");
      setSelectedEmoji("");
    }
  };
  

  const renderFeedbackMessage = () => (
    <div className="livechat-feedback-message">
      <div className="feedback-text">{currentTranslations.question}</div>
      <div className="feedback-emojis">
        <div className="feedback-emoji-option">
          <button
            className={`feedback-emoji-btn ${selectedEmoji === "😠" ? "selected" : ""}`}
            onClick={() => handleEmojiSelect("😠")}
          >
            😠
          </button>
          <span className="feedback-emoji-label">{currentTranslations.disappointing}</span>
        </div>
        <div className="feedback-emoji-option">
          <button
            className={`feedback-emoji-btn ${selectedEmoji === "😊" ? "selected" : ""}`}
            onClick={() => handleEmojiSelect("😊")}
          >
            😊
          </button>
          <span className="feedback-emoji-label">{currentTranslations.acceptable}</span>
        </div>
        <div className="feedback-emoji-option">
          <button
            className={`feedback-emoji-btn ${selectedEmoji === "😍" ? "selected" : ""}`}
            onClick={() => handleEmojiSelect("😍")}
          >
            😍
          </button>
          <span className="feedback-emoji-label">{currentTranslations.excellent}</span>
        </div>
      </div>

      {feedbackStep === "reason" && (
        <>
          <div className="feedback-text">{currentTranslations.reasonQuestion}</div>
          <div className="feedback-input-container">
            <input
              type="text"
              className="feedback-input"
              placeholder={currentTranslations.placeholder}
              value={feedbackReason}
              onChange={e => setFeedbackReason(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") handleFeedbackSubmit(); }}
            />
            <button
              className="feedback-send-btn"
              onClick={handleFeedbackSubmit}
              disabled={!feedbackReason.trim() || !selectedEmoji}
            >
              <img src={sendicon} alt="Send" />
            </button>
          </div>
        </>
      )}
    </div>
  );

  return (
    <div>
      {!open && (
        <img
          src={chatboticon}
          className="feedback-chat-icon"
          alt={currentTranslations.altText}
          onClick={() => setOpen(true)}
          style={{ position: "fixed", right: 40, bottom: 40, width: 80, height: 80, zIndex: 1001, cursor: "pointer" }}
        />
      )}
      {visible && (
        <div className={`feedback-chat-modal${open ? "" : " closed"}`}>
          <img src={livechatopenbg} className="feedback-chat-modal-bg" alt="Live Chat Modal BG" />
          <img
            src={closebutton}
            className="feedback-chat-close-button"
            alt="Close"
            onClick={() => setOpen(false)}
          />
          <div className="feedback-messages-container">
          {messages.map(msg => (
              <div key={msg.id} className={`feedback-chat-message feedback-chat-message-${msg.from}`}>
                {msg.type === "feedback" ? (
                  // Afișezi feedback-ul special (emoji + input)
                  renderFeedbackMessage()
                ) : (
                  // Pentru mesajele normale, dar și pentru "thankYou" care conține HTML, îl afișezi cu innerHTML
                  <div
                    dangerouslySetInnerHTML={{ __html: msg.text }}
                  />
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          
        </div>
      )}
    </div>
  );
};

export default LiveChatFeedback;
