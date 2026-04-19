"""Inicjalizacja parsera Lark dla gramatyki NeuroLang."""

from lark import Lark, Tree

from src.config import Config
from src.loaders import load_text_file


def build_parser(config: Config | None = None) -> Lark:
    """
    Tworzy parser Lark na podstawie gramatyki wczytanej z pliku.

    Argumenty:
        config (Config | None): Opcjonalna instancja konfiguracji

    Zwraca:
        Lark: Gotowy parser LALR(1)
    """
    cfg = config or Config.load()
    grammar = load_text_file(cfg.resource(cfg.paths.grammar_file))
    return Lark(grammar, start="start", parser="lalr", propagate_positions=True)


def parse_source(source: str, config: Config | None = None) -> Tree:
    """
    Parsuje kod NeuroLang i zwraca drzewo AST.

    Argumenty:
        source (str): Kod źródłowy NeuroLang
        config (Config | None): Konfiguracja do zbudowania parsera

    Zwraca:
        Tree: Drzewo AST
    """
    parser = build_parser(config)
    return parser.parse(source)
