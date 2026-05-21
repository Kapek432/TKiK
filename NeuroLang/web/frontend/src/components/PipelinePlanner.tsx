import type { PipelineStep } from "../types";
import { TEMPLATES } from "../templates";

const STEPS: PipelineStep[] = [
  { id: "data", label: "Dane (load_data)", keyword: "load_data" },
  { id: "network", label: "Sieć (network + layer)", keyword: "network" },
  { id: "config", label: "Konfiguracja (train_config)", keyword: "train_config" },
  { id: "train", label: "Trening (train)", keyword: "train" },
  { id: "evaluate", label: "Ewaluacja (evaluate)", keyword: "evaluate", optional: true },
  { id: "save", label: "Zapis (save / export)", keyword: "save", optional: true },
  { id: "if", label: "Warunki (if / else)", keyword: "if ", optional: true },
];

function detectSteps(source: string): Set<string> {
  const found = new Set<string>();
  const lower = source.toLowerCase();
  if (/\bload_data\b/.test(lower) || /\bload_model\b/.test(lower)) found.add("data");
  if (/\bnetwork\b/.test(lower)) found.add("network");
  if (/\btrain_config\b/.test(lower)) found.add("config");
  if (/\btrain\b/.test(lower)) found.add("train");
  if (/\bevaluate\b/.test(lower)) found.add("evaluate");
  if (/\b(save|export)\b/.test(lower)) found.add("save");
  if (/\bif\b/.test(lower)) found.add("if");
  return found;
}

interface PipelinePlannerProps {
  source: string;
  components: string[];
  datasets: string[];
  onInsertTemplate: (key: string) => void;
}

export function PipelinePlanner({
  source,
  components,
  datasets,
  onInsertTemplate,
}: PipelinePlannerProps) {
  const detected = detectSteps(source);
  const requiredDone = ["data", "network", "config", "train"].every((id) =>
    detected.has(id),
  );

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-l border-slate-700/80 bg-slate-900/60">
      <div className="border-b border-slate-700/80 p-3">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          Planer potoku
        </h2>
        <p
          className={`mt-1 text-xs ${requiredDone ? "text-emerald-400" : "text-amber-400"}`}
        >
          {requiredDone
            ? "Wymagane kroki: komplet"
            : "Uzupełnij: dane, sieć, config, train"}
        </p>
      </div>

      <ul className="flex-1 space-y-1 overflow-y-auto p-2 text-sm">
        {STEPS.map((step) => {
          const done = detected.has(step.id);
          return (
            <li
              key={step.id}
              className="flex items-start gap-2 rounded-md px-2 py-1.5 hover:bg-slate-800/80"
            >
              <span
                className={`mt-0.5 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded border text-[10px] ${
                  done
                    ? "border-emerald-500 bg-emerald-500/20 text-emerald-400"
                    : "border-slate-600 text-slate-500"
                }`}
              >
                {done ? "✓" : ""}
              </span>
              <div className="min-w-0 flex-1">
                <span className={done ? "text-slate-200" : "text-slate-400"}>
                  {step.label}
                  {step.optional && (
                    <span className="ml-1 text-[10px] text-slate-500">(opc.)</span>
                  )}
                </span>
                {TEMPLATES[step.id === "if" ? "if_block" : step.id] && (
                  <button
                    type="button"
                    onClick={() =>
                      onInsertTemplate(step.id === "if" ? "if_block" : step.id)
                    }
                    className="mt-1 block text-[10px] text-indigo-400 hover:text-indigo-300"
                  >
                    Wstaw szablon
                  </button>
                )}
              </div>
            </li>
          );
        })}
      </ul>

      <div className="border-t border-slate-700/80 p-2 text-[10px] text-slate-500">
        <p className="mb-1 font-semibold text-slate-400">Datasety</p>
        <p className="line-clamp-2">{datasets.slice(0, 6).join(", ")}...</p>
        <p className="mb-1 mt-2 font-semibold text-slate-400">Komponenty</p>
        <p className="line-clamp-2">{components.slice(0, 8).join(", ")}...</p>
      </div>
    </aside>
  );
}
