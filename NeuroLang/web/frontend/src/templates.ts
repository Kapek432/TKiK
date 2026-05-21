/** Szablony bloków NeuroLang wstawiane z planera potoku. */

export const TEMPLATES: Record<string, string> = {
  load_data: `load_data MNIST {
    batch_size: 128,
    shuffle: true
}`,
  network: `network MyNetwork(1, 28, 28) {
    layer: Flatten(),
    layer: Dense(784, 128),
    layer: ReLU(),
    layer: Dense(128, 10)
}`,
  train_config: `train_config MyConfig {
    epochs: 5,
    learning_rate: 0.001,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}`,
  train: `train MyNetwork with MyConfig on MNIST`,
  evaluate: `evaluate MyNetwork on MNIST`,
  save: `save MyNetwork to "model.pth"`,
  if_block: `if gpu_available {
    train MyNetwork with MyConfig on MNIST using gpu
} else {
    train MyNetwork with MyConfig on MNIST using cpu
}`,
};

export const DEFAULT_SOURCE = `# NeuroLang Studio
# Wczytaj przykład z panelu po lewej lub wpisz kod poniżej

load_data MNIST {
    batch_size: 128,
    shuffle: true
}

network SimpleMLP(1, 28, 28) {
    layer: Flatten(),
    layer: Dense(784, 512),
    layer: ReLU(),
    layer: Dense(512, 10)
}

train_config BasicConfig {
    epochs: 5,
    learning_rate: 0.001,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

train SimpleMLP with BasicConfig on MNIST
`;
