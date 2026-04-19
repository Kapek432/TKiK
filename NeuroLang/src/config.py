"""Klasa konfiguracyjna ładująca stałe z config.yaml."""

from __future__ import annotations

import os
from typing import Any

import yaml


class _Section:
    """
    Opakowuje słownik udostępniając pola jako atrybuty.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        """
        Inicjalizuje sekcję.

        Argumenty:
            data (dict[str, Any]): Słownik z kluczami sekcji.
        """
        self._data = data

    def __getattr__(self, item: str) -> Any:
        """
        Pobiera wartość sekcji.

        Argumenty:
            item (str): Klucz sekcji

        Zwraca:
            Any: Wartość sekcji

        Raises:
            AttributeError: Gdy klucz sekcji nie istnieje
        """
        try:
            return self._data[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def get(self, key: str, default: Any = None) -> Any:
        """
        Pobiera wartość sekcji z opcjonalną wartością domyślną.

        Argumenty:
            key (str): Klucz sekcji
            default (Any): Wartość domyślna

        Zwraca:
            Any: Wartość sekcji

        Raises:
            KeyError: Gdy klucz sekcji nie istnieje.
        """
        return self._data.get(key, default)


class Config:
    """
    Ładowanie i dostęp do parametrów konfiguracyjnych projektu.

    Argumenty:
        path (str): Ścieżka do pliku config.yaml
    """

    _singleton: Config | None = None

    def __init__(self, path: str) -> None:
        """
        Inicjalizuje konfigurację.

        Argumenty:
            path (str): Ścieżka do pliku config.yaml
        """
        self._path = path
        self._project_root = os.path.dirname(os.path.abspath(path))
        with open(path, "r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)

        self.paths = _Section(raw.get("paths", {}))
        self.model = _Section(raw.get("model", {}))
        self.training = _Section(raw.get("training", {}))
        self.logging = _Section(raw.get("logging", {}))
        self.validation = _Section(raw.get("validation", {}))

    @property
    def project_root(self) -> str:
        """
        Zwraca katalog z plikiem konfiguracyjnym.

        Zwraca:
            str: Katalog z plikiem konfiguracyjnym
        """
        return self._project_root

    def resource(self, relative: str) -> str:
        """
        Zamienia ścieżkę względną do pliku konfiguracyjnego na absolutną.

        Argumenty:
            relative (str): Ścieżka względna do korzenia projektu

        Zwraca:
            str: Ścieżka absolutna
        """
        if os.path.isabs(relative):
            return relative
        return os.path.join(self._project_root, relative)

    @classmethod
    def load(cls, path: str | None = None) -> "Config":
        """
        Ładowanie singletona konfiguracji. Pierwsze wywołanie ustawia ścieżkę.

        Argumenty:
            path (str | None): Ścieżka do config.yaml; gdy None używany jest
                plik z korzenia projektu

        Zwraca:
            Config: Współdzielona instancja konfiguracji
        """
        if cls._singleton is None:
            resolved = path or cls._default_path()
            cls._singleton = cls(resolved)
        return cls._singleton

    @classmethod
    def reset(cls) -> None:
        """Czyści współdzieloną instancję - używane w testach."""
        cls._singleton = None

    @staticmethod
    def _default_path() -> str:
        """
        Lokalizuje config.yaml w korzeniu projektu względem pakietu.

        Zwraca:
            str: Ścieżka do config.yaml
        """
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(5):
            candidate = os.path.join(here, "config.yaml")
            if os.path.exists(candidate):
                return candidate
            parent = os.path.dirname(here)
            if parent == here:
                break
            here = parent
        raise FileNotFoundError("config.yaml not found in project tree")
