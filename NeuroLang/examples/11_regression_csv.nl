# Przykład regresji na lokalnym pliku CSV

load_data "data/regression_sample_data.csv" as RegressionData {
    batch_size: 4,
    shuffle: true,
    target_column: "target"
}

network RegressionNet {
    layer: Dense(4, 16),
    layer: ReLU(),
    layer: Dense(16, 1)
}

train_config RegressionCfg {
    task: "regression",
    epochs: 10,
    optimizer: Adam(lr=0.01),
    loss_function: MSELoss(),
    metrics: [MeanSquaredError()]
}

train RegressionNet with RegressionCfg on RegressionData
evaluate RegressionNet on RegressionData
predict RegressionNet on RegressionData
