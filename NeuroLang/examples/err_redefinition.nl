# Przykład z błędem redefinicji zmiennej
let x = 10
let x = 20

network RedefineNet {
    layer: Dense(x, 10)
}

train_config C { epochs: 1 }
load_data MNIST { batch_size: 32 }
train RedefineNet with C on MNIST
