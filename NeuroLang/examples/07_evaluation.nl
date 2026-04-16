# Ewaluacja wytrenowanego modelu na zbiorze danych

network SimpleNet {
    layer: Dense(784, 128),
    layer: ReLU(),
    layer: Dense(128, 10)
}

load_data MNIST {
    batch_size: 64
}

train_config Cfg {
    epochs: 3,
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

train SimpleNet with Cfg on MNIST
evaluate SimpleNet on MNIST
summary SimpleNet
save SimpleNet to "model_eval.pth"
