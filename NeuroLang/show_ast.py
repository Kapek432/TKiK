"""
Plik do wyświetlania Drzewa Składniowego (AST) dla kodu źródłowego napisanego w języku NeuroLang.
"""

from lark import Lark
from lark.exceptions import UnexpectedInput

from constants import AST_SEPARATOR, ERROR_SEPARATOR, GRAMMAR_FILE, SOURCE_FILE_EXAMPLE
from loaders import load_text_file


def main():
    """
    Główna funkcja skryptu show_ast.
    Wczytuje gramatykę i kod źródłowy, a następnie wyświetla sformatowane drzewo AST w konsoli.
    """
    print("Inicjalizacja kompilatora NeuroLang...")

    # Wczytanie gramatyki za pomocą loadera
    try:
        grammar = load_text_file(GRAMMAR_FILE)
        # Tworzymy parser używając algorytmu LALR
        nl_parser = Lark(grammar, start="start", parser="lalr")
        print(f"Gramatyka '{GRAMMAR_FILE}' wczytana pomyślnie.")
    except Exception as e:
        print(e)
        return

    # Wczytanie kodu źródłowego w formacie .nl
    try:
        source_code = load_text_file(SOURCE_FILE_EXAMPLE)
        print(f"Kod źródłowy '{SOURCE_FILE_EXAMPLE}' wczytany.")
    except Exception as e:
        print(e)
        return

    # Parsowanie kodu do Drzewa Składniowego (AST)
    print("Budowanie drzewa składniowego (AST)...")
    try:
        ast_tree = nl_parser.parse(source_code)
        print("Kod sparsowany bez błędów składniowych.\n")

        # Wyświetlamy sformatowane drzewo w konsoli
        print("Wygenerowane Drzewo Składniowe (AST):")
        print(AST_SEPARATOR)
        print(ast_tree.pretty())
        print(AST_SEPARATOR)

    except UnexpectedInput as e:
        # Przechwytywanie błędów składniowych zgłaszanych przez Larka
        print("BŁĄD SKŁADNIOWY:")
        print(f"Lokalizacja: Linia {e.line}, Kolumna {e.column}")
        print(ERROR_SEPARATOR)
        print(e.get_context(source_code))
        print(ERROR_SEPARATOR)
        print(f"Oczekiwano jednego z: {e.expected}")


if __name__ == "__main__":
    main()
