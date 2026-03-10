import React, { useState, useRef, useEffect } from 'react';
import './ChatBot.css';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
}

const ChatBot: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: '👋 Hello! I\'m your AI Trading Assistant. I can help you with stock prices, analysis, and trading. Try asking me something like "What is the price of AAPL?" or "Analyze TSLA".',
            sender: 'bot',
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            text: input,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || "http://localhost:8000"}/market/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    user_id: 'default_user',
                }),
            });

            const data = await response.json();

            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: data.data.response,
                sender: 'bot',
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: '❌ Sorry, I encountered an error. Please try again.',
                sender: 'bot',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const quickActions = [
        'What is the price of AAPL?',
        'Analyze TSLA',
        'Show my portfolio',
        'Buy 10 shares of MSFT',
    ];

    return (
        <div className="chatbot-container fade-in">
            <div className="chatbot-header">
                <div className="chatbot-title">
                    <span className="chatbot-icon">🤖</span>
                    <h2>AI Trading Assistant</h2>
                </div>
                <div className="chatbot-status">
                    <span className="status-dot"></span>
                    <span>Online</span>
                </div>
            </div>

            <div className="quick-actions-bar">
                <span className="quick-label">Quick Actions:</span>
                <div className="quick-buttons">
                    {quickActions.map((action, index) => (
                        <button
                            key={index}
                            className="quick-btn"
                            onClick={() => setInput(action)}
                        >
                            {action}
                        </button>
                    ))}
                </div>
            </div>

            <div className="messages-container">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
                    >
                        <div className="message-avatar">
                            {message.sender === 'user' ? '👤' : '🤖'}
                        </div>
                        <div className="message-content">
                            <div className="message-text">{message.text}</div>
                            <div className="message-time">
                                {message.timestamp.toLocaleTimeString([], {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                })}
                            </div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="message bot-message">
                        <div className="message-avatar">🤖</div>
                        <div className="message-content">
                            <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-container">
                <textarea
                    className="chat-input"
                    placeholder="Ask me anything about stocks, trading, or your portfolio..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    rows={1}
                />
                <button
                    className="send-btn"
                    onClick={sendMessage}
                    disabled={!input.trim() || loading}
                >
                    <span className="send-icon">📤</span>
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatBot;
