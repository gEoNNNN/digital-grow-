// pages/FeedbackPage.tsx
import { useState } from "react";
import LiveChatFeedback from "../components/LiveChatFeedback";
import LiveChat from "../components/LiveChat";

export default function FeedbackPage() {
  const [showChat, setShowChat] = useState(false);

  return showChat ? (
    <LiveChat />
  ) : (
    <LiveChatFeedback onFeedbackComplete={() => setShowChat(true)} />
  );
}