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
| `GPU_AVAILABLE` | `gpu_available` | Warunek dostępności GPU (CUDA) |
| `MPS_AVAILABLE` | `mps_available` | Warunek dostępności MPS (Apple Silicon) |
| `HAS_DATA` | `has_data` | Warunek sprawdzenia czy dane są wczytane |
| `NUMBER` | `[0-9]+` | Literały liczbowe (całkowite i zmiennoprzecinkowe) |
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
condition: "gpu_available" -> cond_gpu
         | "mps_available" -> cond_mps
         | "has_data" -> cond_has_data
         | CNAME -> cond_var

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
