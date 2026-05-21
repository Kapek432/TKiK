import { useState } from "react";
import type { ExampleInfo } from "../types";
import { ExamplesGallery } from "./ExamplesGallery";

interface ExamplesSidebarProps {
  examples: ExampleInfo[];
  activeFile: string | null;
  loading: boolean;
  onSelect: (filename: string) => void;
  onUpload: (file: File) => void;
  onNewTemplate: () => void;
}

type SidebarView = "gallery" | "list";

export function ExamplesSidebar({
  examples,
  activeFile,
  loading,
  onSelect,
  onUpload,
  onNewTemplate,
}: ExamplesSidebarProps) {
  const [view, setView] = useState<SidebarView>("gallery");
  const valid = examples.filter((e) => e.category === "valid");
  const errors = examples.filter((e) => e.category === "error");

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-slate-700/80 bg-slate-900/60">
      <div className="border-b border-slate-700/80 p-3">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          Przykłady
        </h2>
        <div className="mt-2 flex gap-1">
          <button
            type="button"
            onClick={() => setView("gallery")}
            className={`flex-1 rounded px-2 py-1 text-[10px] font-medium ${
              view === "gallery"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            Galeria
          </button>
          <button
            type="button"
            onClick={() => setView("list")}
            className={`flex-1 rounded px-2 py-1 text-[10px] font-medium ${
              view === "list"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            Lista
          </button>
        </div>
        <div className="mt-2 flex flex-col gap-1.5">
          <label className="cursor-pointer rounded-md bg-indigo-600 px-2 py-1.5 text-center text-xs font-medium text-white hover:bg-indigo-500">
            Otwórz plik .nl
            <input
              type="file"
              accept=".nl"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) onUpload(file);
                e.target.value = "";
              }}
            />
          </label>
          <button
            type="button"
            onClick={onNewTemplate}
            className="rounded-md border border-slate-600 px-2 py-1.5 text-xs text-slate-300 hover:bg-slate-800"
          >
            Nowy szablon
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto text-sm">
        {loading && <p className="px-3 py-2 text-slate-500">Ładowanie...</p>}

        {!loading && view === "gallery" && (
          <ExamplesGallery
            examples={examples}
            activeFile={activeFile}
            onSelect={onSelect}
          />
        )}

        {!loading && view === "list" && (
          <div className="p-2">
            <p className="mb-1 px-2 text-[10px] font-semibold uppercase text-emerald-500/90">
              Poprawne
            </p>
            <ul className="mb-3 space-y-0.5">
              {valid.map((ex) => (
                <li key={ex.filename}>
                  <button
                    type="button"
                    onClick={() => onSelect(ex.filename)}
                    className={`w-full truncate rounded px-2 py-1 text-left text-xs hover:bg-slate-800 ${
                      activeFile === ex.filename
                        ? "bg-indigo-900/50 text-indigo-200"
                        : "text-slate-300"
                    }`}
                    title={ex.title ?? ex.filename}
                  >
                    {ex.title ?? ex.filename}
                  </button>
                </li>
              ))}
            </ul>

            <p className="mb-1 px-2 text-[10px] font-semibold uppercase text-rose-400/90">
              Błędy (test)
            </p>
            <ul className="space-y-0.5">
              {errors.map((ex) => (
                <li key={ex.filename}>
                  <button
                    type="button"
                    onClick={() => onSelect(ex.filename)}
                    className={`w-full truncate rounded px-2 py-1 text-left text-xs hover:bg-slate-800 ${
                      activeFile === ex.filename
                        ? "bg-rose-900/40 text-rose-200"
                        : "text-slate-400"
                    }`}
                    title={ex.title ?? ex.filename}
                  >
                    {ex.title ?? ex.filename}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </aside>
  );
}
