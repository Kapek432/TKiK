import sys
from scanner import scan


def print_tokens(file_path: str) -> None:
    """
    Skanuje plik i wypisuje tokeny do stdout w formacie tekstowym.
    Argumenty:
        file_path (str): Ścieżka do pliku do skanowania
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            src = f.read()
        
        tokens = scan(src)
        
        # Wypisujemy nagłówek tabeli i tokeny w czytelnej formie
        print(f"\n{'Lp.':<4} {'Typ':<15} {'Wartość':<50} {'Linia':<6} {'Kolumna':<6}")
        print("=" * 86)
        
        for idx, token in enumerate(tokens, 1):
            value_display = token.value.replace('\n', '\\n')[:45] + ('...' if len(token.value) > 45 else '')
            print(f"{idx:<4} {token.key:<15} {value_display:<50} {token.line:<6} {token.column:<6}")
        
        print(f"\nŁącznie tokenów: {len(tokens)}")
    
    except FileNotFoundError:
        print(f"Błąd: Plik nie znaleziony: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Błąd: {e}")
        sys.exit(1)


if __name__ == '__main__':
    """
    Punkt wejścia programu. Oczekuje jednego argumentu: ścieżki do pliku źródłowego.
    Przykładowe użycie:
        `python3 token_printer.py highlighter.py`
    """
    if len(sys.argv) < 2:
        print("Użycie: python3 token_printer.py <plik>")
        sys.exit(1)
    
    print_tokens(sys.argv[1])