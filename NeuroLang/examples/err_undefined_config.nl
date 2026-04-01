# err_undefined_config.nl
# Przykład błędu: Użycie niezdefiniowanej konfiguracji w komendzie train

network MyNet {
    layer: Dense(10, 2)
}

load_data MNIST {
    batch_size: 32
}

# BŁĄD: Próba trenowania przy użyciu 'Niezdefiniowany_Config'
train MyNet with Niezdefiniowany_Config on MNIST
