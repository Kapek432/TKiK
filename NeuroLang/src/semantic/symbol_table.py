"""Tabela symboli współdzielona przez analizę semantyczną."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class NetworkContext:
    """
    Przechowuje stan wymiarów pojedynczego bloku sieci.

    Argumenty:
        first_input_shape (Optional[tuple[int, ...]]): Wymiary wejścia
        last_output_shape (Any): Wymiary wyjścia
    """

    first_input_shape: Optional[tuple[int, ...]] = None
    last_output_shape: Any = None


@dataclass
class SymbolTable:
    """
    Agreguje tablice symboli wykorzystywane przy walidacji semantycznej.

    Argumenty:
        variables (dict[str, Any]): Tablica symboli
        defined_networks (set[str]): Zbiór nazw zdefiniowanych sieci
        defined_configs (set[str]): Zbiór nazw zdefiniowanych konfiguracji
        defined_data (set[str]): Zbiór nazw zdefiniowanych źródeł danych
        networks (dict[str, NetworkContext]): Mapowanie nazw sieci na konteksty
    """

    variables: dict[str, Any] = field(default_factory=dict)
    defined_networks: set[str] = field(default_factory=set)
    defined_configs: set[str] = field(default_factory=set)
    defined_data: set[str] = field(default_factory=set)
    networks: dict[str, NetworkContext] = field(default_factory=dict)

    def context_for(self, name: str) -> NetworkContext:
        """
        Pobiera lub tworzy kontekst sieci o podanej nazwie.

        Argumenty:
            name (str): Nazwa sieci

        Zwraca:
            NetworkContext: Kontekst sieci
        """
        if name not in self.networks:
            self.networks[name] = NetworkContext()
        return self.networks[name]
