"""Testy uruchamiania skryptów ze Studio."""

from __future__ import annotations

import asyncio
import json

from src.services.run_service import stream_run_python


def test_stream_run_python_prints_hello() -> None:
    """
    Uruchamia prosty skrypt i sprawdza zdarzenia SSE.

    Zwraca:
        None
    """

    async def collect() -> list[dict[str, object]]:
        events: list[dict[str, object]] = []
        async for chunk in stream_run_python('print("hello_studio")', timeout_sec=30):
            for line in chunk.strip().split("\n"):
                if line.startswith("data: "):
                    events.append(json.loads(line[6:]))
        return events

    events = asyncio.run(collect())
    log_lines = [e["line"] for e in events if e.get("type") == "log"]
    done = next((e for e in events if e.get("type") == "done"), None)
    assert "hello_studio" in log_lines
    assert done is not None
    assert done.get("success") is True
