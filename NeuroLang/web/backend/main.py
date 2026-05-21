"""Aplikacja FastAPI dla NeuroLang Studio."""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from web.backend.routes import compile, examples, metadata, run
from web.backend.schemas import HealthResponse, UploadResponse

app = FastAPI(
    title="NeuroLang Studio API",
    description="REST API dla kompilatora NeuroLang",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compile.router)
app.include_router(examples.router)
app.include_router(metadata.router)
app.include_router(run.router)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Sprawdza dostępność API.

    Zwraca:
        HealthResponse: Status i wersja.
    """
    return HealthResponse(status="ok", version="0.1.0")


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    """
    Wczytuje plik .nl przesłany z przeglądarki.

    Argumenty:
        file (UploadFile): Plik .nl.

    Zwraca:
        UploadResponse: Nazwa i treść pliku.
    """
    if not file.filename or not file.filename.endswith(".nl"):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Only .nl files are accepted")

    raw = await file.read()
    content = raw.decode("utf-8")
    return UploadResponse(filename=file.filename, content=content)


def run() -> None:
    """Uruchamia serwer uvicorn (entry point neurolang-web)."""
    import uvicorn

    uvicorn.run(
        "web.backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
