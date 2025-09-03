# Import necessary libraries and handle import errors

class AIMS:
    """
    A class for managing and exporting atomic structures in the FHI-aims file format.

    This class extends FileManager and AtomicProperties, providing functionalities for reading and writing 
    atomic structures in the format used by FHI-aims, a density functional theory (DFT) code.

    Attributes:
        _latticeVectors: Array of lattice vectors defining the unit cell.
        _atomLabelsList: List of labels for each atom in the structure.
        _atomPositions: Array of atomic positions in Cartesian coordinates.
        _atomPositions_fractional: Array of atomic positions in fractional coordinates.
    """
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initialize an AIMS object.

        Parameters:
            file_location (str): Default directory for reading and writing files.
            name (str): Name identifier for the AIMS instance.
            **kwargs: Additional keyword arguments.
        """
        pass

    def export_as_AIMS(self, file_location:str=None, group_elements_and_positions:bool=False, verbose:bool=False) -> bool:
        """
        Exports the atomic structure in the FHI-aims file format.

        Parameters:
            file_location (str): The directory to save the exported file.
            group_elements_and_positions (bool): Whether to group elements and positions for readability.
            verbose (bool): Enable verbose output for debugging.

        Returns:
            bool: True if the file is successfully written, False otherwise.
        """
        file_location  = file_location  if not file_location  is None else self.file_location+'POSCAR' if self.file_location is str else self.file_location

        if group_elements_and_positions: self.group_elements_and_positions()

        with open(file_location, 'w') as file:
            # Write header information
            file.write("#=======================================================\n")
            file.write("# FHI-aims file: {}\n".format(file_location))
            file.write("# Created using SAGE script \n")
            file.write("#=======================================================\n")

            # Write lattice vectors
            for vector in self._latticeVectors:
                file.write("lattice_vector {} {} {}\n".format(*vector))

            # Write atoms
            for label, position in zip(self._atomLabelsList, self._atomPositions):
                file.write("atom {} {} {} {}\n".format(position[0], position[1], position[2], label))

    def read_AIMS(self, file_location:str=None):
        """
        Reads an FHI-aims file and extracts atomic structure information.

        Parameters:
            file_location (str): The directory of the file to be read.

        Note:
            This method populates the class attributes with lattice vectors and atomic positions
            extracted from the file.
        """
        file_location = file_location if type(file_location) == str else self.file_location

        lines = [n for n in self.read_file(file_location) ]

        self._latticeVectors = []
        self._atomLabelsList = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('lattice_vector'):
                # Extract lattice vectors
                parts = line.split()
                vector = [float(parts[1]), float(parts[2]), float(parts[3])]
                self._latticeVectors.append(vector)

            elif line.startswith('atom_frac'):
                if self._atomPositions_fractional is None: self._atomPositions_fractional = []
                # Extract fractional atomic positions and labels
                parts = line.split()
                label = parts[4]
                position = [float(parts[1]), float(parts[2]), float(parts[3])]
                self._atomLabelsList.append(label)
                self._atomPositions_fractional.append(position)

            elif line.startswith('atom'):
                if self._atomPositions is None: self._atomPositions = []
                # # Extract Cartesian atomic positions and labels
                parts = line.split()
                label = parts[4]
                position = [float(parts[1]), float(parts[2]), float(parts[3])]
                self._atomLabelsList.append(label)
                self._atomPositions.append(position)

        if self.atomPositions is not None:
            self._atomPositions  = np.array(self.atomPositions, np.float64)

        if self._atomPositions_fractional is not None:
            self._atomPositions_fractional  = np.array(self.atomPositions_fractional, np.float64)
    
        self._latticeVectors = np.array(self.latticeVectors, np.float64)
