try:
    from ..IO.structure_handling_tools.AtomPosition import AtomPosition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class BandPathGenerator(AtomPosition):
    def __init__(self, file_location:str=None, name:str=None, Periodic_Object:object=None, **kwargs):
        if Periodic_Object is not None:
            self.__dict__.update(Periodic_Object.__dict__)
        else:
            super().__init__(name=name, file_location=file_location)
        self._high_symmetry_points = None 
        self._high_symmetry_points_path = None
        self._lattice_points = {
            'SIMPLECUBIC': {
                'path': ['Gamma', 'X', 'M', 'R', 'Gamma'],
                'Gamma': np.array([0, 0, 0, 'Gamma']),
                'X': np.array([0.5, 0, 0, 'X']),
                'M': np.array([0.5, 0.5, 0, 'M']),
                'R': np.array([0.5, 0.5, 0.5, 'R'])
            },
            'FCC': {
                'path': ['Gamma', 'X', 'W', 'K', 'L', 'U', 'Gamma'],
                'Gamma': np.array([0, 0, 0, 'Gamma']),
                'X': np.array([0.5, 0, 0, 'X']),
                'W': np.array([0.5, 0.25, 0, 'W']),
                'K': np.array([0.375, 0.375, 0.75, 'K']),
                'L': np.array([0.5, 0.5, 0.5, 'L']),
                'U': np.array([0.625, 0.25, 0, 'U'])
            },
            'BCC': {
                'path': ['Gamma', 'H', 'N', 'P', 'Gamma'],
                'Gamma': np.array([0, 0, 0, 'Gamma']),
                'H': np.array([0.5, -0.5, 0.5, 'H']),
                'N': np.array([0, 0, 0.5, 'N']),
                'P': np.array([0.25, 0.25, 0.25, 'P'])
            },
            'TETRAGONAL': {
                'path': ['Gamma', 'X', 'M', 'Z', 'R', 'A', 'Gamma'],
                'Gamma': np.array([0, 0, 0, 'Gamma']),
                'X': np.array([0.5, 0, 0, 'X']),
                'M': np.array([0.5, 0.5, 0, 'M']),
                'Z': np.array([0, 0, 0.5, 'Z']),
                'R': np.array([0.5, 0, 0.5, 'R']),
                'A': np.array([0.5, 0.5, 0.5, 'A'])
            },
            'ORTHORHOMBIC': {
                'path': ['Gamma', 'X', 'Y', 'Z', 'S', 'T', 'U', 'R', 'Gamma'],
                'Gamma': np.array([0, 0, 0, 'Gamma']),
                'X': np.array([0.5, 0, 0, 'X']),
                'Y': np.array([0, 0.5, 0, 'Y']),
                'Z': np.array([0, 0, 0.5, 'Z']),
                'S': np.array([0.5, 0.5, 0, 'S']),
                'T': np.array([0.5, 0, 0.5, 'T']),
                'U': np.array([0, 0.5, 0.5, 'U']),
                'R': np.array([0.5, 0.5, 0.5, 'R'])
            },
            'HEXAGONAL': {
                'path': ['Gamma', 'K', 'M', 'A', 'L', 'H', 'Gamma'],
                'Gamma': np.array([0, 0, 0, 'Gamma']),
                'K': np.array([1/3, 1/3, 0, 'K']),
                'M': np.array([0.5, 0, 0, 'M']),
                'A': np.array([0, 0, 0.5, 'A']),
                'L': np.array([1/3, 1/3, 0.5, 'L']),
                'H': np.array([0.5, 0, 0.5, 'H'])
            },
            'MONOCLINIC': {
                'path': ['Gamma', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'Gamma'],
                'Gamma': np.array([0, 0, 0, 'Gamma']),
                'A': np.array([0.5, 0, 0, 'A']),
                'B': np.array([0, 0.5, 0, 'B']),
                'C': np.array([0, 0, 0.5, 'C']),
                'D': np.array([0.5, 0.5, 0, 'D']),
                'E': np.array([0.5, 0, 0.5, 'E']),
                'F': np.array([0, 0.5, 0.5, 'F']),
                'G': np.array([0.5, 0.5, 0.5, 'G'])
            },
            'TRICLINIC': {
                'path': ['Gamma', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'Gamma'],
                'Gamma': np.array([0, 0, 0, 'Gamma']),
                'A': np.array([0.25, 0, 0, 'A']),
                'B': np.array([0, 0.25, 0, 'B']),
                'C': np.array([0, 0, 0.25, 'C']),
                'D': np.array([0.25, 0.25, 0, 'D']),
                'E': np.array([0.25, 0, 0.25, 'E']),
                'F': np.array([0, 0.25, 0.25, 'F']),
                'G': np.array([0.25, 0.25, 0.25, 'G']),
                'H': np.array([0.5, 0, 0, 'H']),
                'I': np.array([0, 0.5, 0, 'I']),
                'J': np.array([0, 0, 0.5, 'J'])
            }
        }

    @property
    def high_symmetry_points_path(self):
        if not self._high_symmetry_points_path is None:
            return self._high_symmetry_points_path
        elif self.high_symmetry_points is not None:
            self._high_symmetry_points_path = self.get_high_symmetry_points_path()
            return self._high_symmetry_points_path

    @property
    def high_symmetry_points(self):
        if not self._high_symmetry_points is None:
            return self._high_symmetry_points
        else:
            self._high_symmetry_points = self.get_high_symmetry_points()
            return self.high_symmetry_points

    def get_high_symmetry_points_path(self, high_symmetry_points:dict=None):
        high_symmetry_points = high_symmetry_points if type(high_symmetry_points) == str else self.high_symmetry_points
        high_symmetry_points_path = [ [high_symmetry_points[hsp_n], high_symmetry_points[hsp_n1]] for hsp_n, hsp_n1 in zip( high_symmetry_points['path'][:-1], high_symmetry_points['path'][1:] )]

        self._high_symmetry_points_path = high_symmetry_points_path
        return self._high_symmetry_points_path

    def get_high_symmetry_points(self, latticeType:str=None):
        """
        Function to get high-symmetry points for different lattice types.
        
        Parameters:
            latticeType : str
                The type of Bravais lattice ('SC', 'FCC', 'BCC', etc.)
            a1, a2, a3 : array-like
                The real-space lattice vectors.
                
        Returns:
            points : dict
                Dictionary containing the high-symmetry points.
            path : list
                List containing the path to traverse the high-symmetry points.
        """
        latticeType = latticeType if latticeType is not None else self.latticeType
        if latticeType.upper() in self.lattice_points:
            self._high_symmetry_points = self.lattice_points[latticeType.upper()]
            return self._high_symmetry_points
        else:
            raise ValueError("Lattice type not supported")

'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Eg'
ap = BandPathGenerator(file_location=path+'/POSCAR_cubic')
ap.readPOSCAR()
print(ap.latticeType )
print(ap.get_high_symmetry_points( ))# latticeType='SC' ))
print( ap.get_high_symmetry_points_path() )
print( ap.high_symmetry_points_path )

# Example usage
a1 = np.array([1, 0, 0])
a2 = np.array([0, 1, 0])
a3 = np.array([0, 0, 1])


asdf

for lattice in ['SC', 'FCC', 'BCC']:
    points, path = get_high_symmetry_points(lattice, a1, a2, a3)
    print(f"High-symmetry points for {lattice}: {points}")
    print(f"Path for {lattice}: {path}")
'''
