import numpy as np
import re
import sys
import matplotlib.pyplot as plt
import json

class NumpyArrayEncoder(json.JSONEncoder):
    """Custom JSON Encoder for numpy arrays."""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            # Convert numpy array to list with metadata
            data = obj.tolist()
            shape = obj.shape
            dtype = str(obj.dtype)
            return {'__ndarray__': [shape, dtype, data]}
        return json.JSONEncoder.default(self, obj)

class PROFileManager:
    """
    Handles the reading and interpretation of VASP's PROCAR file and DFTB+ output files.

    This class parses the PROCAR file to extract:
    - K-points and their weights
    - Band energies and occupations
    - Orbital projections for each ion

    Additionally, it can parse DFTB+ output files to extract:
    - SCC convergence steps
    - Atomic charges and populations
    - Fermi levels and energies
    - Dipole moments

    Attributes:
        file_location (str): Path to the PROCAR or DFTB+ output file.
        name (str): Optional descriptive name for the data set.
        fermi_energy (float): The Fermi energy level for shifting band energies.
    """

    def __init__(self, file_location: str = None, name: str = None):
        """
        Initializes the PROFileManager instance.

        Parameters:
            file_location (str): Path to the PROCAR or DFTB+ output file.
            name (str): Optional descriptive name for the data set.
        """

        self.file_location = file_location
        self.name = name
        self._kpoints_number = None
        self._bands_number = None
        self._atom_count = None
        self._KPOINTS = None  # Array to store k-points and weights
        self._BANDS = None  # Array to store band energies and occupations
        self._data = None  # Array to store orbital projections
        self._fermi_energy = 0.0  # Default Fermi energy
        self.special_kpoints = None 
        self.dftb_data = {}  # Dictionary to store DFTB+ extracted data

    # Getters and Setters
    @property
    def kpoints_number(self):
        return self._kpoints_number

    @kpoints_number.setter
    def kpoints_number(self, value):
        self._kpoints_number = value

    @property
    def bands_number(self):
        return self._bands_number

    @bands_number.setter
    def bands_number(self, value):
        self._bands_number = value

    @property
    def atom_count(self):
        return self._atom_count

    @atom_count.setter
    def atom_count(self, value):
        self._atom_count = value

    @property
    def KPOINTS(self):
        return self._KPOINTS

    @KPOINTS.setter
    def KPOINTS(self, value):
        self._KPOINTS = value

    @property
    def BANDS(self):
        return self._BANDS

    @BANDS.setter
    def BANDS(self, value):
        self._BANDS = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def fermi_energy(self):
        return self._fermi_energy

    @fermi_energy.setter
    def fermi_energy(self, value):
        self._fermi_energy = value

    def _fix_number_format(self, line):
        """
        Fix improperly formatted numbers in the PROCAR file by:
        - Inserting spaces where numbers are concatenated without spaces.
        - Adding 'E' where necessary in scientific notation.
        """
        # Insert a space before any '+' or '-' that follows a digit (to separate numbers)
        line = re.sub(r'(\d)([+-])(\d)', r'\1 \2\3', line)
        # Match numbers missing the 'E' between the mantissa and exponent
        line = re.sub(r'(\d\.\d+)([+-]\d+)', r'\1E\2', line)
        return line

    def _read_band(self, band_lines, band_number, kpoint_number):
        """
        Reads and parses data for a single band.

        Parameters:
            band_lines (list): Lines containing data for a single band.
            band_number (int): Index of the band.
            kpoint_number (int): Index of the k-point.
        """
        band_info = band_lines[0].split()
        energy, occupation = float(band_info[4]), float(band_info[7])
        self.BANDS[kpoint_number, band_number, :] = [energy, occupation]

        for atom_index in range(self.atom_count):
            # Exclude the ion index (first element)
            data_line = band_lines[3 + atom_index]
            split_data = data_line.split()[1:]  # Exclude ion index
            self.data[kpoint_number, band_number, atom_index, :] = list(
                map(float, split_data)
            )


    def _read_kpoint(self, kpoint_lines, kpoint_number):
        """
        Reads and parses data for a single k-point.

        Parameters:
            kpoint_lines (list): Lines containing data for a single k-point.
            kpoint_number (int): Index of the k-point.
        """
        corrected_line = self._fix_number_format(kpoint_lines[0])
        kpoint_info = corrected_line.split()

        self.KPOINTS[kpoint_number, :] = [
            float(kpoint_info[3]),
            float(kpoint_info[4]),
            float(kpoint_info[5]),
            float(kpoint_info[8]),
        ]

        band_block_size = self.atom_count + 5
        for band_number in range(self.bands_number):
            start_line = 2 + band_block_size * band_number
            end_line = 1 + band_block_size * (band_number + 1)
            band_lines = kpoint_lines[start_line:end_line]
            self._read_band(band_lines, band_number, kpoint_number)

    def read_PROCAR(self):
        """
        Reads the PROCAR file and extracts k-points, bands, and orbital projections.

        Returns:
            bool: True if the file was successfully read, False otherwise.
        """
        if not self.file_location:
            raise ValueError("No file location provided for PROCAR.")

        try:
            with open(self.file_location, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            sys.stderr.write(f"File not found: {self.file_location}\n")
            return False

        header_info = lines[1].strip().split()
        self.kpoints_number = int(header_info[3])
        self.bands_number = int(header_info[7])
        self.atom_count = int(header_info[11])

        print(
            f"Reading PROCAR: KPOINTS={self.kpoints_number}, "
            f"BANDS={self.bands_number}, ATOMS={self.atom_count}"
        )

        # Adjust the last dimension to 10
        self.KPOINTS = np.zeros((self.kpoints_number, 4))
        self.BANDS = np.zeros((self.kpoints_number, self.bands_number, 2))
        self.data = np.zeros(
            (self.kpoints_number, self.bands_number, self.atom_count, 10)  # Changed from 11 to 10
        )

        kpoint_block_size = (self.atom_count + 5) * self.bands_number + 3
        for kpoint_number in range(self.kpoints_number):
            start_line = 3 + kpoint_block_size * kpoint_number
            end_line = start_line + kpoint_block_size
            kpoint_lines = lines[start_line:end_line]
            self._read_kpoint(kpoint_lines, kpoint_number)

        return True

    def detect_special_kpoints(self, distance_threshold=0.5, direction_threshold=0.1):
        """
        Detects special K-points based on changes in direction and large distances.

        Parameters:
            distance_threshold (float): Minimum distance to consider a K-point as special.
            direction_threshold (float): Minimum change in direction to consider a K-point as special.
        
        Returns:
            list: A list of special K-point coordinates.
        """
        special_kpoints = []
        kpoints = self.KPOINTS[:, :3]  # Extract K-point coordinates
        num_kpoints = len(kpoints)
        
        if num_kpoints < 2:  # If there are no valid K-points
            self.special_kpoints = np.array([])
            return self.special_kpoints
        
        for i in range(1, num_kpoints):
            # Calculate distance to the previous point
            distance = LA.norm(kpoints[i] - kpoints[i - 1])
            
            # Calculate direction change if not the first two points
            if i > 1:
                prev_direction = kpoints[i - 1] - kpoints[i - 2]
                curr_direction = kpoints[i] - kpoints[i - 1]
                prev_norm = LA.norm(prev_direction)
                curr_norm = LA.norm(curr_direction)
                
                # Avoid division by zero
                if prev_norm > 0 and curr_norm > 0:
                    cosine_similarity = np.dot(prev_direction, curr_direction) / (prev_norm * curr_norm)
                    angle_change = 1 - cosine_similarity  # Difference from perfect alignment
                else:
                    angle_change = 1.0  # Maximum change
            else:
                angle_change = 0.0  # No change for the first two points
            
            # Mark the point as special if conditions are met
            if distance > distance_threshold or angle_change > direction_threshold:
                special_kpoints.append(kpoints[i].tolist())
        
        # Add the first point as special (convention)
        special_kpoints.insert(0, kpoints[0].tolist())
        
        # Save the special K-points
        self.special_kpoints = np.array(special_kpoints)
        print(f"Detected {len(special_kpoints)} special K-points.")
        return self.special_kpoints


    def to_json(self):
        """
        Converts the extracted data into a JSON-compatible dictionary matching the desired format.
        """
        data_dict = {
            "path": {
                "kpts": {
                    "__ndarray__": [self.KPOINTS.shape, str(self.KPOINTS.dtype), self.KPOINTS.tolist()]
                },
                # Add other necessary components like 'special_points', 'labelseq', 'cell' if available
                # For now, we can include placeholders or omit if not applicable
            },
            "energies": {
                "__ndarray__": [self.BANDS.shape, str(self.BANDS.dtype), self.BANDS.tolist()],
                "reference": 0.0,  # Adjust if you have a different reference energy
                "__ase_objtype__": "bandstructure"
            },
            # Include additional data as needed
            "fermi_energy": self.fermi_energy,
            "kpoints_number": self.kpoints_number,
            "bands_number": self.bands_number,
            "atom_count": self.atom_count,
            "name": self.name
        }
        return data_dict

    def save_to_json(self, json_file_path):
        """
        Saves the extracted data to a JSON file.

        Parameters:
            json_file_path (str): The path to the JSON file to save.
        """
        data_dict = self.to_json()
        with open(json_file_path, 'w') as json_file:
            json.dump(data_dict, json_file, cls=NumpyArrayEncoder)


    # Plotting Functions
    def plot_band_structure(self, shift_fermi=False):
        """
        Plots the band structure.

        Parameters:
            shift_fermi (bool): If True, shift energies with respect to the Fermi energy.
        """
        energies = self.BANDS[:, :, 0]  # Energies
        if shift_fermi:
            energies -= self.fermi_energy

        k_distances = np.arange(self.kpoints_number)
        for band_idx in range(self.bands_number):
            plt.plot(k_distances, energies[:, band_idx], color='b')

        plt.xlabel('K-point Index')
        plt.ylabel('Energy (eV)')
        plt.title('Band Structure')
        plt.axhline(y=0 if shift_fermi else self.fermi_energy, color='k', linestyle='--')
        plt.show()

    def plot_density_of_states(self, shift_fermi=False, bins=200):
        """
        Plots the density of states (DOS).

        Parameters:
            shift_fermi (bool): If True, shift energies with respect to the Fermi energy.
            bins (int): Number of bins for the histogram.
        """
        energies = self.BANDS[:, :, 0].flatten()
        if shift_fermi:
            energies -= self.fermi_energy

        plt.hist(energies, bins=bins, density=True, alpha=0.7, color='g')
        plt.xlabel('Energy (eV)')
        plt.ylabel('Density of States')
        plt.title('Density of States')
        plt.axvline(x=0 if shift_fermi else self.fermi_energy, color='k', linestyle='--')
        plt.show()

    def plot_orbital_projections(self, orbital='s', shift_fermi=False):
        """
        Plots the band structure with orbital projections (fat bands).

        Parameters:
            orbital (str): Orbital to project ('s', 'p', 'd', etc.).
            shift_fermi (bool): If True, shift energies with respect to the Fermi energy.
        """
        orbital_indices = {'s': 1, 'p': slice(2, 5), 'd': slice(5, 10)}
        if orbital not in orbital_indices:
            raise ValueError(f"Invalid orbital: {orbital}. Choose from 's', 'p', or 'd'.")

        orbital_index = orbital_indices[orbital]
        energies = self.BANDS[:, :, 0]  # Energies
        if shift_fermi:
            energies -= self.fermi_energy

        weights = np.sum(self.data[:, :, :, orbital_index], axis=(2, 3))
        k_distances = np.arange(self.kpoints_number)

        plt.figure()
        for k_idx in range(self.kpoints_number):
            plt.scatter(
                [k_distances[k_idx]] * self.bands_number,
                energies[k_idx, :],
                s=weights[k_idx, :] * 100,  # Adjust the multiplier for visibility
                color='r'
            )

        plt.xlabel('K-point Index')
        plt.ylabel('Energy (eV)')
        plt.title(f'Orbital Projections ({orbital})')
        plt.axhline(y=0 if shift_fermi else self.fermi_energy, color='k', linestyle='--')
        plt.show()

    def plot_kpoint_path(self):
        """
        Plots the K-point path and marks special K-points.
        """
        kpoints = self.KPOINTS[:, :3]
        if self.special_kpoints is None or len(self.special_kpoints) == 0:
            print("No special K-points detected.")
            plt.plot(kpoints[:, 0], kpoints[:, 1], 'o-', label='K-points Path')
            plt.xlabel('kx')
            plt.ylabel('ky')
            plt.title('K-point Path')
            plt.legend()
            plt.show()
            return

        plt.plot(kpoints[:, 0], kpoints[:, 1], 'o-', label='K-points Path')
        plt.scatter(self.special_kpoints[:, 0], self.special_kpoints[:, 1], color='r', label='Special K-points')
        plt.xlabel('kx')
        plt.ylabel('ky')
        plt.title('K-point Path with Special Points')
        plt.legend()
        plt.show()



