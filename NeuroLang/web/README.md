# NeuroLang Studio (GUI webowe)

Aplikacja webowa do pracy z kompilatorem NeuroLang: edycja plików `.nl`, kompilacja do Pythona, planer potoku, podgląd AST i błędów.

## Architektura

- **Backend:** FastAPI (`web/backend/`) - REST API, wspólna logika w `src/services/compiler_service.py`
- **Frontend:** React + Vite + TypeScript + Tailwind (`web/frontend/`)
- **Kolorowanie `.nl`:** ten sam plik TextMate co rozszerzenie VS Code (`monaco-editor-textmate` + `neurolang.tmLanguage.json`)

## Kolorowanie składni NeuroLang (TextMate)

Studio ładuje gramatykę z:

`vscode-extension/neurolang/syntaxes/neurolang.tmLanguage.json`

(skopiowaną do `web/frontend/public/syntaxes/` przy buildzie / po `npm run sync-grammar`).

Po zmianie gramatyki w rozszerzeniu VS Code zsynchronizuj kopię:

```bash
cd web/frontend
npm run sync-grammar
```

Następnie odśwież przeglądarkę (Vite dev przeładuje plik z `public/`).

## Wymagania

- Python >= 3.11 z [uv](https://docs.astral.sh/uv/)
- Node.js >= 18 (npm) - tylko dla frontendu

## Uruchomienie (dev)

W dwóch terminalach, z katalogu `TKiK/NeuroLang/`:

### Terminal 1 - API (port 8000)

```bash
uv sync --extra gui
uv run neurolang-web
```

### Terminal 2 - frontend (port 5173)

```bash
cd web/frontend
npm install
npm run dev
```

Otwórz w przeglądarce: **[http://localhost:5173](http://localhost:5173)**

Proxy Vite przekierowuje `/api/*` na `http://127.0.0.1:8000`.

## Funkcje interfejsu


| Obszar                   | Opis                                                                                                            |
| ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| **Sidebar przykładów**   | Lista `examples/*.nl` (poprawne i `err_*`), upload pliku, nowy szablon                                          |
| **Edytor Monaco**        | Edycja kodu NeuroLang                                                                                           |
| **Planer potoku**        | Checklist kroków (dane -> sieć -> config -> train), detekcja słów kluczowych, wstawianie szablonów              |
| **Kompiluj**             | `POST /api/compile` - generuje Python; opcjonalnie wizualizacja (`-v`)                                          |
| **Uruchom**              | `POST /api/run` (SSE) - uruchamia wygenerowany skrypt PyTorch (jak `neurolang -r`); logi na żywo w zakładce Log |
| **Zakładki**             | Python (wygenerowany kod), AST, Błędy (linia/kolumna + kontekst), Log                                           |
| **Pobierz .py**          | Zapis wygenerowanego skryptu lokalnie                                                                           |
| **Przejdź do linii**     | Przy błędzie skok w edytorze do `line`                                                                          |
| **Galeria przykładów**   | Karty z tytułem, opisem i tagami (`examples/catalog.json`)                                                      |
| **Zakładka Graf**        | Po kompilacji z „Wizualizacja (-v)” - podgląd PNG architektury (torchview)                                      |
| **Zakładka NL | Python** | Porównanie obok siebie: źródło `.nl` i wygenerowany `.py`                                                       |


## Endpointy API


| Metoda | Ścieżka                               |
| ------ | ------------------------------------- |
| GET    | `/api/health`                         |
| GET    | `/api/examples`                       |
| GET    | `/api/examples/{filename}`            |
| POST   | `/api/compile`                        |
| POST   | `/api/ast`                            |
| GET    | `/api/metadata/components`            |
| GET    | `/api/metadata/datasets`              |
| POST   | `/api/upload`                         |
| POST   | `/api/run` (SSE: `text/event-stream`) |


`**POST /api/run`** - body JSON: `python_code` (po kompilacji) lub `source` (skompiluj i uruchom). Zdarzenia SSE: `start`, `log` (linia stdout), `done` (exit_code), `error`. Domyślny timeout: 600 s.

## Build produkcyjny (frontend)

```bash
cd web/frontend
npm run build
```

