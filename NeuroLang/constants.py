"""
Stałe konfiguracyjne definiujące domyślne ścieżki i parametry.
"""

# Pliki wejściowe i definicje
GRAMMAR_FILE = "neurolang.lark"
COMPONENTS_FILE = "components.json"
DATASETS_FILE = "datasets.json"

# Domyślne wartości dla CLI
DEFAULT_INPUT = "examples/01_mnist_basic.nl"
DEFAULT_OUTPUT = "generated_script.py"
MODEL_GRAPH_FILE = "model_graph.png"
MODEL_GRAPH_BASENAME = "model_graph"
SOURCE_FILE_EXAMPLE = "examples/01_mnist_basic.nl"

# Ustawienia domyślne architektury
DEFAULT_IMAGE_SIZE = 28
DEFAULT_CHANNELS = 1
DEFAULT_DROPOUT_P = 0.5
DEFAULT_MOMENTUM = 0.9

# Ustawienia treningu
DEFAULT_LEARNING_RATE = 0.001
DEFAULT_EPOCHS = 10
DEFAULT_BATCH_SIZE = 32
DEFAULT_DATA_DIR = "./data"

# Znaki specjalne i formatowanie
AST_SEPARATOR = "-" * 50
ERROR_SEPARATOR = "-" * 30
