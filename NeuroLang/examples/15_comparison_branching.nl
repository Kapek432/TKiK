# Użycie operatorów porównania (==, !=, <, <=, >, >=) w blokach if.

let MODE = 2
let EPOCH_BUDGET = 5

network Net(1, 28, 28) {
    layer: Flatten(),
    layer: Dense(784, 64),
    layer: ReLU(),
    layer: Dense(64, 10)
}

load_data MNIST as MyData {
    batch_size: 128,
    shuffle: true
}

train_config QuickConfig {
    epochs: 1,
    learning_rate: 0.01,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

train_config StandardConfig {
    epochs: 3,
    learning_rate: 0.001,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

train_config ExhaustiveConfig {
    epochs: 6,
    learning_rate: 0.0005,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

if MODE == 1 {
    print "Mode 1 - quick test"
    train Net with QuickConfig on MyData
} else if MODE == 2 {
    print "Mode 2 - standard training"
    train Net with StandardConfig on MyData
} else {
    print "Mode > 2 - longer training"
    train Net with ExhaustiveConfig on MyData
}

if EPOCH_BUDGET >= 5 {
    print "Large budget - exporting model"
    export Net to "model_full.onnx"
}

if EPOCH_BUDGET < 3 {
    print "Limited budget - only saving weights"
    save Net to "model_weights.pth"
}

if EPOCH_BUDGET > 0 and MODE != 0 {
    print "Training started - checking predictions"
    if has_data {
        predict Net on MyData
    }
}
