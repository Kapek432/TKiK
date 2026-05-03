"""Tłumaczenie warunków NeuroLang na wyrażenia Pythona."""

from typing import Any, Optional

_COMPARISON_OPS = {"==", "!=", "<", "<=", ">", ">="}


def _format_operand(value: Any) -> str:
    """Formatuje operand porównania (liczba/bool) na literał Pythona."""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, (int, float)):
        return repr(value)
    return str(value)


def condition_code(condition: dict[str, Any], data_alias: Optional[str] = None) -> str:
    """
    Zamienia słownik warunku na wyrażenie Pythona.

    Obsługiwane typy warunków:
        - gpu_available / mps_available / has_data - predykaty środowiskowe
        - bool - literał true/false
        - truthy - sprawdzenie prawdziwości
        - compare - porównanie (==, !=, <, <=, >, >=)
        - not - negacja logiczna
        - and / or - spójniki logiczne

    Args:
        condition (dict[str, Any]): Struktura opisujaca warunek.
        data_alias (Optional[str]): Alias wczytanych danych wymagany dla
            warunku 'has_data' - gdy brak, fallback do 'False'.

    Returns:
        str: Wyrażenie logiczne w języku Python.
    """
    cond_type = condition["type"]
    if cond_type == "gpu_available":
        return "torch.cuda.is_available()"
    if cond_type == "mps_available":
        return "torch.backends.mps.is_available()"
    if cond_type == "has_data":
        return f"{data_alias} is not None" if data_alias else "False"
    if cond_type == "bool":
        return "True" if condition.get("value") else "False"
    if cond_type == "truthy":
        value = condition["value"]
        return f"bool({_format_operand(value)})"
    if cond_type == "compare":
        op = condition["op"]
        if op not in _COMPARISON_OPS:
            raise ValueError(f"Unsupported comparison operator: {op}")
        left = _format_operand(condition["left"])
        right = _format_operand(condition["right"])
        return f"({left} {op} {right})"
    if cond_type == "not":
        inner = condition_code(condition["operand"], data_alias)
        return f"(not {inner})"
    if cond_type == "and":
        parts = [condition_code(op, data_alias) for op in condition["operands"]]
        return "(" + " and ".join(parts) + ")"
    if cond_type == "or":
        parts = [condition_code(op, data_alias) for op in condition["operands"]]
        return "(" + " or ".join(parts) + ")"
    raise ValueError(f"Unsupported condition type: {cond_type}")
