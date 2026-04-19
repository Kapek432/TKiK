"""Konfiguracja logowania dla całego projektu."""

import logging
from typing import Optional

_CONFIGURED: bool = False


def setup(level: Optional[str] = None, fmt: Optional[str] = None) -> None:
    """
    Konfiguruje globalny logger.

    Argumenty:
        level (Optional[str]): Poziom logowania, np. "INFO", "DEBUG"
        fmt (Optional[str]): Format wiadomości zgodny z modulem logging
    """
    global _CONFIGURED
    resolved_level = level or "INFO"
    resolved_fmt = fmt or "%(message)s"
    logging.basicConfig(
        level=getattr(logging, resolved_level.upper(), logging.INFO),
        format=resolved_fmt,
        force=not _CONFIGURED,
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """
    Zwraca logger o podanej nazwie.

    Argumenty:
        name (str): Nazwa loggera

    Zwraca:
        logging.Logger: Instancja loggera
    """
    return logging.getLogger(name)
