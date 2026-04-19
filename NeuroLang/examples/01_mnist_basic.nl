# Prosty przykład sieci MLP dla zbioru MNIST

# 1. Konfiguracja danych
load_data MNIST {
    batch_size: 128,
    shuffle: true
}

# 2. Architektura sieci
network SimpleMLP(1, 28, 28) {
    layer: Flatten(),
    layer: Dense(784, 512),
    layer: ReLU(),
    layer: Dropout(0.2),
    layer: Dense(512, 10)
}

# 3. Parametry treningu
train_config BasicConfig {
    epochs: 5,
    learning_rate: 0.001,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

# 4. Uruchomienie
train SimpleMLP with BasicConfig on MNIST
save SimpleMLP to "mnist_mlp.pth"
