# Skaner wyrażeń matematycznych - Python

## Opis
Nasz skaner będzie skanował wyrażenia matematyczne, takie jak `2+3*(76+8/3)`, i rozpoznawał tokeny - pary `(kod, wartość)`. Skaner będzie wywoływany w pętli aż do napotkania końca wyrażenia (`EOF`).

## Tokeny

Dla naszego skanera zdefiniujemy następujące tokeny:

| Kod | Opis | Przykład |
|---|---|---|
| `INT` | Liczba całkowita | `1897`, `2`, `11092001` |
| `ID` | Identyfikator | `x`, `abc1`, `my_var` |
| `PLUS` | `+` | `+` |
| `MINUS` | `-` | `-` |
| `MUL` | `*` | `*` |
| `DIV` | `/` | `/` |
| `LPAREN` | `(` | `(` |
| `RPAREN` | `)` | `)` |ś
| `EOF` | Koniec wyrażenia | - |
| `ERROR` | Nieznany znak | `@`, `#` |

---

## Klasa `Token`

### Pola

| Pole | Typ Pythona | Opis |
|---|---|---|
| `key` | `str` | Nazwa typu tokenu, np. `'INT'`, `'PLUS'` |
| `value` | `str` | Dosłowny tekst z wyrażenia, np. `'76'`, `'+'` |
| `column` | `int` | Pozycja w wyrażeniu, liczona od 1 |

### Przykłady obiektów

| Wyrażenie | Obiekt Token |
|---|---|
| `2137` na pozycji 420 | `Token('INT', '2137', 420)` |
| `+` na pozycji 8 | `Token('PLUS', '+', 8)` |
| `@` na pozycji 5 | `Token('ERROR', '@', 5)` |
| koniec na pozycji 13 | `Token('EOF', '', 13)` |

---

## Działanie skanera

Funkcja `next_token(expr: str, pos: int)` zwraca `tuple[Token, int]`:

1. **Pomiń białe znaki** - pomija wszystkie spacje i tabulatory, aktualizując `pos` i kolumnę
2. **EOF** - jeśli `pos` jest poza długością `expr`, zwraca token `EOF`
3. **Cyfra** - zbiera kolejne cyfry, tworząc token `INT`
4. **Litera / Cyfra (po literze lub _) / `_`** - zbiera litery, cyfry i `_`, tworząc token `ID`
5. **Operator / nawias** - tworzy tokeny dla operatorów i nawiasów na podstawie słownika
6. **Inny znak** - tworzy token `ERROR` z numerem kolumny i kontynuuje skanowanie
---

## Obsługa błędów

- Nieznany znak -> token `ERROR` z numerem kolumny 
- Skanowanie **kontynuowane** po błędzie - raport wszystkich błędów na końcu w `main()`

---

## Przykład

Wejście: `2+3*(76+8/3)`

```
(INT, '2')     col. 1
(PLUS, '+')    col. 2
(INT, '3')     col. 3
(MUL, '*')     col. 4
(LPAREN, '(')  col. 5
(INT, '76')    col. 6
(PLUS, '+')    col. 8
(INT, '8')     col. 9
(DIV, '/')     col. 10
(INT, '3')     col. 11
(RPAREN, ')')  col. 12
(EOF, '')      col. 13
```

Wejście: `2 + @3`
```
(INT, '2')     col. 1
(PLUS, '+')    col. 3
(ERROR, '@')   col. 5
(INT, '3')     col. 6
(EOF, '')      col. 7
```