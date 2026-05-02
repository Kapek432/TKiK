"""Generowanie bloku importów wynikowego skryptu."""

from src.codegen.indent import CodeBuffer


def generate_imports(buffer: CodeBuffer, visualize: bool) -> None:
    """
    Dodaje importy bibliotek potrzebnych do uruchomienia wygenerowanego modelu.

    Argumenty:
        buffer (CodeBuffer): Bufor do którego doklejamy kod
        visualize (bool): Czy dołączyć import torchview
    """
    buffer.add("import os")
    buffer.add("import torch")
    buffer.add("import torch.nn as nn")
    buffer.add("import torch.optim as optim")
    buffer.add("from torch.utils.data import DataLoader, TensorDataset")
    buffer.add("import torchvision")
    buffer.add("import torchvision.transforms as transforms")
    buffer.add("import torchmetrics")
    buffer.add("import pandas as pd")
    buffer.add("from tqdm import tqdm")
    if visualize:
        buffer.add("from torchview import draw_graph")
    buffer.add("")
