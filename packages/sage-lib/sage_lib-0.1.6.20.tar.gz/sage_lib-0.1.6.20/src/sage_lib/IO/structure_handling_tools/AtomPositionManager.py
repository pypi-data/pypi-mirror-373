try:
    from .AtomPositionLoader import AtomPositionLoader
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.structure_handling_tools.AtomPositionLoader: {str(e)}\n")
    del sys

try:
    from .AtomPositionOperator import AtomPositionOperator
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.structure_handling_tools.AtomPositionOperator: {str(e)}\n")
    del sys

try:
    from .AtomPositionMaker import AtomPositionMaker
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.structure_handling_tools.AtomPositionMaker: {str(e)}\n")
    del sys
 
try:
    from ...master.AtomicProperties import AtomicProperties
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.structure_handling_tools.AtomPositionMaker: {str(e)}\n")
    del sys
    
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

class AtomPositionManager(AtomPositionOperator, AtomPositionLoader, AtomPositionMaker, AtomicProperties):
    """
    Manages atomic position information, integrating functionalities from AtomPositionOperator and AtomPositionLoader.

    This class is responsible for handling and manipulating atomic positions and related properties
    for a given set of atoms. It allows for loading, processing, and analyzing atomic position data
    from various sources.
    """
    
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initializes the AtomPositionManager instance.

        Args:
            file_location (str, optional): Location of the file containing atomic data.
            name (str, optional): Name identifier for the atomic data.
            kwargs: Additional keyword arguments.
        """

        # Initialize base classes with provided arguments
        AtomPositionOperator.__init__(self, name=name, file_location=file_location)
        AtomPositionLoader.__init__(self, name=name, file_location=file_location)
        AtomPositionMaker.__init__(self, name=name, file_location=file_location)

        # Attributes initialization with descriptions
        self._comment = None  # Placeholder for comments. Type: str or None. Example: "Sample comment about the atomic structure"
        '''
        self._comment:

        Description: A placeholder for any comments associated with the atomic data.
        Type: str or None
        Example: "Sample comment about the atomic structure"
        Size: Variable length string.
        Additional Information: Used to store descriptive or explanatory text related to the atomic data.
        self._atomCount:
        '''
        self._atomCount = None  # Total number of atoms. Type: int or None. Example: 100
        '''
        Description: The total number of atoms in the structure.
        Type: int or None
        Example: 100 (indicating 100 atoms)
        Size: Single integer value.
        Additional Information: Represents the count of all atoms regardless of their type.
        self._scaleFactor:
        '''
        self._scaleFactor = None  # Scale factor for atomic positions. Type: float, int, list, np.array, or None. Example: 1.0 or [1.0, 1.0, 1.0]
        '''
        Description: A scale factor applied to the atomic positions.
        Type: float, int, list, np.array, or None
        Example: 1.0 or [1.0, 1.0, 1.0]
        Size: Single value or an array of up to three elements.
        Additional Information: Used in scaling the atomic positions, often for unit conversion or normalization.
        self._uniqueAtomLabels:
        '''
        self._uniqueAtomLabels = None  # Unique labels of atom types. Type: list of str or None. Example: ["Fe", "N", "C", "H"]
        '''
        Description: A list of unique labels representing different types of atoms.
        Type: list of str or None
        Example: ["Fe", "N", "C", "H"]
        Size: Number of unique atom types.
        Additional Information: Useful for identifying the distinct elements or molecules in the structure.
        self._atomCountByType:
        '''
        self._atomCountByType = None  # Count of atoms for each type. Type: list of int or None. Example: [4, 10, 6, 2]
        '''
        Description: A list indicating the count of atoms for each unique type.
        Type: list of int or None
        Example: [4, 10, 6, 2] corresponding to ["Fe", "N", "C", "H"]
        Size: Same as the number of unique atom types.
        Additional Information: Provides a count of each atom type, useful for composition analysis.
        self._selectiveDynamics:
        '''
        self._selectiveDynamics = None  # Indicates if selective dynamics are used. Type: bool or None. Example: True
        '''
        Description: A boolean indicating if selective dynamics are used (allowing certain atoms to move while others are fixed).
        Type: bool or None
        Example: True (indicating selective dynamics are used)
        Size: Single boolean value.
        Additional Information: Relevant in simulations where only a subset of atoms are allowed to participate in dynamics.
        self._atomPositions:
        '''
        self._atomPositions = None  # Array of atomic positions. Type: np.array(N, 3) or None. Example: np.array([[0, 0, 0], [1.5, 1.5, 1.5]])
        '''
        Description: A NumPy array containing the positions of each atom.
        Type: np.array with shape (N, 3) or None
        Example: np.array([[0, 0, 0], [1.5, 1.5, 1.5]]) for two atoms
        Size: N rows and 3 columns, where N is the number of atoms.
        Additional Information: The positions are typically in Cartesian coordinates (x, y, z).
        self._atomicConstraints:
        '''
        self._atomicConstraints = None # Atomic constraints. Type: np.array(N, 3) or None. Example: np.array([[1, 1, 1], [0, 1, 0]])
        '''
        Description: An array indicating constraints applied to each atom, often used in simulations to control atomic movement.
        Type: np.array with shape (N, 3) or None
        Example: np.array([[1, 1, 1], [0, 1, 0]]) (1s and 0s indicate constrained and unconstrained directions respectively)
        Size: N rows and 3 columns, mirroring the size of _atomPositions.
        Additional Information: Constraints are useful in simulations where certain atomic motions are restricted.
        self._atomLabelsList:
        '''
        
        self._atomLabelsList = None  # List of atom labels for all atoms. Type: list of str or None. Example: ["Fe", "N", "N", "N", "N", "C", "C", "C", "C", "H"]
        '''
        Description: A list of labels for all atoms, in the order they appear.
        Type: list of str or None
        Example: ["Fe", "N",  "N", "N", "N", "N", "C", "C", "C"] (for a structure with these atoms in sequence)
        Size: Length equal to the total number of atoms.
        Additional Information: Provides a straightforward way to identify each atom's type.
        self._fullAtomLabelString:
        '''

        self._atomCountDict = None
        '''
        Description: A dictionary containing the count of atoms for each unique atom type in the structure.
        Type: dict or None
        Example: {"Fe": 4, "N": 10, "C": 6, "H": 2}
        Size: Number of keys equals the number of unique atom types.
        Additional Information: This dictionary is computed from the full list of atom labels and is used for composition analysis.
        '''

        self._time = None
        self._timestep = None 

        self._fullAtomLabelString = None  # Concatenated string of all atom labels. Type: str or None. Example: "FeFeFeNNNNNNNCCCCCCCCCCCCCCCHHHHHHHHHHHHHHHH"
        self._atomPositions_tolerance = 1e-2  # Tolerance for position comparison. Type: float
        self._distance_matrix = None  # Distance matrix between atoms. Type: np.array or None
        self._kdtree = None

        # == == Molecular / atomistic representations == == #
        self._MBTR = None
        self._MBTR_representation, self._MBTR_representation_dev = None, None
        self._graph_representation, self._similarity_matrix = None, None

        # Properties related to atomic calculations
        self._total_charge = None  # Total charge. Type: float or None
        self._charge = None  # charge. Type: float or None

        self._magnetization = None  # Magnetization. Type: float or None
        self._total_force = None  # Total force. Type: np.array or None
        self._force = None  # Total force. Type: np.array or None

        self._class_ID = None
        
        self._E = None  # Total energy. Type: float or None
        self._Edisp = None  # Dispersion energy. Type: float or None

        self._dynamical_eigenvalues = None  # array Type: N
        self._dynamical_eigenvector = None  # array Type: Nx3
        self._dynamical_eigenvalues_fractional = None  # array Type: Nx3
        self._dynamical_eigenvector_diff = None  # array Type: Nx3
        self._dynamical_eigenvector_diff_fractional = None  # array Type: Nx3

        self._mass = None # 
        self._mass_list = None # 

        self.info_system = {}
        self.info_atoms = {}
        
        self.metadata = {}

    def __getstate__(self):
        st = self.__dict__.copy()
        st.pop('_kdtree', None)
        return st

    def __setstate__(self, st):
        self.__dict__.update(st)
        self._kdtree = None

    def configure(self,
                  atomPositions: np.ndarray,
                  atomLabels:    np.ndarray,
                  latticeVectors: np.ndarray,
                  E:              np.ndarray             = None,
                  atomicConstraints: np.ndarray         = None,
                  **kwargs) -> bool:
        """
        Configure the core state of the AtomPositionOperator.

        Required Parameters
        -------------------
        atomPositions : np.ndarray, shape (N,3)
            Cartesian coordinates of N atoms.
        atomLabels : array-like of str, length N
            Element labels (e.g. ['Fe','O','H',…]).
        latticeVectors : np.ndarray, shape (3,3)
            Primitive cell vectors as rows (or columns) of the 3×3 matrix.

        Optional Parameters
        -------------------
        E : np.ndarray, shape (N,) or (N,k), default=None
            Per-atom or per-configuration energy values.
        atomicConstraints : np.ndarray, shape (N,3), default=None
            Per-atom boolean flags indicating which Cartesian components
            are free (1) or fixed (0).
        **kwargs : any
            Additional per-atom arrays (e.g. charges, magnetizations, forces).

        Returns
        -------
        bool
            True if configuration succeeded; False otherwise.

        Notes
        -----
        - All provided arrays must agree on the number of atoms, N.
        - Invalidates any cached attributes: inverse lattice, distance matrix,
          k-d tree, fractional positions, label-based caches.
        """
        # 1) Convert labels to object array
        labels_arr = np.asarray(atomLabels, dtype=object)
        atomPositions = np.asarray(atomPositions, dtype=np.float64)
        latticeVectors = np.asarray(latticeVectors, dtype=np.float64)

        # 2) Validate shapes
        if atomPositions.ndim != 2 or atomPositions.shape[1] != 3:
            raise ValueError(f"atomPositions must be shape (N,3), got {atomPositions.shape}")
        N = atomPositions.shape[0]
        if labels_arr.shape[0] != N:
            raise ValueError(f"Need {N} labels, got {labels_arr.shape[0]}")
        if latticeVectors.shape != (3,3):
            raise ValueError(f"latticeVectors must be shape (3,3), got {latticeVectors.shape}")

        # 3) Assign core arrays
        self._atomPositions       = np.array(atomPositions,      dtype=float)
        self._atomLabelsList      = labels_arr
        self._latticeVectors      = np.array(latticeVectors,    dtype=float)
        # Precompute inverse lattice
        self._latticeVectors_inv  = np.linalg.inv(self._latticeVectors)

        # 4) Optional fields
        if E is not None:
            self._E = np.asarray(E)
        if atomicConstraints is not None:
            ac = np.asarray(atomicConstraints)
            if ac.shape != (N,3):
                raise ValueError(f"atomicConstraints must be shape ({N},3), got {ac.shape}")
            self._atomicConstraints = ac

        # 5) Any additional arrays passed via kwargs
        for key, arr in kwargs.items():
            arr = np.asarray(arr)
            if arr.shape[0] != N:
                raise ValueError(f"{key} must have length {N}, got {arr.shape[0]}")
            setattr(self, f"_{key}", arr)

        # 6) Invalidate all dependent caches
        for attr in ("_atomPositions_fractional", "_distance_matrix",
                     "_kdtree", "_fullAtomLabelString",
                     "_uniqueAtomLabels", "_atomCountByType"):
            setattr(self, attr, None)

        # 7) Update derived scalar fields
        self._atomCount = N
        return True

    @property
    def distance_matrix(self):
        """
        Calculates and returns the distance matrix between atoms.

        The distance matrix is calculated using Euclidean distances. It is computed only if not already available.

        Returns:
            np.array: A matrix of distances between each pair of atoms.
        """
        if self._distance_matrix is not None:
            return self._distance_matrix
        elif self.atomPositions is not None:
            self._distance_matrix = self.distance_matrix_calculator()
            return self._distance_matrix
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def kdtree(self):
        """
        Return a KD-tree object for neighbor queries.

        - Periodic systems: uses PeriodicCKDTree(lattice, positions).
        - Non-periodic / missing lattice: uses SciPy's cKDTree(positions).

        The built tree is cached in self._kdtree. Invalidate it (set to None)
        whenever latticeVectors or atomPositions change.
        """
        # Reuse if already built
        if getattr(self, "_kdtree", None) is not None:
            return self._kdtree

        # ---- detect non-periodic / invalid lattice
        lat = getattr(self, "latticeVectors", None)
        pbc = getattr(self, "pbc", None)
        nonperiodic = True
        try:
            if lat is not None:
                L = np.asarray(lat, float)
                valid_L = (
                    L.shape == (3, 3)
                    and np.isfinite(L).all()
                    and abs(np.linalg.det(L)) > 1e-9
                )
                pbc_on = (pbc is None) or any(bool(x) for x in np.asarray(pbc).ravel())
                nonperiodic = not (valid_L and pbc_on)
        except Exception:
            nonperiodic = True

        # ---- positions as float array
        X = np.asarray(self.atomPositions, float)

        if nonperiodic:
            # Classic KD-tree (no PBC)
            try:
                from scipy.spatial import cKDTree as _KDTree
            except Exception:
                from scipy.spatial import KDTree as _KDTree
            self._kdtree = _KDTree(X)
            self._kdtree_type = "nonperiodic"
            return self._kdtree

        # ---- periodic KD-tree if available; else graceful fallback
        try:
            from ...miscellaneous.periodic_kdtree import PeriodicCKDTree
            self._kdtree = PeriodicCKDTree(np.asarray(lat, float), X)
            self._kdtree_type = "periodic"
            return self._kdtree
        except Exception:
            # Fallback to classic KD-tree if periodic implementation is unavailable
            try:
                from scipy.spatial import cKDTree as _KDTree
            except Exception:
                from scipy.spatial import KDTree as _KDTree
            self._kdtree = _KDTree(X)
            self._kdtree_type = "nonperiodic"
            return self._kdtree

    @property
    def scaleFactor(self):
        """
        Ensures the scale factor is returned as a numpy array.

        If the scale factor is not set, it initializes it to a default value.

        Returns:
            np.array: The scale factor as a numpy array.
        """
        # Convert and return scaleFactor to numpy array
        if type(self._scaleFactor) in [int, float, list, np.array]:
            self._scaleFactor = np.array(self._scaleFactor)
            return self._scaleFactor
        elif self._scaleFactor is None: 
            self._scaleFactor = np.array([1])
            return self._scaleFactor
        elif self._scaleFactor is not None:
            return self._scaleFactor
        else:
            return None

    @property
    def atomCount(self):
        """
        Returns the total count of atoms.

        If the atom count has not been directly set, it is inferred from the shape of `_atomPositions` 
        or the length of `_atomLabelsList`. This property ensures that the atom count is always synchronized 
        with the underlying atomic data.

        Returns:
            int: The total number of atoms.
        """
        if self._atomCount is not None:
            return np.array(self._atomCount, dtype=np.int64)
        elif self.atomPositions is not None: 
            self._atomCount = self.atomPositions.shape[0] 
            return self._atomCount
        elif self.atomLabelsList is not None: 
            self._atomCount = self.atomLabelsList.shape
            return self._atomCount   
        elif'_atomPositions' not in self.__dict__:
            raise AttributeError("Attribute _atomPositions must be initialized before accessing atomLabelsList.")
        else:
            return 0

    @property
    def uniqueAtomLabels(self):
        """
        Provides a list of unique atom labels.

        If not set, it is derived from `_atomLabelsList` by identifying the unique labels. This property is 
        useful for identifying the different types of atoms present in the structure.

        Returns:
            np.array: Array of unique atom labels.
        """
        if self._uniqueAtomLabels is not None:
            return self._uniqueAtomLabels
        elif self.atomLabelsList is not None: 
            self._uniqueAtomLabels = list(dict.fromkeys(self.atomLabelsList).keys())
            return np.array(self._uniqueAtomLabels)
        elif'_atomLabelsList' not in self.__dict__:
            raise AttributeError("Attribute _atomLabelsList must be initialized before accessing atomLabelsList.")
        else:
            return None

    @uniqueAtomLabels.setter
    def uniqueAtomLabels(self, labels):
        # validate or normalize here
        self._uniqueAtomLabels = list(labels)
        # make sure we don’t leave an instance attr called 'uniqueAtomLabels'
        if 'uniqueAtomLabels' in self.__dict__:
            del self.__dict__['uniqueAtomLabels']

    @property
    def atomCountByType(self):
        """
        Returns the count of atoms for each unique atom type.

        If not set, it calculates the count based on `_atomLabelsList`. This property is useful for 
        quantitative analysis of the composition of the atomic structure.

        Returns:
            np.array: Array of atom counts for each type.
        """
        if self._atomCountByType is not None:
            return self._atomCountByType
        elif self._atomLabelsList is not None: 
            atomCountByType, atomLabelByType = {}, []
            for a in self._atomLabelsList:
                if not a in atomCountByType:
                    atomLabelByType.append(1)
                    atomCountByType[a] = len(atomLabelByType)-1
                else:
                    atomLabelByType[atomCountByType[a]] += 1
            self._atomCountByType = np.array(atomLabelByType)
            return self._atomCountByType
        elif'_atomLabelsList' not in self.__dict__:
            raise AttributeError("Attribute _atomLabelsList must be initialized before accessing atomLabelsList.")
        else:
            return None

    @property
    def atomLabelsList(self):
        """
        Constructs and returns a list of all atom labels.

        If not set, it is derived from `_atomCountByType` and `_uniqueAtomLabels`. This property provides a 
        comprehensive list of labels for each atom in the structure.

        Returns:
            np.array: Array of atom labels.
        """
        if '_atomCountByType' not in self.__dict__ or '_uniqueAtomLabels' not in self.__dict__:
            raise AttributeError("Attributes _atomCountByType and _uniqueAtomLabels must be initialized before accessing atomLabelsList.")
        elif self._atomLabelsList is None and not self._atomCountByType is None and not self._uniqueAtomLabels is None: 
            self._atomLabelsList = np.array([label for count, label in zip(self._atomCountByType, self._uniqueAtomLabels) for _ in range(count)], dtype=object)
            return self._atomLabelsList
        elif self._atomLabelsList is None:
            return  np.array([], dtype=object)
        else:
            return  np.array(self._atomLabelsList, dtype=object)

    @atomLabelsList.setter
    def atomLabelsList(self, value):
        """
        Setter for atomLabelsList. Ensures the input value is always an np.array with dtype=object.

        Args:
            value (iterable): New value to assign to atomLabelsList.
        """
        if not isinstance(value, (np.ndarray, list)):
            raise ValueError("atomLabelsList must be set as a list or numpy array.")
        
        # Convert to numpy array with dtype=object
        self._atomLabelsList = np.array(value, dtype=object)

    @property
    def atomCountDict(self):
        """
        Returns a dictionary with the count of each unique atom type present in the structure.

        The keys are the unique atom labels (from self._uniqueAtomLabels) and the values
        are the counts determined from self.atomLabelsList. The result is cached in 
        self._atomCountDict to avoid redundant recalculations.

        Returns:
            dict: A dictionary mapping each unique atom label to its count, 
                  or -1 if atom labels are not available.
        """
        # If the dictionary has already been computed, return it directly.
        if self._atomCountDict is not None:
            return self._atomCountDict

        # Check if atom labels are available.
        elif self._atomLabelsList is not None:
            try:
                # Retrieve the list of all atom labels.
                labels = self.atomLabelsList
            except AttributeError:
                # If an AttributeError is raised, default to an empty list.
                labels = []

            # Initialize the dictionary to store counts.
            self._atomCountDict = {}
            # Loop over each unique atom label.
            for unique_label in self.uniqueAtomLabels:
                # Count occurrences of the current unique label in the labels list.
                self._atomCountDict[unique_label] = int(np.count_nonzero(np.array(labels) == unique_label))
            return self._atomCountDict

        # If atom labels are not available, return -1.
        else:
            return -1

    @atomCountDict.setter
    def atomCountDict(self, value):
        """
        Setter for the 'atomCountDict' property. Allows assigning a new dictionary
        of species counts to replace the existing one.

        Parameters
        ----------
        value : dict
            A dictionary mapping chemical species (or other identifiers) to their
            corresponding integer counts. For example: {'Fe': 4, 'H': 12}.
        
        Raises
        ------
        TypeError
            If 'value' is not a dictionary.
        ValueError
            If any of the counts in 'value' are not integers.
        """
        # Basic type checking to ensure the provided value is a dictionary
        if not (isinstance(value, dict) or value is None):
            raise TypeError("atomCountDict must be assigned a dictionary.")

        # Optional: Validate that all keys map to integer values
        if isinstance(value, dict):
            for k, v in value.items():
                if not isinstance(v, int):
                    raise ValueError(
                        f"Each count must be an integer. "
                        f"Key '{k}' has a non-integer value: {v}"
                    )

        self._atomCountDict = value

    @property
    def fullAtomLabelString(self):
        """
        Returns a concatenated string of all atom labels.

        If not set, it is constructed from `_atomCountByType` and `_uniqueAtomLabels`. This property provides 
        a quick textual representation of the entire atomic composition.

        Returns:
            str: Concatenated string of all atom labels.
        """
        if '_atomCountByType' not in self.__dict__ or '_uniqueAtomLabels' not in self.__dict__:
            raise AttributeError("Attributes _atomCountByType and _uniqueAtomLabels must be initialized before accessing fullAtomLabelString.")
        elif self._fullAtomLabelString is None and not self._atomCountByType is None and not self._uniqueAtomLabels is None: 
            self._fullAtomLabelString = ''.join([label*count for count, label in zip(self._atomCountByType, self._uniqueAtomLabels)])
            return self._fullAtomLabelString
        else:
            return  self._fullAtomLabelString 

    @property
    def atomPositions(self):
        """
        Provides the positions of atoms.

        If the positions are set as a list, they are converted to a NumPy array for consistency. If not set, 
        an empty array is returned.

        Returns:
            np.array: Array of atom positions.
        """
        if isinstance(self._atomPositions, list):
            return np.array(self._atomPositions)
        elif self._atomPositions is None:
            return np.zeros((0, 3))
        else:
            return self._atomPositions

    @atomPositions.setter
    def atomPositions(self, new_atomPositions: np.ndarray):
        """
        Setter para atomPositions. Actualiza las posiciones y borra
        las caches de distance_matrix, kdtree, y posiciones fraccionales.
        """
        self._atomPositions = new_atomPositions
        # invalidamos todos los datos que dependen de las posiciones
        self._distance_matrix = None
        self._kdtree = None
        self._atomPositions_fractional = None

    @property
    def atomicConstraints(self):
        """
        Returns the constraints applied to atoms.

        If not set, and if atom positions are available, it initializes the constraints as an array of ones 
        (indicating no constraints). Otherwise, it returns the set constraints.

        Returns:
            np.array: Array of atomic constraints.
        """
        if self._atomicConstraints is list:
            return np.array(self._atomicConstraints)
        elif self._atomicConstraints is None:
            self._atomicConstraints = np.zeros_like(self.atomPositions) 
            return self._atomicConstraints
        else:
            return self._atomicConstraints

    @property
    def selectiveDynamics(self):
        """
        """
        if self._selectiveDynamics:
            return True        
        if not self._atomicConstraints is None:
            return True
        else:
            return False

    @property
    def mass_list(self):
        """

        """
        if self._mass_list is list:
            return np.array(self._mass_list)
        else:
            self._mass_list = np.array([ float(self.atomic_mass[atom_label]) for atom_label in self.atomLabelsList], np.float64)
            return self._mass_list

    @property
    def time(self):
        """

        """
        if self.is_number(self._time):
            return self._time
        else:
            self._time = 0
            return self._time

    @property
    def timestep(self):
        """

        """
        if self.is_number(self._timestep):
            return self._timestep
        else:
            self._timestep = 0
            return self._timestep

    @property
    def mass(self):
        """

        """
        if self._mass is float:
            return self._mass
        else:
            self._mass = np.sum(self.mass_list)
            return self._mass

    @property
    def MBTR(self):
        """

        """
        if self._MBTR is None:
            self.get_MBTR_representation()
            return self._MBTR
        else:
            return self._MBTR

    @property
    def similarity_matrix(self):
        """

        """
        if self._similarity_matrix is None:
            self._similarity_matrix = self.get_similarity_matrix()
            return self._similarity_matrix
        else:
            return self._similarity_matrix

    @property
    def graph_representation(self):
        """

        """
        if self._graph_representation is None:
            self._graph_representation = self.find_related_atoms_groups()
            return self._graph_representation
        else:
            return self._graph_representation

    @property
    def dynamical_eigenvalues(self):
        """

        """
        if isinstance(self._dynamical_eigenvalues, list):
            self._dynamical_eigenvalues = np.array(self._dynamical_eigenvalues, dtype=np.float64)
            return self._dynamical_eigenvalues
        else:
            return self._dynamical_eigenvalues

    @property
    def dynamical_eigenvector(self):
        """

        """
        if isinstance(self._dynamical_eigenvector, list):
            self._dynamical_eigenvector = np.array(self._dynamical_eigenvector, dtype=np.float64)
            return self._dynamical_eigenvector
        else:
            return self._dynamical_eigenvector

    @property
    def dynamical_eigenvector_diff(self):
        """

        """
        if isinstance(self._dynamical_eigenvector_diff, list):
            self._dynamical_eigenvector_diff = np.array(self._dynamical_eigenvector_diff, dtype=np.float64)
            return self._dynamical_eigenvector_diff
        else:
            return self._dynamical_eigenvector_diff

    @property
    def dynamical_eigenvector(self):
        """

        """
        if isinstance(self._dynamical_eigenvector, list):
            self._dynamical_eigenvector = np.array(self._dynamical_eigenvector, dtype=np.float64)
            return self._dynamical_eigenvector
        else:
            return self._dynamical_eigenvector

    @property
    def dynamical_eigenvector_diff_fractional(self):
        """

        """
        if isinstance(self._dynamical_eigenvector_diff_fractional, list):
            self._dynamical_eigenvector_diff_fractional = np.array(self._dynamical_eigenvector_diff_fractional, dtype=np.float64)
            return self._dynamical_eigenvector_diff_fractional
        else:
            return self._dynamical_eigenvector_diff_fractional

    # ======================================================
    #   ---  Descriptive metadata  -------------------------
    # ======================================================

    @property
    def comment(self) -> str:
        """
        Free-form text attached to the structure, e.g. an
        experimental note or a short description.

        Returns
        -------
        str or None
            The comment string if it exists, otherwise ``None``.
        """
        return self._comment

    @comment.setter
    def comment(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("comment must be a string or None.")
        self._comment = value


    # ======================================================
    #   ---  Energetics  -----------------------------------
    # ======================================================

    @property
    def E(self) -> float | None:
        """
        Total (electronic + nuclear) energy of the structure.

        Units
        -----
        Whatever internal unit system you are using
        (e.g. eV, Ha, …).

        Returns
        -------
        float or None
            Total energy, or ``None`` if it has not been set.
        """
        return self._E

    @E.setter
    def E(self, value: float | None) -> None:
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError("E must be a number (int or float) or None.")
        self._E = float(value) if value is not None else None


    @property
    def Edisp(self) -> float | None:
        """
        Dispersion (e.g. D3, MBD, etc.) correction energy.

        Returns
        -------
        float or None
        """
        return self._Edisp

    @Edisp.setter
    def Edisp(self, value: float | None) -> None:
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError("Edisp must be a number (int or float) or None.")
        self._Edisp = float(value) if value is not None else None


    # ======================================================
    #   ---  Charges & magnetisation  ----------------------
    # ======================================================

    @property
    def totalCharge(self) -> float | None:
        """
        Net charge of the simulation cell.

        Returns
        -------
        float or None
        """
        return self._total_charge

    @totalCharge.setter
    def totalCharge(self, value: float | None) -> None:
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError("totalCharge must be numeric or None.")
        self._total_charge = float(value) if value is not None else None


    @property
    def charge(self) -> np.ndarray | None:
        """
        Per-atom partial charges.

        Returns
        -------
        numpy.ndarray(N,) or None
            A 1-D array with one entry per atom, or ``None`` if not set.
        """
        if isinstance(self._charge, list):
            self._charge = np.asarray(self._charge, dtype=np.float64)
        return self._charge

    @charge.setter
    def charge(self, values: np.ndarray | list | None) -> None:
        if values is None:
            self._charge = None
            return
        arr = np.asarray(values, dtype=np.float64)
        if arr.ndim != 1 or (self.atomCount and arr.size != self.atomCount):
            raise ValueError("charge array must be 1-D and match atomCount.")
        self._charge = arr


    @property
    def magnetization(self) -> float | None:
        """
        Total magnetic moment of the cell.

        Returns
        -------
        float or None
        """
        return self._magnetization

    @magnetization.setter
    def magnetization(self, value: float | None) -> None:
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError("magnetization must be numeric or None.")
        self._magnetization = float(value) if value is not None else None


    # ======================================================
    #   ---  Forces  ---------------------------------------
    # ======================================================

    @property
    def totalForce(self) -> np.ndarray | None:
        """
        Vectorial sum of all forces acting on the atoms.

        Returns
        -------
        numpy.ndarray(3,) or None
            A 3-component vector (Fx, Fy, Fz), or ``None``.
        """
        if isinstance(self._total_force, list):
            self._total_force = np.asarray(self._total_force, dtype=np.float64)
        return self._total_force

    @totalForce.setter
    def totalForce(self, value: np.ndarray | list | None) -> None:
        if value is None:
            self._total_force = None
            return
        arr = np.asarray(value, dtype=np.float64)
        if arr.shape != (3,):
            raise ValueError("totalForce must be a 3-component vector.")
        self._total_force = arr


    @property
    def force(self) -> np.ndarray | None:
        """
        Per-atom forces.

        Returns
        -------
        numpy.ndarray(N,3) or None
            A 2-D array with one (Fx, Fy, Fz) row per atom,
            or ``None`` if not set.
        """
        if isinstance(self._force, list):
            self._force = np.asarray(self._force, dtype=np.float64)
        return self._force

    @force.setter
    def force(self, values: np.ndarray | list | None) -> None:
        if values is None:
            self._force = None
            return
        arr = np.asarray(values, dtype=np.float64)
        if arr.ndim != 2 or arr.shape[1] != 3:
            raise ValueError("force array must have shape (N,3).")
        if self.atomCount and arr.shape[0] != self.atomCount:
            raise ValueError("force array must match atomCount.")
        self._force = arr


    # ======================================================
    #   ---  Dynamical matrix results  ---------------------
    # ======================================================

    @property
    def dynamical_eigenvalues_fractional(self) -> np.ndarray | None:
        """
        Eigen-values of the dynamical matrix expressed in fractional
        coordinates (if available).

        Returns
        -------
        numpy.ndarray(N,) or None
        """
        if isinstance(self._dynamical_eigenvalues_fractional, list):
            self._dynamical_eigenvalues_fractional = np.asarray(
                self._dynamical_eigenvalues_fractional, dtype=np.float64
            )
        return self._dynamical_eigenvalues_fractional

    @dynamical_eigenvalues_fractional.setter
    def dynamical_eigenvalues_fractional(self, values: np.ndarray | list | None) -> None:
        if values is None:
            self._dynamical_eigenvalues_fractional = None
            return
        arr = np.asarray(values, dtype=np.float64)
        self._dynamical_eigenvalues_fractional = arr


    # ======================================================
    #   ---  Miscellaneous helpers  ------------------------
    # ======================================================

    @property
    def atomPositionsTolerance(self) -> float:
        """
        Numerical tolerance (Å) used when comparing two sets of
        Cartesian positions.

        Returns
        -------
        float
        """
        return float(self._atomPositions_tolerance)

    @atomPositionsTolerance.setter
    def atomPositionsTolerance(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("atomPositionsTolerance must be numeric.")
        if value <= 0:
            raise ValueError("atomPositionsTolerance must be positive.")
        self._atomPositions_tolerance = float(value)



    def get_atomic_numbers(self, ):
        return np.array( [self.atomic_numbers[n] for n in self.atomLabelsList] )

    def get_atomic_labels(self, ):
        return self.atomLabelsList

    def get_cell(self, ):
        return self.la

    def get_MBTR_representation(self, grid:int=500, get_dev:bool=True):
        try:
            from ...descriptor import MBTR
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing sage_lib.IO.descriptor.MBTR: {str(e)}\n")
            del sys

        md = MBTR.MDTR( lattice_vectors =   self.latticeVectors, 
                        atomLabelsList  =   self.atomLabelsList, 
                        atomPositions   =   self.atomPositions , )

        self._MBTR_representation, self._MBTR_representation_dev = md.get_mdtr()
        self._MBTR = md

        if get_dev:
            return self.MBTR_representation, self.MBTR_representation_dev
        else:
            return self.MBTR_representation

    def get_similarity_matrix(self, MBTR:object=None):
        MBTR = self.MBTR if MBTR is None else MBTR 
        if self.MBTR_representation_dev == None:
            self.get_MBTR_representation()

        self._similarity_matrix = MBTR.get_selfsimilarity_matrix( (np.sum( self.MBTR_representation_dev[0,:,:,:]**2, axis=2)**0.5).T)
        
        return self._similarity_matrix

    def find_related_atoms_groups(self, metric='kdtree'):

        if metric == 'metric':
            self._graph_representation = MBTR.find_related_atoms_groups(self.similarity_matrix, threshold=0.82)
        elif metric == 'kdtree':
            self._graph_representation = self.get_molecular_graph(sigma=1.0, metric='kdtree')

        return self._graph_representation


    def get_species_count(self, species:str=None) -> int:
        """
        Returns the number of atoms for the given chemical species.
        
        If the count for the species has already been computed, it is retrieved
        from a cache. Otherwise, the method counts the occurrences in self.atomLabelsList,
        stores the result in the cache, and returns it.
        
        Parameters
        ----------
        species : str
            The chemical species (e.g. 'Fe', 'H', etc.)
            
        Returns
        -------
        int
            The count of atoms of the given species, or 0 if none exist.
        """
        # Initialize the cache if it doesn't exist
        if hasattr(self, '_atomCountDict'):
            if type(species) == None:
                return self.atomCountDict
            elif type(species) == int:
                return self.atomCountDict[ self.atomic_name(species) ]
            else:
                return self.atomCountDict[ species ]
        
        else:
            self.atomCountDict = {}  
            for ual in self._uniqueAtomLabels:
                try:
                    labels = self.atomLabelsList
                except AttributeError:
                    labels = []
                
                self.atomCountDict[ual] = int(np.count_nonzero(np.array(labels) == species))

            if type(species) == None:
                return self.atomCountDict
            elif type(species) == int:
                return self.atomCountDict[ self.atomic_name(species) ]
            else:
                return self.atomCountDict[ species ]


    def get_species_count(self, species=None):
        """
        Retrieve the number of atoms corresponding to a given chemical species (string)
        or atomic index (integer). If no species is specified (None), return the entire
        dictionary of cached species counts.

        This method maintains a cache (`_atomCountDict`) to store the counts for each
        unique species label found in `self.atomLabelsList`. If this cache does not
        exist yet, it is built by counting the occurrences of each unique label. Once
        built, subsequent lookups for a given species are efficient.

        Parameters
        ----------
        species : str, int, or None, optional
            - If ``None``, the method returns the entire dictionary of species counts.
            - If a string, it should be a valid chemical symbol (e.g., "Fe", "H", etc.).
            - If an integer, it is interpreted as an atomic index or number; in this case,
              the method will attempt to convert it to a corresponding species label via
              ``self.atomic_name(species)``.

        Returns
        -------
        int or dict
            - If ``species`` is ``None``, returns a dictionary mapping each species label
              to its respective atom count.
            - Otherwise, returns an integer count of the specified species. If the species
              label is not present in the cache (i.e., does not exist in the structure),
              the method returns ``0``.
        """
        # Ensure the cache dictionary exists; if not, build it
        if not hasattr(self, '_atomCountDict'):
            self._atomCountDict = {}
            # Iterate through each unique atom label to count its occurrences in atomLabelsList
            for unique_label in getattr(self, '_uniqueAtomLabels', []):
                # Use built-in list.count() for a straightforward occurrence count
                self._atomCountDict[unique_label] = self.atomLabelsList.count(unique_label)

        # If no specific species is provided, return the entire cache dictionary
        if species is None:
            return self.atomCountDict

        # If species is an integer, convert it to its corresponding label
        if isinstance(species, int):
            species_label = self.atomic_name(species)
            return self.atomCountDict.get(species_label, 0)

        # Otherwise, species is assumed to be a string representing a chemical label
        return self.atomCountDict.get(species, 0)

    '''
    def calculate_rms_displacement_in_angstrom(atomic_mass_amu, temperature, frequency_au=1.0):
        """
        Calculate the root-mean-square displacement of an atom in a harmonic potential in Ångströms.

        Parameters:
        atomic_mass_amu (float): Atomic mass of the element in atomic mass units (amu).
        temperature (float): Temperature in Kelvin.
        frequency_au (float): Vibrational frequency in atomic units (default is 1.0).

        Returns:
        float: RMS displacement in Ångströms.
        """
        # Constants in atomic units
        k_B_au = 3.1668114e-6  # Boltzmann constant in hartree/Kelvin
        amu_to_au = 1822.888486209  # Conversion from amu to atomic units of mass
        bohr_to_angstrom = 0.529177  # Conversion from Bohr radius to Ångströms

        # Convert mass from amu to atomic units
        mass_au = atomic_mass_amu * amu_to_au

        # Force constant in atomic units
        k_au = mass_au * frequency_au**2

        # RMS displacement in atomic units
        sigma_au = np.sqrt(k_B_au * temperature / k_au)

        # Convert RMS displacement to Ångströms
        sigma_angstrom = sigma_au * bohr_to_angstrom
        
        return sigma_angstrom
        '''
