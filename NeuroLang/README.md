# Projekt: NeuroLang - Autorski język programowania dla sieci neuronowych

## Dane studentów

**Autorzy:** Kacper Lipiec, Przemysław Kondrat  
**Adresy e-mail:** 

- klipiec@student.agh.edu.pl
- pkondrat@student.agh.edu.pl  

## Założenia programu 

### Opis programu
NeuroLang to specjalistyczny język programowania zaprojektowany w celu uproszczenia procesu definiowania, trenowania i zarządzania architekturami głębokich sieci neuronowych. Język pozwala na deklaratywne opisywanie struktur warstwowych, konfigurowanie parametrów uczenia oraz zarządzanie pełnym potokiem operacji na danych (od wczytywania, przez uczenie i warunkowe kroki sterujące, po ewaluację, predykcję i eksport) w sposób czytelny i zwięzły, eliminując powtarzalny kod typowy dla bibliotek takich jak PyTorch czy TensorFlow.

### Cele programu
- Umożliwienie szybkiego prototypowania modeli wizyjnych (CNN) i tablicowych (MLP) wraz z pełnymi potokami ekstrakcyjro-trenującymi.
- Automatyzacja wyliczania wymiarów warstw, zwłaszcza przy sieciach konwolucyjnych i spłaszczaniu tensorów, chroniąca przed niepoprawnymi rozmiarami danych.
- Zapewnienie czytelnej składni dla pętli powtarzających bloki warstw (`repeat`) oraz dynamicznego zarządzania przepływem wykorzystując bloki warunkowe (`if`, `else if`, `else`).
- Wprowadzenie obsługi deklaracji i ewaluacji zmiennych do zagnieżdżania wewnątrz konfiguracji
- Rygorystyczna walidacja semantyczna modelu przed wdrożeniem i tłumaczeniem (z uwzględnieniem sprawdzania poprawności parametrów, dzielenia przez zero, ponownych definicji z tym samym identyfikatorem oraz dokładną diagnostyką obejmującą weryfikację ilości klas we wbudowanych metrykach).

### Rodzaj translatora
NeuroLang jest **kompilatorem (transpilatorem)** kodu NeuroLang do wykonywalnego skryptu w języku **Python**, wykorzystującego bibliotekę **PyTorch**. Wynikiem działania programu jest gotowy do uruchomienia plik `.py`, który zawiera definicję klasy modelu, ładowanie danych oraz kompletną pętlę treningową.

### Język implementacji
Kompilator zostanie zaimplementowany w języku **Python 3.14**.

### Sposób realizacji skanera i parsera
Do realizacji analizy leksykalnej i składniowej wykorzystany będzie generator parserów **Lark**, wykorzystujący algorytm **LALR(1)**. Gramatyka została zdefiniowana w formacie EBNF, co pozwoli na przejrzyste mapowanie reguł języka na węzły drzewa składniowego (AST).

## Opis tokenów

Skaner języka NeuroLang rozpoznaje następujące grupy tokenów:

| Token | Wzorzec / Wartość | Opis |
| :--- | :--- | :--- |
| `LET` | `let` | Słowo kluczowe deklaracji zmiennej |
| `NETWORK` | `network` | Rozpoczęcie bloku definicji sieci |
| `LAYER` | `layer` | Deklaracja pojedynczej warstwy |
| `REPEAT` | `repeat` | Rozpoczęcie pętli powtarzania bloków warstw |
| `LOAD_DATA` | `load_data` | Komenda wczytywania zbioru danych |
| `TRAIN_CONFIG` | `train_config` | Definicja parametrów treningu |
| `TRAIN` | `train` | Rozpoczęcie procesu uczenia sieci |
| `WITH` | `with` | Łącznik wskazujący konfigurację w komendzie train |
| `ON` | `on` | Łącznik wskazujący zbiór danych w komendzie train |
| `USING` | `using` | Opcjonalny wybór urządzenia (cpu/gpu/mps) |
| `FROM` | `from` | Ścieżka źródłowa dla modeli |
| `TO` | `to` | Ścieżka zapisu dla modeli |
| `AS` | `as` | Alias dla zbiorów danych lub modeli |
| `EVALUATE` | `evaluate` | Komenda ewaluacji modelu na zbiorze danych |
| `PRINT` | `print` | Instrukcja wypisywania informacji |
| `SUMMARY` | `summary` | Wyświetlenie podsumowania architektury sieci |
| `EXPORT` | `export` | Eksport modelu do formatu ONNX |
| `PREDICT` | `predict` | Komenda predykcji na danych |
| `IF` | `if` | Rozpoczęcie bloku warunkowego |
| `GPU_AVAILABLE` | `gpu_available` | Predykat: dostępność GPU (CUDA) |
| `MPS_AVAILABLE` | `mps_available` | Predykat: dostępność MPS (Apple Silicon) |
| `HAS_DATA` | `has_data` | Predykat: wczytane dane |
| `AND` | `and` | Koniunkcja logiczna w warunkach |
| `OR` | `or` | Alternatywa logiczna w warunkach |
| `NOT` | `not` | Negacja logiczna w warunkach |
| `CMP_OP` | `==`, `!=`, `<`, `<=`, `>`, `>=` | Operatory porównania wyrażeń arytmetycznych |
| `NUMBER` | `\d+(\.\d+)?` | Literały liczbowe |
| `CNAME` | `[a-zA-Z_][a-zA-Z0-9_]*` | Nazwy zmiennych, sieci i komponentów |
| `ESCAPED_STRING` | `"[^"]*"` | Napisy w cudzysłowach (np. ścieżki do plików) |
| `TRUE / FALSE` | `true / false` | Stałe logiczne |
| `OPERATORS` | `+, -, *, /, //` | Operatory arytmetyczne |
| `PARENS` | `(, )` | Nawiasy wywołań i grupowania |
| `BRACES` | `{, }` | Klamry definicji bloków |
| `BRACKETS` | `[, ]` | Nawiasy kwadratowe dla list (np. metryk) |
| `COLON` | `:` | Separator klucz-wartość |
| `EQ` | `=` | Operator przypisania |
| `COMMA` | `,` | Separator elementów |

## Gramatyka języka (Lark EBNF)

Poniżej znajduje się kompletna gramatyka wykorzystywana przez kompilator:

```ebnf
start: instruction+

instruction: var_decl 
           | network_block 
           | config_block 
           | data_block
           | load_model_cmd
           | train_cmd
           | save_cmd
           | evaluate_cmd
           | print_cmd
           | export_cmd
           | predict_cmd
           | summary_cmd
           | if_block

var_decl: "let" CNAME "=" math_expr [","]
var_assign: CNAME "=" math_expr [","]

network_block: "network" CNAME ["(" arguments ")"] "{" net_statement+ "}"

net_statement: layer_decl 
             | repeat_block 
             | var_assign

layer_decl: "layer" ":" call [","]
repeat_block: "repeat" (NUMBER | CNAME) "times" "{" net_statement+ "}" [","]

data_block: "load_data" (CNAME | ESCAPED_STRING) ["as" CNAME] "{" config_item+ "}"

load_model_cmd: "load_model" CNAME "from" ESCAPED_STRING

config_block: "train_config" CNAME "{" config_item+ "}"

config_item: CNAME ":" config_value [","]
config_value: call | math_expr | boolean | ESCAPED_STRING | list_expr

list_expr: "[" [config_value ("," config_value)*] "]"

train_cmd: "train" CNAME "with" CNAME "on" CNAME ["using" device_type]

!device_type: "cpu" | "gpu" | "cuda" | "mps"

save_cmd: "save" CNAME "to" ESCAPED_STRING

evaluate_cmd: "evaluate" CNAME "on" CNAME

print_cmd: "print" print_arg
print_arg: ESCAPED_STRING -> print_string
         | "summary" CNAME -> print_summary
         | math_expr -> print_expr

export_cmd: "export" CNAME "to" ESCAPED_STRING

predict_cmd: "predict" CNAME "on" (CNAME | ESCAPED_STRING)

summary_cmd: "summary" CNAME

if_block: "if" condition "{" instruction+ "}" elif_clause* [else_clause]
elif_clause: "else" "if" condition "{" instruction+ "}"
else_clause: "else" "{" instruction+ "}"

condition: or_condition
or_condition: and_condition ("or" and_condition)*
and_condition: not_condition ("and" not_condition)*
not_condition: "not" not_condition -> cond_not
             | atom_condition
atom_condition: "(" condition ")" -> cond_group
              | "gpu_available" -> cond_gpu
              | "mps_available" -> cond_mps
              | "has_data" -> cond_has_data
              | boolean -> cond_bool
              | comparison
comparison: math_expr CMP_OP math_expr -> cond_compare
          | math_expr -> cond_math
CMP_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"

call: CNAME "(" [arguments] ")"
arguments: arg ("," arg)*
arg: arg_value | CNAME "=" arg_value
arg_value: call | math_expr | ESCAPED_STRING | boolean | list_expr

math_expr: term (ADD_OP term)*
term: factor (MUL_OP factor)*
factor: NUMBER | CNAME | "(" math_expr ")"

ADD_OP: "+" | "-"
MUL_OP: "*" | "/" | "//"

boolean: "true" -> true_val
       | "false" -> false_val

%import common.CNAME
%import common.NUMBER
%import common.ESCAPED_STRING
%import common.WS
%ignore WS

COMMENT: /#[^\n]*/
%ignore COMMENT
```

## Generatory skanerów/parserów i pakiety zewnętrzne

### Generator parserów
- **[Lark](https://github.com/lark-parser/lark)** (`lark>=1.1.0`) - generator skanerów i parserów dla Pythona. Używamy algorytmu **LALR(1)** (`Lark(..., parser="lalr")`), który gwarantuje liniowy czas parsowania oraz precyzyjne raportowanie pozycji błędów (`line`, `column`). Skaner leksykalny jest generowany automatycznie z reguł EBNF zapisanych w pliku `neurolang.lark`.

### Pakiety zewnętrzne (runtime kompilatora)
- **PyYAML** (`pyyaml>=6.0`) - odczyt `config.yaml` (ścieżki, ustawienia, parametry walidacji).
- **Standard library** - `argparse` (CLI), `logging` (logi), `json` (komponenty / datasety), `subprocess` (uruchamianie wygenerowanego skryptu z flagą `--run`).

### Pakiety zewnętrzne (wymagane przez wygenerowany skrypt PyTorch)
- **PyTorch** (`torch>=2.0.0`) - sieci neuronowe, autograd, trening.
- **torchvision** (`torchvision>=0.15.0`) - wbudowane datasety (MNIST, FashionMNIST, CIFAR10/100).
- **torchmetrics** (`torchmetrics>=0.11.0`) - metryki (Accuracy, Precision, Recall, F1Score, AUROC, MeanSquaredError itp.).
- **pandas** (`pandas>=2.0.0`) - wczytywanie danych z plików `.csv`.
- **tqdm** (`tqdm>=4.65.0`) - paski postępu podczas treningu.
- **torchview** (`torchview>=0.2.6`) - opcjonalna wizualizacja grafu architektury (flaga `-v` / `--visualize`).

### Środowisko deweloperskie (`[project.optional-dependencies] dev`)
- **pytest** (`pytest>=7.0.0`) - framework testowy (81 testów: jednostkowych, integracyjnych, CLI).
- **ruff** (`ruff>=0.1.0`) - linter i formatter.

### Menedżer pakietów / wykonawca
- **uv** - nowoczesny menedżer Pythona (instalacja, środowisko wirtualne, uruchamianie skryptów). Wszystkie polecenia w niniejszym README zakładają `uv` (`uv sync`, `uv run`).

## Wymagania i instalacja

### Wymagania systemowe
- **Python >= 3.11** (zalecane 3.14; testowane na 3.14 przy `uv sync`).
- **uv** - instalacja: [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).
- (Opcjonalnie) **GPU** z CUDA / **Apple Silicon** z MPS - tylko jeśli chcesz trenować na akceleratorze. Sam kompilator działa w pełni na CPU.

### Instalacja zależności

```bash
# zmiana katalogu
cd NeuroLang

# zainstalowanie zależności produkcyjnych
uv sync

# zainstalowanie zależności produkcyjnych + dev (pytest, ruff)
uv sync --extra dev
```

`uv` automatycznie utworzy `.venv/` i zainstaluje wszystkie paczki z `pyproject.toml` + `uv.lock`.

## Krótka instrukcja obsługi

### Wbudowane komendy CLI

Po instalacji w środowisku dostępne są dwa polecenia (`pyproject.toml` -> `[project.scripts]`):

| Polecenie | Co robi |
|-----------|---------|
| `neurolang` | Główny kompilator: parsuje plik `.nl`, waliduje semantykę, generuje skrypt `.py` w PyTorch. |
| `neurolang-ast` | Narzędzie debugowe: parsuje plik `.nl` i wyświetla drzewo składniowe (AST) bez generowania kodu. |

Każde z nich uruchamia się przez `uv run`, np.:

```bash
uv run neurolang --help
uv run neurolang-ast --help
```

### Flagi kompilatora `neurolang`

| Krótka | Długa | Opis |
|--------|-------|------|
| `-h` | `--help` | Wyświetla pomoc. |
| `-i ŚCIEŻKA` | `--input ŚCIEŻKA` | Plik wejściowy `.nl`. Domyślnie z `config.yaml` (`paths.default_input`). |
| `-o ŚCIEŻKA` | `--output ŚCIEŻKA` | Plik wyjściowy `.py`. Domyślnie z `config.yaml` (`paths.default_output`). |
| `-r` | `--run` | Uruchamia wygenerowany skrypt po kompilacji (pełny trening). |
| `-v` | `--visualize` | Dołącza kod generujący graf architektury (`torchview`). |

### Typowe scenariusze użycia

Kompilacja przykładu do wybranego pliku:

```bash
uv run neurolang -i examples/01_mnist_basic.nl -o output/gen_mnist.py
```

Kompilacja z wizualizacją architektury:

```bash
uv run neurolang -i examples/02_mnist_cnn.nl -o output/gen_cnn.py -v
```

Kompilacja **i natychmiastowe** uruchomienie wygenerowanego skryptu (pobiera dane, trenuje - uwaga: długo, wymaga internetu):

```bash
uv run neurolang -i examples/01_mnist_basic.nl -o output/run_mnist.py -r
```

Podgląd drzewa AST (bez generowania kodu):

```bash
uv run neurolang-ast -i examples/01_mnist_basic.nl
```
---

## Przykład użycia

### Plik wejściowy NeuroLang (`examples/01_mnist_basic.nl`)

```neurolang
# Prosty przykład sieci MLP dla zbioru MNIST

# 1. Konfiguracja danych
load_data MNIST {
    batch_size: 128,
    shuffle: true
}

# 2. Architektura sieci
network SimpleMLP(1, 28, 28) {
    layer: Flatten(),
    layer: Dense(784, 512),
    layer: ReLU(),
    layer: Dropout(0.2),
    layer: Dense(512, 10)
}

# 3. Parametry treningu
train_config BasicConfig {
    epochs: 5,
    learning_rate: 0.001,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

# 4. Uruchomienie
train SimpleMLP with BasicConfig on MNIST
save SimpleMLP to "mnist_mlp.pth"
```

### Kompilacja

```bash
uv run neurolang -i examples/01_mnist_basic.nl -o output/mnist.py
```

### Co dostaniemy na wyjściu (`output/mnist.py`, skrócone)

Wygenerowany skrypt zawiera m.in.:
- importy (`torch`, `torchvision`, `torchmetrics`, `pandas`, `tqdm`),
- ustawienie urządzenia (`device = torch.device("cpu")`),
- `DataLoader` z MNIST,
- klasę modelu `SimpleMLP(nn.Module)` opartą o `nn.Sequential`,
- pełną pętlę treningową z funkcją straty, optimizerem i metrykami,
- zapis wytrenowanego modelu do pliku `mnist_mlp.pth`.

Wynikowy plik można uruchomić ręcznie:

```bash
uv run python output/mnist.py
```

albo natychmiastowo po kompilacji z flagą `-r`:

```bash
uv run neurolang -i examples/01_mnist_basic.nl -o output/mnist.py -r
```

### Inne gotowe przykłady (`examples/`)

Repozytorium zawiera kompletny korpus przykładów demonstrujących wszystkie funkcje języka:

| Kategoria | Pliki |
|-----------|-------|
| **Klasyfikacja obrazów** | `01_mnist_basic.nl`, `02_mnist_cnn.nl`, `03_fashion_mnist_cnn.nl`, `04_cifar10_cnn.nl` |
| **Dane tablicowe / CSV** | `05_tabular_data_csv.nl`, `10_binary_classification_csv.nl`, `11_regression_csv.nl` |
| **Zaawansowane konstrukcje** | `06_advanced_features.nl` (zmienne `let`, `repeat`), `07_evaluation.nl`, `08_full_pipeline.nl` |
| **Sterowanie przepływem** | `09_if_statements.nl`, `14_advanced_conditions.nl`, `15_comparison_branching.nl` |
| **Wiele sieci / konfiguracji** | `12_multiconfig_binding.nl`, `13_two_networks_trainable.nl` |
| **Błędy (testy negatywne)** | `err_*.nl` - każdy plik celowo łamie jedną regułę semantyki lub składni (do prezentacji diagnostyki) |

## Struktura projektu

```
NeuroLang/
├── neurolang.lark            # Gramatyka EBNF (Lark)
├── components.json           # Mapowanie warstw NeuroLang -> klasy PyTorch
├── datasets.json             # Wbudowane datasety (MNIST, CIFAR, ...)
├── config.yaml               # Konfiguracja projektu (ścieżki, logging, walidacja)
├── pyproject.toml            # Definicja pakietu, zależności, skrypty CLI
├── examples/                 # Programy NeuroLang (.nl)
├── data/                     # Przykładowe pliki csv
└── src/                      # Kod kompilatora
    ├── cli/                  # Punkty wejścia 
    │   ├── compile.py
    │   └── show_ast.py
    ├── parser/               # Wrapper na Lark
    │   └── grammar.py
    ├── semantic/             # Dwufazowa analiza semantyczna
    │   ├── visitor.py        # pass 1 - top-down (let, network shape)
    │   ├── transformer.py    # pass 2 - bottom-up (walidacja + struktura)
    │   ├── shape_inference.py
    │   ├── validators.py
    │   └── symbol_table.py
    ├── codegen/              # Generator kodu PyTorch 
    │   ├── generator.py      # Orkiestrator
    │   ├── imports.py
    │   ├── device.py
    │   ├── data.py
    │   ├── model.py
    │   ├── training.py
    │   ├── evaluation.py
    │   ├── conditions.py
    │   ├── control_flow.py
    │   ├── task.py
    │   ├── indent.py
    ├── config.py             # Wczytywanie config.yaml
    ├── loaders.py            # Ładowanie plików (yaml, json, text)
    └── logger.py             # Konfiguracja loggera
```

## Architektura kompilatora

Pipeline jest klasycznie podzielony na fazy:

1. **Analiza leksykalna i składniowa** - Lark zwraca AST (Tree).
2. **Pass 1 - Visitor (top-down)** - ewaluuje `let X = ...`, wyciąga wymiary wejściowe z nagłówków `network Net(C, H, W)`.
3. **Pass 2 - Transformer (bottom-up)** - walidacja typów parametrów, shape inference dla `Conv2D`/`MaxPool2D`/`Dense`/`Flatten`, zgodność liczby klas w metrykach z wyjściem sieci, wykrywanie redeklaracji i dzielenia przez zero.
4. **Generator** - buduje gotowy skrypt PyTorch z modularnych fragmentów (importy, urządzenie, dane, model, pętla treningowa, ewaluacja, predykcja, sterowanie przepływem, wizualizacja).

## Walidacja semantyczna (najważniejsze sprawdzenia)

- **Niezgodność wymiarów warstw** - `Dense(784, 128) -> Dense(64, 10)` powoduje błąd już przy kompilacji (nie w runtime PyTorch).
- **Conv2D / MaxPool2D / Flatten** - statyczne wyliczanie kolejnych wymiarów; wyłapanie konfiguracji prowadzącej do ujemnego rozmiaru wyjścia.
- **Parametry konfiguracji** - `epochs` musi być dodatnią liczbą całkowitą, `learning_rate` liczbą dodatnią, `Dropout(p)` w przedziale `[0, 1]` itd.
- **Zgodność metryk z wyjściem sieci** - `Accuracy(num_classes=10)` przy sieci dającej 5 wyjść -> błąd.
- **Spójność trybu z funkcją straty** - `task="regression"` z metryką klasyfikacyjną -> błąd.
- **Referencje** - `train/evaluate/predict/save/export/summary` na nieistniejącej sieci, configu lub źródle danych -> błąd.
- **Zmienne** - redeklaracja `let`, użycie niezdefiniowanej zmiennej, dzielenie przez zero w wyrażeniach.
- **Duplikaty kluczy** w `train_config` (`epochs: 5, epochs: 10`).

Każdy komunikat błędu zawiera **numer linii i kolumny** (`[L: ?, C: ?]`).

## Testy

Projekt zawiera **81 testów automatycznych** w katalogu `tests/` (pokrywających semantykę, generator, integrację end-to-end i CLI).

```bash
uv run python -m pytest -v
```

## Konfiguracja projektu (`config.yaml`)

Centralna konfiguracja kompilatora (ścieżki domyślne, format logów, listy lossów per typ zadania, parametry walidacji). Zmiana ustawień nie wymaga modyfikacji kodu Pythona, np. dodanie nowej funkcji straty regresyjnej sprowadza się do dopisania jej do sekcji `validation.regression_losses`.

Pliki pomocnicze:
- [`components.json`](components.json) - mapowanie warstw NeuroLang (`Dense`, `Conv2D`, `Adam`, `CrossEntropyLoss`, ...) na klasy/funkcje PyTorch.
- [`datasets.json`](datasets.json) - metadane wbudowanych zbiorów `torchvision` (MNIST, CIFAR, ...).