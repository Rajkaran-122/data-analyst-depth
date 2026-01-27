import React, { useRef, useEffect } from 'react';
import Editor, { useMonaco } from '@monaco-editor/react';
import { useStudioStore } from '@/stores/studioStore';

interface SQLEditorProps {
    onExecute: () => void;
}

export function SQLEditor({ onExecute }: SQLEditorProps) {
    const { sql, setSql } = useStudioStore();
    const monaco = useMonaco();
    const editorRef = useRef<any>(null);

    useEffect(() => {
        if (monaco) {
            // Define custom theme if needed, or just use vs-dark
            monaco.editor.defineTheme('pro-dark', {
                base: 'vs-dark',
                inherit: true,
                rules: [],
                colors: {
                    'editor.background': '#09090b', // zinc-950
                }
            });
        }
    }, [monaco]);

    const handleEditorDidMount = (editor: any) => {
        editorRef.current = editor;

        // Keybinding: Cmd+Enter to Run
        editor.addCommand(monaco?.KeyMod.CtrlCmd | monaco?.KeyCode.Enter, () => {
            onExecute();
        });
    };

    return (
        <div className="h-full w-full overflow-hidden rounded-md border bg-card">
            <Editor
                height="100%"
                defaultLanguage="sql"
                theme="vs-dark" // Using standard vs-dark for reliability
                value={sql}
                onChange={(val) => setSql(val || '')}
                onMount={handleEditorDidMount}
                options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    padding: { top: 16 },
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                }}
            />
        </div>
    );
}
