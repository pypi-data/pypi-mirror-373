try:
    from ..master.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    from ..master.AtomicProperties import AtomicProperties
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomicProperties: {str(e)}\n")
    del sys

try:
    import ast
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing ast: {str(e)}\n")
    del sys

class Ensemble(FileManager, AtomicProperties):
    def __init__(self, ):
        self.ensembles = {}  # Lista para almacenar subcontenedores
        self.ensembles_path = {}

    def add_ensemble(self, ensemble, ensemble_key):
        self.ensembles[ensemble_key] = ensemble


    def read_ensembles_path(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            data_dict = ast.literal_eval(content)

        self._ensembles_path = data_dict

        return data_dict

    def read_ensembles(self, ensembles_path:dict=None):
        ensembles_path = ensembles_path if ensembles_path else self.ensembles_path 
        
        if isinstance(ensembles_path, dict):
            for key, value in ensembles_path.items():
                if isinstance(value, dict):
                    return {key: read_ensembles(ensembles_path) for key, value in d.items()}
                
                else:
                    PT = Partition()
                    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)
                    
                    return PT









