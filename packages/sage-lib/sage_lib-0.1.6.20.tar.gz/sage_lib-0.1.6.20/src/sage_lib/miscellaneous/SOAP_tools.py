_lazy_imports = {
    # Example: you might keep these for lazy loading if you still want them
    "SOAP": ("dscribe.descriptors", "SOAP"),
    "np": ("numpy", None),
    "tqdm": ("tqdm", None),
    "os": ("os", None),
    "Dict": ("typing", "Dict"),
    "List": ("typing", "List"),
    "Tuple": ("typing", "Tuple"),
    "Union": ("typing", "Union"),
    "defaultdict": ("collections", "defaultdict"),
    "Atoms": ("ase", "Atoms"),
    "Cell": ("ase.cell", "Cell"),
}

def __getattr__(name):
    """
    Lazily import the module/attribute only upon first usage.
    This helps reduce initial import times or avoid heavy dependencies
    that may not be needed every time the module is loaded.
    """
    import importlib
    import sys

    if name in _lazy_imports:
        module_path, attribute = _lazy_imports[name]
        try:
            mod = importlib.import_module(module_path)
            value = getattr(mod, attribute) if attribute is not None else mod
            globals()[name] = value  # Cache the imported value for subsequent calls
            return value
        except ImportError as e:
            sys.stderr.write(f"An error occurred while lazily importing {name}: {e}\n")
            raise
    raise AttributeError(f"module {__name__} has no attribute {name}")

class SOAP_analysis:
    """
    Class that calculates and stores SOAP (Smooth Overlap of Atomic Positions)
    descriptors for given atomic structures, allowing subsequent saving and
    loading of those descriptors.
    """

    def __init__(
        self,
        uniqueAtomLabels: list = None,
        symbols: list = None,
        positions: list = None,
        cell: list = None,
        r_cut: float = None,
        n_max: float = None,
        l_max: float = None,
        sigma: float = None,
        verbose: bool = None
    ):
        """
        Initialize the SOAP_analysis object with basic parameters and references to atomic data.

        Args:
            uniqueAtomLabels (list): Unique atom species or elements, e.g. ['H', 'O'].
            symbols (list): List of arrays (one per structure), each containing symbols for each atom.
            positions (list): List of arrays (one per structure), each containing (x, y, z) positions for each atom.
            cell (list): List of arrays (one per structure), each describing the simulation cell.
            r_cut (float): Cutoff radius for the SOAP descriptor.
            n_max (float): Maximum number of radial basis functions.
            l_max (float): Maximum degree of spherical harmonics.
            sigma (float): Standard deviation for the Gaussian smearing.
            verbose (bool): Optional flag for verbosity.
        """
        self.r_cut = r_cut
        self.n_max = n_max
        self.l_max = l_max
        self.sigma = sigma

        self.symbols = symbols
        self.positions = positions
        self.cell = cell
        self.uniqueAtomLabels = uniqueAtomLabels

        self.descriptors_by_species = None
        self.atom_info_by_species = None

    def calculate_soap_descriptors(
        self,
        symbols=None,
        positions=None,
        cell=None,
        r_cut: float = None,
        n_max: int = None,
        l_max: int = None,
        sigma: float = None
    ):
        """
        Calculate SOAP descriptors for the provided atomic structures.

        If symbols, positions, or cell are not provided, the values from this object's
        attributes will be used. This method returns dictionaries that map each
        atomic species to its corresponding SOAP descriptors and atom indices.

        Args:
            symbols (list, optional): If provided, overrides self.symbols.
            positions (list, optional): If provided, overrides self.positions.
            cell (list, optional): If provided, overrides self.cell.
            r_cut (float, optional): Cutoff radius for atomic interactions. Defaults to self.r_cut.
            n_max (int, optional): Maximum number of radial basis functions. Defaults to self.n_max.
            l_max (int, optional): Maximum degree of spherical harmonics. Defaults to self.l_max.
            sigma (float, optional): Standard deviation for the Gaussian smearing function. Defaults to self.sigma.

        Returns:
            tuple:
                - descriptors_by_species (dict): SOAP descriptors for each atomic species.
                - atom_info_by_species (dict): Information (structure_index, atom_index) for each descriptor.

        Note:
            This method expects that all input arrays (symbols, positions, cell) have consistent dimensions.
        """
        # We import inside the function so only code that calls this method brings the dependency in.
        from dscribe.descriptors import SOAP
        from collections import defaultdict
        import numpy as np
        from ase import Atoms
        from ase.cell import Cell
        from tqdm import tqdm
        
        # Use instance-level defaults if specific arguments are None
        r_cut = self.r_cut if r_cut is None else r_cut
        n_max = self.n_max if n_max is None else n_max
        l_max = self.l_max if l_max is None else l_max
        sigma = self.sigma if sigma is None else sigma

        symbols = self.symbols if symbols is None else symbols
        positions = self.positions if positions is None else positions
        cell = self.cell if cell is None else cell

        # Initialize the SOAP descriptor
        soap = SOAP(
            species=self.uniqueAtomLabels,
            periodic=True,
            r_cut=r_cut,
            n_max=n_max,
            l_max=l_max,
            sigma=sigma,
            sparse=False
        )

        # Dictionaries to store the results
        descriptors_by_species = defaultdict(list)
        atom_info_by_species = defaultdict(list)

        # Loop over all structures
        for idx, (s, p, c) in enumerate(tqdm(zip(symbols, positions, cell), total=len(symbols), desc="Computing SOAP descriptors")):
            # Create ASE Atoms object
            atoms = Atoms(symbols=s, positions=p, cell=Cell(c), pbc=True)

            # Calculate SOAP descriptors
            descriptors = soap.create(atoms)

            # Separate results by species
            for atom_idx, (specie, descriptor) in enumerate(zip(s, descriptors)):
                descriptors_by_species[specie].append(descriptor)
                atom_info_by_species[specie].append((idx, atom_idx))

        # Convert lists to numpy arrays
        for spc in descriptors_by_species:
            descriptors_by_species[spc] = np.array(descriptors_by_species[spc])

        self.descriptors_by_species = descriptors_by_species
        self.atom_info_by_species = atom_info_by_species

        return descriptors_by_species, atom_info_by_species

    def save_descriptors(
        self,
        descriptors_by_species=None,
        atom_info_by_species=None,
        output_dir: str = "./"
    ):
        """
        Save SOAP descriptors and atom information to disk.

        For each species, this will write one .npy file (containing the descriptors)
        and one .txt file (containing lines of "descriptor_index,structure_index,atom_index").

        Args:
            descriptors_by_species (dict, optional): Maps species -> (N, descriptor_dim) array.
                Defaults to the values in self.descriptors_by_species if None.
            atom_info_by_species (dict, optional): Maps species -> list of (structure_index, atom_index).
                Defaults to the values in self.atom_info_by_species if None.
            output_dir (str): Directory in which to write the .npy and .txt files.

        Returns:
            None
        """
        import os
        import numpy as np

        # Use internal references if caller did not provide updated dictionaries
        descriptors_by_species = (
            descriptors_by_species if descriptors_by_species is not None else self.descriptors_by_species
        )
        atom_info_by_species = (
            atom_info_by_species if atom_info_by_species is not None else self.atom_info_by_species
        )

        # Ensure directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save each species
        for species, descriptors in descriptors_by_species.items():
            # Save descriptors as .npy
            desc_filename = os.path.join(output_dir, f"descriptors_{species}.npy")
            np.save(desc_filename, descriptors)
            print(f"Descriptors for species '{species}' saved to: {desc_filename}")

            # Save atom info as .txt
            info_filename = os.path.join(output_dir, f"atom_info_{species}.txt")
            with open(info_filename, "w") as f:
                f.write("descriptor_index,structure_index,atom_index\n")
                for desc_idx, (struct_idx, atom_idx) in enumerate(atom_info_by_species[species]):
                    f.write(f"{desc_idx},{struct_idx},{atom_idx}\n")
            print(f"Atom info for species '{species}' saved to: {info_filename}")

    def verify_and_load_soap(
        self,
        uniqueAtomLabels: list = None,
        output_dir: str = "SOAPs"
    ):
        """
        Check if SOAP files exist for each species and load them if they do.

        This method looks for files named:
            descriptors_{species}.npy
            atom_info_{species}.txt
        inside 'output_dir'. If any file is missing, the method returns False.
        Otherwise, it returns (descriptors_by_species, atom_info_by_species) and
        also sets them on self.

        Args:
            uniqueAtomLabels (list, optional): Species to look for. Defaults to self.uniqueAtomLabels.
            output_dir (str): Directory where the descriptors and info files are stored.

        Returns:
            bool or tuple:
                - False if any required file is missing.
                - (descriptors_by_species, atom_info_by_species) if all files were found and successfully loaded.
        """
        import os
        import numpy as np
        from collections import defaultdict
        from tqdm import tqdm

        # Use the object's own species if none are provided
        if uniqueAtomLabels is None:
            uniqueAtomLabels = self.uniqueAtomLabels

        descriptors_by_species = {}
        atom_info_by_species = {}

        # Iterate over each species we expect
        for species in tqdm(uniqueAtomLabels, desc="Verifying and loading SOAP data"):
            desc_filename = os.path.join(output_dir, f"descriptors_{species}.npy")
            info_filename = os.path.join(output_dir, f"atom_info_{species}.txt")

            # If either file is missing, abort
            if not (os.path.exists(desc_filename) and os.path.exists(info_filename)):
                print(f"Missing SOAP descriptor or info file(s) for species '{species}'.")
                return False

            # Load descriptors
            descriptors_by_species[species] = np.load(desc_filename)

            # Load atom info
            atom_info_list = []
            with open(info_filename, "r") as file_obj:
                next(file_obj)  # Skip header line
                for line in file_obj:
                    # Format: "descriptor_index,structure_index,atom_index"
                    # We only need struct_idx and atom_idx from columns 1,2
                    # although we read descriptor_index to maintain consistency
                    tokens = line.strip().split(",")
                    # tokens[0] = descriptor_index (not used in final data)
                    struct_idx = int(tokens[1])
                    atom_idx = int(tokens[2])
                    atom_info_list.append((struct_idx, atom_idx))
            atom_info_by_species[species] = atom_info_list

        # Store internally
        self.descriptors_by_species = descriptors_by_species
        self.atom_info_by_species = atom_info_by_species

        print("All SOAP files found and loaded successfully.")
        return descriptors_by_species, atom_info_by_species
