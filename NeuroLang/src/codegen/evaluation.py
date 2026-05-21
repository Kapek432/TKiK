"""Generowanie pętli ewaluacyjnej i predykcji."""

from typing import Any

from src.codegen.indent import CodeBuffer, format_value, quote_string
from src.codegen.task import resolve_task
from src.config import Config


def _format_call_args(args: list[dict[str, Any]]) -> str:
    """
    Formatuje argumenty wywołania.

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


def generate_evaluate_loop(
    buffer: CodeBuffer,
    instr: dict[str, Any],
    training_cfg: dict[str, Any],
    components: dict[str, Any],
    config: Config,
    model_var: str = "model",
    indent: int = 0,
) -> None:
    """
    Dodaje pętlę ewaluacyjną z model.eval() i torch.no_grad().

    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Komenda evaluate
        training_cfg (dict[str, Any]): Konfiguracja treningu (dla metryk)
        components (dict[str, Any]): Mapowanie komponentów
        config (Config): Konfiguracja projektu
        model_var (str): Nazwa zmiennej modelu używanego do ewaluacji
        indent (int): Poziom wcięcia
    """
    data_alias = instr["data"]
    params = training_cfg.get("params", {})
    task = resolve_task(params, config)

    loss_cfg = params.get("loss_function", {"name": "CrossEntropyLoss", "args": []})
    loss_name = components.get(loss_cfg["name"], {}).get("pytorch_name", f"nn.{loss_cfg['name']}")
    loss_args_rendered = _format_call_args(loss_cfg.get("args", []))

    buffer.add(f"criterion = {loss_name}({loss_args_rendered})", indent)
    buffer.add(f"{model_var}.eval()", indent)
    buffer.add("eval_loss = 0.0", indent)
    buffer.add("eval_batches = 0", indent)

    metrics = params.get("metrics", [])
    metric_vars: list[tuple[str, str]] = []
    for i, metric in enumerate(metrics):
        var_name = f"eval_metric_{i}"
        metric_name = metric["name"]
        metric_class = components.get(metric_name, {}).get(
            "pytorch_name", f"torchmetrics.{metric_name}"
        )
        metric_args_str = _format_call_args(metric.get("args", []))
        metric_vars.append((var_name, metric_name))
        buffer.add(f"{var_name} = {metric_class}({metric_args_str}).to(device)", indent)

    buffer.add("", indent)
    buffer.add("with torch.no_grad():", indent)
    buffer.add(f"for batch in tqdm({data_alias}, desc='Evaluation'):", indent + 1)
    buffer.add("inputs, targets = batch", indent + 2)
    buffer.add("inputs, targets = inputs.to(device), targets.to(device)", indent + 2)
    buffer.add(f"outputs = {model_var}(inputs)", indent + 2)
    buffer.add("if outputs.ndim > 1 and outputs.size(-1) == 1:", indent + 2)
    buffer.add("outputs_for_loss = outputs.squeeze(-1)", indent + 3)
    buffer.add("else:", indent + 2)
    buffer.add("outputs_for_loss = outputs", indent + 3)
    buffer.add("targets_for_loss = targets", indent + 2)
    buffer.add(f"task = '{task}'", indent + 2)
    buffer.add("if task == 'multiclass':", indent + 2)
    buffer.add("targets_for_loss = targets.long()", indent + 3)
    buffer.add("elif task in ('binary', 'regression'):", indent + 2)
    buffer.add("targets_for_loss = targets.float()", indent + 3)
    buffer.add("if targets_for_loss.ndim > 1 and targets_for_loss.size(-1) == 1:", indent + 3)
    buffer.add("targets_for_loss = targets_for_loss.squeeze(-1)", indent + 4)
    buffer.add("loss = criterion(outputs_for_loss, targets_for_loss)", indent + 2)
    buffer.add("eval_loss += loss.item() * inputs.size(0)", indent + 2)
    buffer.add("eval_batches += inputs.size(0)", indent + 2)

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
    buffer.add("", indent)
    buffer.add("eval_loss /= eval_batches", indent)

    metrics_str = "".join([f", {name}: {{{var}.compute():.4f}}" for var, name in metric_vars])
    buffer.add(f"print(f'Evaluation - loss: {{eval_loss:.4f}}{metrics_str}')", indent)
    for var_name, _ in metric_vars:
        buffer.add(f"{var_name}.reset()", indent)


def generate_predict(
    buffer: CodeBuffer,
    instr: dict[str, Any],
    training_cfg: dict[str, Any],
    config: Config,
    model_var: str = "model",
    indent: int = 0,
) -> None:
    """
    Dodaje kod predykcji na dostępnym zbiorze danych lub pliku CSV.

    Argumenty:
        buffer (CodeBuffer): Bufor kodu
        instr (dict[str, Any]): Komenda predict
        training_cfg (dict[str, Any]): Konfiguracja treningu powiązana z predykcją
        config (Config): Konfiguracja projektu
        model_var (str): Nazwa zmiennej modelu używanego do predykcji
        indent (int): Poziom wcięcia
    """
    source = instr["source"]
    is_path = instr.get("is_path", False)
    task = resolve_task(training_cfg.get("params", {}), config)

    buffer.add(f"{model_var}.eval()", indent)
    buffer.add("with torch.no_grad():", indent)
    buffer.add("try:", indent + 1)

    if is_path:
        buffer.add(f"if not os.path.exists({quote_string(source)}):", indent + 2)
        buffer.add(
            f"raise FileNotFoundError('Prediction source not found: ' + {quote_string(source)})",
            indent + 3,
        )
        buffer.add(f"predict_df = pd.read_csv({quote_string(source)}).dropna()", indent + 2)
        buffer.add(
            "inputs = torch.tensor(predict_df.values, dtype=torch.float32)",
            indent + 2,
        )
    else:
        buffer.add(f"inputs, _ = next(iter({source}))", indent + 2)

    buffer.add("inputs = inputs.to(device)", indent + 2)
    buffer.add(f"outputs = {model_var}(inputs)", indent + 2)
    if task == "multiclass":
        buffer.add("_, predicted = torch.max(outputs, 1)", indent + 2)
        buffer.add("print(f'Predictions: {predicted[:10].tolist()}')", indent + 2)
    elif task == "binary":
        buffer.add("if outputs.ndim > 1 and outputs.size(-1) == 1:", indent + 2)
        buffer.add("logits = outputs.squeeze(-1)", indent + 3)
        buffer.add("else:", indent + 2)
        buffer.add("logits = outputs", indent + 3)
        buffer.add("probs = torch.sigmoid(logits)", indent + 2)
        buffer.add("predicted = (probs >= 0.5).long()", indent + 2)
        buffer.add("print(f'Predictions: {predicted[:10].tolist()}')", indent + 2)
        buffer.add("print(f'Probabilities: {probs[:10].tolist()}')", indent + 2)
    else:
        buffer.add("if outputs.ndim > 1 and outputs.size(-1) == 1:", indent + 2)
        buffer.add("predicted = outputs.squeeze(-1)", indent + 3)
        buffer.add("else:", indent + 2)
        buffer.add("predicted = outputs", indent + 3)
        buffer.add("print(f'Predictions: {predicted[:10].tolist()}')", indent + 2)
    buffer.add("except Exception as e:", indent + 1)
    buffer.add("print(f'Prediction error: {e}')", indent + 2)
