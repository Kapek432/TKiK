import { loadWASM } from "onigasm";
import { Registry } from "monaco-textmate";
import { wireTmGrammars } from "monaco-editor-textmate";
import type * as Monaco from "monaco-editor";

import {
  NEUROLANG_MONACO_THEME_RULES,
  NEUROLANG_RAW_THEME,
  NEUROLANG_THEME_ID,
} from "./neurolangTheme";

const GRAMMAR_URL = "/syntaxes/neurolang.tmLanguage.json";
const ONIGASM_URL = "/onigasm.wasm";
const TM_SCOPE = "source.neurolang";
const LANGUAGE_ID = "neurolang";

let setupPromise: Promise<void> | null = null;

export async function setupNeurolangTextMate(
  monaco: typeof Monaco,
  editor: Monaco.editor.ICodeEditor,
): Promise<void> {
  if (setupPromise) {
    await setupPromise;
    return;
  }

  setupPromise = (async () => {
    await loadWASM(ONIGASM_URL);

    const registry = new Registry({
      theme: NEUROLANG_RAW_THEME,
      getGrammarDefinition: async (scopeName) => {
        if (scopeName !== TM_SCOPE) {
          throw new Error(`Unknown grammar scope: ${scopeName}`);
        }
        const content = await fetch(GRAMMAR_URL).then((response) => {
          if (!response.ok) {
            throw new Error(`Failed to load grammar: ${GRAMMAR_URL}`);
          }
          return response.text();
        });
        return { format: "json", content };
      },
    });

    monaco.languages.register({
      id: LANGUAGE_ID,
      extensions: [".nl"],
      aliases: ["NeuroLang", "neurolang"],
    });

    monaco.editor.defineTheme(NEUROLANG_THEME_ID, {
      base: "vs-dark",
      inherit: true,
      rules: [...NEUROLANG_MONACO_THEME_RULES],
      colors: {
        "editor.background": "#0f1117",
      },
    });

    const grammars = new Map<string, string>();
    grammars.set(LANGUAGE_ID, TM_SCOPE);

    await wireTmGrammars(monaco, registry, grammars, editor);
  })();

  await setupPromise;
}

export { LANGUAGE_ID, NEUROLANG_THEME_ID };
