import React, { useState, useRef, useEffect } from 'react';
import { ExportIcon, RefreshIcon, MoreIcon, CloseIcon } from '../icons';

export function ChatInterface({
    messages = [],
    onSendMessage,
    isLoading = false,
    placeholder = "Ask anything about your data..."
}) {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);

    const suggestedQueries = [
        "Show me revenue trends",
        "Find anomalies in sales data",
        "Compare Q1 vs Q2 performance",
        "Predict next quarter"
    ];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = () => {
        if (!input.trim() || isLoading) return;
        onSendMessage(input.trim());
        setInput('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="
      flex flex-col h-full
      bg-[#0A0A0F] rounded-2xl
      border border-[#1E1E2A]
      overflow-hidden
    ">
            {/* Header */}
            <div className="
        flex items-center justify-between
        px-4 py-3 border-b border-[#1E1E2A]
        bg-[#12121A]
      ">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#8B5CF6] to-[#EC4899] flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none">
                            <path d="M12 4C7.58 4 4 6.69 4 10C4 12.02 5.22 13.82 7.1 14.91L6 20L10.3 17.32C10.85 17.44 11.42 17.5 12 17.5C16.42 17.5 20 14.81 20 11.5C20 8.19 16.42 5.5 12 5.5" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-white">Data Assistant</h3>
                        <span className="text-xs text-[#10B981]">Online</span>
                    </div>
                </div>
                <button className="p-1.5 rounded-lg text-[#71717A] hover:text-white hover:bg-[#1A1A24] transition-all">
                    <MoreIcon className="w-4 h-4" />
                </button>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center py-8">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#3B82F6]/20 to-[#8B5CF6]/20 flex items-center justify-center mb-4">
                            <svg className="w-8 h-8 text-[#3B82F6]" viewBox="0 0 24 24" fill="none">
                                <path d="M12 4C7.58 4 4 6.69 4 10C4 12.02 5.22 13.82 7.1 14.91L6 20L10.3 17.32C10.85 17.44 11.42 17.5 12 17.5C16.42 17.5 20 14.81 20 11.5C20 8.19 16.42 5.5 12 5.5" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                            </svg>
                        </div>
                        <h4 className="text-lg font-semibold text-white mb-2">How can I help you analyze your data?</h4>
                        <p className="text-sm text-[#71717A] max-w-md mb-6">
                            Ask questions about your datasets, generate insights, and create visualizations with natural language.
                        </p>

                        {/* Suggested Queries */}
                        <div className="flex flex-wrap gap-2 justify-center">
                            {suggestedQueries.map((query, index) => (
                                <button
                                    key={index}
                                    onClick={() => setInput(query)}
                                    className="
                    px-3 py-1.5 rounded-full
                    bg-[#1A1A24] border border-[#2A2A3A]
                    text-xs text-[#A1A1AA]
                    hover:bg-[#22222E] hover:text-white hover:border-[#3A3A4A]
                    transition-all duration-200
                  "
                                >
                                    {query}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    messages.map((message, index) => (
                        <MessageBubble key={index} message={message} />
                    ))
                )}

                {isLoading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#8B5CF6] to-[#EC4899] flex items-center justify-center flex-shrink-0">
                            <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none">
                                <circle cx="8" cy="12" r="1.5" fill="currentColor" />
                                <circle cx="12" cy="12" r="1.5" fill="currentColor" />
                                <circle cx="16" cy="12" r="1.5" fill="currentColor" />
                            </svg>
                        </div>
                        <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl rounded-tl-md px-4 py-3">
                            <div className="flex gap-1">
                                <span className="w-2 h-2 bg-[#3B82F6] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <span className="w-2 h-2 bg-[#3B82F6] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <span className="w-2 h-2 bg-[#3B82F6] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-[#1E1E2A] bg-[#12121A]">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        disabled={isLoading}
                        className="
              flex-1 h-11 px-4
              bg-[#1A1A24] border border-[#2A2A3A]
              rounded-xl text-sm text-white
              placeholder:text-[#52525B]
              focus:outline-none focus:border-[#3B82F6]
              focus:ring-1 focus:ring-[#3B82F6]/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isLoading}
                        className="
              px-5 h-11 rounded-xl
              bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6]
              text-white font-medium text-sm
              hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
              flex items-center gap-2
            "
                    >
                        <span>Send</span>
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none">
                            <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
}

function MessageBubble({ message }) {
    const isUser = message.role === 'user';

    return (
        <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
            {/* Avatar */}
            <div className={`
        w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
        ${isUser
                    ? 'bg-[#3B82F6]'
                    : 'bg-gradient-to-br from-[#8B5CF6] to-[#EC4899]'
                }
      `}>
                {isUser ? (
                    <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
                        <path d="M5 20C5 16.13 8.13 13 12 13C15.87 13 19 16.13 19 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                ) : (
                    <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none">
                        <circle cx="8" cy="12" r="1.5" fill="currentColor" />
                        <circle cx="12" cy="12" r="1.5" fill="currentColor" />
                        <circle cx="16" cy="12" r="1.5" fill="currentColor" />
                    </svg>
                )}
            </div>

            {/* Message Content */}
            <div className={`
        max-w-[75%] rounded-2xl px-4 py-3
        ${isUser
                    ? 'bg-[#3B82F6] text-white rounded-tr-md'
                    : 'bg-[#12121A] border border-[#1E1E2A] text-[#E5E7EB] rounded-tl-md'
                }
      `}>
                <div className="text-sm whitespace-pre-wrap">{message.content}</div>

                {/* Response Actions (for assistant messages) */}
                {!isUser && message.showActions && (
                    <div className="flex gap-2 mt-3 pt-3 border-t border-[#2A2A3A]">
                        <button className="
              flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg
              bg-[#1A1A24] border border-[#2A2A3A]
              text-xs text-[#A1A1AA]
              hover:bg-[#22222E] hover:text-white
              transition-all duration-200
            ">
                            <ExportIcon className="w-3.5 h-3.5" />
                            Export
                        </button>
                        <button className="
              flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg
              bg-[#1A1A24] border border-[#2A2A3A]
              text-xs text-[#A1A1AA]
              hover:bg-[#22222E] hover:text-white
              transition-all duration-200
            ">
                            <RefreshIcon className="w-3.5 h-3.5" />
                            Regenerate
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default ChatInterface;
