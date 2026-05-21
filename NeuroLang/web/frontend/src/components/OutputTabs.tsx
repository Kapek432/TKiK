import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import type { CompileResponse, OutputTab } from "../types";
import {
  pythonHighlightStyle,
  pythonLineNumberStyle,
} from "../styles/pythonHighlight";
import { CompareView } from "./CompareView";

interface OutputTabsProps {
  activeTab: OutputTab;
  onTabChange: (tab: OutputTab) => void;
  sourceNl: string;
  activeFilename: string | null;
  compileResult: CompileResponse | null;
  astContent: string | null;
  logLines: string[];
  visualize: boolean;
  graphLoading: boolean;
  onDownloadPython: () => void;
  onJumpToError: () => void;
}

const TABS: { id: OutputTab; label: string }[] = [
  { id: "python", label: "Python" },
  { id: "compare", label: "NL | Python" },
  { id: "ast", label: "AST" },
  { id: "graph", label: "Graf" },
  { id: "errors", label: "Błędy" },
  { id: "log", label: "Log" },
];

export function OutputTabs({
  activeTab,
  onTabChange,
  sourceNl,
  activeFilename,
  compileResult,
  astContent,
  logLines,
  visualize,
  graphLoading,
  onDownloadPython,
  onJumpToError,
}: OutputTabsProps) {
  const hasError = compileResult && !compileResult.success;
  const hasGraph = Boolean(compileResult?.graph_image_base64);
  const canCompare =
    compileResult?.success && Boolean(compileResult.python_code);

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex items-center justify-between border-b border-slate-700/80 px-2">
        <div className="flex gap-0.5">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={`px-3 py-2 text-xs font-medium ${
                activeTab === tab.id
                  ? "border-b-2 border-indigo-500 text-indigo-300"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {tab.label}
              {tab.id === "compare" && canCompare && (
                <span className="ml-1 text-emerald-400">●</span>
              )}
              {tab.id === "graph" && visualize && hasGraph && (
                <span className="ml-1 text-emerald-400">●</span>
              )}
              {tab.id === "errors" && hasError && (
                <span className="ml-1 text-rose-400">!</span>
              )}
            </button>
          ))}
        </div>
        <div className="flex gap-2 pr-2">
          {compileResult?.success && compileResult.python_code && (
            <button
              type="button"
              onClick={onDownloadPython}
              className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-300 hover:bg-slate-700"
            >
              Pobierz .py
            </button>
          )}
          {hasError && compileResult?.line && (
            <button
              type="button"
              onClick={onJumpToError}
              className="rounded bg-rose-900/50 px-2 py-1 text-xs text-rose-200 hover:bg-rose-900"
            >
              Przejdź do linii {compileResult.line}
            </button>
          )}
        </div>
      </div>

      <div
        className={`min-h-0 flex-1 text-sm ${
          activeTab === "compare" ? "overflow-hidden p-0" : "overflow-auto p-2"
        }`}
      >
        {activeTab === "compare" && (
          <>
            {canCompare && compileResult?.python_code ? (
              <CompareView
                sourceNl={sourceNl}
                pythonCode={compileResult.python_code}
                filename={activeFilename}
              />
            ) : (
              <p className="p-2 text-slate-500">
                Skompiluj poprawnie, aby porównać NeuroLang (.nl) z wygenerowanym
                Pythonem (.py).
              </p>
            )}
          </>
        )}

        {activeTab === "python" && (
          <>
            {compileResult?.success && compileResult.python_code ? (
              <div className="syntax-output rounded-md bg-slate-900/50">
                <SyntaxHighlighter
                  language="python"
                  style={pythonHighlightStyle}
                  customStyle={{
                    margin: 0,
                    padding: "0.75rem 0",
                    fontSize: "12px",
                    lineHeight: "1.5",
                    background: "transparent",
                  }}
                  codeTagProps={{
                    style: { background: "transparent" },
                  }}
                  lineNumberStyle={pythonLineNumberStyle}
                  showLineNumbers
                  wrapLongLines
                >
                  {compileResult.python_code}
                </SyntaxHighlighter>
              </div>
            ) : (
              <p className="text-slate-500">
                Skompiluj kod, aby zobaczyć wygenerowany Python.
              </p>
            )}
          </>
        )}

        {activeTab === "graph" && (
          <>
            {graphLoading && (
              <p className="text-slate-400">Generowanie grafu architektury (torchview)...</p>
            )}
            {!graphLoading && hasGraph && (
              <div className="flex flex-col items-start gap-2">
                <img
                  src={`data:image/png;base64,${compileResult!.graph_image_base64}`}
                  alt="Architecture graph"
                  className="max-h-full max-w-full rounded border border-slate-700 bg-white object-contain"
                />
                {compileResult?.graph_message && (
                  <p className="text-xs text-emerald-400">{compileResult.graph_message}</p>
                )}
              </div>
            )}
            {!graphLoading && !hasGraph && (
              <div className="text-slate-500">
                {visualize ? (
                  <>
                    <p>Graf nie został wygenerowany.</p>
                    {compileResult?.graph_message && (
                      <p className="mt-2 text-xs text-amber-300/90">
                        {compileResult.graph_message}
                      </p>
                    )}
                    <p className="mt-2 text-[10px]">
                      Wymaga torchview i poprawnej definicji sieci. Skompiluj ponownie z
                      zaznaczoną wizualizacją.
                    </p>
                  </>
                ) : (
                  <p>Zaznacz „Wizualizacja (-v)” i skompiluj, aby wygenerować graf.</p>
                )}
              </div>
            )}
          </>
        )}

        {activeTab === "ast" && (
          <>
            {astContent ? (
              <pre className="whitespace-pre-wrap font-mono text-xs text-slate-300">
                {astContent}
              </pre>
            ) : (
              <p className="text-slate-500">
                Kliknij Kompiluj lub odśwież AST - drzewo pojawi się tutaj.
              </p>
            )}
          </>
        )}

        {activeTab === "errors" && (
          <>
            {hasError ? (
              <div className="space-y-2 text-rose-200">
                <p className="font-medium">{compileResult?.message}</p>
                {compileResult?.line != null && (
                  <p className="text-xs text-slate-400">
                    Linia {compileResult.line}, kolumna {compileResult.column ?? "?"}
                    {compileResult.error_type && ` (${compileResult.error_type})`}
                  </p>
                )}
                {compileResult?.context && (
                  <pre className="rounded bg-slate-900 p-2 font-mono text-xs text-amber-200/90">
                    {compileResult.context}
                  </pre>
                )}
              </div>
            ) : compileResult?.success ? (
              <p className="text-emerald-400">Kompilacja zakończona bez błędów.</p>
            ) : (
              <p className="text-slate-500">Brak błędów do wyświetlenia.</p>
            )}
          </>
        )}

        {activeTab === "log" && (
          <pre className="whitespace-pre-wrap font-mono text-xs text-slate-400">
            {logLines.length > 0 ? logLines.join("\n") : "Log kompilacji pojawi się tutaj."}
          </pre>
        )}
      </div>
    </div>
  );
}
