# Uproszczony skaner i kolorowanie składni Pythona

## Opis
Projekt zawiera prosty skaner (lexer) dla języka Python oraz dwa sposoby jego wykorzystania:
- generowanie kolorowanego HTML,
- wypisywanie tokenów w terminalu.

Każdy token ma:
- `key` (typ tokenu),
- `value` (tekst tokenu),
- `line` (numer linii),
- `column` (numer kolumny).

## Struktura plików
- `scanner.py` - główny skaner; zwraca listę tokenów `Token`.
- `tokens.py` - definicje słów kluczowych i operatorów (1- i wieloznakowych).
- `token_printer.py` - wypisuje tokeny do terminala (tabela: typ, wartość, linia, kolumna).
- `highlighter.py` - buduje plik `.html` z kolorowaniem składni na bazie tokenów.
- `css_class.py` - mapowanie typów tokenów (`key`) na klasy CSS.
- `html_template.py` - szablon HTML + style używane przez `highlighter.py`.

## Rozpoznawane elementy (tokeny)
Skaner obsługuje m.in.:
- słowa kluczowe (`KEYWORD`),
- identyfikatory (`ID`),
- liczby (`INT`, `FLOAT`),
- stringi (`STRING`, `FSTRING`, w tym potrójne cudzysłowy),
- komentarze (`COMMENT`),
- operatory i znaki interpunkcyjne,
- tokeny strukturalne (`INDENT`, `DEDENT`, `NEWLINE`, `EOF`),
- token błędu (`ERROR`) dla nieznanych znaków.

## Uruchomienie

### 1) Wypisywanie tokenów w terminalu
Z katalogu `TKiK/kolorowanie_skladni`:

```bash
python3 token_printer.py <plik_wejściowy.py>
```

Przykład:

```bash
python3 token_printer.py scanner.py
```

### 2) Generowanie kolorowanego HTML
Z katalogu `TKiK/kolorowanie_skladni`:

```bash
python3 highlighter.py <plik_wejściowy.py> <plik_wyjściowy.html>
```

Przykład:

```bash
python3 highlighter.py scanner.py output.html
```

## Ograniczenia
Najważniejsze ograniczenia (których jesteśmy świadomi 🙂, jest ich na pewno wiele więcej):
- wnętrze f-stringów nie jest analizowane składniowo (`{...}` nie jest osobno tokenizowane),
- nazwy wbudowane (`int`, `str`, `float` itd.) są traktowane jak zwykłe `ID`,
- skaner nie odtwarza wszystkich niuansów tokenizacji Pythona 

Najprawdopodobniej nie będzie obsługiwał jeszcze wielu innych przypadków możliwych w Pythonie, ale powinien działać poprawnie dla większości typowych konstrukcji.