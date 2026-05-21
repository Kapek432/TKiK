import type { CSSProperties } from "react";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

export const pythonHighlightStyle: Record<string, CSSProperties> = Object.fromEntries(
  Object.entries(oneDark).map(([key, value]) => [
    key,
    {
      ...value,
      background: "transparent",
      backgroundColor: "transparent",
    },
  ]),
);

export const pythonLineNumberStyle: CSSProperties = {
  minWidth: "2.75em",
  paddingRight: "1em",
  textAlign: "right",
  color: "#5c6370",
  background: "transparent",
  backgroundColor: "transparent",
  userSelect: "none",
};
