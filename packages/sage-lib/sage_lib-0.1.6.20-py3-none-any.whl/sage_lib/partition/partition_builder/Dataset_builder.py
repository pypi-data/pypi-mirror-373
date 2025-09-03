try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    from sage_lib.partition.PartitionManager import PartitionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
    del sys

class Dataset_builder(PartitionManager):
    """
    Manages a collection of ForceFieldModel instances.
    This class allows for operations such as training, updating, and applying
    force fields on a collection of models.
    """

    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        """
        Initialize the ForceFieldManager with an empty list of force field models.
        """
        self.name = None

    @staticmethod
    def sort_key(container):
        '''
        '''

        # Criterio 1: Número de especies químicas diferentes
        num_unique_species = len(container.AtomPositionManager.uniqueAtomLabels)
        
        # Criterio 2: Orden alfabético de especies únicas
        species_sorted = ''.join(sorted(container.AtomPositionManager.uniqueAtomLabels)) if container.AtomPositionManager.uniqueAtomLabels else ''
        
        # Criterio 3: Cantidad de átomos de la especie con mayor peso, ordenados alfabéticamente
        label_to_count_map = dict(zip(container.AtomPositionManager.uniqueAtomLabels, container.AtomPositionManager.atomCountByType))
        sorted_atomCountByType = [label_to_count_map[species] for species in sorted(container.AtomPositionManager.uniqueAtomLabels) if species in label_to_count_map]

        # Criterio 4: Proximidad según RMSD
        E = container.AtomPositionManager.E  if hasattr(container.AtomPositionManager, 'E') else float('inf')
        
        return num_unique_species, species_sorted, sorted_atomCountByType, E

    def sort_containers(self, verbose:bool=False):
        self.containers = sorted(self.containers, key=self.sort_key)
        
        if verbose: print('|| Dataset Sorted.')

        return self.containers

    def handleDataset(self, values:list, file_location:str=None):
        """

        """
        DS_data = {}

        for operation in values:
            if operation.upper() == 'FILTER':
                pass
            elif operation.upper() == 'SORT':
                self.sort_containers(verbose=values[operation]['verbose'] )

            elif operation.upper() == 'SHUFFLE':
                pass
            elif operation.upper() == 'PLOT':
                pass
            elif operation.upper() == 'SPLIT':
                pass

