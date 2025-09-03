try:
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class AtomPositionManager(FileManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._comment = None
        self._atomCount = None  # N total number of atoms
        self._scaleFactor = None  # scale factor
        self._uniqueAtomLabels = None  # [Fe, N, C, H]
        self._atomCountByType = None  # [n(Fe), n(N), n(C), n(H)]
        self._selectiveDynamics = None  # bool 
        self._atomPositions = None  # np.array(N, 3)
        self._atomicConstraints = None

        self._atomLabelsList = None  # [Fe, N, N, N, N, C, C, C, C, H]
        self._fullAtomLabelString = None  # FeFeFeNNNNNNNCCCCCCCCCCCCCCCHHHHHHHHHHHHHHHH
        self.__atomPositions_tolerance = 1e-2

        self._distance_matrix = None
        
        self._total_charge = None
        self._magnetization = None
        self._total_force = None
        self._E = None
        self._Edisp = None
        self._IRdisplacement = None
        
    @property
    def distance_matrix(self):
        if self._distance_matrix is not None:
            return self._distance_matrix
        elif self._atomPositions is not None:
            from scipy.spatial.distance import cdist 
            self._distance_matrix = cdist(self._atomPositions, self._atomPositions, 'euclidean')
            return self._distance_matrix
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute _atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def scaleFactor(self):
        if self.isnum(self._scaleFactor) or self._scaleFactor is list:
            self._scaleFactor = np.array(self._scaleFactor)
            return np.array(self._scaleFactor)
        elif self._scaleFactor is None: 
            self._scaleFactor = [1]
            return self._scaleFactor
        else:
            return None

    @property
    def atomCount(self):
        if self._atomCount is not None:
            return np.array(self._atomCount)
        elif self._atomPositions is not None: 
            self._atomCount = self._atomPositions.shape[0] 
            return self._atomCount
        elif self._atomLabelsList is not None: 
            self._atomCount = self._atomLabelsList.shape
            return self._atomCount   
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute _atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def uniqueAtomLabels(self):
        if self._uniqueAtomLabels is not None:
            return self._uniqueAtomLabels
        elif self._atomLabelsList is not None: 
            self._uniqueAtomLabels = list(dict.fromkeys(self._atomLabelsList).keys())
            return np.array(self._uniqueAtomLabels)
        elif'_atomLabelsList' not in self.__dict__:
            raise AttributeError("Attribute _atomLabelsList must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def atomCountByType(self):
        if self._atomCountByType is not None:
            return self._atomCountByType
        elif self._atomLabelsList is not None: 
            atomCountByType, atomLabelByType = {}, []
            for a in self._atomLabelsList:
                if not a in atomCountByType:
                    atomLabelByType.append(1)
                    atomCountByType[a] = len(atomLabelByType)-1
                else:
                    atomLabelByType[atomCountByType[a]] += 1
            self._atomCountByType = np.array(atomLabelByType)
            return self._atomCountByType
        elif'_atomLabelsList' not in self.__dict__:
            raise AttributeError("Attribute _atomLabelsList must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def atomLabelsList(self):
        if '_atomCountByType' not in self.__dict__ or '_uniqueAtomLabels' not in self.__dict__:
            raise AttributeError("Attributes _atomCountByType and _uniqueAtomLabels must be initialized before accessing atomLabelsList.")
        elif self._atomLabelsList is None and not self._atomCountByType is None and not self._uniqueAtomLabels is None: 
            return np.array([label for count, label in zip(self._atomCountByType, self._uniqueAtomLabels) for _ in range(count)])
        else:
            return  self._atomLabelsList 

    @property
    def fullAtomLabelString(self):
        if '_atomCountByType' not in self.__dict__ or '_uniqueAtomLabels' not in self.__dict__:
            raise AttributeError("Attributes _atomCountByType and _uniqueAtomLabels must be initialized before accessing fullAtomLabelString.")
        elif self._fullAtomLabelString is None and not self._atomCountByType is None and not self._uniqueAtomLabels is None: 
            self._fullAtomLabelString = ''.join([label*count for count, label in zip(self._atomCountByType, self._uniqueAtomLabels)])
            return self._fullAtomLabelString
        else:
            return  self._fullAtomLabelString 

    @property
    def atomPositions(self):
        if self._atomPositions is list:
            return np.array(self._atomPositions)
        else:
            return self._atomPositions

    def convert_to_periodic(self):
        return PeriodicSystem(**self.attributes)
    
    def convert_to_non_periodic(self):
        return NonPeriodicSystem(**self.attributes)

    def distance(self, r1, r2): return np.linalg.norm(r1, r2)

    def remove_atom(self, atom_index: int):
        """Remove an atom at the given index."""
        self._atomPositions = np.delete(self.atomPositions, atom_index, axis=0)
        self._atomPositions_fractional = np.delete(self._atomPositions_fractional, atom_index, axis=0)
        self._atomLabelsList = np.delete(self.atomLabelsList, atom_index)
        self._atomicConstraints = np.delete(self.atomicConstraints, atom_index, axis=0)
        self._total_charge = np.delete(self.total_charge, atom_index) if self._total_charge is not None else self._total_charge
        self._magnetization = np.delete(self.magnetization, atom_index) if self._magnetization is not None else self._magnetization
        self._total_force = np.delete(self.total_force, atom_index) if self._total_force is not None else self._total_force
        self._atomCount -= 1
        self._atomCountByType = None
        self._fullAtomLabelString = None
        self._uniqueAtomLabels = None

        if self._distance_matrix is not None:
            self._distance_matrix = np.delete(self._distance_matrix, var, axis=0)  # Eliminar fila
            self._distance_matrix = np.delete(self._distance_matrix, var, axis=1)  # Eliminar columna


    def find_n_closest_neighbors(self, position, n):
        """Find the n closest neighbors to a given atom."""
        #distance_matrix = self.distanceamtrix
        #distances = distance_matrix[atom_index]
        
        # Sort the distances and get the indices of the n closest neighbors.
        # We exclude the first index because it's the atom itself (distance=0).
        distances = [self.distance( position, a) for a in self.atomPositions ]
        closest_indices = np.argsort( distances )[:n]
        
        # Get the labels and positions of the closest neighbors.
        closest_labels = [self._atomLabelsList[i] for i in closest_indices]
        closest_distance = [ distances[i] for i in closest_indices]
        
        return closest_indices, closest_labels, closest_distance

    def compare_chemical_environments(self, distances1, labels1, distances2, labels2, label_weights=None, distance_decay=1.0):
        """
        Compare two chemical environments and return a similarity score.

        Parameters:
        - distances1, distances2: List of distances to the atoms in the environments.
        - labels1, labels2: List of labels indicating the type of each atom in the environments.
        - label_weights: Dictionary assigning weights to each type of atom label. If None, all weights are set to 1.
        - distance_decay: A decay factor for the influence of distance in the similarity score.

        Returns:
        - float: A similarity score. Lower values indicate more similar environments.
        """
        if label_weights is None:
            label_weights = {label: 1.0 for label in set(labels1 + labels2)}
        
        # Initialize similarity score
        similarity_score = 0.0

        for d1, l1 in zip(distances1, labels1):
            min_diff = float('inf')
            for d2, l2 in zip(distances2, labels2):
                if l1 == l2:
                    diff = np.abs(d1 - d2)
                    min_diff = min(min_diff, diff)
            
            if min_diff != float('inf'):
                weight = label_weights.get(l1, 1.0)
                similarity_score += weight * np.exp(-distance_decay * min_diff)

        return similarity_score

    def get_plane(self, atom1, atom2, atom3):
        v1 = self.atomPositions[atom1, :] - self.atomPositions[atom2, :]
        v2 = self.atomPositions[atom2, :] - self.atomPositions[atom3, :]
        # | i        j     k   | #
        # | v1x    v1y    v1z  | #
        # | v2x    v2y    v2z  | #
        return np.array([   v1[1]*v2[2]-v1[2]*v2[1],
                            v1[2]*v2[0]-v1[0]*v2[2],
                            v1[0]*v2[1]-v1[1]*v2[0], ])

    def get_dihedric(self, atom1, atom2, atom3, atom4):
        p1 = self.get_plane(atom1, atom2, atom3)
        p2 = self.get_plane(atom2, atom3, atom4)
        '''
     ****         xxx
        ****    xxx
          ****xxxfilename
            xxx***
          xxx   *****
        xxx (P2)   ***** (P1)
        '''
        return self.get_vector_angle(p1, p2)

    def get_angle(self, atom1, atom2, atom3):
        v1 = self.atomPositions[atom1, :] - self.atomPositions[atom2, :]
        v2 = self.atomPositions[atom2, :] - self.atomPositions[atom3, :]

        return self.get_vector_angle(v1, v2)

    def get_vector_angle(self, v1, v2):
        '''
        1.     The get_vector_angle function takes two vectors as input. These vectors represent the direction and magnitude of an angle between the vectors.
        2.     The function calculates the angle between the vectors using the arccosine function.
        3.     The angle returned is a unit vector in the direction of the angle.
        '''
        unit_vector_1 = v1 / np.linalg.norm(v1)
        unit_vector_2 = v2 / np.linalg.norm(v2)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        angle = np.arccos(dot_product)

        return angle


    def group_elements_and_positions(self, atomLabelsList:list=None, atomPositions:list=None):
        # Verificar que la longitud de element_labels coincide con el número de filas en position_matrix
        atomLabelsList = atomLabelsList if atomLabelsList is not None else self.atomLabelsList
        atomPositions = atomPositions if atomPositions is not None else self.atomPositions

        # Crear un diccionario para almacenar los índices de cada tipo de elemento
        element_indices = {}
        for i, label in enumerate(atomLabelsList):
            if label not in element_indices:
                element_indices[label] = []
            element_indices[label].append(i)

        # Crear una nueva lista de etiquetas y una nueva matriz de posiciones
        atomLabelsList_new = []
        atomPositions_new = []
        uniqueAtomLabels_new = element_indices.keys()
        for label in element_indices:
            atomLabelsList_new.extend([label] * len(element_indices[label]))
            atomPositions_new.extend(atomPositions[element_indices[label]])

        self._atomLabelsList = atomLabelsList_new
        self._atomPositions = np.array(atomPositions_new)
        self._uniqueAtomLabels = None  # [Fe, N, C, H]
        self._atomCountByType = None  # [n(Fe), n(N), n(C), n(H)]
        self._fullAtomLabelString = None  # FeFeFeNNNNNNNCCCCCCCCCCCCCCCHHHHHHHHHHHHHHHH

        return True

    def atomLabelFilter(self, ID, v=False):  
        return np.array([ True if n in ID else False for n in self.atomLabelsList])

    def exportAsPDB(self, file_location:str=None, bond_distance:float=2.3, v:bool=False) -> bool:
        if v: print(f' Export as PDB >> {file_location}')
        
        file_location  = file_location  if not file_location  is None else self.file_location+'.pdb'

        filePDB = open(f'{file_location}', 'w')
        for i, pos in enumerate(self.atomPositions):     #loop over different atoms
            S = "ATOM  %5d %2s   MOL     1  %8.3f%8.3f%8.3f  1.00  0.00\n" % (int(i+1), self.atomLabelsList[i], pos[0], pos[1], pos[2])
            filePDB.write(S) #ATOM

        for i1, pos1 in enumerate(self.atomPositions):       #loop over different atoms
            for i2, pos2 in enumerate(self.atomPositions):
                if  i1>i2 and np.linalg.norm(pos1-pos2) < bond_distance:
                    filePDB.write(f'CONECT{int(i1+1):>5}{int(i2+1):>5}\n')

        filePDB.close()
        return True

    def exportAsPOSCAR(self, file_location:str=None, v:bool=False) -> bool:
        file_location  = file_location  if not file_location  is None else self.file_location+'POSCAR' if self.file_location is str else self.file_location
        self.group_elements_and_positions()

        with open(file_location, 'w') as file:
            # Comentario inicial
            file.write(f'POSCAR : JML code \n')

            # Factor de escala
            file.write(f"{' '.join(map(str, self.scaleFactor))}\n")

            # Vectores de la celda unitaria
            for lv in self.latticeVectors:
                file.write('{:>18.15f}\t{:>18.15f}\t{:>18.15f}\n'.format(*lv))

            # Tipos de átomos y sus números
            file.write('    '.join(self.uniqueAtomLabels) + '\n')
            file.write('    '.join(map(str, self.atomCountByType)) + '\n')

            # Opción para dinámica selectiva (opcional)
            if self._selectiveDynamics:     file.write('Selective dynamics\n')
            # Tipo de coordenadas (Direct o Cartesian)
            aCT = 'Cartesian' if self._atomCoordinateType[0].capitalize() in ['C', 'K'] else 'Direct'
            file.write(f'{aCT}\n')

            # Coordenadas atómicas y sus restricciones
            for i, atom in enumerate(self._atomPositions if self._atomCoordinateType[0].capitalize() in ['C', 'K'] else self._atomPositions_fractional):
                coords = '\t'.join(['{:>18.15f}'.format(n) for n in atom])
                constr = '\tT\tT\tT' if self._atomicConstraints is None else '\t'.join(['T' if n else 'F' for n in self._atomicConstraints[i]]) 
                file.write(f'\t{coords}\t{constr}\n')

            # Comentario final (opcional)
            file.write('Comment_line\n')

    def export_as_xyz(self, file_location:str=None, save_to_file:str='w', verbose:bool=False) -> str:
        """
        Export atomistic information in the XYZ format.

        Parameters:
            file_location (str): The location where the XYZ file will be saved. Ignored if save_to_file is False.
            save_to_file (bool): Flag to control whether to save the XYZ content to a file.
            verbose (bool): Flag to print additional information, if True.

        Returns:
            str: The generated XYZ content.
        """
        file_location  = file_location  if not file_location  is None else self.file_location+'config.xyz' if self.file_location is str else self.file_location
        self.group_elements_and_positions()

        # Initialize an empty string to store the XYZ content
        xyz_content = ""

        # Write the number of atoms
        xyz_content += f"{self.atomCount}\n"

        # Write information about the unit cell, energy, etc.
        lattice_str = " ".join(map(str, self._latticeVectors.flatten()))
        xyz_content += f'Lattice="{lattice_str}" Properties=species:S:1:pos:R:3:masses:R:1:DFT_forces:R:3 DFT_energy={self._E} ...\n'

        # Column widths for alignment. These can be adjusted.
        col_widths = {'element': 5, 'position': 12, 'mass': 12, 'force': 12}

        # Write the atom positions, masses, and forces
        for i in range(self.atomCount):
            atom_label = self.atomLabelsList[i]
            pos = " ".join(map("{:12.6f}".format, self.atomPositions[i])) if self.atomPositions is not None else ''
            mass = "{:12.6f}".format(self._atomic_mass.get(atom_label, float('nan')))  # Retrieve mass from the predefined atom_dict
            force = " ".join(map("{:12.6f}".format, self.total_force[i])) if self.total_force is not None else ''  # Assuming that self._total_force is an array (N, 3)
            xyz_content += f"{atom_label:<{col_widths['element']}}{pos}{mass}{force}\n"

        # Save the generated XYZ content to a file if file_location is specified and save_to_file is True
        if file_location and save_to_file:
            with open(file_location, save_to_file) as f:
                f.write(xyz_content)
            if verbose:
                print(f"XYZ content has been saved to {file_location}")

        return xyz_content
