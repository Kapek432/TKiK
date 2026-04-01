# Przykład z błędem parametru Dropout (p=1.5, dopuszczalne [0, 1])
network DropoutError {
    layer: Dense(784, 128),
    layer: Dropout(1.5),
    layer: Dense(128, 10)
}

train_config C { epochs: 1 }
load_data MNIST { batch_size: 32 }
train DropoutError with C on MNIST
