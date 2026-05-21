import Editor, { type OnMount } from "@monaco-editor/react";
import { useCallback, useEffect, useRef } from "react";
import type * as Monaco from "monaco-editor";

import {
  LANGUAGE_ID,
  NEUROLANG_THEME_ID,
  setupNeurolangTextMate,
} from "../monaco/neurolangTextMate";

interface CompareViewProps {
  sourceNl: string;
  pythonCode: string;
  filename: string | null;
}

const READONLY_EDITOR_OPTIONS: Monaco.editor.IStandaloneEditorConstructionOptions =
  {
    readOnly: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    fontSize: 12,
    lineNumbers: "on",
    wordWrap: "on",
    automaticLayout: true,
    tabSize: 4,
    padding: { top: 8, bottom: 8 },
    renderLineHighlight: "none",
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    scrollbar: { vertical: "auto", horizontal: "auto", useShadows: false },
    contextmenu: false,
    folding: true,
  };

function syncScroll(
  source: Monaco.editor.IStandaloneCodeEditor,
  target: Monaco.editor.IStandaloneCodeEditor,
  syncing: { current: boolean },
) {
  if (syncing.current) return;
  const sourceMax =
    source.getScrollHeight() - source.getLayoutInfo().height;
  const targetMax =
    target.getScrollHeight() - target.getLayoutInfo().height;
  if (sourceMax <= 0 || targetMax <= 0) return;
  syncing.current = true;
  target.setScrollTop((source.getScrollTop() / sourceMax) * targetMax);
  syncing.current = false;
}

export function CompareView({ sourceNl, pythonCode, filename }: CompareViewProps) {
  const nlEditorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const pyEditorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const syncing = useRef(false);
  const scrollBound = useRef(false);
  const scrollDisposables = useRef<Monaco.IDisposable[]>([]);

  const bindScrollSync = useCallback(() => {
    const nl = nlEditorRef.current;
    const py = pyEditorRef.current;
    if (!nl || !py || scrollBound.current) return;
    scrollBound.current = true;

    scrollDisposables.current.forEach((d) => d.dispose());
    scrollDisposables.current = [
      nl.onDidScrollChange(() => syncScroll(nl, py, syncing)),
      py.onDidScrollChange(() => syncScroll(py, nl, syncing)),
    ];
  }, []);

  useEffect(() => {
    return () => {
      scrollDisposables.current.forEach((d) => d.dispose());
      scrollDisposables.current = [];
      scrollBound.current = false;
    };
  }, []);

  useEffect(() => {
    const editor = nlEditorRef.current;
    if (editor && editor.getValue() !== sourceNl) {
      editor.setValue(sourceNl);
    }
  }, [sourceNl]);

  useEffect(() => {
    const editor = pyEditorRef.current;
    if (editor && editor.getValue() !== pythonCode) {
      editor.setValue(pythonCode);
    }
  }, [pythonCode]);

  const handleNlMount: OnMount = async (editor, monaco) => {
    nlEditorRef.current = editor;
    try {
      await setupNeurolangTextMate(monaco, editor);
      monaco.editor.setTheme(NEUROLANG_THEME_ID);
    } catch (err) {
      console.error("NeuroLang TextMate setup failed:", err);
    }
    bindScrollSync();
  };

  const handlePyMount: OnMount = (editor, monaco) => {
    pyEditorRef.current = editor;
    monaco.editor.setTheme(NEUROLANG_THEME_ID);
    bindScrollSync();
  };

  const nlName = filename ?? "wejscie.nl";
  const pyName = filename?.replace(/\.nl$/i, ".py") ?? "wyjscie.py";

  return (
    <div className="flex h-full min-h-0 gap-0">
      <div className="flex min-h-0 min-w-0 flex-1 flex-col border-r border-slate-700/80">
        <div className="shrink-0 border-b border-slate-700/60 bg-indigo-950/30 px-3 py-1.5">
          <span className="text-xs font-medium text-indigo-300">NeuroLang</span>
          <span className="ml-2 font-mono text-[10px] text-slate-500">{nlName}</span>
        </div>
        <div className="min-h-0 flex-1">
          <Editor
            height="100%"
            language={LANGUAGE_ID}
            theme={NEUROLANG_THEME_ID}
            value={sourceNl}
            onMount={handleNlMount}
            options={READONLY_EDITOR_OPTIONS}
          />
        </div>
      </div>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <div className="shrink-0 border-b border-slate-700/60 bg-emerald-950/20 px-3 py-1.5">
          <span className="text-xs font-medium text-emerald-300">Python</span>
          <span className="ml-2 font-mono text-[10px] text-slate-500">{pyName}</span>
        </div>
        <div className="min-h-0 flex-1">
          <Editor
            height="100%"
            language="python"
            theme={NEUROLANG_THEME_ID}
            value={pythonCode}
            onMount={handlePyMount}
            options={READONLY_EDITOR_OPTIONS}
          />
        </div>
      </div>
    </div>
  );
}
