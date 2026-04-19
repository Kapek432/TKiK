# Zaawansowany model dla kolorowych obrazów CIFAR10 (3 kanały, 32x32)

network CIFAR_Net(3, 32, 32) {
    layer: Conv2D(3, 32, 3, padding=1),
    layer: ReLU(),
    layer: Conv2D(32, 32, 3, padding=1),
    layer: ReLU(),
    layer: MaxPool2D(2),
    
    layer: Conv2D(32, 64, 3, padding=1),
    layer: ReLU(),
    layer: MaxPool2D(2),
    
    layer: Flatten(),
    layer: Dense(4096, 512),
    layer: ReLU(),
    layer: Dense(512, 10)
}

load_data CIFAR10 {
    batch_size: 64,
    shuffle: true
}

train_config CIFAR_Config {
    epochs: 5,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

train CIFAR_Net with CIFAR_Config on CIFAR10
