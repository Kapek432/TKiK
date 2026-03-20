from tokens import KEYWORDS, MULTI_CHAR_OPERATORS, SINGLE_CHAR_OPERATORS

class Token:
    """
    Klasa reprezentująca token - podstawową jednostkę leksykalną.
    Atrybuty:
        key (str): Typ tokenu (np. 'INT', 'ID', 'PLUS', 'ERROR', 'EOF')
        value (str): Tekstowa reprezentacja tokenu (np. '123', 'x', '+')
        line (int): Numer linii, w której token się znajduje (licząc od 1)
        column (int): Numer kolumny, w której token się zaczyna (licząc od 1)
    """
    def __init__(self, key: str, value: str, line: int, column: int) -> None:
        """
        Inicializuje token z podanym typem, wartością, numerem linii i kolumny.
        """
        self.key = key
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        """
        Zwraca czytelną reprezentację tokenu, np. "(INT, '123') line 5, col 10".
        """
        return f"({self.key}, '{self.value}')  line {self.line}, col {self.column}"


def _scan_string(src: str, pos: int, col: int) -> tuple[str, int, int]:
    """
    Skanuje ciąg znaków, obsługując zarówno zwykłe stringi, jak i f-stringi, a także pojedyncze i potrójne cudzysłowy.
    Argumenty:
        src (str): Pełny tekst źródłowy.
        pos (int): Indeks pierwszego znaku stringa (lub prefiksu f-stringa).
        col (int): Aktualny numer kolumny.
    Zwraca:
        tuple[str, int, int]: (wartość stringa, nowy indeks po stringu, nowy numer kolumny)
    """
    start = pos
    prefix = ""

    # Obsluga prefiksów stringów 
    while pos < len(src) and src[pos].lower() in "frbu":
        pos += 1
        col += 1

    if pos >= len(src):
        return src[start:pos], pos, col

    # Pobieranie cudzysłowu
    if src[pos:pos+3] in ('"""', "'''"):
        # Potrójny cudzysłów
        delimiter = src[pos:pos+3]
        d_len = 3
    else:
        # Pojedynczy cudzysłów
        delimiter = src[pos]
        d_len = 1
    
    pos += d_len
    col += d_len

    # Szukanie domknięcia stringa
    while pos < len(src):
        if src[pos:pos+d_len] == delimiter:
            pos += d_len
            col += d_len
            break
        
        # Pomiijamy znak ucięcia linii w stringu (np. \n) - ważne dla f-stringów, które mogą być wieloliniowe
        if src[pos] == "\\":
            pos += 2
            col += 2
            continue 
            
        if src[pos] == "\n":
            if d_len == 1: # Zwykły string nie może mieć nowej linii (tylko z \ może) - byłby niedomknięty
                break 
            col = 1
        else:
            col += 1
        pos += 1

    return src[start:pos], pos, col


def _scan_number(src: str, pos: int, col: int) -> tuple[str, str, int, int]:
    """
    Skanuje liczbę, obsługując zarówno liczby całkowite, jak i zmiennoprzecinkowe, a także różne systemy liczbowe (hex, octal, binary).
    Argumenty:
        src (str): Pełny tekst źródłowy.
        pos (int): Indeks pierwszego znaku liczby.
        col (int): Aktualny numer kolumny.
    Zwraca:
        tuple[str, str, int, int]: (key, raw_value, new_pos, new_col)
    """
    start = pos
    is_float = False

    # Hex / octal / binary
    if src[pos] == "0" and pos + 1 < len(src) and src[pos+1].lower() in "xob":
        prefix = src[pos+1].lower()
        pos += 2
        col += 2
        
        # Dozwolone znaki w zależności od systemu liczbowego
        valid_chars = "01" if prefix == "b" else "01234567" if prefix == "o" else "0123456789abcdefABCDEF"
        
        while pos < len(src) and (src[pos] in valid_chars or src[pos] == "_"):
            pos += 1
            col += 1
        return "INT", src[start:pos], pos, col

    # Część całkowita (dla dzesiętnych i zmiennoprzecinkowych)
    while pos < len(src) and (src[pos].isdigit() or src[pos] == "_"):
        pos += 1
        col += 1

    # Część ułamkowa
    if pos < len(src) and src[pos] == "." and (pos + 1 >= len(src) or src[pos+1] != "."):
        is_float = True
        pos += 1
        col += 1
        while pos < len(src) and (src[pos].isdigit() or src[pos] == "_"):
            pos += 1
            col += 1
        return "FLOAT", src[start:pos], pos, col

    # Część wykładnicza (np.: 1e10, 1.5E-5)
    if pos < len(src) and src[pos].lower() == "e":
        is_float = True
        pos += 1
        col += 1
        if pos < len(src) and src[pos] in "+-":
            pos += 1
            col += 1
        while pos < len(src) and (src[pos].isdigit() or src[pos] == "_"):
            pos += 1
            col += 1

    # Liczby urojone (np.: 1j, 3.14j)
    if pos < len(src) and src[pos].lower() == "j":
        is_float = True
        pos += 1
        col += 1

    token_type = "FLOAT" if is_float else "INT"
    return token_type, src[start:pos], pos, col


def _compute_indent(line: str) -> int:
    """
    Oblicza poziom wcięcia linii, traktując tabulatory jako 4 spacje.
    Argumenty:
        line (str): Linia tekstu, dla której obliczamy wcięcie
    Zwraca:
        int: Poziom wcięcia 
    """
    count = 0
    for ch in line:
        if ch == " ":
            count += 1
        elif ch == "\t":
            count += 4
        else:
            break
    return count


def _get_triple_quote_delimiter(value: str) -> str | None:
    """
    Zwraca delimiter potrójnego cudzysłowu, jeśli token stringa go zawiera.
    Argumenty:
        value (str): Wartość tokenu stringa
    Zwraca:
        str | None: Delimiter potrójnego cudzysłowu lub None, jeśli nie jest to potrójny string
    """
    if not value:
        return None

    quote_start = 0
    # Znajdujemy początek rzeczywistego cudzysłowu, pomijając prefiksy stringów
    while quote_start < len(value) and value[quote_start].lower() in "frbu":
        quote_start += 1

    # Sprawdzamy, czy od tego miejsca mamy 3 takie same znaki
    if len(value) >= quote_start + 3:
        delimiter = value[quote_start:quote_start + 3]
        if delimiter in ('"""', "'''"):
            return delimiter

    return None


def _is_unclosed_triple_quoted_string(value: str, delimiter: str) -> bool:
    """
    Sprawdza, czy token potrójnego stringa nie został zamknięty w tej samej linii.
    Argumenty:
        value (str): Wartość tokenu stringa
        delimiter (str): Delimiter potrójnego cudzysłowu
    Zwraca:
        bool: True jeśli string jest niedomknięty, False jeśli jest zamknięty
    """
    quote_start = 0
    while quote_start < len(value) and value[quote_start].lower() in "frbu":
        quote_start += 1
    
    payload = value[quote_start:]

    # Jeśli długość payloadu jest mniejsza niż długość delimitera razy 2, to na pewno nie jest zamknięty
    if len(payload) < 2 * len(delimiter):
        return True
        
    return not payload.endswith(delimiter)


def scan(src: str) -> list[Token]:
    """
    Skanuje cały źródłowy kod Pythona i zwraca listę tokenów.
    Argumenty:
        src (str): Pełny kod źródłowy do zeskanowania
    Zwraca:
        list[Token]: Lista tokenów znalezionych w kodzie źródłowym
    """
    # Lista tokenów, które zostaną zwrócone po przetworzeniu całego źródła
    tokens = []

    # Dzielimy źródło na linie, zachowując znaki nowej linii, aby móc poprawnie śledzić numery linii i kolumn
    lines = src.splitlines(keepends=True)

    # Stos do śledzenia poziomów wcięcia 
    indent_stack = [0]

    # Numer linii, zaczynając od 1
    line_no = 0

    # Zmienna do śledzenia otwartego potrójnego stringa, jeśli jest niedomknięty na końcu linii
    open_multiline_delimiter = None

    # Zmienna do śledzenia typu otwartego potrójnego stringa (STRING lub FSTRING)
    open_multiline_key = "STRING"

    # Jeśli ostatnio napotkaliśmy `def` lub `class`, oczekujemy nazwy funkcji/klasy
    expected_named_token = None

    for raw_line in lines:
        line_no += 1
        stripped = raw_line.rstrip("\r\n")
        line_src = stripped
        continued_multiline_line = False

        # Kontynuacja potrójnego stringa z poprzedniej linii
        if open_multiline_delimiter is not None:
            continued_multiline_line = True
            end_idx = line_src.find(open_multiline_delimiter)
            if end_idx == -1:
                if line_src:
                    tokens.append(Token(open_multiline_key, line_src, line_no, 1))
                tokens.append(Token("NEWLINE", "\\n", line_no, len(line_src) + 1))
                continue

            end_pos = end_idx + len(open_multiline_delimiter)
            tokens.append(Token(open_multiline_key, line_src[:end_pos], line_no, 1))
            open_multiline_delimiter = None

            if end_pos >= len(line_src):
                tokens.append(Token("NEWLINE", "\\n", line_no, len(line_src) + 1))
                continue

            pos = end_pos
            col = end_pos + 1
            while pos < len(line_src) and line_src[pos] in " \t":
                pos += 1
                col += 1
        else:
            pos = 0
            col = 1

        
        if not continued_multiline_line:
            content = stripped.lstrip()
            # Jeśli linia jest pusta lub zawiera tylko komentarz, emitujemy odpowiednie tokeny i przechodzimy do następnej linii
            if not content or content.startswith("#"):
                if content.startswith("#"):
                    indent = len(stripped) - len(content)
                    tokens.append(Token("COMMENT", content, line_no, indent + 1))

                tokens.append(Token("NEWLINE", "\\n", line_no, len(stripped) + 1))
                expected_named_token = None
                continue

            current_indent = _compute_indent(stripped)
            if current_indent > indent_stack[-1]:
                indent_stack.append(current_indent)
                tokens.append(Token("INDENT", "", line_no, 1))
            else:
                while indent_stack[-1] > current_indent:
                    indent_stack.pop()
                    tokens.append(Token("DEDENT", "", line_no, 1))

            # Pomijamy wiodące spacje i tabulatory
            while pos < len(line_src) and line_src[pos] in " \t":
                col += 1
                pos += 1

        while pos < len(line_src):
            start_col = col

            # Komentarz
            if line_src[pos] == "#":
                tokens.append(Token("COMMENT", line_src[pos:], line_no, start_col))
                expected_named_token = None
                break

            # String / f-string
            if line_src[pos] in ('"', "'") or (
                line_src[pos].lower() in "frbu"
                and pos + 1 < len(line_src)
                and line_src[pos+1] in ('"', "'")
            ) or (
                pos + 2 < len(line_src) 
                and line_src[pos:pos+2].lower() in ("fr", "rf", "br", "rb") 
                and line_src[pos+2] in ('"', "'")
            ):
                value, pos, col = _scan_string(line_src, pos, col)
                # Sprawdzamy, czy w prefiksie znajduje się 'f' (np. 'f', 'fr', 'rf')
                key = "FSTRING" if value.lower().startswith(("f", "fr", "rf")) else "STRING"
                tokens.append(Token(key, value, line_no, start_col))
                expected_named_token = None

                delimiter = _get_triple_quote_delimiter(value)
                # Jeśli jest to potrójny string i nie został zamknięty, ustawiamy zmienne do śledzenia otwartego potrójnego stringa
                if delimiter is not None and _is_unclosed_triple_quoted_string(value, delimiter):
                    open_multiline_delimiter = delimiter
                    open_multiline_key = key
                continue

            # Liczba
            if line_src[pos].isdigit() or (line_src[pos] == "." and pos + 1 < len(line_src) and line_src[pos+1].isdigit()):
                key, value, pos, col = _scan_number(line_src, pos, col)
                tokens.append(Token(key, value, line_no, start_col))
                expected_named_token = None
                continue

            # Identyfikator lub słowo kluczowe
            if line_src[pos].isalpha() or line_src[pos] == "_":
                start = pos
                while pos < len(line_src) and (line_src[pos].isalnum() or line_src[pos] == "_"):
                    pos += 1
                    col += 1
                word = line_src[start:pos]
                # Obsługa f-stringów
                valid_prefixes = ("f", "r", "b", "u", "fr", "rf", "br", "rb")
                if word.lower() in valid_prefixes and pos < len(line_src) and line_src[pos] in ('"', "'"):
                    value, pos, col = _scan_string(line_src, start, col - len(word))
                    key = "FSTRING" if "f" in word.lower() else "STRING"
                    tokens.append(Token(key, value, line_no, start_col))
                    expected_named_token = None

                    delimiter = _get_triple_quote_delimiter(value)
                    if delimiter is not None and _is_unclosed_triple_quoted_string(value, delimiter):
                        open_multiline_delimiter = delimiter
                        open_multiline_key = key
                    continue
                
                if expected_named_token is not None:
                    key = expected_named_token
                    expected_named_token = None
                else:
                    key = "KEYWORD" if word in KEYWORDS else "ID"

                if key == "ID":
                    look = pos
                    while look < len(line_src) and line_src[look] in " \t":
                        look += 1
                    if look < len(line_src) and line_src[look] == "(":
                        key = "FUNC_CALL"

                tokens.append(Token(key, word, line_no, start_col))

                if key == "KEYWORD" and word == "def":
                    expected_named_token = "FUNC_NAME"
                elif key == "KEYWORD" and word == "class":
                    expected_named_token = "CLASS_NAME"
                continue

            # Pomijamy spacje i tabulatory między tokenami
            if line_src[pos] in " \t":
                while pos < len(line_src) and line_src[pos] in " \t":
                    pos += 1
                    col += 1
                continue

            # Operatory wieloznakowe - w MULTI_CHAR_OPERATORS klucze są posortowane od najdłuższych do najkrótszych -> pierwsze dopasowanie będzie najdłuższym możliwym operatorem
            matched = False
            for op in MULTI_CHAR_OPERATORS:
                if line_src[pos:pos+len(op)] == op:
                    tokens.append(Token(MULTI_CHAR_OPERATORS[op], op, line_no, start_col))
                    col += len(op)
                    pos += len(op)
                    matched = True
                    expected_named_token = None
                    break
            if matched:
                continue

            # Operatory jednoznakowe 
            ch = line_src[pos]
            if ch in SINGLE_CHAR_OPERATORS:
                tokens.append(Token(SINGLE_CHAR_OPERATORS[ch], ch, line_no, start_col))
                pos += 1
                col += 1
                if ch != ":":
                    expected_named_token = None
                continue

            # \ na końcu linii może oznaczać kontynuację linii, ale po nim nic już nie może być (poza komentarzem) 
            if ch == "\\" and pos + 1 == len(line_src):
                tokens.append(Token("CONTINUATION", ch, line_no, start_col))
                pos += 1
                col += 1
                expected_named_token = None
                continue

            # Nieznany znak - emitujemy token ERROR i przechodzimy dalej
            tokens.append(Token("ERROR", ch, line_no, start_col))
            pos += 1
            col += 1
            expected_named_token = None

        tokens.append(Token("NEWLINE", "\\n", line_no, col))
        expected_named_token = None

    # Po przetworzeniu wszystkich linii, jeśli nadal mamy jakieś poziomy wcięcia na stosie, emitujemy tokeny DEDENT aż do poziomu 0
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "", line_no, 1))

    tokens.append(Token("EOF", "", line_no, 1))
    return tokens