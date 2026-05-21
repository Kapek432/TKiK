"""Wyświetlanie sformatowanego drzewa AST dla kodu NeuroLang."""

import argparse
import os
import sys

from src import logger as log_setup
from src.config import Config
from src.loaders import load_text_file
from src.services.compiler_service import parse_ast


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

    if not os.path.exists(args.input):
        logger.error(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    try:
        source_code = load_text_file(args.input)
        logger.info(f"Source code '{args.input}' loaded successfully.")
    except Exception as exc:
        logger.error(f"{exc}")
        sys.exit(1)

    logger.info("Building syntax tree...")
    result = parse_ast(source_code, config=config)

    if not result.success:
        logger.error(result.message)
        if result.context:
            logger.error(f"{result.context}")
        sys.exit(1)

    logger.info("Syntax tree built successfully.")
    logger.info("Generated Syntax Tree:")
    logger.info("--------------------------------")
    logger.info(f"{result.ast_pretty}")
    logger.info("--------------------------------")


if __name__ == "__main__":
    main()
