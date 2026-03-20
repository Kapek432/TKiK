import sys
from scanner import scan
from css_class import CSS_CLASS
from html_template import HTML_TEMPLATE


def escape(text: str) -> str:
    """
    Zastępuje specjalne znaki HTML ich bezpiecznymi odpowiednikami, aby uniknąć problemów z interpretacją HTML.
    Dzięki temu można bezpiecznie wstawić dowolny tekst do HTML, nawet jeśli zawiera on znaki takie jak <, > czy &.
    Argumenty:
        text (str): Tekst do przetworzenia
    Zwraca:
        str: Tekst z zastąpionymi znakami
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def highlight(src: str) -> str:
    """
    Tworzy podświetlony HTML z podanego źródła Pythona. 
    Używa skanera do tokenizacji źródła, a następnie generuje HTML.
    Argumenty:
        src (str): Źródłowy kod Pythona do podświetlenia
    Zwraca:
        str: Podświetlony HTML
    """
    tokens = scan(src)
    parts = []
    cursor = 0

    for token in tokens:
        # Pomijamy tokeny, które nie mają wartości lub są związane z formatowaniem (INDENT, DEDENT, NEWLINE, EOF)
        if token.key in ("EOF", "INDENT", "DEDENT", "NEWLINE"):
            continue
        if not token.value:
            continue

        tok_start = src.index(token.value, cursor)

        # Dodajemy nieprzetworzony tekst między poprzednim tokenem a obecnym tokenem aby zachować oryginalne formatowanie i spacje
        parts.append(escape(src[cursor:tok_start]))

        # Pobieramy klasę CSS dla danego tokenu i generujemy odpowiedni fragment HTML
        css = CSS_CLASS.get(token.key, "")
        raw = escape(token.value)
        parts.append(f'<span class="{css}">{raw}</span>' if css else raw)

        # Aktualizujemy kursor do końca obecnego tokenu
        cursor = tok_start + len(token.value)

    parts.append(escape(src[cursor:]))
    return HTML_TEMPLATE.format(content="".join(parts))


def main() -> None:
    """
    Punkt wejścia programu. Oczekuje dwóch argumentów: ścieżki do pliku źródłowego i ścieżki do pliku docelowego HTML. 
    Wczytuje zawartość pliku źródłowego, generuje podświetlony HTML i zapisuje go do pliku docelowego.
    Przykładowe użycie: 
        `python highlighter.py input.py output.html`
    """
    if len(sys.argv) != 3:
        print("Użycie: python highlighter.py <input.py> <output.html>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        src = f.read()

    html = highlight(src)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Pomyślnie wygenerowano plik {output_path} z podświetleniem składni")


if __name__ == "__main__":
    main()