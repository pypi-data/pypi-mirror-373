# En __init__.py del paquete que contiene AtomPositionManager
try:
    from sage_lib.AtomPositionManager import AtomPositionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPositionManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class PeriodicSystem(AtomPositionManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._reciprocalLatticeVectors = None # [b1, b2, b3]
        self._latticeVectors = None # [a1,a2,a3]
        self._latticeVectors_inv = None # [a1,a2,a3]

        self._symmetryEquivPositions = None
        self._atomCoordinateType = None  # str cartedian direct
        self._latticeParameters = None # []
        self._latticeAngles = None  # [alpha, beta, gamma]
        self._cellVolumen = None  # float

        self._atomPositions_fractional = None

        self._latticeType = None
        self._latticeType_tolerance = 1e-4

        self._is_surface = False
        self._distance_matrix = None

    @property
    def distance_matrix(self):
        if self._distance_matrix is not None:
            return self._distance_matrix
        elif self._atomPositions is not None:
            distance_matrix = np.zeros((self.atomCount, self.atomCount))
            for i in range(self.atomCount):
                for j in range(i, self.atomCount):
                    distance_matrix[i, j] = self.minimum_image_distance( self.atomPositions[i], self.atomPositions[j] )
            self._distance_matrix = distance_matrix
            return self._distance_matrix
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute _atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def latticeType(self):
        if not self._latticeType is None:
            return np.array(self._latticeType)
        elif self.latticeVectors is not None and self.latticeAngles is not None:
            a,b,c = [np.linalg.norm(vec) for vec in self.latticeVectors]
            alpha, beta, gamma = self.latticeAngles 

            # Check if angles are 90 degrees within tolerance
            is_90 = lambda angle: abs(angle - np.pi/2) < self._latticeType_tolerance

            # Check if angles are 120 or 60 degrees within tolerance
            is_120 = lambda angle: abs(angle - np.pi*2/3) < self._latticeType_tolerance
            is_60 = lambda angle: abs(angle - np.pi/3) < self._latticeType_tolerance

            # Check if lattice constants are equal within tolerance
            equal_consts = lambda x, y: abs(x - y) < self._latticeType_tolerance
            
            if all(map(is_90, [alpha, beta, gamma])):
                if equal_consts(a, b) and equal_consts(b, c):
                    return "Cubic"
                elif equal_consts(a, b) or equal_consts(b, c) or equal_consts(a, c):
                    return "Tetragonal"
                else:
                    return "Orthorhombic"

            elif is_90(alpha) and is_90(beta) and is_120(gamma):
                if equal_consts(a, b) and not equal_consts(b, c):
                    return "Hexagonal"

            elif is_90(alpha) and is_90(beta) and is_90(gamma):
                if equal_consts(a, b) and not equal_consts(b, c):
                    return "Hexagonal"  # This is actually a special case sometimes considered under Tetragonal

            elif is_90(alpha):
                return "Monoclinic"

            else:
                return "Triclinic"

            return self._latticeType
        elif 'latticeVectors' not in self.__dict__:
            raise AttributeError("Attributes latticeVectors and latticeAngles must be initialized before accessing latticeParameters.")

    @property
    def atomPositions_fractional(self):
        if not self._atomPositions_fractional is None:
            return self._atomPositions_fractional
        elif self._atomPositions is not None:
            self._atomPositions_fractional = np.dot(self._atomPositions, self.latticeVectors_inv)
            return self._atomPositions_fractional
        elif '_atomPositions' not in self.__dict__:
            raise AttributeError("Attributes _atomPositions must be initialized before accessing latticeParameters.")

    @property
    def atomPositions(self):
        if not self._atomPositions is None:
            return np.array(self._atomPositions)
        elif self._atomPositions_fractional is not None:
            self._atomPositions = np.dot(self.latticeVectors, self._atomPositions_fractional.T).T
            return self._atomPositions
        elif '_atomPositions_fractional' not in self.__dict__:
            raise AttributeError("Attributes _atomPositions_fractional must be initialized before accessing latticeParameters.")

    @property
    def reciprocalLatticeVectors(self):
        if not self._reciprocalLatticeVectors is None:
            return self._reciprocalLatticeVectors
        elif self._latticeVectors is not None:
            a1,a2,a3 = self._latticeVectors
            self._reciprocalLatticeVectors = np.array([
                    2 * np.pi * np.cross(a2, a3) / np.dot(a1, np.cross(a2, a3)),
                    2 * np.pi * np.cross(a3, a1) / np.dot(a2, np.cross(a3, a1)),
                    2 * np.pi * np.cross(a1, a2) / np.dot(a3, np.cross(a1, a2)) 
                                                    ])
            return self._reciprocalLatticeVectors


        elif '_latticeVectors' not in self.__dict__:
            raise AttributeError("Attributes _latticeParameters and _latticeAngles must be initialized before accessing latticeParameters.")

    @property
    def latticeAngles(self):
        if not self._latticeAngles is None:
            return self._latticeAngles
        elif self._latticeVectors is not None:
            a1,a2,a3 = self._latticeVectors 
            # Calculate magnitudes of the lattice vectors
            norm_a1 = np.linalg.norm(a1)
            norm_a2 = np.linalg.norm(a2)
            norm_a3 = np.linalg.norm(a3)
            # Calculate the angles in radians
            self._latticeAngles = np.array([
                    np.arccos(np.dot(a2, a3) / (norm_a2 * norm_a3)),
                    np.arccos(np.dot(a1, a3) / (norm_a1 * norm_a3)),
                    np.arccos(np.dot(a1, a2) / (norm_a1 * norm_a2))
                    ])
            return self._latticeAngles
        elif '_latticeVectors' not in self.__dict__:
            raise AttributeError("Attributes _latticeVectors and _latticeAngles must be initialized before accessing latticeParameters.")


    @property
    def latticeVectors(self):
        if not self._latticeVectors is None:
            return self._latticeVectors
        elif self._latticeAngles is not None and self._latticeParameters is not None:
            m1, m2, m3 = self._latticeParameters
            alpha, beta, gamma = self._latticeAngles  # Convert to radians
            
            self._latticeVectors = np.array([
                    [m1, 0, 0],
                    [m2 * np.cos(gamma), m2 * np.sin(gamma), 0],
                    [m3 * np.cos(beta),
                     m3 * (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma),
                     m3 * np.sqrt(1 - np.cos(beta)**2 - ((np.cos(alpha) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma))**2)
                                            ] ])
            return self._latticeVectors
        elif '_latticeParameters' not in self.__dict__ or '_latticeAngles' not in self.__dict__:
            raise AttributeError("Attributes _latticeParameters and _latticeAngles must be initialized before accessing latticeParameters.")
 
    @property
    def latticeVectors_inv(self):
        if not self._latticeVectors_inv is None:
            return self._atomPositions_fractional
        elif self.latticeVectors is not None:
            self._latticeVectors_inv = np.linalg.inv(self.latticeVectors)
            return self._latticeVectors_inv
        elif 'latticeVectors' not in self.__dict__:
            raise AttributeError("Attributes latticeVectors must be initialized before accessing latticeParameters.")

    @property
    def latticeParameters(self):
        if '_latticeParameters' not in self.__dict__ or '_latticeParameters' not in self.__dict__:
            raise AttributeError("Attributes _latticeParameters and _latticeParameters must be initialized before accessing latticeParameters.")
        elif not self._latticeParameters is None:
            return self._latticeParameters  
        elif self._latticeVectors is not None and self._latticeParameters is not None:
            self._latticeParameters = [np.linalg.norm(self.latticeVectors) for vector in vectors]
            return self._latticeParameters
        else:
            return None

    @property
    def cellVolumen(self):
        if '_cellVolumen' not in self.__dict__ or '_cellVolumen' not in self.__dict__:
            raise AttributeError("Attributes _cellVolumen and _cellVolumen must be initialized before accessing cellVolumen.")
        elif not self._cellVolumen is None: 
            return  self._cellVolumen 
        elif self._latticeParameters is not None or self._latticeAngles is not None:
            a, b, c = self._latticeParameters
            alpha, beta, gamma = self._latticeAngles  # Convert to radians

            # Calculate volume using the general formula for triclinic cells
            self._cellVolumen = a * b * c * np.sqrt(
                1 - np.cos(alpha)**2 - np.cos(beta)**2 - np.cos(gamma)**2 +
                2 * np.cos(alpha) * np.cos(beta) * np.cos(gamma)
            )
            return self._cellVolumen
        else:
            return None

    def to_fractional_coordinates(self, cart_coords):
        inv_lattice_matrix = np.linalg.inv(self.latticeVectors)
        return np.dot(inv_lattice_matrix, cart_coords.T).T
    
    def to_cartesian_coordinates(self, frac_coords):
        return np.dot(self.latticeVectors.T, frac_coords.T).T
    
    def distance(self, r1, r2): return self.minimum_image_distance(r1, r2)

    def pack_to_unit_cell(self, ):
        # Apply minimum image convention
        self._atomPositions_fractional = self.atomPositions_fractional%1.0
        
        # Convert back to Cartesian coordinates
        self._atomPositions = np.dot(self.atomPositions_fractional, self.latticeVectors)

    def minimum_image_distance(self, r1, r2, n_max=3):
        """
        Calcula la distancia mínima entre dos puntos en un sistema periódico usando NumPy.
        
        Parámetros:
        r1, r2 : arrays de NumPy
            Las coordenadas cartesianas de los dos puntos.
        lattice_vectors : matriz de 3x3
            Los vectores de la red cristalina.
        n_max : int
            El número máximo de imágenes a considerar en cada dimensión.
            
        Retorna:
        d_min : float
            La distancia mínima entre los dos puntos.
        """
        
        # Generar todas las combinaciones de índices de celda
        n_values = np.arange(-n_max, n_max + 1)
        n_combinations = np.array(np.meshgrid(n_values, n_values, n_values)).T.reshape(-1, 3)
        
        # Calcular todas las imágenes del segundo punto
        r2_images = r2 + np.dot(n_combinations, self.latticeVectors)
        
        # Calcular las distancias entre r1 y todas las imágenes de r2
        distances = np.linalg.norm(r1 - r2_images, axis=1)
        
        # Encontrar y devolver la distancia mínima
        d_min = np.min(distances)
        return d_min

    def cellDuplication(self, factor:np.array=np.array([2,2,1], dtype=np.int64)):
        factor = np.array(factor, dtype=np.int64)
        atomPositions = np.zeros( (self._atomCount*np.prod(factor),3) )
        atomicConstraints = np.zeros( (self._atomCount*np.prod(factor),3), dtype=str )

        index = 0
        for n, atom in enumerate(self._atomPositions):

            for fx in range(factor[0]):
                for fy in range(factor[1]):
                    for fz in range(factor[2]):
                        atomPositions[index,:] = atom + np.dot( ap.latticeVectors,np.array([fx,fy,fz]))
                        atomicConstraints[index,:] = self._atomicConstraints[n]
                        index += 1

        self._atomicConstraints = atomicConstraints
        self._atomPositions = atomPositions
        self._latticeVectors = self._latticeVectors*factor
        self._atomCount *= np.prod(factor)
        self._atomCountByType *= np.prod(factor)

        self._atomLabelsList = None
        self._fullAtomLabelString = None

    def find_opposite_atom(self, atom_position, label, tolerance_z=1.8, tolerance=6):
        """Find the symmetrically opposite atom's index."""
        # Convert to fractional coordinates and find center
        lattice_matrix = np.array(self._latticeVectors)
        atom_frac = self.to_fractional_coordinates(atom_position)
        inv_lattice_matrix = np.linalg.inv(lattice_matrix)
        center_frac = np.mean(np.dot(inv_lattice_matrix, self.atomPositions.T).T, axis=0)

        # Find opposite atom in fractional coordinates
        opposite_atom_position_frac = 2 * center_frac - atom_frac
        opposite_atom_position = np.dot(lattice_matrix, opposite_atom_position_frac)

        removed_atom_closest_indices, removed_atom_closest_labels, removed_atom_closest_distance = self.find_n_closest_neighbors(atom_position, 4)

        # Calculate distances to find opposite atom
        distances = np.zeros(self._atomCount)
        for i, a in enumerate(self.atomPositions):
            if (self.atomLabelsList[i] == label and
                np.abs(atom_position[2] - a[2]) >= tolerance_z and
                np.abs(opposite_atom_position[2] - a[2]) <= tolerance_z):

                closest_indices, closest_labels, closest_distance = self.find_n_closest_neighbors(a, 4)
                distances[i] = self.compare_chemical_environments(removed_atom_closest_distance, removed_atom_closest_labels,
                                                            closest_distance, closest_labels)#self.minimum_image_distance(opposite_atom_position, a)

        opposite_atom_index = np.argmax(distances)
        opposite_atom_distance = np.max(distances)

        return opposite_atom_index if opposite_atom_distance >= 2 else None

    def summary(self, v=0):
        text_str = ''
        text_str += f'{self._latticeVectors} \n'
        text_str += f'Atom:{self._atomCount} \n'
        text_str += f'Atom:{self._uniqueAtomLabels} \n'
        text_str += f'Atom:{self._atomCountByType} \n'

        return text_str

    def readPOSCAR(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self._file_location

        lines = [n for n in self.read_file() ]
        
        self._comment = lines[0].strip()
        self._scaleFactor = list(map(float, lines[1].strip().split()))
        
        # Reading lattice vectors
        self._latticeVectors = np.array([list(map(float, line.strip().split())) for line in lines[2:5]])
        
        # Species names (optional)
        if self.is_number(lines[5].strip().split()[0]):
            self._uniqueAtomLabels = None
            offset = 0
        else:
            self._uniqueAtomLabels = lines[5].strip().split()
            offset = 1
  
        # Ions per species
        self._atomCountByType = np.array(list(map(int, lines[5+offset].strip().split())))
        
        # Selective dynamics (optional)
        if not self.is_number(lines[6+offset].strip()[0]):
            if lines[6+offset].strip()[0].capitalize() == 'S':
                self._selectiveDynamics = True
                offset += 1
            else:
                self._selectiveDynamics = False
        
        # atomic coordinated system
        if lines[6+offset].strip()[0].capitalize() in ['C', 'K']:
            self._atomCoordinateType = 'cartesian'
        else:
            self._atomCoordinateType = 'direct'

        # Ion positions
        self._atomCount = np.array(sum(self._atomCountByType))
        if self._atomCoordinateType == 'cartesian':
            self._atomPositions = np.array([list(map(float, line.strip().split()[:3])) for line in lines[7+offset:7+offset+self._atomCount]])
        else:
            self._atomPositions_fractional = np.array([list(map(float, line.strip().split()[:3])) for line in lines[7+offset:7+offset+self._atomCount]])

        self._atomicConstraints = np.array([list(map(str, line.strip().split()[3:])) for line in lines[7+offset:7+offset+self._atomCount]])
        # Check for lattice velocities
        # Check for ion velocities

    def readCIF(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self._file_location

        lines = [n for n in self.read_file() ]
        # Initialize variables
        self._latticeParameters = [0,0,0]
        self._latticeAngles = [0,0,0]
        self._atomPositions = []
        self._symmetryEquivPositions = []
        self._atomLabelsList = []

        # Flags to indicate the reading context
        reading_atoms = False
        reading_symmetry = False

        for line in lines:
            line = line.strip()

            # Lattice Parameters
            if line.startswith('_cell_length_a'):
                self._latticeParameters[0] = float(line.split()[1])
            elif line.startswith('_cell_length_b'):
                self._latticeParameters[1] = float(line.split()[1])
            elif line.startswith('_cell_length_c'):
                self._latticeParameters[2] = float(line.split()[1])

            # Lattice angles
            if line.startswith('_cell_angle_alpha'):
                self._latticeAngles[0] = np.radians(float(line.split()[1]))
            elif line.startswith('_cell_angle_beta'):
                self._latticeAngles[1] = np.radians(float(line.split()[1]))
            elif line.startswith('_cell_angle_gamma'):
                self._latticeAngles[2] = np.radians(float(line.split()[1]))


            # Symmetry Equiv Positions
            elif line.startswith('loop_'):
                reading_atoms = False  # Reset flags
                reading_symmetry = False  # Reset flags
            elif line.startswith('_symmetry_equiv_pos_as_xyz'):
                reading_symmetry = True
                continue  # Skip the line containing the column headers
            elif reading_symmetry:
                self._symmetryEquivPositions.append(line)

            # Atom positions
            elif line.startswith('_atom_site_label'):
                reading_atoms = True  # Set flag to start reading atoms
                continue  # Skip the line containing the column headers
            elif reading_atoms:
                tokens = line.split()
                if len(tokens) >= 4:  # Make sure it's a complete line
                    label, x, y, z = tokens[:4]
                    self._atomPositions.append([float(x), float(y), float(z)])
                    self._atomLabelsList.append(label)

        # Convert to numpy arrays
        self._atomPositions = np.array(self._atomPositions, dtype=np.float64)
        self._atomicConstraints = np.ones_like(self._atomPositions)
        self._atomCount = self._atomPositions.shape[0]
        self._atomCoordinateType = 'direct'
        self._selectiveDynamics = True
        self._scaleFactor = [1]

        return True

    def readSIFile(self, file_location:str=None):
        # read files commondly presente in the SI
        file_location = file_location if type(file_location) == str else self._file_location

        lines = [n for n in self.read_file() ]
                    
        # Flags to indicate which section of the file we are in
        reading_lattice_vectors = False
        reading_atomic_positions = False

        self._latticeVectors = []
        self._atomLabelsList = []
        self._atomPositions = []

        for line in lines:
            # Remove leading and trailing whitespaces
            line = line.strip()

            # Check for section headers
            if "Supercell lattice vectors" in line:
                reading_lattice_vectors = True
                reading_atomic_positions = False
                continue
            elif "Atomic positions" in line:
                reading_lattice_vectors = False
                reading_atomic_positions = True
                continue
            
            # Read data based on current section
            if reading_lattice_vectors:
                vector = [float(x) for x in line.split(",")]
                self._latticeVectors.append(vector)
            elif reading_atomic_positions:
                elements = line.split()
                self._atomLabelsList.append(elements[0])
                self._atomPositions.append([ float(n) for n in elements[1:] ])

        self._atomPositions = np.array(self._atomPositions)             
        self._atomLabelsList = np.array(self._atomLabelsList)             
        self._latticeVectors = np.array(self._latticeVectors)             
        self._atomCoordinateType = 'Cartesian'
        self._atomicConstraints = np.ones_like(self._atomPositions)
        self._atomCount = self._atomPositions.shape[0]
        self._selectiveDynamics = True
        self._scaleFactor = [1]

        return True

'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/dataset/CoFeNiOOH_jingzhu/bulk_CoFe'
ap = PeriodicSystem(file_location=path+'/CONTCAR')
ap.readPOSCAR()
print(ap.atomPositions)
ap.exportAsPDB(path+'/PDB.pdb')

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/*OOH surface for pure NiOOH'
ap = PeriodicSystem(file_location=path+'/SUPERCELL')
ap.readSIFile()
#ap.pack_to_unit_cell()
ap.exportAsPOSCAR(path+'/POSCAR')

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/*OH surface with Fe(HS)'
ap = PeriodicSystem(file_location=path+'/SUPERCELL')
ap.readSIFile()
ap.exportAsPOSCAR(path+'/POSCAR')


path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Eg'
ap = PeriodicSystem(file_location=path+'/POSCAR_tetragonal')
ap.readPOSCAR()
print(ap.atomPositions)
print( ap.latticeType )

print( ap.latticeVectors )
print( ap.minimum_image_distance( [0,0,0], [0,0,4.187]) )
fsad

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk FeOOH with β-NiOOH structure (Fe(LS))'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk FeOOH with β-NiOOH structure (Fe(HS))'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk β-NiOOH doped with 1 Fe(HS)'

ap = PeriodicSystem(file_location=path+'/SUPERCELL')
ap.readSIFile()
print( ap.latticeType )
ap.exportAsPOSCAR(path+'/POSCAR')
'''


'''
_uniqueAtomLabels
uniqueAtomLabels

#ap = PeriodicSystem(file_location='/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/Hydrotalcite/Hydrotalcite.cif')
#ap.readCIF()
#print(ap.latticeParameters, ap.latticeAngles)
#ap.exportAsPOSCAR()

ap = PeriodicSystem(file_location='/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/SAM/FeBzBzAu/FePC_5Bz_OH')
ap.readPOSCAR()


print(ap.atomicConstraints )

print( ap.atomPositions )
ap.cellDuplication( [2,2,1] )
print( ap.atomicConstraints.shape )
'''


