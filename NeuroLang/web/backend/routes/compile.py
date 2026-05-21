"""Endpointy kompilacji i AST."""

from fastapi import APIRouter

from src.services.compiler_service import compile_source, parse_ast
from web.backend.schemas import AstRequest, CompileRequest, CompileResponse

router = APIRouter(prefix="/api", tags=["compile"])


def _to_response(result) -> CompileResponse:
    """
    Mapuje CompileResult na model odpowiedzi API.

    Argumenty:
        result: Wynik z compiler_service.

    Zwraca:
        CompileResponse: Odpowiedź JSON.
    """
    return CompileResponse(
        success=result.success,
        python_code=result.python_code,
        ast_pretty=result.ast_pretty,
        error_type=result.error_type,
        message=result.message,
        line=result.line,
        column=result.column,
        context=result.context,
        graph_image_base64=result.graph_image_base64,
        graph_message=result.graph_message,
    )


@router.post("/compile", response_model=CompileResponse)
def compile_endpoint(body: CompileRequest) -> CompileResponse:
    """
    Kompiluje kod NeuroLang do Pythona.

    Argumenty:
        body (CompileRequest): Kod źródłowy i opcje.

    Zwraca:
        CompileResponse: Wynik kompilacji.
    """
    result = compile_source(
        body.source,
        visualize=body.visualize,
        render_graph=body.visualize,
    )
    return _to_response(result)


@router.post("/ast", response_model=CompileResponse)
def ast_endpoint(body: AstRequest) -> CompileResponse:
    """
    Parsuje kod NeuroLang i zwraca drzewo AST.

    Argumenty:
        body (AstRequest): Kod źródłowy.

    Zwraca:
        CompileResponse: Wynik z ast_pretty lub błędem.
    """
    result = parse_ast(body.source)
    return _to_response(result)
