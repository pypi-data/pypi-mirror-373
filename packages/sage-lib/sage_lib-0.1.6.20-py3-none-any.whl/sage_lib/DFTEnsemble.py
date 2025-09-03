
class DFTEnsemble:
    def __init__(self):
        self.containers = []  # Lista para almacenar subcontenedores

    def add_container(self, container):
        self.containers.append(container)

    def remove_container(self, container):
        self.containers.remove(container)