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

const initialMessages: ChatMessage[] = [];

interface LiveChatProps {
  open?: boolean;
  setOpen?: (open: boolean) => void;
}

declare global {
  interface Window {
    language: string;
  }
}

const LiveChat: React.FC<LiveChatProps> = ({ open: controlledOpen, setOpen: setControlledOpen }) => {
  const [mess, setMess] = useState<string | null>(null);
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const [onboardingStep, setOnboardingStep] = useState<number>(0);
  const setOpen = setControlledOpen || setInternalOpen;
  const [loading, setLoading] = useState(false);

  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const storedLang = localStorage.getItem("language");
    if (storedLang) {
      window.language = storedLang;
      console.log("Limba restaurată din localStorage:", window.language);
    } else {
      console.log("⚠️ Limba nu a fost găsită în localStorage!");
    }
  }, []);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const typeHtmlMessage = (htmlString: string) => {
    const id = Date.now();
    setMessages(prev => [...prev, { id, text: "", from: "bot" }]);
  
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, "text/html");
  
    // Extragem nodurile din body, le procesăm în ordine
    const nodes = Array.from(doc.body.childNodes);
  
    let output = "";
  
    const processNode = (node: ChildNode, doneCallback: () => void) => {
      if (node.nodeType === Node.TEXT_NODE) {
        // Text node - facem typing caracter cu caracter
        const text = node.textContent || "";
        let i = 0;
        const interval = setInterval(() => {
          i++;
          output += text[i - 1];
          setMessages(prev =>
            prev.map(msg =>
              msg.id === id ? { ...msg, text: output } : msg
            )
          );
          if (i >= text.length) {
            clearInterval(interval);
            doneCallback();
          }
        }, 20);
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        // Nod element: îl serializăm complet și îl adăugăm instant
        const el = node as HTMLElement;
        output += el.outerHTML;
        setMessages(prev =>
          prev.map(msg =>
            msg.id === id ? { ...msg, text: output } : msg
          )
        );
        // Instant continuăm
        doneCallback();
      } else {
        doneCallback();
      }
    };
  
    // Procesăm nodurile unul câte unul, în serie
    const processNodesSequentially = (index: number) => {
      if (index >= nodes.length) return;
      processNode(nodes[index], () => processNodesSequentially(index + 1));
    };
  
    processNodesSequentially(0);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendStartRequest = (name: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, message }),
    })
      .then((res) => res.json())
      .then((data) => {
        window.language = data.language;
        localStorage.setItem("language", data.language);
  
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
  
        typeHtmlMessage(data.ask_name || "Cum te numești?");
  
        setMess(name);
        setOnboardingStep(1);
      })
      .catch((err) => {
        setMessages((prev) => [
          ...prev.filter((m) => m.id !== typingId),
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendInterestsDetailRequest = (userName: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: " . . . ",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/interests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          // Apelează funcția typeHtmlMessage în loc să elimin typingMsg din mesaje

          setMessages((prev) => prev.filter((m) => m.id !== typingId));

          typeHtmlMessage(data.ask_interests || "Cum te numești?");
  
          const text = data.ask_interests;

          if (
            text.includes("Mǎ bucur că vrei să plasezi o comandă!") ||
            text.includes("Мне приятно, что вы хотите сделать заказ!") ||
            text.includes("I'm glad you want to place an order!")
          ) {
            setOnboardingStep(15);
            return;
          }
  
          if (
            text.includes("Landing Page One-Page") ||
            text.includes("Site Simplu (3–5 pagini)") ||
            text.includes("Одностраничный сайт (лендинг-пейдж)") ||
            text.includes("Простой сайт (3–5 страниц)") ||
            text.includes("Simple Website (3–5 pages)")
          ) {
            setOnboardingStep(2);
            return;
          } else if (
            text.includes("Haide să alegem un buget") ||
            text.includes("Давайте выберем подходящий бюджет") ||
            text.includes("Let's choose a suitable budget")
          ) {
            setOnboardingStep(5);
            return;
          } else if (
            text.includes("Te rugăm să ne spui dacă") ||
            text.includes("Пожалуйста, скажите, хотите ли вы:") ||
            text.includes("Please let us know")
          ) {
            setOnboardingStep(1);
            return;
          } else if (
            text.includes("Cum ai dori să continuăm?") ||
            text.includes("Как вы хотите продолжить?") ||
            text.includes("How would you like to continue?")
          ) {
            setOnboardingStep(4);
            return;
          }
        }, 1000);
      })
      .catch((err) => {
        // Elimină mesajul typing și afișează eroarea
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendCriteriaRequest = (userName: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/criteria", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Ce urmează?");
  
          const text = data.message || "";
  
          if (
            text.includes("Landing Page One-Page") ||
            text.includes("Site Simplu (3–5 pagini)") ||
            text.includes("Одностраничный сайт (лендинг-пейдж)") ||
            text.includes("Простой сайт (3–5 страниц)") ||
            text.includes("Simple Website (3–5 pages)")
          ) {
            setOnboardingStep(2);
          } else if (
            text.includes("Haide să alegem un buget") ||
            text.includes("Давайте выберем подходящий бюджет") ||
            text.includes("Let's choose a suitable budget")
          ) {
            setOnboardingStep(5);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendWelcomeRequest = (userName: string, userInterests: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/welcome", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Bun venit!");
  
          const text = data.message || "";
  
          if (
            text.includes("Dacă vrei detalii despre ") ||
            text.includes("Если хотите узнать детали о") ||
            text.includes("If you'd like to see details")
          ) {
            setOnboardingStep(3);
          } else if (
            text.includes("Landing Page One-Page") ||
            text.includes("Site Simplu (3–5 pagini)") ||
            text.includes("Одностраничный сайт (лендинг-пейдж)") ||
            text.includes("Простой сайт (3–5 страниц)") ||
            text.includes("Simple Website (3–5 pages)")
          ) {
            setOnboardingStep(2);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendChatRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
  
          if (
            text.includes("Doriți să plasați o comandă pentru serviciul") ||
            text.includes("Хотите оформить заказ на услугу") ||
            text.includes("Would you like to place an order for the")
          ) {
            setOnboardingStep(20);
            return;
          }
          if (
            text.includes("Mǎ bucur că vrei să plasezi o comandă!") ||
            text.includes("Рад(а), что вы хотите сделать заказ!") ||
            text.includes("I'm glad you want to place an order!")
          ) {
            setOnboardingStep(15);
            return;
          }
          if (
            text.includes("Landing Page One-Page") ||
            text.includes("Site Simplu (3–5 pagini)") ||
            text.includes("Одностраничный сайт (лендинг-пейдж)") ||
            text.includes("Простой сайт (3–5 страниц)") ||
            text.includes("Simple Website (3–5 pages)")
          ) {
            setOnboardingStep(2);
          } else if (
            text.includes("Îți pot oferi o gamă variată de servicii IT specializate.") ||
            text.includes("Я могу предложить вам широкий спектр IT-услуг.") ||
            text.includes("I can offer you a wide range of IT services.")
          ) {
            setOnboardingStep(2);
          } else if (
            text.includes("Haide să alegem un buget") ||
            text.includes("Давайте выберем подходящий бюджет") ||
            text.includes("Let's choose a suitable budget")
          ) {
            setOnboardingStep(5);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendBudgetRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
  
          if (
            text.includes("Apropo, ca să pot veni cu sugestii potrivite") ||
            text.includes("Кстати, чтобы предложить оптимальные варианты") ||
            text.includes("By the way, to offer the most suitable options")
          ) {
            setOnboardingStep(5);
          } else {
            setOnboardingStep(6);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendPreferenceLanguageRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/preference_language", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
  
          if (
            text.includes("Ca să-ți ofer informațiile cât mai potrivit") ||
            text.includes("Чтобы дать тебе максимально точную информацию") ||
            text.includes("To offer you the most relevant information")
          ) {
            setOnboardingStep(6);
          } else {
            setOnboardingStep(7);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendFunctionalitiesRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/functionalities", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
  
          if (
            text.includes("❗️ Din ce ai scris, nu am reușit") ||
            text.includes("❗️ Из того, что вы написали, я не смог") ||
            text.includes("From what you wrote, I couldn’t quite identify")
          ) {
            setOnboardingStep(7);
          } else if (
            text.includes("Dorești să faci o comandă") ||
            text.includes("Хотите сделать заказ?") ||
            text.includes("Do you want to make an order?")
          ) {
            setOnboardingStep(8);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendComandaRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/comanda", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
  
          if (
            text.includes("Alegeți unul dintre următoarele produse pentru a plasa o comandă") ||
            text.includes("Выберите один из следующих продуктов для размещения заказа") ||
            text.includes("Choose one of the following products to place an order:")
          ) {
            setOnboardingStep(21);
            return;
          }
          if (
            text.includes("Dacă vrei detalii despre") ||
            text.includes("Если хотите узнать подробнее") ||
            text.includes("If you want to know more about")
          ) {
            setOnboardingStep(1);
            return;
          } else if (
            text.includes("Nu mi-e clar dacă vrei") ||
            text.includes("Мне не совсем понятно") ||
            text.includes("I'm not sure if you want to place an order")
          ) {
            setOnboardingStep(8);
            return;
          } else {
            setOnboardingStep(12);
            return;
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendCheckNameSurnameRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/check_name_surname", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
          if (
            text.includes("Mulțumim! Ai un nume frumos!") ||
            text.includes("Спасибо! У тебя красивое имя!") ||
            text.includes("Thank you! You have a nice name!")
          ) {
            setOnboardingStep(11);
          } else if (
            text.includes("Introdu, te rog") ||
            text.includes("Пожалуйста, введите") ||
            text.includes("Please, enter")
          ) {
            setOnboardingStep(10);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendPhoneNumberRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/numar_de_telefon", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
          if (
            text.includes("Numărul tău a fost salvat cu succes!") ||
            text.includes("Номер телефона успешно сохранен!") ||
            text.includes("Your phone number has been successfully saved!")
          ) {
            setOnboardingStep(14);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendShowProductRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/afiseaza_produs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
          if (
            text.includes("Iată toate detaliile despre") ||
            text.includes("Вот все детали о") ||
            text.includes("Here are all the details about")
          ) {
            setOnboardingStep(13);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendConfirmProductRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/confirma_produs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
          if (
            text.includes("Landing Page One-Page") ||
            text.includes("Site Simplu (3–5 pagini)") ||
            text.includes("Одностраничный сайт (лендинг-пейдж)") ||
            text.includes("Простой сайт (3–5 страниц)") ||
            text.includes("Simple Website (3–5 pages)")
          ) {
            setOnboardingStep(12);
          } else if (
            text.includes("Serviciul a fost salvat cu succes") ||
            text.includes("Заказ успешно сохранен") ||
            text.includes("The service has been successfully saved!")
          ) {
            setOnboardingStep(10);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendEmailRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
          if (
            text.includes("Am notat toate datele importante și totul este pregătit.") ||
            text.includes("Все важные данные записаны, всё готово") ||
            text.includes("All the important details are saved and everything is ready")
          ) {
            setOnboardingStep(1);
          } else {
            setOnboardingStep(14);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendComandaInceputRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/comanda_inceput", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
          if (
            text.includes("Iată toate detaliile despre") ||
            text.includes("Вот все детали о") ||
            text.includes("Here are all the details about")
          ) {
            setOnboardingStep(13);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendProdusIntrebareRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/produs_intrebare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
  
          if (
            text.includes("Serviciul a fost salvat cu succes!") ||
            text.includes("Заказ успешно сохранен!") ||
            text.includes("The service has been successfully saved!")
          ) {
            setOnboardingStep(10);
            return;
          }
  
          if (
            text.includes("Landing Page One-Page") ||
            text.includes("Site Simplu (3–5 pagini)") ||
            text.includes("Одностраничный сайт (лендинг-пейдж)") ||
            text.includes("Простой сайт (3–5 страниц)") ||
            text.includes("Simple Website (3–5 pages)")
          ) {
            setOnboardingStep(12);
            return;
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendSelecteazaProdusRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/selecteaza_produs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          typeHtmlMessage(data.message || "Răspuns chatbot");
  
          const text = data.message || "";
          if (
            text.includes("Serviciul a fost salvat cu succes!") ||
            text.includes("Сервис успешно сохранен!") ||
            text.includes("The service has been successfully saved!")
          ) {
            setOnboardingStep(10);
          }
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };

  const sendIpRequest = (userName: string, userInterests: string, message: string) => {
    const typingId = Date.now();
    const typingMsg: ChatMessage = {
      id: typingId,
      text: "...",
      from: "bot",
    };
  
    setMessages((prev) => [...prev, typingMsg]);
  
    return fetch("http://127.0.0.1:5000/ip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: userName, interests: userInterests, message, language: window.language }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTimeout(() => {
          setMessages((prev) => prev.filter((m) => m.id !== typingId));
          // Afișează doar IP-ul primit, fără mesaj text suplimentar
          typeHtmlMessage(data.ip || "IP necunoscut");
        }, 1000);
      })
      .catch((err) => {
        setMessages((prev) => prev.filter((m) => m.id !== typingId));
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), text: "Eroare la inițializare: " + err.message, from: "bot" },
        ]);
      });
  };



  // const sendStartRequest = (name: string) => {
  //   return fetch("https://lumea-mea.onrender.com/start", {
  //     method: "POST",
  //     headers: { "Content-Type": "application/json" },
  //     body: JSON.stringify({ name }),
  //   })
  //     .then((res) => res.json())
  //     .then((data) => {
  //       const botMsg: ChatMessage = {
  //         id: Date.now(),
  //         text: data.ask_name || "Cum te numești?",
  //         from: "bot",
  //       };
  //       // const language = data.language;
  //       // window.language = language;
  //         // localStorage.setItem("language", language);
  //       window.language = data.language
  //       localStorage.setItem("language", data.language);
  //       setMessages((prev) => [...prev, botMsg]);
  //       setMess(name);
  //       setOnboardingStep(1);
  //     });
  // };

  React.useEffect(() => {
    if (open) setVisible(true);
    else {
      // Wait for animation before removing from DOM
      const timeout = setTimeout(() => setVisible(false), 300);
      return () => clearTimeout(timeout);
    }
  }, [open]);

  const handleSend = async () => {
    

    if (message.trim() !== "") {
      setMessages(prev => [
        ...prev,
        { id: Date.now(), text: message, from: "user" }
      ]);
      setMessage("");
    }
    setLoading(true);

    const currentStep = onboardingStep;

    try {
      switch (currentStep) {
        case -1:
          await sendStartRequest(message);
          break;
        case 1:
          await sendInterestsDetailRequest(message);
          break;
        case 4:
          await sendCriteriaRequest(message, message);
          break;
        case 2:
          await sendWelcomeRequest(message, message);
          break;
        case 3:
          await sendChatRequest(message, message, message);
          break;
        case 5:
          await sendBudgetRequest(message, message, message)
          break;
        case 6:
          await sendPreferenceLanguageRequest(message, message, message)
          break;
        case 7:
          await sendFunctionalitiesRequest(message, message, message);
          break;
        case 8:
          await sendComandaRequest(message, message, message);
          break;
        case 10:
          await sendCheckNameSurnameRequest(message, message, message);
          break;
        case 11:
          await sendPhoneNumberRequest(message, message, message);
          break;
        case 12:
          await sendShowProductRequest(message, message, message);
          break;
        case 13:
          await sendConfirmProductRequest(message, message, message);
          break;
        case 14:
          await sendEmailRequest(message, message, message);
          break;
        case 15:
          await sendComandaInceputRequest(message, message, message);
          break;
        case 20:
          await sendProdusIntrebareRequest(message, message, message);
          break;
        case 21:
          await sendSelecteazaProdusRequest(message, message, message);
          break;
        case 40:
          await sendIpRequest(message, message, message);
          break;
        
        default:
          // fallback chat simplu
          console.log("1");
      }
    } catch (error: any) {
      console.error("Eroare:", error);
      const errMsg: ChatMessage = {
        id: Date.now(),
        text: "Eroare la comunicarea cu serverul.",
        from: "bot",
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
      setMessage("");
    }
  };

  useEffect(() => {
    scrollToBottom();
    if (open) {
      setVisible(true);
      if (messages.length === 0 && onboardingStep === 0) {
        setLoading(true);
        fetch("http://127.0.0.1:5000/language")
          .then((res) => res.json())
          .then((data) => {
            // window.language = data.language || "RO";
            const botMsg: ChatMessage = {
              id: Date.now(),
              text: data.ask_name || "Bun venit! Care este numele tău?",
              from: "bot",
            };
            setMessages([botMsg]);
            setOnboardingStep(-1);
          })
          .catch(() => {
            const errMsg: ChatMessage = {
              id: Date.now(),
              text: "Eroare la comunicarea cu serverul.",
              from: "bot",
            };
            setMessages([errMsg]);
          })
          .finally(() => setLoading(false));
      }
    } else {
      const timeout = setTimeout(() => setVisible(false), 300);
      return () => clearTimeout(timeout);
    }
  }, [open]);


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
              dangerouslySetInnerHTML={{ __html: msg.text }}
            />
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