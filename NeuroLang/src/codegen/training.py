"""Generowanie pętli treningowej."""

from typing import Any

from src.codegen.indent import CodeBuffer, format_value
from src.codegen.task import resolve_task
from src.config import Config


def _format_call_args(args: list[dict[str, Any]]) -> str:
    """
    Formatuje argumenty wywołania (np. optymalizator, funkcja straty).

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


def generate_training_loop(
    buffer: CodeBuffer,
    instr: dict[str, Any],
    training_cfg: dict[str, Any],
    components: dict[str, Any],
    config: Config,
    model_var: str = "model",
    indent: int = 0,
) -> None:
    """
    Dodaje pętlę treningową z obsługą metryk i tqdm.

    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Komenda train
        training_cfg (dict[str, Any]): Konfiguracja train_config
        components (dict[str, Any]): Mapowanie komponentów
        config (Config): Konfiguracja projektu
        model_var (str): Nazwa zmiennej modelu używanego do treningu
        indent (int): Poziom wcięcia
    """
    if training_cfg.get("name") != instr["config"]:
        return

    data_alias = instr["data"]
    params = training_cfg.get("params", {})
    task = resolve_task(params, config)
    epochs = params.get("epochs", int(config.training.default_epochs))
    lr = params.get("learning_rate", float(config.training.default_learning_rate))

    opt_cfg = params.get(
        "optimizer",
        {"name": "Adam", "args": [{"type": "keyword", "name": "lr", "value": lr}]},
    )
    opt_name = components.get(opt_cfg["name"], {}).get("pytorch_name", f"optim.{opt_cfg['name']}")
    opt_args_rendered = _format_call_args(opt_cfg.get("args", []))
    has_lr = any(a.get("name") == "lr" for a in opt_cfg.get("args", []) if a["type"] == "keyword")
    has_positional = any(a["type"] == "positional" for a in opt_cfg.get("args", []))
    if not has_lr and not has_positional:
        if opt_args_rendered:
            opt_args_rendered = f"{opt_args_rendered}, lr={lr}"
        else:
            opt_args_rendered = f"lr={lr}"

    loss_cfg = params.get("loss_function", {"name": "CrossEntropyLoss", "args": []})
    loss_name = components.get(loss_cfg["name"], {}).get("pytorch_name", f"nn.{loss_cfg['name']}")
    loss_args_rendered = _format_call_args(loss_cfg.get("args", []))

    buffer.add(f"task = '{task}'", indent)
    buffer.add(f"criterion = {loss_name}({loss_args_rendered})", indent)
    buffer.add(f"optimizer = {opt_name}({model_var}.parameters(), {opt_args_rendered})", indent)
    buffer.add(f"epochs = {epochs}", indent)
    buffer.add("", indent)

    metrics = params.get("metrics", [])
    metric_vars: list[tuple[str, str]] = []
    for i, metric in enumerate(metrics):
        var_name = f"metric_{i}"
        metric_name = metric["name"]
        metric_class = components.get(metric_name, {}).get(
            "pytorch_name", f"torchmetrics.{metric_name}"
        )
        metric_args_str = _format_call_args(metric.get("args", []))
        metric_vars.append((var_name, metric_name))
        buffer.add(f"{var_name} = {metric_class}({metric_args_str}).to(device)", indent)

    buffer.add("", indent)
    buffer.add("for epoch in range(epochs):", indent)
    buffer.add(f"{model_var}.train()", indent + 1)
    buffer.add("epoch_loss = 0.0", indent + 1)
    buffer.add(
        f"progress_bar = tqdm({data_alias}, desc=f'Epoch {{epoch+1}}/{{epochs}}')",
        indent + 1,
    )
    buffer.add("for batch in progress_bar:", indent + 1)
    buffer.add("inputs, targets = batch", indent + 2)
    buffer.add("inputs, targets = inputs.to(device), targets.to(device)", indent + 2)
    buffer.add("optimizer.zero_grad()", indent + 2)
    buffer.add(f"outputs = {model_var}(inputs)", indent + 2)
    buffer.add("if outputs.ndim > 1 and outputs.size(-1) == 1:", indent + 2)
    buffer.add("outputs_for_loss = outputs.squeeze(-1)", indent + 3)
    buffer.add("else:", indent + 2)
    buffer.add("outputs_for_loss = outputs", indent + 3)
    buffer.add("targets_for_loss = targets", indent + 2)
    buffer.add("if task == 'multiclass':", indent + 2)
    buffer.add("targets_for_loss = targets.long()", indent + 3)
    buffer.add("elif task in ('binary', 'regression'):", indent + 2)
    buffer.add("targets_for_loss = targets.float()", indent + 3)
    buffer.add("if targets_for_loss.ndim > 1 and targets_for_loss.size(-1) == 1:", indent + 3)
    buffer.add("targets_for_loss = targets_for_loss.squeeze(-1)", indent + 4)
    buffer.add("loss = criterion(outputs_for_loss, targets_for_loss)", indent + 2)
    buffer.add("loss.backward()", indent + 2)
    buffer.add("optimizer.step()", indent + 2)
    buffer.add("epoch_loss += loss.item() * inputs.size(0)", indent + 2)

    buffer.add("metric_outputs = outputs", indent + 2)
    buffer.add("metric_targets = targets", indent + 2)
    buffer.add("if task == 'binary':", indent + 2)
    buffer.add("binary_probs = torch.sigmoid(outputs_for_loss)", indent + 3)
    buffer.add("metric_outputs = (binary_probs >= 0.5).long()", indent + 3)
    buffer.add("metric_targets = targets_for_loss.long()", indent + 3)
    buffer.add("elif task == 'regression':", indent + 2)
    buffer.add("metric_outputs = outputs_for_loss", indent + 3)
    buffer.add("metric_targets = targets_for_loss", indent + 3)
    buffer.add("else:", indent + 2)
    buffer.add("metric_targets = targets_for_loss", indent + 3)

    for var_name, _ in metric_vars:
        buffer.add(f"{var_name}(metric_outputs, metric_targets)", indent + 2)

    buffer.add("progress_bar.set_postfix(loss=loss.item())", indent + 2)
    buffer.add("", indent)
    buffer.add(f"epoch_loss /= len({data_alias}.dataset)", indent + 1)

    metrics_str = "".join([f", {name}: {{{var}.compute():.4f}}" for var, name in metric_vars])
    buffer.add(
        f"print(f'Epoch [{{epoch+1}}/{{epochs}}], Loss: {{epoch_loss:.4f}}{metrics_str}')",
        indent + 1,
    )

    for var_name, _ in metric_vars:
        buffer.add(f"{var_name}.reset()", indent + 1)
    buffer.add("", indent)
