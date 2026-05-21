import type { IRawTheme } from "monaco-textmate";

/** Kolory zbliżone do VS Code Dark+ dla scopeów NeuroLang. */
export const NEUROLANG_RAW_THEME: IRawTheme = {
  name: "neurolang-dark",
  settings: [
    { settings: { foreground: "#d4d4d4", background: "#1e1e1e" } },
    {
      scope: ["comment.line.number-sign.neurolang", "comment"],
      settings: { foreground: "#6a9955", fontStyle: "italic" },
    },
    {
      scope: ["string.quoted.double.neurolang", "string"],
      settings: { foreground: "#ce9178" },
    },
    {
      scope: ["constant.numeric.neurolang", "constant.numeric"],
      settings: { foreground: "#b5cea8" },
    },
    {
      scope: [
        "constant.language.boolean.neurolang",
        "constant.language.predicate.neurolang",
        "constant.language.device.neurolang",
      ],
      settings: { foreground: "#569cd6" },
    },
    {
      scope: ["keyword.declaration.neurolang", "keyword.control.neurolang"],
      settings: { foreground: "#c586c0" },
    },
    {
      scope: ["keyword.operator.logical.neurolang"],
      settings: { foreground: "#c586c0" },
    },
    {
      scope: [
        "support.function.builtin.neurolang",
        "entity.name.function.neurolang",
      ],
      settings: { foreground: "#dcdcaa" },
    },
    {
      scope: ["variable.parameter.neurolang"],
      settings: { foreground: "#9cdcfe" },
    },
    {
      scope: [
        "keyword.operator.comparison.neurolang",
        "keyword.operator.arithmetic.neurolang",
        "keyword.operator.assignment.neurolang",
      ],
      settings: { foreground: "#d4d4d4" },
    },
    {
      scope: ["variable.other.neurolang"],
      settings: { foreground: "#9cdcfe" },
    },
  ],
};

/** Reguły motywu Monaco (muszą odpowiadać tokenom z TextMate). */
export const NEUROLANG_MONACO_THEME_RULES = [
  { token: "comment.line.number-sign.neurolang", foreground: "6a9955", fontStyle: "italic" },
  { token: "string.quoted.double.neurolang", foreground: "ce9178" },
  { token: "constant.numeric.neurolang", foreground: "b5cea8" },
  { token: "constant.language.boolean.neurolang", foreground: "569cd6" },
  { token: "constant.language.predicate.neurolang", foreground: "569cd6" },
  { token: "constant.language.device.neurolang", foreground: "569cd6" },
  { token: "keyword.declaration.neurolang", foreground: "c586c0" },
  { token: "keyword.control.neurolang", foreground: "c586c0" },
  { token: "keyword.operator.logical.neurolang", foreground: "c586c0" },
  { token: "support.function.builtin.neurolang", foreground: "dcdcaa" },
  { token: "entity.name.function.neurolang", foreground: "dcdcaa" },
  { token: "variable.parameter.neurolang", foreground: "9cdcfe" },
  { token: "keyword.operator.comparison.neurolang", foreground: "d4d4d4" },
  { token: "keyword.operator.arithmetic.neurolang", foreground: "d4d4d4" },
  { token: "keyword.operator.assignment.neurolang", foreground: "d4d4d4" },
  { token: "variable.other.neurolang", foreground: "9cdcfe" },
] as const;

export const NEUROLANG_THEME_ID = "neurolang-dark";
