try:
    import numpy as np
    from tqdm import tqdm
    import copy
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class PositionEditor_builder(BasePartition):
    """
    A class for managing and editing atomic positions in various ways, inheriting from PartitionManager.

    Methods
    -------
    handle_rattle(values, file_location=None)
        Applies a random displacement to atomic positions.

    handle_compress(container, values, container_index, file_location=None)
        Compresses a given container along a defined direction.

    handle_widening(values, file_location=None)
        Stacks atoms from different containers to widen atomic layers.

    handle_interpolation(values, file_location=None)
        Interpolates between atomic positions using splines.

    handle_exfoliation(values, file_location=None)
        Separates atomic layers to simulate exfoliation.
    """
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        Initialize the PositionEditorBuilder instance.

        Parameters
        ----------
        file_location : str, optional
            The file location for the atomic data.
        name : str, optional
            The name for this instance.
        """
        super().__init__(*args, **kwargs)

    def handle_rattle(self, values, file_location=None):
        """
        Applies random displacements to atom positions within containers to simulate atomic 'rattling'.
        
        Parameters
        ----------
        values : dict
            Contains parameters for the rattling process (e.g., standard deviation 'std', number of iterations 'N').
        file_location : str, optional
            Directory to store rattled configurations.

        Returns
        -------
        list
            A list of containers with rattled atom positions.
        """
        containers = []

        # Iterate through each container and apply random rattling 'N' times.
        for container_index, container in enumerate(self.containers):
            for n in range(values['N']):
                # Create a copy of the container and apply the random displacement.
                container_copy = self.copy_and_update_container(container, f'/rattle/{container_index}_{n}', file_location)
                container_copy.AtomPositionManager.rattle(stdev=values['std'], seed=n)

                containers.append(container_copy)
        
        # Update the current containers with the rattled containers.
        self.containers = containers

        return containers

    def handle_compress(self, values, file_location=None):
        """
        Compresses the atom positions within a container by applying different compression factors.
        
        Parameters
        ----------
        container : object
            The container whose atom positions will be compressed.
        values : dict
            Contains parameters like 'compress_min', 'compress_max', and 'N' for the compression range.
        container_index : int
            Index of the container.
        file_location : str, optional
            Directory to store compressed configurations.

        Returns
        -------
        list
            A list of containers with compressed atom positions.
        """
        sub_directories, containers = [], []

        # Create a vector of compression factors.
        compress_vector = self.interpolate_vectors(values['compress_min'], values['compress_max'], values['N'])

        # Iterate through each container and compress.
        for container_index, container in enumerate(tqdm(self.containers, desc="Processing Containers")):

            for v_i, v in enumerate(compress_vector):
                # Create a copy of the container and apply the compression factor.
                container_copy = self.copy_and_update_container(container, f'/compress/{v_i}', file_location)
                container_copy.AtomPositionManager.compress(compress_factor=v, verbose=False)
                    
                sub_directories.append(f'/{v_i}')
                containers.append(container_copy)

        return containers

    def handle_widening(self, values, file_location=None):
        """
        Stacks multiple atomic configurations to create wider layers of atoms.
        
        Parameters
        ----------
        values : list of dict
            Each dictionary contains indices and stacking direction information.
        file_location : str, optional
            Directory to store widened configurations.

        Returns
        -------
        list
            A list of containers with widened atomic layers.
        """
        sub_directories, containers = [], []

        # Iterate over the provided values to stack atomic configurations.
        for v_i, v in enumerate(values):
            container_init = self.containers[v['init_index']]
            container_mid = self.containers[v['mid_index']]
            container_end = self.containers[v['end_index']]
            
            # Create a copy of the initial container.
            container_copy = self.copy_and_update_container(container_init, f'/widening/{v_i}', file_location)

            # Stack the middle container 'N' times, then add the end container.
            for n in range(v['N']):
                container_copy.AtomPositionManager.stack(AtomPositionManager=container_mid.AtomPositionManager, direction=v['direction'])
            container_copy.AtomPositionManager.stack(AtomPositionManager=container_end.AtomPositionManager, direction=v['direction'])

            sub_directories.append(f'/{v_i}')
            containers.append(container_copy)
    
        return containers

    def handle_interpolation(self, values, file_location=None):
        """
        Interpolates atom positions between given configurations using spline interpolation.
        
        Parameters
        ----------
        values : dict
            Contains parameters for interpolation like 'images' and 'degree'.
        file_location : str, optional
            Directory to store interpolated configurations.

        Returns
        -------
        list
            A list of containers with interpolated atom positions.
        """
        interpolation_data = np.zeros((self.containers[0].AtomPositionManager.atomCount, 3, len(self.containers)), dtype=np.float64)

        # Collect atomic positions from each container.
        for container_index, container in enumerate(self.containers):
            if values.get('first_neighbor', False):
                container.AtomPositionManager.wrap()
            interpolation_data[:, :, container_index] = container.AtomPositionManager.atomPositions_fractional

        # Adjust positions for periodic boundaries if specified.
        if values.get('first_neighbor', False):
            diff = np.diff(interpolation_data, axis=2)
            interpolation_data[:, :, 1:][diff > 0.5] -= 1
            interpolation_data[:, :, 1:][diff < -0.5] += 1

        # Perform spline interpolation on the collected data.
        new_interpolated_data = self.interpolate_with_splines(interpolation_data, M=values['images'], degree=values['degree'])

        containers = [self.copy_and_update_container(self.containers[0], f'/interpolation/init', file_location)]
        for container_index, container in enumerate(self.containers[1:]):
            for n in range(values['images'] + 1):
                container_copy = self.copy_and_update_container(container, f'/interpolation/{container_index}_{n}', file_location)
                container_copy.AtomPositionManager.set_atomPositions_fractional(new_interpolated_data[:, :, container_index * (values['images'] + 1) + n + 1])
                if values.get('first_neighbor', False):
                    container_copy.AtomPositionManager.wrap()
                containers.append(container_copy)
        
        self.containers = containers

        return containers

    def handle_exfoliation(self, values, file_location=None):
        """
        Simulates the exfoliation of atomic layers by separating them along a specified axis.
        
        Parameters
        ----------
        values : dict
            Contains parameters such as 'direction' and 'threshold' to determine layers.
        file_location : str, optional
            Directory to store exfoliated configurations.

        Returns
        -------
        list
            A list of containers with exfoliated atomic layers.
        """
        containers = []
        separation_distance = values.get('separation_distance', 20.0)   # Default separation distance between layers.
        layer_direction = values.get('direction', 'y') 
        layer_threshold = values.get('threshold', 2.0) 

        # Iterate through each container and separate layers.
        for container_index, container in enumerate(tqdm( copy.deepcopy(self.containers), desc="Processing Containers")):
            # Wrap atom positions within simulation boundaries to ensure all atoms are inside the box.
            container.AtomPositionManager.wrap()

            # Get indices of atoms in each layer based on the specified direction and threshold.
            layers_index_list = container.AtomPositionManager.get_layers(direction=layer_direction, 
                                                                         threshold=layer_threshold)
            
            # Create a deep copy of the original container to add solvent in the slab form.
            container_original = copy.deepcopy(container)
            
            container_original_water = self.handleCLUSTER(    values = {'ADD_SOLVENT':{
                                            'density': 1.01,
                                            'solvent': ['H2O'],
                                            'slab': True,
                                            'shape': None,
                                            'size': None,
                                            'vacuum_tolerance': 0,
                                            'colition_tolerance': 1.75,
                                            'translation': None,
                                            'wrap': True,
                                            'seed':0,
                                            'max_iteration':100000,
                                            'verbose':True
                                        }}, 
                                    containers=container_original)

            # Add the modified container with water to the list of results.
            containers += container_original_water

            # Iterate through possible separation points and generate configurations for exfoliated layers.
            for cut_index in range(1, len(layers_index_list)):
                # Create a deep copy of the container for each new configuration.
                container_copy = copy.deepcopy(container)

                # Move atoms in different directions to simulate the exfoliation process.
                for i, layer_indices in enumerate(layers_index_list):
                    if i > cut_index:
                        container_copy.AtomPositionManager.move_atom(layer_indices, [0, separation_distance / 2, 0])
                    #else:
                    #    container_copy.AtomPositionManager.move_atom(layer_indices, [0, -separation_distance / 2, 0])

                # Determine the vacuum box dimensions (used if further modification is needed).
                vacuum_box, vacuum_start = container.AtomPositionManager.get_vacuum_box(tolerance=0)
                
                # Add solvent to the exfoliated container using more customizable parameters.
                container_copy_water = self.handleCLUSTER(values={'ADD_SOLVENT': {
                                        'density': 1.0,
                                        'solvent': ['H2O'],
                                        'slab': False,
                                        'shape': 'CELL',
                                        'size': None,
                                        'vacuum_tolerance': 0,
                                        'colition_tolerance': 1.75,
                                        'molecules_number':self.molecules_number,
                                        'translation': None,
                                        'wrap': True,
                                        'seed':0,
                                        'max_iteration':100000,
                                        'verbose':True
                                    }}, 

                                containers=[container_copy])

                # Attempt to add the modified container with water to the list of results.
                try:
                    containers += container_copy_water
                except:
                    print('Warning: Could not add solvent to the container. Consider trying a lower density.')
                        
        return containers









