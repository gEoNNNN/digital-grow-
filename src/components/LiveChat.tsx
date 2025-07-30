import React, { useState, useRef, useEffect } from "react";
import "./LiveChat.css";
import livechatopenbg from "../assets/Group 71.png"
import closebutton from "../assets/closebutton.svg"
import sendicon from "../assets/sendicon.svg"
import chatboticon from "../assets/chatlogo.svg"

type ChatMessage = {
  id: number;
  text: string;
  from: "user" | "bot";
};

const initialMessages: ChatMessage[] = [
  { id: 1, text: "👋 Bun venit pe site-ul Lumea Ta! Cu ce te pot ajuta astăzi?", from: "bot" },
];

interface LiveChatProps {
  open?: boolean;
  setOpen?: (open: boolean) => void;
}

const LiveChat: React.FC<LiveChatProps> = ({ open: controlledOpen, setOpen: setControlledOpen }) => {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = setControlledOpen || setInternalOpen;

  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
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
      // Wait for animation before removing from DOM
      const timeout = setTimeout(() => setVisible(false), 300);
      return () => clearTimeout(timeout);
    }
  }, [open]);

  const handleSend = () => {
    if (message.trim() !== "") {
      setMessages(prev => [
        ...prev,
        { id: Date.now(), text: message, from: "user" }
      ]);
      setMessage("");
    }
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
                {msg.text}
              </div>
            ))}
            {/* Invisible element to scroll to */}
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
export default LiveChat;