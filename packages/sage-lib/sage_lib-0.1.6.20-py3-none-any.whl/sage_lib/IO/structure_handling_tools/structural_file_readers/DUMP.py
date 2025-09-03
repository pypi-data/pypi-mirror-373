try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import re
    import warnings
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing re / warnings: {str(e)}\n")
    del sys

from ....master.AtomicProperties import AtomicProperties

class DUMP:
    """
    A class to handle and parse LAMMPS dump files and convert the box bounds to VASP lattice vectors.
    
    Inherits from:
        FileManager: Manages file operations.
        AtomicProperties: Manages atomic properties.
    """

    atomic_numbers = AtomicProperties.atomic_numbers

    def __init__(self, file_location: str = None, name: str = None, **kwargs):
        """
        Initializes the DUMP object with the specified file location and name.

        Parameters:
            file_location (str, optional): Path to the dump file. Defaults to None.
            name (str, optional): Name of the file. Defaults to None.
        """
        pass

    @staticmethod
    def box_2_latticeVectors(box_bounds: list) -> np.ndarray:
        """
        Transforms LAMMPS box bounds to VASP lattice vectors.

        Parameters:
            box_bounds (list of tuple): List of 3 tuples representing the box bounds in LAMMPS.
                                        Each tuple contains (xlo, xhi), (ylo, yhi), and (zlo, zhi).
        
        Returns:
            np.ndarray: 3x3 matrix representing the lattice vectors for VASP.
        """
        # Extracting box bounds
        xlo, xhi = box_bounds[0]
        ylo, yhi = box_bounds[1]
        zlo, zhi = box_bounds[2]
        
        # Calculating lattice vectors
        a1 = [xhi - xlo, 0.0, 0.0]
        a2 = [0.0, yhi - ylo, 0.0]
        a3 = [0.0, 0.0, zhi - zlo]
        
        return np.array([a1, a2, a3])

    @staticmethod
    def latticeVectors_2_box(lattice_vectors: np.ndarray) -> list:
        """
        Transforms VASP lattice vectors to LAMMPS box bounds.

        Parameters:
            lattice_vectors (np.ndarray): 3x3 matrix representing the lattice vectors for VASP.
        
        Returns:
            list: List of 3 tuples representing the box bounds in LAMMPS.
                  Each tuple contains (xlo, xhi), (ylo, yhi), and (zlo, zhi).
        """
        if lattice_vectors.shape != (3, 3):
            raise ValueError("lattice_vectors must be a 3x3 matrix")
        
        # Extracting lattice vectors
        a1, a2, a3 = lattice_vectors
        
        # Calculating box bounds
        xlo, xhi = 0.0, a1[0]
        ylo, yhi = 0.0, a2[1]
        zlo, zhi = 0.0, a3[2]
        
        return [(xlo, xhi), (ylo, yhi), (zlo, zhi)]

    @staticmethod   
    def latticeVectors_2_triclinic_box(lattice_vectors: np.ndarray) -> list:
        """
        Transforms VASP lattice vectors to LAMMPS triclinic box bounds.

        Parameters:
            lattice_vectors (np.ndarray): 3x3 matrix representing the lattice vectors for VASP.
        
        Returns:
            list: List representing the box bounds in LAMMPS.
                  It includes (xlo, xhi), (ylo, yhi), (zlo, zhi), xy, xz, yz.
        """
        if lattice_vectors.shape != (3, 3):
            raise ValueError("lattice_vectors must be a 3x3 matrix")
        
        # Extracting lattice vectors
        a1, a2, a3 = lattice_vectors
        
        # Calculating box bounds
        xlo, xhi = 0.0, np.linalg.norm(a1)
        xy = np.dot(a1, a2) / xhi

        ylo, yhi = 0.0, np.sqrt(np.linalg.norm(a2)**2 - xy**2)

        xz = np.dot(a1, a3) / xhi
        yz = (np.dot(a2, a3) - xy * xz) / yhi
        zlo, zhi = 0.0, np.sqrt(np.linalg.norm(a3)**2 - xz**2 - yz**2)
        
        return [(xlo, xhi), (ylo, yhi), (zlo, zhi), xy, xz, yz]

    def read_DUMP(self, file_location: str = None, lines: list = None, verbose: bool = False) -> dict:
        """
        Reads a single timestep configuration from a LAMMPS dump file.

        Parameters:
            file_location (str, optional): Location of the dump file. Defaults to instance file location if None.
            lines (list, optional): List of lines from the dump file. If None, reads from file.
            verbose (bool, optional): If True, prints additional information. Defaults to False.

        Returns:
            dict: Parsed data for the specified timestep.
        """ 
        # Use the provided file location or the instance's file location
        file_location = file_location if isinstance(file_location, str) else self.file_location
        lines = lines or list(self.read_file(file_location, strip=False))

        data = {}

        # Initialize variables
        timestep = 0
        atom_count = 0
        box_bounds = []
        atoms_data = []
        column_names = []
        atom_positions = []
        atom_labels_list = []

        for i, line in enumerate(lines):
            if line.startswith("ITEM: TIMESTEP"):
                # Extract the timestep
                timestep = int(lines[i + 1].strip())

            elif line.startswith("ITEM: NUMBER OF ATOMS"):
                # Extract the number of atoms
                atom_count = int(lines[i + 1].strip())
                atom_positions = np.zeros((atom_count, 3))

            elif line.startswith("ITEM: BOX BOUNDS"):
                # Extract the box bounds
                for j in range(3):
                    box_bounds.append([float(x) for x in lines[i + 1 + j].strip().split()])

            elif line.startswith("ITEM: ATOMS"):
                # Extract column names and atoms data
                column_names = line.strip().split()[2:]
                atoms_data = np.zeros((atom_count, len(column_names)))
                for atom_i in range(atom_count):
                    atoms_data[atom_i, :] = list(map(float, lines[i + atom_i + 1].strip().split()))

                # Get positions and labels
                atom_positions = atoms_data[:, [column_names.index('x'), 
                                                column_names.index('y'), 
                                                column_names.index('z')]]
                atom_labels_list = [self._atomic_name[int(z)] for z in atoms_data[:, column_names.index('type')]]
                break

        # Set instance variables
        self._atomCount = atom_count
        self._timestep = timestep
        self._latticeVectors = self.box_2_latticeVectors(box_bounds)
        self._column_names = column_names
        self._atomPositions = atom_positions
        self._atomLabelsList = np.array(atom_labels_list)

        return {
            "timestep": timestep,
            "atom_count": atom_count,
            "lattice_vectors": self._latticeVectors,
            "column_names": column_names,
            "atom_positions": atom_positions,
            "atom_labels_list": atom_labels_list
        }

    @staticmethod
    def _masses2numbers(masses: np.ndarray) -> np.ndarray:
        """
        Guess atomic numbers from atomic masses.

        Parameters:
            masses (np.ndarray): Array of atomic masses.
        
        Returns:
            np.ndarray: Array of atomic numbers guessed from masses.
        """
        # Use the _atomic_mass_list to find the closest match for each mass
        return np.argmin(np.abs(self._atomic_mass_list - masses[:, None]), axis=1)

    def export_as_DUMP(self, file_location: str):
        """
        Exports the current timestep configuration to a LAMMPS dump file.

        Parameters:
            file_location (str): Location of the file to write the dump data.
        """
        with open(file_location, 'w') as file:
            # Write timestep
            file.write("ITEM: TIMESTEP\n")
            file.write(f"{self.timestep}\n")
            
            # Write number of atoms
            file.write("ITEM: NUMBER OF ATOMS\n")
            file.write(f"{self.atomCount}\n")

            # Transform lattice vectors to box bounds
            box_bounds = self.latticeVectors_2_triclinic_box(self._latticeVectors)
            
            xlo, xhi = box_bounds[0]
            ylo, yhi = box_bounds[1]
            zlo, zhi = box_bounds[2]
            xy, xz, yz = box_bounds[3], box_bounds[4], box_bounds[5]

            # Write box bounds
            if xy == 0 and xz == 0 and yz == 0:
                # Orthogonal box
                file.write("ITEM: BOX BOUNDS pp pp pp\n")
                file.write(f"{xlo} {xhi}\n")
                file.write(f"{ylo} {yhi}\n")
                file.write(f"{zlo} {zhi}\n")
            else:
                # Triclinic box
                file.write("ITEM: BOX BOUNDS xy xz yz pp pp pp\n")
                file.write(f"{xlo} {xhi} {xy}\n")
                file.write(f"{ylo} {yhi} {xz}\n")
                file.write(f"{zlo} {zhi} {yz}\n")
                
            # Write atoms data
            column_names = ['id','type'] + ['x', 'y', 'z']  # Adjust according to your actual column names
            file.write("ITEM: ATOMS " + " ".join(column_names) + "\n")
            for i in range(self.atomCount):
                data_line = f"{i + 1} "  # Atom ID (starting from 1)
                if hasattr(self, '_atomLabelsList'):
                    data_line += str(self.atomic_numbers[self.atomLabelsList[i]])+ " "
                data_line += " ".join(map(str, self.atomPositions[i])) + " "
                data_line += "\n"
                file.write(data_line)




