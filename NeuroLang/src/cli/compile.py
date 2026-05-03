"""Punkt wejścia CLI dla kompilatora NeuroLang."""

import argparse
import os
import subprocess
import sys

from lark.exceptions import UnexpectedInput, VisitError

from src import logger as log_setup
from src.config import Config
from src.codegen.generator import PyTorchGenerator
from src.loaders import load_text_file
from src.parser.grammar import build_parser
from src.semantic.transformer import NeuroLangCompiler
from src.semantic.visitor import NeuroLangVisitor


def _build_arg_parser(config: Config) -> argparse.ArgumentParser:
    """
    Buduje parser argumentów CLI na podstawie wartości z konfiguracji.

    Argumenty:
        config (Config): Konfiguracja projektu

    Zwraca:
        argparse.ArgumentParser: Parser argumentów CLI
    """
    parser = argparse.ArgumentParser(description="NeuroLang to PyTorch compiler.")
    parser.add_argument(
        "-i",
        "--input",
        default=config.paths.default_input,
        help="NeuroLang input file (.nl)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=config.paths.default_output,
        help="Python output file (.py)",
    )
    parser.add_argument(
        "-r",
        "--run",
        action="store_true",
        help="Run generated script after compilation",
    )
    parser.add_argument(
        "-v",
        "--visualize",
        action="store_true",
        help=f"Generate architecture visualization ({config.paths.model_graph_file})",
    )
    return parser


def _extract_semantic_message(error_msg: str) -> str:
    """
    Wyciąga komunikat semantyczny z owinietego wyjątku.

    Argumenty:
        error_msg (str): Komunikat błędu semantycznego

    Zwraca:
        str: Komunikat semantyczny
    """
    if "SEMANTIC ERROR" in error_msg or "BLAD SEMANTYCZNY" in error_msg:
        return error_msg.split("\n")[-1] if "\n" in error_msg else error_msg
    return error_msg


def main() -> None:
    """
    Przeprowadza proces kompilacji: parser -> visitor -> transformer -> generator.
    """
    config = Config.load()
    log_setup.setup(
        level=str(config.logging.get("level", "INFO")),
        fmt=str(config.logging.get("format", "%(message)s")),
    )
    logger = log_setup.get_logger("neurolang.cli")

    args = _build_arg_parser(config).parse_args()
    logger.info(f"Compiling NeuroLang: {args.input}")

    try:
        parser = build_parser(config)
        if not os.path.exists(args.input):
            logger.error(f"ERROR: Input file not found: {args.input}")
            sys.exit(1)
        source_code = load_text_file(args.input)
    except Exception as exc:
        logger.error(f"INITIALIZATION ERROR: {exc}")
        sys.exit(1)

    logger.info("Parsing...")
    try:
        ast_tree = parser.parse(source_code)
    except UnexpectedInput as exc:
        logger.error(f"SYNTAX ERROR: Line {exc.line}, Column {exc.column}")
        if hasattr(exc, "get_context"):
            logger.error("%s", exc.get_context(source_code))
        sys.exit(1)

    logger.info("Semantic analysis...")
    compiler = NeuroLangCompiler(config=config)
    visitor = NeuroLangVisitor(compiler)
    visitor.visit(ast_tree)

    try:
        compiler.transform(ast_tree)
    except (VisitError, ValueError) as exc:
        logger.error(f"{_extract_semantic_message(str(exc))}")
        sys.exit(1)
    except Exception as exc:
        logger.error(f"UNEXPECTED ERROR: {exc}")
        sys.exit(1)

    logger.info("Code generation...")
    generator = PyTorchGenerator(
        parsed_config=compiler.parsed_config,
        components=compiler.components,
        visualize=args.visualize,
        config=config,
    )
    python_code = generator.generate()

    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(python_code)

    logger.info(f"Success! Generated: {args.output}")

    if args.run:
        logger.info(f"Running: {args.output}")
        result = subprocess.run([sys.executable, args.output])
        if result.returncode != 0:
            logger.error(f"Script finished with error (code: {result.returncode})")
        else:
            logger.info("Execution finished successfully.")


if __name__ == "__main__":
    main()
