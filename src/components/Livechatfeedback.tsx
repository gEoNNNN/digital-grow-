import React, { useState, useRef, useEffect } from "react";
import "./Livechatfeedback.css";
import livechatopenbg from "../assets/Group 71feedback.png"
import closebutton from "../assets/closebutton.svg"
import sendicon from "../assets/sendicon.svg"
import chatboticon from "../assets/chatlogo.svg"
import { useLanguage } from "./LanguageContext";

type ChatMessage = {
  id: number;
  text: string;
  from: "user" | "bot";
  type?: "feedback" | "normal";
};

const initialMessages: ChatMessage[] = [
  { id: 1, text: "feedback", from: "bot", type: "feedback" } // Special feedback message
];

interface LiveChatFeedbackProps {
  open?: boolean;
  setOpen?: (open: boolean) => void;
}

const LiveChatFeedback: React.FC<LiveChatFeedbackProps> = ({ 
  open: controlledOpen, 
  setOpen: setControlledOpen
}) => {
  const { language } = useLanguage();
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = setControlledOpen || setInternalOpen;

  const [visible, setVisible] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [feedbackStep, setFeedbackStep] = useState<"none" | "emoji" | "reason">("emoji");
  const [selectedEmoji, setSelectedEmoji] = useState("");
  const [feedbackReason, setFeedbackReason] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Translations for feedback
  const feedbackTranslations = {
    RO: {
      question: "Cum ți s-a părut chatbot-ul?",
      disappointing: "Dezamăgitor",
      acceptable: "Acceptabil", 
      excellent: "Excelent",
      reasonQuestion: "De ce ai ales această reacție?",
      placeholder: "Spune-ne motivul...",
      inputPlaceholder: "Scrie-ți mesajul aici...",
      thankYou: "Mulțumim pentru feedback! Ne ajută să îmbunătățim serviciile noastre.",
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
      thankYou: "Thank you for your feedback! It helps us improve our services.",
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
      thankYou: "Спасибо за отзыв! Это помогает нам улучшать наши услуги.",
      altText: "Открыть чат"
    }
  };

  const currentTranslations = feedbackTranslations[language as keyof typeof feedbackTranslations];

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  React.useEffect(() => {
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

  const handleFeedbackSubmit = () => {
    if (feedbackReason.trim() !== "" && selectedEmoji) {
      // Add user's complete feedback response
      setMessages(prev => [
        ...prev.filter(msg => msg.type !== "feedback"), // Remove the feedback message
        { 
          id: Date.now(), 
          text: `Emoji: ${selectedEmoji} - ${language === 'RO' ? 'Motiv' : language === 'EN' ? 'Reason' : 'Причина'}: ${feedbackReason}`, 
          from: "user" 
        },
        { 
          id: Date.now() + 1, 
          text: currentTranslations.thankYou, 
          from: "bot" 
        }
      ]);
      setFeedbackReason("");
      setFeedbackStep("none");
      setSelectedEmoji("");
    }
  };

  const renderFeedbackMessage = () => {
    return (
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
  };

  return (
    <div>
      {!open && (
        <img
          src={chatboticon}
          className="feedback-chat-icon"
          alt={currentTranslations.altText}
          onClick={() => setOpen(true)}
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
          {/* Messages container */}
          <div className="feedback-messages-container">
            {messages.map(msg => (
              <div
                key={msg.id}
                className={`feedback-chat-message feedback-chat-message-${msg.from} ${msg.type === "feedback" ? "feedback-chat-message-special" : ""}`}
              >
                {msg.type === "feedback" ? renderFeedbackMessage() : msg.text}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}
    </div>
  );
}
export default LiveChatFeedback;