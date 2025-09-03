try:
    from .PeriodicSystem import PeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.structure_handling_tools.PeriodicSystem: {str(e)}\n")
    del sys

try:
    from .NonPeriodicSystem import NonPeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.structure_handling_tools.NonPeriodicSystem: {str(e)}\n")
    del sys

try:
    from .plot import plot
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.structure_handling_tools.NonPeriodicSystem: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class AtomPosition(PeriodicSystem, NonPeriodicSystem, plot):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        PeriodicSystem.__init__(self, name=name, file_location=file_location)
        NonPeriodicSystem.__init__(self, name=name, file_location=file_location)
        self._comment = None
        self._atomCount = None  # N total number of atoms
        self._data_dtype = np.float64
        
    def NonPeriodic_2_Periodic(self, latticeVectors:np.array=None, center:bool=True, vacuum:float=12.0):
        """
        Converts a NonPeriodicSystem instance to a PeriodicSystem instance by creating a new PeriodicSystem 
        object and copying shared attributes from the NonPeriodicSystem. It then adjusts the atom positions 
        to ensure that the atom with the lowest coordinate in each axis is at least 6 Angstroms from the origin.
        Finally, it sets the lattice vectors based on the adjusted atom positions.

        :return: A new instance of PeriodicSystem with shared attributes copied and adjusted atom positions.
        """ 
        if self.latticeVectors is not None: 
            return self

        # Adjust atom positions
        min_coords = np.min(self.atomPositions, axis=0)
        max_coords = np.max(self.atomPositions, axis=0)
 
        self.atomPositions += (vacuum/2 - min_coords) if center else 0

        # Set lattice vectors
        self.latticeVectors = latticeVectors if latticeVectors is not None else \
            np.array([  [max_coords[0] + vacuum/2, 0, 0], 
                        [0, max_coords[1] + vacuum/2, 0], 
                        [0, 0, max_coords[2] + vacuum/2]])

        self.atomCoordinateType = 'Cartesian'

        return self
