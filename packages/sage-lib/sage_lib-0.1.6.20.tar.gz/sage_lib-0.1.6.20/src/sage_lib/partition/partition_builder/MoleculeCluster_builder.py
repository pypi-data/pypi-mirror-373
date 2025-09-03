try:
    from ...IO.structure_handling_tools.AtomPosition import AtomPosition
    from ...miscellaneous.marching_cubes import generate_offset_mesh
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys
    
try:
    import numpy as np
    import copy
    from tqdm import tqdm
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class MoleculeCluster_builder(BasePartition):
    """
    MoleculeCluster_builder is a class for building molecular clusters, particularly useful in simulations involving molecular systems.

    This class extends the functionality of PartitionManager to provide specific methods for creating and managing clusters of molecules. It includes methods for calculating cluster volumes, determining the number of molecules for a given density, adding individual molecules or solvents, and handling complex molecular cluster setups.

    Attributes:
        _molecule_template (dict): A dictionary to store molecule templates.
        _density (float): Density of the cluster.
        _cluster_lattice_vectors (np.array): Lattice vectors defining the cluster's boundaries.

    Methods:
        get_cluster_volume(shape, cluster_lattice_vectors): Calculates the volume of the cluster.
        get_molecules_number_for_target_density(density, cluster_volume, molecules): Calculates the number of molecules needed for a target density.
        add_molecule_template(name, atoms): Adds a molecule template to the builder.
        add_molecule(container, molecule, shape, cluster_lattice_vectors, translation, distribution, tolerance, max_iteration): Adds a molecule to the cluster.
        add_solvent(container, shape, cluster_lattice_vectors, translation, distribution, molecules, density, max_iteration): Adds solvent molecules to the cluster.
        handleCLUSTER(container, values, container_index, file_location): Handles the creation of a molecular cluster within a specified container.

    Parameters:
        file_location (str, optional): The initial file location for the cluster data.
        name (str, optional): The initial name of the molecule cluster.

    Examples:
        # Create a MoleculeCluster_builder instance
        cluster_builder = MoleculeCluster_builder(name="WaterCluster", file_location="/path/to/cluster")

        # Add a molecule template
        cluster_builder.add_molecule_template(name="H2O", atoms=water_atoms)

        # Add molecules to the cluster
        cluster_builder.add_molecule(container, water_molecule, shape='box')
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor method for initializing the MoleculeCluster_builder instance.
        """
        self._molecule_template = {}
        self._density = None
        self._cluster_lattice_vectors = None

        super().__init__(*args, **kwargs)

    def is_point_inside_unit_cell(unit_cell, point):
        """
        Determines if a given point is inside a unit cell defined by a 3x3 matrix.

        Parameters:
            unit_cell (np.ndarray): A 3x3 matrix where each row represents a lattice vector.
            point (np.ndarray): A 3-element vector representing the Cartesian coordinates of the point.

        Returns:
            bool: True if the point is inside the unit cell, False otherwise.
        """
        # Compute the fractional coordinates of the point relative to the unit cell
        # by solving the linear system: unit_cell * fractional = point
        fractional_coords = np.linalg.solve(unit_cell, point)
        
        # Check if all fractional coordinates are in the interval [0, 1)
        return np.all(fractional_coords >= 0) and np.all(fractional_coords < 1)

    @staticmethod
    def generate_points_in_sphere(radius, num_points, distribution:str='uniform'):
        """
        Generates a uniform distribution of points inside a sphere.

        Parameters:
            radius (float): The radius of the sphere.
            num_points (int): The number of points to generate.

        Returns:
            np.ndarray: An array of shape (num_points, 3) containing the generated points.
        """
        points = np.zeros( (num_points,3) )

        for i in range(num_points):
            # Generate a random point in spherical coordinates
            phi = np.random.uniform(0, 2 * np.pi)  # azimuthal angle
            costheta = np.random.uniform(-1, 1)  # cosine of polar angle
            u = np.random.uniform(0, 1)  # random number for radius

            theta = np.arccos(costheta)  # polar angle

            if distribution == 'uniform':
                r = radius * (u ** (1/3))  # cubic root to ensure uniform distribution
            elif distribution == 'center':
                r = radius   # cubic root to ensure center distribution

            # Convert spherical coordinates to Cartesian coordinates
            x = r * np.sin(theta) * np.cos(phi)
            y = r * np.sin(theta) * np.sin(phi)
            z = r * np.cos(theta)
            points[i, :] = [x,y,z]

        return np.array(points)

    def get_cluster_volume(self, shape:str='box', cluster_lattice_vectors:np.array=None ):
        """
        Calculates the volume of the molecular cluster based on its shape and lattice vectors.

        Parameters:
            shape (str): The shape of the cluster, default is 'box'.
            cluster_lattice_vectors (np.array): The lattice vectors defining the cluster boundaries.

        Returns:
            float: The volume of the cluster in cubic angstroms.
        """
        cluster_lattice_vectors = cluster_lattice_vectors if cluster_lattice_vectors is not None else self.cluster_lattice_vectors 
        
        if shape.lower() == 'box':
            return np.abs(np.linalg.det(cluster_lattice_vectors)) * 10**-24
        elif shape.lower() == 'sphere':
            return np.pi * 3/4 * cluster_lattice_vectors[0]**3 * 10**-24
        
        else:
            print(f'Undefine shape : {shape}')

        return volume

    def get_molecules_number_for_target_density(self, density:float=1.0, cluster_volume:float=None, molecules:dict={'H2O':1.0} ) -> dict:
        """
        Calculates the number of molecules needed to achieve a target density in the cluster.

        Parameters:
            density (float): The target density in g/cm^3.
            cluster_volume (float): The volume of the cluster in cubic angstroms.
            molecules (dict): A dictionary of molecule types and their fractional composition.

        Returns:
            dict: A dictionary with molecule names as keys and the number of molecules as values.
        """
        mass_suma = np.sum( [ self._molecule_template[m_name].mass * m_fraction for m_name, m_fraction in molecules.items()] ) 
        factor = density * self.NA * cluster_volume / mass_suma
        return { m_name: int(np.round(factor*m_fraction)) for m_name, m_fraction in molecules.items() }

    def add_molecule_template(self, name:str, atoms:object, ) -> bool:
        """
        Adds a molecule template to the builder.

        Parameters:
            name (str): The name of the molecule.
            atoms (object): The atom object representing the molecule.

        Returns:
            bool: True if the molecule template was added successfully.
        """
        self._molecule_template[name] = atoms
        return True

    def add_molecule(self, container, molecule, 
                        shape:str='box', cluster_lattice_vectors:np.array=np.array([[10, 0, 0], [0,10, 0], [0, 0, 10]]), 
                        translation:np.array=None, distribution:str='random', surface:np.array=None,
                        tolerance:float=1.6, max_iteration:int=6000, probability=None):
        """
        Adds a single molecule to the cluster.

        Parameters:
            container: The container to which the molecule is added.
            molecule: The molecule to be added.
            shape (str): The shape of the cluster.
            cluster_lattice_vectors (np.array): The lattice vectors of the cluster.
            translation (np.array): The translation vector for placing the molecule.
            distribution (str): The distribution method for placing the molecule.
            tolerance (float): The minimum allowable distance between molecules.
            max_iteration (int): The maximum number of iterations for placing the molecule.

        Returns:
            bool: True if the molecule was added successfully, False otherwise.
        """
        translation = translation if translation is not None else np.array([0,0,0], dtype=np.float64)
        iteration = 0

        molecule_copy = copy.deepcopy(molecule) 
        while True:
            if shape.lower() == 'box':
                if distribution.lower() == 'random':
                    displacement = translation + molecule_copy.generate_uniform_translation_from_fractional(latticeVectors=cluster_lattice_vectors )

            elif shape.lower() == 'sphere':
                if distribution.lower() == 'random':
                    displacement = translation + self.generate_points_in_sphere(radius=cluster_lattice_vectors[0], num_points=1, distribution='uniform')
                if distribution.lower() == 'center':
                    displacement = translation + self.generate_points_in_sphere(radius=cluster_lattice_vectors[0], num_points=1, distribution='center')

            elif shape.lower() == 'surface':
                if probability is not None:
                    displacement = translation + surface[np.random.choice(surface.shape[0], p=probability)]
                else:
                    displacement = translation + surface[np.random.randint(surface.shape[0])]

            atomPositions = np.dot(molecule.atomPositions, molecule.generate_random_rotation_matrix().T) + displacement
            molecule_copy.set_atomPositions(new_atomPositions=atomPositions) 
            molecule_copy.latticeVectors = container.AtomPositionManager.latticeVectors
            
            if np.sum( container.AtomPositionManager.count_neighbors( molecule_copy, r=tolerance) ) == 0:   
                container.AtomPositionManager.add_atom( atomLabels=molecule_copy.atomLabelsList, atomPosition=molecule_copy.atomPositions, atomicConstraints=molecule_copy.atomicConstraints )
                return True
            else:
                iteration += 1

            if iteration > max_iteration:
                print(f' (!) Can not set cluster :: {max_iteration} iterations cap reach ::try lower density')
                return False

    def add_solvent(self, container, 
                        shape:str='box', cluster_lattice_vectors:np.array=np.array([[10, 0, 0], [0,10, 0], [0, 0, 10]]), translation:np.array=np.array([0,0,0]), distribution:str='random', tolerance:float=1.6, 
                        molecules:dict={'H2O':1.0}, density:float=1.0, max_iteration:int=60000, molecules_number:dict=None, verbosity:bool=False):
        """
        Adds solvent molecules to the cluster.

        Parameters:
            container: The container to which the solvent is added.
            shape (str): The shape of the cluster.
            cluster_lattice_vectors (np.array): The lattice vectors of the cluster.
            translation (np.array): The translation vector for placing the solvent molecules.
            distribution (str): The distribution method for placing the solvent molecules.
            molecules (dict): The solvent molecules and their proportions.
            density (float): The target density for the solvent.
            max_iteration (int): The maximum number of iterations for placing the solvent molecules.

        Returns:
            None
        """
        max_iteration = max_iteration if isinstance(max_iteration,int) else 100000
        cluster_volume = self.get_cluster_volume(shape=shape, cluster_lattice_vectors=cluster_lattice_vectors)

        molecules_number = molecules_number if isinstance(molecules_number,dict) else self.get_molecules_number_for_target_density(density=density, cluster_volume=cluster_volume, molecules=molecules) 
        
        for molecule_name, molecule_number in molecules_number.items():
            iterable = range(molecule_number)
            if verbosity:
                iterable = tqdm(iterable, desc=f"Adding {molecule_name} to empty spaces")

            for mn in iterable:
                success = self.add_molecule( 
                    container=container, 
                    molecule=self.molecule_template[molecule_name], 
                    translation=translation, 
                    tolerance=tolerance,
                    shape=shape, 
                    cluster_lattice_vectors=cluster_lattice_vectors, 
                    distribution=distribution, 
                    max_iteration=max_iteration )
                if not success:
                    if verbosity:
                        print('Can not set cluster, try lower density. ')
                    return False
                    break

        self.molecules_number = molecules_number

        return True

    def add_adsobate(self, container, 
                        shape:str='surface', translation:np.array=np.array([0,0,0]), distribution:str='random', tolerance:float=1.6, surface:np.array=None, 
                        molecules:dict={'H2O':1.0}, density:float=1.0, max_iteration:int=60000, molecules_number:dict=None, verbosity:bool=True):
        """
        Adds solvent molecules to the cluster.

        Parameters:
            container: The container to which the solvent is added.
            shape (str): The shape of the cluster.
            cluster_lattice_vectors (np.array): The lattice vectors of the cluster.
            translation (np.array): The translation vector for placing the solvent molecules.
            distribution (str): The distribution method for placing the solvent molecules.
            molecules (dict): The solvent molecules and their proportions.
            max_iteration (int): The maximum number of iterations for placing the solvent molecules.

        Returns:
            None
        """
        max_iteration = max_iteration if isinstance(max_iteration,int) else 100000
        
        min_value = min(list(molecules.values()))
        molecules_number = molecules_number if isinstance(molecules_number,dict) else {key: abs(value/min_value) for key, value in molecules.items() }
        
        for molecule_name, molecule_number in molecules_number.items():
            iterable = range(molecule_number)
            if verbosity:
                iterable = tqdm(iterable, desc=f"Adding {molecule_name} to empty spaces")

            for mn in iterable:
                success = self.add_molecule(
                    container=container,
                    molecule=self.molecule_template[molecule_name],
                    translation=translation,
                    tolerance=tolerance,
                    surface=surface,
                    shape=shape,
                    distribution=distribution,
                    max_iteration=max_iteration
                )
                if not success:
                    if verbosity:
                        print('Cannot set cluster, try lowering the number of molecules.')
                    return False
                    break

        self.molecules_number = molecules_number

        return True
    def handleCLUSTER(self, values:dict, containers:list=None):
        """
        Handles the creation and management of a molecular cluster within a specified container.

        Parameters:
            container (object): The container in which the cluster is built.
            values (list): A list of parameters defining the cluster properties.
            container_index (int): The index of the container.
            file_location (str, optional): The file location for storing cluster data.

        Returns:
            list: A list of containers with the created clusters.
        """
        #sub_directories, containers = [], []
        
        containers_new = []
        containers = containers if isinstance(containers, list) else self.containers

        for container_index, container in enumerate(containers):
            for v_key, v_item in values.items():

                if 'seed' in v_item and isinstance(v_item['seed'], float): np.random.seed(int(v_item['seed'])) 

                if v_key.upper() == 'ADD_SOLVENT':
                    # Copy and update container for each set of k-point values
                    container_copy = self.copy_and_update_container(container, f'/solvent/', '')
                    
                    for s in v_item['solvent']:
                        molecule = AtomPosition()
                        molecule.build(s)
                        self.add_molecule_template(s, molecule)
                    molecules= {s:1 for s in v_item['solvent']}

                    if 'slab' in v_item and v_item['slab']:
                        vacuum_box, vacuum_start = container_copy.AtomPositionManager.get_vacuum_box(tolerance=v_item['vacuum_tolerance']) 
                        shape = 'box'
                        distribution = 'random'
                    else:
                        shape = v_item['shape']
                        if shape.upper() == 'BOX':
                            shape = 'box'
                            vacuum_box, vacuum_start = np.array([[v_item['size'][0],0,0],[0,v_item['size'][1],0],[0,0,v_item['size'][2]]], dtype=np.float64), v_item['translation']
                        elif shape.upper() == 'SPHERE':
                            shape = 'sphere'
                            vacuum_box, vacuum_start = [float(v_item['size'][0])], v_item['translation']
                        elif shape.upper() == 'PARALLELEPIPED':
                            shape = 'box'
                            if len(v_item['size'].shape) > 1:
                                v_item['size'] = v_item['size'].flatten()
                            vacuum_box, vacuum_start = np.array([
                                                            [v_item['size'][0],v_item['size'][1],v_item['size'][2]],
                                                            [v_item['size'][3],v_item['size'][4],v_item['size'][5]],
                                                            [v_item['size'][6],v_item['size'][7],v_item['size'][8]]], 
                                                        dtype=np.float64), v_item['translation']
                        elif shape.upper() == 'CELL':
                            shape = 'box'
                            vacuum_box, vacuum_start = np.array(container_copy.AtomPositionManager.get_cell() ,dtype=np.float64), np.array([0,0,0] ,dtype=np.float64)

                        distribution = v_item.get('distribution', 'random')

                    tolerance = v_item['collision_tolerance']
                    density = v_item['density']

                    molecules_number = v_item.get('molecules_number')
                    # If 'molecules_number' is a list, convert it into a dictionary using 'solvent' as keys
                    if isinstance(molecules_number, (list, np.ndarray)):
                        molecules_number = {solvent: int(mn) for solvent, mn in zip(v_item['solvent'], molecules_number)}
                    # If 'molecules_number' is neither a list nor a dict, set it to None
                    elif not isinstance(molecules_number, dict):
                        molecules_number = None

                    max_iteration = v_item.get('max_iteration', None)
                    if not self.add_solvent(container=container_copy, shape=shape, cluster_lattice_vectors=vacuum_box, 
                                translation=vacuum_start, distribution=distribution, density=density, tolerance=tolerance,
                                molecules=molecules, molecules_number=molecules_number, max_iteration=max_iteration):
                        return False
                    else:
                        if v_item.get('verbose', False):
                            print(' Solvent added (ok!)')

                    if v_item['wrap']:
                        container_copy.AtomPositionManager.pack_to_unit_cell()

                    containers_new.append(container_copy)
                
                # =================================================== #
                if v_key.upper() == 'ADD_ADSOBATE':
                    container_copy = self.copy_and_update_container(container, f'/adsobate/', '')
                    shape = 'surface'

                    for s in v_item['adsobate']:
                        molecule = AtomPosition()
                        molecule.build(s)
                        self.add_molecule_template(s, molecule)
                    molecules= {s:1 for s in v_item['adsobate']}

                    d = v_item['d']
                    resolution = v_item['resolution']
                    padding = v_item['padding']

                    # Retrieve the list of IDs from v_item
                    ID_label_list = v_item['ID']

                    # Convert elements that are int or float to integers
                    ID_number = [int(x) for x in ID_label_list if isinstance(x, (int, float))]

                    # Append indices from container.AtomPositionManager.atomLabelsList where the label is present in ID_label_list
                    ID_number.extend(
                        i for i, label in enumerate(container.AtomPositionManager.atomLabelsList)
                        if label in ID_label_list
                    )

                    positions = np.atleast_2d(container.AtomPositionManager.atomPositions[ID_number])
                    verts, faces = generate_offset_mesh(positions, d, resolution=resolution, padding=padding)
                    if len(verts) == 0:
                        verts = self.generate_points_in_sphere(radius=d, num_points=resolution**2, distribution='center') + positions[0]

                    tolerance = v_item['collision_tolerance']
                    molecules_number = v_item.get('molecules_number')
                    translation = v_item.get('translation', [0,0,0])
                    distribution = v_item.get('distribution', 'random')
                    density = v_item.get('density', 1.0) # NOT IMPLEMENTED
                    slab = v_item.get('slab', False)
                    verbosity =  v_item.get('verbosity', False)
                    prioritize_connectivity = v_item.get('prioritize_connectivity', False)

                    if slab:
                        z_mean = np.mean(container.AtomPositionManager.atomPositions, axis=0)[2]
                        verts = verts[verts[:,2] > z_mean]
                        #verts = verts[verts[:,2] < 11.5]
                    
                    #'''
                    #results = container.AtomPositionManager.kdtree.query_ball_point(verts, tolerance, p=2., eps=0)
                    #verts = np.array([x for x, r in zip(verts, results) if not r], dtype=np.float64)
                    #'''

                    if prioritize_connectivity:
                        results = container.AtomPositionManager.kdtree.query_ball_point(verts, d+padding, p=2., eps=0)
                        verts_probability = np.array([len(r) for r in results], dtype=np.float64)
                        verts_probability /= np.sum(verts_probability)

                    else:
                        verts_probability = np.ones(len(verts))

                    if v_item.get('verbose', False):
                        print(f' {len(verts)} vertices found')

                    '''    
                    print(f' {len(verts)} vertices found')
                    # DEBBUG #
                    import matplotlib.pyplot as plt
                    fig2 = plt.figure()
                    ax2 = fig2.add_subplot(projection='3d')
                    ax2.plot_trisurf(verts[:, 0], verts[:, 1], faces, verts[:, 2], linewidth=0.2, antialiased=True)
                    ax2.set_title(f"Offset Surface at d={d}")
                    ax2.set_xlabel("X")
                    ax2.set_ylabel("Y")
                    ax2.set_zlabel("Z")

                    plt.show()
                    '''

                    """
                    vals_v = verts_probability

                    fig2 = plt.figure()
                    ax2 = fig2.add_subplot(projection='3d')

                    # Compute one color value per triangle by averaging its 3 vertices
                    vals_tri = vals_v[faces].mean(axis=1)

                    surf = ax2.plot_trisurf(
                        verts[:, 0], verts[:, 1], verts[:, 2],
                        triangles=faces,
                        linewidth=0.2, antialiased=True, shade=False, cmap='viridis'
                    )

                    # Attach the triangle-wise scalar array to the surface
                    surf.set_array(vals_tri)
                    surf.autoscale()  # rescale color limits to data

                    ax2.set_title(f"Offset Surface at d={d}")
                    ax2.set_xlabel("X"); ax2.set_ylabel("Y"); ax2.set_zlabel("Z")
                    fig2.colorbar(surf, ax=ax2, shrink=0.65, pad=0.1, label="Value")
                    plt.show()
                    """

                    # If 'molecules_number' is a list, convert it into a dictionary using 'solvent' as keys
                    if isinstance(molecules_number, (list, np.ndarray)):
                        molecules_number = {solvent: int(mn) for solvent, mn in zip(v_item['adsobate'], molecules_number)}
                    # If 'molecules_number' is neither a list nor a dict, set it to None
                    elif not isinstance(molecules_number, dict):
                        molecules_number = None
    
                    max_iteration = v_item.get('max_iteration', None)
                    if not self.add_adsobate(container=container_copy, shape=shape,  surface=verts,
                                translation=translation, distribution=distribution, density=density, tolerance=tolerance,
                                molecules=molecules, molecules_number=molecules_number, max_iteration=max_iteration, verbosity=verbosity):
                        return False
                    else:
                        if v_item.get('verbose', False):
                            print(' Adsobate added (ok!)')

                    
                    if v_item['wrap']:
                        container_copy.AtomPositionManager.pack_to_unit_cell()

                    containers_new.append(container_copy)


        self.set_container(containers_new)

        return containers_new

