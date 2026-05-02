"""Wspólna logika rozpoznawania typu zadania (task)."""

from typing import Any

from src.config import Config


def resolve_task(training_params: dict[str, Any], config: Config) -> str:
    """
    Wyznacza typ zadania na podstawie train_config i list lossów z config.yaml.

    Argumenty:
        training_params (dict[str, Any]): Parametry bloku train_config
        config (Config): Konfiguracja projektu

    Zwraca:
        str: multiclass, binary lub regression
    """
    explicit = training_params.get("task")
    if explicit in ("multiclass", "binary", "regression"):
        return explicit

    loss = (
        training_params.get("loss_function")
        if isinstance(training_params.get("loss_function"), dict)
        else {}
    )
    loss_name = loss.get("name")
    regression_losses = set(config.validation.get("regression_losses", []))
    binary_losses = set(config.validation.get("binary_losses", []))

    if loss_name in regression_losses:
        return "regression"
    if loss_name in binary_losses:
        return "binary"
    return "multiclass"
