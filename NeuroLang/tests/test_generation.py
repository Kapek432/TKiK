"""Testy generowania kodu PyTorch."""

from typing import Any, Optional

from src.codegen.generator import PyTorchGenerator


def _config(
    *,
    networks: Optional[dict[str, dict[str, Any]]] = None,
    configs: Optional[dict[str, dict[str, Any]]] = None,
    data_sources: Optional[dict[str, dict[str, Any]]] = None,
    instructions: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Buduje słownik parsed_config w nowym layoucie wieloseciowym/wielokonfiguracyjnym."""
    return {
        "networks": networks or {},
        "configs": configs or {},
        "data_sources": data_sources or {},
        "instructions": instructions or [],
    }


def test_pytorch_generator_imports():
    """
    Sprawdza, czy kod zawiera importy niezbędnych bibliotek.
    """
    gen = PyTorchGenerator({}, {})
    code = gen.generate()
    assert "import torch" in code, f"Code does not contain import torch: {code}"
    assert "import pandas as pd" in code, f"Code does not contain import pandas as pd: {code}"


def test_csv_loading_generation():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla plików CSV.
    """
    config = _config(
        networks={"Simple": {"name": "Simple", "layers": []}},
        configs={"Cfg": {"name": "Cfg", "params": {}}},
        data_sources={
            "MyData": {
                "source": "data.csv",
                "alias": "MyData",
                "params": {"target_column": "label", "batch_size": 16},
            }
        },
        instructions=[
            {
                "cmd_type": "train",
                "network": "Simple",
                "config": "Cfg",
                "data": "MyData",
                "device": "cpu",
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "pd.read_csv('data.csv').dropna()" in code, (
        f"Code does not contain pd.read_csv('data.csv').dropna(): {code}"
    )
    assert "df.drop('label', axis=1)" in code, (
        f"Code does not contain df.drop('label', axis=1): {code}"
    )
    assert "MyData = DataLoader(dataset, batch_size=16" in code, (
        f"Code does not contain MyData = DataLoader(dataset, batch_size=16: {code}"
    )


def test_mnist_loading_generation():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla zbioru MNIST.
    """
    config = _config(
        networks={"Simple": {"name": "Simple", "layers": []}},
        configs={"Cfg": {"name": "Cfg", "params": {}}},
        data_sources={"MNIST": {"source": "MNIST", "alias": "MNIST", "params": {"batch_size": 32}}},
        instructions=[
            {
                "cmd_type": "train",
                "network": "Simple",
                "config": "Cfg",
                "data": "MNIST",
                "device": "cpu",
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "torchvision.datasets.MNIST" in code, (
        f"Code does not contain torchvision.datasets.MNIST: {code}"
    )
    assert "DataLoader(dataset, batch_size=32" in code, (
        f"Code does not contain DataLoader(dataset, batch_size=32: {code}"
    )


def test_model_class_generation():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla klasy modelu nn.Module.
    """
    network = {
        "name": "MyNet",
        "layers": [
            {
                "name": "Dense",
                "args": [
                    {"type": "positional", "value": 10},
                    {"type": "positional", "value": 20},
                ],
            },
            {"name": "ReLU", "args": []},
        ],
    }
    components = {
        "Dense": {"pytorch_name": "nn.Linear"},
        "ReLU": {"pytorch_name": "nn.ReLU"},
    }
    config = _config(networks={"MyNet": network})
    gen = PyTorchGenerator(config, components)
    code = gen.generate()
    assert "class MyNet(nn.Module):" in code, (
        f"Code does not contain class MyNet(nn.Module): {code}"
    )
    assert "nn.Linear(10, 20)," in code, f"Code does not contain nn.Linear(10, 20): {code}"
    assert "nn.ReLU()," in code, f"Code does not contain nn.ReLU(): {code}"


def test_complex_layers_generation():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla BatchNorm, Dropout i Flatten.
    """
    network = {
        "name": "ComplexNet",
        "layers": [
            {"name": "BatchNorm2D", "args": [{"type": "positional", "value": 32}]},
            {
                "name": "Dropout",
                "args": [{"type": "keyword", "name": "p", "value": 0.3}],
            },
            {"name": "Flatten", "args": []},
        ],
    }
    components = {
        "BatchNorm2D": {"pytorch_name": "nn.BatchNorm2d"},
        "Dropout": {"pytorch_name": "nn.Dropout"},
        "Flatten": {"pytorch_name": "nn.Flatten"},
    }
    config = _config(networks={"ComplexNet": network})
    gen = PyTorchGenerator(config, components)
    code = gen.generate()
    assert "nn.BatchNorm2d(32)," in code, f"Code does not contain nn.BatchNorm2d(32): {code}"
    assert "nn.Dropout(p=0.3)," in code, f"Code does not contain nn.Dropout(p=0.3): {code}"
    assert "nn.Flatten()," in code, f"Code does not contain nn.Flatten(): {code}"


def test_training_config_generation():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla parametrów treningu.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        configs={
            "Cfg": {
                "name": "Cfg",
                "params": {
                    "optimizer": {"name": "Adam", "args": []},
                    "loss_function": {"name": "CrossEntropyLoss", "args": []},
                    "learning_rate": 0.005,
                },
            }
        },
        instructions=[
            {
                "cmd_type": "train",
                "network": "Net",
                "config": "Cfg",
                "data": "D",
                "device": "cpu",
            }
        ],
    )
    components = {
        "Adam": {"pytorch_name": "optim.Adam"},
        "CrossEntropyLoss": {"pytorch_name": "nn.CrossEntropyLoss"},
    }
    gen = PyTorchGenerator(config, components)
    code = gen.generate()
    assert "optim.Adam(model.parameters(), lr=0.005)" in code, (
        f"Code does not contain optim.Adam(model.parameters(), lr=0.005): {code}"
    )
    assert "nn.CrossEntropyLoss()" in code, f"Code does not contain nn.CrossEntropyLoss(): {code}"


def test_evaluate_generation():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla pętli ewaluacyjnej.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": [], "first_input": (1, 784)}},
        configs={"Cfg": {"name": "Cfg", "params": {"metrics": []}}},
        instructions=[{"cmd_type": "evaluate", "network": "Net", "config": "Cfg", "data": "MNIST"}],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "model.eval()" in code, f"Code does not contain model.eval(): {code}"
    assert "torch.no_grad()" in code, f"Code does not contain torch.no_grad(): {code}"
    assert "eval_loss" in code, f"Code does not contain eval_loss: {code}"


def test_export_generation():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla eksportu ONNX.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": [], "first_input": (1, 784)}},
        instructions=[{"cmd_type": "export", "network": "Net", "filepath": "model.onnx"}],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "torch.onnx.export" in code, f"Code does not contain torch.onnx.export(): {code}"
    assert "'model.onnx'" in code, f"Code does not contain 'model.onnx': {code}"


def test_summary_generation_emits_name():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla polecenia summary.
    """
    config = _config(
        networks={"TestNet": {"name": "TestNet", "layers": []}},
        instructions=[{"cmd_type": "summary", "network": "TestNet"}],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "'TestNet'" in code, f"Code does not contain 'TestNet': {code}"
    assert "print(model)" in code, f"Code does not contain print(model): {code}"
    assert "parameter" in code.lower(), f"Code does not contain parameter: {code}"


def test_print_string_generation():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla instrukcji print z napisem.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        instructions=[{"cmd_type": "print", "subtype": "string", "value": "Hello NeuroLang!"}],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "'Hello NeuroLang!'" in code, f"Code does not contain 'Hello NeuroLang!': {code}"


def test_print_string_escapes_apostrophe():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla apostrofów w literalach.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        instructions=[{"cmd_type": "print", "subtype": "string", "value": "it's ok"}],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    compile(code, "<generated>", "exec")
    assert "it's ok" in code, f"Code does not contain it's ok: {code}"


def test_predict_generation_datasource():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla predykcji na aliasie danych.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": [], "first_input": (1, 784)}},
        instructions=[
            {
                "cmd_type": "predict",
                "network": "Net",
                "source": "MNIST",
                "is_path": False,
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "model.eval()" in code, f"Code does not contain model.eval(): {code}"
    assert "next(iter(MNIST))" in code, f"Code does not contain next(iter(MNIST)): {code}"


def test_predict_generation_csv_path():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla predykcji z pliku CSV.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": [], "first_input": (1, 4)}},
        instructions=[
            {
                "cmd_type": "predict",
                "network": "Net",
                "source": "sample.csv",
                "is_path": True,
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "pd.read_csv('sample.csv')" in code, (
        f"Code does not contain pd.read_csv('sample.csv'): {code}"
    )
    assert "next(iter(" not in code, f"Code does not contain next(iter(: {code}"


def test_predict_generation_binary_task_uses_sigmoid_threshold():
    """
    Sprawdza, czy predykcja binarna używa sigmoid oraz progu 0.5.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": [], "first_input": (1, 4)}},
        configs={
            "Cfg": {
                "name": "Cfg",
                "params": {
                    "task": "binary",
                    "loss_function": {"name": "BCEWithLogitsLoss", "args": []},
                },
            }
        },
        instructions=[
            {
                "cmd_type": "predict",
                "network": "Net",
                "config": "Cfg",
                "source": "sample.csv",
                "is_path": True,
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "probs = torch.sigmoid" in code, f"Code does not contain sigmoid: {code}"
    assert "predicted = (probs >= 0.5).long()" in code, (
        f"Code does not contain binary thresholding: {code}"
    )


def test_predict_generation_regression_task_avoids_argmax():
    """
    Sprawdza, czy predykcja regresyjna nie używa argmax.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": [], "first_input": (1, 4)}},
        configs={
            "Cfg": {
                "name": "Cfg",
                "params": {
                    "task": "regression",
                    "loss_function": {"name": "MSELoss", "args": []},
                },
            }
        },
        instructions=[
            {
                "cmd_type": "predict",
                "network": "Net",
                "config": "Cfg",
                "source": "sample.csv",
                "is_path": True,
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "torch.max(outputs, 1)" not in code, f"Code contains multiclass argmax: {code}"


def test_device_propagation_mps():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla MPS.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        configs={"C": {"name": "C", "params": {"epochs": 1}}},
        instructions=[
            {
                "cmd_type": "train",
                "network": "Net",
                "config": "C",
                "data": "D",
                "device": "mps",
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "torch.device('mps'" in code, f"Code does not contain torch.device('mps': {code}"


def test_device_propagation_gpu():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla GPU.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        configs={"C": {"name": "C", "params": {"epochs": 1}}},
        instructions=[
            {
                "cmd_type": "train",
                "network": "Net",
                "config": "C",
                "data": "D",
                "device": "gpu",
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "torch.device('cuda'" in code, f"Code does not contain torch.device('cuda': {code}"


def test_train_uses_instruction_specific_config_generation():
    """
    Sprawdza, czy generator dla train używa konfiguracji wskazanej przez instrukcję.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        configs={
            "CfgA": {
                "name": "CfgA",
                "params": {
                    "optimizer": {"name": "Adam", "args": []},
                    "loss_function": {"name": "CrossEntropyLoss", "args": []},
                    "learning_rate": 0.005,
                },
            },
            "CfgB": {
                "name": "CfgB",
                "params": {
                    "optimizer": {"name": "Adam", "args": []},
                    "loss_function": {"name": "CrossEntropyLoss", "args": []},
                    "learning_rate": 0.02,
                },
            },
        },
        instructions=[
            {
                "cmd_type": "train",
                "network": "Net",
                "config": "CfgA",
                "data": "D",
                "device": "cpu",
            }
        ],
    )
    components = {
        "Adam": {"pytorch_name": "optim.Adam"},
        "CrossEntropyLoss": {"pytorch_name": "nn.CrossEntropyLoss"},
    }
    gen = PyTorchGenerator(config, components)
    code = gen.generate()
    assert "optim.Adam(model.parameters(), lr=0.005)" in code, (
        f"Code does not use instruction-selected config learning rate: {code}"
    )
    assert "optim.Adam(model.parameters(), lr=0.02)" not in code, (
        f"Code unexpectedly used fallback/global config: {code}"
    )


def test_train_loads_instruction_data_alias_generation():
    """
    Sprawdza, czy generator ładuje alias danych użyty w instrukcji train.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        configs={
            "Cfg": {
                "name": "Cfg",
                "params": {
                    "optimizer": {"name": "Adam", "args": []},
                    "loss_function": {"name": "CrossEntropyLoss", "args": []},
                    "learning_rate": 0.001,
                },
            }
        },
        data_sources={
            "D": {
                "source": "data/sample_data.csv",
                "alias": "D",
                "params": {"target_column": "label", "batch_size": 16},
            },
            "Other": {
                "source": "data/other.csv",
                "alias": "Other",
                "params": {"target_column": "label", "batch_size": 8},
            },
        },
        instructions=[
            {
                "cmd_type": "train",
                "network": "Net",
                "config": "Cfg",
                "data": "D",
                "device": "cpu",
            }
        ],
    )
    components = {
        "Adam": {"pytorch_name": "optim.Adam"},
        "CrossEntropyLoss": {"pytorch_name": "nn.CrossEntropyLoss"},
    }
    gen = PyTorchGenerator(config, components)
    code = gen.generate()
    assert "pd.read_csv('data/sample_data.csv').dropna()" in code, (
        f"Code does not load instruction data alias source: {code}"
    )
    assert "D = DataLoader(dataset, batch_size=16" in code, (
        f"Code does not initialize instruction alias D: {code}"
    )


def test_has_data_respects_alias():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla warunku has_data.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        data_sources={
            "MyData": {"source": "MNIST", "alias": "MyData", "params": {"batch_size": 32}},
        },
        instructions=[
            {
                "cmd_type": "if_block",
                "condition": {"type": "has_data"},
                "body": [{"cmd_type": "print", "subtype": "string", "value": "ok"}],
                "elif_clauses": [],
                "else_body": None,
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "MyData is not None" in code, f"Code does not contain MyData is not None: {code}"


def test_string_variable_is_quoted():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla zmiennej string.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        instructions=[
            {
                "cmd_type": "var_decl",
                "name": "msg",
                "value": "hello",
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "msg = 'hello'" in code, f"Code does not contain msg = 'hello': {code}"


def test_regression_csv_uses_float_dtype():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla dtype=torch.float32 i dtype=torch.long.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        configs={
            "C": {
                "name": "C",
                "params": {
                    "loss_function": {"name": "MSELoss", "args": []},
                },
            }
        },
        data_sources={
            "CsvData": {
                "source": "data.csv",
                "alias": "CsvData",
                "params": {"target_column": "y"},
            }
        },
        instructions=[
            {
                "cmd_type": "train",
                "network": "Net",
                "config": "C",
                "data": "CsvData",
                "device": "cpu",
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "dtype=torch.float32" in code, f"Code does not contain dtype=torch.float32: {code}"
    assert "dtype=torch.long" not in code.split("y = torch.tensor")[1].split("\n")[0], (
        f"Code does not contain dtype=torch.long: {code}"
    )


def test_predicted_aliases_initialized_none():
    """
    Sprawdza, czy kod zawiera poprawne generowanie kodu dla regresji.
    """
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        data_sources={
            "MyData": {"source": "MNIST", "alias": "MyData", "params": {}},
        },
    )
    gen = PyTorchGenerator(config, {})
    code = gen.generate()
    assert "MyData = None" in code, f"Code does not contain MyData = None: {code}"


def _cond_gen_code(condition: dict) -> str:
    """Pomocniczo generuje skrypt z pojedynczym if-blokiem o zadanym warunku."""
    config = _config(
        networks={"Net": {"name": "Net", "layers": []}},
        instructions=[
            {
                "cmd_type": "if_block",
                "condition": condition,
                "body": [{"cmd_type": "print", "subtype": "string", "value": "hit"}],
                "elif_clauses": [],
                "else_body": None,
            }
        ],
    )
    gen = PyTorchGenerator(config, {})
    return gen.generate()


def test_condition_bool_true_generates_true_literal():
    """Literal 'true' tlumaczy sie na 'if True:'."""
    code = _cond_gen_code({"type": "bool", "value": True})
    assert "if True:" in code, f"Expected 'if True:' in code: {code}"


def test_condition_bool_false_generates_false_literal():
    """Literal 'false' tlumaczy sie na 'if False:'."""
    code = _cond_gen_code({"type": "bool", "value": False})
    assert "if False:" in code, f"Expected 'if False:' in code: {code}"


def test_condition_not_generates_negation():
    """'not gpu_available' tlumaczy sie na '(not torch.cuda.is_available())'."""
    code = _cond_gen_code({"type": "not", "operand": {"type": "gpu_available"}})
    assert "(not torch.cuda.is_available())" in code, f"Expected negation in code: {code}"


def test_condition_and_generates_conjunction():
    """'gpu_available and mps_available' tworzy koniunkcje."""
    code = _cond_gen_code(
        {
            "type": "and",
            "operands": [{"type": "gpu_available"}, {"type": "mps_available"}],
        }
    )
    assert "torch.cuda.is_available()" in code
    assert "torch.backends.mps.is_available()" in code
    assert " and " in code.split("if ")[1]


def test_condition_or_generates_disjunction():
    """'gpu_available or mps_available' tworzy alternatywe."""
    code = _cond_gen_code(
        {
            "type": "or",
            "operands": [{"type": "gpu_available"}, {"type": "mps_available"}],
        }
    )
    assert " or " in code.split("if ")[1]


def test_condition_compare_generates_comparison():
    """Warunek compare tlumaczy sie na operator porownania Pythona."""
    code = _cond_gen_code({"type": "compare", "op": ">=", "left": 5, "right": 3})
    assert "(5 >= 3)" in code, f"Expected '(5 >= 3)' in code: {code}"


def test_condition_compare_equal_operator():
    """Operator '==' pojawia sie w wygenerowanym kodzie."""
    code = _cond_gen_code({"type": "compare", "op": "==", "left": 10, "right": 10})
    assert "(10 == 10)" in code, f"Expected '(10 == 10)' in code: {code}"
