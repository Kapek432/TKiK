"""Wspólne fixture pytest dla testów."""

import pytest
from lark import Lark

from src.config import Config
from src.parser.grammar import build_parser
from src.semantic.transformer import NeuroLangCompiler


@pytest.fixture
def config() -> Config:
    """
    Zwraca nową konfigurację projektu dla każdego testu.

    Zwraca:
        Config: Konfiguracja projektu
    """
    Config.reset()
    return Config.load()


@pytest.fixture
def parser(config: Config) -> Lark:
    """
    Zwraca parser Lark inicjalizowany jednorazowo na test.

    Argumenty:
        config (Config): Konfiguracja projektu

    Zwraca:
        Lark: Parser Lark
    """
    return build_parser(config)


@pytest.fixture
def compiler(config: Config) -> NeuroLangCompiler:
    """
    Zwraca nowy transformer semantyczny.

    Argumenty:
        config (Config): Konfiguracja projektu

    Zwraca:
        NeuroLangCompiler: Transformer semantyczny
    """
    return NeuroLangCompiler(config=config)
