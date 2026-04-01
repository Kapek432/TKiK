# Przykład z błędem dzielenia przez zero w deklaracji zmiennej
let x = 10 / (5 - 5)

network ZeroNet {
    layer: Dense(x, 10)
}

train_config C { epochs: 1 }
load_data MNIST { batch_size: 32 }
train ZeroNet with C on MNIST
