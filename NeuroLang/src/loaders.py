"""Funkcje pomocnicze do wczytywania plików tekstowych i JSON."""

import json
import os


def load_text_file(filepath: str) -> str:
    """
    Wczytuje plik tekstowy w kodowaniu UTF-8.

    Argumenty:
        filepath (str): Ścieżka do pliku tekstowego

    Zwraca:
        str: Zawartość pliku

    Raises:
        FileNotFoundError: Gdy plik nie istnieje
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as handle:
        return handle.read()


def load_json_file(filepath: str) -> dict:
    """
    Wczytuje plik JSON i zwraca słownik.

    Argumenty:
        filepath (str): Ścieżka do pliku JSON

    Zwraca:
        dict: Struktura załadowana z pliku

    Raises:
        FileNotFoundError: Gdy plik nie istnieje.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as handle:
        return json.load(handle)
