"""Wspólna logika kompilacji NeuroLang (CLI, API, testy)."""

from __future__ import annotations

import base64
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Any, Literal, Optional

from lark.exceptions import UnexpectedInput, VisitError

from src.codegen.generator import PyTorchGenerator
from src.config import Config
from src.parser.grammar import build_parser
from src.semantic.transformer import NeuroLangCompiler
from src.semantic.visitor import NeuroLangVisitor

ErrorType = Literal["syntax", "semantic", "io", "unknown"]


@dataclass
class CompileResult:
    """
    Wynik kompilacji lub parsowania NeuroLang.

    Atrybuty:
        success (bool): Czy operacja zakończyła się sukcesem.
        python_code (Optional[str]): Wygenerowany kod Python (przy kompilacji).
        ast_pretty (Optional[str]): Tekstowe drzewo AST.
        error_type (Optional[ErrorType]): Typ błędu.
        message (str): Komunikat lub podsumowanie.
        line (Optional[int]): Numer linii błędu.
        column (Optional[int]): Numer kolumny błędu.
        context (Optional[str]): Kontekst źródła wokół błędu.
        graph_image_base64 (Optional[str]): PNG grafu architektury (base64).
        graph_message (Optional[str]): Komunikat lub błąd generowania grafu.
    """

    success: bool
    python_code: Optional[str] = None
    ast_pretty: Optional[str] = None
    error_type: Optional[ErrorType] = None
    message: str = ""
    line: Optional[int] = None
    column: Optional[int] = None
    context: Optional[str] = None
    graph_image_base64: Optional[str] = None
    graph_message: Optional[str] = None


def _extract_semantic_message(error_msg: str) -> str:
    """
    Wyciąga komunikat semantyczny z owinietego wyjątku.

    Argumenty:
        error_msg (str): Komunikat błędu semantycznego.

    Zwraca:
        str: Uproszczony komunikat.
    """
    if "SEMANTIC ERROR" in error_msg or "BLAD SEMANTYCZNY" in error_msg:
        return error_msg.split("\n")[-1] if "\n" in error_msg else error_msg
    return error_msg


def _syntax_error_result(exc: UnexpectedInput, source: str) -> CompileResult:
    """
    Buduje CompileResult dla błędu składniowego.

    Argumenty:
        exc (UnexpectedInput): Wyjątek parsera Lark.
        source (str): Kod źródłowy NeuroLang.

    Zwraca:
        CompileResult: Wynik z informacją o błędzie składni.
    """
    context = exc.get_context(source) if hasattr(exc, "get_context") else None
    return CompileResult(
        success=False,
        error_type="syntax",
        message=f"SYNTAX ERROR: Line {exc.line}, Column {exc.column}",
        line=exc.line,
        column=exc.column,
        context=context,
    )


def parse_ast(source: str, *, config: Optional[Config] = None) -> CompileResult:
    """
    Parsuje kod NeuroLang i zwraca sformatowane drzewo AST.

    Argumenty:
        source (str): Kod źródłowy NeuroLang.
        config (Optional[Config]): Konfiguracja projektu.

    Zwraca:
        CompileResult: Wynik z ast_pretty lub informacją o błędzie.
    """
    cfg = config or Config.load()
    try:
        parser = build_parser(cfg)
        ast_tree = parser.parse(source)
    except UnexpectedInput as exc:
        return _syntax_error_result(exc, source)
    except Exception as exc:
        return CompileResult(
            success=False,
            error_type="unknown",
            message=f"UNEXPECTED ERROR: {exc}",
        )

    return CompileResult(
        success=True,
        ast_pretty=ast_tree.pretty(),
        message="Syntax tree built successfully.",
    )


def _run_graph_preview(
    parsed_config: dict[str, Any],
    components: dict[str, Any],
    config: Config,
    timeout: int = 90,
) -> tuple[Optional[str], Optional[str]]:
    """
    Generuje i uruchamia skrypt podglądu grafu (tylko model + torchview).

    Argumenty:
        parsed_config (dict[str, Any]): Konfiguracja po analizie semantycznej.
        components (dict[str, Any]): Mapowanie komponentów.
        config (Config): Konfiguracja projektu.
        timeout (int): Limit czasu uruchomienia w sekundach.

    Zwraca:
        tuple: (base64 PNG lub None, komunikat błędu lub None).
    """
    try:
        generator = PyTorchGenerator(
            parsed_config=parsed_config,
            components=components,
            visualize=True,
            config=config,
        )
        preview_code = generator.generate(graph_preview_only=True)
    except Exception as exc:
        return None, f"Graph preview codegen failed: {exc}"

    graph_file = str(config.paths.model_graph_file)
    graph_basename = str(config.paths.model_graph_basename)

    with tempfile.TemporaryDirectory(prefix="nl_graph_") as tmp:
        script_path = os.path.join(tmp, "preview_graph.py")
        with open(script_path, "w", encoding="utf-8") as handle:
            handle.write(preview_code)

        try:
            proc = subprocess.run(
                [sys.executable, script_path],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return None, f"Graph render timed out after {timeout}s."
        except Exception as exc:
            return None, f"Graph render failed: {exc}"

        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "unknown error").strip()
            return None, f"Graph script error: {detail[:600]}"

        candidates = [
            os.path.join(tmp, graph_file),
            os.path.join(tmp, f"{graph_basename}.png"),
            os.path.join(tmp, f"{graph_basename}.gv.png"),
        ]
        png_path = next((p for p in candidates if os.path.isfile(p)), None)
        if not png_path:
            return None, "Graph file was not created (check torchview installation)."

        with open(png_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode("ascii")
        return encoded, "Architecture graph generated."


def compile_source(
    source: str,
    *,
    visualize: bool = False,
    render_graph: bool = False,
    config: Optional[Config] = None,
) -> CompileResult:
    """
    Kompiluje kod NeuroLang do skryptu Python (PyTorch).

    Argumenty:
        source (str): Kod źródłowy NeuroLang.
        visualize (bool): Czy dołączyć kod wizualizacji architektury.
        render_graph (bool): Czy uruchomić podgląd grafu (wymaga visualize i sukcesu).
        config (Optional[Config]): Konfiguracja projektu.

    Zwraca:
        CompileResult: Wynik z python_code lub informacją o błędzie.
    """
    cfg = config or Config.load()

    try:
        parser = build_parser(cfg)
    except Exception as exc:
        return CompileResult(
            success=False,
            error_type="io",
            message=f"INITIALIZATION ERROR: {exc}",
        )

    try:
        ast_tree = parser.parse(source)
    except UnexpectedInput as exc:
        return _syntax_error_result(exc, source)

    ast_pretty = ast_tree.pretty()
    compiler = NeuroLangCompiler(config=cfg)
    visitor = NeuroLangVisitor(compiler)
    visitor.visit(ast_tree)

    try:
        compiler.transform(ast_tree)
    except (VisitError, ValueError) as exc:
        return CompileResult(
            success=False,
            ast_pretty=ast_pretty,
            error_type="semantic",
            message=_extract_semantic_message(str(exc)),
        )
    except Exception as exc:
        return CompileResult(
            success=False,
            ast_pretty=ast_pretty,
            error_type="unknown",
            message=f"UNEXPECTED ERROR: {exc}",
        )

    try:
        generator = PyTorchGenerator(
            parsed_config=compiler.parsed_config,
            components=compiler.components,
            visualize=visualize,
            config=cfg,
        )
        python_code = generator.generate()
    except Exception as exc:
        return CompileResult(
            success=False,
            ast_pretty=ast_pretty,
            error_type="unknown",
            message=f"CODE GENERATION ERROR: {exc}",
        )

    result = CompileResult(
        success=True,
        python_code=python_code,
        ast_pretty=ast_pretty,
        message="Compilation successful.",
    )

    if visualize and render_graph:
        graph_b64, graph_msg = _run_graph_preview(
            compiler.parsed_config,
            compiler.components,
            cfg,
        )
        result.graph_image_base64 = graph_b64
        result.graph_message = graph_msg

    return result
