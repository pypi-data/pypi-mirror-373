try:
    import numpy as np
    import warnings
    from collections import defaultdict
    from typing import Dict, List, Any

except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class plot:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._comment = None
        self._atomCount = None 
        self._RBF = None


    def get_RBF(self, cutoff: float = 6.0, number_of_bins: int = 100,
                bin_volume_normalize: bool = True, number_of_atoms_normalize: bool = True, density_normalize: bool = True,
                A_class: bool = False, B_class: bool = False,
                method: str = 'kdtree'):
        """
        Computes the Radial Basis Function (RBF) of atomic positions in a molecular system.

        Parameters:
        ----------
        cutoff : float, optional
            The maximum distance up to which atomic pair interactions are considered (default is 6.0 Å).
        number_of_bins : int, optional
            The number of bins used to compute the histogram of interatomic distances (default is 100).
        bin_volume_normalize : bool, optional
            If True, normalizes the histogram by the volume of each bin (default is True).
        number_of_atoms_normalize : bool, optional
            If True, normalizes the histogram by the total number of atoms (default is True).
        density_normalize : bool, optional
            If True, normalizes the histogram by the density of the system (default is True).
        A_class : bool, optional
            If True, appends the atomic class information to atom labels for type A (default is False).
        B_class : bool, optional
            If True, appends the atomic class information to atom labels for type B (default is False).
        method : str, optional
            The method to find neighbors, default is 'kdtree'.

        Returns:
        -------
        rbf : dict
            A dictionary containing the RBF values for each atom pair type. The keys are atom type pairs, 
            and the values are lists containing bin centers and normalized histogram values.
        """
        # Validate A_class and B_class parameters
        if not isinstance(A_class, bool):
            warnings.warn(
                f"A_class is expected to be a boolean; received {type(A_class).__name__}. Defaulting to False.",
                UserWarning
            )
            A_class = False
        if not isinstance(B_class, bool):
            warnings.warn(
                f"B_class is expected to be a boolean; received {type(B_class).__name__}. Defaulting to False.",
                UserWarning
            )
            B_class = False

        # Convert number of bins to integer in case a float is provided
        number_of_bins = int(number_of_bins)

        # Retrieve lattice vectors, atomic positions, and atom labels
        cell, positions, atom_Labels_List = self.latticeVectors, self.atomPositions, self.atomLabelsList

        # Initialize and compute distance matrix dictionary
        distance_matrix_dict = self._compute_distance_matrix(cutoff, A_class, B_class)

        # Calculate and normalize RBF
        rbf = self._calculate_normalized_rbf(distance_matrix_dict, number_of_bins, cutoff, 
                                             bin_volume_normalize, number_of_atoms_normalize, density_normalize)

        return rbf


    def _compute_distance_matrix(
        self,
        cutoff: float,
        A_class: bool,
        B_class: bool
    ) -> Dict[str, Dict[str, List[float]]]:
        """
        Computes a distance matrix dictionary that stores distances between different atom types.

        Parameters:
        ----------
        cutoff : float
            The maximum distance up to which atomic pair interactions are considered.
        A_class : bool
            Whether to append atomic class information to atom labels for type A.
        B_class : bool
            Whether to append atomic class information to atom labels for type B.

        Returns:
        -------
        distance_matrix_dict : dict
            A dictionary storing distances between different atom types.
        """
        # Retrieve class IDs and create unique class dictionaries
        class_IDs = self.atomLabelsList
        unique_class_IDs_dict = {cid: i for i, cid in enumerate(set(class_IDs))}
        uniqueAtomLabels_dict = {ual: i for i, ual in enumerate(self.uniqueAtomLabels)}

        # 1) Find neighbor lists
        # Find neighbors using k-d tree
        ID_neighbors = self.find_ID_neighbors(other=self.kdtree, r=cutoff)

        # 2) Prepare result container
        # Initialize the dictionary to store distance matrices
        distance_matrix_dict = {}

        # 3) Loop over atoms and their neighbors
        # Iterate over each atom to compute pairwise distances
        for raw_ID_a, ID_neighbors_a in enumerate(ID_neighbors):
            ID_a = int(raw_ID_a)
            label_a = str(self.atomLabelsList[ID_a])+str(class_IDs[ID_a]) if A_class else self.atomLabelsList[ID_a]

            # Initialize distance dictionary for atom A
            if label_a not in distance_matrix_dict:
                distance_matrix_dict[label_a] = {}

            position_a = self.atomPositions[ID_a]

            # Calculate distances to neighbors
            for raw_ID_b in ID_neighbors_a:
                ID_b = int(raw_ID_b)
                if ID_a != ID_b:  # Exclude self-interactions
                    label_b = str(self.atomLabelsList[ID_b])+str(class_IDs[ID_b]) if B_class else self.atomLabelsList[ID_b]

                    # Initialize the distance list for the pair if not existing
                    if label_b not in distance_matrix_dict[label_a]:
                        distance_matrix_dict[label_a][label_b] = []

                    # Append the computed distance
                    position_b = self.atomPositions[ID_b]
                    distance_matrix_dict[label_a][label_b].append(self.distance(position_a, position_b))

        return distance_matrix_dict

    def _calculate_normalized_rbf(self, distance_matrix_dict: dict, number_of_bins: int, cutoff: float, 
                                  bin_volume_normalize: bool, number_of_atoms_normalize: bool, density_normalize: bool) -> dict:
        """
        Calculates and normalizes the Radial Basis Function (RBF) for each atom pair type.

        Parameters:
        ----------
        distance_matrix_dict : dict
            Dictionary storing distances between different atom types.
        number_of_bins : int
            Number of bins to use for the histogram.
        cutoff : float
            Maximum distance for considering atomic pair interactions.
        bin_volume_normalize : bool
            Whether to normalize the histogram by bin volume.
        number_of_atoms_normalize : bool
            Whether to normalize the histogram by the total number of atoms.
        density_normalize : bool
            Whether to normalize the histogram by the density of the system.

        Returns:
        -------
        rbf : dict
            A dictionary containing the normalized RBF values.
        """
        rbf = {label_a: {} for label_a in distance_matrix_dict}

        # Compute the RBF for each atom pair type
        for label_a, distance_matrix_dict_a in distance_matrix_dict.items():
            for label_b, distances_list in distance_matrix_dict_a.items():
                # Filter out very small distances and compute the histogram
                distances = np.array(distances_list)
                distances = distances[distances > 0.1]
                rbf_a, bin_edges = np.histogram(distances, bins=number_of_bins, range=(0, cutoff))
                bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2

                # Normalize the histogram #
                # Normalize by bin volume
                rbf_a = rbf_a.astype(np.float64)

                if bin_volume_normalize:
                    rbf_a /= (4.0 * np.pi / 3.0 * (bin_edges[1:]**3 - bin_edges[:-1]**3))
                # Normalize by the total number of atoms
                if number_of_atoms_normalize:
                    rbf_a /= self.atomPositions.shape[0]
                # Normalize by density
                if density_normalize:
                    rbf_a /= len(self.atomPositions) / self.get_volume()

                # Store the results
                rbf[label_a][label_b] = [bin_centers, rbf_a]

        return rbf

    def get_RBF_cdist(self, periodic_image:int=0, cutoff:float=6.0, number_of_bins:int=100, 
                bin_volume_normalize:bool=True, number_of_atoms_normalize:bool=True, density_normalize:bool=True, ):
        """
        """

        try:
            from scipy.spatial.distance import cdist
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing scipy.spatial.distance.cdist: {str(e)}\n")
            del sys

        number_of_bins = int(number_of_bins)

        # Process each frame in the trajectory
        cell = self.latticeVectors
        positions = self.atomPositions

        # Crear imágenes en las fronteras (ejemplo simple para una imagen en cada dirección)
        if periodic_image == 0:
            periodic_image = cutoff/np.max( np.linalg.norm(self.latticeVectors,axis=0) )
        periodic_image = int( np.round(periodic_image) )

        images = positions.copy()
        for i in range(-periodic_image, periodic_image+1):
            for j in range(-periodic_image, periodic_image+1):
                for k in range(-periodic_image, periodic_image+1):
                    if (i, j, k) != (0, 0, 0):
                        offset = np.dot( [i, j, k], cell )
                        images = np.vstack([images, positions + offset])

        distance_matrix = cdist(positions, images, 'euclidean')

        label_list_unit_cell = self.atomLabelsList
        label_list_expand_cell = np.tile(self.atomLabelsList, (periodic_image*2+1)**3)

        distance_matrix_dict = {a_label:{b_label:[] for b_index, b_label in enumerate(self.uniqueAtomLabels) if a_index >= b_index } for a_index, a_label in enumerate(self.uniqueAtomLabels) }

        uniqueAtomLabels_dict = {a_label:a_index for a_index, a_label in enumerate(self.uniqueAtomLabels) }
        for a_index, a_label in enumerate(label_list_unit_cell):
            for b_index, b_label in enumerate(label_list_expand_cell):
                if uniqueAtomLabels_dict[a_label] > uniqueAtomLabels_dict[b_label]:
                    distance_matrix_dict[a_label][b_label].append( distance_matrix[a_index, b_index] ) 
                else:
                    distance_matrix_dict[b_label][a_label].append( distance_matrix[a_index, b_index] ) 

        rbf = { a_label:{} for a_index, a_label in enumerate(self.uniqueAtomLabels) }
        for a_index, a_label in enumerate(self.uniqueAtomLabels):
            for b_index, b_label in enumerate(self.uniqueAtomLabels):

                distances = np.array(distance_matrix_dict[a_label][b_label]) if a_index >= b_index else np.array(distance_matrix_dict[b_label][a_label])
                distances = distances[ distances>0.1 ]

                rbf_a, bin_edges = np.histogram(distances, bins=number_of_bins, range=(0, cutoff))

                bin_centers = (bin_edges[1:]+bin_edges[:-1])/2

                # Normalize by bin volume and total number of atoms
                if bin_volume_normalize:
                    rbf_a = rbf_a/(4*np.pi/3 * (bin_edges[1:]**3-bin_edges[:-1]**3))

                if number_of_atoms_normalize:
                    rbf_a /= positions.shape[0]

                # Normalize by density
                if density_normalize:
                    rbf_a /= len(positions)/self.get_volume()

                rbf[a_label][b_label] = [bin_centers, rbf_a]

        return rbf

    def plot_RBF(self, cutoff:float=6.0, number_of_bins:int=100, partial_rbf:bool=True,
                output_path:str=None, save:bool=True, kdtree:bool=True, 
                bin_volume_normalize:bool=True, number_of_atoms_normalize:bool=True, density_normalize:bool=True, 
                A_class:bool=False, B_class:bool=False):
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing matplotlib.pyplot: {str(e)}\n")
            del sys

        def _save(ax, name):
            plt.tight_layout()
            plt.savefig(name)  
            plt.clf()

        def _make_ax(a_label):
            fig, ax = plt.subplots()

            ax.set_xlabel('Distance (Angstrom)')
            ax.set_ylabel('g(r)')
            ax.set_title(f'Radial Distribution Function {a_label} ')

            return fig, ax 

        output_path = "." if output_path is None else output_path # Default to the current working directory

        self.wrap()
        number_of_bins = int(number_of_bins)

        if kdtree:
            rbf = self.get_RBF( cutoff=cutoff, number_of_bins=number_of_bins,  
                                bin_volume_normalize=bin_volume_normalize, number_of_atoms_normalize=number_of_atoms_normalize, density_normalize=density_normalize,
                                A_class=A_class, B_class=B_class
                                )

        if partial_rbf:

            for a_index, (a_label, a_dict) in enumerate(rbf.items()):
                fig, ax = _make_ax(a_label) 

                for b_index, (b_label, b_dict) in enumerate(a_dict.items()):

                    bin_centers, rbf_a = rbf[a_label][b_label]
                    color = self.element_colors[b_label] 

                    ax.plot(bin_centers, rbf_a, 'x-', alpha=0.8, color=color, label=f'd({a_label}-{b_label})' )
                    ax.fill_between(bin_centers, rbf_a, alpha=0.1, color=color )  # Rellena debajo de la línea con transparencia

                ax.legend()
                if save: _save(ax, f"{output_path}/RBF_{a_label}.png")
                plt.close(fig)

        rbf_total = np.sum([ rbf[a_label][b_label][1] for a_index, (a_label, a_dict) in enumerate(rbf.items()) for b_index, (b_label, b_dict) in enumerate(a_dict.items())], axis=0)
        fig, ax = _make_ax(a_label) 

        ax.plot(bin_centers, rbf_total, 'x-', color=(0.3, 0.3, 0.3))
        ax.fill_between(bin_centers, rbf_total, alpha=0.3, color=(0.3, 0.3, 0.3))  # Rellena debajo de la línea con transparencia

        if save: _save(ax, f"{output_path}/RBF_total.png")
        plt.close(fig)

        return rbf

    def count_species(self,  specie:list, sigma:float=1.4 ):

        # Process each frame in the trajectory
        positions = self.atomPositions
        atom_Labels_List = self.atomLabelsList
        uniqueAtomLabels_dict = { ual:i for i, ual in enumerate(self.uniqueAtomLabels) }
        self.wrap()

        cutoff = np.max([self.covalent_radii[label_a]+self.covalent_radii[label_b] for label_a in self.uniqueAtomLabels for label_b in self.uniqueAtomLabels])
        ans = {}
        #if specie.upper() in ['H2O', 'WATER']:
        for n in self.uniqueAtomLabels:
            ans = { }
            ID_specie = np.arange(self.atomCount)[self.atomLabelsList==n]
            for ID in ID_specie:



                ID_neighbors = self.find_all_neighbors_radius( x=self.atomPositions[ID], r=cutoff )
                embedding = sorted([ self.atomLabelsList[i] for i in ID_neighbors if self.covalent_radii[self.atomLabelsList[i]]+self.covalent_radii[n]*sigma > self.distance(positions[ID], positions[i]) and  i != ID ])
                if ''.join(embedding) in ans:
                    ans[''.join(embedding)] += 1
                else:
                    ans[''.join(embedding)] = 1

            for m in ans:
                print(n, ans[m], m)


