"""Endpointy metadanych komponentów i datasetów."""

from fastapi import APIRouter

from src.config import Config
from src.loaders import load_json_file
from web.backend.schemas import MetadataResponse

router = APIRouter(prefix="/api/metadata", tags=["metadata"])


@router.get("/components", response_model=MetadataResponse)
def list_components() -> MetadataResponse:
    """
    Zwraca nazwy komponentów z components.json.

    Zwraca:
        MetadataResponse: Lista nazw warstw, optimizerów itd.
    """
    config = Config.load()
    data = load_json_file(config.resource(config.paths.components_file))
    return MetadataResponse(items=sorted(data.keys()))


@router.get("/datasets", response_model=MetadataResponse)
def list_datasets() -> MetadataResponse:
    """
    Zwraca nazwy wbudowanych datasetów z datasets.json.

    Zwraca:
        MetadataResponse: Lista nazw datasetów.
    """
    config = Config.load()
    data = load_json_file(config.resource(config.paths.datasets_file))
    return MetadataResponse(items=sorted(data.keys()))
