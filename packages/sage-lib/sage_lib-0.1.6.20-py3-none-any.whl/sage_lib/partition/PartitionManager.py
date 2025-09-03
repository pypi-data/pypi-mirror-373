try:
    from ..master.FileManager import *   
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    from ..master.AtomicProperties import AtomicProperties
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomicProperties: {str(e)}\n")
    del sys

try:
    from ..single_run.SingleRun import SingleRun
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing SingleRun: {str(e)}\n")
    del sys

try:
    from ..IO.OutFileManager import OutFileManager
    from ..IO.storage_backend import MemoryStorage, SQLiteStorage

except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing OutFileManager: {str(e)}\n")
    del sys

try:
    from ..IO.structure_handling_tools.AtomPosition import AtomPosition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys

try:
    import os, sys
    import traceback
    import re
    import numpy as np
    from typing import List, Optional, Union
    import copy
    import logging
    from tqdm import tqdm
    import mmap

except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing traceback: {str(e)}\n")
    del sys

try:
    from ase.io import Trajectory
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing ase.io.Trajectory: {str(e)}\n")
    del sys

class PartitionManager(FileManager, AtomicProperties): 
    """
    PartitionManager class for managing and partitioning simulation data.

    Inherits:
    - FileManager: For file management functionalities.

    Attributes:
    - file_location (str): File path for data files.
    - containers (list): Containers to hold various data structures.
    """
    def __init__(
        self,
        path : str = None,
        storage: str = 'memory',
        db_path: Optional[str] = 'data.db',
        *args,
        **kwargs
    ):
        """
        Initializes the PartitionManager object.

        Args:
        - file_location (str, optional): File path location.
        - name (str, optional): Name of the partition.
        - **kwargs: Additional arguments.
        """
        
        self._containers = []
        self._time = []
        self._N = None
        self._size = None

        self._uniqueAtomLabels = None
        self._uniqueAtomLabels_order = None

        super().__init__(path, *args, **kwargs)

        if storage == 'memory':
            self._store = MemoryStorage()
        elif storage == 'sqlite':
            if not db_path:
                raise ValueError("db_path must be provided for sqlite storage")
            self._store = SQLiteStorage(db_path)
        else:
            raise ValueError(f"Unknown storage backend: {storage}")

    def __iter__(self):
        return iter(self.containers)

    def __len__(self):
        return self.N

    def __getitem__(self, index: int):
        return self.get_container(index)

    def __iadd__(self, other: object) -> 'PartitionManager':
        """
        In‑place absorb all containers from other into self, then return self.
        """
        if not isinstance(other, PartitionManager):
            return NotImplemented
        for run in other.containers:
            self.add_container(copy.deepcopy(run))
        return self
        
    @property
    def containers(self) -> List[SingleRun]:
        """
        Legacy-style property returning the list of container objects.
        """
        return self.list_containers()

    @property
    def N(self) -> int:
        """
        Return the number of containers managed by the PartitionManager.
        
        Returns:
        int: Number of containers. Returns 0 if containers are not initialized or of unsupported type.
        """
        return self._store.count()

    @property
    def size(self) -> int:
        """
        Return the number of containers managed by the PartitionManager.
        
        Returns:
        int: Number of containers. Returns 0 if containers are not initialized or of unsupported type.
        """
        return self.N

    @property
    def uniqueAtomLabels(self) -> List[str]:
        """
        Get unique atom labels from all containers.
        
        Returns:
        list: A list of unique atom labels.
        
        Raises:
        AttributeError: If containers are not initialized.
        """
        if self._uniqueAtomLabels is None:
            uniqueAtomLabels = set()
            for c in self.containers:
                assert hasattr(c, 'AtomPositionManager'), "Container must have an AtomPositionManager attribute."
                uniqueAtomLabels.update(c.AtomPositionManager.uniqueAtomLabels)
            self._uniqueAtomLabels = list(uniqueAtomLabels)

        return self._uniqueAtomLabels

    @property
    def uniqueAtomLabels_order(self) -> dict:
        """
        Get a dictionary mapping unique atom labels to their indices.
        
        Returns:
        dict: A dictionary with unique atom labels as keys and their order as values.
        
        Raises:
        AttributeError: If containers are not initialized.
        """
        if self._uniqueAtomLabels_order is None:
            labels = self.uniqueAtomLabels
            self._uniqueAtomLabels_order = {n: i for i, n in enumerate(labels)}
        return self._uniqueAtomLabels_order

    def add_container(self, container: Union[SingleRun, List[SingleRun]]) -> Union[int, List[int]]:
        """
        Add one or multiple SingleRun containers.
        Returns a single storage ID (int) or a list of IDs.
        """
        self._uniqueAtomLabels = None
        self._uniqueAtomLabels_order = None

        if isinstance(container, list):
            ids: List[int] = []
            for obj in container:
                ids.append(self._store.add(obj))
            return ids
        return self._store.add(container)

    add = add_container
        
    def add_empty_container(self, ):
        """
        Add a new container to the list of containers.

        Parameters:
            container (object): The container object to be added.
        """
        self.add_container( SingleRun() )
        return self.containers[-1]

    def get_container(self, container_id: int) -> SingleRun:
        """Retrieve a container by its storage ID."""
        return self._store.get(container_id)

    def set_container(self, containers_list: list) -> bool:
        """Retrieve a container by its storage ID."""
        return self._store.set(containers_list)

    def remove_container(self, container: Union[int, SingleRun]) -> None:
        """
        Remove a container either by ID (int) or by object reference.

        Parameters:
            container: storage ID or SingleRun object to remove.
        """
        # reset caches
        self._uniqueAtomLabels = None
        self._uniqueAtomLabels_order = None

        # remove by ID
        if isinstance(container, int):
            self._store.remove(container)
            return
        # remove by object: find matching ID
        for cid in self._store.list_ids():
            obj = self._store.get(cid)
            if obj is container or obj == container:
                self._store.remove(cid)
                return
        raise KeyError("Container not found for removal")

    def empty_container(self):
        """
        Empty the list of containers.
        """
        self.containers = []
        self._N = None
        self._size = None
        self._uniqueAtomLabels = None
        self._uniqueAtomLabels_order = None

    def list_containers(self) -> List[SingleRun]:
        """Return all containers as a list of SingleRun objects."""
        return self._store.get()

    def apply_filter_mask(self, mask:list) -> bool:
        """
        Filters containers based on a boolean mask.

        Parameters
        ----------
        mask : list
            A list of 0/1 values indicating which containers to keep. 
            Must have the same length as `self.containers`.

        Returns
        -------
        bool
            True if filtering is successfully applied.

        Example
        -------
        If `self.containers = [A, B, C]` and `mask = [1, 0, 1]`, 
        the result will be `self._containers = [A, C]`.
        """
        self.filter_containers(mask) 

    def filter_containers(self, mask: List[int]) -> None:
        """
        Filters containers based on a boolean mask.

        Parameters
        ----------
        mask : list
            A list of 0/1 values indicating which containers to keep. 
            Must have the same length as `self.containers`.

        Returns
        -------
        bool
            True if filtering is successfully applied.

        Example
        -------
        If `self.containers = [A, B, C]` and `mask = [1, 0, 1]`, 
        the result will be `self._containers = [A, C]`.
        """
        all_ids = set(self._store.list_ids())
        for cid in sorted(all_ids - set(mask), reverse=True):
            self._store.remove(cid)

    def apply_sorting_order(self, order: List[int]) -> bool:
        """
        Reorder containers according to provided index order (legacy behavior).

        Parameters:
            order: new ordering list of indices into current containers list.
        """
        # reset caches
        self._uniqueAtomLabels = None
        self._uniqueAtomLabels_order = None

        current = self.list_containers()
        # validate
        if sorted(order) != list(range(len(current))):
            raise ValueError("Invalid sorting order list")
        # get objects in new order
        new_list = [current[i] for i in order]
        # clear and re-add
        for cid in self._store.list_ids()[::-1]:
            self._store.remove(cid)
        for obj in new_list:
            self._store.add(obj)
        return True

    def _update_container(self, container: SingleRun, container_setter: object) -> None:
        """
        Updates a given container with simulation parameters extracted from the simulation reader.

        Parameters:
        - container: The container to be updated with simulation settings.
        - container_setter: The simulation reader instance containing the extracted settings.

        Returns:
        None
        """
        container.InputFileManager = container_setter.InputFileManager
        container.KPointsManager = container_setter.KPointsManager
        container.PotentialManager = container_setter.PotentialManager
        container.BashScriptManager = container_setter.BashScriptManager
        container.vdw_kernel_Handler = container_setter.vdw_kernel_Handler
        container.WaveFileManager = container_setter.WaveFileManager
        container.ChargeFileManager = container_setter.ChargeFileManager

    @error_handler
    def read_config_setup(self, file_location: str = None, source: str = 'VASP', verbose: bool = False):
        """
        Reads simulation configuration from a specified file location and updates containers with the read settings.

        This method supports reading configurations specifically tailored for VASP simulations. It extracts simulation
        parameters such as input file management, k-points, potentials, and more, and applies these configurations
        across all containers managed by this instance.

        Parameters:
        - file_location (str, optional): The path to the directory containing the simulation files. Defaults to None,
                                         in which case the instance's file_location attribute is used.
        - source (str, optional): The source/format of the simulation files. Currently, only 'VASP' is supported.
                                  Defaults to 'VASP'.
        - verbose (bool, optional): If True, prints detailed messages during the process. Defaults to False.

        Returns:
        None
        """

        # Use instance's file_location if none provided or invalid
        file_location = file_location if isinstance(file_location, str) else self.file_location

        # Initialize simulation reader based on the source format
        if source.upper() == 'VASP':
            container_setter = self.read_vasp_folder(file_location=file_location, add_container=False, verbose=verbose)
            if container_setter.AtomPositionManager is not None:
                container_setter.InputFileManager.set_LDAU(container_setter.AtomPositionManager.uniqueAtomLabels)

        # Update all containers with the read configuration
        for container in self.containers:
            self._update_container(container, container_setter)

    @staticmethod
    def _identify_file_type(file_name: str) -> str:
        """
        Identifies the type of file based on common atomic input file identifiers.

        The function is case-insensitive and recognizes a variety of file types commonly
        used in computational chemistry and physics. If the file type is not recognized,
        it returns 'Unknown File Type'.

        Parameters:
        - file_name (str): The name of the file to identify.

        Returns:
        - str: The identified file type or 'Unknown File Type' if not recognized.

        Example:
        >>> identify_file_type('sample-OUTCAR.txt')
        'OUTCAR'
        """

        # Mapping of file identifiers to their respective types, case-insensitive
        file_types = {
            'poscar': 'POSCAR', 'contcar': 'POSCAR',
            'outcar': 'OUTCAR',
            'xyz': 'xyz',
            'traj': 'traj',
            'config': 'xyz',
            'gen': 'gen',
            'pdb': 'pdb',
            'cif': 'CIF',
            'vasp': 'VASP',
            'chgcar': 'CHGCAR',
            'doscar': 'DOSCAR',
            'xdatcar': 'XDATCAR',
            'incar': 'INCAR',
            'procar': 'PROCAR',
            'wavecar': 'WAVECAR',
            'kpoints': 'KPOINTS',
            'eigenval': 'EIGENVAL',
            'metadata': 'METADATA',
        }

        # Convert the file name to lowercase for case-insensitive comparison
        file_name_lower = file_name.lower()

        # Identify the file type based on the presence of identifiers in the file name
        for identifier, file_type in file_types.items():
            if identifier in file_name_lower:
                return file_type

        # Return a default value if no known identifier is found
        return 'Unknown File Type'

    @error_handler
    def read_files(self, file_location: str = None, source: str = None, subfolders: bool = False,
                   energy_tag: str = None, forces_tag: str = None, container_index:int =None,
                   verbose: bool = False):
        """
        Reads simulation files from the specified location, handling both individual files and subfolders
        containing simulation data. It supports multiple file formats and structures, adapting the reading
        process according to the source parameter.

        Parameters:
        - file_location (str, optional): The path to the directory or file containing simulation data.
                                         Defaults to None, which uses the instance's file_location attribute.
        - source (str, optional): The format/source of the simulation files (e.g., 'VASP', 'TRAJ', 'XYZ', 'OUTCAR').
                                  Defaults to None.
        - subfolders (bool, optional): If True, reads files from subfolders under the specified location.
                                       Defaults to False.
        - energy_tag (str, optional): Specific tag used to identify energy data within the files, applicable for
                                      formats like 'XYZ'. Defaults to None.
        - forces_tag (str, optional): Specific tag used to identify forces data within the files, applicable for
                                      formats like 'XYZ'. Defaults to None.
        - verbose (bool, optional): If True, enables verbose output during the file reading process. Defaults to False.

        Raises:
        - ValueError: If the source format is not recognized or supported.

        Returns:
        None
        """
        source = self._identify_file_type(file_location) if source is None else source

        if subfolders:
            self.readSubFolder(file_location=file_location, source=source, container_index=container_index, verbose=verbose)
            return

        # Define a strategy for each source format to simplify the conditional structure
        source_strategy = {
            'VASP': self.read_vasp_folder,
            'DFTB': self.read_dftb_folder,
            'TRAJ': self.read_traj,
            'XYZ': self.read_XYZ,
            'OUTCAR': self.read_OUTCAR,
            'DUMP': self.read_dump,
            'METADATA': self.read_METADATA,
        }

        # Attempt to read using a specific strategy for the source format
        if source.upper() in source_strategy:
            source_strategy[source.upper()](
                file_location=file_location, 
                add_container=True,
                verbose=verbose, 
                energy_tag=energy_tag, 
                forces_tag=forces_tag,
                container_index=container_index, 
            )
        else:
            # Fallback for other sources
            self.read_structure(
                file_location=file_location, 
                source=source, 
                add_container=True, 
                verbose=verbose
            )

    @error_handler
    def read_METADATA(self,
                 file_location: Optional[str] = None,
                 add_container: bool = True,
                 energy_tag: Optional[str] = None,
                 forces_tag: Optional[str] = None,
                 container_index: Optional[int] = None,
                 verbose: bool = False) -> List[SingleRun]:
        """
        Reads a metadata file with columns for lattice parameters, multiple elemental species counts, 
        and an energy entry. Automatically infers which columns correspond to lattice, which to species, 
        and which to energy by examining the header labels.

        .. note::

           An example of an expected header might be:

           .. code-block:: none

              l0,l1,l2,l3,l4,l5,l6,l7,l8,H,Ni,O,K,Fe,V,E

           The first 9 columns (l0..l8) represent lattice parameters, while the final column (E) is assumed
           to be energy. All remaining columns correspond to species (e.g., H, Ni, O, K, Fe, V).

        Each subsequent row of data has the corresponding values in the same order:

        1. Identifies lattice columns by detecting those whose header starts with ``l`` (e.g. l0..l8).
        2. Identifies energy columns by detecting ``E`` or ``energy`` in the header.
        3. Classifies all remaining columns as species (e.g., H, O, Ni, etc.).
        4. Creates a :class:`SingleRun` object for each row, populating:
           - Lattice vectors
           - Composition data (number of atoms of each species)
           - Energy value
           - Calls :meth:`add_atom` on :attr:`AtomPositionManager` for as many atoms as indicated by each species count.

        :param file_location: 
            The path to the metadata file. If ``None``, uses ``self.file_location``.
        :type file_location: str, optional

        :param add_container: 
            If ``True``, the newly created :class:`SingleRun` objects are appended to the current container.
        :type add_container: bool

        :param verbose: 
            If ``True``, prints progress or debug information.
        :type verbose: bool

        :returns: 
            A list of :class:`SingleRun` objects, each corresponding to one line of data in the file.
        :rtype: List[SingleRun]

        :raises ValueError:
            If no valid file location is provided or if the file fails basic structure checks (e.g., 
            insufficient lines, column mismatch, reading errors).
        """
        # 1) Determine file location
        file_location = file_location or self.file_location
        if not file_location or not isinstance(file_location, str):
            raise ValueError("A valid file location (string) must be provided.")

        # 2) Read file content using mmap (memory-mapped file)
        try:
            with open(file_location, "r+b") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    content = mm.read().decode("utf-8")
        except Exception as e:
            raise ValueError(f"Error reading file with mmap: {str(e)}")

        # Split the file into lines. 
        lines = content.splitlines()
        if len(lines) < 2:
            raise ValueError("File must contain at least one header line and one data line.")

        # 3) Parse header and classify columns
        header_cols = lines[0].strip().split(',')

        # Identify lattice columns by those that start with 'l'
        lattice_indices = [i for i, h in enumerate(header_cols) if h.startswith('l')]

        # Identify any column(s) for energy by looking for 'E' or 'energy'
        energy_indices = [i for i, h in enumerate(header_cols) if h.lower() == 'e' or 'energy' in h.lower()]

        # Remaining columns are treated as species
        species_indices = [
            i for i in range(len(header_cols))
            if i not in lattice_indices and i not in energy_indices
        ]
        species_list = [header_cols[i] for i in species_indices]

        if verbose:
            print("Header columns:", header_cols)
            print("Lattice column indices:", lattice_indices)
            print("Energy column indices:", energy_indices)
            print("Species column indices:", species_indices)
            print("Detected species:", species_list)

        # 4) Parse data lines and build SingleRun objects
        data_lines = lines[1:]  # everything after the header
        container = []
        line_count = 0

        for row in tqdm(data_lines, desc="Processing lines", unit="line"):
            line_count += 1
            row_str = row.strip()

            # Skip empty lines
            if not row_str:
                continue

            columns = row_str.split(',')
            # If a line doesn't match the column count in the header, skip it (or handle as needed).
            if len(columns) != len(header_cols):
                if verbose:
                    print(f"Skipping line {line_count} due to column mismatch: {len(columns)} != {len(header_cols)}")
                continue

            # Create a new SingleRun object with an AtomPositionManager
            sr = SingleRun(file_location)
            sr.AtomPositionManager = AtomPosition()

            # 4a) Parse lattice data
            try:
                lattice_floats = [float(columns[i]) for i in lattice_indices]
                # Reshape to 3x3 if exactly 9 lattice entries exist; adapt if different lattice dimension
                sr.AtomPositionManager.set_latticeVectors(
                    new_latticeVectors=np.array(lattice_floats).reshape(3, 3)
                )
            except ValueError:
                if verbose:
                    print(f"Failed to parse lattice data on line {line_count}.")
                continue

            # 4b) Parse energy data (if any)
            if energy_indices:
                try:
                    # If there's only one energy column, assume the first found is the main entry
                    energy_col = energy_indices[0]
                    parsed_energy = float(columns[energy_col])
                    sr.AtomPositionManager.E = parsed_energy
                    sr.E = parsed_energy  # Optionally store in sr as well
                except ValueError:
                    if verbose:
                        print(f"Failed to parse energy data on line {line_count}.")
                    continue

            # 4c) Parse composition data (species)
            # Convert each species column to float, then store in sr.composition_data
            composition_values = []
            try:
                for i, sp_idx in enumerate(species_indices):
                    count_val = float(columns[sp_idx])
                    composition_values.append(count_val)
                sr.composition_data = np.array(composition_values, dtype=float)
            except ValueError:
                if verbose:
                    print(f"Failed to parse composition data on line {line_count}.")
                continue

            # 4d) Add atoms to the AtomPositionManager for each species
            #     We assume composition values are integer counts; fractional counts are rounded.
            for i, sp_label in enumerate(species_list):
                atom_count = int(round(sr.composition_data[i]))
                # Generate an array of zeros for positions (atom_count x 3)
                
                # Each atom belongs to the same species label; multiply the label list
                if atom_count > 0:
                    positions = np.zeros((atom_count, 3), dtype=np.float64)
                    sr.AtomPositionManager.add_atom(
                        atomLabels=[sp_label] * atom_count,
                        atomPosition=positions
                    )

            # Append this SingleRun to our local container
            container.append(sr)

        # 5) Optionally add these SingleRun objects to the current container
        if add_container:
            for sr in container:
                self.add_container(sr)

        return container

    def readSubFolder(self, file_location:str=None, source:str='VASP', container_index:int=None, verbose:bool=False, ):
        """
        Reads files from a specified directory and its subdirectories.

        This function is designed to traverse through a directory (and its subdirectories) to read files 
        according to the specified source type. It handles various file-related errors gracefully, providing 
        detailed information if verbose mode is enabled.

        Args:
            file_location (str, optional): The root directory from where the file reading starts. 
                                           Defaults to the instance's file_location attribute if not specified.
            source (str): Type of the source files to be read (e.g., 'OUTCAR' for VASP output files).
            verbose (bool, optional): If True, enables verbose output including error traces.
        """
        file_location = file_location if type(file_location) == str else self.file_location
        for root, dirs, files in os.walk(file_location):
            if verbose: print(root, dirs, files)

            if source == 'OUTCAR': file_location_edited = f'{root}/OUTCAR'
            else: file_location_edited = f'{root}' 

            try:
                SR = self.read_files(file_location=file_location_edited, source=source, subfolders=False, container_index=container_index, verbose=verbose)
            except FileNotFoundError:
                self._handle_error(f"File not found at {file_location_edited}", verbose)
            except IOError:
                self._handle_error(f"IO error reading file at {file_location_edited}", verbose)
            except Exception as e:
                self._handle_error(f"Unexpected error: {e}", verbose)

    @error_handler
    def read_structure(self, file_location:str=None, source:str=None, add_container:bool=True, container_index:int=None, verbose=False):
        """
        Reads a trajectory file and stores each frame along with its time information.

        Args:
            file_location (str, optional): The file path of the trajectory file.
            verbose (bool, optional): If True, enables verbose output.

        Notes:
            This method updates the containers with SingleRun objects representing each frame.
            If available, time information is also stored.
        """
        file_location = file_location if type(file_location) == str else self.file_location
        SR = SingleRun(file_location)
        SR.read_structure(file_location=file_location, source=source, container_index=container_index) 
        self.add_container(container=SR)

    @error_handler
    def read_dump(self, file_location:str=None, add_container:bool=True, container_index: Optional[int] = None, verbose=False, **kargs):
        '''
        '''
        file_location = file_location if type(file_location) == str else self.file_location

        lines =list(self.read_file(file_location,strip=False))
        container = []

        for i, line in enumerate(lines):
            if line.startswith("ITEM: TIMESTEP"):
                SR = SingleRun(file_location)
                SR.AtomPositionManager = AtomPosition()
                SR.AtomPositionManager.read_DUMP(lines=lines[i:])

                container.append(SR)

                if add_container and SR.AtomPositionManager is not None: 
                    container.append(SR)
                    
                if verbose: 
                    try: 
                        print(f' >> READ dump :: frame {len(container)} - atoms {num_atoms}')
                    except Exception as e:
                        print(f'Verbose output failed due to an error: {e}')
                        print('Skipping line due to the above error.')

        if isinstance(container_index, int):  
            self.add_container(container=container[container_index])
        else:
            for sr in container:
                self.add_container(container=container[container_index])
          
        return container

    @error_handler
    def read_traj(self, file_location:str=None, add_container:bool=True, container_index: Optional[int] = None, verbose=False, *args, **kargs):
        """
        Reads a trajectory file and stores each frame along with its time information.

        Args:
            file_location (str, optional): The file path of the trajectory file.
            verbose (bool, optional): If True, enables verbose output.

        Notes:
            This method updates the containers with SingleRun objects representing each frame.
            If available, time information is also stored.
        """
        file_location = file_location if type(file_location) == str else self.file_location
        from ase.io import Trajectory
        traj = Trajectory(file_location)
        container = []

        for atoms in traj:

            sr = SingleRun(file_location)
            sr.AtomPositionManager.read_ASE(ase_atoms=atoms) 

            if add_container and sr.AtomPositionManager is not None: 
                # Store the frame
                container.append(sr)
                
                if verbose: 
                    try: 
                        print(f' >> READ dump :: frame {len(container)} - atoms {num_atoms}')
                    except Exception as e:
                        print(f'Verbose output failed due to an error: {e}')
                        print('Skipping line due to the above error.')

        if add_container:
            if isinstance(container_index, int):
                if container_index < len(container):
                    self.add_container(container=container[container_index])
                else:
                    raise IndexError("Container index out of range.")
            else:
                for sr in container:
                    if sr.AtomPositionManager is not None:
                        self.add_container(container=sr)

        del Trajectory

        return container

    def read_XYZ(self,
                 file_location: Optional[str] = None,
                 add_container: bool = True,
                 energy_tag: Optional[str] = None,
                 forces_tag: Optional[str] = None,
                 container_index: Optional[int] = None,
                 verbose: bool = False) -> List[SingleRun]:
        """
        Read XYZ file(s) and create SingleRun objects with AtomPosition data.

        This method processes XYZ format files, extracting atomic positions and 
        optionally energy and forces data. It creates SingleRun objects for each 
        frame in the XYZ file and can add them to the current object's container.

        Args:
            file_location (str, optional): Path to the XYZ file. If None, uses self.file_location.
            add_container (bool): If True, adds created SingleRun objects to the current object's container.
            energy_tag (str, optional): Tag to identify energy data in the XYZ file.
            forces_tag (str, optional): Tag to identify forces data in the XYZ file.
            container_index (int, optional): If provided, only adds the SingleRun at this index to the container.
            verbose (bool): If True, prints progress information.

        Returns:
            List[SingleRun]: A list of created SingleRun objects.

        Raises:
            ValueError: If the file cannot be read or parsed correctly.
        """

        # --------------------------------------------------------------------------
        # 1) Determine file location
        # --------------------------------------------------------------------------
        file_location = file_location or self.file_location
        if not isinstance(file_location, str):
            raise ValueError("Invalid file location provided.")

        # --------------------------------------------------------------------------
        # 2) Use mmap to read the entire file content in binary mode
        #    We decode it into a string for further line splitting.
        #    If mmap fails for some reason, a ValueError is raised.
        # --------------------------------------------------------------------------
        try:
            with open(file_location, "r+b") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # Read entire file content from the memory map
                    content = mm.read().decode("utf-8")
        except Exception as e:
            raise ValueError(f"Error reading file with mmap: {str(e)}")

        # --------------------------------------------------------------------------
        # 3) Convert file content into a list of lines
        #    splitlines() automatically handles various newline styles.
        # --------------------------------------------------------------------------
        lines = content.splitlines(keepends=False)

        # --------------------------------------------------------------------------
        # 4) First pass: determine total number of frames (for tqdm initialization).
        #    Each frame is denoted by a valid integer > 0 on a line (the number of atoms).
        # --------------------------------------------------------------------------
        total_frames = 0
        for line in lines:
            line_str = line.strip()
            if line_str.isdigit():
                try:
                    if int(line_str) > 0:
                        total_frames += 1
                except ValueError:
                    # If parsing fails, we ignore this line
                    pass

        # --------------------------------------------------------------------------
        # 5) Main loop: parse each frame by detecting its start, then reading
        #    'num_atoms + 2' lines for that frame.
        # --------------------------------------------------------------------------
        
        container = []

        i = 0  # line index
        idx = 0
        with tqdm(total=total_frames, desc="Reading XYZ frames", unit="frame") as pbar:
            while i < len(lines):
                line_str = lines[i].strip()
                # If this line is a valid positive integer, treat it as a frame start
                if line_str.isdigit():
                        #try:

                        num_atoms = int(line_str)
                        if num_atoms > 0:
                            # Create a SingleRun instance and parse the frame
                            
                            #sr.AtomPositionManager = AtomPosition()

                            end_idx = i + num_atoms + 2
                            # Check if the file has enough lines for this frame
                            if end_idx > len(lines):
                                if verbose:
                                    print(f"Frame extends beyond end of file at line {i}. Stopping parse.")
                                break

                            sr = SingleRun(file_location)
                            # The method 'AtomPositionManager.read_XYZ' will parse these lines

                            sr.AtomPositionManager.read_XYZ(
                                lines=lines[i:end_idx],
                                tags={'energy': energy_tag, 'forces': forces_tag}
                            )

                            container.append( sr )
                            pbar.update(1)

                            # Jump the file pointer to the end of the current frame
                            i = end_idx
                            idx += 1
                            continue
                        #except Exception as e:
                        # Any parsing errors get printed if verbose is True
                        if verbose:
                            print(f"Verbose output failed at frame {len(container)}: {e}")
                i += 1  # Move to the next line if not a valid frame start

        # --------------------------------------------------------------------------
        # 6) Optionally add these SingleRun objects to the current object's container
        # --------------------------------------------------------------------------
        if add_container:
            if isinstance(container_index, int):
                if container_index < len(container):
                    self.add_container(container=container[container_index])
                else:
                    raise IndexError("Container index out of range.")
            else:
                for sr in container:
                    if sr.AtomPositionManager is not None:
                        self.add_container(container=sr)

        return container

    def read_OUTCAR(self,
                    file_location: Optional[str] = None,
                    add_container: bool = True,
                    container_index: Optional[int] = None,
                    verbose: bool = False,
                    **kwargs) -> List[SingleRun]:
        """
        Read and process an OUTCAR file, creating SingleRun objects from its contents.

        This method reads an OUTCAR file using the OutFileManager, extracts relevant data,
        and creates SingleRun objects. It handles both cases where dynamical eigenvectors
        are present or not.

        Args:
            file_location (str, optional): Path to the OUTCAR file. If None, uses the default location.
            add_container (bool): If True, adds created SingleRun objects to the container.
            container_index (int, optional): If provided, only adds the SingleRun at this index to the container.
            verbose (bool): If True, prints additional information during processing.
            **kwargs: Additional keyword arguments (unused in this implementation but allows for future expansion).

        Returns:
            List[SingleRun]: A list of created SingleRun objects.

        Raises:
            FileNotFoundError: If the specified OUTCAR file is not found.
            ValueError: If container_index is out of range or if no file location is provided.
            RuntimeError: If there's an error reading the OUTCAR file.
        """
        # Validate and set file location
        file_location = file_location or self.file_location
        if not file_location:
            raise ValueError("No file location provided for OUTCAR reading.")

        # Read OUTCAR file
        try:
            of = OutFileManager(file_location)
            of.readOUTCAR()
            if verbose:
                print(f"Successfully read OUTCAR file from {file_location}")
        except FileNotFoundError:
            raise FileNotFoundError(f"OUTCAR file not found at {file_location}")
        except Exception as e:
            raise RuntimeError(f"Error reading OUTCAR file: {str(e)}")

        new_containers = []

        # Process data based on presence of dynamical eigenvectors
        if of.dynamical_eigenvector is not None:
            if verbose:
                print("Processing OUTCAR with dynamical eigenvectors.")
            for eigenvalues, eigenvector, eigenvector_diff in zip(
                of.dynamical_eigenvalues, of.dynamical_eigenvector, of.dynamical_eigenvector_diff
            ):
                sr = SingleRun(file_location)
                sr._AtomPositionManager = of.AtomPositionManager[0]
                sr._AtomPositionManager._atomPositions = eigenvector
                sr._AtomPositionManager._dynamical_eigenvector = eigenvector
                sr._AtomPositionManager._dynamical_eigenvalues = eigenvalues
                sr._AtomPositionManager._dynamical_eigenvector_diff = eigenvector_diff
                sr._InputFileManager = of.InputFileManager
                sr._KPointsManager = of._KPointsManager
                sr._PotentialManager = of._PotentialManager
                new_containers.append(sr)
        else:
            if verbose:
                print("Processing OUTCAR without dynamical eigenvectors.")
            for apm in of.AtomPositionManager:
                sr = SingleRun(file_location)
                sr._AtomPositionManager = apm
                sr._InputFileManager = of.InputFileManager
                sr._KPointsManager = of._KPointsManager
                sr._PotentialManager = of._PotentialManager
                new_containers.append(sr)

        if verbose:
            print(f"Created {len(new_containers)} SingleRun objects from OUTCAR.")

        # Add containers to the manager based on the provided index or add all
        if add_container:
            if isinstance(container_index, int):
                if 0 <= container_index < len(new_containers):
                    self.add_container(container=new_containers[container_index])
                    if verbose:
                        print(f"Added SingleRun object at index {container_index} to container.")
                else:
                    raise ValueError(f"Container index {container_index} is out of range.")
            else:
                for sr in new_containers:
                    self.add_container(container=sr)
                if verbose:
                    print(f"Added all {len(new_containers)} SingleRun objects to container.")

        return new_containers

    def read_vasp_folder(self, file_location:str=None, add_container:bool=True, verbose:bool=False, **kwargs):
        '''
        '''
        file_location = file_location if type(file_location) == str else self.file_location
        SR = SingleRun(file_location)
        SR.readVASPDirectory(file_location)        
        if add_container and SR.AtomPositionManager is not None: 
            self.add_container(container=SR)

        return SR

    def read_dftb_folder(self, file_location:str=None, add_container:bool=True, verbose:bool=False, **kwargs):
        '''
        '''
        file_location = file_location if type(file_location) == str else self.file_location
        SR = SingleRun(file_location)
        SR.readDFTBDirectory(file_location)        
        if add_container and SR.AtomPositionManager is not None: 
            self.add_container(container=SR)

        return SR

    def export_files(self, file_location:str=None, source:str=None, label:str=None, bond_factor:float=None, verbose:bool=False):
        """
        Exports files for each container in a specified format.

        The function iterates over all containers and exports them according to the specified format.
        In case of an error during export, it logs the error (if verbose is True) and continues with the next container.

        Args:
            file_location (str): The base directory for exporting files.
            source (str): The format to export files in ('VASP', 'POSCAR', 'XYZ', 'PDB', 'ASE').
            label (str): Labeling strategy for exported files ('enumerate' or 'fixed').
            bond_factor (float): The bond factor to use for PDB export.
            verbose (bool): If True, enables verbose output including error messages.
        """
        # Identify the file type if 'source' is not specified
        source = self._identify_file_type(file_location) if source is None else source
        # Set a default labeling strategy if not provided
        label = label if isinstance(label, str) else 'fixed'

        file_locations = []

        # Use tqdm to show progress over the containers
        for c_i, container in enumerate(tqdm(self.containers, desc="Exporting containers", unit="container")):
            try:
                # Determine the number of digits to keep enumeration consistent (e.g., 001, 002, ...)
                num_digits = len(str(len(self.containers)))

                # Label-based path selection
                if label == 'enumerate':
                    file_location_edited = file_location + f'/{c_i:0{num_digits}d}'
                elif label == 'fixed':
                    file_location_edited = container.file_location

                # Create necessary directories
                if source.upper() != 'XYZ':
                    self.create_directories_for_path(file_location_edited)
                else:
                    # For XYZ, we might just create the base directory once
                    self.create_directories_for_path(file_location)

                # Export based on the specified source format
                if source.upper() == 'VASP':
                    container.exportVASP(file_location=file_location_edited)

                elif source.upper() == 'POSCAR':
                    container.AtomPositionManager.export_as_POSCAR(
                        file_location=file_location_edited + '/POSCAR'
                    )

                elif source.upper() == 'XYZ':
                    container.AtomPositionManager.export_as_xyz(
                        file_location=file_location + '/config.xyz', 
                        save_to_file='a'
                    )

                elif source.upper() == 'PDB':
                    container.AtomPositionManager.export_as_PDB(
                        file_location=file_location_edited + '/structure.pdb',
                        bond_factor=bond_factor
                    )

                elif source.upper() == 'GEN':
                    container.AtomPositionManager.export_as_GEN(
                        file_location=file_location_edited + '/geo_end.gen',
                    )

                elif source.upper() == 'ASE':
                    container.AtomPositionManager.export_as_ASE(
                        file_location=file_location_edited + '/ase.obj'
                    )

                else:
                    # For any other recognized format
                    container.AtomPositionManager.export(
                        file_location=file_location_edited + f'/structure.{source}',
                        fmt=source
                    )

                # Keep track of the exported file location
                file_locations.append(file_location_edited)

            except Exception as e:
                # Print error details for this container, continue with the next
                print(f"Failed to export container {c_i}: {e}")
                traceback.print_exc()

        # self.generate_execution_script_for_each_container(directories=file_locations, file_location='.')
        return file_locations

    def export_configXYZ(self, file_location: Optional[str] = None, verbose: bool = False) -> bool:
        """
        Export configuration data in XYZ format for all containers with OutFileManager.

        This method creates a single XYZ file containing the configuration data from all
        containers that have an OutFileManager. The data is appended to the file for each
        container.

        Args:
            file_location (str, optional): Path where the XYZ file will be saved.
                If None, uses the default location with '_config.xyz' appended.
            verbose (bool): If True, prints additional information during the export process.

        Returns:
            bool: True if the export was successful, False otherwise.

        Raises:
            IOError: If there's an error creating or writing to the file.
        """
        try:
            # Determine the file location
            file_location = file_location or f"{self.file_location}_config.xyz"
            
            if verbose:
                print(f"Preparing to export XYZ configuration to {file_location}")

            # Create an empty file or truncate existing file
            with open(file_location, 'w') as f:
                pass

            export_count = 0
            for container_index, container in enumerate(self.containers):
                if container.OutFileManager is not None:
                    try:
                        container.OutFileManager.export_configXYZ(
                            file_location=file_location, 
                            save_to_file='a',  # Append mode
                            verbose=False  # We'll handle verbosity here
                        )
                        export_count += 1
                        if verbose:
                            print(f"Exported configuration for container {container_index}")
                    except Exception as e:
                        print(f"Warning: Failed to export container {container_index}. Error: {str(e)}")

            if verbose:
                print(f"XYZ content has been saved to {file_location}")
                print(f"Exported configurations for {export_count} out of {len(self.containers)} containers")

            return True

        except IOError as e:
            print(f"Error: Failed to create or write to file {file_location}. Error: {str(e)}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return False
    
    def _is_redundant(self, containers:list=None, new_container:object=None):
        """
        Checks if a new container is redundant within existing containers.

        Args:
        - new_container (object): The new container to check.
        - containers (list, optional): List of existing containers.

        Returns:
        - bool: True if redundant, False otherwise.
        """
        containers = containers if containers is not None else self.containers
        return any(np.array_equal(conteiner.atomPositions, new_container.atomPositions) for conteiner in containers)

    def summary(self, ) -> str:
        """
        Generates a summary string of the PartitionManager's current state.

        Returns:
            str: A summary string detailing the file location and the number of containers managed.
        """
        text_str = ''
        text_str += f'{self.file_location}\n'
        text_str += f'> Conteiners : { len(self.containers) }\n'
        return text_str
    
    def copy_and_update_container(self, container, sub_directory: str, file_location=None):
        """
        Creates a deep copy of a given container and updates its file location.

        Args:
            container (object): The container object to be copied.
            sub_directory (str): The subdirectory to append to the container's file location.
            file_location (str, optional): Custom file location for the new container. If None, appends sub_directory to the original container's file location.

        Returns:
            object: The copied and updated container object.
        """
        container_copy = copy.deepcopy(container)
        container_copy.file_location = f'{container.file_location}{sub_directory}' if file_location is None else file_location
        return container_copy

    def generate_execution_script_for_each_container(self, directories: list = None, file_location: str = None, max_batch_size:int=200):
        """
        Generates and writes an execution script for each container in the specified directories.

        Args:
            directories (list, optional): List of directory paths for which the execution script is to be generated.
            file_location (str, optional): The file path where the generated script will be saved.

        Notes:
            The script 'RUNscript.sh' will be generated and saved to each specified directory.
        """
        self.create_directories_for_path(file_location)
        script_content = self.generate_script_content(script_name='RUNscript.sh', directories=directories, max_batch_size=max_batch_size)
        self.write_script_to_file(script_content, f"{file_location}")

    def generate_script_content(self, script_name:str, directories:list=None, max_batch_size:int=200) -> str:
        """
        Generates the content for a script that runs specified scripts in given directories.

        Args:
            script_name (str): The name of the script to run in each directory.
            directories (list, optional): A list of directories where the script will be executed.

        Returns:
            str: The generated script content as a string.
        """
        directories_str_list = [  "\n".join([f"    '{directory}'," for directory in directories[i:i + max_batch_size] ]) for i in range(0, len(directories), max_batch_size)]
        
        return [f'''#!/usr/bin/env python3
import os
import subprocess

original_directory = os.getcwd()

directories = [
{directories_str}
]

for directory in directories:
    os.chdir(directory)
    subprocess.run(['chmod', '+x', '{script_name}'])
    subprocess.run(['sbatch', '{script_name}'])
    os.chdir(original_directory)
''' for directories_str in directories_str_list ] 

    def write_script_to_file(self, script_content: str, file_path: str):
        """
        Writes the provided script content to a file at the specified path.

        Args:
            script_content (str): The content of the script to be written.
            file_path (str): The file path where the script will be saved.

        Notes:
            This method creates or overwrites the file at the specified path with the given script content.
        """
        for sc_index, sc in enumerate(script_content):
            with open(file_path+f"/execution_script_for_each_container_{sc_index}.py", "w") as f:
                f.write(sc)

    def save_array_to_csv(self, array, column_names:list = None, sample_numbers: bool = False, file_path: str = '.', verbose: bool = False):
        """
        Save a NumPy array to a CSV file with specified column names and sample numbers.
        
        Parameters:
        array (np.ndarray): The data array to save.
        column_names (list of str, optional): The names of the columns. If None, no column names are written. Defaults to None.
        sample_numbers (bool, optional): If True, sample numbers (row indices) are included as the first column. Defaults to False.
        file_path (str, optional): The directory path to save the CSV file. Defaults to '.'.
        verbose (bool, optional): If True, prints additional information. Defaults to False.
        """
        # Ensure array is 2D
        if array.ndim == 1:
            array = array.reshape(1, -1)

        # Ensure column_names is a list if it is a NumPy array
        if isinstance(column_names, np.ndarray):
            column_names = column_names.tolist()

        # Create the full file path
        full_file_path = os.path.join(file_path, 'sage_data_array.csv')
        
        # Open the file in write mode
        with open(full_file_path, mode='w') as file:
            # Write the header if column names are provided
            if column_names:
                if sample_numbers:
                    header = 'Sample,' + ','.join(column_names) + '\n'
                else:
                    header = ','.join(column_names) + '\n'
                file.write(header)
            
            # Write the data rows
            for i, row in enumerate(array):
                row_str = ','.join(map(str, row))
                if sample_numbers:
                    file.write(f"{i},{row_str}\n")
                else:
                    file.write(f"{row_str}\n")
        
        if verbose:
            print(f"Array saved to {full_file_path}")
