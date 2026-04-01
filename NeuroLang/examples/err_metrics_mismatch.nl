# Przykład z błędem niezgodności metryk (num_classes=5 w sieci na MNIST/10 wyjść)
network Net10 {
    layer: Dense(784, 128),
    layer: Dense(128, 10)
}

train_config Config5 {
    metrics: [Accuracy(task="multiclass", num_classes=5)]
}

load_data MNIST { batch_size: 32 }
train Net10 with Config5 on MNIST
