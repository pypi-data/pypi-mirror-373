class SI:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        pass
        
    def read_SI(self, file_location:str=None):
        try:
            import numpy as np
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
            del sys

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
