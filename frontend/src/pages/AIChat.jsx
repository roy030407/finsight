import { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import api from "@/api/axios";
import useStore from "@/store";

export default function AIChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const { auth } = useStore();

  // Set page title
  useEffect(() => {
    document.title = "FinSight | AI Chat";
  }, []);

  const suggestedQuestions = [
    "What's my savings rate?",
    "How do I build an emergency fund?",
    "Explain SIP investing",
    "How can I reduce my Food spending?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const formatTimestamp = (date) => {
    return new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    }).format(date);
  };

  const handleSendMessage = async (messageText = input) => {
    if (!messageText.trim()) return;

    const userMessage = {
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.post("/chat/", { message: messageText });
      
      const aiMessage = {
        role: "assistant",
        content: response.data.reply,
        timestamp: new Date(),
        sourcesUsed: response.data.sources_used,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      console.error("Error response:", error.response?.data);
      console.error("Error status:", error.response?.status);
      
      const errorMessage = {
        role: "assistant",
        content: "Sorry, I couldn't connect. Please try again.",
        timestamp: new Date(),
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question) => {
    handleSendMessage(question);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message, index) => {
    const isUser = message.role === "user";
    const isAI = message.role === "assistant";

    return (
      <div
        key={index}
        className={`flex ${
          message.role === "user" ? "justify-end" : "justify-start"
        }`}
      >
        <div
          className={`max-w-[80%] rounded-lg px-4 py-2 ${
            message.role === "user"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-900"
          }`}
        >
          <div className="flex items-start gap-2">
            {message.role === "assistant" && (
              <Bot className="w-5 h-5 mt-0.5 flex-shrink-0" />
            )}
            <div>
              {message.content}
              {message.sourcesUsed && (
                <div className="text-xs opacity-75 mt-1">
                  Sources: {message.sourcesUsed}
                </div>
              )}
            </div>
            {message.role === "user" && (
              <User className="w-5 h-5 mt-0.5 flex-shrink-0" />
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderWelcomeState = () => (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center max-w-md">
        <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
          <Bot className="w-8 h-8 text-blue-600" />
        </div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
          Hi {auth?.user?.username || "there"}, ask me anything about your finances
        </h2>
        <div className="grid grid-cols-1 gap-2 mt-6">
          {suggestedQuestions.map((question, index) => (
            <button
              key={index}
              onClick={() => handleSuggestedQuestion(question)}
              className="text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors border border-gray-200"
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-semibold">AI Financial Assistant</h1>
        <p className="text-gray-600">Get personalized financial advice powered by AI</p>
      </div>

      <div className="flex-1 bg-white rounded-lg border border-gray-200 flex flex-col">
        {messages.length === 0 ? (
          renderWelcomeState()
        ) : (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.role === "assistant" && (
                      <Bot className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    )}
                    <div>
                      {message.content}
                      {message.sourcesUsed && (
                        <div className="text-xs opacity-75 mt-1">
                          Sources: {message.sourcesUsed}
                        </div>
                      )}
                    </div>
                    {message.role === "user" && (
                      <User className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    )}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="mt-4 border-t pt-4">
        <div className="flex gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your finances..."
            className="flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={1}
            style={{ minHeight: "40px", maxHeight: "120px" }}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </div>
        <div className="text-xs text-gray-500 mt-2 text-center">
          FinSight AI • Powered by Gemini
        </div>
      </div>
    </div>
  );
}
