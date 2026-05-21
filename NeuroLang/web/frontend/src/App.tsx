import { useCallback, useEffect, useRef, useState } from "react";
import {
  compile,
  fetchAst,
  fetchComponents,
  fetchDatasets,
  fetchExample,
  listExamples,
  streamRun,
  uploadNl,
} from "./api/client";
import { EditorPanel, type EditorPanelHandle } from "./components/EditorPanel";
import { ExamplesSidebar } from "./components/ExamplesSidebar";
import { OutputTabs } from "./components/OutputTabs";
import { PipelinePlanner } from "./components/PipelinePlanner";
import { ResizableOutputPanel } from "./components/ResizableOutputPanel";
import { useVerticalResize } from "./hooks/useVerticalResize";
import { DEFAULT_SOURCE, TEMPLATES } from "./templates";
import type { CompileResponse, ExampleInfo, OutputTab } from "./types";

function appendLog(lines: string[], msg: string): string[] {
  const ts = new Date().toLocaleTimeString();
  return [...lines, `[${ts}] ${msg}`];
}

export default function App() {
  const editorRef = useRef<EditorPanelHandle>(null);
  const [source, setSource] = useState(DEFAULT_SOURCE);
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [examples, setExamples] = useState<ExampleInfo[]>([]);
  const [examplesLoading, setExamplesLoading] = useState(true);
  const [components, setComponents] = useState<string[]>([]);
  const [datasets, setDatasets] = useState<string[]>([]);
  const [visualize, setVisualize] = useState(false);
  const [compiling, setCompiling] = useState(false);
  const [running, setRunning] = useState(false);
  const runAbortRef = useRef<AbortController | null>(null);
  const [compileResult, setCompileResult] = useState<CompileResponse | null>(null);
  const [astContent, setAstContent] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<OutputTab>("python");
  const [logLines, setLogLines] = useState<string[]>([]);
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const { height: outputHeight, onResizeMouseDown } = useVerticalResize();

  useEffect(() => {
    void (async () => {
      try {
        setExamplesLoading(true);
        const [exList, comps, dsets] = await Promise.all([
          listExamples(),
          fetchComponents(),
          fetchDatasets(),
        ]);
        setExamples(exList);
        setComponents(comps);
        setDatasets(dsets);
        setApiOk(true);
        setLogLines((l) => appendLog(l, "Połączono z API NeuroLang."));
      } catch {
        setApiOk(false);
        setLogLines((l) =>
          appendLog(l, "Błąd API - uruchom: uv run neurolang-web"),
        );
      } finally {
        setExamplesLoading(false);
      }
    })();
  }, []);

  const handleSelectExample = useCallback(async (filename: string) => {
    try {
      const content = await fetchExample(filename);
      setSource(content);
      setActiveFile(filename);
      setCompileResult(null);
      setAstContent(null);
      setLogLines((l) => appendLog(l, `Wczytano: ${filename}`));
    } catch (err) {
      setLogLines((l) => appendLog(l, `Błąd wczytywania: ${String(err)}`));
    }
  }, []);

  const handleCompile = useCallback(async () => {
    const code = editorRef.current?.getValue() ?? source;
    setCompiling(true);
    setLogLines((l) =>
      appendLog(
        l,
        visualize ? "Kompilacja + generowanie grafu..." : "Kompilacja...",
      ),
    );
    try {
      const [result, ast] = await Promise.all([
        compile(code, visualize),
        fetchAst(code),
      ]);
      setCompileResult(result);
      if (ast.success && ast.ast_pretty) {
        setAstContent(ast.ast_pretty);
      } else if (result.ast_pretty) {
        setAstContent(result.ast_pretty);
      } else {
        setAstContent(ast.ast_pretty ?? null);
      }
      if (result.success) {
        if (visualize && result.graph_image_base64) {
          setActiveTab("graph");
          setLogLines((l) => [
            ...appendLog(l, result.message),
            ...appendLog(l, result.graph_message ?? "Graf wygenerowany."),
          ]);
        } else {
          setActiveTab("python");
          setLogLines((l) => appendLog(l, result.message));
          if (visualize && result.graph_message) {
            setLogLines((l) => appendLog(l, result.graph_message!));
          }
        }
      } else {
        setActiveTab("errors");
        setLogLines((l) => appendLog(l, result.message));
      }
    } catch (err) {
      const msg = String(err);
      setCompileResult({
        success: false,
        message: msg,
        error_type: "unknown",
      });
      setActiveTab("errors");
      setLogLines((l) => appendLog(l, msg));
    } finally {
      setCompiling(false);
    }
  }, [source, visualize]);

  const handleUpload = useCallback(async (file: File) => {
    try {
      const content = await uploadNl(file);
      setSource(content);
      setActiveFile(file.name);
      setLogLines((l) => appendLog(l, `Upload: ${file.name}`));
    } catch (err) {
      setLogLines((l) => appendLog(l, `Upload failed: ${String(err)}`));
    }
  }, []);

  const handleInsertTemplate = useCallback((key: string) => {
    const block = TEMPLATES[key];
    if (!block) return;
    editorRef.current?.insertAtCursor("\n" + block + "\n");
    setLogLines((l) => appendLog(l, `Wstawiono szablon: ${key}`));
  }, []);

  const handleDownloadPython = useCallback(() => {
    if (!compileResult?.python_code) return;
    const blob = new Blob([compileResult.python_code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = (activeFile?.replace(".nl", "") ?? "generated") + ".py";
    a.click();
    URL.revokeObjectURL(url);
  }, [compileResult, activeFile]);

  const handleJumpToError = useCallback(() => {
    if (compileResult?.line) {
      editorRef.current?.revealLine(compileResult.line);
    }
  }, [compileResult]);

  const handleRun = useCallback(async () => {
    const code = compileResult?.python_code;
    if (!code) {
      setLogLines((l) =>
        appendLog(l, "Najpierw skompiluj kod (przycisk Kompiluj)."),
      );
      setActiveTab("log");
      return;
    }
    const ok = window.confirm(
      "Uruchomienie wygenerowanego skryptu może trwać długo (pobieranie danych, trening na CPU/GPU). Kontynuować?",
    );
    if (!ok) return;

    runAbortRef.current?.abort();
    const controller = new AbortController();
    runAbortRef.current = controller;

    setRunning(true);
    setActiveTab("log");
    setLogLines((l) => appendLog(l, "--- Uruchamianie skryptu PyTorch ---"));

    try {
      await streamRun(
        { python_code: code },
        {
          signal: controller.signal,
          onEvent: (event) => {
            if (event.type === "start") {
              setLogLines((l) =>
                appendLog(l, `Skrypt: ${event.script}`),
              );
            } else if (event.type === "log") {
              setLogLines((l) => [...l, event.line]);
            } else if (event.type === "error") {
              setLogLines((l) => appendLog(l, event.message));
            } else if (event.type === "done") {
              setLogLines((l) =>
                appendLog(
                  l,
                  event.success
                    ? "Uruchomienie zakończone pomyślnie."
                    : `Zakończono z kodem wyjścia: ${event.exit_code}`,
                ),
              );
            }
          },
        },
      );
    } catch (err) {
      if (controller.signal.aborted) {
        setLogLines((l) => appendLog(l, "Uruchomienie przerwane przez użytkownika."));
      } else {
        setLogLines((l) => appendLog(l, `Błąd uruchomienia: ${String(err)}`));
      }
    } finally {
      setRunning(false);
      runAbortRef.current = null;
    }
  }, [compileResult]);

  const handleStopRun = useCallback(() => {
    runAbortRef.current?.abort();
  }, []);

  return (
    <div className="flex h-full flex-col">
      <header className="flex shrink-0 items-center justify-between border-b border-slate-700/80 bg-slate-900/80 px-4 py-3">
        <div className="flex items-center gap-3">
          <h1 className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-lg font-bold text-transparent">
            NeuroLang Studio
          </h1>
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] ${
              apiOk === true
                ? "bg-emerald-500/20 text-emerald-400"
                : apiOk === false
                  ? "bg-rose-500/20 text-rose-400"
                  : "bg-slate-700 text-slate-400"
            }`}
          >
            {apiOk === true ? "API online" : apiOk === false ? "API offline" : "..."}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 text-xs text-slate-400">
            <input
              type="checkbox"
              checked={visualize}
              onChange={(e) => setVisualize(e.target.checked)}
              className="rounded border-slate-600"
            />
            Wizualizacja (-v)
          </label>
          <button
            type="button"
            onClick={() => void handleRun()}
            disabled={
              running ||
              compiling ||
              apiOk === false ||
              !compileResult?.success
            }
            title={
              compileResult?.success
                ? "Uruchom wygenerowany skrypt PyTorch (jak neurolang -r)"
                : "Najpierw skompiluj kod"
            }
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800 disabled:opacity-50"
          >
            {running ? "Uruchamiam..." : "Uruchom"}
          </button>
          {running ? (
            <button
              type="button"
              onClick={handleStopRun}
              className="rounded-lg border border-rose-600/60 px-3 py-2 text-sm text-rose-300 hover:bg-rose-950/40"
            >
              Przerwij
            </button>
          ) : null}
          <button
            type="button"
            onClick={() => void handleCompile()}
            disabled={compiling || running || apiOk === false}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {compiling ? "Kompiluję..." : "Kompiluj"}
          </button>
        </div>
      </header>

      <div className="flex min-h-0 flex-1">
        <ExamplesSidebar
          examples={examples}
          activeFile={activeFile}
          loading={examplesLoading}
          onSelect={(f) => void handleSelectExample(f)}
          onUpload={(f) => void handleUpload(f)}
          onNewTemplate={() => {
            setSource(DEFAULT_SOURCE);
            setActiveFile("nowy_szablon.nl");
            setCompileResult(null);
            setAstContent(null);
          }}
        />

        <div className="flex min-w-0 flex-1 flex-col">
          <div className="flex min-h-0 flex-1">
            <EditorPanel
              ref={editorRef}
              value={source}
              onChange={setSource}
              filename={activeFile}
            />
            <PipelinePlanner
              source={source}
              components={components}
              datasets={datasets}
              onInsertTemplate={handleInsertTemplate}
            />
          </div>
          <ResizableOutputPanel
            height={outputHeight}
            onResizeMouseDown={onResizeMouseDown}
          >
            <OutputTabs
              activeTab={activeTab}
              onTabChange={setActiveTab}
              sourceNl={source}
              activeFilename={activeFile}
              compileResult={compileResult}
              astContent={astContent}
              logLines={logLines}
              visualize={visualize}
              graphLoading={compiling && visualize}
              onDownloadPython={handleDownloadPython}
              onJumpToError={handleJumpToError}
            />
          </ResizableOutputPanel>
        </div>
      </div>
    </div>
  );
}
