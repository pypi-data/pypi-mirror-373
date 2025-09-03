import numpy as np

# The following is a list of the critical points in the 1st Brillouin zone
# for some typical crystal structures following the conventions of Setyawan
# and Curtarolo [https://doi.org/10.1016/j.commatsci.2010.05.010].
#
# In units of the reciprocal basis vectors.
#
# See http://en.wikipedia.org/wiki/Brillouin_zone

sc_special_points = {
    'cubic': {'G': [0, 0, 0],
              'M': [1 / 2, 1 / 2, 0],
              'R': [1 / 2, 1 / 2, 1 / 2],
              'X': [0, 1 / 2, 0]},
    'fcc': {'G': [0, 0, 0],
            'K': [3 / 8, 3 / 8, 3 / 4],
            'L': [1 / 2, 1 / 2, 1 / 2],
            'U': [5 / 8, 1 / 4, 5 / 8],
            'W': [1 / 2, 1 / 4, 3 / 4],
            'X': [1 / 2, 0, 1 / 2]},
    'bcc': {'G': [0, 0, 0],
            'H': [1 / 2, -1 / 2, 1 / 2],
            'P': [1 / 4, 1 / 4, 1 / 4],
            'N': [0, 0, 1 / 2]},
    'tetragonal': {'G': [0, 0, 0],
                   'A': [1 / 2, 1 / 2, 1 / 2],
                   'M': [1 / 2, 1 / 2, 0],
                   'R': [0, 1 / 2, 1 / 2],
                   'X': [0, 1 / 2, 0],
                   'Z': [0, 0, 1 / 2]},
    'bct': {'G': [0, 0, 0],
            'X': [0, 0, 1 / 2],
            'M': [-1 / 2, 1 / 2, 1 / 2],
            'Z': [1 / 4, 1 / 4, 1 / 4],
            'P': [1 / 2, 0, 1 / 2]},
    'orthorhombic': {'G': [0, 0, 0],
                     'R': [1 / 2, 1 / 2, 1 / 2],
                     'S': [1 / 2, 1 / 2, 0],
                     'T': [0, 1 / 2, 1 / 2],
                     'U': [1 / 2, 0, 1 / 2],
                     'X': [1 / 2, 0, 0],
                     'Y': [0, 1 / 2, 0],
                     'Z': [0, 0, 1 / 2]},
    'hexagonal': {'G': [0, 0, 0],
                  'A': [0, 0, 1 / 2],
                  'H': [1 / 3, 1 / 3, 1 / 2],
                  'K': [1 / 3, 1 / 3, 0],
                  'L': [1 / 2, 0, 1 / 2],
                  'M': [1 / 2, 0, 0]},
    'rhombohedral': {'G': [0, 0, 0],
                     'L': [1 / 2, 0, 0],
                     'F': [1 / 2, 1 / 2, 0],
                     'P': [1 / 4, 1 / 4, 1 / 4],
                     'Q': [1 / 3, 1 / 3, 1 / 3]},
    'monoclinic': {'G': [0, 0, 0],
                   'A': [1 / 2, 1 / 2, 0],
                   'Y': [0, 1 / 2, 0],
                   'Z': [0, 0, 1 / 2],
                   'M': [1 / 2, 0, 1 / 2]},
    'triclinic': {'G': [0, 0, 0],
                  'X': [1 / 2, 0, 0],
                  'Y': [0, 1 / 2, 0],
                  'Z': [0, 0, 1 / 2],
                  'R': [1 / 2, 1 / 2, 1 / 2]}
}

ibz_points = {
    'cubic': {'Gamma': [0, 0, 0],
              'X': [0, 1 / 2, 0],
              'R': [1 / 2, 1 / 2, 1 / 2],
              'M': [1 / 2, 1 / 2, 0]},
    'fcc': {'Gamma': [0, 0, 0],
            'X': [1 / 2, 0, 1 / 2],
            'W': [1 / 2, 1 / 4, 3 / 4],
            'K': [3 / 8, 3 / 8, 3 / 4],
            'U': [5 / 8, 1 / 4, 5 / 8],
            'L': [1 / 2, 1 / 2, 1 / 2]},
    'bcc': {'Gamma': [0, 0, 0],
            'H': [1 / 2, -1 / 2, 1 / 2],
            'N': [0, 0, 1 / 2],
            'P': [1 / 4, 1 / 4, 1 / 4]},
    'hexagonal': {'Gamma': [0, 0, 0],
                  'M': [0, 1 / 2, 0],
                  'K': [-1 / 3, 1 / 3, 0],
                  'A': [0, 0, 1 / 2],
                  'L': [0, 1 / 2, 1 / 2],
                  'H': [-1 / 3, 1 / 3, 1 / 2]},
    'tetragonal': {'Gamma': [0, 0, 0],
                   'X': [1 / 2, 0, 0],
                   'M': [1 / 2, 1 / 2, 0],
                   'Z': [0, 0, 1 / 2],
                   'R': [1 / 2, 0, 1 / 2],
                   'A': [1 / 2, 1 / 2, 1 / 2]},
    'orthorhombic': {'Gamma': [0, 0, 0],
                     'R': [1 / 2, 1 / 2, 1 / 2],
                     'S': [1 / 2, 1 / 2, 0],
                     'T': [0, 1 / 2, 1 / 2],
                     'U': [1 / 2, 0, 1 / 2],
                     'X': [1 / 2, 0, 0],
                     'Y': [0, 1 / 2, 0],
                     'Z': [0, 0, 1 / 2]},
    'rhombohedral': {'Gamma': [0, 0, 0],
                     'L': [1 / 2, 0, 0],
                     'F': [1 / 2, 1 / 2, 0],
                     'P': [1 / 4, 1 / 4, 1 / 4],
                     'Q': [1 / 3, 1 / 3, 1 / 3]},
    'monoclinic': {'Gamma': [0, 0, 0],
                   'A': [1 / 2, 1 / 2, 0],
                   'Y': [0, 1 / 2, 0],
                   'Z': [0, 0, 1 / 2],
                   'M': [1 / 2, 0, 1 / 2]},
    'triclinic': {'Gamma': [0, 0, 0],
                  'X': [1 / 2, 0, 0],
                  'Y': [0, 1 / 2, 0],
                  'Z': [0, 0, 1 / 2],
                  'R': [1 / 2, 1 / 2, 1 / 2]}
}

special_segments = {
    'cubic': [
        ('G', 'X'), ('X', 'M'), ('M', 'G'), ('G', 'R'), ('R', 'X'),
        ('M', 'R')
    ],
    'fcc': [
        ('G', 'X'), ('X', 'W'), ('W', 'K'), ('K', 'G'), ('G', 'L'),
        ('L', 'U'), ('U', 'W'), ('W', 'L'), ('L', 'K'),
        ('U', 'X')
    ],
    'bcc': [
        ('G', 'H'), ('H', 'N'), ('N', 'G'), ('G', 'P'),
        ('P', 'H'), ('P', 'N')
    ],
    'tetragonal': [
        ('G', 'X'), ('X', 'M'), ('M', 'G'), ('G', 'Z'), ('Z', 'R'),
        ('R', 'A'), ('A', 'Z'), ('Z', 'X'), ('X', 'R'),
        ('M', 'A')
    ],
    'orthorhombic': [
        ('G', 'X'), ('X', 'S'), ('S', 'Y'), ('Y', 'G'), ('G', 'Z'),
        ('Z', 'U'), ('U', 'R'), ('R', 'T'), ('T', 'Z'),
        ('Y', 'T'), ('U', 'X'), ('S', 'R')
    ],
    'hexagonal': [
        ('G', 'M'), ('M', 'K'), ('K', 'G'), ('G', 'A'), ('A', 'L'),
        ('L', 'H'), ('H', 'A'), ('L', 'M'), ('K', 'H')
    ],
    'monoclinic': [
        ('G', 'Y'), ('Y', 'H'), ('H', 'C'), ('C', 'E'), ('E', 'M1'),
        ('M1', 'A'), ('A', 'X'), ('X', 'H1'), ('M', 'D'), ('D', 'Z'), 
        ('Y', 'D')
    ],
    'rhombohedral': [
        ('G', 'L'), ('L', 'B1'), ('B1', 'B'), ('B', 'Z'), ('Z', 'G'),
        ('G', 'X'), ('X', 'Q'), ('Q', 'F'), ('F', 'P1'),
        ('P1', 'Z'), ('L', 'P')
    ],
    'rhombohedral type 1': [
        ('G', 'L'), ('L', 'B1'), ('B1', 'B'), ('B', 'Z'), ('Z', 'G'),
        ('G', 'X'), ('X', 'Q'), ('Q', 'F'), ('F', 'P1'),
        ('P1', 'Z'), ('L', 'P')
    ],
    'rhombohedral type 2': [
        ('G', 'P'), ('P', 'Z'), ('Z', 'Q'), ('Q', 'G'), ('G', 'F'),
        ('F', 'P1'), ('P1', 'Q1'), ('Q1', 'L'), ('L', 'Z')
    ], # !!
    'triclinic': [
        ('X', 'G'), ('G', 'Y'), ('L', 'G'), ('G', 'Z'),
        ('N', 'G'), ('G', 'M'), ('R', 'G')
    ],
    'BCT1': [ # body-centered tetragonal
        ('G', 'X'), ('X', 'M'), ('M', 'G'), ('G', 'Z'), ('Z', 'P'),
        ('P', 'N'), ('N', 'Z1'), ('Z1', 'M'), ('X', 'P')
    ],
    'BCT2': [ # body-centered tetragonal
        ('G', 'X'), ('X', 'Y'), ('Y', 'R'), ('R', 'G'), ('G', 'Z'),
        ('Z', 'R1'), ('R1', 'N'), ('N', 'P'), ('P', 'Y1'),
        ('Y1', 'Z'), ('X', 'P')
    ],
    'ORCF': [ # face-centered orthorhombic
        ('G', 'Y'), ('Y', 'T'), ('T', 'Z'), ('Z', 'G'), ('G', 'X'),
        ('X', 'A1'), ('A1', 'Y'), ('T', 'X1'), ('X', 'A'),
        ('A', 'Z'), ('L', 'G')
    ],
    'MCLC1': [ # c-centered monoclinic 
        ('G', 'Y'), ('Y', 'F'), ('F', 'L'), ('L', 'I'), ('I', 'I1'),
        ('I1', 'Z'), ('Z', 'F1'), ('F1', 'Y'), ('Y', 'X1'),
        ('X1', 'X'), ('X', 'G'), ('G', 'N'), ('N', 'M'),
        ('M', 'G')
    ],
    'MCLC2': [ # c-centered monoclinic 
        ('G', 'Y'), ('Y', 'F'), ('F', 'L'), ('L', 'I'), ('I', 'I1'),
        ('I1', 'Z'), ('Z', 'F1'), ('F1', 'N'), ('N', 'G'),
        ('G', 'M')
    ]
}

class Cubic:
    """Abstract class for cubic lattices."""
    conventional_cls = 'CUB'

    def __init__(self, a):
        """Initialize cubic lattice with lattice parameter 'a'."""
        pass

# Identity matrix for convenience
_identity = np.identity(3, int)

# Class definitions for lattice types
class CUB:
    """Cubic lattice class."""
    name = "cubic"

    def __init__(self, a):
        self.a = a

    def get_cell(self):
        """Returns the cubic lattice as a 3x3 matrix."""
        return self.a * np.eye(3)

class FCC:
    """Face-Centered Cubic (FCC) lattice class."""
    name = "fcc"

    def __init__(self, a):
        self.a = a

    def get_cell(self):
        """Returns the FCC lattice as a 3x3 matrix."""
        return 0.5 * np.array([[0., self.a, self.a],
                               [self.a, 0., self.a],
                               [self.a, self.a, 0.]])

class BCC:
    """Body-Centered Cubic (BCC) lattice class."""
    name = "bcc"

    def __init__(self, a):
        self.a = a

    def get_cell(self):
        """Returns the BCC lattice as a 3x3 matrix."""
        return 0.5 * np.array([[-self.a, self.a, self.a],
                               [self.a, -self.a, self.a],
                               [self.a, self.a, -self.a]])

class TET:
    """Tetragonal lattice class."""
    name = "tetragonal"

    def __init__(self, a, c):
        self.a = a
        self.c = c

    def get_cell(self):
        """Returns the Tetragonal lattice as a 3x3 matrix."""
        return np.diag([self.a, self.a, self.c])

class HEX:
    """Hexagonal lattice class."""
    name = "hexagonal"

    def __init__(self, a, c):
        self.a = a
        self.c = c

    def get_cell(self):
        """Returns the Hexagonal lattice as a 3x3 matrix."""
        x = 0.5 * np.sqrt(3)
        return np.array([[0.5 * self.a, -x * self.a, 0.],
                         [0.5 * self.a,  x * self.a, 0.],
                         [0., 0., self.c]])

class ORC:
    """Orthorhombic lattice class."""
    name = "orthorhombic"

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def get_cell(self):
        """Returns the Orthorhombic lattice as a 3x3 matrix."""
        return np.diag([self.a, self.b, self.c])

class MCL:
    """Monoclinic lattice class."""
    name = "monoclinic"

    def __init__(self, a, b, c, alpha):
        self.a = a
        self.b = b
        self.c = c
        self.alpha = np.radians(alpha)  # Convert angle to radians

    def get_cell(self):
        """Returns the Monoclinic lattice as a 3x3 matrix."""
        return np.array([[self.a, 0, 0],
                         [0, self.b, 0],
                         [self.c * np.cos(self.alpha), 0, self.c * np.sin(self.alpha)]])

class TRI:
    """Triclinic lattice class."""
    name = "triclinic"

    def __init__(self, a, b, c, alpha, beta, gamma):
        self.a = a
        self.b = b
        self.c = c
        self.alpha = np.radians(alpha)
        self.beta = np.radians(beta)
        self.gamma = np.radians(gamma)

    def get_cell(self):
        """Returns the Triclinic lattice as a 3x3 matrix."""
        cos_alpha = np.cos(self.alpha)
        cos_beta = np.cos(self.beta)
        cos_gamma = np.cos(self.gamma)
        sin_gamma = np.sin(self.gamma)

        # Compute third vector components
        v3x = self.c * cos_beta
        v3y = self.c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma
        v3z = self.c * np.sqrt(1 - cos_beta**2 - (cos_alpha - cos_beta * cos_gamma)**2 / sin_gamma**2)

        return np.array([[self.a, 0, 0],
                         [self.b * cos_gamma, self.b * sin_gamma, 0],
                         [v3x, v3y, v3z]])

class BCT:
    """Body-Centered Tetragonal (BCT) lattice class."""
    name = "Body-Centered Tetragonal (BCT)"

    def __init__(self, a, c):
        self.a = a
        self.c = c

    def get_cell(self):
        """Returns the BCT lattice as a 3x3 matrix."""
        return 0.5 * np.array([[-self.a, self.a, self.c],
                               [self.a, -self.a, self.c],
                               [self.a, self.a, -self.c]])

class BravaisLattice:
    name = ""
    sc_special_points = sc_special_points
    ibz_points = ibz_points
    special_segments = special_segments
    
    def get_cell(self):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def get_special_points(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

# Cubic lattice class
class CUB(BravaisLattice):
    """Cubic lattice class."""
    name = "cubic"

    def __init__(self, a):
        self.a = a

    def get_cell(self):
        """Returns the cubic lattice as a 3x3 matrix."""
        return self.a * np.eye(3)

    def get_special_points(self):
        """Returns the special k-points for the cubic lattice."""
        points = {
            'G': [0, 0, 0],
            'X': [0, 1 / 2, 0],
            'M': [1 / 2, 1 / 2, 0],
            'R': [1 / 2, 1 / 2, 1 / 2]
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points
        special_segments[self.name] = [
            ('G', 'X'), ('X', 'M'), ('M', 'G'), ('G', 'R'), ('R', 'X'), ('M', 'R')
        ]

# Face-Centered Cubic (FCC) lattice class
class FCC(BravaisLattice):
    """Face-Centered Cubic (FCC) lattice class."""
    name = "fcc"

    def __init__(self, a):
        self.a = a

    def get_cell(self):
        """Returns the FCC lattice as a 3x3 matrix."""
        return 0.5 * np.array([[0, self.a, self.a],
                               [self.a, 0, self.a],
                               [self.a, self.a, 0]])

    def get_special_points(self):
        """Returns the special k-points for the FCC lattice."""
        points = {
            'G': [0, 0, 0],
            'X': [1 / 2, 0, 1 / 2],
            'W': [1 / 2, 1 / 4, 3 / 4],
            'K': [3 / 8, 3 / 8, 3 / 4],
            'U': [5 / 8, 1 / 4, 5 / 8],
            'L': [1 / 2, 1 / 2, 1 / 2]
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points
        special_segments[self.name] = [
            ('G', 'X'), ('X', 'W'), ('W', 'K'), ('K', 'G'),
            ('G', 'L'), ('L', 'U'), ('U', 'W'), ('W', 'L'),
            ('L', 'K'), ('U', 'X')
        ]

# Body-Centered Cubic (BCC) lattice class
class BCC(BravaisLattice):
    """Body-Centered Cubic (BCC) lattice class."""
    name = "bcc"

    def __init__(self, a):
        self.a = a

    def get_cell(self):
        """Returns the BCC lattice as a 3x3 matrix."""
        return 0.5 * np.array([[-self.a, self.a, self.a],
                               [self.a, -self.a, self.a],
                               [self.a, self.a, -self.a]])

    def get_special_points(self):
        """Returns the special k-points for the BCC lattice."""
        points = {
            'G': [0, 0, 0],
            'H': [1 / 2, -1 / 2, 1 / 2],
            'N': [0, 0, 1 / 2],
            'P': [1 / 4, 1 / 4, 1 / 4]
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points
        special_segments[self.name] = [
            ('G', 'H'), ('H', 'N'), ('N', 'G'), ('G', 'P'),
            ('P', 'H'), ('P', 'N')
        ]

# Tetragonal lattice class
class TET(BravaisLattice):
    """Tetragonal lattice class."""
    name = "tetragonal"

    def __init__(self, a, c):
        self.a = a
        self.c = c

    def get_cell(self):
        """Returns the Tetragonal lattice as a 3x3 matrix."""
        return np.diag([self.a, self.a, self.c])

    def get_special_points(self):
        """Returns the special k-points for the tetragonal lattice."""
        points = {
            'G': [0, 0, 0],
            'X': [1 / 2, 0, 0],
            'M': [1 / 2, 1 / 2, 0],
            'Z': [0, 0, 1 / 2],
            'R': [0, 1 / 2, 1 / 2],
            'A': [1 / 2, 1 / 2, 1 / 2]
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points
        special_segments[self.name] = [
            ('G', 'X'), ('X', 'M'), ('M', 'G'), ('G', 'Z'),
            ('Z', 'R'), ('R', 'A'), ('A', 'Z'), ('Z', 'X'),
            ('X', 'R'), ('M', 'A')
        ]

# Hexagonal lattice class
class HEX(BravaisLattice):
    """Hexagonal lattice class."""
    name = "hexagonal"

    def __init__(self, a, c):
        self.a = a
        self.c = c

    def get_cell(self):
        """Returns the Hexagonal lattice as a 3x3 matrix."""
        x = 0.5 * np.sqrt(3)
        return np.array([[0.5 * self.a, -x * self.a, 0.],
                         [0.5 * self.a,  x * self.a, 0.],
                         [0., 0., self.c]])

    def get_special_points(self):
        """Returns the special k-points for the hexagonal lattice."""
        points = {
            'G': [0, 0, 0],
            'M': [1 / 2, 0, 0],
            'K': [1 / 3, 1 / 3, 0],
            'A': [0, 0, 1 / 2],
            'L': [1 / 2, 0, 1 / 2],
            'H': [1 / 3, 1 / 3, 1 / 2]
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points
        special_segments[self.name] = [
            ('G', 'M'), ('M', 'K'), ('K', 'G'), ('G', 'A'),
            ('A', 'L'), ('L', 'H'), ('H', 'A'), ('L', 'M'),
            ('K', 'H')
        ]
        return sc_special_points[self.name], ibz_points[self.name], special_segments[self.name]

# Orthorhombic lattice class
class ORC(BravaisLattice):
    """Orthorhombic lattice class."""
    name = "orthorhombic"

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def get_cell(self):
        """Returns the Orthorhombic lattice as a 3x3 matrix."""
        return np.diag([self.a, self.b, self.c])

    def get_special_points(self):
        """Returns the special k-points for the orthorhombic lattice."""
        points = {
            'G': [0, 0, 0],
            'X': [1 / 2, 0, 0],
            'Y': [0, 1 / 2, 0],
            'Z': [0, 0, 1 / 2],
            'T': [0, 1 / 2, 1 / 2],
            'U': [1 / 2, 0, 1 / 2],
            'S': [1 / 2, 1 / 2, 0],
            'R': [1 / 2, 1 / 2, 1 / 2]
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points
        special_segments[self.name] = [
            ('G', 'X'), ('X', 'S'), ('S', 'Y'), ('Y', 'G'),
            ('G', 'Z'), ('Z', 'U'), ('U', 'R'), ('R', 'T'),
            ('T', 'Z'), ('Y', 'T'), ('U', 'X'), ('S', 'R')
        ]

# Monoclinic lattice class
class MCL(BravaisLattice):
    """Monoclinic lattice class."""
    name = "monoclinic"

    def __init__(self, a, b, c, alpha):
        self.a = a
        self.b = b
        self.c = c
        self.alpha = np.radians(alpha)  # Convert angle to radians

    def get_cell(self):
        """Returns the Monoclinic lattice as a 3x3 matrix."""
        return np.array([[self.a, 0, 0],
                         [0, self.b, 0],
                         [self.c * np.cos(self.alpha), 0, self.c * np.sin(self.alpha)]])

    def get_special_points(self):
        """Returns the special k-points for the monoclinic lattice."""
        # Calculate parameters g and m based on lattice parameters
        cos_alpha = np.cos(self.alpha)
        sin_alpha = np.sin(self.alpha)
        g = (1 - self.b * cos_alpha / self.c) / (2 * sin_alpha ** 2)
        m = 1 / 2 - g * self.c * cos_alpha / self.b

        points = {
            'G': [0, 0, 0],
            'A': [1 / 2, 1 / 2, 0],
            'Y': [0, 1 / 2, 0],
            'M': [1 / 2, 0, 1 / 2],
            'M1': [1 / 2, 1 / 2, 1 / 2],
            'D': [1 / 2, 0, 1 / 2],
            'D1': [1 / 2, 0, -1 / 2],
            'E': [1 / 2, 1 / 2, 1 / 2],
            'H': [0, g, 1 - m],
            'H1': [0, 1 - g, m],
            'H2': [0, g, -m],
            'X': [0, 1 / 2, 0],
            'Y1': [0, 0, 1 / 2],
            'Z': [1 / 2, 0, 0],
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points

        special_segments[self.name] = [
            ('G', 'Y'), ('Y', 'H'), ('H', 'G'), ('G', 'E'),
            ('E', 'M1'), ('M1', 'A'), ('A', 'X'), ('X', 'H1'),
            ('M', 'D'), ('D', 'Z'), ('Y', 'D')
        ]

# Triclinic lattice class
class TRI(BravaisLattice):
    """Triclinic lattice class with variants TRI1a, TRI1b, TRI2a, and TRI2b."""
    name = "triclinic"

    def __init__(self, a, b, c, alpha, beta, gamma):
        if not (0 < alpha < 180 and 0 < beta < 180 and 0 < gamma < 180):
            raise ValueError(f"Invalid angles: alpha={alpha}, beta={beta}, gamma={gamma}")
        
        self.a = a
        self.b = b
        self.c = c
        self.alpha = np.radians(alpha)
        self.beta = np.radians(beta)
        self.gamma = np.radians(gamma)
        self.variant = self._determine_variant(alpha, beta, gamma)

    def _determine_variant(self, alpha, beta, gamma):
        """Determines the triclinic lattice variant."""
        if abs(gamma - 90) < 1e-6:
            return 'TRI2a' if alpha > 90 and beta > 90 else 'TRI2b'
        elif gamma < 90:
            return 'TRI1b' if alpha < 90 and beta < 90 else 'TRI1a'
        elif gamma > 90:
            return 'TRI1a' if alpha > 90 and beta > 90 else 'TRI1b'
        else:
            raise ValueError(f"Unknown variant for Triclinic lattice: alpha={alpha}, beta={beta}, gamma={gamma}")

    def get_cell(self):
        """Returns the Triclinic lattice as a 3x3 matrix."""
        cos_alpha = np.cos(self.alpha)
        cos_beta = np.cos(self.beta)
        cos_gamma = np.cos(self.gamma)
        sin_gamma = np.sin(self.gamma)

        # Compute third vector components
        v3x = self.c * cos_beta
        v3y = self.c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma
        v3z = self.c * np.sqrt(1 - cos_beta**2 - ((cos_alpha - cos_beta * cos_gamma) / sin_gamma)**2)

        return np.array([
            [self.a, 0, 0],
            [self.b * cos_gamma, self.b * sin_gamma, 0],
            [v3x, v3y, v3z]
        ])

    def get_special_points(self):
        """Returns the special k-points for the Triclinic lattice."""
        # Define symmetry points for each variant based on the image
        points_variants = {
            'TRI1a': {
                'G': [0, 0, 0],
                'R': [1 / 2, 1 / 2, 1 / 2],
                'L': [1 / 2, 1 / 2, 0],
                'X': [1 / 2, 0, 0],
                'M': [0, 1 / 2, 1 / 2],
                'Y': [0, 1 / 2, 0],
                'N': [1 / 2, 0, 1 / 2],
                'Z': [0, 0, 1 / 2]
            },
            'TRI2a': {  # Same points as TRI1a
                'G': [0, 0, 0],
                'R': [1 / 2, 1 / 2, 1 / 2],
                'L': [1 / 2, 1 / 2, 0],
                'X': [1 / 2, 0, 0],
                'M': [0, 1 / 2, 1 / 2],
                'Y': [0, 1 / 2, 0],
                'N': [1 / 2, 0, 1 / 2],
                'Z': [0, 0, 1 / 2]
            },
            'TRI1b': {
                'G': [0, 0, 0],
                'R': [-1 / 2, 1 / 2, 1 / 2],
                'L': [0, -1 / 2, 0],
                'X': [-1 / 2, -1 / 2, 0],
                'M': [0, 1 / 2, 1 / 2],
                'Y': [1 / 2, 0, 0],
                'N': [-1 / 2, -1 / 2, 1 / 2],
                'Z': [-1 / 2, 0, 1 / 2]
            },
            'TRI2b': {  # Same points as TRI1b
                'G': [0, 0, 0],
                'R': [-1 / 2, 1 / 2, 1 / 2],
                'L': [0, -1 / 2, 0],
                'X': [-1 / 2, -1 / 2, 0],
                'M': [0, 1 / 2, 1 / 2],
                'Y': [1 / 2, 0, 0],
                'N': [-1 / 2, -1 / 2, 1 / 2],
                'Z': [-1 / 2, 0, 1 / 2]
            }
        }

        # Assign special points and segments based on variant
        if self.variant in points_variants:
            points = points_variants[self.variant]
            sc_special_points[self.name] = points
            ibz_points[self.name] = points

            # Define the Brillouin zone path for all variants
            special_segments[self.name] = [
                ('X', 'G'), ('G', 'Y'), ('Y', 'L'), ('L', 'G'),
                ('G', 'Z'), ('Z', 'N'), ('N', 'G'),
                ('G', 'M'), ('M', 'R'), ('R', 'G')
            ]
        else:
            raise ValueError(f"Unknown variant for Triclinic lattice: {self.variant}")

        return sc_special_points[self.name], ibz_points[self.name], special_segments[self.name]


# Rhombohedral lattice class
class RHL(BravaisLattice):
    """Rhombohedral (RHL) lattice class."""
    name = "rhombohedral"

    def __init__(self, a, alpha):
        if alpha >= 120 or alpha <= 0:
            raise UnconventionalLattice('Need alpha < 120 degrees, got {}'
                                        .format(alpha))

        self.a = a
        self.alpha = np.radians(alpha)  # Convert alpha to radians

    def get_cell(self):
        """Returns the Rhombohedral lattice as a 3x3 matrix."""
        cos_alpha = np.cos(self.alpha)
        cos_half_alpha = np.cos(self.alpha / 2)
        sin_half_alpha = np.sin(self.alpha / 2)

        a1 = [self.a * cos_half_alpha, self.a * sin_half_alpha, 0]
        a2 = [self.a * cos_half_alpha, -self.a * sin_half_alpha, 0]
        a3_x = self.a * cos_alpha / cos_half_alpha
        a3_z = self.a * np.sqrt(1 - (cos_alpha ** 2) / (cos_half_alpha ** 2))
        a3 = [a3_x, 0, a3_z]

        return np.array([a1, a2, a3])

    def get_special_points(self):
        """Returns the special k-points for the rhombohedral lattice."""
        cos_alpha = np.cos(self.alpha)
        eta = (1 + 4 * cos_alpha) / (2 + 4 * cos_alpha)
        mu = 0.75 - eta / 2

        points = {
            'G': [0, 0, 0],
            'L': [1 / 2, 0, 0],
            'F': [1 / 2, 1 / 2, 0],
            'P': [eta, eta, eta],
            'Q': [mu, mu, mu],
            'Z': [1 / 2, 1 / 2, 1 / 2],
            'X': [mu, 0, -mu],
            'B': [mu, 1 - mu, -mu],
            'B1': [1 - mu, mu - 1, mu]
        }
        self.sc_special_points[self.name] = points
        self.ibz_points[self.name] = points

        self.special_segments[self.name] = [
            ('G', 'L'), ('L', 'B1'), ('B1', 'B'), ('B', 'Z'), ('Z', 'G'),
            ('G', 'X'), ('X', 'Q'), ('Q', 'F'), ('F', 'P'), ('P', 'Z'),
            ('L', 'P')
        ]

class ORCF(BravaisLattice):
    """Face-Centered Orthorhombic (ORCF) lattice class."""
    name = "orthorhombic_face_centered"

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def get_cell(self):
        """Returns the ORCF lattice as a 3x3 matrix."""
        return 0.5 * np.array([[0, self.b, self.c],
                               [self.a, 0, self.c],
                               [self.a, self.b, 0]])

    def get_special_points(self):
        """Returns the special k-points for the ORCF lattice."""
        points = {
            'G': [0, 0, 0],
            'L': [1 / 2, 0, 0],
            'F': [1 / 2, 1 / 2, 0],
            'P': [1 / 4, 1 / 4, 1 / 4],
            'Q': [3 / 4, 3 / 4, 3 / 4],
            'Z': [1 / 2, 1 / 2, 1 / 2],
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points
        special_segments[self.name] = [
            ('G', 'L'), ('L', 'F'), ('F', 'P'), ('P', 'G'),
            ('G', 'Z'), ('Z', 'Q'), ('Q', 'L'), ('F', 'Z')
        ]

class ORCI(BravaisLattice):
    """Body-Centered Orthorhombic (ORCI) lattice class."""
    name = "orthorhombic_body_centered"

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def get_cell(self):
        """Returns the ORCI lattice as a 3x3 matrix."""
        return 0.5 * np.array([[-self.a, self.b, self.c],
                               [self.a, -self.b, self.c],
                               [self.a, self.b, -self.c]])

    def get_special_points(self):
        """Returns the special k-points for the ORCI lattice."""
        points = {
            'G': [0, 0, 0],
            'T': [1 / 2, 1 / 2, 0],
            'U': [1 / 2, 0, 1 / 2],
            'R': [1 / 2, 1 / 2, 1 / 2],
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points
        special_segments[self.name] = [
            ('G', 'T'), ('T', 'U'), ('U', 'R'), ('R', 'G')
        ]

class ORCC(BravaisLattice):
    """Base-Centered Orthorhombic (ORCC) lattice class."""
    name = "orthorhombic_base_centered"

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
        # Calculamos f para los puntos de simetría
        self.f = (1 + (a**2 / b**2)) / 4

    def get_cell(self):
        """Returns the ORCC lattice as a 3x3 matrix."""
        # Vector convencional de la celda base centrada
        return np.array([[self.a, 0, 0],
                         [0.5 * self.a, self.b, 0],
                         [0, 0, self.c]])

    def get_special_points(self):
        """Returns the special k-points for the ORCC lattice."""
        # Definimos los puntos de simetría usando 'f' como se especifica
        points = {
            'G': [0, 0, 0],
            'X': [self.f, self.f, 0],
            'S': [0, 1 / 2, 0],
            'R': [0, 1 / 2, 1 / 2],
            'A': [self.f, self.f, 1 / 2],
            'Z': [0, 0, 1 / 2],
            'Y': [1 / 2, 1 / 2, 0],
            'X1': [1 - self.f, 1 - self.f, 0],
            'A1': [1 - self.f, 1 - self.f, 1 / 2],
            'T': [1 / 2, 1 / 2, 1 / 2],
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points

        # Camino en la zona de Brillouin según la especificación
        special_segments[self.name] = [
            ('G', 'X'), ('X', 'S'), ('S', 'R'), ('R', 'A'),
            ('A', 'Z'), ('Z', 'G'), ('G', 'Y'), ('Y', 'X1'),
            ('X1', 'A1'), ('A1', 'T'), ('T', 'Y'), ('Z', 'T')
        ]

    #C–X–S–R–A–Z–C–Y–X1–A1–T–YjZ–T.

class MCLC(BravaisLattice):
    """Monoclinic Centered Lattice Class (MCLC)."""
    name = "monoclinic_centered"

    def __init__(self, a, b, c, alpha):
        self.a = a
        self.b = b
        self.c = c
        self.alpha = np.radians(alpha)  # Convertimos el ángulo a radianes
        # Calculamos los parámetros g y m según las especificaciones
        self.g = (1 - (self.b * np.cos(self.alpha) / self.c)) / (2 * np.sin(self.alpha)**2)
        self.m = 0.5 - (self.g * self.c * np.cos(self.alpha) / self.b)

    def get_cell(self):
        """Returns the MCLC lattice as a 3x3 matrix."""
        return np.array([[0.5 * self.a, -0.5 * self.b, 0],
                         [0.5 * self.a, 0.5 * self.b, 0],
                         [self.c * np.cos(self.alpha), 0, self.c * np.sin(self.alpha)]])

    def get_special_points(self):
        """Returns the special k-points for the MCLC lattice."""
        points = {
            'G': [0, 0, 0],
            'C': [0, self.g, self.m],
            'A': [0.5, self.g, 1],
            'M': [0.5, self.g, self.m],
            'M1': [0.5, 1, self.g],
            'M2': [0.5, self.g, self.m],
            'D': [0.5, self.g, self.m],
            'D1': [0.5, self.g, -self.m],
            'E': [0.5, 0.5, 0.5],
            'H': [0, self.g, 1 - self.m],
            'H1': [0, 1 - self.g, self.m],
            'H2': [0, self.g, -self.m],
            'X': [0, 0.5, 0],
            'Y': [0, 0, 0.5],
            'Y1': [0, self.g, 0.5],
            'Z': [0.5, 0, 0],
        }
        sc_special_points[self.name] = points
        ibz_points[self.name] = points

        # Ruta en la zona de Brillouin
        special_segments[self.name] = [
            ('C', 'Y'), ('Y', 'F'), ('F', 'L'), ('L', 'IjI1'), ('IjI1', 'Z'),
            ('Z', 'F1jY'), ('F1jY', 'X1jX'), ('X1jX', 'C'), ('C', 'NjM'),
            ('NjM', 'C')
        ]

def complete_cell(cell):
    """Calculate complete cell with missing lattice vectors.

    Returns a new 3x3 ndarray.
    """
    if hasattr(cell, "get_cell"):
    	cell = cell.get_cell()

    cell = np.array(cell, dtype=float)
    missing = np.nonzero(~cell.any(axis=1))[0]

    if len(missing) == 3:
        cell.flat[::4] = 1.0
    if len(missing) == 2:
        # Must decide two vectors:
        V, s, WT = np.linalg.svd(cell.T)
        sf = [s[0], 1, 1]
        cell = (V @ np.diag(sf) @ WT).T
        if np.sign(np.linalg.det(cell)) < 0:
            cell[missing[0]] = -cell[missing[0]]
    elif len(missing) == 1:
        i = missing[0]
        cell[i] = np.cross(cell[i - 2], cell[i - 1])
        cell[i] /= np.linalg.norm(cell[i])

    return cell

def cell_to_cellpar(cell, radians=False):
	"""Returns the cell parameters [a, b, c, alpha, beta, gamma].

	Angles are in degrees unless radian=True is used.
	"""
	lengths = [np.linalg.norm(v) for v in cell]
	angles = []
	for i in range(3):
		j = i - 1
		k = i - 2
		ll = lengths[j] * lengths[k]
		if ll > 1e-16:
			x = np.dot(cell[j], cell[k]) / ll
			angle = 180.0 / np.pi * np.arccos(x)
		else:
			angle = 90.0
		angles.append(angle)
	if radians:
		angles = [angle * pi / 180 for angle in angles]
	return np.array(lengths + angles)

class UnconventionalLattice(ValueError):
    pass
    
class LatticeChecker:
	 # The check order is slightly different than elsewhere listed order
	 # as we need to check HEX/RHL before the ORCx family.
	 check_orders = {
		  1: ['LINE'],
		  2: ['SQR', 'RECT', 'HEX2D', 'CRECT', 'OBL'],
		  3: ['CUB', 'FCC', 'BCC', 'TET', 'BCT', 'HEX', 'RHL',
				'ORC', 'ORCF', 'ORCI', 'ORCC', 'MCL', 'MCLC', 'TRI']}

	 def __init__(self, cell, eps=2e-4):
		  """Generate Bravais lattices that look (or not) like the given cell.

		  The cell must be reduced to canonical form, i.e., it must
		  be possible to produce a cell with the same lengths and angles
		  by directly through one of the Bravais lattice classes.

		  Generally for internal use (this module).

		  For each of the 14 Bravais lattices, this object can produce
		  a lattice object which represents the same cell, or None if
		  the tolerance eps is not met."""
		  self.cell = cell
		  self.eps = eps

		  self.cellpar = cell_to_cellpar(cell)

		  self.lengths = self.A, self.B, self.C = self.cellpar[:3]
		  self.angles = self.cellpar[3:]

		  # Use a 'neutral' length for checking cubic lattices
		  self.A0 = self.lengths.mean()

		  # Vector of the diagonal and then off-diagonal dot products:
		  #   [a1 · a1, a2 · a2, a3 · a3, a2 · a3, a3 · a1, a1 · a2]
		  self.prods = (cell @ cell.T).flat[[0, 4, 8, 5, 2, 1]]


	 def celldiff(self, cell1, cell2):
		 """Return a unitless measure of the difference between two cells."""
		 cell1 = complete_cell(cell1)
		 cell2 = complete_cell(cell2)
		 v1v2 = np.abs(np.linalg.det(cell1)) * np.abs(np.linalg.det(cell2))
		 if v1v2 < 1e-10:
			  # (Proposed cell may be linearly dependent)
			  return np.inf

		 scale = v1v2**(-1. / 3.)  # --> 1/Ang^2
		 x1 = cell1 @ cell1.T
		 x2 = cell2 @ cell2.T
		 dev = scale * np.abs(x2 - x1).max()
		 return dev

	 def _check(self, latcls, *args):
		  if any(arg <= 0 for arg in args):
		  	return None
		  try:
		  		lat = latcls(*args)
		  except UnconventionalLattice:
		  		return None

		  newcell = lat
		  err = self.celldiff(self.cell, newcell)
		  if err < self.eps:
		  		return lat

	 def match(self):
		  """Match cell against all lattices, returning most symmetric match.

		  Returns the lattice object.  Raises RuntimeError on failure."""
		  for name in self.check_orders[self.cell.rank]:
		  		lat = self.query(name)
		  		if lat:
		  			 return lat
		  raise RuntimeError('Could not find lattice type for cell '
									'with lengths and angles {}'
									.format(self.cellpar.tolist()))

	 def query(self, latname):
		  """Match cell against named Bravais lattice.

		  Return lattice object on success, None on failure."""
		  meth = getattr(self, latname)

		  lat = meth()
		  return lat

	 def LINE(self):
		  return self._check(LINE, self.lengths[0])

	 def SQR(self):
		  return self._check(SQR, self.lengths[0])

	 def RECT(self):
		  return self._check(RECT, *self.lengths[:2])

	 def CRECT(self):
		  return self._check(CRECT, self.lengths[0], self.angles[2])

	 def HEX2D(self):
		  return self._check(HEX2D, self.lengths[0])

	 def OBL(self):
		  return self._check(OBL, *self.lengths[:2], self.angles[2])

	 def CUB(self):
		  # These methods (CUB, FCC, ...) all return a lattice object if
		  # it matches, else None.
		  return self._check(CUB, self.A0)

	 def FCC(self):
		  return self._check(FCC, np.sqrt(2) * self.A0)

	 def BCC(self):
		  return self._check(BCC, 2.0 * self.A0 / np.sqrt(3))

	 def TET(self):
		  return self._check(TET, self.A, self.C)

	 def _bct_orci_lengths(self):
		  # Coordinate-system independent relation for BCT and ORCI
		  # standard cells:
		  #   a1 · a1 + a2 · a3 == a² / 2
		  #   a2 · a2 + a3 · a1 == a² / 2 (BCT)
		  #                     == b² / 2 (ORCI)
		  #   a3 · a3 + a1 · a2 == c² / 2
		  # We use these to get a, b, and c in those cases.
		  prods = self.prods
		  lengthsqr = 2.0 * (prods[:3] + prods[3:])
		  if any(lengthsqr < 0):
		  		return None
		  return np.sqrt(lengthsqr)

	 def BCT(self):
		  lengths = self._bct_orci_lengths()
		  if lengths is None:
		  		return None
		  return self._check(BCT, lengths[0], lengths[2])

	 def HEX(self):
		  return self._check(HEX, self.A, self.C)

	 def RHL(self):
		  return self._check(RHL, self.A, self.angles[0])

	 def ORC(self):
		  return self._check(ORC, *self.lengths)

	 def ORCF(self):
		  # ORCF standard cell:
		  #   a2 · a3 = a²/4
		  #   a3 · a1 = b²/4
		  #   a1 · a2 = c²/4
		  prods = self.prods
		  if all(prods[3:] > 0):
		  		orcf_abc = 2 * np.sqrt(prods[3:])
		  		return self._check(ORCF, *orcf_abc)

	 def ORCI(self):
		  lengths = self._bct_orci_lengths()
		  if lengths is None:
		  		return None
		  return self._check(ORCI, *lengths)

	 def _orcc_ab(self):
		  # ORCC: a1 · a1 + a2 · a3 = a²/2
		  #       a2 · a2 - a2 · a3 = b²/2
		  prods = self.prods
		  orcc_sqr_ab = np.empty(2)
		  orcc_sqr_ab[0] = 2.0 * (prods[0] + prods[5])
		  orcc_sqr_ab[1] = 2.0 * (prods[1] - prods[5])
		  if all(orcc_sqr_ab > 0):
		  		return np.sqrt(orcc_sqr_ab)

	 def ORCC(self):
		  orcc_lengths_ab = self._orcc_ab()
		  if orcc_lengths_ab is None:
		  		return None
		  return self._check(ORCC, *orcc_lengths_ab, self.C)

	 def MCL(self):
		  return self._check(MCL, *self.lengths, self.angles[0])

	 def MCLC(self):
		  # MCLC is similar to ORCC:
		  orcc_ab = self._orcc_ab()
		  if orcc_ab is None:
		  		return None

		  prods = self.prods
		  C = self.C
		  mclc_a, mclc_b = orcc_ab[::-1]  # a, b reversed wrt. ORCC
		  mclc_cosa = 2.0 * prods[3] / (mclc_b * C)
		  if -1 < mclc_cosa < 1:
		  		mclc_alpha = np.arccos(mclc_cosa) * 180 / np.pi
		  		if mclc_b > C:
					 # XXX Temporary fix for certain otherwise
					 # unrecognizable lattices.
					 #
					 # This error could happen if the input lattice maps to
					 # something just outside the domain of conventional
					 # lattices (less than the tolerance).  Our solution is to
					 # propose a nearby conventional lattice instead, which
					 # will then be accepted if it's close enough.
		  			 mclc_b = 0.5 * (mclc_b + C)
		  			 C = mclc_b
		  		return self._check(MCLC, mclc_a, mclc_b, C, mclc_alpha)

	 def TRI(self):
		  return self._check(TRI, *self.cellpar)


niggli_op_table = {  # Generated by generate_niggli_op_table()
	 'BCC': [(1, 0, 0, 0, 1, 0, 0, 0, 1)],
	 'BCT': [(1, 0, 0, 0, 1, 0, 0, 0, 1),
				(0, 1, 0, 0, 0, 1, 1, 0, 0),
				(0, 1, 0, 1, 0, 0, 1, 1, -1),
				(-1, 0, 1, 0, 1, 0, -1, 1, 0),
				(1, 1, 0, 1, 0, 0, 0, 0, -1)],
	 'CUB': [(1, 0, 0, 0, 1, 0, 0, 0, 1)],
	 'FCC': [(1, 0, 0, 0, 1, 0, 0, 0, 1)],
	 'HEX': [(1, 0, 0, 0, 1, 0, 0, 0, 1), (0, 1, 0, 0, 0, 1, 1, 0, 0)],
	 'ORC': [(1, 0, 0, 0, 1, 0, 0, 0, 1)],
	 'ORCC': [(1, 0, 0, 0, 1, 0, 0, 0, 1),
				 (1, 0, -1, 1, 0, 0, 0, -1, 0),
				 (-1, 1, 0, -1, 0, 0, 0, 0, 1),
				 (0, 1, 0, 0, 0, 1, 1, 0, 0),
				 (0, -1, 1, 0, -1, 0, 1, 0, 0)],
	 'ORCF': [(0, -1, 0, 0, 1, -1, 1, 0, 0), (-1, 0, 0, 1, 0, 1, 1, 1, 0)],
	 'ORCI': [(0, 0, -1, 0, -1, 0, -1, 0, 0),
				 (0, 0, 1, -1, 0, 0, -1, -1, 0),
				 (0, 1, 0, 1, 0, 0, 1, 1, -1),
				 (0, -1, 0, 1, 0, -1, 1, -1, 0)],
	 'RHL': [(0, -1, 0, 1, 1, 1, -1, 0, 0),
				(1, 0, 0, 0, 1, 0, 0, 0, 1),
				(1, -1, 0, 1, 0, -1, 1, 0, 0)],
	 'TET': [(1, 0, 0, 0, 1, 0, 0, 0, 1), (0, 1, 0, 0, 0, 1, 1, 0, 0)],
	 'MCL': [(0, 0, 1, -1, -1, 0, 1, 0, 0),
				(-1, 0, 0, 0, 1, 0, 0, 0, -1),
				(0, 0, -1, 1, 1, 0, 0, -1, 0),
				(0, -1, 0, 1, 0, 1, -1, 0, 0),
				(0, 1, 0, -1, 0, -1, 0, 0, 1),
				(-1, 0, 0, 0, 1, 1, 0, 0, -1),
				(0, 1, 0, 1, 0, -1, -1, 0, 0),
				(0, 0, 1, 1, -1, 0, 0, 1, 0),
				(0, 1, 0, -1, 0, 0, 0, 0, 1),
				(0, 0, -1, -1, 1, 0, 1, 0, 0),
				(1, 0, 0, 0, 1, -1, 0, 0, 1),
				(0, -1, 0, -1, 0, 1, 0, 0, -1),
				(-1, 0, 0, 0, -1, 1, 0, 1, 0),
				(1, 0, 0, 0, -1, -1, 0, 1, 0),
				(0, 0, -1, 1, 0, 0, 0, -1, 0)],
	 'MCLC': [(1, 1, 1, 1, 0, 1, 0, 0, -1),
				 (1, 1, 1, 1, 1, 0, -1, 0, 0),
				 (1, -1, 1, -1, 0, 1, 0, 0, -1),
				 (-1, 1, 0, 1, 0, 0, 0, 0, -1),
				 (1, 0, 0, 0, 1, 0, 0, 0, 1),
				 (-1, 0, -1, 1, -1, -1, 0, 0, 1),
				 (1, -1, -1, 1, -1, 0, -1, 0, 0),
				 (-1, -1, 0, -1, 0, -1, 1, 0, 0),
				 (1, 0, 1, 1, 0, 0, 0, 1, 0),
				 (-1, 1, 0, -1, 0, 1, 1, 0, 0),
				 (0, -1, 1, -1, 0, 1, 0, 0, -1),
				 (-1, -1, 0, -1, 0, 0, 0, 0, -1),
				 (-1, -1, 1, -1, 0, 1, 0, 0, -1),
				 (1, 0, 0, 0, -1, 1, 0, 0, -1),
				 (-1, 0, -1, 0, -1, -1, 0, 0, 1),
				 (1, 0, -1, -1, 1, -1, 0, 0, 1),
				 (1, -1, 1, 1, -1, 0, 0, 1, 0),
				 (0, -1, 0, 1, 0, -1, 0, 0, 1),
				 (-1, 0, 0, 1, 1, 1, 0, 0, -1),
				 (1, 0, -1, 0, 1, -1, 0, 0, 1),
				 (-1, 1, 0, 1, 1, -1, 0, -1, 0),
				 (1, 1, -1, 1, -1, 0, -1, 0, 0),
				 (-1, -1, -1, -1, -1, 0, 0, 1, 0),
				 (-1, 1, 1, 1, 0, 1, 0, 0, -1),
				 (-1, 0, 0, 0, -1, 0, 0, 0, 1),
				 (-1, -1, 1, 1, -1, 0, 0, 1, 0),
				 (1, 1, 0, -1, 0, -1, 0, 0, 1)],
	 'TRI': [(0, -1, 0, -1, 0, 0, 0, 0, -1),
				(0, 1, 0, 0, 0, 1, 1, 0, 0),
				(0, 0, -1, 0, -1, 0, -1, 1, 0),
				(0, 0, 1, 0, 1, 0, -1, 0, 0),
				(0, -1, 0, 0, 0, -1, 1, 1, 1),
				(0, 1, 0, 0, 0, 1, 1, -1, 0),
				(0, 0, -1, 0, -1, 0, -1, 0, 0),
				(-1, 1, 0, 0, 0, -1, 0, -1, 0),
				(0, 0, 1, 1, -1, 0, 0, 1, 0),
				(0, 0, -1, 1, 1, 1, 0, -1, 0),
				(-1, 0, 0, 0, 1, 0, 0, -1, -1),
				(0, 0, 1, 1, 0, 0, 0, 1, 0),
				(0, 0, 1, 0, 1, 0, -1, -1, -1),
				(-1, 0, 0, 0, 0, -1, 0, -1, 0),
				(0, -1, 0, 0, 0, -1, 1, 0, 0),
				(1, 0, 0, 0, 1, 0, 0, 0, 1),
				(0, 0, -1, -1, 0, 0, 1, 1, 1),
				(0, 0, -1, -1, 0, 0, 0, 1, 0),
				(-1, -1, -1, 0, 0, 1, 0, 1, 0)]
}

def pick_best_lattice(matching_lattices):
	 """Return (lat, op) with lowest orthogonality defect."""
	 best = None
	 best_defect = np.inf
	 for lat, op in matching_lattices:
		  cell = lat.get_cell()
		  orthogonality_defect = np.prod( np.linalg.norm(cell, axis=1) ) / np.abs(np.linalg.det(cell))
		  if orthogonality_defect < best_defect:
		  		best = lat, op
		  		best_defect = orthogonality_defect
	 return best

def uncomplete(cell, pbc):
	  """Return new cell, zeroing cell vectors where not periodic."""
	  _pbc = np.empty(3, bool)
	  _pbc[:] = pbc
	  cell[~_pbc] = 0
	  return cell

class _gtensor(object):
	 """The G tensor as defined in Grosse-Kunstleve."""
	 def __init__(self, cell):

		  self.cell = cell

		  self.epsilon = 1e-5 * abs(np.linalg.det(cell))**(1. / 3.)

		  self.a = np.dot(cell[0], cell[0])
		  self.b = np.dot(cell[1], cell[1])
		  self.c = np.dot(cell[2], cell[2])

		  self.x = 2 * np.dot(cell[1], cell[2])
		  self.y = 2 * np.dot(cell[0], cell[2])
		  self.z = 2 * np.dot(cell[0], cell[1])

		  self._G = np.array([[self.a, self.z / 2., self.y / 2.],
									 [self.z / 2., self.b, self.x / 2.],
									 [self.y / 2., self.x / 2., self.c]])

	 def update(self, C):
		  """Procedure A0 as defined in Krivy."""
		  self._G = np.dot(C.T, np.dot(self._G, C))

		  self.a = self._G[0][0]
		  self.b = self._G[1][1]
		  self.c = self._G[2][2]

		  self.x = 2 * self._G[1][2]
		  self.y = 2 * self._G[0][2]
		  self.z = 2 * self._G[0][1]

	 def get_new_cell(self):
		  """Returns new basis vectors"""
		  a = np.sqrt(self.a)
		  b = np.sqrt(self.b)
		  c = np.sqrt(self.c)

		  ad = self.cell[0] / np.linalg.norm(self.cell[0])

		  Z = np.cross(self.cell[0], self.cell[1])
		  Z /= np.linalg.norm(Z)
		  X = ad - np.dot(ad, Z) * Z
		  X /= np.linalg.norm(X)
		  Y = np.cross(Z, X)

		  alpha = np.arccos(self.x / (2 * b * c))
		  beta = np.arccos(self.y / (2 * a * c))
		  gamma = np.arccos(self.z / (2 * a * b))

		  va = a * np.array([1, 0, 0])
		  vb = b * np.array([np.cos(gamma), np.sin(gamma), 0])
		  cx = np.cos(beta)
		  cy = (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) \
				/ np.sin(gamma)
		  cz = np.sqrt(1. - cx * cx - cy * cy)
		  vc = c * np.array([cx, cy, cz])

		  abc = np.vstack((va, vb, vc))
		  T = np.vstack((X, Y, Z))
		  return np.dot(abc, T)


def niggli_reduce_cell(cell):
	 C = np.eye(3, dtype=int)
	 cell = np.asarray(cell, dtype=float)
	 G = _gtensor(cell)

	 def lt(x, y, epsilon=G.epsilon):
		  return x < y - epsilon

	 def gt(x, y, epsilon=G.epsilon):
		  return lt(y, x, epsilon)

	 def eq(x, y, epsilon=G.epsilon):
		  return not (lt(x, y, epsilon) or gt(x, y, epsilon))

	 # Once A2 and A5-A8 all evaluate to False, the unit cell will have
	 # been fully reduced.
	 for count in range(10000):
		  if gt(G.a, G.b) or (eq(G.a, G.b) and gt(np.abs(G.x), np.abs(G.y))):
				# Procedure A1
		  		A = np.array([[0, -1, 0],
								  [-1, 0, 0],
								  [0, 0, -1]])
		  		G.update(A)
		  		C = np.dot(C, A)

		  if gt(G.b, G.c) or (eq(G.b, G.c) and gt(np.abs(G.y), np.abs(G.z))):
				# Procedure A2
		  		A = np.array([[-1, 0, 0],
								  [0, 0, -1],
								  [0, -1, 0]])
		  		G.update(A)
		  		C = np.dot(C, A)
		  		continue

		  if gt(G.x * G.y * G.z, 0, G.epsilon**3):
		  		# Procedure A3
		  		i = -1 if lt(G.x, 0) else 1
		  		j = -1 if lt(G.y, 0) else 1
		  		k = -1 if lt(G.z, 0) else 1
		  else:
				# Procedure A4
		  		i = -1 if gt(G.x, 0) else 1
		  		j = -1 if gt(G.y, 0) else 1
		  		k = -1 if gt(G.z, 0) else 1

		  		if i * j * k == -1:
		  			 if eq(G.z, 0):
		  				  k = -1
		  			 elif eq(G.y, 0):
		  				  j = -1
		  			 elif eq(G.x, 0):
		  				  i = -1
		  			 else:
		  				  raise RuntimeError('p unassigned and i*j*k < 0!')

		  A = np.array([[i, 0, 0],
							 [0, j, 0],
							 [0, 0, k]])
		  G.update(A)
		  C = np.dot(C, A)

		  if (lt(G.b, np.abs(G.x)) or
				(eq(G.x, G.b) and lt(2 * G.y, G.z)) or
				(eq(G.x, -G.b) and lt(G.z, 0))):
				# Procedure A5
		  		A = np.array([[1, 0, 0],
								  [0, 1, -np.sign(G.x)],
								  [0, 0, 1]], dtype=int)
		  		G.update(A)
		  		C = np.dot(C, A)
		  elif (lt(G.a, np.abs(G.y)) or
				  (eq(G.y, G.a) and lt(2 * G.x, G.z)) or
				  (eq(G.y, -G.a) and lt(G.z, 0))):
				# Procedure A6
		  		A = np.array([[1, 0, -np.sign(G.y)],
								  [0, 1, 0],
								  [0, 0, 1]], dtype=int)
		  		G.update(A)
		  		C = np.dot(C, A)
		  elif (lt(G.a, np.abs(G.z)) or
				  (eq(G.z, G.a) and lt(2 * G.x, G.y)) or
				  (eq(G.z, -G.a) and lt(G.y, 0))):
				# Procedure A7
		  		A = np.array([[1, -np.sign(G.z), 0],
								  [0, 1, 0],
								  [0, 0, 1]], dtype=int)
		  		G.update(A)
		  		C = np.dot(C, A)
		  elif (lt(G.x + G.y + G.z + G.a + G.b, 0) or
				  (eq(G.x + G.y + G.z + G.a + G.b, 0) and
					gt(2 * (G.a + G.y) + G.z, 0))):
				# Procedure A8
		  		A = np.array([[1, 0, 1],
								  [0, 1, 1],
								  [0, 0, 1]])
		  		G.update(A)
		  		C = np.dot(C, A)
		  else:
		  		break
	 else:
		  raise RuntimeError('Niggli did not converge \
					 in {n} iterations!'.format(n=count))
	 return G.get_new_cell(), C

def niggli_reduce(cell, eps=1e-5):
	  """Niggli reduce this cell, returning a new cell and mapping.

	  See also :func:`ase.build.tools.niggli_reduce_cell`."""
	  cell, op = niggli_reduce_cell(cell)
	  return cell, op

def identify_lattice(cell, eps=2e-4, *, pbc=[True, True, True]):
	 """Find Bravais lattice representing this cell.

	 Returns Bravais lattice object representing the cell along with
	 an operation that, applied to the cell, yields the same lengths
	 and angles as the Bravais lattice object."""
	 npbc = sum(pbc)

	 cell = uncomplete(cell, pbc)
	 rcell, reduction_op = niggli_reduce(cell, eps=eps)

	 # We tabulate the cell's Niggli-mapped versions so we don't need to
	 # redo any work when the same Niggli-operation appears multiple times
	 # in the table:
	 memory = {}

	 # We loop through the most symmetric kinds (CUB etc.) and return
	 # the first one we find:
	 check_orders = {
		  1: ['LINE'],
		  2: ['SQR', 'RECT', 'HEX2D', 'CRECT', 'OBL'],
		  3: ['CUB', 'FCC', 'BCC', 'TET', 'BCT', 'HEX', 'RHL',
				'ORC', 'ORCF', 'ORCI', 'ORCC', 'MCL', 'MCLC', 'TRI']}

	 for latname in check_orders[npbc]:
		  # There may be multiple Niggli operations that produce valid
		  # lattices, at least for MCL.  In that case we will pick the
		  # one whose angle is closest to 90, but it means we cannot
		  # just return the first one we find so we must remember then:
		  matching_lattices = []

		  for op_key in niggli_op_table[latname]:
		  		checker_and_op = memory.get(op_key)
		  		if checker_and_op is None:
		  			 normalization_op = np.array(op_key).reshape(3, 3)
		  			 candidate = np.linalg.inv(normalization_op.T) @ rcell
		  			 checker = LatticeChecker(candidate, eps=eps)
		  			 memory[op_key] = (checker, normalization_op)
		  		else:
		  			 checker, normalization_op = checker_and_op
  
		  		lat = checker.query(latname)
		  		if lat is not None:
		  			 op = normalization_op @ np.linalg.inv(reduction_op)
		  			 matching_lattices.append((lat, op))
  
		  if not matching_lattices:
		  		continue  # Move to next Bravais lattice

		  lat, op = pick_best_lattice(matching_lattices)

		  if npbc == 2 and op[2, 2] < 0:
		  		op = flip_2d_handedness(op)

		  return lat, op

	 raise RuntimeError('Failed to recognize lattice')

if __name__ == "__main__":
    # Example: Hexagonal cell
    cell_hex = np.array([[1.0, 0.0, 0.0],               # Vector a
                         [-0.5, np.sqrt(3) / 2, 0.0],   # Vector b
                         [0.0, 0.0, 2.0]])              # Vector c

    # Identify the hexagonal lattice
    try:
        lattice, operation = identify_lattice(cell_hex, eps=1e-4, pbc=[True, True, True])
        print(f"The identified lattice type is: {lattice.name}")
        print(f"The identified lattice type is: { lattice.get_special_points() }")
    except RuntimeError as e:
        print(f"Could not identify the lattice: {e}")


