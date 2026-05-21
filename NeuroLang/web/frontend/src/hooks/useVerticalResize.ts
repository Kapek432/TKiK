import { useCallback, useEffect, useRef, useState } from "react";

const DEFAULT_HEIGHT = 256;
const MIN_HEIGHT = 120;
const MAX_HEIGHT = 720;

/**
 * Hook do zmiany wysokości panelu przez przeciąganie krawędzi (oś pionowa).
 */
export function useVerticalResize(
  initial: number = DEFAULT_HEIGHT,
  min: number = MIN_HEIGHT,
  max: number = MAX_HEIGHT,
) {
  const [height, setHeight] = useState(initial);
  const dragging = useRef(false);
  const startRef = useRef({ y: 0, h: initial });

  const onMouseDown = useCallback(
    (event: React.MouseEvent) => {
      event.preventDefault();
      dragging.current = true;
      startRef.current = { y: event.clientY, h: height };
      document.body.style.cursor = "row-resize";
      document.body.style.userSelect = "none";
    },
    [height],
  );

  useEffect(() => {
    const onMouseMove = (event: MouseEvent) => {
      if (!dragging.current) return;
      const delta = startRef.current.y - event.clientY;
      const next = Math.min(max, Math.max(min, startRef.current.h + delta));
      setHeight(next);
    };

    const onMouseUp = () => {
      if (!dragging.current) return;
      dragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
    return () => {
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };
  }, [min, max]);

  return { height, onResizeMouseDown: onMouseDown };
}
