import React, { useState, useRef, useEffect } from 'react';
import { ExportIcon, RefreshIcon, MoreIcon, CloseIcon, SettingsIcon } from '../icons';
import { CopyIcon, ImageDownIcon, CheckIcon } from 'lucide-react';
import html2canvas from 'html2canvas';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter
} from 'recharts';

export function ChatInterface({
    messages = [],
    onSendMessage,
    isLoading = false,
    placeholder = "Ask anything about your data..."
}) {
    const [input, setInput] = useState('');
    const [showSettings, setShowSettings] = useState(false);
    const [apiKey, setApiKey] = useState(localStorage.getItem('da_api_key') || '');
    const [modelProvider, setModelProvider] = useState(localStorage.getItem('da_model_provider') || 'gemini');
    
    // Save settings when changed
    useEffect(() => {
        localStorage.setItem('da_api_key', apiKey);
        localStorage.setItem('da_model_provider', modelProvider);
    }, [apiKey, modelProvider]);

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
        // Pass configurations dynamically with the message payload
        onSendMessage(input.trim(), { apiKey, modelProvider });
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
                <div className="relative">
                    <button 
                        onClick={() => setShowSettings(!showSettings)}
                        className={`p-1.5 rounded-lg transition-all ${showSettings ? 'bg-[#3B82F6]/20 text-[#3B82F6]' : 'text-[#71717A] hover:text-white hover:bg-[#1A1A24]'}`}
                        title="AI Settings"
                    >
                        <SettingsIcon className="w-4 h-4" />
                    </button>
                    
                    {/* Settings Dropdown */}
                    {showSettings && (
                        <div className="absolute right-0 mt-2 w-64 bg-[#12121A] border border-[#1E1E2A] rounded-xl shadow-xl z-50 p-4 animate-in fade-in zoom-in-95 duration-200">
                            <div className="flex items-center justify-between mb-3 border-b border-[#1E1E2A] pb-2">
                                <h4 className="text-sm font-semibold text-[#E5E7EB]">AI Configuration</h4>
                                <button onClick={() => setShowSettings(false)} className="text-[#A1A1AA] hover:text-white">
                                    <CloseIcon className="w-4 h-4" />
                                </button>
                            </div>
                            
                            <div className="space-y-4">
                                <div className="space-y-1.5">
                                    <label className="text-xs font-medium text-[#A1A1AA]">Model Provider</label>
                                    <select 
                                        value={modelProvider}
                                        onChange={(e) => setModelProvider(e.target.value)}
                                        className="w-full bg-[#1A1A24] border border-[#2A2A3A] rounded-lg px-2.5 py-1.5 text-sm text-white focus:border-[#3B82F6] outline-none transition-colors"
                                    >
                                        <option value="gemini">Google Gemini (Default)</option>
                                        <option value="openai">OpenAI GPT-4o</option>
                                    </select>
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-xs font-medium text-[#A1A1AA]">API Key (Optional)</label>
                                    <input 
                                        type="password"
                                        placeholder="Sk-..."
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        className="w-full bg-[#1A1A24] border border-[#2A2A3A] rounded-lg px-2.5 py-1.5 text-sm text-white placeholder-[#52525B] focus:border-[#3B82F6] outline-none transition-colors"
                                    />
                                    <p className="text-[10px] text-[#71717A]">Leave empty to use server default.</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
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
    const chartRef = useRef(null);
    const [copied, setCopied] = useState(false);

    const handleCopyText = async () => {
        try {
            await navigator.clipboard.writeText(message.content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (e) {
            console.error('Failed to copy text', e);
        }
    };

    const handleExportPNG = async () => {
        if (!chartRef.current) return;
        try {
            // Apply slight padding for cleaner export
            const canvas = await html2canvas(chartRef.current, { 
                backgroundColor: '#12121A',
                scale: 2 // Higher resolution
            });
            const image = canvas.toDataURL("image/png");
            const link = document.createElement("a");
            link.href = image;
            link.download = `chart_snapshot_${Date.now()}.png`;
            link.click();
        } catch (e) {
            console.error('Failed to export chart', e);
        }
    };

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
                
                {/* Dynamically Render Data Visualizations */}
                {message.chartData && message.chartData.length > 0 && message.chartConfig && (
                    <div ref={chartRef} className="bg-[#12121A] rounded-xl p-2 pb-4 mt-3">
                        <DynamicChart data={message.chartData} config={message.chartConfig} />
                    </div>
                )}

                {/* Response Actions (for assistant messages) */}
                {!isUser && message.showActions && (
                    <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-[#2A2A3A]">
                        <button 
                            onClick={handleCopyText}
                            className="
                            flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg
                            bg-[#1A1A24] border border-[#2A2A3A]
                            text-xs text-[#A1A1AA]
                            hover:bg-[#22222E] hover:text-white
                            transition-all duration-200
                        ">
                            {copied ? <CheckIcon className="w-3.5 h-3.5 text-[#10B981]" /> : <CopyIcon className="w-3.5 h-3.5" />}
                            {copied ? 'Copied' : 'Copy'}
                        </button>
                        {message.chartData && message.chartData.length > 0 && (
                            <button 
                                onClick={() => {
                                    const csvContent = "data:text/csv;charset=utf-8," 
                                        + Object.keys(message.chartData[0]).join(",") + "\n" 
                                        + message.chartData.map(e => Object.values(e).join(",")).join("\n");
                                    const encodedUri = encodeURI(csvContent);
                                    const link = document.createElement("a");
                                    link.setAttribute("href", encodedUri);
                                    link.setAttribute("download", "chart_data_export.csv");
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                }}
                                className="
                                flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg
                                bg-[#1A1A24] border border-[#2A2A3A]
                                text-xs text-[#A1A1AA]
                                hover:bg-[#22222E] hover:text-white
                                transition-all duration-200
                            ">
                                <ExportIcon className="w-3.5 h-3.5" />
                                Export CSV
                            </button>
                        )}
                        {message.chartData && message.chartData.length > 0 && (
                            <button 
                                onClick={handleExportPNG}
                                className="
                                flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg
                                bg-[#1A1A24] border border-[#2A2A3A]
                                text-xs text-[#A1A1AA]
                                hover:bg-[#22222E] hover:text-white
                                transition-all duration-200
                            ">
                                <ImageDownIcon className="w-3.5 h-3.5" />
                                Export PNG
                            </button>
                        )}
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
                        
                        {/* Token / Cost tracking badge */}
                        {message.usage && (
                            <div className="ml-auto flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#111118] border border-[#1E1E2A] text-[11px] text-[#A1A1AA]" title="Token usage for this query">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                                {message.usage.provider ? message.usage.provider.charAt(0).toUpperCase() + message.usage.provider.slice(1) : 'AI Model'} 
                                <span className="text-[#52525B]">|</span> 
                                {message.usage.total_tokens ? message.usage.total_tokens.toLocaleString() : 0} tokens
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

const COLORS = ['#3B82F6', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#6366F1'];

function DynamicChart({ data, config }) {
  const [activeType, setActiveType] = useState(config?.type || 'table');

  useEffect(() => {
     if (config?.type) {
         setActiveType(config.type);
     }
  }, [config]);

  if (!data || data.length === 0 || !config) return null;

  const { xAxisKey, yAxisKey, title } = config;
  // yAxisKey might be an array or string
  const yKeys = Array.isArray(yAxisKey) ? yAxisKey : [yAxisKey].filter(Boolean);

  const renderChart = () => {
    switch (activeType) {
      case 'bar':
        return (
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2A3A" />
            <XAxis dataKey={xAxisKey} stroke="#71717A" fontSize={12} />
            <YAxis stroke="#71717A" fontSize={12} />
            <Tooltip contentStyle={{ backgroundColor: '#1A1A24', border: '1px solid #2A2A3A', borderRadius: '8px' }} />
            <Legend />
            {yKeys.map((key, idx) => (
              <Bar key={key} dataKey={key} fill={COLORS[idx % COLORS.length]} radius={[4, 4, 0, 0]} />
            ))}
          </BarChart>
        );
      case 'line':
        return (
          <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2A3A" />
            <XAxis dataKey={xAxisKey} stroke="#71717A" fontSize={12} />
            <YAxis stroke="#71717A" fontSize={12} />
            <Tooltip contentStyle={{ backgroundColor: '#1A1A24', border: '1px solid #2A2A3A', borderRadius: '8px' }} />
            <Legend />
            {yKeys.map((key, idx) => (
              <Line key={key} type="monotone" dataKey={key} stroke={COLORS[idx % COLORS.length]} strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            ))}
          </LineChart>
        );
      case 'pie':
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey={yKeys[0] || "value"}
              nameKey={xAxisKey || "name"}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#1A1A24', border: '1px solid #2A2A3A', borderRadius: '8px' }} />
            <Legend />
          </PieChart>
        );
      case 'scatter':
         return (
          <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2A3A" />
            <XAxis dataKey={xAxisKey} stroke="#71717A" fontSize={12} name={xAxisKey} />
            <YAxis dataKey={yKeys[0]} stroke="#71717A" fontSize={12} name={yKeys[0]} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1A1A24', border: '1px solid #2A2A3A', borderRadius: '8px' }} />
            <Scatter name={title || 'Data'} data={data} fill={COLORS[0]} />
          </ScatterChart>
         );
      case 'table':
      default:
        const keys = Object.keys(data[0] || {});
        return (
           <div className="overflow-x-auto w-full mt-4 bg-[#1A1A24] rounded-lg border border-[#2A2A3A]">
              <table className="w-full text-sm text-left text-gray-400">
                 <thead className="text-xs text-gray-300 uppercase bg-[#22222E]">
                    <tr>{keys.map(k => <th key={k} className="px-4 py-3">{k}</th>)}</tr>
                 </thead>
                 <tbody>
                    {data.slice(0, 10).map((row, i) => (
                       <tr key={i} className="border-b border-[#2A2A3A]">
                          {keys.map(k => <td key={k} className="px-4 py-2">{row[k]}</td>)}
                       </tr>
                    ))}
                 </tbody>
              </table>
              {data.length > 10 && <div className="p-2 text-xs text-center text-gray-500">Showing 10 of {data.length} rows</div>}
           </div>
        );
    }
  };

  return (
    <div className="mt-4 w-full pt-4 border-t border-[#2A2A3A] relative group">
      <div className="flex items-center justify-between mb-4">
          {title ? (
              <h4 className="text-sm font-semibold text-white">{title}</h4>
          ) : <div />}
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#71717A]">Type:</span>
            <select
               value={activeType}
               onChange={(e) => setActiveType(e.target.value)}
               className="bg-[#1A1A24] border border-[#2A2A3A] text-xs text-[#A1A1AA] rounded px-2 py-1 outline-none hover:border-[#3B82F6] hover:text-white transition-colors cursor-pointer"
            >
               <option value="bar">Bar</option>
               <option value="line">Line</option>
               <option value="pie">Pie</option>
               <option value="scatter">Scatter</option>
               <option value="table">Table</option>
            </select>
          </div>
      </div>
      {activeType !== 'table' ? (
         <div className="w-full h-64 min-w-[300px]">
           <ResponsiveContainer width="100%" height="100%">
             {renderChart()}
           </ResponsiveContainer>
         </div>
      ) : renderChart()}
    </div>
  );
}

export default ChatInterface;
