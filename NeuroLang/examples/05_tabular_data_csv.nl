# Wczytanie danych z lokalnego pliku CSV i trening prostej sieci regresyjnej/klasyfikacyjnej

load_data "data/sample_data.csv" as MojeDane {
    batch_size: 4,
    shuffle: true,
    target_column: "label"
}

network TabularNet {
    layer: Dense(4, 16),
    layer: ReLU(),
    layer: Dense(16, 3)
}

train_config CSV_Config {
    epochs: 10,
    optimizer: Adam(lr=0.01),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=3)]
}

train TabularNet with CSV_Config on MojeDane
