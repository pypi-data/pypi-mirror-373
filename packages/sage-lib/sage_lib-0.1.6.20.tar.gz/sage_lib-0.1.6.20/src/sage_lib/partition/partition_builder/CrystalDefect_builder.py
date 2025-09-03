try:
    import copy 
    import functools, time
    import numpy as np
    from scipy.spatial import Voronoi
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

try:
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing BasePartition: {str(e)}\n")
    del sys

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

class CrystalDefect_builder(BasePartition):
    def __init__(self, *args, **kwargs):
        """
        Initializes the CrystalDefectBuilder object. If a Periodic_Object is provided, its attributes are copied.

        Parameters:
            file_location (str): Location of the file.
            name (str): Name of the object.
            Periodic_Object (object): An object containing periodic attributes.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def generate_combinations(self, lists: list, counts: list):
        """
        Generates all possible combinations of elements from the given lists based on the specified counts.

        Parameters:
            lists (list of lists): List of lists containing elements.
            counts (list of int): List of counts specifying the number of elements to select from each list.

        Returns:
            list: A list of combinations.
        """
        if len(lists) != len(counts):
            raise ValueError("The number of lists must be equal to the number of counts")

        def combinations_helper(current_combination, remaining_lists, remaining_counts):
            if not remaining_lists:
                yield current_combination
                return

            next_list = remaining_lists[0]
            next_count = remaining_counts[0]

            for combination in combinations(next_list, next_count):
                yield from combinations_helper(current_combination + combination, remaining_lists[1:], remaining_counts[1:])

        def combinations(lst, count):
            if count == 0:
                yield []
                return
            if not lst:
                return

            for i in range(len(lst)):
                for tail in combinations(lst[i+1:], count-1):
                    yield [lst[i]] + tail

        result = list(combinations_helper([], lists, counts))
        return result
    
    @staticmethod
    def get_probability(combination: list = None, distribution: str = 'uniform', AtomPositionManager: object = None, distances_dict: dict = None, coefficient: float = 1.0) -> float:
        """
        Calculates the probability of a combination based on the specified distribution.

        Parameters:
            combination (list): The combination of atom IDs.
            distribution (str): The type of distribution ('uniform', 'distance', 'distance-1', 'random').
            AtomPositionManager (object): An object managing atom positions.
            distances_dict (dict): A dictionary containing precomputed distances.
            coefficient (float): A coefficient to modify the probability calculation.

        Returns:
            float: The calculated probability.
        """
        if distribution in ['random', 'uniform']:
            return 1

        if distribution == 'distance':
            if distances_dict:
                return np.sum([distances_dict[n2][n1] if n1 > n2 else distances_dict[n1][n2] for i, n1 in enumerate(combination) for j, n2 in enumerate(combination[i:])]) ** coefficient
            else:
                return np.sum([AtomPositionManager.distance(AtomPositionManager.atomPositions[n1], AtomPositionManager.atomPositions[n2]) for i, n1 in enumerate(combination) for j, n2 in enumerate(combination[i:])]) ** coefficient

        if distribution == 'distance-1':
            if distances_dict:
                return 1 / np.sum([distances_dict[n2][n1] if n1 > n2 else distances_dict[n1][n2] for i, n1 in enumerate(combination) for j, n2 in enumerate(combination[i:])]) ** coefficient
            else:
                return 1 / np.sum([AtomPositionManager.distance(AtomPositionManager.atomPositions[n1], AtomPositionManager.atomPositions[n2]) for i, n1 in enumerate(combination) for j, n2 in enumerate(combination[i:])]) ** coefficient

        return 0

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
                                atom_ids.add( tuple(closest_neighbors[1][:3]) )
           
                if item.upper() in ['H-OH']:
                    for i, label in enumerate(AtomPositionManager.atomLabelsList):
                        if label == 'O':
                            pos = AtomPositionManager.atomPositions[i]
                            closest_neighbors = AtomPositionManager.find_n_closest_neighbors(pos, 4)
                            if AtomPositionManager.atomLabelsList[closest_neighbors[1][1]] == AtomPositionManager.atomLabelsList[closest_neighbors[1][2]] == 'H' and closest_neighbors[0][2] < 1.2 and closest_neighbors[0][3] > 1.2: 
                                atom_ids.update([closest_neighbors[1][1], closest_neighbors[1][2]])

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

    @staticmethod
    def get_distances_dict(atom_groups_ID: np.array, AtomPositionManager: object) -> dict:
        """
        Creates a dictionary of distances between atom groups.

        Parameters:
            atom_groups_ID (np.array): An array of atom IDs.
            AtomPositionManager (object): An object managing atom positions.

        Returns:
            dict: A dictionary of distances between atom groups.
        """
        distances_dict = { n:{n:0} for n in atom_groups_ID }
        
        for n1 in atom_groups_ID:

            if isinstance(n1, (list, tuple, np.ndarray)):
                # If n1 is a list, tuple, or an array of indices, calculate the mean position.
                n1_positions = np.mean([AtomPositionManager.atomPositions[ap] for ap in n1], axis=0)
            elif isinstance(n1, (int, np.integer, np.int64)):
                # If n1 is a single integer value, use the position directly associated with that index.
                n1_positions = AtomPositionManager.atomPositions[n1]
            else:
                raise TypeError("n1 must be an integer, a list, a tuple, or a numpy array of integers")

            for n2 in atom_groups_ID:
                if n1 < n2:
                    if isinstance(n2, (list, tuple, np.ndarray)):
                        # If n2 is a list, tuple, or an array of indices, calculate the mean position.
                        n2_positions = np.mean([AtomPositionManager.atomPositions[ap] for ap in n2], axis=0)
                    elif isinstance(n2, (int, np.integer, np.int64)):
                        # If n2 is a single integer value, use the position directly associated with that index.
                        n2_positions = AtomPositionManager.atomPositions[n2]
                    else:
                        raise TypeError("n1 must be an integer, a list, a tuple, or a numpy array of integers")

                    distances_dict[n1][n2] = AtomPositionManager.distance( n1_positions, n2_positions )

        return distances_dict

    def generate_configurational_space(self, values, verbose:bool=False, containers:list=None):
        """
        Generates the configurational space by creating various combinations of defects in the crystal structure.

        Parameters:
            values (dict): A dictionary containing parameters for generating the configurational space.

        Returns:
            list: A list of containers with updated configurations.
        """
        iterations = values.get('iterations', 1)
        distribution = values.get('distribution', 'uniform')
        fill = values.get('fill', False)
        repetitions = values.get('repetitions', 1)
        atom_groups = values.get('atom_groups', None)
        group_numbers = values.get('group_numbers', None)
        coefficient = values.get('coefficient', 10)
        Nw = values.get('Nw', None)

        containers_new = [] # here we alocate new configurations 
        containers = containers if isinstance(containers, list) else self.containers

        if not group_numbers or (isinstance(group_numbers,list) and len(group_numbers) == 0):
            group_numbers = np.ones( len(atom_groups) )
        
        for container_index, container in enumerate(containers):
            if verbose: print(f'>> Analising container {container_index}')
            for rep in range(repetitions):
                if verbose: print(f' - Repetitions : {rep} ({100*float(rep)/repetitions}%)')    
                
                container_copy = self.copy_and_update_container(container, f'/generate_configurational_space/{container_index}_{rep}', '')
                
                for ite in range(iterations):
                    if verbose: print(f' - iteration : {ite} ({100*float(ite)/iterations}%)')    
                    
                    atom_groups_ID = [self.get_atom_ids(container_copy.AtomPositionManager, group) for group in atom_groups]
                    if verbose: print(f' - Processing : {len(atom_groups_ID)} groups : { [len(agi) for agi in atom_groups_ID] } groups len ')    

                    if 'distance' in distribution:
                        distances_dict = self.get_distances_dict(list(set(item for sublist in atom_groups_ID for item in sublist)), container_copy.AtomPositionManager) 
                        if verbose: print(f' - Distance dict calculated (ok!) ')    
                    else:
                        distances_dict = {}

                    combinations = self.generate_combinations(atom_groups_ID, group_numbers)
                    if verbose: print(f' - Founded {len(combinations)} ')    

                    probabilities = [self.get_probability(  combination=c, distribution=distribution, AtomPositionManager=container_copy.AtomPositionManager, 
                                                            distances_dict=distances_dict, coefficient=coefficient) for c in combinations]
                    if verbose: print(f' - Probabilities calculated')    

                    probabilities_norm = np.array(probabilities) / np.sum(probabilities)
                    if verbose: print(f' - Probabilities normalized')

                    selected_index = np.random.choice(np.arange(len(combinations)), p=probabilities_norm)
                    selected_combination = np.array(combinations[selected_index]).flatten()

                    container_copy.AtomPositionManager.atomLabelsList = np.array(container_copy.AtomPositionManager.atomLabelsList)

                    if fill:
                        #translation = np.mean([container_copy.AtomPositionManager.atomPositions[n] for n in selected_combination], axis=0)
                        translation = np.sum([container_copy.AtomPositionManager.atomPositions[n]*container_copy.AtomPositionManager.covalent_radii[container_copy.AtomPositionManager.atomLabelsList[n]]**2 for n in selected_combination]) / np.sum([container_copy.AtomPositionManager.covalent_radii[container_copy.AtomPositionManager.atomLabelsList[n]]**2 for n in selected_combination])
                        r = 2 + np.max([container_copy.AtomPositionManager.distance(container_copy.AtomPositionManager.atomPositions[n1], container_copy.AtomPositionManager.atomPositions[n2]) for i, n1 in enumerate(combinations[selected_index]) for j, n2 in enumerate(combinations[selected_index][i:])]) 

                        # mean distance for N point in a r radius circle
                        if verbose: print(f' - Fill with water | sphere r={r} c={translation}')

                    container_copy.AtomPositionManager.remove_atom(selected_combination)
                    
                    if fill:
                        values = {
                            'density': 1,
                            'solvent': ['H2O'],
                            'molecules_number': {'H2O':Nw},
                            'max_iteration':100000,
                            'shape': 'sphere',
                            'size': [r],
                            'colition_tolerance': 1.7,
                            'translation': translation,
                            'distribution':'center',
                            'wrap': True,
                            'verbose':verbose
                        }

                        container_solvent = self.handleCLUSTER(values= {'ADD_SOLVENT':values}, containers=[container_copy])
                        
                        while container_solvent == False:
                            values['max_iteration'] += 5000
                            values['colition_tolerance'] -= .02
                            values['size'][0] -= .1

                            container_solvent = self.handleCLUSTER(values= {'ADD_SOLVENT':values}, containers=[container_copy])
                        
                        container_copy = container_solvent[0]

                containers_new.append(container_copy)
                if verbose: print(f' - Configuration generated (ok!)')
            

        self.containers = containers_new

        return containers_new

    def handleVacancy(self, container, values, container_index, file_location=None):
        sub_directories, containers = [], []

        container_copy = self.copy_and_update_container(container, '/Vacancy', file_location)
        container_copy.AtomPositionManager = CrystalDefectGenerator(Periodic_Object=container_copy.AtomPositionManager)
        all_vacancy_configs, all_vacancy_label = container_copy.AtomPositionManager.generate_all_vacancies()

        for cv_i, (vacancy_configs, vacancy_label) in enumerate(zip(all_vacancy_configs, all_vacancy_label)):
            container_copy2 = copy.deepcopy(container_copy)
            container_copy2.AtomPositionManager = vacancy_configs
            container_copy2.file_location = f'{container_copy.file_location}/{cv_i}_{vacancy_label}'
            sub_directories.append(f'{cv_i}_{vacancy_label}')
            containers.append(container_copy2)
        
        self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/Vacancy')
        return containers

    def handleDefect(self, container, values, container_index, file_location):

        for v in values:
            if v['defect'].upper() == 'SUBSTITUTION':
                self.generate_all_substitutional_impurity( container=container, species=v['species'], new_species=v['new_species'], weights=v['weights'] )

    # ------------------------------------------------------------------------------------#
    def _generate_defect_configurations(self, defect_introducer, configurations:list=None):
        """
        General method to generate defect configurations.

        Parameters:
        - defect_introducer (function): Function that introduces the specific defect.
        - positions (list or None): Positions to introduce defects.
        - labels (list or None): Labels of atoms to introduce defects.

        Returns:
        - tuple: Two lists containing defect configurations and corresponding labels.
        """
        all_configs = []
        all_labels = []

        for config in configurations:
            temp_manager = copy.deepcopy(self)
            method = getattr(temp_manager, defect_introducer, None)

            if callable(method):
                method(**config)
            else:
                print(f"ERROR '{defect_introducer}' does not exist.")

            if not self._is_redundant(all_configs, temp_manager):
                all_configs.append(temp_manager)
                all_labels.append( '_'.join([str(c) for c in config.values()]) )

        return all_configs, all_labels


    # ------------------------------------------------------------------------------------ #
    def generate_all_vacancies(self, atomlabel=None):
        """
        Generate all possible vacancy configurations for the system.

        Parameters:
        - atomlabel (list or None): Specifies the type of atom for which vacancies should be generated.

        Returns:
        - tuple: Two lists containing vacancy configurations and corresponding labels.
        """
        # Parameters:
        atomlabel = list(atomlabel) if atomlabel is str else atomlabel

        # Determine the indices at which vacancies should be introduced
        if atomlabel:   indices = [i for i, label in enumerate(self.atomLabelsList) if label in atomlabel]
        else:           indices = np.array(range(self._atomCount), dtype=np.int64)

        configurations = [ {'atom_index':i} for i in indices  ]
        return self._generate_defect_configurations('introduce_vacancy', configurations)
    
    def generate_all_interstitial(self, atomlabel:list, new_atom_position:np.array=None):
        """

        """
        # Parameters: 
        new_atom_position = new_atom_position if new_atom_position is not None else self._find_volumes_center()
        new_atom_position = [nap for nap in new_atom_position if self.is_point_inside_unit_cell(nap) ] 

        # Determine the indices at which vacancies should be introduced
        if atomlabel:   indices = [i for i, label in enumerate(self.atomLabelsList) if label in atomlabel]
        else:           indices = np.array(range(self._atomCount), dtype=np.int64)

        configurations = [ {'new_atom_label':al, 'new_atom_position':nap } for al in atomlabel for nap in new_atom_position ]
        return self._generate_defect_configurations('introduce_interstitial', configurations)
    
    def generate_all_self_interstitial(self, atomlabel:list, new_atom_position:np.array=None):
        """

        """
        return self.generate_all_interstitial(atomlabel=self.uniqueAtomLabels, new_atom_position=None)
    
    def generate_one_substitutional_impurity(self, container, species:list, new_species:list):
        '''
        md = MBTR.MDTR(lattice_vectors=container.AtomPositionManager.latticeVectors, 
                    atomLabelsList=container.AtomPositionManager.atomLabelsList, 
                    atomPositions=container.AtomPositionManager.atomPositions, )

        rep, rep_div = md.get_mdtr()
        similarity_matrix = md.get_selfsimilarity_matrix( np.sum( np.abs( rep_div[0,:,:,:]), axis=2).T) 

        groups = md.find_related_atoms_groups(similarity_matrix, threshold=0.82)
        '''
        from ...descriptor import MBTR

        ans = []
        for i, ID in enumerate(container.AtomPositionManager.atomLabelsList):
            if ID in species:
                for ID2 in new_species:
                    container_copy = copy.deepcopy(container)
                    container_copy.AtomPositionManager.set_ID( atom_index=i, ID=ID2 )
                    ans.append(container_copy)

                    md = MBTR.MDTR(lattice_vectors=container_copy.AtomPositionManager.latticeVectors, 
                                atomLabelsList=container_copy.AtomPositionManager.atomLabelsList, 
                                atomPositions=container_copy.AtomPositionManager.atomPositions, )

                    rep, rep_div = md.get_mdtr()
                    #similarity_matrix = md.get_selfsimilarity_matrix( np.sum( np.abs( rep_div[0,:,:,:]), axis=2).T) 

                    #groups = md.find_related_atoms_groups(similarity_matrix, threshold=0.82)
                    print( i, rep.shape)
                    ans1.append( np.abs(rep[0,:]) )
                    plt.plot( np.abs(rep[0,:]) )
                    
    def generate_all_substitutional_impurity(self, container, species:list, new_species:list, ):
        """

        """
        nes = self.generate_one_substitutional_impurity(container=container, species=species, new_species=new_species)

        '''
        md = MBTR.MDTR(lattice_vectors=self.containers[0].AtomPositionManager.latticeVectors, 
                    atomLabelsList=self.containers[0].AtomPositionManager.atomLabelsList, 
                    atomPositions=self.containers[0].AtomPositionManager.atomPositions, )

        rep, rep_div = md.get_mdtr()
        similarity_matrix = md.get_selfsimilarity_matrix( np.sum( np.abs( rep_div[0,:,:,:]), axis=2).T) 

        groups = md.find_related_atoms_groups(similarity_matrix, threshold=0.82)
        print(groups)
        print( self.containers[0].AtomPositionManager.atomPositions[4,:] )
        print( self.containers[0].AtomPositionManager.atomPositions[5,:] )
        print( self.containers[0].AtomPositionManager.atomPositions[10,:] )
        print(rep.shape , rep_div.shape) 
        print('dif', np.sum( (np.abs(rep_div[0,:,13,0].T) - np.abs(rep_div[0,:,17,0].T))**2 )**0.5 )
        print('dif', np.sum( (np.abs(rep_div[0,:,0,0].T) - np.abs(rep_div[0,:,1,0].T))**2 )**0.5 )
        print('dif', np.sum( (np.abs(rep_div[0,:,4,0].T) - np.abs(rep_div[0,:,5,0].T))**2 )**0.5 )
        print('dif', np.sum( (np.abs(rep_div[0,:,12,0].T) - np.abs(rep_div[0,:,13,0].T))**2 )**0.5 )
        mask = self.containers[0].AtomPositionManager.atomLabelsList == 'Ni'
                
        plt.plot( np.abs(rep_div[0,:,4,1].T) )
        plt.plot( np.abs(rep_div[0,:,5,1].T) )
        plt.plot( np.abs(rep_div[0,:,10,2].T) )
        #similarity_matrix[similarity_matrix>0.8] = 1
        #similarity_matrix[similarity_matrix<=0.8] = 0
        plt.matshow( similarity_matrix )

        plt.show()
        print(a.shape, b.shape)

        asdf
        '''
        '''
        # Parameters: 
        atomlabel = atomlabel if atomlabel is not None else self.uniqueAtomLabels
        new_atom_label = list(new_atom_label) if new_atom_label is list else new_atom_label
        # Determine the indices at which vacancies should be introduced
        if atomlabel:   indices = [i for i, label in enumerate(self.atomLabelsList) if label in atomlabel]
        else:           indices = np.array(range(self._atomCount), dtype=np.int64)
        print(indices)

        configurations = [ {'atom_index':i, 'new_atom_label':nal } for i in indices for nal in new_atom_label ]
        return self._generate_defect_configurations('introduce_substitutional_impurity', configurations)

        '''

    def _find_volumes_center(self, atomPositions:np.array=None):
        """
        Finds potential volumes for new atoms in a structure.

        Args:
            atom_coordinates (list of list of floats): List of existing atom coordinates.

        Returns:
            list of Voronoi region vertices: List of vertices of the Voronoi regions.
        """
        # Convert coordinates to a NumPy array.
        atomPositions = atomPositions if atomPositions is not None else self.atomPositions

        # Calculate the Voronoi decomposition.
        vor = Voronoi(atomPositions)

        return vor.vertices


'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/dataset/CoFeNiOOH_jingzhu/surf_CoFe_2H_4OH/vacancy'
ap = CrystalDefectGenerator(file_location=path+'/POSCAR')
ap.readPOSCAR()
all_configs, all_labels = ap.generate_all_substitutional_impurity( 'V') # generate_all_vacancies generate_all_substitutional_impurity generate_all_interstitial


for a, b in zip(all_configs, all_labels):
    print(a.atomCountByType, b)
sadfsafd



path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/*OH surface for pure NiOOH'
ap = CrystalDefectGenerator(file_location=path+'/SUPERCELL')
ap.readSIFile()
ap.is_surface = True
print( ap.latticeType )
#ap.introduce_vacancy(atom_index=10)
res,_ = ap.generate_all_vacancies()

ap.exportAsPOSCAR(path+'/POSCAR_d1')
for i, n in enumerate(res):
    n.exportAsPOSCAR(path+f'/POSCAR_d{i}')
'''
