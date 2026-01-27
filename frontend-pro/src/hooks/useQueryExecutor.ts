import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

interface QueryResult {
    columns: string[];
    rows: any[];
    rowCount: number;
    durationMs: number;
}

interface QueryError {
    message: string;
    line?: number;
}

export function useQueryExecutor() {
    return useMutation({
        mutationFn: async (sql: string): Promise<QueryResult> => {
            // PRO: In a real app, this hits the backend.
            // For the prototype foundation, we'll hit the real backend if variable is set, 
            // otherwise mock it for immediate "Show me" value.

            const MOCK_MODE = false; // Toggle to false to hit real API

            if (MOCK_MODE) {
                await new Promise(r => setTimeout(r, 600)); // Fake latency
                if (sql.toLowerCase().includes('error')) throw new Error("Syntax Error: Unexpected token 'ERROR' at line 1.");

                return {
                    columns: ['id', 'name', 'role', 'created_at', 'revenue'],
                    rows: Array.from({ length: 50 }).map((_, i) => ({
                        id: i + 1,
                        name: `User ${i + 1}`,
                        role: i % 3 === 0 ? 'Admin' : 'Viewer',
                        created_at: new Date().toISOString(),
                        revenue: Math.floor(Math.random() * 10000)
                    })),
                    rowCount: 50,
                    durationMs: 124
                };
            }

            // Real Backend Call
            const response = await apiClient.post('/api/explorer/query', { sql });
            return response.data;
        }
    });
}
