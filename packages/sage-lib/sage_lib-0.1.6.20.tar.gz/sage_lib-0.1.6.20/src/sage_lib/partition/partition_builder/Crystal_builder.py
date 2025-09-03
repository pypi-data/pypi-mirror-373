import math
import numpy as np
from typing import Dict, List, Sequence, Tuple
from scipy.spatial import Voronoi
from collections.abc import Iterable
from collections import Counter
try:
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class Crystal_builder(BasePartition):
    """
    A class for generating crystalline structures.

    This class provides methods to generate various types of crystal cells,
    including but not limited to cubic, face-centered cubic (FCC), body-centered
    cubic (BCC), tetragonal, body-centered tetragonal (BCT), orthorhombic,
    hexagonal, rhombohedral, monoclinic, triclinic as well as 2D lattices such as
    square, rectangular, oblique, and hexagonal (2D). The lattice vectors and atomic
    positions are computed based on the selected lattice type and provided parameters.
    The resulting structure is used to populate the AtomPositionManager attributes
    within a container.

    Attributes
    ----------
    lattice_type : str
        Identifier for the crystal lattice type (e.g. 'cubic', 'fcc', 'bcc',
        'tetragonal', 'bct', 'orthorhombic', 'hexagonal', 'rhombohedral',
        'monoclinic', 'triclinic', 'square2d', 'rectangular2d', 'oblique2d', 'hexagonal2d').
    lattice_parameters : dict
        Dictionary holding the parameters specific to the chosen lattice type.
    atom_positions : numpy.ndarray
        Array containing the atomic positions within the unit cell.
    lattice_vectors : numpy.ndarray
        3x3 array representing the lattice vectors.
    atom_labels : list
        List of atom labels for each atom in the structure.
    atom_count : int
        Total number of atoms in the unit cell.
    pbc : list
        Periodic boundary conditions in each direction (typically [True, True, True]).

    Methods
    -------
    set_lattice_type(lattice_type: str, **params)
        Set the lattice type and its required parameters.
    generate_lattice_vectors()
        Compute the lattice vectors based on the chosen lattice type.
    generate_atom_positions(atom_label: str = 'H')
        Generate the atomic positions for the cell.
    build_crystal(lattice_type: str, lattice_parameters: dict)
        Build the complete crystal structure and populate the AtomPositionManager.
    """
    SUPPORTED_LATTICES: Tuple[str, ...] = (
        "cubic", "fcc", "bcc",
        "tetragonal", "bct",
        "orthorhombic", "hexagonal",
        "rhombohedral", "monoclinic", "triclinic",
        #"square2d", "rectangular2d", "oblique2d", "hexagonal2d",
    )

    def __init__(self, *args, **kwargs):
        """
        """

        # Initialize lattice-related attributes with default values
        self.lattice_type = None
        self.lattice_parameters = {}
        self.atom_positions = None
        self.lattice_vectors = None
        self.atom_labels = []
        self.atom_count = 0
        self.pbc = [True, True, True]
        self._primitive_basis_cart: np.ndarray | None = None  # new
        
        self.hex_c_over_a = 1.633  # ideal HCP ratio; used by hexagonal branch

        super().__init__(*args, **kwargs)
    
    # ==================================================================
    #  Helpers – geometry & hashing
    # ==================================================================
    @staticmethod
    def _structure_signature(cart: np.ndarray, *, decimals: int = 3) -> Tuple[float, ...]:
        """Order‑independent tuple of rounded pairwise distances."""
        n = len(cart)
        dists: List[float] = []
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(cart[i] - cart[j])
                dists.append(round(d, decimals))
        return tuple(sorted(dists))

    def _dist_pbc(self, p: np.ndarray, q: np.ndarray, min_distance: float) -> bool:
        """Return *True* if ‖p−q‖ (Cartesian, PBC‑aware) > *min_distance*."""
        d = p - q
        d -= np.rint(d)  # wrap into [-0.5, 0.5]
        cart = d @ self.lattice_vectors
        return np.linalg.norm(cart) > min_distance

    def _unique_rows(self, arr: np.ndarray, tol: float = 1e-6) -> np.ndarray:
        out: List[np.ndarray] = []
        for r in arr:
            if not any(np.allclose(r, x, atol=tol) for x in out):
                out.append(r)
        return np.asarray(out)

    # ==================================================================
    #  Volume-per-atom helpers (new)
    # ==================================================================
    def _packing_fraction_default(self, lt: str) -> float:
        """Close-packing fraction φ* used to convert sphere volumes → per-atom cell volume."""
        lt = lt.lower()
        if lt in {"fcc"}:
            return 0.74048        # FCC
        if lt in {"hexagonal", "hcp"}:
            return 0.74048        # HCP (ideal c/a)
        if lt in {"bcc", "bct"}:
            return 0.68017        # BCC/BCT
        if lt in {"cubic", "sc", "tetragonal", "orthorhombic"}:
            return math.pi / 6.0  # ≈ 0.5236 (simple cubic baseline)
        # Rhombohedral/Monoclinic/Triclinic vary with angles; keep a conservative default
        return 0.60

    def _mean_atomic_sphere_volume(self, species: Sequence[str]) -> float:
        """Average per-atom sphere volume from covalent radii."""
        vols = [(4.0/3.0) * math.pi * (self.covalent_radii[s] ** 3) for s in species]
        return float(np.mean(vols))

    def _cell_volume_per_atom(self, species: Sequence[str], lt: str, packing: float) -> float:
        """Target per-atom cell volume: V* = (⟨V_sphere⟩ / φ*) × packing."""
        phi = self._packing_fraction_default(lt)
        return (self._mean_atomic_sphere_volume(species) / phi) * float(packing)

    def _a_from_target_volume(self, lt: str, V_atom: float, angles: Tuple[float, float, float]) -> float:
        """Solve for length 'a' such that det(L(a,angles)) == V_atom (one atom / primitive cell)."""
        alpha, beta, gamma = angles

        # Build the lattice with a=1 to measure the geometric factor F = det(L(a=1))
        backup_lv = None if self.lattice_vectors is None else self.lattice_vectors.copy()
        self._prepare_lattice(lt, 1.0, alpha, beta, gamma)
        F = abs(np.linalg.det(self.lattice_vectors))
        if backup_lv is not None:
            self.lattice_vectors = backup_lv
        if F <= 0:
            raise RuntimeError(f"Degenerate lattice for {lt} with angles={angles}: det=0")

        # Volume scales as a^3 for all branches defined in _prepare_lattice
        return (V_atom / F) ** (1.0 / 3.0)

    def set_lattice_type(self, lattice_type: str, **params):
        """
        Set the lattice type and its associated parameters.

        Parameters
        ----------
        lattice_type : str
            Identifier for the crystal lattice type. Supported types include:
            'cubic', 'fcc', 'bcc', 'tetragonal'.
        **params
            Lattice-specific parameters. For example, for a cubic lattice provide 'a',
            for a tetragonal cell provide 'a' and 'c', etc.
        """
        self.lattice_type = lattice_type.lower()
        self.lattice_parameters = params

    def generate_lattice_vectors(self):
        """
        Compute lattice vectors based on the selected lattice type and parameters.

        Returns
        -------
        numpy.ndarray
            A 3x3 array containing the lattice vectors.

        Raises
        ------
        ValueError
            If the lattice type is not set or required parameters are missing.
        """
        if self.lattice_type is None:
            raise ValueError("Lattice type not set. Use set_lattice_type() first.")

        lp = self.lattice_parameters  # shorthand
        # 3D lattices
        if self.lattice_type == 'cubic':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for cubic lattice.")
            self.lattice_vectors = a * np.eye(3)

        elif self.lattice_type == 'fcc':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for FCC lattice.")
            self.lattice_vectors = 0.5 * np.array([[0, a, a],
                                                    [a, 0, a],
                                                    [a, a, 0]])

        elif self.lattice_type == 'bcc':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for BCC lattice.")
            self.lattice_vectors = 0.5 * np.array([[-a, a, a],
                                                    [a, -a, a],
                                                    [a, a, -a]])

        elif self.lattice_type == 'tetragonal':
            try:
                a = float(lp['a'])
                c = float(lp['c'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'c' must be provided for tetragonal lattice.")
            self.lattice_vectors = np.diag([a, a, c])

        elif self.lattice_type == 'bct':
            try:
                a = float(lp['a'])
                c = float(lp['c'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'c' must be provided for body-centered tetragonal lattice.")
            # Primitive cell for body-centered tetragonal (analogous to BCC with tetragonal distortion)
            self.lattice_vectors = 0.5 * np.array([[ a,  a,  c],
                                                    [-a,  a,  c],
                                                    [ a, -a,  c]])

        elif self.lattice_type == 'orthorhombic':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
                c = float(lp['c'])
            except KeyError:
                raise ValueError("Parameters 'a', 'b', and 'c' must be provided for orthorhombic lattice.")
            self.lattice_vectors = np.diag([a, b, c])

        elif self.lattice_type == 'hexagonal':
            try:
                a = float(lp['a'])
                c = float(lp['c'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'c' must be provided for hexagonal lattice.")
            self.lattice_vectors = np.array([[ a,        0, 0],
                                             [-a/2, a*np.sqrt(3)/2, 0],
                                             [ 0,        0, c]])

        elif self.lattice_type == 'rhombohedral':
            try:
                a = float(lp['a'])
                alpha = float(lp['alpha'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'alpha' must be provided for rhombohedral lattice.")
            alpha_rad = np.deg2rad(alpha)
            v1 = np.array([a, 0, 0])
            v2 = np.array([a * np.cos(alpha_rad), a * np.sin(alpha_rad), 0])
            # A common representation for a rhombohedral cell:
            # v3 is defined so that the angle between any two vectors equals alpha.
            v3_x = a * np.cos(alpha_rad)
            # Using an equivalent formulation: v3_y = a*(1 - cos(alpha))/tan(alpha)
            v3_y = a * (1 - np.cos(alpha_rad)) / np.tan(alpha_rad) if np.tan(alpha_rad) != 0 else 0
            v3_z = a * np.sqrt(1 - 3*np.cos(alpha_rad)**2 + 2*np.cos(alpha_rad)**3)
            v3 = np.array([v3_x, v3_y, v3_z])
            self.lattice_vectors = np.array([v1, v2, v3])

        elif self.lattice_type == 'monoclinic':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
                c = float(lp['c'])
                beta = float(lp['beta'])
            except KeyError:
                raise ValueError("Parameters 'a', 'b', 'c', and 'beta' must be provided for monoclinic lattice.")
            beta_rad = np.deg2rad(beta)
            v1 = np.array([a, 0, 0])
            v2 = np.array([0, b, 0])
            v3 = np.array([c * np.cos(beta_rad), 0, c * np.sin(beta_rad)])
            self.lattice_vectors = np.array([v1, v2, v3])

        elif self.lattice_type == 'triclinic':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
                c = float(lp['c'])
                alpha = float(lp['alpha'])
                beta  = float(lp['beta'])
                gamma = float(lp['gamma'])
            except KeyError:
                raise ValueError("Parameters 'a', 'b', 'c', 'alpha', 'beta', and 'gamma' must be provided for triclinic lattice.")
            alpha_rad = np.deg2rad(alpha)
            beta_rad  = np.deg2rad(beta)
            gamma_rad = np.deg2rad(gamma)
            v1 = np.array([a, 0, 0])
            v2 = np.array([b * np.cos(gamma_rad), b * np.sin(gamma_rad), 0])
            v3_x = c * np.cos(beta_rad)
            v3_y = c * (np.cos(alpha_rad) - np.cos(beta_rad) * np.cos(gamma_rad)) / np.sin(gamma_rad)
            term = 1 - np.cos(beta_rad)**2 - ((np.cos(alpha_rad) - np.cos(beta_rad)*np.cos(gamma_rad)) / np.sin(gamma_rad))**2
            if term < 0:
                term = 0
            v3_z = c * np.sqrt(term)
            v3 = np.array([v3_x, v3_y, v3_z])
            self.lattice_vectors = np.array([v1, v2, v3])

        # 2D lattices (assume the third row is zero)
        elif self.lattice_type == 'square2d':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for square2d lattice.")
            self.lattice_vectors = np.array([[a, 0, 0],
                                             [0, a, 0],
                                             [0, 0, 0]])
        elif self.lattice_type == 'rectangular2d':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'b' must be provided for rectangular2d lattice.")
            self.lattice_vectors = np.array([[a, 0, 0],
                                             [0, b, 0],
                                             [0, 0, 0]])
        elif self.lattice_type == 'oblique2d':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
                gamma = float(lp['gamma'])
            except KeyError:
                raise ValueError("Parameters 'a', 'b', and 'gamma' must be provided for oblique2d lattice.")
            gamma_rad = np.deg2rad(gamma)
            self.lattice_vectors = np.array([[a, 0, 0],
                                             [b * np.cos(gamma_rad), b * np.sin(gamma_rad), 0],
                                             [0, 0, 0]])
        elif self.lattice_type == 'hexagonal2d':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for hexagonal2d lattice.")
            self.lattice_vectors = np.array([[a, 0, 0],
                                             [a/2, a*np.sqrt(3)/2, 0],
                                             [0, 0, 0]])
        else:
            raise ValueError(f"Lattice type '{self.lattice_type}' not supported.")

        return self.lattice_vectors

    def generate_atom_positions(self, atom_label: str = 'X'):
        """
        Generate atomic positions for the unit cell based on the lattice type.

        Returns
        -------
        numpy.ndarray
            An array of atomic positions.

        Notes
        -----
        For primitive cells a single atom is placed at the origin. For lattices with a basis,
        such as FCC, BCC, and BCT, multiple atomic positions are provided. In 2D systems the z-coordinate
        is set to zero.
        """
        if self.lattice_type is None:
            raise ValueError("Lattice type not set. Use set_lattice_type() first.")

        # Ensure lattice vectors are generated
        if self.lattice_vectors is None:
            self.generate_lattice_vectors()

        lt = self.lattice_type

        if lt == "cubic":
            basis_frac = np.array([[0.0, 0.0, 0.0]])
        elif lt == "fcc":
            basis_frac = np.array([
                [0.0, 0.0, 0.0],
                [0.0, 0.5, 0.5],
                [0.5, 0.0, 0.5],
                [0.5, 0.5, 0.0],
            ])
        elif lt == "bcc":
            basis_frac = np.array([
                [0.0, 0.0, 0.0],
                [0.5, 0.5, 0.5],
            ])
        elif lt == "bct":
            basis_frac = np.array([
                [0.0, 0.0, 0.0],
                [0.5, 0.5, 0.5],
            ])
        elif lt in (
            "tetragonal",
            "orthorhombic",
            "hexagonal",
            "rhombohedral",
            "monoclinic",
            "triclinic",
        ):
            basis_frac = np.array([[0.0, 0.0, 0.0]])
        # -------- 2D lattices (z = 0) ----------------------------------
        elif lt == "square2d":
            basis_frac = np.array([[0.0, 0.0, 0.0]])
        elif lt == "rectangular2d":
            basis_frac = np.array([[0.0, 0.0, 0.0]])
        elif lt == "oblique2d":
            basis_frac = np.array([[0.0, 0.0, 0.0]])
        elif lt == "hexagonal2d":
            basis_frac = np.array([
                [0.0, 0.0, 0.0],
                [2.0 / 3.0, 1.0 / 3.0, 0.0],
            ])
        else:
            raise ValueError(f"Atom positions for lattice '{lt}' not implemented.")

        # Cartesian positions
        self._primitive_basis_cart = basis_frac @ self.lattice_vectors
        self.atom_positions = self._primitive_basis_cart.copy()
        self.atom_labels = [atom_label] * len(self.atom_positions)
        self.atom_count = len(self.atom_positions)
        return self.atom_positions

    def build_crystal(self, lattice_type:str='fcc', lattice_parameters:dict={'a':1}, atom_label:str='H'):
        """
        Build the crystal structure and populate the AtomPositionManager attributes.

        This method calculates the lattice vectors and atomic positions using the
        specified lattice type and parameters. The generated structure data can then
        be assigned to the container's AtomPositionManager.

        Returns
        -------
        dict
            A dictionary with keys:
            - 'atomCount': number of atoms in the cell.
            - 'atomPositions': numpy array of atomic positions.
            - 'atomLabelsList': list of atomic labels.
            - 'latticeVectors': 3x3 array of lattice vectors.
            - 'pbc': periodic boundary conditions list.
        
        Example
        -------
        >>> container = SingleRun('')
        >>> cpb = Crystal_builder()
        >>> cpb.set_lattice_type('fcc', a=4.0)
        >>> structure = cpb.build_crystal()
        >>> container.AtomPositionManager.atomCount = structure['atomCount']
        >>> container.AtomPositionManager.atomPositions = structure['atomPositions']
        >>> container.AtomPositionManager.atomLabelsList = structure['atomLabelsList']
        >>> container.AtomPositionManager.latticeVectors = structure['latticeVectors']
        >>> container.AtomPositionManager.pbc = structure['pbc']
        >>> self.add_container(container)
        """

        container = self.add_empty_container()
        lattice_parameters = lattice_parameters or {"a": 1.0}

        self.set_lattice_type(lattice_type, 
            a=lattice_parameters.get('a', 0), 
            b=lattice_parameters.get('b', 0), 
            c=lattice_parameters.get('c', 0),
            alpha=lattice_parameters.get('alpha', 0),
            beta=lattice_parameters.get('beta', 0),
            gamma=lattice_parameters.get('gamma', 0) )

        self.generate_lattice_vectors()
        self.generate_atom_positions(atom_label=atom_label)

        structure_data = {
            'atomCount': self.atom_count,
            'atomPositions': self.atom_positions,
            'atomLabelsList': self.atom_labels,
            'latticeVectors': self.lattice_vectors,
            'pbc': self.pbc
        }   

        container.AtomPositionManager.set_latticeVectors( structure_data['latticeVectors'] )
        container.AtomPositionManager.add_atom(structure_data['atomLabelsList'], structure_data['atomPositions'])
        self.add_container(container)

        return container

    # ------------------------------------------------------------------
    #  Public API – single cell via Voronoi
    # ------------------------------------------------------------------
    def build_crystal_voronoi(
        self,
        lattice_type: str,
        species: List[str],
        packing: float = 1.15,   # tighter default recommended
        pad: int = 1,
    ):
        angles = (90.0, 90.0, 90.0)
        V_atom = self._cell_volume_per_atom(species, lattice_type, packing)
        a_len  = self._a_from_target_volume(lattice_type, V_atom, angles)
        self._prepare_lattice(lattice_type, a_len, *angles)

        sites_frac = self._voronoi_vertices(pad)
        cart = self._select_sites_cartesian(sites_frac, len(species))
        return self._populate_container(species, cart)

    # ------------------------------------------------------------------
    #  Public API – recursive list (k = 1 … N)
    # ------------------------------------------------------------------
    def build_all_voronoi_cells(
        self,
        lattice_type: str,
        species_list: List[str],
        packing: float = 1.15,   # tighter default recommended
        pad: int = 1,
    ) -> Dict[int, "BasePartition"]:
        N = len(species_list)
        angles = (90.0, 90.0, 90.0)
        V_atom = self._cell_volume_per_atom(species_list, lattice_type, packing)
        a_len  = self._a_from_target_volume(lattice_type, V_atom, angles)
        self._prepare_lattice(lattice_type, a_len, *angles)

        sites_frac = self._voronoi_vertices(pad)
        result: Dict[int, BasePartition] = {}

        def _recurse(k: int):
            if k == 0:
                return
            cart = self._select_sites_cartesian(sites_frac, k)
            cont = self._populate_container(species_list[:k], cart)
            result[k] = cont
            _recurse(k - 1)

        _recurse(N)
        return result

    # ==================================================================
    #  Public API – exhaustive enumeration with duplicate culling
    # ==================================================================
    def build_all_crystals(
        self,
        species_list: List[str],
        packing: float = 2.25,
        pad: int = 1,
        angle_delta: float = 0.0,
        *,
        min_distance: float = 1e-3,
        dedup_tol: float = 1e-1,
        max_vertices: int | None = 2,
        max_structures: int | None = None,
    ) -> Dict[Tuple[str, int, Tuple[float, float, float], int], "BasePartition"]:
        """See original doc‑string; new keyword‑only knobs described below.

        | Parameter            | Type / Unit | Default | Meaning                                                                                                                                                                                                               |                                                                                                                                                          |
        | -------------------- | ----------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
        | **`species_list`**   | `list[str]` | –       | Multiset of chemical symbols to distribute (e.g. `['Fe','O','O']`). Every permutation is explored.                                                                                                                    |                                                                                                                                                          |
        | **`packing`**        | `float`     | `1.25`  | Safety factor applied to the *isotropic* cell length `a = packing × Σ(2 rᵢ)` where `rᵢ` are the covalent radii of the atoms already placed. Larger values ⇒ more spacious cells.                                      |                                                                                                                                                          |
        | **`pad`**            | `int`       | `1`     | How far the periodic image grid extends (± *pad* replicas in each lattice direction) when computing Voronoi vertices.                                                                                                 |                                                                                                                                                          |
        | **`angle_delta`**    | `float` (°) | `0.0`   | Generates a small grid of cell angles around 90°. If 0 ⇒ only (90, 90, 90). If *d* > 0 ⇒ Cartesian product (90 ± *d*)³ (max 27 angle triplets).                                                                       |                                                                                                                                                          |
        | **`min_distance`**   | `float` (Å) | `1e-3`  | Hard lower bound for every *Cartesian* pairwise separation. A default of 0.001 Å is practically “disabled”, preserving legacy behaviour unless you specify a larger value.                                            |                                                                                                                                                          |
        | **`dedup_tol`**      | `float` (Å) | `1e-3`  | Resolution used when rounding the inter-atomic distances that form the **structure signature**. Two signatures identical to this tolerance are deemed geometrically equivalent and the second structure is discarded. |                                                                                                                                                          |
        | **`max_vertices`**   | `int       | None`  | `2`                                                                                                                                                                                                                   | Optional cap on the number of Voronoi vertices tested **per insertion step**. `None` keeps all vertices; a small integer throttles the branching factor. |
        | **`max_structures`** | `int       | None`  | `None`                                                                                                                                                                                                                | Global ceiling on the number of *accepted, unique* structures. When the limit is reached the search terminates immediately.                              |

        Parameters (additions)
        ---------------------
        min_distance : float, default 1e‑3 Å
            Hard lower bound for every pairwise separation.
        dedup_tol : float, default 1e‑3 Å
            Tolerance used when rounding distances for duplicate removal.
        max_structures : int | None
            If given, stop once this many unique geometries have been accepted.
        """
        class _MaxReached(Exception):
            """Private sentinel raised when the hard ceiling is hit."""
            pass

        if not species_list:
            raise ValueError("species_list must contain at least one element.")

        # --------------- angle grid -----------------------------------
        if angle_delta <= 0.0:
            angle_grid = [(90.0, 90.0, 90.0)]
        else:
            offs = (-angle_delta, 0.0, angle_delta)
            angle_grid = [(90.0 + da, 90.0 + db, 90.0 + dc)
                          for da in offs for db in offs for dc in offs]

        # --------------- bookkeeping ----------------------------------
        result: Dict[Tuple[str, int, Tuple[float, float, float], int], BasePartition] = {}
        signatures: set[Tuple[float, ...]] = set()
        branch_id = 0
        decimals = max(0, int(round(-math.log10(dedup_tol)))) if dedup_tol > 0 else 3

        def register(cont: "BasePartition", cart: np.ndarray,
                      key: Tuple[str, int, Tuple[float, float, float], int]):
            sig = self._structure_signature(cart, decimals=decimals)
            if sig in signatures:
                return  # duplicate – ignore
            signatures.add(sig)
            result[key] = cont
            if max_structures is not None and len(result) >= max_structures:
                raise _MaxReached

        # --------------- DFS ------------------------------------------
        def dfs(atoms_frac: List[np.ndarray], remaining: Counter, labels_order: List[str],
                lt: str, angles: Tuple[float, float, float]):
            nonlocal branch_id
            depth = len(labels_order)

            if depth:  # store prefix
                cart = np.vstack(atoms_frac) @ self.lattice_vectors
                cont = self._populate_container(labels_order, cart)
                key = (lt, depth, angles, branch_id)
                register(cont, cart, key)

            if not remaining:
                branch_id += 1
                return

            for sp in list(remaining):
                remaining[sp] -= 1
                if remaining[sp] == 0:
                    del remaining[sp]

                new_labels = labels_order + [sp]
                alpha, beta, gamma = angles
                V_atom = self._cell_volume_per_atom(new_labels, lt, packing)
                a_len  = self._a_from_target_volume(lt, V_atom, angles)
                self._prepare_lattice(lt, a_len, alpha, beta, gamma)

                verts = (self._voronoi_vertices_atoms([], pad) if not atoms_frac
                         else self._voronoi_vertices_atoms(atoms_frac, pad))
                good = [v for v in verts if all(
                    self._dist_pbc(v, a, min_distance) for a in atoms_frac)]
                if max_vertices is not None:
                    good = good[:max_vertices]

                if not good:
                    branch_id += 1
                else:
                    for v in good:
                        dfs(atoms_frac + [v], remaining, new_labels, lt, angles)

                remaining[sp] += 1

        # --------------- outer loops -----------------------------------
        try:
            for angles in angle_grid:
                alpha, beta, gamma = angles  # not used directly but kept for clarity
                for lt in self.SUPPORTED_LATTICES:
                    dfs([], Counter(species_list), [], lt, angles)
        except _MaxReached:
            pass  # hard ceiling hit – silent exit

        return result



    # =====================================================================
    #  Internal helpers – geometry, lattice, etc.
    # =====================================================================
    def _largest_diameter(self, species: Sequence[str]) -> float:
        try:
            return 2.0 * max(self.covalent_radii[s] for s in species)
        except KeyError as exc:
            raise ValueError(
                f"Atomic radius for element '{exc.args[0]}' is missing in self._covalent_radii."
            )

    def _total_diameter(self, species: Sequence[str]) -> float:
        """Sum of *individual* diameters (2·r) – generous upper bound."""
        try:
            return sum(2.0 * self.covalent_radii[s] for s in species)
        except KeyError as exc:
            raise ValueError(f"Missing covalent radius for element {exc.args[0]}")

    def _compute_isotropic_size(self, species: Sequence[str], packing: float) -> float:
        return packing * self._total_diameter(species)

    # ------------------------------------------------------------------
    #  Geometry helpers – Voronoi
    # ------------------------------------------------------------------
    def _voronoi_vertices(self, pad: int = 1, *, joggle: bool = True) -> np.ndarray:
        """Return Voronoi‑vertex fractional coordinates of the Wigner–Seitz cell.

        Robust to numerical degeneracies:
        * Uses Qhull *QJ* joggle if needed.
        * Falls back to Moore–Penrose pseudo‑inverse if the lattice matrix is
          (nearly) singular (e.g. 2D lattices embedded in 3D).
        """
        if Voronoi is None:
            raise ModuleNotFoundError(
                "scipy is required for Voronoi‑based site generation – please install scipy"
            )

        rng = range(-pad, pad + 1)
        grid = np.array([[i, j, k] for i in rng for j in rng for k in rng], dtype=float)
        pts_cart = grid @ self.lattice_vectors
        try:
            v = Voronoi(pts_cart)
        except Exception:
            if not joggle:
                raise
            from scipy.spatial import Voronoi as _Voronoi
            v = _Voronoi(pts_cart, qhull_options="Qbb Qc Qx QJ")

        idx0 = len(pts_cart) // 2
        region_idx = v.point_region[idx0]
        vert_idx = v.regions[region_idx]
        if -1 in vert_idx:
            raise RuntimeError("Increase pad; Voronoi region unbounded.")
        verts_cart = v.vertices[vert_idx]
        inv_lv = np.linalg.pinv(self.lattice_vectors)  # robust
        verts_frac = (verts_cart @ inv_lv) % 1.0
        verts_frac = self._unique_rows(verts_frac)
        order = np.argsort(np.sum(verts_frac ** 2, axis=1))
        return verts_frac[order]

    # ---------------- Voronoi of current atoms ------------------------
    def _voronoi_vertices_atoms(self, atoms_frac: Sequence[np.ndarray], pad: int) -> List[np.ndarray]:
        # --- early exit: no atoms yet -> use bare lattice vertices
        if len(atoms_frac) == 0:
            return list(self._voronoi_vertices(pad))

        if Voronoi is None:
            raise ModuleNotFoundError("SciPy required for Voronoi tessellation")
        
        atoms_frac = np.asarray(atoms_frac, dtype=float).reshape(-1, 3)
        #atoms_frac = np.asarray(atoms_frac)
        translations = np.array([[i, j, k] for i in range(-pad, pad + 1)
                                           for j in range(-pad, pad + 1)
                                           for k in range(-pad, pad + 1)], float)
        tiled = atoms_frac[:, None, :] + translations[None, :, :]
        pts_cart = tiled.reshape(-1, 3) @ self.lattice_vectors

        # Voronoi computation with joggle fallback
        try:
            v = Voronoi(pts_cart)
        except Exception:
            from scipy.spatial import Voronoi as _Voronoi
            v = _Voronoi(pts_cart, qhull_options="Qbb Qc Qx QJ")

        verts_cart = v.vertices
        inv_lv = np.linalg.pinv(self.lattice_vectors)
        verts_frac = (verts_cart @ inv_lv) % 1.0
        # deduplicate rows
        unique: List[np.ndarray] = []
        for r in verts_frac:
            if not any(np.allclose(r, u, atol=1e-6) for u in unique):
                unique.append(r)
        return unique

    # ------------------------------------------------------------------
    #  Lattice preparation – currently only primitive cubic (sc) handled
    # ------------------------------------------------------------------
    def _prepare_lattice(self, lt: str, a: float, alpha: float, beta: float, gamma: float):
        lt = lt.lower()
        self.lattice_type = lt

        if lt in {"cubic", "sc"}:  # simple cubic
            self.lattice_vectors = a * np.eye(3)

        elif lt == "fcc":  # face‑centred cubic (primitive)
            self.lattice_vectors = 0.5 * a * np.array([
                [0, 1, 1],
                [1, 0, 1],
                [1, 1, 0],
            ])

        elif lt == "bcc":  # body‑centred cubic (primitive)
            self.lattice_vectors = 0.5 * a * np.array([
                [-1, 1, 1],
                [1, -1, 1],
                [1, 1, -1],
            ])

        elif lt == "tetragonal":  # a = b ≠ c
            c = a  # placeholder – could scale differently
            self.lattice_vectors = np.diag([a, a, c])

        elif lt == "bct":  # body‑centred tetragonal (primitive)
            c = a  # placeholder
            self.lattice_vectors = 0.5 * np.array([
                [ a,  a,  c],
                [-a,  a,  c],
                [ a, -a,  c],
            ])

        elif lt == "orthorhombic":
            b = c = a  # placeholders
            self.lattice_vectors = np.diag([a, b, c])

        elif lt == "hexagonal":
            # Allow ideal c/a unless overridden elsewhere
            c_over_a = getattr(self, "hex_c_over_a", 1.633)  # ideal ≈ sqrt(8/3)
            c = c_over_a * a
            self.lattice_vectors = np.array([
                [ a,        0, 0],
                [-a/2, a*np.sqrt(3)/2, 0],
                [ 0,        0, c],
            ])

        elif lt == "rhombohedral":
            alpha_rad = math.radians(alpha)
            self.lattice_vectors = a * np.array([
                [ 1,                                0,                              0],
                [ math.cos(alpha_rad), math.sin(alpha_rad),                          0],
                [ math.cos(alpha_rad), (math.cos(alpha_rad) - math.cos(alpha_rad)**2)/math.sin(alpha_rad) if abs(math.sin(alpha_rad))>1e-8 else 0,
                  math.sqrt(1 - 3*math.cos(alpha_rad)**2 + 2*math.cos(alpha_rad)**3) ],
            ])

        elif lt == "monoclinic":
            beta_rad = math.radians(beta)
            b = c = a
            self.lattice_vectors = np.array([
                [a, 0, 0],
                [0, b, 0],
                [c*math.cos(beta_rad), 0, c*math.sin(beta_rad)],
            ])

        elif lt == "triclinic":
            alpha_rad = math.radians(alpha)
            beta_rad  = math.radians(beta)
            gamma_rad = math.radians(gamma)
            b = c = a
            v1 = np.array([a, 0, 0])
            v2 = np.array([b*math.cos(gamma_rad), b*math.sin(gamma_rad), 0])
            v3_x = c*math.cos(beta_rad)
            v3_y = c*(math.cos(alpha_rad) - math.cos(beta_rad)*math.cos(gamma_rad)) / max(math.sin(gamma_rad), 1e-8)
            term = 1 - math.cos(beta_rad)**2 - ((math.cos(alpha_rad) - math.cos(beta_rad)*math.cos(gamma_rad)) / max(math.sin(gamma_rad),1e-8))**2
            v3_z = c*math.sqrt(max(term, 0))
            self.lattice_vectors = np.array([v1, v2, [v3_x, v3_y, v3_z]])

        else:
            raise NotImplementedError(f"Lattice '{lt}' not supported.")

        # Warn if user gave non‑90° angles for lattices that ignore them
        if lt in {"cubic", "sc", "fcc", "bcc", "tetragonal", "bct", "orthorhombic", "hexagonal"}:
            if any(abs(x - 90.0) > 1e-2 for x in (alpha, beta, gamma)):
                import warnings
                warnings.warn("Angles ignored for high‑symmetry lattice ‘%s’." % lt, RuntimeWarning)

    def set_lattice_type(self, lattice_type: str, **params):
        self.lattice_type = lattice_type.lower()
        self.lattice_parameters = params

    def _set_lattice_vectors_sc(self, a: float):
        self.lattice_type = "cubic"
        self.lattice_vectors = a * np.eye(3)

    # ------------------------------------------------------------------
    #  Minimal generate_atom_positions to satisfy legacy API (origin only)
    # ------------------------------------------------------------------
    #def generate_atom_positions(self, atom_label: str = "X"):
    #    basis_frac = np.array([[0.0, 0.0, 0.0]])
    #    self._primitive_basis_cart = basis_frac @ self.lattice_vectors
    #    return self._primitive_basis_cart

    # ------------------------------------------------------------------
    #  Container helpers
    # ------------------------------------------------------------------
    def _select_sites_cartesian(self, sites_frac: np.ndarray, k: int) -> np.ndarray:
        if k > len(sites_frac):
            reps = math.ceil(k / len(sites_frac))
            sites_frac = np.tile(sites_frac, (reps, 1))[:k]
        else:
            sites_frac = sites_frac[:k]
        return sites_frac @ self.lattice_vectors

    def _populate_container(self, labels: Sequence[str], positions_cart: np.ndarray):
        container = self.add_empty_container()
        container.AtomPositionManager.set_latticeVectors(self.lattice_vectors)
        container.AtomPositionManager.add_atom(labels, positions_cart)
        #self.add_container(container)
        return container
