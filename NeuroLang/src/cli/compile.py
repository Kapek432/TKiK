"""Punkt wejścia CLI dla kompilatora NeuroLang."""

import argparse
import os
import subprocess
import sys

from src import logger as log_setup
from src.config import Config
from src.loaders import load_text_file
from src.services.compiler_service import compile_source


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

    if not os.path.exists(args.input):
        logger.error(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    try:
        source_code = load_text_file(args.input)
    except Exception as exc:
        logger.error(f"INITIALIZATION ERROR: {exc}")
        sys.exit(1)

    logger.info("Parsing...")
    result = compile_source(source_code, visualize=args.visualize, config=config)

    if not result.success:
        logger.error(result.message)
        if result.context:
            logger.error("%s", result.context)
        sys.exit(1)

    logger.info("Code generation...")
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(result.python_code or "")

    logger.info(f"Success! Generated: {args.output}")

    if args.run:
        logger.info(f"Running: {args.output}")
        run_result = subprocess.run([sys.executable, args.output])
        if run_result.returncode != 0:
            logger.error(f"Script finished with error (code: {run_result.returncode})")
        else:
            logger.info("Execution finished successfully.")


if __name__ == "__main__":
    main()
