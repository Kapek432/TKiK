"""Generowanie konfiguracji urządzenia obliczeniowego."""

from typing import Any, Optional

from src.codegen.indent import CodeBuffer


def resolve_train_device(config: dict[str, Any]) -> Optional[str]:
    """
    Wyszukuje pierwszą komendę train i pobiera z niej device.

    Argumenty:
        config (dict[str, Any]): Słownik konfiguracji kompilatora

    Zwraca:
        Optional[str]: Nazwa urządzenia lub None jeśli nie znaleziono komendy train
    """
    for instr in config.get("instructions", []):
        if instr.get("cmd_type") == "train":
            return instr.get("device")
    return None


def generate_device_config(buffer: CodeBuffer, device: Optional[str]) -> None:
    """
    Dodaje kod wybierający urządzenie (CPU/CUDA/MPS).

    Argumenty:
        buffer (CodeBuffer): Bufor generowanego kodu
        device (Optional[str]): Nazwa urządzenia pochodząca z komendy train
    """
    if device in ("gpu", "cuda"):
        buffer.add("device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')")
    elif device == "mps":
        buffer.add("device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')")
    else:
        buffer.add("device = torch.device('cpu')")
    buffer.add("")
