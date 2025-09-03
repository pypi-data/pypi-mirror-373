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

class LAMMPS:
    """
    A class to handle and parse LAMMPS dump files and convert the box bounds to VASP lattice vectors.
    
    Inherits from:
        FileManager: Manages file operations.
        AtomicProperties: Manages atomic properties.
    """
    atomic_mass = AtomicProperties.atomic_mass

    def __init__(self, file_location: str | None = None, name: str | None = None, **kwargs):
        """
        Initializes the DUMP object with the specified file location and name.

        Parameters:
            file_location (str, optional): Path to the dump file. Defaults to None.
            name (str, optional): Name of the file. Defaults to None.
        """
        pass

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

    def read_LAMMPS(self, file_location: str = None, lines: list = None, verbose: bool = False) -> dict:
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

    def export_as_LAMMPS(self, file_location: str):
        """
        Exports the current configuration to a LAMMPS data file.

        Parameters:
            file_location (str): Location of the file to write the data.
        """
        with open(file_location, 'w') as file:
            # LAMMPS Description
            file.write("SAGE generated file\n\n")
            
            # Counts of atoms, bonds, angles, etc.
            file.write(f"{self.atomCount} atoms\n")
            #file.write(f"{self.num_bonds} bonds\n")
            #file.write(f"{self.num_angles} angles\n")
            #file.write(f"{self.num_dihedrals} dihedrals\n")
            #file.write(f"{self.num_impropers} impropers\n\n")
            
            # Counts of atom types, bond types, etc.
            file.write(f"{len(self.uniqueAtomLabels)} atom types\n")
            #file.write(f"{len(self.bond_types)} bond types\n")
            #file.write(f"{len(self.angle_types)} angle types\n")
            #file.write(f"{len(self.dihedral_types)} dihedral types\n")
            #file.write(f"{len(self.improper_types)} improper types\n\n")
            
            # Box bounds
            (xlo, xhi), (ylo, yhi), (zlo, zhi), xy, xz, yz = self.latticeVectors_2_triclinic_box(self._latticeVectors)
            file.write(f"{xlo} {xhi} xlo xhi\n")
            file.write(f"{ylo} {yhi} ylo yhi\n")
            file.write(f"{zlo} {zhi} zlo zhi\n")
            file.write(f"{xy} {xz} {yz} xy xz yz\n\n")

            # Masses
            file.write("Masses\n\n")
            for i, unique_atom_label in enumerate(self.uniqueAtomLabels, start=1):
                file.write(f"{i} {self.atomic_mass[unique_atom_label]}\n")
            file.write("\n")
            '''
            # Nonbond Coeffs
            file.write("Nonbond Coeffs\n\n")
            for i, coeffs in enumerate(self.nonbond_coeffs, start=1):
                file.write(f"{i} " + " ".join(map(str, coeffs)) + "\n")
            file.write("\n")
            
            # Bond Coeffs
            file.write("Bond Coeffs\n\n")
            for i, coeffs in enumerate(self.bond_coeffs, start=1):
                file.write(f"{i} " + " ".join(map(str, coeffs)) + "\n")
            file.write("\n")
            
            # Angle Coeffs
            file.write("Angle Coeffs\n\n")
            for i, coeffs in enumerate(self.angle_coeffs, start=1):
                file.write(f"{i} " + " ".join(map(str, coeffs)) + "\n")
            file.write("\n")
            
            # Dihedral Coeffs
            file.write("Dihedral Coeffs\n\n")
            for i, coeffs in enumerate(self.dihedral_coeffs, start=1):
                file.write(f"{i} " + " ".join(map(str, coeffs)) + "\n")
            file.write("\n")
            
            # Improper Coeffs
            file.write("Improper Coeffs\n\n")
            for i, coeffs in enumerate(self.improper_coeffs, start=1):
                file.write(f"{i} " + " ".join(map(str, coeffs)) + "\n")
            file.write("\n")
            '''

            # Atoms
            label_dict = {unique_atom_label:i for i, unique_atom_label in enumerate(self.uniqueAtomLabels, start=1) }
            file.write("Atoms\n\n")
            for i, (atom_position, atom_label) in enumerate( zip(self.atomPositions, self.atomLabelsList) ):
                file.write(f"{i+1} {label_dict[atom_label]} {atom_position[0]} {atom_position[1]} {atom_position[2]}\n")
            file.write("\n")
            '''
            # Velocities
            file.write("Velocities\n\n")
            for velocity in self.velocities:
                file.write(f"{velocity['id']} {velocity['vx']} {velocity['vy']} {velocity['vz']}\n")
            file.write("\n")
            
            # Bonds
            file.write("Bonds\n\n")
            for bond in self.bonds:
                file.write(f"{bond['id']} {bond['bond-type']} {bond['atom-1']} {bond['atom-2']}\n")
            file.write("\n")
            
            # Angles
            file.write("Angles\n\n")
            for angle in self.angles:
                file.write(f"{angle['id']} {angle['angle-type']} {angle['atom-1']} {angle['atom-2']} {angle['atom-3']}\n")
            file.write("\n")
            
            # Dihedrals
            file.write("Dihedrals\n\n")
            for dihedral in self.dihedrals:
                file.write(f"{dihedral['id']} {dihedral['dihedral-type']} {dihedral['atom-1']} {dihedral['atom-2']} {dihedral['atom-3']} {dihedral['atom-4']}\n")
            file.write("\n")
            
            # Impropers
            file.write("Impropers\n\n")
            for improper in self.impropers:
                file.write(f"{improper['id']} {improper['improper-type']} {improper['atom-1']} {improper['atom-2']} {improper['atom-3']} {improper['atom-4']}\n")
            file.write("\n")
            '''

