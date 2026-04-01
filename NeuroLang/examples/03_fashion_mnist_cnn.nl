# Ten sam model CNN co w przykładzie 02_mnist_cnn.nl, ale dla zbioru FashionMNIST

network FashionNet(1, 28, 28) {
    layer: Conv2D(1, 16, 3, padding=1),
    layer: ReLU(),
    layer: MaxPool2D(2),
    layer: Flatten(),
    layer: Dense(3136, 10)
}

load_data FashionMNIST {
    batch_size: 64,
    shuffle: true
}

train_config FashionConfig {
    epochs: 1,
    optimizer: Adam(lr=0.001),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

train FashionNet with FashionConfig on FashionMNIST
