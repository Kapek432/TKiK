"""Generatory dla instrukcji sterujących i operacji na modelu."""

from typing import Any

from src.codegen.indent import CodeBuffer, format_value, quote_string


def generate_variable(buffer: CodeBuffer, instr: dict[str, Any], indent: int = 0) -> None:
    """
    Dodaje przypisanie zmiennej (literal, liczba, boolean lub napis).
    
    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Słownik instrukcji
        indent (int): Poziom wcięcia
    """
    name = instr["name"]
    buffer.add(f"{name} = {format_value(instr['value'])}", indent)


def generate_load_weights(
    buffer: CodeBuffer, instr: dict[str, Any], model_var: str = "model", indent: int = 0
) -> None:
    """
    Dodaje opcjonalne wczytanie wag modelu z pliku.
    
    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Słownik instrukcji
        model_var (str): Nazwa zmiennej modelu, na której operujemy
        indent (int): Poziom wcięcia
    """
    filepath = instr["filepath"]
    quoted = quote_string(filepath)
    buffer.add(f"if os.path.exists({quoted}):", indent)
    buffer.add(
        f"{model_var}.load_state_dict(torch.load({quoted}, weights_only=True))",
        indent + 1,
    )
    buffer.add(f"print(f'Loaded weights from {{{quoted}}}')", indent + 1)
    buffer.add("else:", indent)
    buffer.add(
        f"print(f'Warning: file {{{quoted}}} does not exist. Model initialized randomly.')",
        indent + 1,
    )
    buffer.add("")


def generate_save_weights(
    buffer: CodeBuffer, instr: dict[str, Any], model_var: str = "model", indent: int = 0
) -> None:
    """
    Dodaje zapis wag do pliku.
    
    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Słownik instrukcji
        model_var (str): Nazwa zmiennej modelu, którego wagi zapisujemy
        indent (int): Poziom wcięcia
    """
    buffer.add(f"torch.save({model_var}.state_dict(), {quote_string(instr['filepath'])})", indent)


def generate_export(
    buffer: CodeBuffer,
    instr: dict[str, Any],
    first_input: tuple,
    model_var: str = "model",
    indent: int = 0,
) -> None:
    """
    Dodaje eksport modelu do formatu ONNX.
    
    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Słownik instrukcji
        first_input (tuple): Rozmiar wejścia modelu
        model_var (str): Nazwa zmiennej modelu eksportowanego do ONNX
        indent (int): Poziom wcięcia
    """
    buffer.add(f"{model_var}.eval()", indent)
    buffer.add(f"dummy_input = torch.randn({first_input}).to(device)", indent)
    buffer.add("try:", indent)
    buffer.add(
        f"torch.onnx.export({model_var}, dummy_input, {quote_string(instr['filepath'])}, "
        "input_names=['input'], output_names=['output'])",
        indent + 1,
    )
    buffer.add("except Exception as e:", indent)
    buffer.add("print(f'Export error: {e}')", indent + 1)


def generate_print_commands(
    buffer: CodeBuffer, instr: dict[str, Any], model_var: str = "model", indent: int = 0
) -> None:
    """
    Dodaje instrukcje print w wariantach string, summary i wyrażenie.
    
    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Słownik instrukcji
        model_var (str): Nazwa zmiennej modelu użytej dla podsumowania
        indent (int): Poziom wcięcia
    """
    subtype = instr["subtype"]
    if subtype == "string":
        buffer.add(f"print({quote_string(instr['value'])})", indent)
    elif subtype == "summary":
        buffer.add(f"print('Model architecture ' + {quote_string(instr['network'])})", indent)
        buffer.add(f"print({model_var})", indent)
    elif subtype == "expr":
        buffer.add(f"print({instr['value']})", indent)


def generate_summary(
    buffer: CodeBuffer, instr: dict[str, Any], model_var: str = "model", indent: int = 0
) -> None:
    """
    Dodaje podsumowanie architektury - nazwa sieci i liczba parametrów.
    
    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Słownik instrukcji
        model_var (str): Nazwa zmiennej modelu, dla którego wypisujemy summary
        indent (int): Poziom wcięcia
    """
    network_name = instr["network"]
    buffer.add(f"print('Model Summary: ' + {quote_string(network_name)})", indent)
    buffer.add(f"print({model_var})", indent)
    buffer.add(
        f"total_params = sum(p.numel() for p in {model_var}.parameters() if p.requires_grad)",
        indent,
    )
    buffer.add("print(f'Parameters: {total_params}')", indent)
