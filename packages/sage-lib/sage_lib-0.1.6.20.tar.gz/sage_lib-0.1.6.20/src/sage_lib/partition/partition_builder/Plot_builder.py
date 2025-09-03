try:
    from ...miscellaneous.math_tools import normalize_matrix_to_doubly_stochastic
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
    del sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.colors import LinearSegmentedColormap
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing matplotlib.pyplot: {str(e)}\n")
    del sys
    
try:
    from scipy.stats import iqr
    from scipy.interpolate import make_interp_spline

except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing scipy: {str(e)}\n")
    del sys

try:
    import os
    import copy
    import numpy as np
    from tqdm import tqdm
    from itertools import cycle
    from typing import Dict, List, Tuple, Union, Optional
    from collections import defaultdict
    from joblib import Memory
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import imageio
    import pickle
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing os: {str(e)}\n")
    del sys

class Plot_builder(BasePartition):
    """
    Class for building and managing molecular dynamic simulations.
    
    Inherits from PartitionManager and integrates additional functionalities
    specific to molecular dynamics, such as calculating displacement and plotting.

    Attributes:
        _molecule_template (dict): A template for the molecule structure.
        _density (float): Density value of the molecule.
        _cluster_lattice_vectors (numpy.ndarray): Lattice vectors of the cluster.
    """
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        Initialize the MolecularDynamicBuilder object.

        Args:
            file_location (str, optional): File location of the input data.
            name (str, optional): Name of the simulation.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def visualize_graph_2d(self, 
                           adjacency_matrix: np.ndarray, 
                           labels: List[str], 
                           title: str = "2D Graph Visualization",
                           num_attempts: int = 2, 
                           output_path: str = './',) -> None:
        """
        Create a sophisticated 2D visualization of a graph from a square adjacency matrix.

        Args:
            adjacency_matrix (np.ndarray): The square adjacency matrix of the graph.
            labels (List[str]): A list of labels for the nodes.
            title (str, optional): The title of the graph visualization. 
            num_attempts (int, optional): Number of layout attempts to try. Defaults to 5.

        Raises:
            ValueError: If the number of labels doesn't match the matrix dimensions.

        Returns:
            None: The function displays the graph using matplotlib.pyplot.show().
        """
        n = adjacency_matrix.shape[0]
        if len(labels) != n:
            raise ValueError("Number of labels must match the dimensions of the adjacency matrix.")

        # Calculate mean connection value
        mean_connection = np.mean(adjacency_matrix)

        def calculate_force(pos1: np.ndarray, pos2: np.ndarray, weight: float) -> np.ndarray:
            """Calculate force between two nodes based on their connection weight."""
            diff = pos2 - pos1
            distance = np.linalg.norm(diff)
            if distance == 0:
                return np.random.rand(2) * 0.001
            
            force_magnitude = 0.1 * (weight - mean_connection) / (distance ** 2)
            return force_magnitude * diff

        def layout_energy(positions: np.ndarray) -> float:
            """Calculate the energy of the current layout."""
            energy = 0
            for i in range(n):
                for j in range(i + 1, n):
                    diff = positions[i] - positions[j]
                    distance = np.linalg.norm(diff)
                    if distance > 0:
                        energy += (adjacency_matrix[i, j] - mean_connection) * (distance ** 2)
            return energy

        def perform_layout(initial_positions: np.ndarray) -> Tuple[np.ndarray, float]:
            positions = initial_positions.copy()
            for _ in range(2000):  # Number of iterations
                new_positions = positions.copy()
                for i in range(n):
                    force = np.zeros(2)
                    for j in range(n):
                        if i != j:
                            force += calculate_force(positions[i], positions[j], adjacency_matrix[i, j])
                    new_positions[i] += force
                positions = new_positions
            
            # Normalize positions to fit in [0, 1] range
            positions = (positions - positions.min(axis=0)) / (positions.max(axis=0) - positions.min(axis=0))
            return positions, layout_energy(positions)

        # Perform multiple layout attempts and select the best one
        best_positions = None
        best_energy = float('inf')
        for _ in range(num_attempts):
            initial_positions = np.random.rand(n, 2)
            positions, energy = perform_layout(initial_positions)
            if energy < best_energy:
                best_positions = positions
                best_energy = energy

        positions = best_positions

        # Calculate degree centrality
        degree_centrality = np.sum(adjacency_matrix, axis=0)

        # Set up the plot
        plt.figure(figsize=(16, 12))
        ax = plt.gca()

        # Create custom colormap
        colors = ["#FFA07A", "#98FB98", "#87CEFA"]
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list("custom", colors, N=n_bins)

        # Normalize centrality for coloring
        centrality_norm = (degree_centrality - degree_centrality.min()) / (degree_centrality.max() - degree_centrality.min())

        # Draw edges
        for i in range(n):
            for j in range(i+1, n):
                if adjacency_matrix[i, j] != 0:
                    color = 'red' if adjacency_matrix[i, j] < mean_connection else 'green'
                    ax.plot([positions[i, 0], positions[j, 0]],
                            [positions[i, 1], positions[j, 1]],
                            color=color, 
                            linewidth=abs(adjacency_matrix[i, j] - mean_connection) * 2,
                            alpha=0.6,
                            zorder=1)

        # Draw nodes
        scatter = ax.scatter(positions[:, 0], positions[:, 1],
                             s=degree_centrality * 100,
                             c=centrality_norm,
                             cmap=cmap,
                             alpha=0.8,
                             zorder=2)

        # Add labels to nodes
        for i, label in enumerate(labels):
            ax.annotate(label,
                        (positions[i, 0], positions[i, 1]),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=10,
                        fontweight='bold',
                        zorder=3)

        # Customize the plot
        ax.set_title(title, fontsize=20, fontweight='bold')
        ax.axis('off')
        plt.tight_layout()

        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Degree Centrality', fontsize=12)

        # Save the plot with an appropriate filename
        filename = f"graph_plot.png"
        plt.tight_layout()
        plt.savefig(f"{output_path}/{filename}", dpi=300, bbox_inches='tight')
    
    def generate_integral_matrix(self, data: dict) -> np.ndarray:
        """
        Generate a matrix containing the integrals (sums) of vectors from a nested dictionary.

        Args:
            data (dict): A dictionary with sub-dictionaries containing vectors.

        Returns:
            np.ndarray: A matrix where each element represents the integral (sum) of a vector from the nested dictionary.
        """
        # Step 1: Extract unique keys for rows and columns
        main_keys = list(data.keys())  # Main dictionary keys
        sub_keys = list({key for sub_dict in data.values() for key in sub_dict.keys()})  # Unique sub-dictionary keys

        # Step 2: Check if main_keys and sub_keys are the same
        if set(main_keys) == set(sub_keys):
            # Ensure the same order for both row and column indices
            common_keys = sorted(main_keys)  # Sorting to ensure consistent ordering
            main_key_to_index = {key: i for i, key in enumerate(common_keys)}
            sub_key_to_index = {key: i for i, key in enumerate(common_keys)}
            # Initialize a square matrix
            matrix = np.zeros((len(common_keys), len(common_keys)))
        else:
            # Different keys for rows and columns
            main_key_to_index = {key: i for i, key in enumerate(main_keys)}
            sub_key_to_index = {key: i for i, key in enumerate(sub_keys)}
            # Initialize a matrix with size len(main_keys) x len(sub_keys)
            matrix = np.zeros((len(main_keys), len(sub_keys)))

        # Step 3: Populate the matrix with integrals
        for main_key, sub_dict in data.items():
            for sub_key, vector in sub_dict.items():
                if main_key in main_key_to_index and sub_key in sub_key_to_index:
                    row_index = main_key_to_index[main_key]
                    col_index = sub_key_to_index[sub_key]

                    # Calculate the integral (sum) of the vector and store it in the matrix
                    matrix[row_index, col_index] = np.sum(vector)

        return matrix, main_key_to_index, sub_key_to_index

    def plot_RBF_correlation(self, cutoff: float = 3.0, number_of_bins: int = 100, output_path: str = './',
                            A_class:bool=False, B_class:bool=False, verbose:bool=False):
        """
        Plot Radial Basis Function (RBF) clusters for different atom types.

        This function calculates and plots the Radial Distribution Function (RDF) for different
        cluster classes and atom types. It aggregates data from multiple containers, normalizes
        the RBF, and generates plots for each cluster class.

        Args:
            cutoff (float): The maximum distance to consider for RBF calculation. Default is 3.0.
            number_of_bins (int): The number of bins to use for RBF histogram. Default is 100.
            output_path (str): The directory to save the output plots. Default is './'.

        Returns:
            None. Plots are saved to the specified output path.
        """
        # Ensure the output directory exists
        self.create_directories_for_path(output_path)

        # Initialize dictionary to store RBF data
        rbf: Dict[str, Dict[str, np.ndarray]] = {}

        # Aggregate RBF data from all containers
        for container in self.containers:
            self._aggregate_rbf_data(
                container=container, rbf=rbf, 
                cutoff=cutoff, number_of_bins=number_of_bins, 
                A_class=A_class, B_class=B_class)

        # Generate the integral matrix
        rbf_matrix, mapping_a, mapping_b = self.generate_integral_matrix(rbf)

        # Sinkhorn normalization to make the matrix doubly stochastic
        rbf_matrix = normalize_matrix_to_doubly_stochastic(rbf_matrix, tol=1e-9, max_iter=1000)
        
        self.visualize_graph_2d(adjacency_matrix=rbf_matrix,
                           labels=sorted(mapping_a, key=lambda x: mapping_a[x]),
                           output_path=output_path
                           )

        # Get labels for rows and columns from the mappings
        row_labels = [key for key, index in sorted(mapping_a.items(), key=lambda x: x[1])]
        col_labels = [key for key, index in sorted(mapping_b.items(), key=lambda x: x[1])]

        if verbose:
            print(f' >: RBF Matrix shape {rbf_matrix.shape}')
            print(rbf_matrix)

        # Plot the matrix using a heatmap
        plt.figure(figsize=(10, 8))
        heatmap = plt.imshow(rbf_matrix, cmap='viridis', aspect='auto')

        # Add labels for the axes
        plt.xticks(ticks=np.arange(len(col_labels)), labels=col_labels, rotation=45, ha='right')
        plt.yticks(ticks=np.arange(len(row_labels)), labels=row_labels)

        # Add a color bar to the heatmap
        plt.colorbar(heatmap, label='Integral Sum')

        # Add title and labels
        plt.title('RBF Correlation Matrix')
        plt.xlabel('Atom Types')
        plt.ylabel('Cluster Classes')

        # Save the plot with an appropriate filename
        filename = f"RBF_Correlation_Matrix_cutoff{cutoff}_bins{number_of_bins}.png"
        plt.tight_layout()
        plt.savefig(f"{output_path}/{filename}", dpi=300)

        # Close the plot to avoid displaying
        plt.close()

        return rbf

    def plot_RBF(self, cutoff: float = 3.0, number_of_bins: int = 100, output_path: str = './',
                            A_class:bool=False, B_class:bool=False, individual=False, verbose:bool=False):
        """
        Plot Radial Basis Function (RBF) clusters for different atom types.

        This function calculates and plots the Radial Distribution Function (RDF) for different
        cluster classes and atom types. It aggregates data from multiple containers, normalizes
        the RBF, and generates plots for each cluster class.

        Args:
            cutoff (float): The maximum distance to consider for RBF calculation. Default is 3.0.
            number_of_bins (int): The number of bins to use for RBF histogram. Default is 100.
            output_path (str): The directory to save the output plots. Default is './'.
            A_class (bool): Toggle processing for A_class clusters.
            B_class (bool): Toggle processing for B_class clusters.
            individual (bool): If True, process containers individually.
            verbose (bool): Toggle verbose output.

        Returns:
            None. Plots are saved to the specified output path. Data is also saved as a pickle file.
        """
        
        # Ensure the output directory exists
        #os.makedirs(output_path, exist_ok=True)
        self.create_directories_for_path(output_path)

        if individual:
            for container_i, container in enumerate(tqdm(self.containers, desc="Generating frame RBF plots")):
                container_path = output_path+f'/{container_i}'
                self.create_directories_for_path(container_path)
                rbf = container.AtomPositionManager.plot_RBF(output_path=container_path, save=True)
                
                # Save the aggregated data using pickle
                pickle_path = os.path.join(container_path, f'rbf_data_{container_i}.pickle')
                
                try:
                    with open(pickle_path, 'wb') as handle:
                        pickle.dump(rbf, handle, protocol=pickle.HIGHEST_PROTOCOL)
                    if verbose:
                        print(f"RBF data successfully saved to {pickle_path}.")
                except Exception as e:
                    if verbose:
                        print(f"Failed to save RBF data: {e}")

            return True

        else:
            # Initialize dictionary to store RBF data
            rbf: Dict[str, Dict[str, np.ndarray]] = {}

            # Aggregate RBF data from all containers
            for container in tqdm(self.containers, desc="Aggregating RBF data"):
                self._aggregate_rbf_data(
                            container=container, rbf=rbf, 
                            cutoff=cutoff, number_of_bins=number_of_bins, 
                            A_class=A_class, B_class=B_class)

            # Plot RBF for each cluster class
            for rbf_i, (cluster_class_name, rbf_data) in tqdm( enumerate(rbf.items()), desc="Plotting RBF per cluster class"):
                self._plot_rbf(cluster_class_name, rbf_data, output_path)

            # Save the aggregated data using pickle
            pickle_path = os.path.join(output_path, 'rbf_data.pickle')
            try:
                with open(pickle_path, 'wb') as handle:
                    pickle.dump(rbf, handle, protocol=pickle.HIGHEST_PROTOCOL)
                if verbose:
                    print(f"RBF data successfully saved to {pickle_path}.")
            except Exception as e:
                if verbose:
                    print(f"Failed to save RBF data: {e}")

            return rbf

    def _aggregate_rbf_data(self, container, rbf: Dict[str, Dict[str, np.ndarray]], 
                            cutoff: float, number_of_bins: int,
                            A_class:bool=False, B_class:bool=False):
        """
        Aggregate RBF data from a single container.

        Args:
            container: The container object with AtomPositionManager.
            rbf (Dict): The dictionary to store aggregated RBF data.
            cutoff (float): The maximum distance for RBF calculation.
            number_of_bins (int): The number of bins for RBF histogram.
        """
        rbf_container = container.AtomPositionManager.get_RBF(
            cutoff=cutoff, 
            number_of_bins=number_of_bins,
            bin_volume_normalize=False, 
            number_of_atoms_normalize=False, 
            density_normalize=False,
            A_class=A_class, 
            B_class=B_class,
        )

        for cluster_class, cluster_data in rbf_container.items():
            if cluster_class not in rbf:
                rbf[cluster_class] = {}
            
            for atom_label, atom_data in cluster_data.items():
                if atom_label not in rbf[cluster_class]:
                    rbf[cluster_class][atom_label] = np.zeros((2, number_of_bins))
                
                rbf[cluster_class][atom_label][0] = atom_data[0]  # bin centers
                rbf[cluster_class][atom_label][1] += atom_data[1]  # RBF values

    def _plot_rbf(self, cluster_class_name: str, 
                              rbf_data: Dict[str, np.ndarray], output_path: str):
        """
        Plot RBF for a specific cluster class.

        Args:
            cluster_class_name (str): The name of the cluster class.
            rbf_data (Dict): RBF data for the cluster class.
            output_path (str): The directory to save the plot.
        """
        # Calculate the integrals (sums) of RBFs
        integrals = {label: np.sum(rbf_values[1]) for label, rbf_values in rbf_data.items()}

        # Sort labels by their integral in descending order and select the top N=15
        top_labels = sorted(integrals, key=integrals.get, reverse=True)[:15]

        fig, ax = plt.subplots()
        ax.set_xlabel('Distance (Angstrom)')
        ax.set_ylabel('g(r)')
        ax.set_title(f'Radial Distribution Function {cluster_class_name}')

        # Plot all lines, but only label the top 15
        for atom_label, rbf_values in rbf_data.items():
            bin_centers, rbf_a = rbf_values
            color = self.element_colors.get(atom_label, tuple(np.random.rand(3)))
            
            # Add a label only if the atom_label is in the top N labels
            label = f'd({cluster_class_name}-{atom_label})' if atom_label in top_labels else None
            
            ax.plot(bin_centers, rbf_a, 'x-', alpha=0.8, color=color, label=label)
            ax.fill_between(bin_centers, rbf_a, alpha=0.1, color=color)

        ax.legend()
        plt.tight_layout()
        plt.savefig(f"{output_path}/RBF_{cluster_class_name}.png")
        plt.close(fig)

    def plot_value_distribution_by_group(
        self,
        values: List[float],
        labels: List[str],
        reference_values: Optional[Dict[str, float]] = None,
        output_filename: str = "value_distribution_by_group.png",
        title: str = "Distribution of Values by Group",
        x_label: str = "Value",
        y_label: str = "Groups",
        figsize: Tuple[int, int] = (14, 8),
        dpi: int = 300,
        point_alpha: float = 0.6,
        annotation_alpha: float = 0.7,
        annotation_fontsize: int = 8,
        reference_marker_size: int = 100
    ) -> str:
        """
        Plot the distribution of values for different groups, including optional reference values,
        and save the plot as a PNG file.

        This function creates a scatter plot where each group (derived from the labels) is represented
        on a separate row. It can also include reference values for each group if provided.

        Args:
            values (List[float]): Values for each data point.
            labels (List[str]): Labels for each data point in the format "group_id".
            reference_values (Optional[Dict[str, float]]): Reference values for each group. Default is None.
            output_filename (str): Name of the output PNG file. Default is "value_distribution_by_group.png".
            title (str): Title of the plot. Default is "Distribution of Values by Group".
            x_label (str): Label for the x-axis. Default is "Value".
            y_label (str): Label for the y-axis. Default is "Groups".
            figsize (Tuple[int, int]): Figure size in inches. Default is (14, 8).
            dpi (int): DPI for the output image. Default is 300.
            point_alpha (float): Alpha value for data points. Default is 0.6.
            annotation_alpha (float): Alpha value for annotations. Default is 0.7.
            annotation_fontsize (int): Font size for annotations. Default is 8.
            reference_marker_size (int): Size of the marker for reference values. Default is 100.

        Returns:
            str: The absolute path of the saved PNG file.

        Raises:
            ValueError: If the lengths of values and labels do not match.

        Note:
            This function saves the visualization as a PNG file, useful for batch processing
            and including in reports or presentations in data analysis workflows.
        """
        if len(values) != len(labels):
            raise ValueError("The lengths of values and labels must be the same.")

        # Group data by group name
        groups = defaultdict(list)
        for value, label in zip(values, labels):
            group = label.split('_')[0]
            groups[group].append((value, label))

        # Set up the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors for each group
        colors = plt.cm.rainbow(plt.Normalize()(range(len(groups))))

        # Plot data for each group
        for i, (group, data) in enumerate(groups.items()):
            group_values, point_labels = zip(*data)
            y = [i] * len(group_values)
            
            # Plot points
            ax.scatter(group_values, y, c=[colors[i]], label=group, alpha=point_alpha)

            # Add annotations for each point
            for x, y, label in zip(group_values, y, point_labels):
                ax.annotate(label, (x, y), xytext=(5, 0), textcoords='offset points', 
                            fontsize=annotation_fontsize, alpha=annotation_alpha, 
                            rotation=45, ha='left', va='bottom')
            
            # Plot reference value if available
            if reference_values and group in reference_values:
                ref_value = reference_values[group]
                ax.scatter(ref_value, i, c=[colors[i]], marker='s', 
                           s=reference_marker_size, edgecolors='black')
                ax.annotate(f'{group}_ref', (ref_value, i), xytext=(5, 5), 
                            textcoords='offset points', fontsize=10, fontweight='bold')

        # Configure axes and labels
        ax.set_yticks(range(len(groups)))
        ax.set_yticklabels(groups.keys())
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        
        # Add legend and adjust layout
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()

        # Save the plot as a PNG file
        plt.savefig(output_filename, dpi=dpi, bbox_inches='tight')
        plt.close(fig)  # Close the figure to free up memory

        # Return the full path of the saved file
        return os.path.abspath(output_filename)

    def plot_manifold(self, features: np.ndarray, response: np.ndarray, 
                      output_path: str = None, save: bool = True, 
                      verbose: bool = True) -> None:
        """
        Plot the manifold of the data using T-SNE and PCA, along with the response variable.

        Args:
            features (np.ndarray): Feature array (typically composition data).
            response (np.ndarray): Response array (typically energy or error data).
            output_path (str, optional): Path to save the plot.
            save (bool): Whether to save the plot to a file.
            verbose (bool): Whether to print additional information.
        """
        print("Generating manifold plots using T-SNE and PCA...")

        tsne = TSNE(n_components=2, random_state=42)
        tsne_results = tsne.fit_transform(features)

        pca = PCA(n_components=3)
        pca_results = pca.fit_transform(features)
        explained_variance = pca.explained_variance_ratio_

        fig, ax = plt.subplots(2, 2, figsize=(20, 20))

        # T-SNE plot
        sc = ax[0, 0].scatter(tsne_results[:, 0], tsne_results[:, 1], c=response, cmap='viridis')
        ax[0, 0].set_title('T-SNE Projection')
        ax[0, 0].set_xlabel('T-SNE Component 1')
        ax[0, 0].set_ylabel('T-SNE Component 2')
        plt.colorbar(sc, ax=ax[0, 0], label='Response')

        # PCA plot (2D projection)
        sc_pca = ax[0, 1].scatter(pca_results[:, 0], pca_results[:, 1], c=response, cmap='viridis')
        ax[0, 1].set_title('PCA Projection (2D)')
        ax[0, 1].set_xlabel(f'PCA Component 1 ({explained_variance[0]*100:.2f}% variance)')
        ax[0, 1].set_ylabel(f'PCA Component 2 ({explained_variance[1]*100:.2f}% variance)')
        plt.colorbar(sc_pca, ax=ax[0, 1], label='Response')

        # PCA plot (3D projection)
        ax_3d = fig.add_subplot(223, projection='3d')
        sc_pca_3d = ax_3d.scatter(pca_results[:, 0], pca_results[:, 1], pca_results[:, 2], 
                                  c=response, cmap='viridis')
        ax_3d.set_title('PCA Projection (3D)')
        ax_3d.set_xlabel(f'PC1 ({explained_variance[0]*100:.2f}%)')
        ax_3d.set_ylabel(f'PC2 ({explained_variance[1]*100:.2f}%)')
        ax_3d.set_zlabel(f'PC3 ({explained_variance[2]*100:.2f}%)')
        plt.colorbar(sc_pca_3d, ax=ax_3d, label='Response')

        # Response plot
        ax[1, 1].plot(response, 'o-', c='#1f77b4')
        RMSE = np.sqrt(np.mean(response**2))
        ax[1, 1].axhline(y=RMSE, color='r', linestyle='--', label=f'RMSE: {RMSE:.5f}')
        ax[1, 1].set_title('Response Distribution')
        ax[1, 1].set_xlabel('Index')
        ax[1, 1].set_ylabel('Response')
        ax[1, 1].legend()
        plt.tight_layout()

        if save:
            if not output_path:
                output_path = '.'
            plt.savefig(f'{output_path}/manifold_plot.png', dpi=300)
            if verbose:
                print(f"Manifold plot saved to {output_path}/manifold_plot.png")
        else:
            plt.show()

        if verbose:
            print(f"PCA explained variance ratios: {explained_variance}")
