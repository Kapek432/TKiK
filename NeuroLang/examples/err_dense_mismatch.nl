# Błąd Semantyczny: Niezgodność wymiarów w warstwie Dense

network MismatchedNet {
    layer: Dense(784, 128),
    layer: Dense(64, 10)
}
