# Sieć konwolucyjna (CNN) dla zbioru MNIST - automatyczne wyliczanie wymiarów

network CNN_MNIST(1, 28, 28) {
    layer: Conv2D(1, 32, 3, padding=1),
    layer: ReLU(),
    layer: MaxPool2D(2),
    
    layer: Conv2D(32, 64, 3, padding=1),
    layer: ReLU(),
    layer: MaxPool2D(2),
    
    layer: Flatten(),
    layer: Dense(3136, 128), # 3136 = 64 * 7 * 7
    layer: ReLU(),
    layer: Dense(128, 10)
}

load_data MNIST {
    batch_size: 64,
    shuffle: true
}

train_config CNN_Config {
    epochs: 2,
    optimizer: Adam(lr=0.001),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

train CNN_MNIST with CNN_Config on MNIST
save CNN_MNIST to "mnist_cnn.pth"
