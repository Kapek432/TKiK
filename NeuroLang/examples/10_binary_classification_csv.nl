# Przykład klasyfikacji binarnej na lokalnym pliku CSV

load_data "data/binary_sample_data.csv" as BinaryData {
    batch_size: 4,
    shuffle: true,
    target_column: "label"
}

network BinaryNet {
    layer: Dense(4, 8),
    layer: ReLU(),
    layer: Dense(8, 1)
}

train_config BinaryCfg {
    task: "binary",
    epochs: 8,
    optimizer: Adam(lr=0.01),
    loss_function: BCEWithLogitsLoss(),
    metrics: [Accuracy(task="binary")]
}

train BinaryNet with BinaryCfg on BinaryData
evaluate BinaryNet on BinaryData
predict BinaryNet on BinaryData
