"""Endpointy listy i wczytywania przykładów .nl."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.config import Config
from src.loaders import load_json_file, load_text_file
from web.backend.schemas import (
    ExampleContentResponse,
    ExampleInfo,
    ExamplesListResponse,
)

router = APIRouter(prefix="/api", tags=["examples"])


def _load_catalog() -> dict:
    """
    Wczytuje metadane galerii przykładów z catalog.json.

    Zwraca:
        dict: Mapowanie nazwa_pliku -> {title, description, tags}.
    """
    config = Config.load()
    catalog_path = config.resource("examples/catalog.json")
    if not Path(catalog_path).is_file():
        return {}
    return load_json_file(catalog_path)


def _examples_dir() -> Path:
    """
    Zwraca ścieżkę do katalogu examples/.

    Zwraca:
        Path: Katalog z plikami .nl.
    """
    config = Config.load()
    return Path(config.resource("examples"))


@router.get("/examples", response_model=ExamplesListResponse)
def list_examples() -> ExamplesListResponse:
    """
    Listuje pliki przykładów NeuroLang.

    Zwraca:
        ExamplesListResponse: Lista plików z kategorią valid/error.
    """
    examples_path = _examples_dir()
    if not examples_path.is_dir():
        raise HTTPException(status_code=404, detail="examples/ directory not found")

    catalog = _load_catalog()
    items: list[ExampleInfo] = []
    for entry in sorted(examples_path.glob("*.nl")):
        name = entry.name
        category = "error" if name.startswith("err_") else "valid"
        meta = catalog.get(name, {})
        items.append(
            ExampleInfo(
                filename=name,
                category=category,
                title=meta.get("title"),
                description=meta.get("description"),
                tags=meta.get("tags", []),
            )
        )

    return ExamplesListResponse(examples=items)


@router.get("/examples/{filename}", response_model=ExampleContentResponse)
def get_example(filename: str) -> ExampleContentResponse:
    """
    Zwraca treść pliku przykładu.

    Argumenty:
        filename (str): Nazwa pliku .nl.

    Zwraca:
        ExampleContentResponse: Treść pliku.

    Raises:
        HTTPException: Gdy plik nie istnieje lub nazwa jest niebezpieczna.
    """
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = _examples_dir() / filename
    if not path.is_file() or path.suffix != ".nl":
        raise HTTPException(status_code=404, detail=f"Example not found: {filename}")

    content = load_text_file(str(path))
    return ExampleContentResponse(filename=filename, content=content)
