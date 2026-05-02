"""Generowanie kodu ładującego dane."""

from typing import Any

from src.codegen.indent import CodeBuffer, quote_string
from src.codegen.task import resolve_task
from src.config import Config


def _resolve_target_type(
    params: dict[str, Any], training_params: dict[str, Any], config: Config
) -> str:
    """
    Wyznacza docelowy typ tensora z etykiet w zbiorze CSV.

    Argumenty:
        params (dict[str, Any]): Parametry load_data
        training_params (dict[str, Any]): Parametry bloku train_config
        config (Config): Konfiguracja projektu

    Zwraca:
        str: torch.long dla klasyfikacji, torch.float32 dla regresji
    """
    explicit = params.get("target_type")
    if explicit == "long":
        return "torch.long"
    if explicit == "float":
        return "torch.float32"

    if resolve_task(training_params or {}, config) == "regression":
        return "torch.float32"
    return "torch.long"


def generate_data_loader(
    buffer: CodeBuffer,
    data_cfg: dict[str, Any],
    training_params: dict[str, Any],
    config: Config,
    defined_aliases: list[str],
    initialize_aliases: bool = False,
    indent: int = 0,
) -> None:
    """
    Dodaje kod ładowania zbioru danych.

    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        data_cfg (dict[str, Any]): Słownik konfiguracji źródła danych
        training_params (dict[str, Any]): Parametry treningu - użyte do wnioskowania
            typu etykiet
        config (Config): Konfiguracja projektu
        defined_aliases (list[str]): Wszystkie aliasy danych dostępne w skrypcie
        initialize_aliases (bool): Czy zainicjalizować aliasy jako None u góry skryptu
        indent (int): Poziom wcięcia dla generowanych instrukcji (ważne przy
            generowaniu w środku bloku if)
    """
    if initialize_aliases:
        for alias in defined_aliases:
            buffer.add(f"{alias} = None", indent)
        if defined_aliases:
            buffer.add("", indent)

    if not data_cfg:
        return

    source = data_cfg["source"]
    alias = data_cfg["alias"]
    params = data_cfg["params"]

    batch_size = params.get("batch_size", int(config.training.default_batch_size))
    shuffle = params.get("shuffle", True)
    data_dir = str(config.paths.default_data_dir)
    image_datasets = set(config.validation.get("image_datasets", []))

    if source in image_datasets:
        transform_call = params.get("transform")
        transform_name = transform_call["name"] if transform_call else "ToTensor"
        buffer.add(f"transform = transforms.Compose([transforms.{transform_name}()])", indent)

        download = params.get("download", True)
        buffer.add(
            f"dataset = torchvision.datasets.{source}("
            f"root={quote_string(data_dir)}, train=True, "
            f"download={download}, transform=transform)",
            indent,
        )
        buffer.add(
            f"{alias} = DataLoader(dataset, batch_size={batch_size}, shuffle={shuffle})",
            indent,
        )
        buffer.add("", indent)
        return

    if isinstance(source, str) and source.lower().endswith(".csv"):
        target_col = params.get("target_column", "target")
        target_type = _resolve_target_type(params, training_params, config)
        buffer.add(f"if not os.path.exists({quote_string(source)}):")
        buffer.add(
            f"raise FileNotFoundError('CSV data not found: ' + {quote_string(source)})",
            indent + 1,
        )
        buffer.add(f"df = pd.read_csv({quote_string(source)}).dropna()", indent)
        buffer.add(
            f"X = torch.tensor(df.drop({quote_string(target_col)}, axis=1).values, "
            f"dtype=torch.float32)",
            indent,
        )
        buffer.add(
            f"y = torch.tensor(df[{quote_string(target_col)}].values, dtype={target_type})",
            indent,
        )
        buffer.add("dataset = TensorDataset(X, y)", indent)
        buffer.add(
            f"{alias} = DataLoader(dataset, batch_size={batch_size}, shuffle={shuffle})",
            indent,
        )
        buffer.add("", indent)
