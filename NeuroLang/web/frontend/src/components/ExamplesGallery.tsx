import type { ExampleInfo } from "../types";

interface ExamplesGalleryProps {
  examples: ExampleInfo[];
  activeFile: string | null;
  onSelect: (filename: string) => void;
}

export function ExamplesGallery({
  examples,
  activeFile,
  onSelect,
}: ExamplesGalleryProps) {
  const valid = examples.filter((e) => e.category === "valid");
  const errors = examples.filter((e) => e.category === "error");

  return (
    <div className="space-y-3 p-2">
      <p className="px-1 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
        Galeria przykładów
      </p>

      <div className="space-y-2">
        {valid.map((ex) => (
          <GalleryCard
            key={ex.filename}
            example={ex}
            active={activeFile === ex.filename}
            onSelect={() => onSelect(ex.filename)}
            variant="valid"
          />
        ))}
      </div>

      <p className="px-1 pt-1 text-[10px] font-semibold uppercase tracking-wide text-rose-400/80">
        Testy błędów
      </p>
      <div className="space-y-2">
        {errors.map((ex) => (
          <GalleryCard
            key={ex.filename}
            example={ex}
            active={activeFile === ex.filename}
            onSelect={() => onSelect(ex.filename)}
            variant="error"
          />
        ))}
      </div>
    </div>
  );
}

function GalleryCard({
  example,
  active,
  onSelect,
  variant,
}: {
  example: ExampleInfo;
  active: boolean;
  onSelect: () => void;
  variant: "valid" | "error";
}) {
  const title = example.title ?? example.filename;
  const border =
    variant === "valid"
      ? active
        ? "border-indigo-500 bg-indigo-950/40"
        : "border-slate-700 hover:border-indigo-600/50 hover:bg-slate-800/80"
      : active
        ? "border-rose-500/70 bg-rose-950/30"
        : "border-slate-700/80 hover:border-rose-600/40 hover:bg-slate-800/60";

  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full rounded-lg border p-2.5 text-left transition-colors ${border}`}
    >
      <p className="text-xs font-semibold text-slate-100">{title}</p>
      {example.description && (
        <p className="mt-1 line-clamp-2 text-[10px] leading-snug text-slate-400">
          {example.description}
        </p>
      )}
      {example.tags && example.tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {example.tags.slice(0, 4).map((tag) => (
            <span
              key={tag}
              className="rounded bg-slate-800 px-1.5 py-0.5 text-[9px] text-slate-400"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
      <p className="mt-1.5 font-mono text-[9px] text-slate-600">{example.filename}</p>
    </button>
  );
}
