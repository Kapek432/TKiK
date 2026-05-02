"""Generowanie definicji klasy modelu PyTorch."""

from typing import Any

from src.codegen.indent import CodeBuffer, format_value


def _format_layer_args(args: list[dict[str, Any]]) -> str:
    """
    Formatuje argumenty pojedynczej warstwy.

    Argumenty:
        args (list[dict[str, Any]]): Lista argumentów

    Zwraca:
        str: Formatowane argumenty
    """
    rendered: list[str] = []
    for arg in args:
        value = format_value(arg["value"])
        if arg["type"] == "positional":
            rendered.append(value)
        else:
            rendered.append(f"{arg['name']}={value}")
    return ", ".join(rendered)


def generate_model_class(
    buffer: CodeBuffer, network: dict[str, Any], components: dict[str, Any]
) -> None:
    """
    Dodaje klasę sieci dziedziczącą po nn.Module.

    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        network (dict[str, Any]): Opis sieci (name, layers)
        components (dict[str, Any]): Mapowanie warstw na klasy PyTorch
    """
    if not network:
        return

    name = network["name"]
    layers = network["layers"]

    buffer.add(f"class {name}(nn.Module):")
    buffer.add("def __init__(self):", 1)
    buffer.add("super().__init__()", 2)
    buffer.add("self.model = nn.Sequential(", 2)

    for layer in layers:
        layer_name = layer["name"]
        args_str = _format_layer_args(layer.get("args", []))
        pt_class = components.get(layer_name, {}).get("pytorch_name", f"nn.{layer_name}")
        buffer.add(f"{pt_class}({args_str}),", 3)

    buffer.add(")", 2)
    buffer.add("")

    buffer.add("def forward(self, x):", 1)
    first_layer = layers[0]["name"] if layers else ""
    if first_layer == "Dense":
        buffer.add("if x.dim() > 2:", 2)
        buffer.add("x = x.view(x.size(0), -1)", 3)
    buffer.add("return self.model(x)", 2)
    buffer.add("")


def generate_model_instantiations(
    buffer: CodeBuffer, networks: dict[str, dict[str, Any]]
) -> None:
    """
    Dodaje linie tworzące instancje modeli i przenoszące je na wybrane urządzenie.

    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        networks (dict[str, dict[str, Any]]): Opisy sieci
    """
    if not networks:
        return

    network_names = list(networks.keys())
    for name in network_names:
        buffer.add(f"model_{name} = {name}().to(device)")
    if len(network_names) == 1:
        only_name = network_names[0]
        buffer.add(f"model = model_{only_name}")
    buffer.add("")
