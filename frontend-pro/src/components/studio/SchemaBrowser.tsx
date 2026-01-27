import React from 'react';
import { Database, Table, Columns, ChevronRight, ChevronDown } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area'; // Assuming Shadcn scroll-area exists or using native for now
import { cn } from '@/lib/utils';

// Mock Schema - In real app, fetch from useQuery
const mockSchema = [
    {
        name: 'public',
        tables: [
            { name: 'users', columns: ['id', 'email', 'name', 'role', 'created_at'] },
            { name: 'orders', columns: ['id', 'user_id', 'total', 'status'] },
            { name: 'products', columns: ['id', 'sku', 'price', 'inventory'] },
        ]
    },
    {
        name: 'analytics',
        tables: [
            { name: 'events', columns: ['id', 'type', 'payload', 'timestamp'] },
        ]
    }
];

export function SchemaBrowser() {
    const [expanded, setExpanded] = React.useState<Record<string, boolean>>({ 'public': true });

    const toggle = (key: string) => {
        setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div className="h-full flex flex-col bg-card border-r">
            <div className="p-3 border-b bg-muted/30">
                <h3 className="font-semibold text-sm flex items-center gap-2">
                    <Database className="w-4 h-4" />
                    Database Explorer
                </h3>
            </div>

            <div className="flex-1 overflow-auto p-2">
                {mockSchema.map(schema => (
                    <div key={schema.name} className="mb-2">
                        <button
                            onClick={() => toggle(schema.name)}
                            className="flex items-center gap-1 w-full text-left text-sm font-medium p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
                        >
                            {expanded[schema.name] ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                            {schema.name}
                        </button>

                        {expanded[schema.name] && (
                            <div className="ml-2 pl-2 border-l border-border mt-1 space-y-1">
                                {schema.tables.map(table => (
                                    <div key={table.name}>
                                        <button
                                            onClick={() => toggle(`${schema.name}.${table.name}`)}
                                            className="flex items-center gap-2 w-full text-left text-sm p-1 hover:bg-muted rounded group"
                                        >
                                            <Table className="w-3 h-3 text-blue-500" />
                                            <span className="text-foreground">{table.name}</span>
                                        </button>

                                        {/* Columns */}
                                        {expanded[`${schema.name}.${table.name}`] && (
                                            <div className="ml-4 pl-2 border-l border-border/50 mt-1 space-y-0.5">
                                                {table.columns.map(col => (
                                                    <div key={col} className="text-xs text-muted-foreground flex items-center gap-2 py-0.5 px-1 hover:bg-muted/50 rounded cursor-pointer">
                                                        <Columns className="w-3 h-3 opacity-50" />
                                                        {col}
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
