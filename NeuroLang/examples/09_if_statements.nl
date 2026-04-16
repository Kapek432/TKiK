# Różne zastosowania bloków warunkowych (if/elif/else)

network ConditionNet(1, 28, 28) {
    layer: Conv2D(1, 16, 3, padding=1),
    layer: ReLU(),
    layer: MaxPool2D(2),
    layer: Flatten(),
    layer: Dense(3136, 10)
}

load_data MNIST as MyData {
    batch_size: 64,
    shuffle: true
}

let USE_FANCY_METRICS = 1

train_config BasicConfig {
    epochs: 1,
    learning_rate: 0.01,
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

# 1. Podsumowanie struktury
summary ConditionNet

# 2. Reagowanie na system
if gpu_available {
    print "NVIDIA detected"
    train ConditionNet with BasicConfig on MyData
    save ConditionNet to "gpu_model_weights.pth"
    export ConditionNet to "gpu_model.onnx"

} else if mps_available {
    print "Apple Silicon detected"
    train ConditionNet with BasicConfig on MyData using mps
    save ConditionNet to "apple_model_weights.pth"

} else {
    print "CPU only"
    train ConditionNet with BasicConfig on MyData using cpu
    save ConditionNet to "cpu_model_weights.pth"
}

# 3. Zastosowanie warunków na zmienną
if USE_FANCY_METRICS {
    print "USE_FANCY_METRICS is enabled. Evaluation with additional logs:"
    evaluate ConditionNet on MyData
}

# 4. Predykcja jeśli dane są w pamięci
if has_data {
    print "Checking samples on the dataset:"
    predict ConditionNet on MyData
}
