"""Testy integracyjne: pełna ścieżka od kodu NeuroLang do skryptu PyTorch."""

from lark import Lark

from src.codegen.generator import PyTorchGenerator
from src.semantic.transformer import NeuroLangCompiler
from src.semantic.visitor import NeuroLangVisitor


def _compile(parser: Lark, compiler: NeuroLangCompiler, code: str) -> str:
    """
    Pomocnicza funkcja do kompilacji kodu NeuroLang.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
        code (str): Kod NeuroLang

    Zwraca:
        str: Kod PyTorch
    """
    tree = parser.parse(code)
    NeuroLangVisitor(compiler).visit(tree)
    compiler.transform(tree)
    gen = PyTorchGenerator(compiler.parsed_config, compiler.components)
    return gen.generate()


def test_full_compilation_mnist(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Testuje pełną kompilację prostego modelu MNIST.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    load_data MNIST as D { batch_size: 32 }
    network Net { layer: Dense(784, 10) }
    train_config C { epochs: 1 }
    train Net with C on D
    """
    python_code = _compile(parser, compiler, code)
    assert "class Net(nn.Module):" in python_code, (
        f"Code does not contain class Net(nn.Module): {python_code}"
    )
    assert "torchvision.datasets.MNIST" in python_code
    assert "D = DataLoader(dataset, batch_size=32" in python_code, (
        f"Code does not contain D = DataLoader(dataset, batch_size=32: {python_code}"
    )


def test_full_compilation_csv(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Testuje pełną kompilację dla danych CSV.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    load_data "data.csv" as CsvData { target_column: "target" }
    network Net { layer: Dense(4, 2) }
    train_config C { epochs: 5 }
    train Net with C on CsvData
    """
    python_code = _compile(parser, compiler, code)
    assert "pd.read_csv('data.csv').dropna()" in python_code, (
        f"Code does not contain pd.read_csv('data.csv').dropna(): {python_code}"
    )
    assert "CsvData = DataLoader(dataset" in python_code, (
        f"Code does not contain CsvData = DataLoader(dataset: {python_code}"
    )


def test_repeat_loop_integration(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Testuje pętlę 'repeat' rozwijaną do wielu warstw w nn.Sequential.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    network RepeatNet {
        repeat 3 times {
            layer: Dense(10, 10),
            layer: ReLU()
        }
    }
    """
    python_code = _compile(parser, compiler, code)
    assert python_code.count("torch.nn.Linear(10, 10)") == 3, (
        f"Code does not contain torch.nn.Linear(10, 10): {python_code}"
    )
    assert python_code.count("torch.nn.ReLU()") == 3, (
        f"Code does not contain torch.nn.ReLU(): {python_code}"
    )


def test_full_compilation_compiles(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Testuje pełną kompilację i sprawdza, czy wygenerowany kod jest poprawnym programem Python bez SyntaxError.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    load_data MNIST as D { batch_size: 32 }
    network Net { layer: Dense(784, 10) }
    train_config C { epochs: 1, optimizer: Adam() }
    train Net with C on D using cpu
    save Net to "my_model.pth"
    print "it's working"
    summary Net
    """
    python_code = _compile(parser, compiler, code)
    compile(python_code, "<generated>", "exec"), f"Code does not compile: {python_code}"


def test_full_compilation_multiple_networks(parser: Lark, compiler: NeuroLangCompiler) -> None:
    """
    Testuje kompilację dwóch sieci w jednym pliku z osobnymi modelami.

    Argumenty:
        parser (Lark): Parser Lark
        compiler (NeuroLangCompiler): Compiler NeuroLang
    """
    code = """
    load_data MNIST as D { batch_size: 32 }

    network NetA { layer: Dense(784, 2) }
    network NetB { layer: Dense(784, 3) }

    train_config CfgA {
        task: "multiclass",
        epochs: 1,
        loss_function: CrossEntropyLoss(),
        metrics: [Accuracy(task="multiclass", num_classes=2)]
    }
    train_config CfgB {
        task: "multiclass",
        epochs: 1,
        loss_function: CrossEntropyLoss(),
        metrics: [Accuracy(task="multiclass", num_classes=3)]
    }

    train NetA with CfgA on D
    train NetB with CfgB on D
    """
    python_code = _compile(parser, compiler, code)
    assert "class NetA(nn.Module):" in python_code
    assert "class NetB(nn.Module):" in python_code
    assert "model_NetA = NetA().to(device)" in python_code
    assert "model_NetB = NetB().to(device)" in python_code
    assert "optimizer =" in python_code
    compile(python_code, "<generated>", "exec"), f"Code does not compile: {python_code}"
