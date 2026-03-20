import { Play, Loader2, Sparkles } from 'lucide-react';

import { SQLEditor } from './SQLEditor';
import { DataGrid } from './DataGrid';
import { SchemaBrowser } from './SchemaBrowser';
import { ChatPanel } from './ChatPanel';
import { useQueryExecutor } from '@/hooks/useQueryExecutor';
import { useStudioStore } from '@/stores/studioStore';
import { useCopilotStore } from '@/stores/copilotStore';
import { cn } from '@/lib/utils';

export function StudioLayout() {
    const { sql } = useStudioStore();
    const { isOpen: isChatOpen, toggleChat } = useCopilotStore();
    const { mutate: executeQuery, isPending, data: queryData, error } = useQueryExecutor();

    const handleRun = () => {
        executeQuery(sql);
    };

    return (
        <div className="h-full flex flex-col">
            {/* Toolbar */}
            <div className="h-12 border-b flex items-center justify-between px-4 bg-card">
                <div className="flex items-center gap-4">
                    <button
                        onClick={handleRun}
                        disabled={isPending}
                        className={cn(
                            "flex items-center gap-2 px-4 py-1.5 rounded-md font-medium text-sm transition-colors",
                            "bg-primary text-primary-foreground hover:bg-primary/90",
                            isPending && "opacity-70 cursor-not-allowed"
                        )}
                    >
                        {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                        Run Query
                    </button>

                    {queryData && (
                        <span className="text-xs text-muted-foreground animate-in fade-in">
                            {queryData.rowCount} rows in {queryData.durationMs}ms
                        </span>
                    )}

                    {error && (
                        <span className="text-xs text-destructive font-medium">
                            Error: {error.message}
                        </span>
                    )}
                </div>

                {/* Right Actions */}
                <button
                    onClick={toggleChat}
                    className={cn(
                        "flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors border",
                        isChatOpen
                            ? "bg-purple-100 text-purple-900 border-purple-200 dark:bg-purple-900/40 dark:text-purple-300 dark:border-purple-800"
                            : "hover:bg-muted text-muted-foreground"
                    )}
                >
                    <Sparkles className="w-4 h-4" />
                    {!isChatOpen && "Ask AI"}
                </button>
            </div>

            {/* Main Workspace - Simplified grid layout instead of resizable panels */}
            <div className="flex-1 overflow-hidden flex">
                {/* Left: Schema */}
                <div className="w-64 border-r overflow-hidden flex-shrink-0">
                    <SchemaBrowser />
                </div>

                {/* Center: Work Area */}
                <div className={cn("flex-1 flex flex-col", isChatOpen && "mr-80")}>
                    {/* Top: Editor */}
                    <div className="h-2/5 border-b overflow-hidden">
                        <SQLEditor onExecute={handleRun} />
                    </div>

                    {/* Bottom: Results */}
                    <div className="flex-1 overflow-hidden">
                        <DataGrid data={queryData?.rows} isLoading={isPending} />
                    </div>
                </div>

                {/* Right: AI Chat */}
                {isChatOpen && (
                    <div className="w-80 border-l flex-shrink-0">
                        <ChatPanel />
                    </div>
                )}
            </div>
        </div>
    );
}
