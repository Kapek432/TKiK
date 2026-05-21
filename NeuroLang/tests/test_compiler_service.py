"""Testy warstwy serwisowej kompilatora."""

from pathlib import Path

import pytest

from src.config import Config
from src.loaders import load_text_file
from src.services.compiler_service import compile_source, parse_ast

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture
def config() -> Config:
    """Ładuje konfigurację projektu."""
    return Config.load()


def test_compile_source_success_mnist(config: Config) -> None:
    """Kompilacja poprawnego przykładu MNIST zwraca kod Python."""
    source = load_text_file(str(EXAMPLES_DIR / "01_mnist_basic.nl"))
    result = compile_source(source, config=config)

    assert result.success is True
    assert result.python_code is not None
    assert len(result.python_code) > 0
    assert "import torch" in result.python_code
    assert result.error_type is None


def test_compile_source_semantic_error(config: Config) -> None:
    """Kompilacja błędnego przykładu zwraca błąd semantyczny."""
    source = load_text_file(str(EXAMPLES_DIR / "err_dense_mismatch.nl"))
    result = compile_source(source, config=config)

    assert result.success is False
    assert result.error_type == "semantic"
    assert result.python_code is None
    assert result.message


def test_parse_ast_success(config: Config) -> None:
    """Parsowanie poprawnego źródła zwraca drzewo AST."""
    source = load_text_file(str(EXAMPLES_DIR / "01_mnist_basic.nl"))
    result = parse_ast(source, config=config)

    assert result.success is True
    assert result.ast_pretty is not None
    assert "network_block" in result.ast_pretty or "network" in result.ast_pretty.lower()


def test_parse_ast_syntax_error() -> None:
    """Niepoprawna składnia zwraca błąd syntax z numerem linii."""
    source = "network Broken { layer: }"
    result = parse_ast(source)

    assert result.success is False
    assert result.error_type == "syntax"
    assert result.line is not None
