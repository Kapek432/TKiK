"""Modele Pydantic dla API webowego NeuroLang."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class CompileRequest(BaseModel):
    """Żądanie kompilacji kodu NeuroLang."""

    source: str = Field(..., description="Kod źródłowy NeuroLang")
    visualize: bool = Field(default=False, description="Dołącz wizualizację architektury")


class AstRequest(BaseModel):
    """Żądanie parsowania drzewa AST."""

    source: str = Field(..., description="Kod źródłowy NeuroLang")


class CompileResponse(BaseModel):
    """Odpowiedź kompilatora (JSON)."""

    success: bool
    python_code: Optional[str] = None
    ast_pretty: Optional[str] = None
    error_type: Optional[Literal["syntax", "semantic", "io", "unknown"]] = None
    message: str = ""
    line: Optional[int] = None
    column: Optional[int] = None
    context: Optional[str] = None
    graph_image_base64: Optional[str] = None
    graph_message: Optional[str] = None


class ExampleInfo(BaseModel):
    """Metadane pliku przykładu."""

    filename: str
    category: Literal["valid", "error"]
    title: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class ExamplesListResponse(BaseModel):
    """Lista przykładów NeuroLang."""

    examples: list[ExampleInfo]


class ExampleContentResponse(BaseModel):
    """Treść pliku przykładu."""

    filename: str
    content: str


class MetadataResponse(BaseModel):
    """Lista nazw komponentów lub datasetów."""

    items: list[str]


class HealthResponse(BaseModel):
    """Status serwera API."""

    status: str
    version: str


class UploadResponse(BaseModel):
    """Odpowiedź po wczytaniu pliku .nl."""

    filename: str
    content: str


class RunRequest(BaseModel):
    """Żądanie uruchomienia wygenerowanego skryptu."""

    source: Optional[str] = Field(
        default=None,
        description="Kod NeuroLang - skompiluj i uruchom",
    )
    python_code: Optional[str] = Field(
        default=None,
        description="Gotowy skrypt Python do uruchomienia",
    )
    visualize: bool = Field(
        default=False,
        description="Przy kompilacji z source: dołącz wizualizację",
    )
    timeout_sec: int = Field(
        default=600,
        ge=30,
        le=3600,
        description="Maksymalny czas wykonania w sekundach",
    )
