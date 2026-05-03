"""Testy interfejsu wiersza poleceń."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.cli.compile import main


def test_cli_help() -> None:
    """
    Sprawdza, czy komenda --help wyświetla pomoc i kończy działanie z kodem 0.
    """
    with patch("sys.argv", ["neurolang", "--help"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0, f"Error code is not 0: {exc.value.code}"


def test_cli_output_file_creation(tmp_path: Path) -> None:
    """
    Sprawdza, czy kompilator tworzy plik .py na podstawie pliku .nl oraz czy plik istnieje i zawiera klasę T(nn.Module).

    Argumenty:
        tmp_path (Path): Ścieżka do pliku tymczasowego
    """
    input_file = tmp_path / "test.nl"
    input_file.write_text("network T { layer: ReLU() }")
    output_file = tmp_path / "out.py"

    with patch("sys.argv", ["neurolang", "-i", str(input_file), "-o", str(output_file)]):
        main()

    assert output_file.exists(), f"Output file does not exist: {output_file}"
    assert "class T(nn.Module):" in output_file.read_text(), (
        f"Output file does not contain class T(nn.Module): {output_file.read_text()}"
    )


@patch("subprocess.run")
def test_cli_run_flag(mock_run: Mock, tmp_path: Path) -> None:
    """
    Sprawdza, czy flaga --run uruchamia wygenerowany skrypt.

    Argumenty:
        mock_run (Mock): Mock subprocess.run
        tmp_path (Path): Ścieżka do pliku tymczasowego
    """
    input_file = tmp_path / "test.nl"
    input_file.write_text("network T { layer: ReLU() }")
    output_file = tmp_path / "out.py"

    with patch("sys.argv", ["neurolang", "-i", str(input_file), "-o", str(output_file), "--run"]):
        main()

    assert mock_run.called, f"Subprocess was not called: {mock_run.call_args}"
    args, _ = mock_run.call_args
    assert str(output_file) in args[0], f"Output file was not passed to subprocess: {args[0]}"


def test_cli_visualize_flag(tmp_path: Path) -> None:
    """
    Sprawdza, czy flaga --visualize dodaje kod "draw_graph" i nazwę pliku grafu.

    Argumenty:
        tmp_path (Path): Ścieżka do pliku tymczasowego
    """
    input_file = tmp_path / "test.nl"
    input_file.write_text("network T { layer: ReLU() }")
    output_file = tmp_path / "out.py"

    with patch(
        "sys.argv",
        ["neurolang", "-i", str(input_file), "-o", str(output_file), "--visualize"],
    ):
        main()

    assert output_file.exists(), f"Output file does not exist: {output_file}"
    content = output_file.read_text()
    assert "draw_graph(model" in content, (
        f"Output file does not contain draw_graph(model): {content}"
    )
    assert "model_graph" in content, f"Output file does not contain model_graph: {content}"
