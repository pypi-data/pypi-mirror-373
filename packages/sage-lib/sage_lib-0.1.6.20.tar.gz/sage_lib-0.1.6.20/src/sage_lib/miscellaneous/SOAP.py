import numpy as np
from scipy.special import gamma, sph_harm
from scipy.linalg import sqrtm, inv
from tqdm import tqdm

try:
    from numba import jit
    print("Numba is available; optimizations will be applied.")
except ImportError:
    print("Numba is not available; running without JIT optimizations.")
    

class SOAP:
    def __init__(
        self,
        species,
        periodic=False,
        r_cut=None,
        n_max=None,
        l_max=None,
        sigma=1.0,
        rbf="gto",
        weighting=None,
        average="off",
        compression={"mode": "off", "species_weighting": None},
        sparse=False,
        dtype="float64",
    ):
        self._atomic_numbers_dict = {
                'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
                'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29,
                'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43,
                'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50, 'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'Lu': 71,
                'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
                'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'U': 92, 'Np': 93, 'Pu': 94, 'X': 99
                                }

        self.species = species
        self.n_elements = len(species)

        self.periodic = periodic
        self._r_cut = float(r_cut)
        self._n_max = n_max
        self._l_max = l_max
        self._sigma = sigma
        self._eta = 1 / (2 * sigma**2)
        self._rbf = rbf
        self._weighting = weighting
        self.average = average
        self.compression = compression
        self.sparse = sparse
        self.dtype = dtype

        # Setup species-related attributes
        self._atomic_numbers = self._get_atomic_numbers(species)
        self._species_to_index = {s: i for i, s in enumerate(species)}
        self._index_to_species = {i: s for i, s in enumerate(species)}
        self.n_elements = len(species)

        # Calculate basis functions
        if self._rbf == "gto":
            self._alphas, self._betas = self.get_basis_gto(r_cut, n_max, l_max)
        elif self._rbf == "polynomial":
            self._rx, self._gss = self.get_basis_poly(r_cut, n_max)

    def _get_atomic_numbers(self, atom_labels):

        return np.array([self._atomic_numbers_dict[label] for label in atom_labels])

    def create(self, atoms):
        positions = atoms.AtomPositionManager._atomPositions
        unique_labels = atoms.AtomPositionManager._uniqueAtomLabels
        atomic_numbers = self._get_atomic_numbers(atoms.AtomPositionManager._atomLabelsList)
        cell = atoms.AtomPositionManager._latticeVectors
        pbc = self.periodic
        
        centers = positions
        n_centers = len(centers)
        n_features = self.get_number_of_features()
        soap_mat = np.zeros((n_centers, n_features), dtype=np.float64)
        
        print(f"soap_mat shape: {soap_mat.shape}")
        print(f"n_centers: {n_centers}, n_features: {n_features}")
        print(f"positions length: {len(positions)}")
        print(f"atomic_numbers length: { atomic_numbers.shape }")
        
        cutoff_padding = self.get_cutoff_padding()

        if self._rbf == "gto":
            alphas = self._alphas.flatten()
            betas = self._betas.flatten()
            self._create_gto(soap_mat, positions, atomic_numbers, cell, pbc, centers, alphas, betas, cutoff_padding, atoms)
        elif self._rbf == "polynomial":
            self._create_polynomial(soap_mat, positions, atomic_numbers, cell, pbc, centers, cutoff_padding)

        if self.average != "off":
            soap_mat = np.mean(soap_mat, axis=0)

        return soap_mat

    def _create_gto(self, soap_mat, positions, atomic_numbers, cell, pbc, centers, alphas, betas, cutoff_padding, atoms):
        n_atoms = len(positions)
        n_centers = len(centers)
        n_features = soap_mat.shape[1]
        
        for i_center in tqdm(range(n_centers), desc="Processing i_center"):
            center = centers[i_center]
            n_atoms_idx = atoms.AtomPositionManager.find_all_neighbors_radius(center, self._r_cut + cutoff_padding, p=2., eps=0)

            for i_atom_idx in n_atoms_idx:
                atom_pos = positions[i_atom_idx]
                atom_type = atomic_numbers[i_atom_idx]
                
                r_vec = atom_pos - center
                
                #if pbc:
                #    r_vec = r_vec - cell * np.round(r_vec / cell)

                r = np.linalg.norm(r_vec)
                
                if r < self._r_cut + cutoff_padding:
                    if r == 0:
                        continue  # Skip self-interaction
                    
                    cos_theta = r_vec[2] / r
                    theta = np.arccos(np.clip(cos_theta, -1.0, 1.0))
                    phi = np.arctan2(r_vec[1], r_vec[0])
                    
                    for n in range(self._n_max):
                        R_nl = np.exp(-alphas[n] * r**2) * r**self._l_max
                        for l in range(self._l_max + 1):
                            for m in range(-l, l+1):
                                Y_lm = sph_harm(m, l, phi, theta)
                                idx = self._get_feature_index(n, l, m, atom_type)
                                
                                
                                if idx >= n_features:
                                    print(f"Warning: idx {idx} is out of bounds for soap_mat with shape {soap_mat.shape}")
                                    continue
                                
                                # Handle Y_lm as an array
                                value = R_nl * np.mean(np.real(Y_lm))
                                
                                soap_mat[i_center, idx] += value

        # Normalize the SOAP vectors
        norms = np.linalg.norm(soap_mat, axis=1)
        norms[norms == 0] = 1.0  # Avoid division by zero
        soap_mat /= norms[:, np.newaxis]

    @staticmethod
    @jit(nopython=True)
    def calculate_R_nl(r, alphas, l_max):
        return np.exp(-alphas[np.newaxis, :] * r[:, np.newaxis]**2) * r[:, np.newaxis]**l_max

    def _create_gto(self, soap_mat, positions, atomic_numbers, cell, pbc, centers, alphas, betas, cutoff_padding, atoms):
        n_atoms = len(positions)
        n_centers = len(centers)
        n_features = soap_mat.shape[1]
        
        # Precalculate values
        l_values = np.arange(self._l_max + 1)
        
        for i_center in tqdm(range(n_centers), desc="Processing centers"):
            center = centers[i_center]
            n_atoms_idx = atoms.AtomPositionManager.find_all_neighbors_radius(center, self._r_cut + cutoff_padding, p=2., eps=0)
            
            r_vecs = positions[n_atoms_idx] - center
            r = np.linalg.norm(r_vecs, axis=1)
            mask = r < (self._r_cut + cutoff_padding)
            r_vecs = r_vecs[mask]
            r = r[mask]
            atom_types = atomic_numbers[n_atoms_idx][mask]
            
            if len(r) == 0:
                continue
            
            # Calculate spherical coordinates
            theta = np.arccos(np.clip(r_vecs[:, 2] / r, -1.0, 1.0))
            phi = np.arctan2(r_vecs[:, 1], r_vecs[:, 0])
            
            # Calculate R_nl for all n and r
            R_nl = self.calculate_R_nl(r, alphas, self._l_max)
            
            for n in range(self._n_max):
                for l in l_values:
                    for m in range(-l, l+1):
                        Y_lm = sph_harm(m, l, phi, theta)
                        idx = self._get_feature_index(n, l, m, atom_types)
                        
                        mask = idx < n_features
                        if not np.any(mask):
                            continue
                        
                        value = R_nl[:, n] * np.real(Y_lm)
                        np.add.at(soap_mat[i_center], idx[mask], value[mask])

        # Normalize the SOAP vectors
        norms = np.linalg.norm(soap_mat, axis=1)
        norms[norms == 0] = 1.0  # Avoid division by zero
        soap_mat /= norms[:, np.newaxis]

    def _create_polynomial(self, soap_mat, positions, atomic_numbers, cell, pbc, centers, cutoff_padding):
        n_atoms = len(positions)
        n_centers = len(centers)
        
        for i_center in range(n_centers):
            center = centers[i_center]
            for i_atom in range(n_atoms):
                atom_pos = positions[i_atom]
                atom_type = atomic_numbers[i_atom]
                
                r_vec = atom_pos - center
                
                if pbc:
                    r_vec = r_vec - cell * np.round(r_vec / cell)
                
                r = np.linalg.norm(r_vec)
                
                if r < self._r_cut + cutoff_padding:
                    theta = np.arccos(r_vec[2] / r)
                    phi = np.arctan2(r_vec[1], r_vec[0])
                    
                    g_interp = np.interp(r, self._rx, self._gss)
                    
                    for n in range(self._n_max):
                        for l in range(self._l_max + 1):
                            for m in range(-l, l+1):
                                R_nl = g_interp[n]
                                Y_lm = sph_harm(m, l, phi, theta)
                                
                                idx = self._get_feature_index(n, l, m, atom_type)
                                soap_mat[i_center, idx] += R_nl * Y_lm.real

        # Normalize the SOAP vectors
        norms = np.linalg.norm(soap_mat, axis=1)
        norms[norms == 0] = 1.0  # Avoid division by zero
        soap_mat /= norms[:, np.newaxis]

    def _get_feature_index(self, n, l, m, atom_types):
        idx = (atom_types * self._n_max * (self._l_max + 1)**2 +
               n * (self._l_max + 1)**2 +
               l * (2 * l + 1) +
               (m + l)).astype(int)
        return idx % self.get_number_of_features()

    def get_number_of_features(self):
        n_elem = self.n_elements
        if self.compression["mode"] == "mu2":
            return int((self._n_max) * (self._n_max + 1) * (self._l_max + 1) / 2)
        elif self.compression["mode"] == "mu1nu1":
            return int(self._n_max**2 * n_elem * (self._l_max + 1))
        elif self.compression["mode"] == "crossover":
            return int(n_elem * self._n_max * (self._n_max + 1) / 2 * (self._l_max + 1))
        n_elem_radial = n_elem * self._n_max
        return int((n_elem_radial) * (n_elem_radial + 1) / 2 * (self._l_max + 1))

    def init_descriptor_array(self, n_centers):
        n_features = self.get_number_of_features()
        return np.zeros((n_centers, n_features), dtype=self.dtype)

    def get_cutoff_padding(self):
        threshold = 0.001
        cutoff_padding = self._sigma * np.sqrt(-2 * np.log(threshold))
        return cutoff_padding

    def get_number_of_features(self):
        n_elem = self.n_elements
        if self.compression["mode"] == "mu2":
            return int((self._n_max) * (self._n_max + 1) * (self._l_max + 1) / 2)
        elif self.compression["mode"] == "mu1nu1":
            return int(self._n_max**2 * n_elem * (self._l_max + 1))
        elif self.compression["mode"] == "crossover":
            return int(n_elem * self._n_max * (self._n_max + 1) / 2 * (self._l_max + 1))
        n_elem_radial = n_elem * self._n_max
        return int((n_elem_radial) * (n_elem_radial + 1) / 2 * (self._l_max + 1))

    def get_location(self, species):
        if len(species) != 2:
            raise ValueError("Please use a pair of atomic numbers or chemical symbols.")

        numbers = []
        for specie in species:
            if isinstance(specie, str):
                specie = self._get_atomic_number(specie)
            numbers.append(specie)

        for number in numbers:
            if number not in self._atomic_numbers:
                raise ValueError(f"Atomic number {number} was not specified in the species.")

        numbers = [self._species_to_index[self._index_to_species[self._atomic_numbers.index(x)]] for x in numbers]
        n_elem = self.n_elements

        if numbers[0] > numbers[1]:
            numbers = list(reversed(numbers))
        i, j = numbers

        if self.compression["mode"] == "off":
            n_elem_feat_symm = self._n_max * (self._n_max + 1) / 2 * (self._l_max + 1)
            n_elem_feat_unsymm = self._n_max * self._n_max * (self._l_max + 1)
            n_elem_feat = n_elem_feat_symm if i == j else n_elem_feat_unsymm

            m_symm = i + int(j > i)
            m_unsymm = j + i * n_elem - i * (i + 1) / 2 - m_symm

            start = int(m_symm * n_elem_feat_symm + m_unsymm * n_elem_feat_unsymm)
            end = int(start + n_elem_feat)
        elif self.compression["mode"] == "mu2":
            n_elem_feat_symm = self._n_max * (self._n_max + 1) * (self._l_max + 1) / 2
            start = 0
            end = int(n_elem_feat_symm)
        elif self.compression["mode"] in ["mu1nu1", "crossover"]:
            n_elem_feat_symm = self._n_max**2 * (self._l_max + 1)
            if self.compression["mode"] == "crossover":
                n_elem_feat_symm = self._n_max * (self._n_max + 1) * (self._l_max + 1) / 2
            if i != j:
                raise ValueError("Compression has been selected. No cross-species output available")
            start = int(i * n_elem_feat_symm)
            end = int(start + n_elem_feat_symm)

        return slice(start, end)

    def get_basis_gto(self, r_cut, n_max, l_max):
        a = np.linspace(1, r_cut, n_max)
        threshold = 1e-3

        alphas_full = np.zeros((l_max + 1, n_max))
        betas_full = np.zeros((l_max + 1, n_max, n_max))

        for l in range(0, l_max + 1):
            alphas = -np.log(threshold / np.power(a, l)) / a**2
            m = alphas[:, np.newaxis] + alphas[np.newaxis, :]
            S = 0.5 * gamma(l + 3.0 / 2.0) * m ** (-l - 3.0 / 2.0)
            betas = sqrtm(inv(S))

            if betas.dtype == np.complex128:
                raise ValueError(
                    "Could not calculate normalization factors for the radial "
                    "basis in the domain of real numbers. Lowering the number of "
                    "radial basis functions (n_max) or increasing the radial "
                    "cutoff (r_cut) is advised."
                )

            alphas_full[l, :] = alphas
            betas_full[l, :, :] = betas

        return alphas_full, betas_full

    def get_basis_poly(self, r_cut, n_max):
        S = np.zeros((n_max, n_max), dtype=np.float64)
        for i in range(1, n_max + 1):
            for j in range(1, n_max + 1):
                S[i - 1, j - 1] = (2 * (r_cut) ** (7 + i + j)) / (
                    (5 + i + j) * (6 + i + j) * (7 + i + j)
                )

        betas = sqrtm(np.linalg.inv(S))

        if betas.dtype == np.complex128:
            raise ValueError(
                "Could not calculate normalization factors for the radial "
                "basis in the domain of real numbers. Lowering the number of "
                "radial basis functions (n_max) or increasing the radial "
                "cutoff (r_cut) is advised."
            )

        x = np.zeros(100)
        x[0] = -0.999713726773441234
        x[1] = -0.998491950639595818
        x[2] = -0.996295134733125149
        x[3] = -0.99312493703744346
        x[4] = -0.98898439524299175
        x[5] = -0.98387754070605702
        x[6] = -0.97780935848691829
        x[7] = -0.97078577576370633
        x[8] = -0.962813654255815527
        x[9] = -0.95390078292549174
        x[10] = -0.94405587013625598
        x[11] = -0.933288535043079546
        x[12] = -0.921609298145333953
        x[13] = -0.90902957098252969
        x[14] = -0.895561644970726987
        x[15] = -0.881218679385018416
        x[16] = -0.86601468849716462
        x[17] = -0.849964527879591284
        x[18] = -0.833083879888400824
        x[19] = -0.815389238339176254
        x[20] = -0.79689789239031448
        x[21] = -0.77762790964949548
        x[22] = -0.757598118519707176
        x[23] = -0.736828089802020706
        x[24] = -0.715338117573056447
        x[25] = -0.69314919935580197
        x[26] = -0.670283015603141016
        x[27] = -0.64676190851412928
        x[28] = -0.622608860203707772
        x[29] = -0.59784747024717872
        x[30] = -0.57250193262138119
        x[31] = -0.546597012065094168
        x[32] = -0.520158019881763057
        x[33] = -0.493210789208190934
        x[34] = -0.465781649773358042
        x[35] = -0.437897402172031513
        x[36] = -0.409585291678301543
        x[37] = -0.380872981624629957
        x[38] = -0.351788526372421721
        x[39] = -0.322360343900529152
        x[40] = -0.292617188038471965
        x[41] = -0.26258812037150348
        x[42] = -0.23230248184497397
        x[43] = -0.201789864095735997
        x[44] = -0.171080080538603275
        x[45] = -0.140203137236113973
        x[46] = -0.109189203580061115
        x[47] = -0.0780685828134366367
        x[48] = -0.046871682421591632
        x[49] = -0.015628984421543083
        x[50] = 0.0156289844215430829
        x[51] = 0.046871682421591632
        x[52] = 0.078068582813436637
        x[53] = 0.109189203580061115
        x[54] = 0.140203137236113973
        x[55] = 0.171080080538603275
        x[56] = 0.201789864095735997
        x[57] = 0.23230248184497397
        x[58] = 0.262588120371503479
        x[59] = 0.292617188038471965
        x[60] = 0.322360343900529152
        x[61] = 0.351788526372421721
        x[62] = 0.380872981624629957
        x[63] = 0.409585291678301543
        x[64] = 0.437897402172031513
        x[65] = 0.465781649773358042
        x[66] = 0.49321078920819093
        x[67] = 0.520158019881763057
        x[68] = 0.546597012065094168
        x[69] = 0.572501932621381191
        x[70] = 0.59784747024717872
        x[71] = 0.622608860203707772
        x[72] = 0.64676190851412928
        x[73] = 0.670283015603141016
        x[74] = 0.693149199355801966
        x[75] = 0.715338117573056447
        x[76] = 0.736828089802020706
        x[77] = 0.75759811851970718
        x[78] = 0.77762790964949548
        x[79] = 0.79689789239031448
        x[80] = 0.81538923833917625
        x[81] = 0.833083879888400824
        x[82] = 0.849964527879591284
        x[83] = 0.866014688497164623
        x[84] = 0.881218679385018416
        x[85] = 0.89556164497072699
        x[86] = 0.90902957098252969
        x[87] = 0.921609298145333953
        x[88] = 0.933288535043079546
        x[89] = 0.94405587013625598
        x[90] = 0.953900782925491743
        x[91] = 0.96281365425581553
        x[92] = 0.970785775763706332
        x[93] = 0.977809358486918289
        x[94] = 0.983877540706057016
        x[95] = 0.98898439524299175
        x[96] = 0.99312493703744346
        x[97] = 0.99629513473312515
        x[98] = 0.998491950639595818
        x[99] = 0.99971372677344123

        rx = r_cut * 0.5 * (x + 1)

        fs = np.zeros([n_max, len(x)])
        for n in range(1, n_max + 1):
            fs[n - 1, :] = (r_cut - np.clip(rx, 0, r_cut)) ** (n + 2)

        gss = np.dot(betas, fs)

        return rx, gss

    @property
    def compression(self):
        return self._compression

    @compression.setter
    def compression(self, value):
        supported_modes = set(("off", "mu2", "mu1nu1", "crossover"))
        mode = value.get("mode", "off")
        if mode not in supported_modes:
            raise ValueError(
                f"Invalid compression mode '{mode}' given. Please use "
                f"one of the following: {supported_modes}"
            )

        species_weighting = value.get("species_weighting")
        if species_weighting is None:
            self._species_weights = np.ones((self.n_elements))

        else:
            if not isinstance(species_weighting, dict):
                raise ValueError(
                    f"Invalid species weighting '{value}' given. Species weighting must "
                    "be either None or a dict."
                )

            if len(species_weighting) != self.n_elements:
                raise ValueError(
                    "The species_weighting dictionary, "
                    "if supplied, must contain the same keys as "
                    "the list of accepted species."
                )
            species_weights = []
            for specie in self.species:
                if specie not in species_weighting:
                    raise ValueError(
                        "The species_weighting dictionary, "
                        "if supplied, must contain the same keys as "
                        "the list of accepted species."
                    )
                weight = species_weighting[specie]
                atomic_number = self._get_atomic_number(specie)
                species_weights.append((weight, atomic_number))

            species_weights = [s[0] for s in sorted(species_weights, key=lambda x: x[1])]
            self._species_weights = np.array(species_weights).astype(np.float64)

        self._compression = value

    def derivatives_numerical(self, d, c, atoms, centers, indices, attach, return_descriptor=True):
        # This is a placeholder for the numerical derivatives calculation
        # You would need to implement the full calculation here
        pass

    def derivatives_analytical(self, d, c, atoms, centers, indices, attach, return_descriptor=True):
        # This is a placeholder for the analytical derivatives calculation
        # You would need to implement the full calculation here
        pass

    def validate_derivatives_method(self, method, attach):
        methods = {"numerical", "analytical", "auto"}
        if method not in methods:
            raise ValueError(f"Invalid method specified. Please choose from: {methods}")
        
        if method == "numerical":
            return method

        try:
            if self._rbf == "polynomial":
                raise ValueError("Analytical derivatives currently not available for polynomial radial basis functions.")
            if self.average != "off":
                raise ValueError("Analytical derivatives currently not available for averaged output.")
            if self.compression["mode"] not in ["off", "crossover"]:
                raise ValueError("Analytical derivatives not currently available for mu1nu1, mu2 compression.")
            if self.periodic:
                raise ValueError("Analytical derivatives currently not available for periodic systems.")
            if self._weighting:
                raise ValueError("Analytical derivatives currently not available when weighting is used.")
        except Exception as e:
            if method == "analytical":
                raise e
            elif method == "auto":
                method = "numerical"
        else:
            if method == "auto":
                method = "analytical"

        return method