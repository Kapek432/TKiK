# Przykład błędu: druga sieć ma inny wymiar wyjściowy niż metryka w train_config

network NetA {
    layer: Dense(4, 2)
}

network NetB {
    layer: Dense(4, 3)
}

load_data "data/sample_data.csv" as D {
    batch_size: 4,
    target_column: "label"
}

train_config CfgA {
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=2)]
}

train_config CfgB {
    task: "multiclass",
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=3)]
}

train NetA with CfgA on D
train NetB with CfgA on D
