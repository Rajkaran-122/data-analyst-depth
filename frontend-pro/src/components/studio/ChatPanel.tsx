import React, { useRef, useEffect } from 'react';
import { Send, Bot, User, X, Sparkles, Terminal } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useCopilotStore } from '@/stores/copilotStore';
import { useStudioStore } from '@/stores/studioStore';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

// Simple mocked Input/Button removed in favor of Shadcn components

export function ChatPanel() {
    const { messages, isLoading, sendMessage, isOpen, toggleChat } = useCopilotStore();
    const { setSql } = useStudioStore(); // To inject code
    const [input, setInput] = React.useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || isLoading) return;

        const val = input;
        setInput('');
        await sendMessage(val);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    // Extract SQL blocks to add "Run" buttons (Simple regex for demo)
    const renderContent = (content: string) => {
        return (
            <ReactMarkdown
                components={{
                    code({ node, inline, className, children, ...props }: any) {
                        const match = /language-(\w+)/.exec(className || '');
                        const isSql = match && match[1] === 'sql';
                        const codeText = String(children).replace(/\n$/, '');

                        return !inline && isSql ? (
                            <div className="my-2 rounded-md border bg-muted/50 overflow-hidden">
                                <div className="flex items-center justify-between px-3 py-1 bg-muted border-b">
                                    <span className="text-xs font-mono text-muted-foreground">SQL</span>
                                    <button
                                        onClick={() => setSql(codeText)}
                                        className="flex items-center gap-1 text-xs text-primary hover:underline"
                                    >
                                        <Terminal className="w-3 h-3" />
                                        Insert
                                    </button>
                                </div>
                                <div className="p-3 overflow-x-auto text-sm font-mono whitespace-pre text-foreground">
                                    {children}
                                </div>
                            </div>
                        ) : (
                            <code className={cn("bg-muted px-1.5 py-0.5 rounded text-sm font-mono", className)} {...props}>
                                {children}
                            </code>
                        );
                    }
                }}
            >
                {content}
            </ReactMarkdown>
        );
    };

    if (!isOpen) return null;

    return (
        <div className="h-full flex flex-col bg-card border-l">
            {/* Header */}
            <div className="h-12 border-b flex items-center justify-between px-4 bg-muted/20">
                <div className="flex items-center gap-2 font-semibold text-sm">
                    <Sparkles className="w-4 h-4 text-purple-500" />
                    AI Analyst
                </div>
                <button onClick={toggleChat} className="text-muted-foreground hover:text-foreground">
                    <X className="w-4 h-4" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-auto p-4 space-y-4" ref={scrollRef}>
                {messages.map((msg) => (
                    <div key={msg.id} className={cn("flex gap-3", msg.role === 'user' ? "flex-row-reverse" : "")}>
                        <div className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
                            msg.role === 'assistant' ? "bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-800" : "bg-muted text-muted-foreground"
                        )}>
                            {msg.role === 'assistant' ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                        </div>

                        <div className={cn(
                            "max-w-[85%] rounded-lg p-3 text-sm",
                            msg.role === 'user'
                                ? "bg-primary text-primary-foreground"
                                : "bg-muted/50 border text-foreground"
                        )}>
                            {renderContent(msg.content)}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center shrink-0">
                            <Bot className="w-4 h-4 text-purple-500" />
                        </div>
                        <div className="bg-muted/50 border rounded-lg p-3 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce"></span>
                        </div>
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="p-4 border-t bg-background">
                <div className="relative">
                    <Textarea
                        value={input}
                        onChange={(e: any) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask AI to write a query..."
                        className="pr-12 min-h-[60px] resize-none"
                    />
                    <Button
                        size="icon"
                        onClick={() => handleSubmit()}
                        className="absolute bottom-2 right-2 h-7 w-7"
                        disabled={isLoading || !input.trim()}
                    >
                        <Send className="w-3 h-3" />
                    </Button>
                </div>
                <div className="mt-2 text-[10px] text-center text-muted-foreground">
                    AI can make mistakes. Verify generated SQL.
                </div>
            </div>
        </div>
    );
}
