# Subclase para sistemas no periódicos
class NonPeriodicSystem(AtomPositionManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Atributos específicos para sistemas no periódicos

    def read_PDB(self, file_path):
        # Implementación
        pass

    def convert_to_periodic(self):
        return PeriodicSystem(**self.attributes)
