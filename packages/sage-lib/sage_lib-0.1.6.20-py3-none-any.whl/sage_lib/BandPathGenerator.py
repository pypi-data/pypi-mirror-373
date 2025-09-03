try:
    from sage_lib.PeriodicSystem import PeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PeriodicSystem: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class PathGenerator(PeriodicSystem):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._high_symmetry_points = None 
        self._high_symmetry_points_path = None
        self._lattice_points = {
            'SC': {
                'path': ['Gamma', 'X', 'M', 'R', 'Gamma'],
                'Gamma': np.array([0, 0, 0]),
                'X': np.array([0.5, 0, 0]),
                'M': np.array([0.5, 0.5, 0]),
                'R': np.array([0.5, 0.5, 0.5])
            },
            'FCC': {
                'path': ['Gamma', 'X', 'W', 'K', 'L', 'U', 'Gamma'],
                'Gamma': np.array([0, 0, 0]),
                'X': np.array([0.5, 0, 0]),
                'W': np.array([0.5, 0.25, 0]),
                'K': np.array([0.375, 0.375, 0.75]),
                'L': np.array([0.5, 0.5, 0.5]),
                'U': np.array([0.625, 0.25, 0])
            },
            'BCC': {
                'path': ['Gamma', 'H', 'N', 'P', 'Gamma'],
                'Gamma': np.array([0, 0, 0]),
                'H': np.array([0.5, -0.5, 0.5]),
                'N': np.array([0, 0, 0.5]),
                'P': np.array([0.25, 0.25, 0.25])
            },
            'TETRAGONAL': {
                'path': ['Gamma', 'X', 'M', 'Z', 'R', 'A', 'Gamma'],
                'Gamma': np.array([0, 0, 0]),
                'X': np.array([0.5, 0, 0]),
                'M': np.array([0.5, 0.5, 0]),
                'Z': np.array([0, 0, 0.5]),
                'R': np.array([0.5, 0, 0.5]),
                'A': np.array([0.5, 0.5, 0.5])
            },
            'ORTHORHOMBIC': {
                'path': ['Gamma', 'X', 'Y', 'Z', 'S', 'T', 'U', 'R', 'Gamma'],
                'Gamma': np.array([0, 0, 0]),
                'X': np.array([0.5, 0, 0]),
                'Y': np.array([0, 0.5, 0]),
                'Z': np.array([0, 0, 0.5]),
                'S': np.array([0.5, 0.5, 0]),
                'T': np.array([0.5, 0, 0.5]),
                'U': np.array([0, 0.5, 0.5]),
                'R': np.array([0.5, 0.5, 0.5])
            },
            'HEXAGONAL': {
                'path': ['Gamma', 'K', 'M', 'A', 'L', 'H', 'Gamma'],
                'Gamma': np.array([0, 0, 0]),
                'K': np.array([1/3, 1/3, 0]),
                'M': np.array([0.5, 0, 0]),
                'A': np.array([0, 0, 0.5]),
                'L': np.array([1/3, 1/3, 0.5]),
                'H': np.array([0.5, 0, 0.5])
            },
            'MONOCLINIC': {
                'path': ['Gamma', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'Gamma'],
                'Gamma': np.array([0, 0, 0]),
                'A': np.array([0.5, 0, 0]),
                'B': np.array([0, 0.5, 0]),
                'C': np.array([0, 0, 0.5]),
                'D': np.array([0.5, 0.5, 0]),
                'E': np.array([0.5, 0, 0.5]),
                'F': np.array([0, 0.5, 0.5]),
                'G': np.array([0.5, 0.5, 0.5])
            },
            'TRICLINIC': {
                'path': ['Gamma', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'Gamma'],
                'Gamma': np.array([0, 0, 0]),
                'A': np.array([0.25, 0, 0]),
                'B': np.array([0, 0.25, 0]),
                'C': np.array([0, 0, 0.25]),
                'D': np.array([0.25, 0.25, 0]),
                'E': np.array([0.25, 0, 0.25]),
                'F': np.array([0, 0.25, 0.25]),
                'G': np.array([0.25, 0.25, 0.25]),
                'H': np.array([0.5, 0, 0]),
                'I': np.array([0, 0.5, 0]),
                'J': np.array([0, 0, 0.5])
            }
        }
    def get_high_symmetry_points_path(self, high_symmetry_points:dict=None):
        high_symmetry_points = high_symmetry_points if type(high_symmetry_points) == str else self._high_symmetry_points
        high_symmetry_points_path = []

        high_symmetry_points_path = [ [high_symmetry_points[hsp_n], high_symmetry_points[hsp_n1]] for hsp_n, hsp_n1 in zip( high_symmetry_points['path'][:-1], high_symmetry_points['path'][1:] )]

        self._high_symmetry_points_path = high_symmetry_points_path
        return self._high_symmetry_points_path

    def get_high_symmetry_points(self, lattice_type:str=None):
        """
        Function to get high-symmetry points for different lattice types.
        
        Parameters:
            lattice_type : str
                The type of Bravais lattice ('SC', 'FCC', 'BCC', etc.)
            a1, a2, a3 : array-like
                The real-space lattice vectors.
                
        Returns:
            points : dict
                Dictionary containing the high-symmetry points.
            path : list
                List containing the path to traverse the high-symmetry points.
        """

        if lattice_type.upper() in self.lattice_points:
            self._high_symmetry_points = self._lattice_points[lattice_type]
            return self._high_symmetry_points
        else:
            raise ValueError("Lattice type not supported")


'''
# Example usage
a1 = np.array([1, 0, 0])
a2 = np.array([0, 1, 0])
a3 = np.array([0, 0, 1])

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Eg'
ap = PathGenerator(file_location=path+'/POSCAR_cubic')
ap.readPOSCAR()
print( ap.latticeType )
ap.get_high_symmetry_points( lattice_type='SC' )
ap.get_high_symmetry_points_path(  )
print( ap.high_symmetry_points_path )

asdf

for lattice in ['SC', 'FCC', 'BCC']:
    points, path = get_high_symmetry_points(lattice, a1, a2, a3)
    print(f"High-symmetry points for {lattice}: {points}")
    print(f"Path for {lattice}: {path}")
'''
