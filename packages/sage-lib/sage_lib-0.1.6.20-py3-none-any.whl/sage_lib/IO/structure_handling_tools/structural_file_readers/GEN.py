try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import re
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing re: {str(e)}\n")
    del sys

class GEN:
    """
    A class for managing and exporting atomic structures in the FHI-aims file format.

    This class extends FileManager and AtomicProperties to provide functionalities for
    reading and writing atomic structures in the format used by FHI-aims, a density
    functional theory (DFT) code.

    Attributes:
        _latticeVectors (np.ndarray): Array of lattice vectors defining the unit cell.
        _atomLabelsList (np.ndarray): List of labels for each atom in the structure.
        _atomPositions (np.ndarray): Array of atomic positions in Cartesian coordinates.
        _atomPositions_fractional (np.ndarray): Array of atomic positions in fractional coordinates.
    """

    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initialize a GEN object.

        Parameters:
            file_location (str): Default directory for reading and writing files.
            name (str): Name identifier for the GEN instance.
            **kwargs: Additional keyword arguments for extended functionalities.
        """
        pass

    def export_as_GEN(self, file_location:str=None, group_elements_and_positions:bool=False, verbose:bool=False) -> bool:
        """
        Export the atomic structure data as a .gen file.

        This method writes the atomic structure information, including the lattice vectors
        and atom positions, to a file in the .gen format used by FHI-aims.

        Parameters:
            file_location (str): The file path where the .gen file will be saved.
            group_elements_and_positions (bool): If True, groups elements and positions. (Currently not implemented)
            verbose (bool): If True, prints additional information during execution.

        Returns:
            bool: True if the file was successfully written, False otherwise.
        """
        file_location = file_location if file_location is not None else self.file_location+'POSCAR' if isinstance(self.file_location, str) else self.file_location
        file_str = ''
        
        with open(file_location, 'w') as file:
            file_str += f"{int(self.atomCount)}  S\n"
            file_str += f"{' '.join(self.uniqueAtomLabels) }\n"

            # Create a dictionary mapping atom labels to their indices
            ids_dict = {n:i+1 for i, n in enumerate(self.uniqueAtomLabels)}

            # Write atom positions to the file
            for i, (id_label, (x, y, z)) in enumerate(zip(self.atomLabelsList, self.atomPositions), 1):
                file_str += f"{i}\t{ids_dict[id_label]}\t{x:.12f}\t{y:.12f}\t{z:.12f}\n"
            file_str += f"    0.000\t0.000\t0.000\t\n"

            # Write lattice vectors if they are defined
            if isinstance(self.latticeVectors, np.ndarray):
                for (lv_a, lv_b, lv_c) in self.latticeVectors:
                    file_str += f"    {lv_a:.12f}\t{lv_b:.12f}\t{lv_c:.12f}\n"

            file.write(file_str)

    def read_GEN(self, file_location:str=None):
        """
        Read atomic structure data from a .gen file.

        This method parses a .gen file and extracts atomic structure information,
        including atom positions and lattice vectors.

        Parameters:
            file_location (str): The file path of the .gen file to be read.

        Returns:
            dict: A dictionary containing atom count, unique atom labels, atom labels list,
                  lattice vectors, and atom positions.
        """
        file_location = file_location if isinstance(file_location, str) else self.file_location

        lines = [n for n in self.read_file(file_location)]

        # Parse the first line for the number of atoms
        atomCount = int(lines[0].split()[0])

        # Get the unique atom labels from the second line
        uniqueAtomLabels = lines[1].split()

        # Initialize lists to hold atom data and positions
        atomLabelsList = []
        atomPositions = []

        # Process atom data
        for line in lines[2:2+atomCount]:
            parts = line.split()
            atomLabelsList.append(uniqueAtomLabels[int(parts[1])-1])
            atomPositions.append([float(parts[2]), float(parts[3]), float(parts[4])])

        # Initialize lattice vectors and check for their presence
        latticeVectors = []
        if len(lines) > 3 + atomCount:
            for line in lines[3+atomCount:]:
                parts = line.split()
                latticeVectors.append([float(parts[0]), float(parts[1]), float(parts[2])])

        # Assign read data to class attributes
        self._atomPositions = np.array(atomPositions, dtype=np.float64)
        self._latticeVectors = np.array(latticeVectors, dtype=np.float64)
        self._atomLabelsList = np.array(atomLabelsList)
        self._uniqueAtomLabels = np.array(uniqueAtomLabels)
        self._atomCount = np.array(atomCount, dtype=np.int64)

        return {
            "atomCount": atomCount,
            "uniqueAtomLabels": uniqueAtomLabels,
            "atomLabelsList": atomLabelsList,
            "latticeVectors": latticeVectors,
            "atomPositions": atomPositions,
        }
        
    def read_DFTB_gen(self, file_location: str = None):
        """Alias to read a .gen file as used in DFTB calculations."""
        self.read_GEN(file_location)
