try:
    import copy 
    import pickle
    import numpy as np
    import functools, time
    from scipy.spatial import Voronoi
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

from .BasePartition import BasePartition

def timeit_decorator(func):
    """Decorator to measure the execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time  # Calculate the execution time
        print(f"Execution time of {func.__name__}: {execution_time} seconds")
        return result
    return wrapper

class Extract_builder(BasePartition):
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        Initializes the CrystalDefectBuilder object. If a Periodic_Object is provided, its attributes are copied.

        Parameters:
            file_location (str): Location of the file.
            name (str): Name of the object.
            Periodic_Object (object): An object containing periodic attributes.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_atom_ids(AtomPositionManager, selection_list):
        """
        Retrieves atom IDs based on the selection list which can contain atom indices or labels.

        Parameters:
            AtomPositionManager (object): An object managing atom positions and labels.
            selection_list (list): A list of atom indices or labels.

        Returns:
            list: A list of unique atom IDs.
        """
        is_number = lambda s: s.replace('.', '', 1).isdigit() or s.replace('-', '', 1).replace('.', '', 1).isdigit()

        atom_ids = set()
        for item in selection_list:
            if isinstance(item, int) or is_number(item):
                atom_ids.add( int(item) )
            elif isinstance(item, str):
                if item.upper() in ['H2O', 'water']:
                    for i, label in enumerate(AtomPositionManager.atomLabelsList):
                        if label == 'O':
                            pos = AtomPositionManager.atomPositions[i]
                            closest_neighbors = AtomPositionManager.find_n_closest_neighbors(pos, 4)
                            if AtomPositionManager.atomLabelsList[closest_neighbors[1][1]] == AtomPositionManager.atomLabelsList[closest_neighbors[1][2]] == 'H' and closest_neighbors[0][2] < 1.2 and closest_neighbors[0][3] > 1.2: 
                                #if AtomPositionManager.atomPositions[i][2] > 26:
                                atom_ids.add( tuple(closest_neighbors[1][:3]) )

                if item.upper() in ['OOH']:
                    for i, label in enumerate(AtomPositionManager.atomLabelsList):
                        if label == 'O':
                            pos = AtomPositionManager.atomPositions[i]
                            closest_neighbors = AtomPositionManager.find_n_closest_neighbors(pos, 4)
                            if AtomPositionManager.atomLabelsList[closest_neighbors[1][1]] == 'H' and AtomPositionManager.atomLabelsList[closest_neighbors[1][2]] == 'O' and closest_neighbors[0][2] < 2.2 and closest_neighbors[0][3] > 2.2: 
                                #if AtomPositionManager.atomPositions[i][2] > 26:
                                atom_ids.add( tuple(closest_neighbors[1][:3]) )

                elif '-' in item:
                    a1, a2 = item.split('-')
                    for i, label in enumerate(AtomPositionManager.atomLabelsList):
                        if label == a1:
                            
                            pos = AtomPositionManager.atomPositions[i]
                            if AtomPositionManager.atomLabelsList[AtomPositionManager.find_n_closest_neighbors(pos, 2)[1][1]] == a2 or \
                                AtomPositionManager.atomLabelsList[AtomPositionManager.find_n_closest_neighbors(pos, 3)[1][2]] == a2 :
                                atom_ids.add( int(i) )

                else:
                    atom_ids.update([i for i, label in enumerate(AtomPositionManager.atomLabelsList) if label == item])
        
        return list(atom_ids) 

    def generate_extract(self, values, verbose:bool=False, containers:list=None):
        """
        Generates the configurational space by creating various combinations of defects in the crystal structure.

        Parameters:
            values (dict): A dictionary containing parameters for generating the configurational space.

        Returns:
            list: A list of containers with updated configurations.
        """
        containers = containers if isinstance(containers, list) else self.containers

        if values.get('last', False): containers = [containers[-1]]

        group = values['g']

        for container_index, container in enumerate(containers):
            
            atom_groups_ID = self.get_atom_ids(container.AtomPositionManager, group) 
            return atom_groups_ID

            if verbose: print(f' - Processing : {len(atom_groups_ID)} ')    
            print(group, atom_groups_ID)
            
            charge = container.AtomPositionManager.charge[atom_groups_ID][:,-1]
            magnetization = container.AtomPositionManager.magnetization[atom_groups_ID][:,-1]
            dist_matrix = np.array([ [container.AtomPositionManager.distance(container.AtomPositionManager.atomPositions[n1], 
                container.AtomPositionManager.atomPositions[n2]) if n1 > n2 else 0  for i2, n2 in enumerate(atom_groups_ID) ] for i1, n1 in enumerate(atom_groups_ID) ], dtype=np.float64 )
            labels = container.AtomPositionManager.atomLabelsList[atom_groups_ID]
            E = container.AtomPositionManager.E

            dictionary = { 
                'charge'        :     charge,
                'magnetization' :     magnetization,
                'dist_matrix'   :     dist_matrix,
                'labels'        :     labels,
                'E'             :     E,
                }

            print(dictionary)

            file_path = 'data'
            with open(file_path, 'wb') as file:
                pickle.dump(dictionary, file)
            
            print(f"Dictionary saved to {file_path}")












