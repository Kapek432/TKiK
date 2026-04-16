# Pełny pipeline demonstrujący wszystkie nowe instrukcje

let num_classes = 10

# Blok warunkowy z else if / else
if gpu_available {
    print "GPU is available"
} else if mps_available {
    print "MPS is available"
} else {
    print "Using CPU"
}

network MyModel {
    layer: Dense(784, 256),
    layer: ReLU(),
    layer: Dropout(0.3),
    layer: Dense(256, num_classes)
}

load_data MNIST {
    batch_size: 32
}

train_config Cfg {
    epochs: 5,
    optimizer: Adam(),
    loss_function: CrossEntropyLoss(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

# Wypisywanie informacji
print "Pipeline starting..."
summary MyModel

# Trening
train MyModel with Cfg on MNIST

# Ewaluacja po treningu
evaluate MyModel on MNIST

# Predykcja na zbiorze danych
predict MyModel on MNIST

# Informacja końcowa
print "Pipeline finished"

# Zapis i eksport modelu
save MyModel to "my_model.pth"
export MyModel to "my_model.onnx"
