"""Wyświetlanie sformatowanego drzewa AST dla kodu NeuroLang."""

import argparse

from lark.exceptions import UnexpectedInput

from src import logger as log_setup
from src.config import Config
from src.loaders import load_text_file
from src.parser.grammar import build_parser


def _build_arg_parser(config: Config) -> argparse.ArgumentParser:
    """
    Buduje parser argumentów CLI na podstawie wartości z konfiguracji.

    Argumenty:
        config (Config): Konfiguracja projektu

    Zwraca:
        argparse.ArgumentParser: Parser argumentów CLI
    """
    parser = argparse.ArgumentParser(description="Display AST for a NeuroLang source file.")
    parser.add_argument(
        "-i",
        "--input",
        default=config.paths.default_input,
        help="NeuroLang input file (.nl)",
    )
    return parser


def main() -> None:
    """
    Ładuje źródło, parsuje je i drukuje drzewo AST.
    """
    config = Config.load()
    log_setup.setup(level=str(config.logging.get("level", "INFO")))
    logger = log_setup.get_logger("neurolang.cli.show_ast")

    args = _build_arg_parser(config).parse_args()
    logger.info("Initializing NeuroLang compiler...")

    try:
        parser = build_parser(config)
        logger.info("Grammar loaded successfully.")
    except Exception as exc:
        logger.error(f"{exc}")
        return

    try:
        source_code = load_text_file(args.input)
        logger.info(f"Source code '{args.input}' loaded successfully.")
    except Exception as exc:
        logger.error(f"{exc}")
        return

    logger.info("Building syntax tree...")
    try:
        ast_tree = parser.parse(source_code)
    except UnexpectedInput as exc:
        logger.error(f"SYNTAX ERROR at line {exc.line}, column {exc.column}")
        logger.error(f"{exc.get_context(source_code)}")
        logger.error(f"Expected one of: {exc.expected}")
        return

    logger.info("Syntax tree built successfully.")
    logger.info("Generated Syntax Tree:")
    logger.info("--------------------------------")
    logger.info(f"{ast_tree.pretty()}")
    logger.info("--------------------------------")


if __name__ == "__main__":
    main()
