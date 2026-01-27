import { create } from 'zustand';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface CopilotState {
    messages: Message[];
    isLoading: boolean;
    isOpen: boolean;

    toggleChat: () => void;
    sendMessage: (content: string) => Promise<void>;
    addMessage: (role: 'user' | 'assistant', content: string) => void;
}

export const useCopilotStore = create<CopilotState>((set, get) => ({
    messages: [
        {
            id: '1',
            role: 'assistant',
            content: 'Hello! I am your Data Analyst Copilot. I can help you write queries, visualize data, or fix errors. Try asking: "Show me the top users by revenue".',
            timestamp: new Date(),
        }
    ],
    isLoading: false,
    isOpen: true,

    toggleChat: () => set((state) => ({ isOpen: !state.isOpen })),

    addMessage: (role, content) => set((state) => ({
        messages: [...state.messages, { id: Date.now().toString(), role, content, timestamp: new Date() }]
    })),

    sendMessage: async (content) => {
        const { addMessage } = get();

        // 1. Add User Message
        addMessage('user', content);
        set({ isLoading: true });

        // 2. Mock API Call (Replace with /api/analyze)
        try {
            await new Promise(r => setTimeout(r, 1500)); // Latency

            let response = "I'm not connected to the real backend yet, but I can simulate help.";
            if (content.toLowerCase().includes('revenue')) {
                response = `Here is the query for revenue:\n\`\`\`sql\nSELECT name, revenue FROM users ORDER BY revenue DESC LIMIT 10;\n\`\`\``;
            } else if (content.toLowerCase().includes('error')) {
                response = `It looks like you have a syntax error. You used \`SELEC\` instead of \`SELECT\`.`;
            }

            // 3. Add AI Response
            addMessage('assistant', response);
        } catch (err) {
            addMessage('assistant', 'Sorry, I encountered an error processing your request.');
        } finally {
            set({ isLoading: false });
        }
    },
}));
