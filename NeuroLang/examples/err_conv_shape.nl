# Przykład z błędem kształtu (kernel 10x10 na obrazku 4x4)
network ConvError(1, 4, 4) {
    layer: Conv2D(1, 32, 10)
}

train_config C { epochs: 1 }
load_data MNIST { batch_size: 32 }
train ConvError with C on MNIST
