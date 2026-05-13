# NeuroLang - rozszerzenie VS Code / Cursor

Minimalistyczne rozszerzenie typu **TextMate grammar** dla plików `.nl` języka NeuroLang.
Bez Node.js, bez LSP, bez serwera - sam manifest VS Code.

## Co zapewnia

- Kolorowanie składni (`*.nl`):
  - słowa kluczowe (`network`, `train`, `if`, `else`, `repeat`, `load_data`, `train_config`, ...),
  - komponenty wbudowane (`Dense`, `Conv2D`, `ReLU`, `Adam`, `CrossEntropyLoss`, `Accuracy`, ...),
  - predykaty (`gpu_available`, `mps_available`, `has_data`) i urządzenia (`cpu`, `gpu`, `cuda`, `mps`),
  - operatory arytmetyczne, porównania i logiczne,
  - stringi `"..."`, liczby, `true` / `false`,
  - komentarze rozpoczynające się od `#`.
- Konfigurację języka:
  - parowanie i autodomykanie nawiasów `{}`, `[]`, `()`, `""`,
  - togglowanie komentarzy `Ctrl + /` (Cmd + / na macOS),
  - reguły wcięć w blokach.
- Snippety szkieletów (Tab po wpisaniu prefiksu):

  | Prefix    | Co rozwija                                  |
  |-----------|---------------------------------------------|
  | `nw`      | blok `network NazwaSieci(...) { ... }`      |
  | `cfg`     | blok `train_config NazwaConfig { ... }`     |
  | `data`    | `load_data MNIST { ... }`                   |
  | `datacsv` | `load_data "...csv" as Alias { ... }`       |
  | `tr`      | `train Net with Cfg on Data`                |
  | `ife`     | `if ... { ... } else { ... }`               |
  | `ifgpu`   | `if gpu_available { ... } else { ... }`     |
  | `let`     | `let nazwa = wartosc`                       |
  | `rep`     | `repeat N times { ... }`                    |
  | `eval`    | `evaluate Net on Data`                      |
  | `save`    | `save Net to "model.pth"`                   |
  | `exp`     | `export Net to "model.onnx"`                |
  | `pred`    | `predict Net on Data`                       |
  | `sum`     | `summary Net`                               |

- Ikonę plików `.nl` w drzewku eksploratora.

## Instalacja

### Wariant 1 - kopiowanie folderu (najszybsze, polecane na zaliczenie)

```bash
# VS Code
cp -r vscode-extension/neurolang ~/.vscode/extensions/neurolang-0.1.0

# Cursor
cp -r vscode-extension/neurolang ~/.cursor/extensions/neurolang-0.1.0

```

Po skopiowaniu zrestartuj edytor (`Cmd+Shift+P` -> `Developer: Reload Window`).

### Wariant 2 - paczka `.vsix`

Wymaga `npx`:

```bash
cd vscode-extension/neurolang
npx @vscode/vsce package
```

Wygenerowany plik `neurolang-0.1.0.vsix` instalujesz w edytorze przez:

`Cmd+Shift+P` -> `Extensions: Install from VSIX...` -> wskaż plik.

### Wariant 3 - tryb deweloperski

1. Otwórz katalog `vscode-extension/neurolang/` jako workspace w VS Code / Cursor.
2. Naciśnij `F5` (`Run Extension`) - uruchomi się nowe okno edytora z załadowanym rozszerzeniem.
3. W tym oknie otwórz dowolny plik `.nl` z `examples/`.

## Weryfikacja, że działa

1. Otwórz `examples/01_mnist_basic.nl`.
2. Sprawdź, czy w prawym dolnym rogu paska statusu język wykrywany jest jako **NeuroLang** (nie `Plain Text`).
3. `network`, `train_config`, `load_data`, `train`, `save` powinny być pokolorowane jak słowa kluczowe.
4. `Dense`, `Conv2D`, `ReLU`, `Adam`, `CrossEntropyLoss`, `Accuracy` - jak funkcje wbudowane.
5. W pustym pliku `.nl` wpisz `nw` i naciśnij Tab - powinien rozwinąć się szkielet sieci.

## Co świadomie pominięto

- LSP / live diagnostyka błędów semantycznych - wymaga osobnego serwera (`pygls`); obecny zakres to wyłącznie kolorowanie i ergonomia edycji.
- Publikacja w Marketplace - wymaga konta publishera Azure DevOps.

