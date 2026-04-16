"""
Funkcje pomocnicze do wczytywania plików tekstowych i JSON.
"""

import json
import os


def load_text_file(filepath: str) -> str:
    """
    Wczytuje plik tekstowy.
    Jeśli plik nie istnieje, zgłasza FileNotFoundError.

    Argumenty:
        - filepath (str): Ścieżka do pliku tekstowego.

    Zwraca:
        - str: Zawartość pliku tekstowego.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r") as f:
        return f.read()


def load_json_file(filepath: str) -> dict:
    """
    Wczytuje plik JSON.
    Jeśli plik nie istnieje, zgłasza FileNotFoundError.

    Argumenty:
        - filepath (str): Ścieżka do pliku JSON.

    Zwraca:
        - dict: Zawartość pliku JSON jako słownik.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r") as f:
        return json.load(f)
