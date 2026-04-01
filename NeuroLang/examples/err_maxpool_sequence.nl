# Przykład z błędem sekwencji (MaxPool2D po warstwie Flatten)
network MaxPoolError {
    layer: Conv2D(1, 32, 3),
    layer: Flatten(),
    layer: MaxPool2D(2)
}

train_config C { epochs: 1 }
load_data MNIST { batch_size: 32 }
train MaxPoolError with C on MNIST
