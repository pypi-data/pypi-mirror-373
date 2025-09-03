class BasePartition:
    def __init__(self, *args, **kwargs):
        # Inicialización propia de BasePartition
        super().__init__(*args, **kwargs)  # Llama al siguiente __init__ en la cadena
        