try:
    from ...IO.structure_handling_tools.AtomPosition import AtomPosition
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys

try:
    from ...single_run.SingleRun import SingleRun
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing SingleRunDFT: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class VacuumStates_builder(BasePartition):
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        Initializes the VacuumStatesBuilder class.

        This class is responsible for generating and handling dimer configurations in a computational chemistry context, 
        particularly for vacuum state simulations.

        Parameters:
        - file_location (str, optional): Path to the directory containing initial data files.
        - name (str, optional): Name identifier for this instance of VacuumStatesBuilder.
        - **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)
        
    def generate_dimers(self, container, steps: int = None, atomlabel_A: str = None, atomlabel_B: str = None, 
                        initial_distance: float = None, final_distance: float = None, factor:float=None,
                        vacuum_tolerance: float = 6.0, file_location: str = None):
        """
        Generates a series of dimer configurations with varying distances.

        Parameters:
        - container (object): The container where the dimer configurations will be stored.
        - steps (int, optional): Number of steps between initial and final distance.
        - atomlabel_A (str, optional): Label of the first atom in the dimer.
        - atomlabel_B (str, optional): Label of the second atom in the dimer.
        - initial_distance (float, optional): Starting distance between the dimer atoms.
        - final_distance (float, optional): Ending distance between the dimer atoms.
        - vacuum_tolerance (float, optional): Additional space around the dimer in the simulation box.
        - file_location (str, optional): File location for the AtomPosition data.

        Returns:
        - tuple: A pair of lists, one containing containers with dimer configurations, and the other containing subdirectories for these containers.

        Raises:
        - ValueError: If required parameters are not provided or invalid.
        """
        factor = factor if factor else 0.8 
        initial_distance = initial_distance if initial_distance is not None else (self.covalent_radii[atomlabel_A]+self.covalent_radii[atomlabel_B])*0.85
        final_distance = final_distance if final_distance is not None else 5
        delta_distance =  (final_distance-initial_distance)/steps
        sub_directories, containers = [], []
        lattice_distance =  np.array([ [final_distance+vacuum_tolerance,0,0], [0,vacuum_tolerance,0], [0,0,vacuum_tolerance] ]) 

        for step in range(steps):
            distance = initial_distance + delta_distance*float(step)
            container = SingleRun()
            container.AtomPositionManager = AtomPosition(file_location)
            container.AtomPositionManager.add_atom(atomLabels=atomlabel_A, 
                                                        atomPosition=[0,0,0], )
            container.AtomPositionManager.add_atom(atomLabels=atomlabel_B, 
                                                        atomPosition=[distance,0,0], )
            container.AtomPositionManager.set_latticeVectors( lattice_distance, edit_positions=False ) 
            containers.append( container )
            sub_directories.append(f'/generate_dimers/{atomlabel_A}_{atomlabel_B}_{step}')
            
        return containers, sub_directories

    def handleDimers(self, values:list, file_location:str=None):
        """
        Manages the creation of dimer configurations based on specified values.

        Parameters:
        - values (list): List of dictionaries with parameters for dimer generation.
        - container_index (int): Index for tracking containers.
        - file_location (str, optional): File location for atom positions.

        Returns:
        - list: Containers with generated dimer configurations.

        This method iterates over a list of value dictionaries to create various dimer configurations.
        It updates the internal 'containers' attribute with the new configurations.
        """
        containers = []
        sub_directories = []

        for v in values:
            # Assuming self.containers is already defined and AtomLabels is initially None or an empty set
            AtomLabels = v['AtomLabels'] or list(set().union(*(container.AtomPositionManager.uniqueAtomLabels for container in self.containers)))
            initial_distance = v['initial_distance']
            final_distance = v['final_distance']
            steps = v['steps']
            vacuum_tolerance = v['vacuum_tolerance']
            for atomlabel_A_index, atomlabel_A in enumerate(AtomLabels):
                for atomlabel_B_index, atomlabel_B in enumerate(AtomLabels[atomlabel_A_index:] ):
                    container_copy = SingleRun()
                    container_copy.AtomPositionManager = AtomPosition(file_location)
                    
                    container_list, sub_directories_list = self.generate_dimers(container=container_copy, steps=steps, atomlabel_A=atomlabel_A, atomlabel_B=atomlabel_B, 
                                                                                initial_distance=initial_distance, final_distance=final_distance, file_location=file_location,
                                                                                vacuum_tolerance=vacuum_tolerance)
                    containers += container_list
                    sub_directories += sub_directories_list

        self.containers = containers

        return containers
