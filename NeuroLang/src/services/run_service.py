"""Uruchamianie wygenerowanych skryptów PyTorch (Studio / API)."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Optional

from src.config import Config
from src.services.compiler_service import compile_source

DEFAULT_RUN_TIMEOUT_SEC = 600


def _project_root(config: Config) -> Path:
    """
    Zwraca katalog główny projektu NeuroLang.

    Argumenty:
        config (Config): Konfiguracja projektu.

    Zwraca:
        Path: Ścieżka do korzenia repozytorium.
    """
    return Path(config.resource("."))


async def _stream_process_output(
    proc: asyncio.subprocess.Process,
    timeout_sec: int,
) -> AsyncIterator[str]:
    """
    Emituje linie stdout/stderr procesu jako zdarzenia SSE (JSON).

    Argumenty:
        proc (asyncio.subprocess.Process): Uruchomiony proces.
        timeout_sec (int): Limit czasu w sekundach.

    Yields:
        str: Fragmenty SSE (data: {...}\\n\\n).
    """
    assert proc.stdout is not None

    async def read_lines() -> AsyncIterator[str]:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").rstrip("\n\r")
            payload = json.dumps({"type": "log", "line": text}, ensure_ascii=False)
            yield f"data: {payload}\n\n"

    try:
        async with asyncio.timeout(timeout_sec):
            async for event in read_lines():
                yield event
            await proc.wait()
    except TimeoutError:
        proc.kill()
        await proc.wait()
        payload = json.dumps(
            {"type": "error", "message": f"Przekroczono limit czasu ({timeout_sec}s)."},
            ensure_ascii=False,
        )
        yield f"data: {payload}\n\n"
        return

    exit_code = proc.returncode if proc.returncode is not None else -1
    done_payload = json.dumps(
        {"type": "done", "exit_code": exit_code, "success": exit_code == 0},
        ensure_ascii=False,
    )
    yield f"data: {done_payload}\n\n"


async def stream_run_python(
    python_code: str,
    *,
    config: Optional[Config] = None,
    timeout_sec: int = DEFAULT_RUN_TIMEOUT_SEC,
) -> AsyncIterator[str]:
    """
    Zapisuje kod do pliku tymczasowego i uruchamia go w katalogu projektu.

    Argumenty:
        python_code (str): Wygenerowany skrypt Python.
        config (Optional[Config]): Konfiguracja projektu.
        timeout_sec (int): Maksymalny czas wykonania.

    Yields:
        str: Zdarzenia SSE w trakcie i po zakończeniu procesu.
    """
    cfg = config or Config.load()
    root = _project_root(cfg)
    run_dir = root / "output" / "studio_run"
    run_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        prefix="studio_run_",
        dir=str(run_dir),
        delete=False,
        encoding="utf-8",
    ) as handle:
        handle.write(python_code)
        script_path = handle.name

    start_payload = json.dumps(
        {"type": "start", "script": os.path.basename(script_path)},
        ensure_ascii=False,
    )
    yield f"data: {start_payload}\n\n"

    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-u",
        script_path,
        cwd=str(root),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    async for event in _stream_process_output(proc, timeout_sec):
        yield event


async def stream_run_from_source(
    source: str,
    *,
    visualize: bool = False,
    config: Optional[Config] = None,
    timeout_sec: int = DEFAULT_RUN_TIMEOUT_SEC,
) -> AsyncIterator[str]:
    """
    Kompiluje NeuroLang i uruchamia wygenerowany skrypt.

    Argumenty:
        source (str): Kod źródłowy NeuroLang.
        visualize (bool): Czy kompilować z wizualizacją grafu.
        config (Optional[Config]): Konfiguracja projektu.
        timeout_sec (int): Maksymalny czas wykonania skryptu.

    Yields:
        str: Zdarzenia SSE (błąd kompilacji lub logi procesu).
    """
    cfg = config or Config.load()
    result = compile_source(source, visualize=visualize, config=cfg)
    if not result.success or not result.python_code:
        err_payload = json.dumps(
            {
                "type": "error",
                "message": result.message or "Kompilacja nie powiodła się.",
            },
            ensure_ascii=False,
        )
        yield f"data: {err_payload}\n\n"
        return

    async for event in stream_run_python(
        result.python_code,
        config=cfg,
        timeout_sec=timeout_sec,
    ):
        yield event
