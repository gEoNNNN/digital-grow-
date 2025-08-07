import React, { useState, useRef, useEffect } from "react";
import "./Livechatfeedback.css";
import livechatopenbg from "../assets/Group 71.png"
import closebutton from "../assets/closebutton.svg"
import sendicon from "../assets/sendicon.svg"
import chatboticon from "../assets/chatlogo.svg"

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
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = setControlledOpen || setInternalOpen;

  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [feedbackStep, setFeedbackStep] = useState<"none" | "emoji" | "reason">("emoji");
  const [selectedEmoji, setSelectedEmoji] = useState("");
  const [feedbackReason, setFeedbackReason] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
          text: `Emoji: ${selectedEmoji} - Motiv: ${feedbackReason}`, 
          from: "user" 
        },
        { 
          id: Date.now() + 1, 
          text: "Mulțumim pentru feedback! Ne ajută să îmbunătățim serviciile noastre.", 
          from: "bot" 
        }
      ]);
      setFeedbackReason("");
      setFeedbackStep("none");
      setSelectedEmoji("");
    }
  };

  const handleSend = () => {
    if (feedbackStep === "reason") {
      handleFeedbackSubmit();
    } else if (message.trim() !== "") {
      setMessages(prev => [
        ...prev,
        { id: Date.now(), text: message, from: "user" }
      ]);
      setMessage("");
    }
  };

  const renderFeedbackMessage = () => {
    return (
      <div className="livechat-feedback-message">
        <div className="feedback-text">Cum ți s-a părut chatbot-ul?</div>
        
        <div className="feedback-emojis">
          <div className="feedback-emoji-option">
            <button 
              className={`feedback-emoji-btn ${selectedEmoji === "😠" ? "selected" : ""}`}
              onClick={() => handleEmojiSelect("😠")}
            >
              😠
            </button>
            <span className="feedback-emoji-label">Dezamăgitor</span>
          </div>
          
          <div className="feedback-emoji-option">
            <button 
              className={`feedback-emoji-btn ${selectedEmoji === "😊" ? "selected" : ""}`}
              onClick={() => handleEmojiSelect("😊")}
            >
              😊
            </button>
            <span className="feedback-emoji-label">Acceptabil</span>
          </div>
          
          <div className="feedback-emoji-option">
            <button 
              className={`feedback-emoji-btn ${selectedEmoji === "😍" ? "selected" : ""}`}
              onClick={() => handleEmojiSelect("😍")}
            >
              😍
            </button>
            <span className="feedback-emoji-label">Excelent</span>
          </div>
        </div>

        {feedbackStep === "reason" && (
          <>
            <div className="feedback-text">De ce ai ales această reacție?</div>
            <div className="feedback-input-container">
              <input
                type="text"
                className="feedback-input"
                placeholder="Spune-ne motivul..."
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
          className="livechat-chatboticon"
          alt="Deschide chat"
          onClick={() => setOpen(true)}
          style={{ position: "fixed", right: 40, bottom: 40, width: 80, height: 80, zIndex: 1001, cursor: "pointer" }}
        />
      )}
      {visible && (
        <div className={`livechat-modal${open ? "" : " closed"}`}>
          <img src={livechatopenbg} className="livechat-modal-bg" alt="Live Chat Modal BG" />
          <img
            src={closebutton}
            className="livechat-close-button"
            alt="Close"
            onClick={() => setOpen(false)}
          />
          {/* Messages container */}
          <div className="livechat-messages">
            {messages.map(msg => (
              <div
                key={msg.id}
                className={`livechat-message livechat-message-${msg.from}`}
              >
                {msg.type === "feedback" ? renderFeedbackMessage() : msg.text}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div className="livechat-input-row">
            <input
              type="text"
              className="livechat-input"
              placeholder="Scrie-ți mesajul aici..."
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") handleSend(); }}
            />
            <button
              className="livechat-send-btn"
              onClick={handleSend}
              type="button"
              aria-label="Trimite mesaj"
            >
              <img src={sendicon} alt="Send" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
export default LiveChatFeedback;