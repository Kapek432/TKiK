from operators import OPERATORS
from examples import TEST_EXPRESSIONS


class Token:
    """
    Klasa reprezentująca token - podstawową jednostkę leksykalną.
    Atrybuty:
        key (str): Typ tokenu (np. 'INT', 'ID', 'PLUS', 'ERROR', 'EOF')
        value (str): Tekstowa reprezentacja tokenu (np. '123', 'x', '+')
        column (int): Numer kolumny, w której token się zaczyna (licząc od 1)
    """
    def __init__(self, key: str, value: str, column: int) -> None: 
        """
        Inicjalizuje token z podanym typem, wartością i numerem kolumny.
        """
        self.key = key
        self.value = value
        self.column = column

    def __repr__(self) -> str:
        """
        Zwraca czytelną reprezentację tokenu, np. "(INT, '123')  col. 5".
        """
        return f"({self.key}, '{self.value}')  col. {self.column}"

def next_token(expr: str, pos: int) -> tuple[Token, int]:
    """
    Funkcja skanująca `expr` od pozycji `pos`, zwracająca kolejny token i nową pozycję.
    Atrybuty:
        expr (str): Wyrażenie do zeskanowania
        pos (int): Aktualna pozycja w wyrażeniu (indeks)
    Zwraca:
        tuple[Token, int]: Kolejny token i nowa pozycja (indeks) po tokenie
    """
    # 1. Pomijamy białe znaki - spacje i tabulatory
    while pos < len(expr) and expr[pos] in " \t":
        pos += 1
    
    # 2. EOF - jeśli pos jest poza długością expr, zwracamy token EOF
    if pos >= len(expr):
        return Token("EOF", "", pos + 1), pos + 1
    
    # 3. Cyfra - zbieramy ciąg kolejnych cyfr, tworząc token INT
    if expr[pos].isdigit():
        start_pos = pos
        while pos < len(expr) and expr[pos].isdigit():
            pos += 1
        return Token("INT", expr[start_pos:pos], start_pos + 1), pos
    
    # 4. Litera / Cyfra (po literze lub _) / `_` - zbieramy litery, cyfry i _, tworząc token ID
    if expr[pos].isalpha() or expr[pos] == '_':
        start_pos = pos
        while pos < len(expr) and (expr[pos].isalnum() or expr[pos] == '_'):
            pos += 1
        return Token("ID", expr[start_pos:pos], start_pos + 1), pos

    # 5. Operator / nawias - tworzymy tokeny dla operatorów i nawiasów na podstawie słownika
    if expr[pos] in OPERATORS:
        token_key = OPERATORS[expr[pos]]
        token_val = expr[pos]
        return Token(token_key, token_val, pos + 1), pos + 1
    
    # 6. Inny znak - tworzymy token ERROR z numerem kolumny
    return Token("ERROR", expr[pos], pos + 1), pos + 1

def scan_expression(expr: str) -> list[Token]:
    """
    Funkcja skanująca całe wyrażenie, zwracająca listę tokenów.
    Atrybuty:
        expr (str): Wyrażenie do zeskanowania
    Zwraca:
        list[Token]: Lista tokenów znalezionych w wyrażeniu
    """
    tokens = []
    pos = 0
    while True:
        token, pos = next_token(expr, pos)
        tokens.append(token)

        if token.key == "EOF":
            break

    return tokens

def main() -> None:
    """
    Funkcja główna testująca skaner na różnych wyrażeniach.
    """
    for expr in TEST_EXPRESSIONS:
        print(f"Wejście: `{expr}`\n")
        tokens = scan_expression(expr)
        errors = []
        for token in tokens:
            print(token)
            if token.key == "ERROR":
                errors.append(token)

        if errors:
            print("\nNapotkane nieznane tokeny:")
            for error in errors:
                print(error)

        print()

if __name__ == "__main__":
    main()