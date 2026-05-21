import type { ReactNode } from "react";

interface ResizableOutputPanelProps {
  height: number;
  onResizeMouseDown: (event: React.MouseEvent) => void;
  children: ReactNode;
}

/**
 * Dolny panel z uchwytem do zmiany wysokości przeciąganiem.
 */
export function ResizableOutputPanel({
  height,
  onResizeMouseDown,
  children,
}: ResizableOutputPanelProps) {
  return (
    <div
      className="relative flex shrink-0 flex-col bg-slate-950/80"
      style={{ height }}
    >
      <div
        role="separator"
        aria-orientation="horizontal"
        aria-label="Zmień wysokość panelu wyników"
        title="Przeciągnij, aby zmienić wysokość"
        onMouseDown={onResizeMouseDown}
        className="group absolute left-0 right-0 top-0 z-20 flex h-2 -translate-y-1/2 cursor-row-resize items-center justify-center"
      >
        <div className="h-1 w-16 rounded-full bg-slate-600 transition-colors group-hover:bg-indigo-500 group-active:bg-indigo-400" />
      </div>
      <div className="flex min-h-0 flex-1 flex-col border-t border-slate-700/80 pt-1">
        {children}
      </div>
    </div>
  );
}
