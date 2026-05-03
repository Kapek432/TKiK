"""Narzędzia pomocnicze dla generatora kodu PyTorch."""

from typing import Any


def format_value(value: Any) -> str:
    """
    Formatuje dowolną wartość do zapisu w generowanym kodzie Pythona.

    Argumenty:
        value (Any): Wartość do sformatowania

    Zwraca:
        str: Reprezentacja tekstowa wartości gotowa do wklejenia w kodzie
    """
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return repr(value)
    if value is None:
        return "None"
    return str(value)


def quote_string(value: str) -> str:
    """
    Zapewnia poprawny literał napisowy w generowanym kodzie.

    Argumenty:
        value (str): Wartość do opakowania

    Zwraca:
        str: Opakowana wartość
    """
    return repr(value)


class CodeBuffer:
    """
    Bufor linii kodu z obsługą wcięć (4 spacje na poziom).
    """

    def __init__(self) -> None:
        """
        Tworzy bufor linii kodu.

        Argumenty:
            lines (list[str]): Lista linii kodu
        """
        self.lines: list[str] = []

    def add(self, line: str, indent: int = 0) -> None:
        """
        Dodaje linię z odpowiednim wcięciem.

        Argumenty:
            line (str): Linia kodu
            indent (int): Poziom wcięcia
        """
        self.lines.append("    " * indent + line)

    def render(self) -> str:
        """
        Zwraca cały kod jako jeden tekst.

        Zwraca:
            str: Cały kod jako jeden tekst
        """
        return "\n".join(self.lines)
