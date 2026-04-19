# Przykład - wiele konfiguracji, train używa tej wskazanej po "with"

network NetA {
    layer: Dense(4, 2)
}

network NetB {
    layer: Dense(4, 3)
}

load_data "data/sample_data.csv" as D {
    batch_size: 4,
    shuffle: true,
    target_column: "label"
}

train_config CfgA {
    task: "multiclass",
    epochs: 2,
    optimizer: Adam(lr=0.01),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=2)]
}

train_config CfgB {
    task: "multiclass",
    epochs: 2,
    optimizer: Adam(lr=0.01),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=3)]
}

train NetA with CfgA on D
evaluate NetA on D
predict NetA on D
