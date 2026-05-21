import Editor, { type OnMount } from "@monaco-editor/react";
import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";

import {
  LANGUAGE_ID,
  NEUROLANG_THEME_ID,
  setupNeurolangTextMate,
} from "../monaco/neurolangTextMate";

export interface EditorPanelHandle {
  revealLine: (line: number) => void;
  insertAtCursor: (text: string) => void;
  getValue: () => string;
}

interface EditorPanelProps {
  value: string;
  onChange: (value: string) => void;
  filename: string | null;
}

export const EditorPanel = forwardRef<EditorPanelHandle, EditorPanelProps>(
  function EditorPanel({ value, onChange, filename }, ref) {
    const editorRef = useRef<Parameters<OnMount>[0] | null>(null);

    useImperativeHandle(ref, () => ({
      revealLine(line: number) {
        const editor = editorRef.current;
        if (!editor) return;
        editor.revealLineInCenter(line);
        editor.setPosition({ lineNumber: line, column: 1 });
        editor.focus();
      },
      insertAtCursor(text: string) {
        const editor = editorRef.current;
        if (!editor) {
          onChange(value + "\n" + text);
          return;
        }
        const selection = editor.getSelection();
        if (!selection) return;
        editor.executeEdits("template", [
          {
            range: selection,
            text,
            forceMoveMarkers: true,
          },
        ]);
        editor.focus();
        onChange(editor.getValue());
      },
      getValue() {
        return editorRef.current?.getValue() ?? value;
      },
    }));

    const handleMount: OnMount = async (editor, monaco) => {
      editorRef.current = editor;
      try {
        await setupNeurolangTextMate(monaco, editor);
        monaco.editor.setTheme(NEUROLANG_THEME_ID);
      } catch (err) {
        console.error("NeuroLang TextMate setup failed:", err);
      }
    };

    useEffect(() => {
      const editor = editorRef.current;
      if (!editor) return;
      const current = editor.getValue();
      if (current !== value) {
        editor.setValue(value);
      }
    }, [value, filename]);

    return (
      <div className="flex h-full min-h-0 flex-1 flex-col">
        <div className="flex items-center justify-between border-b border-slate-700/80 bg-slate-900/40 px-3 py-2">
          <span className="text-sm text-slate-300">
            {filename ?? "nowy_plik.nl"}
          </span>
          <span className="text-xs text-slate-500">NeuroLang</span>
        </div>
        <div className="min-h-0 flex-1">
          <Editor
            key={filename ?? "untitled"}
            height="100%"
            language={LANGUAGE_ID}
            theme={NEUROLANG_THEME_ID}
            value={value}
            onChange={(v) => onChange(v ?? "")}
            onMount={handleMount}
            options={{
              fontSize: 13,
              minimap: { enabled: false },
              wordWrap: "on",
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
            }}
          />
        </div>
      </div>
    );
  },
);
