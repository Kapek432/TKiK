# Wykorzystanie zmiennych, pętli repeat i wczytywania wag

let input_size = 784
let hidden_size = 256
let num_layers = 3

network AdvancedMLP(1, 28, 28) {
    layer: Flatten(),
    layer: Dense(input_size, hidden_size),
    
    repeat num_layers times {
        layer: ReLU(),
        layer: Dropout(0.3),
        layer: Dense(hidden_size, hidden_size)
    },
    
    layer: ReLU(),
    layer: Dense(hidden_size, 10)
}

load_data MNIST {
    batch_size: 128
}

train_config MyConfig {
    epochs: 5,
    learning_rate: 0.001,
    optimizer: Adam(),
    metrics: [Accuracy(task="multiclass", num_classes=10)]
}

# Opcjonalne wczytanie wag przed treningiem
load_model AdvancedMLP from "model_weights.pth"

train AdvancedMLP with MyConfig on MNIST
save AdvancedMLP to "final_model.pth"
