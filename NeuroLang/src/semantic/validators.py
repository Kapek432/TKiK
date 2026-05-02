"""Walidatory semantyczne dla bloku konfiguracyjnego, danych i metryk."""

from typing import Any, Optional

from src.config import Config
from src.semantic.symbol_table import SymbolTable


def _allowed_config_keys(config: Optional[Config] = None) -> set[str]:
    """
    Zwraca zbiór dozwolonych kluczy bloku train_config z config.yaml.

    Argumenty:
        config (Optional[Config]): Konfiguracja projektu

    Zwraca:
        set[str]: Zbiór dozwolonych kluczy bloku train_config
    """
    cfg = config or Config.load()
    return set(cfg.validation.get("allowed_config_keys", []))


def _metrics_with_num_classes(config: Optional[Config] = None) -> set[str]:
    """
    Zwraca metryki parametryzowane liczbą klas z config.yaml.

    Argumenty:
        config (Optional[Config]): Konfiguracja projektu

    Zwraca:
        set[str]: Zbiór metryk parametryzowanych liczbą klas
    """
    cfg = config or Config.load()
    return set(cfg.validation.get("metrics_with_num_classes", []))


def _semantic_error(message: str, line: Any = "?", col: Any = "?") -> ValueError:
    """
    Tworzy ustandaryzowany wyjątek semantyczny.

    Argumenty:
        message (str): Komunikat błędu
        line (Any): Linia błędu
        col (Any): Kolumna błędu

    Zwraca:
        ValueError: Wyjątek semantyczny
    """
    return ValueError(f"SEMANTIC ERROR [L: {line}, C: {col}]: {message}")


def validate_config_item(key: str, value: Any, line: Any = "?", col: Any = "?") -> None:
    """
    Sprawdza dozwolone klucze i typy wartości w bloku train_config.

    Argumenty:
        key (str): Nazwa parametru konfiguracji
        value (Any): Wartość parametru
        line (Any): Linia wystąpienia
        col (Any): Kolumna wystąpienia
    """
    if key == "epochs":
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise _semantic_error(f"'epochs' must be a positive integer, got {value!r}.", line, col)
    elif key == "learning_rate":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise _semantic_error(
                f"'learning_rate' must be a positive number, got {value!r}.", line, col
            )
    elif key == "batch_size":
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise _semantic_error(
                f"'batch_size' must be a positive integer, got {value!r}.", line, col
            )
    elif key == "shuffle":
        if not isinstance(value, bool):
            raise _semantic_error(
                f"'shuffle' must be boolean (true/false), got {value!r}.", line, col
            )
    elif key == "target_type":
        if value not in ("long", "float"):
            raise _semantic_error(
                f"'target_type' must be 'long' or 'float', got {value!r}.", line, col
            )
    elif key == "task":
        if value not in ("multiclass", "binary", "regression"):
            raise _semantic_error(
                f"'task' must be 'multiclass', 'binary' or 'regression', got {value!r}.",
                line,
                col,
            )


def validate_config_block(
    cfg: dict[str, Any],
    block_name: str,
    line: Any = "?",
    col: Any = "?",
    config: Optional[Config] = None,
) -> None:
    """
    Sprawdza dozwolone klucze bloku train_config.

    Argumenty:
        cfg (dict[str, Any]): Blok train_config
        block_name (str): Nazwa bloku
        line (Any): Linia wystąpienia
        col (Any): Kolumna wystąpienia
        config (Optional[Config]): Konfiguracja projektu
    """
    allowed_keys = _allowed_config_keys(config)
    unknown = [k for k in cfg.keys() if k not in allowed_keys]
    if unknown:
        allowed = ", ".join(sorted(allowed_keys))
        raise _semantic_error(
            f"Unknown config key(s) {unknown} in block '{block_name}'. Allowed: {allowed}.",
            line,
            col,
        )


def validate_dataset_source(
    source: str, known_datasets: set[str], line: Any = "?", col: Any = "?"
) -> None:
    """
    Waliduje, czy źródło danych jest znanym zbiorem lub plikiem CSV.

    Argumenty:
        source (str): Źródło danych
        known_datasets (set[str]): Zbiór znanych zbiorów danych
        line (Any): Linia wystąpienia
        col (Any): Kolumna wystąpienia
    """
    if source in known_datasets:
        return
    if isinstance(source, str) and source.lower().endswith(".csv"):
        return
    allowed = ", ".join(sorted(known_datasets))
    raise _semantic_error(
        f"Unknown dataset source '{source}'. Expected a .csv path or one of: {allowed}.",
        line,
        col,
    )


def validate_metric_against_output(
    metric: dict[str, Any],
    last_output: Any,
    get_arg_value: Any,
    line: Any = "?",
    col: Any = "?",
    task: str = "multiclass",
    config: Optional[Config] = None,
) -> None:
    """
    Sprawdza zgodność liczby klas metryki z wyjściem sieci.

    Argumenty:
        metric (dict[str, Any]): Słownik metryki z polami name i args
        last_output (Any): Ostatni wymiar wyjściowy sieci
        get_arg_value (Any): Funkcja pobierająca wartość argumentu
        line (Any): Linia wywołania train
        col (Any): Kolumna wywołania train
        config (Optional[Config]): Konfiguracja projektu
    """
    name = metric.get("name")
    metric_task = get_arg_value(metric["args"], 0, "task")

    if task == "regression" and name in _metrics_with_num_classes(config):
        raise _semantic_error(
            f"Metric '{name}' is classification-only and cannot be used with regression task.",
            line,
            col,
        )

    if task in ("binary", "multiclass") and name in _metrics_with_num_classes(config):
        expected_metric_task = task
        if metric_task is not None and metric_task != expected_metric_task:
            raise _semantic_error(
                f"Metric '{name}' uses task='{metric_task}' but train task is '{task}'.",
                line,
                col,
            )

    if name not in _metrics_with_num_classes(config):
        return

    effective_task = metric_task if metric_task is not None else task
    num_classes = get_arg_value(metric["args"], 1, "num_classes")
    if not isinstance(last_output, int):
        return

    if effective_task == "binary":
        if last_output not in (1, 2):
            raise _semantic_error(
                f"Metric '{name}' uses task='binary' but network outputs {last_output}.",
                line,
                col,
            )
        return

    if effective_task == "multiclass" and last_output <= 1:
        raise _semantic_error(
            f"Metric '{name}' uses task='multiclass' but network outputs {last_output}.",
            line,
            col,
        )

    if num_classes is not None and num_classes != last_output:
        raise _semantic_error(
            f"Class count mismatch! Network outputs {last_output}, "
            f"and metric '{name}' expects {num_classes}.",
            line,
            col,
        )


def ensure_identifier_defined(
    kind: str,
    name: str,
    table: SymbolTable,
    line: Any = "?",
    col: Any = "?",
) -> None:
    """
    Sprawdza, czy identyfikator (sieć/konfiguracja/dane) został zdefiniowany.

    Argumenty:
        kind (str): "network", "config" lub "data"
        name (str): Szukana nazwa
        table (SymbolTable): Tablica symboli
        line (Any): Linia wystąpienia
        col (Any): Kolumna wystąpienia
    """
    mapping = {
        "network": (table.defined_networks, "network"),
        "config": (table.defined_configs, "training configuration"),
        "data": (table.defined_data, "data source"),
    }
    defined, label = mapping[kind]
    if name not in defined:
        raise _semantic_error(f"Attempt to use undefined {label} '{name}'!", line, col)
