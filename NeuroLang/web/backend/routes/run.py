"""Endpoint uruchamiania wygenerowanego kodu PyTorch."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.services.run_service import stream_run_from_source, stream_run_python
from web.backend.schemas import RunRequest

router = APIRouter(prefix="/api", tags=["run"])


@router.post("/run")
async def run_script(body: RunRequest) -> StreamingResponse:
    """
    Kompiluje (opcjonalnie) i uruchamia skrypt PyTorch.

    Argumenty:
        body (RunRequest): Kod Python lub źródło NeuroLang.

    Zwraca:
        StreamingResponse: strumień zdarzeń text/event-stream.
    """
    if body.python_code:
        generator = stream_run_python(
            body.python_code,
            timeout_sec=body.timeout_sec,
        )
    elif body.source:
        generator = stream_run_from_source(
            body.source,
            visualize=body.visualize,
            timeout_sec=body.timeout_sec,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Podaj python_code lub source.",
        )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
