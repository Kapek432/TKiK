"""Tabela symboli współdzielona przez analizę semantyczną."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class NetworkContext:
    """
    Przechowuje stan wymiarów pojedynczego bloku sieci.

    Argumenty:
        name (str): Nazwa sieci
        first_input_shape (Optional[tuple[int, ...]]): Wymiary wejścia
        last_output_shape (Any): Wymiary wyjścia
    """

    name: str
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
    active_network: Optional[str] = None

    def context_for(self, name: str) -> NetworkContext:
        """
        Pobiera lub tworzy kontekst sieci o podanej nazwie.

        Argumenty:
            name (str): Nazwa sieci

        Zwraca:
            NetworkContext: Kontekst sieci
        """
        if name not in self.networks:
            self.networks[name] = NetworkContext(name=name)
        return self.networks[name]

    def enter_network(self, name: str) -> NetworkContext:
        """
        Ustawia aktywny kontekst sieci i zwraca go.

        Argumenty:
            name (str): Nazwa sieci

        Zwraca:
            NetworkContext: Kontekst sieci
        """
        self.active_network = name
        return self.context_for(name)

    def leave_network(self) -> None:
        """
        Usuwa aktywny kontekst sieci.

        Argumenty:
            name (str): Nazwa sieci
        """
        self.active_network = None

    @property
    def active_context(self) -> Optional[NetworkContext]:
        """
        Zwraca kontekst aktualnie przetwarzanej sieci, jeśli istnieje.

        Zwraca:
            Optional[NetworkContext]: Kontekst aktualnie przetwarzanej sieci
        """
        if self.active_network is None:
            return None
        return self.networks.get(self.active_network)
