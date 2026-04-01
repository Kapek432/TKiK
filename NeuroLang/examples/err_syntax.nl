# Przykład z błędem składniowym (brak nawiasu domykającego)
network SyntaxError {
    layer: Dense(784, 10
}

train_config C { epochs: 1 }
load_data MNIST { batch_size: 32 }
train SyntaxError with C on MNIST
