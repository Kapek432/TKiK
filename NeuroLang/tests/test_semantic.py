"""Testy analizy semantycznej NeuroLang."""

from typing import Any

import pytest
from lark import Lark
from lark.exceptions import VisitError

from src.semantic.transformer import NeuroLangCompiler
from src.semantic.visitor import NeuroLangVisitor


def _extract_error(excinfo: Any) -> str:
    """
    Pomocnicza funkcja do wyciągnięcia wiadomości błędu z otoczonego wyjątku Lark.

    Argumenty:
        excinfo (Any): Obiekt wyjątku zwracany przez pytest.raises (ExceptionInfo)

    Zwraca:
        str: Wiadomość błędu zawarta w wyjątku Lark
    """
    msg = str(excinfo.value)
    if "SEMANTIC ERROR" in msg:
        return msg.split("\n")[-1] if "\n" in msg else msg
    return msg


def _run(parser: Lark, compiler: NeuroLangCompiler, code: str) -> dict[str, Any]:
    """
    Funkcja pomocnicza do uruchomienia kodu NeuroLang.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
        code (str): Kod NeuroLang

    Zwraca:
        dict[str, Any]: Wynik transformacji
    """
    tree = parser.parse(code)
    visitor = NeuroLangVisitor(compiler)
    visitor.visit(tree)
    return compiler.transform(tree)


def test_variable_redefinition(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Weryfikuje, czy kompilator zgłasza błąd przy ponownej deklaracji zmiennej.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, "let x = 5\nlet x = 10")
    assert "is already declared" in _extract_error(excinfo), (
        f"Expected 'is already declared', got {_extract_error(excinfo)}"
    )


def test_undefined_variable(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Sprawdza, czy użycie niezdefiniowanej zmiennej powoduje błąd semantyczny.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, "let y = x + 5")
    assert "Use of undefined variable 'x'" in _extract_error(excinfo), (
        f"Expected 'Use of undefined variable 'x'', got {_extract_error(excinfo)}"
    )


def test_division_by_zero(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Upewnia się, że dzielenie przez zero w wyrażeniach jest wykrywane.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, "let x = 10 / (2 - 2)")
    assert "Division by zero" in _extract_error(excinfo), (
        f"Expected 'Division by zero', got {_extract_error(excinfo)}"
    )


def test_mismatched_dense_layers(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Testuje walidację wymiarów warstw Dense i zgłasza błąd przy niezgodności wymiarów.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network BadNet {
        layer: Dense(784, 128),
        layer: Dense(64, 10)
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "Dimension mismatch" in _extract_error(excinfo), (
        f"Expected 'Dimension mismatch', got {_extract_error(excinfo)}"
    )


def test_invalid_dropout_p(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Sprawdza, czy parametr 'p' w Dropout miesci sie w [0, 1] i zgłasza błąd przy nieprawidłowym parametrze.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network BadNet {
        layer: Dropout(1.5)
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "must be in range [0, 1]" in _extract_error(excinfo), (
        f"Expected 'must be in range [0, 1]', got {_extract_error(excinfo)}"
    )


def test_conv2d_shape_mismatch(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Weryfikuje, czy liczba kanałów wejściowych Conv2D zgadza się z poprzednią warstwą i zgłasza błąd przy niezgodności wymiarów.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network BadConv {
        layer: Conv2D(1, 32, 3),
        layer: Conv2D(16, 64, 3)
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "Conv2D channels mismatch" in _extract_error(excinfo), (
        f"Expected 'Conv2D channels mismatch', got {_extract_error(excinfo)}"
    )


def test_duplicate_config_keys(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Zgłasza błąd przy wielokrotnym kluczu w bloku train_config.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    train_config BadConfig {
        learning_rate: 0.01,
        learning_rate: 0.02
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "is defined multiple times" in _extract_error(excinfo), (
        f"Expected 'is defined multiple times', got {_extract_error(excinfo)}"
    )


def test_metrics_mismatch(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Liczba klas w metryce musi zgadzać się z wyjściem sieci i zgłasza błąd przy niezgodności.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Siec10 { layer: Dense(784, 10) }
    train_config Config5 { metrics: [Accuracy(task="multiclass", num_classes=5)] }
    load_data MNIST { batch_size: 32 }
    train Siec10 with Config5 on MNIST
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "Class count mismatch" in _extract_error(excinfo), (
        f"Expected 'Class count mismatch', got {_extract_error(excinfo)}"
    )


def test_error_location_formatting(parser, compiler):
    """
    Błędy zawierają informacje o linii i kolumnie.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, "let x = 5\nlet x = 10")
    error = _extract_error(excinfo)
    assert "[L: 2, C: 1]" in error, f"Expected '[L: 2, C: 1]', got {error}"
    assert "Variable 'x' is already declared" in error, (
        f"Expected 'Variable 'x' is already declared', got {error}"
    )


def test_maxpool2d_invalid_sequence(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    MaxPool2D nie może być użyta po Flatten/Dense.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network BadSeq {
        layer: Conv2D(1, 32, 3),
        layer: Flatten(),
        layer: MaxPool2D(2)
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "must follow a spatial layer" in _extract_error(excinfo), (
        f"Expected 'must follow a spatial layer', got {_extract_error(excinfo)}"
    )


def test_conv2d_negative_output(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Wykrywanie Conv2D o parametrach skutkujących ujemnym rozmiarem wyjściowym.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network SmallNet(1, 4, 4) {
        layer: Conv2D(1, 32, 10)
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "negative output size" in _extract_error(excinfo), (
        f"Expected 'negative output size', got {_extract_error(excinfo)}"
    )


def test_evaluate_undefined_network(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Ewaluacja na niezdefiniowanej sieci zgłasza błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Net { layer: Dense(784, 10) }
    load_data MNIST { batch_size: 32 }
    train_config Cfg { epochs: 1 }
    train Net with Cfg on MNIST
    evaluate FakeNet on MNIST
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "undefined network 'FakeNet'" in _extract_error(excinfo), (
        f"Expected 'undefined network 'FakeNet'', got {_extract_error(excinfo)}"
    )


def test_evaluate_undefined_data(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Ewaluacja na niezdefiniowanym zbiorze danych zgłasza błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Net { layer: Dense(784, 10) }
    evaluate Net on FakeData
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "undefined data source 'FakeData'" in _extract_error(excinfo), (
        f"Expected 'undefined data source 'FakeData'', got {_extract_error(excinfo)}"
    )


def test_print_summary_undefined_network(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Print summary niezdefiniowanej sieci zgłasza błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, "print summary FakeNet")
    assert "undefined network 'FakeNet'" in _extract_error(excinfo), (
        f"Expected 'undefined network 'FakeNet'', got {_extract_error(excinfo)}"
    )


def test_export_undefined_network(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Eksport niezdefiniowanej sieci zgłasza błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, 'export FakeNet to "model.onnx"')
    assert "undefined network 'FakeNet'" in _extract_error(excinfo), (
        f"Expected 'undefined network 'FakeNet'', got {_extract_error(excinfo)}"
    )


def test_predict_undefined_network(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Predykcja na niezdefiniowanej sieci zgłasza błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, "predict FakeNet on MNIST")
    assert "undefined network 'FakeNet'" in _extract_error(excinfo), (
        f"Expected 'undefined network 'FakeNet'', got {_extract_error(excinfo)}"
    )


def test_summary_undefined_network(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Summary niezdefiniowanej sieci zgłasza błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, "summary FakeNet")
    assert "undefined network 'FakeNet'" in _extract_error(excinfo), (
        f"Expected 'undefined network 'FakeNet'', got {_extract_error(excinfo)}"
    )


def test_if_block_parses(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Blok warunkowy z gpu_available parsuje się poprawnie.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Net { layer: Dense(784, 10) }
    if gpu_available {
        save Net to "model_gpu.pth"
    }
    """
    _run(parser, compiler, code)
    assert "instructions" in compiler.parsed_config
    block = compiler.parsed_config["instructions"][-1]
    assert block["cmd_type"] == "if_block", f"Expected 'if_block', got {block['cmd_type']}"
    assert block["condition"]["type"] == "gpu_available", (
        f"Expected 'gpu_available', got {block['condition']['type']}"
    )


def test_if_elif_else_parses(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Pelny blok if/elif/else parsuje się poprawnie.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Net { layer: Dense(784, 10) }
    if gpu_available {
        save Net to "model_gpu.pth"
    } else if mps_available {
        save Net to "model_mps.pth"
    } else {
        save Net to "model_cpu.pth"
    }
    """
    _run(parser, compiler, code)
    block = compiler.parsed_config["instructions"][-1]
    assert block["condition"]["type"] == "gpu_available", (
        f"Expected 'gpu_available', got {block['condition']['type']}"
    )
    assert len(block["elif_clauses"]) == 1, (
        f"Expected 1 elif_clause, got {len(block['elif_clauses'])}"
    )
    assert block["elif_clauses"][0]["condition"]["type"] == "mps_available", (
        f"Expected 'mps_available', got {block['elif_clauses'][0]['condition']['type']}"
    )
    assert block["else_body"] is not None, f"Expected 'else_body' in {block}"


def test_unknown_dataset_errors(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Nieznany zbiór danych (ani torchvision, ani CSV) zgłasza błąd semantyczny.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    load_data NotADataset {
        batch_size: 32
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "Unknown dataset source" in _extract_error(excinfo), (
        f"Expected 'Unknown dataset source', got {_extract_error(excinfo)}"
    )


def test_repeat_with_unknown_var(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Użycie niezdefiniowanej zmiennej w 'repeat' zgłasza czytelny błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Net {
        repeat k times {
            layer: ReLU()
        }
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    error = _extract_error(excinfo)
    assert "Use of undefined variable 'k'" in error, (
        f"Expected 'Use of undefined variable 'k'', got {error}"
    )
    assert "repeat" in error, f"Expected 'repeat', got {error}"


def test_config_value_type_validation(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Parametr epochs musi być dodatnią liczbą całkowitą.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    train_config Bad {
        epochs: 3.5
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "'epochs' must be a positive integer" in _extract_error(excinfo), (
        f"Expected 'epochs' must be a positive integer', got {_extract_error(excinfo)}"
    )


def test_unknown_config_key(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Nieznany klucz w train_config zgłasza błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    train_config Bad {
        epochs: 1,
        nonsense_key: 0.5
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "Unknown config key" in _extract_error(excinfo), (
        f"Expected 'Unknown config key', got {_extract_error(excinfo)}"
    )


def test_invalid_task_value(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Nieprawidłowa wartość klucza task zgłasza błąd semantyczny.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    train_config Bad {
        task: "classification"
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "'task' must be 'multiclass', 'binary' or 'regression'" in _extract_error(excinfo), (
        f"Expected task validation error, got {_extract_error(excinfo)}"
    )


@pytest.mark.parametrize("task_value", ["multiclass", "binary", "regression"])
def test_valid_task_values(parser: Lark, compiler: NeuroLangCompiler, task_value: str) -> None:
    """
    Dozwolone wartości klucza task przechodzą walidację semantyczną.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
        task_value (str): Wartość task do zweryfikowania
    """
    code = f'''
    train_config Good {{
        task: "{task_value}"
    }}
    '''
    _run(parser, compiler, code)


def test_regression_rejects_classification_metric(
    parser: Lark, compiler: NeuroLangCompiler
) -> None:
    """
    Metryka klasyfikacyjna nie może być użyta z task='regression'.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network RegNet { layer: Dense(4, 1) }
    train_config Cfg {
        task: "regression",
        loss_function: MSELoss(),
        metrics: [Accuracy(task="multiclass", num_classes=2)]
    }
    load_data "data.csv" as Csv { target_column: "target" }
    train RegNet with Cfg on Csv
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "classification-only" in _extract_error(excinfo), (
        f"Expected regression/classification metric mismatch, got {_extract_error(excinfo)}"
    )


def test_multi_network_shapes_isolated(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Dwa bloki network zachowują własne wymiary niezależnie od siebie.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Alpha(1, 28, 28) {
        layer: Flatten(),
        layer: Dense(784, 32)
    }
    network Beta(3, 32, 32) {
        layer: Conv2D(3, 8, 3),
        layer: Flatten(),
        layer: Dense(7200, 10)
    }
    """
    _run(parser, compiler, code)
    alpha = compiler.parsed_networks["Alpha"]
    beta = compiler.parsed_networks["Beta"]
    assert alpha["first_input"] == (1, 1, 28, 28), (
        f"Expected (1, 1, 28, 28), got {alpha['first_input']}"
    )
    assert alpha["last_output"] == 32, f"Expected 32, got {alpha['last_output']}"
    assert beta["first_input"] == (1, 3, 32, 32), (
        f"Expected (1, 3, 32, 32), got {beta['first_input']}"
    )
    assert beta["last_output"] == 10, f"Expected 10, got {beta['last_output']}"


def test_network_arg_expression_evaluated(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Nagłówek network(H, W, C) z wyrażeniami jest ewaluowany przez visitor.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Expr(3, 16, 16) {
        layer: Conv2D(3, 8, 3, padding=1)
    }
    """
    _run(parser, compiler, code)
    net = compiler.parsed_networks["Expr"]
    assert net["first_input"] == (1, 3, 16, 16), (
        f"Expected (1, 3, 16, 16), got {net['first_input']}"
    )


def test_predict_on_unknown_source(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Predykcja na nieznanym źródle (nie-alias, nie-CSV) zgłasza błąd.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network Net { layer: Dense(10, 2) }
    predict Net on UnknownAlias
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "undefined data source 'UnknownAlias'" in _extract_error(excinfo), (
        f"Expected 'undefined data source 'UnknownAlias'', got {_extract_error(excinfo)}"
    )


def test_train_uses_referenced_config(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Walidacja metryk w train korzysta z konfiguracji wskazanej po "with", a nie ostatniej zdefiniowanej.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network NetA { layer: Dense(4, 2) }
    network NetB { layer: Dense(4, 3) }
    load_data "data.csv" as D { target_column: "label" }

    train_config CfgA {
        task: "multiclass",
        loss_function: CrossEntropyLoss(),
        metrics: [Accuracy(task="multiclass", num_classes=2)]
    }
    train_config CfgB {
        task: "multiclass",
        loss_function: CrossEntropyLoss(),
        metrics: [Accuracy(task="multiclass", num_classes=3)]
    }

    train NetA with CfgA on D
    """
    _run(parser, compiler, code)


def test_evaluate_predict_inherit_bound_config(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    evaluate/predict dziedziczą konfigurację powiązaną z wcześniejszym train dla tej samej sieci.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network NetA { layer: Dense(4, 2) }
    load_data "data.csv" as D { target_column: "label" }
    train_config CfgA {
        task: "multiclass",
        loss_function: CrossEntropyLoss(),
        metrics: [Accuracy(task="multiclass", num_classes=2)]
    }

    train NetA with CfgA on D
    evaluate NetA on D
    predict NetA on D
    """
    _run(parser, compiler, code)

    eval_instr = next(
        i for i in compiler.parsed_config["instructions"] if i["cmd_type"] == "evaluate"
    )
    pred_instr = next(
        i for i in compiler.parsed_config["instructions"] if i["cmd_type"] == "predict"
    )
    assert eval_instr.get("config") == "CfgA", (
        f"Expected evaluate config CfgA, got {eval_instr.get('config')}"
    )
    assert pred_instr.get("config") == "CfgA", (
        f"Expected predict config CfgA, got {pred_instr.get('config')}"
    )


def test_condition_boolean_literal_true(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """Literal true w warunku jest rozpoznawany jako cond_bool."""
    code = """
    network Net { layer: Dense(784, 10) }
    if true {
        save Net to "always.pth"
    }
    """
    _run(parser, compiler, code)
    block = compiler.parsed_config["instructions"][-1]
    assert block["condition"]["type"] == "bool"
    assert block["condition"]["value"] is True


def test_condition_boolean_literal_false(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """Literal false w warunku jest rozpoznawany jako cond_bool."""
    code = """
    network Net { layer: Dense(784, 10) }
    if false {
        save Net to "never.pth"
    }
    """
    _run(parser, compiler, code)
    block = compiler.parsed_config["instructions"][-1]
    assert block["condition"]["type"] == "bool"
    assert block["condition"]["value"] is False


def test_condition_not_operator(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """Operator 'not' tworzy cond_not z operandem wewnatrz."""
    code = """
    network Net { layer: Dense(784, 10) }
    if not gpu_available {
        save Net to "cpu.pth"
    }
    """
    _run(parser, compiler, code)
    cond = compiler.parsed_config["instructions"][-1]["condition"]
    assert cond["type"] == "not"
    assert cond["operand"]["type"] == "gpu_available"


def test_condition_and_or_operators(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """Operatory 'and' / 'or' tworza polaczone warunki."""
    code = """
    network Net { layer: Dense(784, 10) }
    if gpu_available and has_data {
        save Net to "a.pth"
    }
    if gpu_available or mps_available {
        save Net to "b.pth"
    }
    """
    _run(parser, compiler, code)
    and_block = compiler.parsed_config["instructions"][-2]
    or_block = compiler.parsed_config["instructions"][-1]
    assert and_block["condition"]["type"] == "and"
    assert len(and_block["condition"]["operands"]) == 2
    assert or_block["condition"]["type"] == "or"


def test_condition_precedence_not_over_and(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """'not' wiaze scislej niz 'and'."""
    code = """
    network Net { layer: Dense(784, 10) }
    if not gpu_available and has_data {
        save Net to "a.pth"
    }
    """
    _run(parser, compiler, code)
    cond = compiler.parsed_config["instructions"][-1]["condition"]
    assert cond["type"] == "and"
    assert cond["operands"][0]["type"] == "not"
    assert cond["operands"][1]["type"] == "has_data"


def test_condition_comparison_operators(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """Wszystkie operatory porownania sa rozpoznawane."""
    ops = ["==", "!=", "<", "<=", ">", ">="]
    for op in ops:
        local_parser = parser
        local_compiler = NeuroLangCompiler(config=compiler.config)
        code = f"""
        let x = 5
        network Net {{ layer: Dense(784, 10) }}
        if x {op} 3 {{
            save Net to "cmp.pth"
        }}
        """
        _run(local_parser, local_compiler, code)
        cond = local_compiler.parsed_config["instructions"][-1]["condition"]
        assert cond["type"] == "compare"
        assert cond["op"] == op


def test_condition_compare_with_expression(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """Porownanie moze uzywac wyrazen arytmetycznych po obu stronach."""
    code = """
    let x = 5
    let y = 2
    network Net { layer: Dense(784, 10) }
    if x + y >= 7 {
        save Net to "sum.pth"
    }
    """
    _run(parser, compiler, code)
    cond = compiler.parsed_config["instructions"][-1]["condition"]
    assert cond["type"] == "compare"
    assert cond["op"] == ">="
    assert cond["left"] == 7


def test_condition_grouping_with_parentheses(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """Nawiasy w warunkach zmieniaja precedencje."""
    code = """
    network Net { layer: Dense(784, 10) }
    if (gpu_available or mps_available) and has_data {
        save Net to "fast.pth"
    }
    """
    _run(parser, compiler, code)
    cond = compiler.parsed_config["instructions"][-1]["condition"]
    assert cond["type"] == "and"
    assert cond["operands"][0]["type"] == "or"


def test_condition_undefined_variable_in_compare(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """Porownanie z niezdefiniowana zmienna zglasza blad semantyczny."""
    code = """
    network Net { layer: Dense(784, 10) }
    if foo > 3 {
        save Net to "e.pth"
    }
    """
    with pytest.raises(VisitError) as excinfo:
        _run(parser, compiler, code)
    assert "Use of undefined variable 'foo'" in _extract_error(excinfo)
