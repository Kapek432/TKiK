# Zaawansowane warunki: operatory logiczne (not / and / or), literały true/false oraz grupowanie nawiasami. 

network ClassifierNet(1, 28, 28) {
    layer: Conv2D(1, 32, 3, padding=1),
    layer: ReLU(),
    layer: MaxPool2D(2),
    layer: Flatten(),
    layer: Dense(6272, 128),
    layer: ReLU(),
    layer: Dense(128, 10)
}

load_data MNIST as MyData {
    batch_size: 64,
    shuffle: true
}

train_config FastConfig {
    epochs: 1,
    learning_rate: 0.01,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

train_config SlowConfig {
    epochs: 3,
    learning_rate: 0.001,
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

let EXPORT_ENABLED = true

if (gpu_available or mps_available) and has_data {
    print "Accelerator detected - using FastConfig"
    train ClassifierNet with FastConfig on MyData
} else {
    print "No accelerator - using SlowConfig on CPU"
    train ClassifierNet with SlowConfig on MyData using cpu
}

if not gpu_available and not mps_available {
    print "Saving version for CPU only"
    save ClassifierNet to "model_cpu.pth"
}

if true {
    summary ClassifierNet
}

if false {
    print "This text will not be printed"
}

if EXPORT_ENABLED and not (gpu_available and mps_available) {
    print "Exporting to ONNX"
    export ClassifierNet to "model.onnx"
}
