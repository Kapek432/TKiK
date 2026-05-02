"""Wnioskowanie wymiarów warstw sieci neuronowych."""

from typing import Any

from src.config import Config
from src.semantic.symbol_table import NetworkContext


def _get_arg_value(
    args_list: list[dict[str, Any]],
    pos_idx: int,
    name: str,
    default: Any = None,
) -> Any:
    """
    Pobiera wartość argumentu po nazwie lub pozycji.

    Argumenty:
        args_list (list[dict[str, Any]]): Lista argumentów z kluczami type/value
        pos_idx (int): Indeks pozycyjny.
        name (str): Oczekiwana nazwa argumentu
        default (Any): Wartość domyślna

    Zwraca:
        Any: Wartość argumentu
    """
    for arg in args_list:
        if arg["type"] == "keyword" and arg["name"] == name:
            return arg["value"]
    positional = [a for a in args_list if a["type"] == "positional"]
    if pos_idx < len(positional):
        return positional[pos_idx]["value"]
    return default


def _semantic_error(line: Any, col: Any, message: str) -> ValueError:
    """
    Tworzy ustandaryzowany wyjątek semantyczny.

    Argumenty:
        line (Any): Linia błędu
        col (Any): Kolumna błędu
        message (str): Komunikat błędu

    Zwraca:
        ValueError: Wyjątek semantyczny
    """
    return ValueError(f"SEMANTIC ERROR [L: {line}, C: {col}]: {message}")


def infer_dense(
    ctx: NetworkContext,
    provided_args: list[dict[str, Any]],
    line: Any,
    col: Any,
) -> None:
    """
    Waliduje warstwę Dense i aktualizuje kontekst wymiarów.

    Argumenty:
        ctx (NetworkContext): Kontekst sieci
        provided_args (list[dict[str, Any]]): Lista argumentów
        line (Any): Linia błędu
        col (Any): Kolumna błędu
    """
    in_features = _get_arg_value(provided_args, 0, "in_features")
    out_features = _get_arg_value(provided_args, 1, "out_features")
    if in_features is None or out_features is None:
        raise _semantic_error(line, col, "Dense layer requires in_features and out_features.")
    if in_features <= 0 or out_features <= 0:
        raise _semantic_error(
            line,
            col,
            f"Dense layer dimensions must be positive ({in_features}, {out_features}).",
        )

    if ctx.first_input_shape is None:
        ctx.first_input_shape = (1, in_features)

    if ctx.last_output_shape is not None:
        current = ctx.last_output_shape
        expected = current[0] * current[1] * current[2] if isinstance(current, tuple) else current
        if in_features != expected:
            raise _semantic_error(
                line,
                col,
                f"Dimension mismatch. Dense layer expects {in_features}, but got {expected}.",
            )
    ctx.last_output_shape = out_features


def infer_conv2d(
    ctx: NetworkContext,
    provided_args: list[dict[str, Any]],
    line: Any,
    col: Any,
    config: Config,
) -> None:
    """
    Waliduje Conv2D i oblicza wyjściowe wymiary przestrzenne.

    Argumenty:
        ctx (NetworkContext): Kontekst sieci
        provided_args (list[dict[str, Any]]): Lista argumentów
        line (Any): Linia błędu
        col (Any): Kolumna błędu
    """
    in_ch = _get_arg_value(provided_args, 0, "in_channels")
    out_ch = _get_arg_value(provided_args, 1, "out_channels")
    k = _get_arg_value(provided_args, 2, "kernel_size")
    s = _get_arg_value(provided_args, 3, "stride", 1)
    p = _get_arg_value(provided_args, 4, "padding", 0)

    if in_ch is None or out_ch is None or k is None:
        raise _semantic_error(line, col, "Conv2D requires in_channels, out_channels, kernel_size.")
    if in_ch <= 0 or out_ch <= 0 or k <= 0:
        raise _semantic_error(line, col, "Conv2D parameters must be positive.")

    default_size = int(config.model.default_image_size)

    if ctx.first_input_shape is None:
        ctx.first_input_shape = (1, in_ch, default_size, default_size)

    if ctx.last_output_shape is None:
        if len(ctx.first_input_shape) == 4:
            ctx.last_output_shape = (
                ctx.first_input_shape[1],
                ctx.first_input_shape[2],
                ctx.first_input_shape[3],
            )
        else:
            ctx.last_output_shape = (in_ch, default_size, default_size)

    if in_ch != ctx.last_output_shape[0]:
        raise _semantic_error(
            line,
            col,
            f"Conv2D channels mismatch. Expected {ctx.last_output_shape[0]}, got {in_ch}.",
        )

    h_out = ((ctx.last_output_shape[1] + 2 * p - k) // s) + 1
    w_out = ((ctx.last_output_shape[2] + 2 * p - k) // s) + 1
    if h_out <= 0 or w_out <= 0:
        raise _semantic_error(line, col, "Conv2D parameters result in negative output size!")
    ctx.last_output_shape = (out_ch, h_out, w_out)


def infer_maxpool2d(
    ctx: NetworkContext,
    provided_args: list[dict[str, Any]],
    line: Any,
    col: Any,
) -> None:
    """
    Waliduje i oblicza wyjścia MaxPool2D.

    Argumenty:
        ctx (NetworkContext): Kontekst sieci
        provided_args (list[dict[str, Any]]): Lista argumentów
        line (Any): Linia błędu
        col (Any): Kolumna błędu
    """
    k = _get_arg_value(provided_args, 0, "kernel_size")
    s = _get_arg_value(provided_args, 1, "stride", k)
    p = _get_arg_value(provided_args, 2, "padding", 0)
    if not isinstance(ctx.last_output_shape, tuple):
        raise _semantic_error(line, col, "MaxPool2D must follow a spatial layer.")
    h_out = ((ctx.last_output_shape[1] + 2 * p - k) // s) + 1
    w_out = ((ctx.last_output_shape[2] + 2 * p - k) // s) + 1
    ctx.last_output_shape = (ctx.last_output_shape[0], h_out, w_out)


def infer_flatten(ctx: NetworkContext) -> None:
    """
    Zamienia wymiar (C, H, W) na płaski wektor.

    Argumenty:
        ctx (NetworkContext): Kontekst sieci
    """
    if isinstance(ctx.last_output_shape, tuple):
        ctx.last_output_shape = (
            ctx.last_output_shape[0] * ctx.last_output_shape[1] * ctx.last_output_shape[2]
        )
