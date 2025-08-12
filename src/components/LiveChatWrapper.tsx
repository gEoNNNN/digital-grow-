// LiveChatWrapper.tsx
import React, { useState } from "react";
import LiveChatFeedback from "./Livechatfeedback";
import LiveChat from "./LiveChat";

interface LiveChatWrapperProps {
  open?: boolean;
  setOpen?: (open: boolean) => void;
}

const LiveChatWrapper: React.FC<LiveChatWrapperProps> = ({ open, setOpen }) => {
  const [feedbackGiven, setFeedbackGiven] = useState(false);

  const handleFeedbackSubmit = (data: { emoji: string; reason: string; language: string }) => {
    console.log("Feedback trimis:", data);
    setFeedbackGiven(true); // trece în modul chat normal
  };

  if (!feedbackGiven) {
    return (
      <LiveChatFeedback
        open={open}
        setOpen={setOpen}
        onFeedbackSubmit={handleFeedbackSubmit}
      />
    );
  }

  return <LiveChat open={open} setOpen={setOpen} />;
};

export default LiveChatWrapper;
