import sys
import importlib
from typing import List, Tuple, Optional, Dict, Union
from tqdm import tqdm

def safe_import(module_path: str, attribute: str = None, alias: str = None) -> None:
    """
    Attempts to import a module or attribute from the given module path.
    If a relative module path is provided (starting with '.'), it uses __package__.
    If an ImportError occurs, an error message is written to stderr.

    Parameters:
      module_path: The module path to import.
      attribute: The attribute to import from the module (if None, the entire module is imported).
      alias: The name under which the imported object will be stored in globals().
    """
    try:
        if module_path.startswith('.'):
            mod = importlib.import_module(module_path, package=__package__)
        else:
            mod = importlib.import_module(module_path)
        value = getattr(mod, attribute) if attribute else mod
        globals()[alias or attribute or module_path] = value
    except ImportError as e:
        sys.stderr.write(f"An error occurred while importing {attribute or module_path}: {e}\n")

imports = [
    (".partition_builder.AbInitioThermodynamics_builder", "AbInitioThermodynamics_builder"),
    (".partition_builder.BandStructure_builder", "BandStructure_builder"),
    (".partition_builder.Blender_builder", "Blender_builder"),
    (".partition_builder.Config_builder", "Config_builder"),
    (".partition_builder.Conductivity_builder", "Conductivity_builder"),
    (".partition_builder.CrystalDefect_builder", "CrystalDefect_builder"),
    (".partition_builder.Crystal_builder", "Crystal_builder"),
    (".partition_builder.Extract_builder", "Extract_builder"),
    (".partition_builder.Filter_builder", "Filter_builder"),
    (".partition_builder.Metadata_builder", "Metadata_builder"),
    (".partition_builder.MoleculeCluster_builder", "MoleculeCluster_builder"),
    (".partition_builder.Molecule_builder", "Molecule_builder"),
    (".partition_builder.MolecularDynamic_builder", "MolecularDynamic_builder"),
    (".partition_builder.Network_builder", "Network_builder"),
    (".partition_builder.Plot_builder", "Plot_builder"),
    (".partition_builder.PositionEditor_builder", "PositionEditor_builder"),
    (".partition_builder.SurfaceStates_builder", "SurfaceStates_builder"),
    (".partition_builder.VacuumStates_builder", "VacuumStates_builder"),
    (".PartitionManager", "PartitionManager"),
    ("numpy", None, "np"),
    ("scipy.interpolate", "interp1d", "interp1d"),
    ("typing", "List", "List"),
    ("typing", "Optional", "Optional"),
    ("typing", "Dict", "Dict"),
    ("typing", "Tuple", "Tuple"),
]

from ..miscellaneous.data_mining import *
for imp in imports:
    if len(imp) == 2:
        module_path, attribute = imp
        safe_import(module_path, attribute)
    elif len(imp) == 3:
        module_path, attribute, alias = imp
        safe_import(module_path, attribute, alias)

class Partition(PartitionManager, AbInitioThermodynamics_builder, BandStructure_builder, Blender_builder, Config_builder,
                Conductivity_builder, CrystalDefect_builder, Crystal_builder, Extract_builder, Filter_builder,
                Metadata_builder, MoleculeCluster_builder, Molecule_builder, MolecularDynamic_builder,
                Network_builder, Plot_builder, PositionEditor_builder, SurfaceStates_builder, VacuumStates_builder
                ):
    """
    The Partition class is designed to handle various operations related to different types
    of crystal structure manipulations. It inherits from multiple builder classes, each
    specialized in a specific aspect of crystal structure and simulation setup.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Partition class with the provided file location and name.

        Args:
            file_location (str, optional): The path to the file or directory where the data is stored.
            name (str, optional): The name associated with this instance of the Partition class.
            kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def get_composition_data(self, verbose: bool = True) -> Dict[str, np.ndarray]:
        """
        Extract composition, energy, and area data from containers.

        This function iterates through all containers and extracts relevant information such as the composition data,
        energy values, surface area, and lattice vectors. The extracted data is stored as numpy arrays for efficient
        numerical operations.

        Parameters:
            verbose (bool): If True, prints progress messages.

        Returns:
            Dict[str, np.ndarray]: A dictionary containing:
                - composition_data: Array with composition counts for each container.
                - energy_data: Array with energy values for each container.
                - area_data: Array with surface area values for each container.
                - uniqueAtomLabels: Unique atom labels used in the containers.
                - lattice_data: Array with lattice vector information for each container.
        """
        if verbose:
            print("Extracting composition, energy, and area data from containers...")

        # Initialize arrays to store the data extracted from containers
        num_containers = len(self.containers)
        num_labels = len(self.uniqueAtomLabels)

        composition_data = np.zeros((num_containers, num_labels), dtype=np.float64)
        energy_data = np.zeros(num_containers, dtype=np.float64)
        area_data = np.zeros(num_containers, dtype=np.float64)
        lattice_data = np.zeros((num_containers, 9), dtype=np.float64)

        # Extract data for each container
        for c_i, c in enumerate(self.containers):  
            comp = np.zeros_like(self.uniqueAtomLabels, dtype=np.float64)
            for ual, ac in zip(c.AtomPositionManager.uniqueAtomLabels, c.AtomPositionManager.atomCountByType):
                comp[self.uniqueAtomLabels_order[ual]] = ac

            # Store extracted data in the corresponding arrays
            composition_data[c_i, :] = comp
            energy_data[c_i] = c.AtomPositionManager.E
            area_data[c_i] = c.AtomPositionManager.get_area('z')
            lattice_data[c_i, :] = np.ravel( c.AtomPositionManager.latticeVectors )

        # Store data in instance attributes for future use
        self.composition_data = composition_data
        self.energy_data = energy_data
        self.area_data = area_data
        self.lattice_data = lattice_data

        if verbose:
            print(f"Extracted data for {num_containers} structures.")

        # Return the extracted data as a dictionary
        return {
            'composition_data': composition_data,
            'energy_data': energy_data,
            'area_data': area_data,
            'uniqueAtomLabels': self.uniqueAtomLabels,
            'lattice_data': lattice_data,
        }

    def generate_variants(self, parameter: str, values:np.array=None, file_location: str = None) -> bool:
        """
        Generates variants of the current container set based on the specified parameter and its range of values.

        This method iterates over the existing containers and applies different modifications
        according to the specified parameter (e.g., KPOINTS, VACANCY). The result is a new set
        of containers with the applied variations.

        Args:
            parameter (str): The parameter based on which the variants are to be generated.
            values (np.array, optional): The range of values to be applied for the parameter.
            file_location (str, optional): The location where the generated data should be stored.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        containers = []
        directories = ['' for _ in self.containers]
        parameter = parameter.upper().strip()

        for container_index, container in enumerate(self.containers):

            if parameter.upper() == 'KPOINTS':
                containers += self.handleKPoints(container, values, container_index,  file_location) 
                directories[container_index] = 'KPOINTConvergence'

            elif container.InputFileManager and parameter.upper() in container.InputFileManager.parameters_data:
                containers += self.handleInputFile(container, values, parameter,  container_index, file_location)
                directories[container_index] = f'{parameter}_analysis'

            elif parameter.upper() == 'DEFECTS':
                containers += self.handleDefect(container, values, container_index, file_location)
                directories[container_index] = 'Vacancy'

            elif parameter.upper() == 'BAND_STRUCTURE':
                containers += self.handleBandStruture(container, values, container_index, file_location)
                directories[container_index] = 'band_structure'

            elif parameter.upper() == 'CHANGE_ATOM_ID':
                containers += self.handleAtomIDChange(container, values, container_index, file_location)
                directories[container_index] = 'changeID'

            elif parameter.upper() == 'SOLVENT':
                containers += self.handleCLUSTER(container, values, container_index, file_location)
                directories[container_index] = 'solvent'

        self.containers = containers
        #self.generate_master_script_for_all_containers(directories, file_location if not file_location is None else container.file_location )

    @staticmethod
    def _compute_lag_msd(pos: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute the MSD using lag time differences, returning total MSD and MSD by dimension.
        
        pos shape: (n_particles, n_time, n_dim)
        Returns:
         Dt_r: (n_time-1,)
         MSD_total: (n_time-1,) averaged total MSD over particles
         MSD_by_dim: (n_particles, n_time-1, n_dim)
        """
        n_particles, n_time, n_dim = pos.shape
        Dt_r = np.arange(1, n_time)
        MSD_by_dim = np.zeros((n_particles, len(Dt_r), n_dim))

        for i, Dt in enumerate(Dt_r):
            diffs = pos[:, Dt:, :] - pos[:, :-Dt, :]
            diffs_sq = diffs**2
            MSD_by_dim[:, i, :] = np.mean(diffs_sq, axis=1)  # mean over time

        # MSD_total is the sum over dimensions, averaged over particles
        MSD_total = np.mean(np.sum(MSD_by_dim, axis=-1), axis=0)

        return Dt_r, MSD_total, MSD_by_dim

    @staticmethod
    def _compute_initial_msd(pos: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute the MSD relative to the initial position, returning total MSD and MSD by dimension.
        
        pos shape: (n_particles, n_time, n_dim)
        """
        n_particles, n_time, n_dim = pos.shape
        Dt_r = np.arange(1, n_time)

        diffs = pos - pos[:, 0:1, :]
        diffs_sq = diffs**2

        # MSD_by_dim: promedio sobre partículas ya que en _compute_lag_msd no lo hacíamos,
        # aquí lo haremos similarmente:
        # Queremos (n_particles, n_time-1, n_dim)
        MSD_by_dim = diffs_sq[:, 1:, :]  # sacamos el primer punto (Dt=0)
        
        # MSD_total: sum sobre dim y promedio sobre partículas
        MSD_total = np.mean(np.sum(MSD_by_dim, axis=-1), axis=0)

        return Dt_r, MSD_total, MSD_by_dim

    @staticmethod
    def _compute_fft_msd(pos: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute the Mean Squared Displacement (MSD) using the Fast Fourier Transform (FFT) method,
        returning total MSD and MSD by dimension.

        Parameters:
            pos (np.ndarray): Particle positions with shape (n_particles, n_time, n_dim).

        Returns:
            Dt_r (np.ndarray): Array of lag times (of length n_time-2).
            MSD_total (np.ndarray): The averaged total MSD over all particles and summed across all dimensions.
                                   Shape (n_time-2,).
            MSD_by_dim (np.ndarray): MSD values for each particle and dimension.
                                     Shape (n_particles, n_time-2, n_dim).

        Method:
        -------
        1. Decompose the calculation by dimension. For each dimension, use FFT to compute the MSD.
        2. For each dimension, we obtain a (n_particles, n_time-2) MSD array.
        3. Stack these results across the dimension axis to form MSD_by_dim.
        4. Compute MSD_total by summing over dimensions and averaging over particles.
        
        Note:
        -----
        The logic for handling arrays (e.g., D_pad, D_flip_pad) ensures that the shapes match 
        before summation, preventing broadcasting errors. This follows the Wiener-Khinchin theorem
        for MSD calculation via FFT.
        """

        n_particles, n_time, n_dim = pos.shape
        Dt_r = np.arange(1, n_time - 1)

        MSD_dimensional_list = []
        for d in range(n_dim):
            # Extract one dimension
            pos_d = pos[:, :, d]  # (n_particles, n_time)

            # FFT-based computations
            f_pos = np.fft.fft(pos_d, n=2*n_time, axis=-1)
            S2 = np.fft.ifft(np.abs(f_pos)**2, axis=-1).real[:, :n_time]
            S2 /= (n_time - np.arange(n_time))[None, :]

            D = pos_d**2
            D = np.append(D, np.zeros((n_particles, 1)), axis=-1)  # (n_particles, n_time+1)

            # Prepare arrays for S1 calculation
            D_pad = np.insert(D[:, :-1], 0, 0, axis=-1)      # (n_particles, n_time+1)
            D_flip = np.flip(D[:, :-1], axis=-1)             # (n_particles, n_time)
            D_flip_pad = np.insert(D_flip, 0, 0, axis=-1)    # (n_particles, n_time+1)

            S1 = (2 * np.sum(D, axis=-1)[:, None] - np.cumsum(D_pad + D_flip_pad, axis=-1))
            # Reduce back to n_time columns
            S1 = S1[:, :-1] / (n_time - np.arange(n_time))[None, :]

            # MSD for this dimension
            MSD_d = S1 - 2 * S2
            MSD_d = MSD_d[:, Dt_r]  # keep only lags 1 to n_time-2
            MSD_dimensional_list.append(MSD_d)

        # Combine all dimensions
        MSD_by_dim = np.stack(MSD_dimensional_list, axis=-1)  #  (particles, frames-2, dimentions)  (n_particles, n_time-2, n_dim)
        MSD_total = np.mean(np.sum(MSD_by_dim, axis=-1), axis=0)  # (frames,) average over particles, sum over dim

        return Dt_r, MSD_total, MSD_by_dim



    def MSD(self, pos: np.ndarray, lag: bool = True, fft: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate the MSD (total and by dimension) for given particle positions.
        
        Returns:
         Dt_r (np.ndarray): time differences
         MSD_total (np.ndarray): average MSD total over particles (sum of all dimensions)
         MSD_by_dim (np.ndarray): MSD for each particle and dimension (n_particles, n_times, n_dim)
        """
        if fft:
            return self._compute_fft_msd(pos)
        elif lag:
            return self._compute_lag_msd(pos)
        else:
            return self._compute_initial_msd(pos)

    def rmse(self, y_true: np.array, y_pred: np.array) -> float:
        """
        Calculate the Root Mean Square Error (RMSE).

        Parameters
        ----------
        y_true : np.array
            The ground truth target values.
        y_pred : np.array
            The predicted values by the model.

        Returns
        -------
        float
            The RMSE metric as a float.
        """
        # Compute RMSE using the square root of the mean squared error.
        return np.sqrt(np.mean((y_true - y_pred) ** 2))

    def nrmse(self, y_true: np.array, y_pred: np.array) -> float:
        """
        Calculate the Normalized Root Mean Square Error (NRMSE).

        Parameters
        ----------
        y_true : np.array
            The ground truth target values.
        y_pred : np.array
            The predicted values by the model.

        Returns
        -------
        float
            The NRMSE metric as a float. Normalization is done using the range of y_true.
        """
        # Ensure the RMSE function is accessed correctly within the class.
        return self.rmse(y_true, y_pred) / (y_true.max() - y_true.min())

    def mae(self, y_true: np.array, y_pred: np.array) -> float:
        """
        Calculate the Mean Absolute Error (MAE).

        Parameters
        ----------
        y_true : np.array
            The ground truth target values.
        y_pred : np.array
            The predicted values by the model.

        Returns
        -------
        float
            The MAE metric as a float.
        """
        # Compute MAE as the mean of absolute differences between true and predicted values.
        return np.mean(np.abs(y_true - y_pred))

    def mape(self, y_true: np.array, y_pred: np.array) -> float:
        """
        Calculate the Mean Absolute Percentage Error (MAPE).

        Parameters
        ----------
        y_true : np.array
            The ground truth target values.
        y_pred : np.array
            The predicted values by the model.

        Returns
        -------
        float
            The MAPE metric as a float, expressed in percentage terms.
        """
        # Compute MAPE, avoiding division by zero by adding a small constant to y_true if necessary.
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def r_squared(self, y_true: np.array, y_pred: np.array) -> float:
        """
        Calculate the coefficient of determination, R^2 score.

        Parameters
        ----------
        y_true : np.array
            The ground truth target values.
        y_pred : np.array
            The predicted values by the model.

        Returns
        -------
        float
            The R^2 score as a float.
        """
        # Compute R^2 score, indicating the proportion of variance in the dependent variable predictable from the independent variable(s).
        return 1 - (np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2))

    def str_to_connectivity(self, input_string:str) -> dict:
        # Initialize variables
        elements = {}  # To store parsed elements and their indexes
        i = 0  # Index to iterate through the string
        element_id_map = {}

        # Iterate through the string to parse elements and indexes
        while i < len(input_string):
            # Detect element (considering elements can have 2 characters, e.g., 'Ni')
            if i < len(input_string) - 1 and input_string[i:i+2] in self.atomic_numbers.keys() :
                element = input_string[i:i+2]
                i += 2

            elif input_string[i:i+1] in self.atomic_numbers.keys() or input_string[i:i+1] == '*':
                element = input_string[i]
                i += 1

            # If next character is a digit, it's an index for self-connection, skip it
            if i < len(input_string) and input_string[i].isdigit():
                if not input_string[i] in element_id_map: element_id_map[input_string[i]] = len(elements)
                element_id = element_id_map[input_string[i]]
                i += 1
            
            else:
                element_id = len(elements)
            
            # Add element to list
            elements[len(elements)] = [element, element_id] 

        return elements

    def interpolate_with_splines(self, data:np.array, M:int, degree='cubic'):
        """
        Interpolates using splines or polynomials between each pair of subsequent images.
        
        Parameters:
        - data: A NumPy array of shape (N, 3, I).
        - M: Number of points to interpolate between each pair of images.
        - degree: Type of spline or polynomial for interpolation ('linear', 'cubic', 'quadratic', etc.).
        
        Returns:
        - A new array with interpolations.
        """
        N, _, I = data.shape
        # Original "x" positions (indices of the images)
        x_orig = np.arange(I)
        # New "x" positions where we want to interpolate
        x_new = np.linspace(0, I - 1, I + (I - 1) * M)
        
        # Prepare the new array
        new_array = np.empty((N, 3, len(x_new)))
        
        # Iterate over each atom and each spatial dimension
        for n in range(N):
            for dim in range(3):
                # Create an interpolation function for each atom and dimension
                f_interp = interp1d(x_orig, data[n, dim, :], kind=degree)
                # Compute interpolated values and assign them to the new array
                new_array[n, dim, :] = f_interp(x_new)
        
        return new_array

    def get_SOAP(self, r_cut: float, n_max: int, l_max: int, sigma: float, save: bool, cache: bool, verbose: bool = False):
        """
        Compute or load SOAP descriptors for all structures contained within self.containers.

        This function first extracts atom labels, positions, and lattice vectors from each
        container (structure). It then initializes a SOAP_analysis object with the given parameters
        and either loads cached SOAP descriptors (if available and enabled) or computes them. If
        'save' is enabled, newly calculated descriptors are saved to the output directory.

        Parameters
        ----------
        r_cut : float
            Cutoff radius for the SOAP calculation.
        n_max : int
            Maximum number of radial basis functions.
        l_max : int
            Maximum degree of spherical harmonics.
        sigma : float
            Gaussian width for the SOAP descriptors.
        save : bool
            Flag indicating whether to save the computed SOAP descriptors.
        cache : bool
            Flag indicating whether to use cached SOAP data if available.
        verbose : bool, optional
            Verbose flag for additional output; default is False.

        Returns
        -------
        tuple
            A tuple containing:
                - descriptors_by_species: A dictionary mapping species to their SOAP descriptor arrays.
                - atom_info_by_species: A dictionary containing additional atom-related information per species.
        """
            # Attempt to import the SOAP_analysis class from the SOAP_tools module.
        try:
            from ..miscellaneous.SOAP_tools import SOAP_analysis
        except ImportError as e:
            sys.stderr.write(f"An error occurred while importing SOAP_tools: {e}\n")
            raise

        # Extract atomic labels, positions, and lattice vectors from each container.
        symbols = [container.AtomPositionManager.atomLabelsList for container in self.containers]
        positions = [container.AtomPositionManager.atomPositions for container in self.containers]
        cell = [container.AtomPositionManager.latticeVectors for container in self.containers]

        if verbose:
            print(f"Computing SOAP descriptors with r_cut={r_cut}, n_max={n_max}, l_max={l_max}, sigma={sigma}.")

        # Initialize the SOAP_analysis instance using the unique atomic labels.
        soap = SOAP_analysis(
            uniqueAtomLabels=self.uniqueAtomLabels,
            r_cut=r_cut,
            n_max=n_max,
            l_max=l_max,
            sigma=sigma,
        )

        # If caching is enabled, attempt to load existing SOAP data.
        if cache:
            soap_data = soap.verify_and_load_soap()
            if soap_data:
                descriptors_by_species, atom_info_by_species = soap_data
                if verbose:
                    print("Loaded existing SOAP data from cache.")
            else:
                if verbose:
                    print("Cache enabled but SOAP files are missing; recalculating SOAP descriptors.")
                try:
                    descriptors_by_species, atom_info_by_species = soap.calculate_soap_descriptors(
                        symbols=symbols,
                        positions=positions,
                        cell=cell,
                    )
                except Exception as e:
                    sys.stderr.write(f"Error calculating SOAP descriptors: {e}\n")
                    raise
                if save:
                    try:
                        soap.save_descriptors(
                            descriptors_by_species=descriptors_by_species,
                            atom_info_by_species=atom_info_by_species,
                            output_dir='SOAPs'
                        )
                    except Exception as e:
                        sys.stderr.write(f"Error saving SOAP descriptors: {e}\n")
        else:
            if verbose:
                print("Cache disabled. Calculating SOAP descriptors from scratch.")
            try:
                descriptors_by_species, atom_info_by_species = soap.calculate_soap_descriptors(
                    symbols=symbols,
                    positions=positions,
                    cell=cell,
                )
            except Exception as e:
                sys.stderr.write(f"Error calculating SOAP descriptors: {e}\n")
                raise
            if save:
                try:
                    soap.save_descriptors(
                        descriptors_by_species=descriptors_by_species,
                        atom_info_by_species=atom_info_by_species,
                        output_dir='SOAPs'
                    )
                except Exception as e:
                    sys.stderr.write(f"Error saving SOAP descriptors: {e}\n")

        if verbose:
            print("SOAP descriptor calculation completed successfully.")

        return descriptors_by_species, atom_info_by_species

    def get_positions(self, fractional: bool = False, wrap: bool = False):
        """
        Retrieve atomic positions from all containers.

        Depending on the flags, returns either Cartesian or fractional coordinates.
        Optionally, periodic boundary conditions can be enforced.

        Parameters
        ----------
        fractional : bool, optional
            Return positions in fractional coordinates relative to the unit cell if True.
        wrap : bool, optional
            Apply periodic boundary conditions if True.

        Returns
        -------
        np.ndarray
            Array of atomic positions.
        """
        if wrap:
            for container in self.containers:
                container.AtomPositionManager.wrap()

        if fractional:
            return np.array([
                container.AtomPositionManager.atomPositions_fractional
                for container in self.containers
            ], dtype=np.float64)
        else:
            return np.array([
                container.AtomPositionManager.atomPositions
                for container in self.containers
            ], dtype=np.float64)

    def get_msd_data(self, chemical_ID: List[str] = None) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Extract the atom positions and labels from the loaded simulation containers.
        Also returns the simulation cell volume.

        Parameters
        ----------
        chemical_ID : list of str, optional
            If provided, can be used to filter atoms by their chemical labels.

        Returns
        -------
        atoms_positions : np.ndarray
            Atomic positions with shape (n_atoms, n_steps, 3).
        atom_labels : np.ndarray
            Atomic labels corresponding to each atom.
        volume : float
            The simulation cell volume.

        Notes
        -----
        The raw data is reorganized so that the resulting array has
        dimensions (n_atoms, n_steps, 3).
        """

        volume = self.containers[0].AtomPositionManager.get_volume()
        atom_labels = self.containers[0].AtomPositionManager.get_atomic_labels()

        num_steps = len(self.containers)
        num_atoms = self.containers[0].AtomPositionManager.atomPositions.shape[0]
        atoms_positions = np.zeros((num_steps, num_atoms, 3))

        for c_i in tqdm(range(num_steps), desc="Extracting MSD Data", unit="step"):
            atoms_positions[c_i, :, :] = self.containers[c_i].AtomPositionManager.atomPositions

        # Rearranging into (n_atoms, n_steps, 3)
        atoms_positions = np.transpose(atoms_positions, (1, 0, 2))

        return atoms_positions, atom_labels, volume

    def generate_atom_labels_and_cluster_counts(
        self,
        atom_clusters: Dict[str, Union[List[int], np.ndarray]],
        atom_structures: Dict[str, Union[List[Union[List[int], np.ndarray]], np.ndarray]]
    ) -> Tuple[List[np.ndarray], List[np.ndarray], np.ndarray, List[str]]:
        """
        Generate atom labels for each structure, count clusters across structures, and create class labels.

        Args:
            atom_clusters: Dictionary mapping element symbols to cluster labels for each atom.
            atom_structures: Dictionary mapping element symbols to structure and atom IDs.

        Returns:
            A tuple containing:
            - List of numpy arrays with cluster labels for atoms in each structure.
            - 2D numpy array of cluster counts for each structure.
            - List of class labels in the format "Element_ClusterNumber".
        """
        # Get the number of structures
        num_structures = len(self.containers)

        # Initialize variables for cluster mapping and class labels
        total_clusters = 0
        cluster_mapping = {}
        class_labels = []

        # Process each unique element
        for element in self.uniqueAtomLabels:
            clusters = atom_clusters[element]
            unique_clusters = sorted(set(clusters))
            
            # Create mapping for cluster indices and generate class labels
            cluster_mapping[element] = {c: i + total_clusters for i, c in enumerate(unique_clusters)}
            class_labels.extend([f"{element}_{c}" for c in unique_clusters])
            total_clusters += len(unique_clusters)

        # Initialize output structures
        structure_labels = [np.zeros(c.AtomPositionManager.atomCount, dtype=np.int64) for c in self.containers]
        cluster_counts = np.zeros((num_structures, total_clusters), dtype=int)

        # Process atom clusters for each element
        for element, clusters in atom_clusters.items():
            structures = atom_structures[element]
            element_mapping = cluster_mapping[element]

            # Extract structure IDs and atom IDs
            struct_ids, atom_ids = structures if isinstance(structures, list) else structures.T

            # Assign cluster labels and count clusters
            for struct_id, atom_id, cluster in zip(struct_ids, atom_ids, clusters):
                mapped_cluster = element_mapping[int(cluster)]
                structure_labels[int(struct_id)][int(atom_id)] = mapped_cluster
                cluster_counts[int(struct_id), mapped_cluster] += 1

        return structure_labels, cluster_counts, class_labels

    def compute_structure_cluster_counts(
        self,
        # SOAP hyperparameters
        r_cut: float = 5.0,
        n_max: int = 5,
        l_max: int = 5,
        sigma: float = 0.1,
        cache: bool = False,
        # compression hyperparameters
        compress_model: str = "pca",
        n_components: int = 15,
        # clustering hyperparameters
        cluster_model: str = "minibatch-kmeans",
        max_clusters: int = 15,
        eps: float = 0.7,
        min_samples: int = 2,
        save: bool = False,
        sub_sample: int = None,
        store_data_in_object: bool =None, 
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Compute cluster counts per structure by running SOAP → compression → clustering.

        Parameters
        ----------
        r_cut : float, default 4.0
            SOAP cutoff radius (Å).
        n_max : int, default 12
            Maximum radial basis functions for SOAP.
        l_max : int, default 12
            Maximum angular momentum channels for SOAP.
        sigma : float, default 0.01
            Gaussian width for SOAP.
        cache : bool, default True
            If True, load/save intermediate SOAP descriptors and compressed data.
        compress_model : str, default "umap"
            Dimensionality-reduction method identifier (e.g. "umap", "pca").
        n_components : int, default 10
            Number of output components for compression.
        cluster_model : str, default "dbscan"
            Clustering algorithm identifier (currently supports "dbscan").
        eps : float, default 0.7
            DBSCAN epsilon neighborhood radius.
        min_samples : int, default 2
            DBSCAN minimum samples per cluster.

        Returns
        -------
        cluster_counts : np.ndarray, shape (n_structures, n_total_clusters)
            Each row i contains the count of atoms assigned to each cluster
            (across all species) in structure i.
        class_labels : List[str]
            Labels of length n_total_clusters, each of the form
            "<species>:<cluster_id>", corresponding to the columns of `cluster_counts`.
        """
        import time

        # 1) Compute or load SOAP descriptors by species
        descriptors_by_species, atom_info_by_species = self.get_SOAP(
            r_cut=r_cut,
            n_max=n_max,
            l_max=l_max,
            sigma=sigma,
            save=save,
            cache=cache
        )
 
        # 2) Compress descriptors
        compressor = Compress(unique_labels=self.uniqueAtomLabels)
        compressed_by_species = compressor.verify_and_load_or_compress(
            descriptors_by_species,
            method=compress_model,
            n_components={spec: min(n_components, spect_data.shape[1] ) for spec, spect_data in descriptors_by_species.items() },
            load=cache,
            save=save,
            sub_sample=sub_sample,
        )

        # 3) Cluster each species’ compressed vectors
        cluster_labels_by_species: Dict[str, np.ndarray] = {}
        for species, data in compressed_by_species.items():
            analyzer = ClusteringAnalysis()
            results = analyzer.cluster_analysis(
                data=data,
                params={"eps": eps, "min_samples": min_samples, },
                methods=[cluster_model],
                output_dir=f'./cluster_results/{species}',
                use_cache=cache,
                max_clusters=int(max_clusters),
                save=save,
                sub_sample=sub_sample,
            )
            cluster_labels_by_species[species] = results[cluster_model]

        #start = time.time()
        # 4) Build per-structure cluster counts
        #    atom_info_by_species maps species → array of shape (n_atoms, 2):
        #       each row is [structure_index, atom_index]
        structure_labels, cluster_counts, class_labels = self.generate_atom_labels_and_cluster_counts(
            atom_clusters=cluster_labels_by_species,
            atom_structures={key:np.array(atom_info_by_species[key]) for key, item in atom_info_by_species.items()},
        )
        #print(f"Elapsed: {time.time() - start:.6f} s")

        if store_data_in_object:
            for specie, cluster_data in cluster_labels_by_species.items():
                for cluster_idx, (structure_idx, atom_idx) in enumerate(np.array(atom_info_by_species[specie])):
                    if type(self.containers[ structure_idx ].AtomPositionManager.class_ID) == type(None):
                        self.containers[ structure_idx ].AtomPositionManager.class_ID = np.zeros(self.containers[ structure_idx ].AtomPositionManager.atomCount, dtype=np.int64)
                    self.containers[ structure_idx ].AtomPositionManager.class_ID[atom_idx] = int(cluster_data[cluster_idx])

        return structure_labels, cluster_counts, class_labels






