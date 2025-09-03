try:
    import numpy as np
    from itertools import cycle
    import copy, os
    from tqdm import tqdm
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing : {str(e)}\n")
    del sys
    
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing matplotlib.pyplot: {str(e)}\n")
    del sys
    
try:
    from scipy.stats import iqr
    from scipy.interpolate import make_interp_spline
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing itertools: {str(e)}\n")
    del sys

class MolecularDynamic_builder(BasePartition):
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
        self._molecule_template = {}
        self._density = None
        self._cluster_lattice_vectors = None

        super().__init__(*args, **kwargs)

    def _calculate_reference_values(self, container, reference):
        """
        Calculate reference values based on the specified reference type.

        Args:
            container: The container holding atom positions and lattice vectors.
            reference (str): The reference type ('a', 'b', 'c', 'x', 'y', 'z').

        Returns:
            numpy.ndarray: Calculated reference values.
        """
        if type(reference) is str and reference.upper() in ['A', 'B', 'C']:
            lv_index = {'A': 0, 'B': 1, 'C': 2}[reference.upper()]
            lv = container.AtomPositionManager.latticeVectors[:, lv_index]
            return np.dot(container.AtomPositionManager.atomPositions, lv / np.linalg.norm(lv))
        
        if type(reference) is str and reference.upper() in ['X', 'Y', 'Z']:
            return container.AtomPositionManager.atomPositions[:, {'X': 0, 'Y': 1, 'Z': 2}[reference.upper()]]
    
        return np.zeros(container.AtomPositionManager.atomCount)

    '''
    def get_positions(self, fractional:bool=False, wrap:bool=False):
        """
        """
        if wrap:
            for container_i, container in enumerate(self.containers):
                container.AtomPositionManager.wrap()

        if fractional:
            return np.array([container.AtomPositionManager.atomPositions_fractional  for container_i, container in enumerate(self.containers)], dtype=np.float64)
        else:
            return np.array([container.AtomPositionManager.atomPositions  for container_i, container in enumerate(self.containers)], dtype=np.float64)
    '''

    def get_count_species(self, sigma:float=None) -> list:
        """
        """
        count_species = []
        for container_i, container in enumerate(self.containers):
            count_species.append( container.AtomPositionManager.count_species(sigma) )

        return count_species

    def get_evaluation(self, ff_energy_tag:str='ff-energy', ff_forces_tag:str='ff-forces', ):
        """
        Collects and organizes energy and force data for training and validation.

        This method compiles energies and forces from the AtomPositionManager instances
        associated with each container in the current EvaluationManager. It organizes
        this data into a structured format suitable for comparison and further analysis.

        Parameters
        ----------
        ff_energy_tag : str, optional
            The tag used to identify force field energy data within the AtomPositionManager.
            Defaults to 'ff-energy'.
        ff_forces_tag : str, optional
            The tag used to identify force field forces data within the AtomPositionManager.
            Defaults to 'ff-forces'.

        Returns
        -------
        dict
            A dictionary containing structured energy and force data for training and
            validation purposes. The data includes reference and FF-calculated values
            for energies and forces, segregated by atomic species.

        Notes
        -----
        The method assumes that each container's AtomPositionManager has attributes
        for energies and forces tagged according to `ff_energy_tag` and `ff_forces_tag`.
        The energies and forces are expected to be accessible as numpy arrays.
        """

        # Validate input parameters
        ff_energy_tag = ff_energy_tag if isinstance(ff_energy_tag, str) else 'ff-energy'
        ff_forces_tag = ff_forces_tag if isinstance(ff_forces_tag, str) else 'ff-forces'

        # Initialize the data structure for collecting evaluation data
        N = len(self.containers)    
        data = {
            'E': {'train': np.zeros(N), 'validation': np.zeros(N)},
            'N': {'train': np.zeros(N), 'validation': np.zeros(N)},
            'F': {'train': {}, 'validation': {}}
        }

        # Iterate over each container to populate the data structure
        for c_i, c in enumerate(self.containers):
            # Energy data
            data['E']['train'][c_i] = c.AtomPositionManager.E
            data['E']['validation'][c_i] = getattr(c.AtomPositionManager, ff_energy_tag, None)

            # Atom count data
            data['N']['train'][c_i] = c.AtomPositionManager.atomCount
            data['N']['validation'][c_i] = c.AtomPositionManager.atomCount

            # Forces data, organized by unique atomic labels
            for ul in c.AtomPositionManager.uniqueAtomLabels:
                # Training forces
                if ul in data['F']['train']:
                    data['F']['train'][ul] = np.vstack((data['F']['train'][ul], c.AtomPositionManager.total_force[c.AtomPositionManager.atomLabelsList == ul]))
                else:
                    data['F']['train'][ul] = c.AtomPositionManager.total_force[c.AtomPositionManager.atomLabelsList == ul]

                # Validation forces
                if ul in data['F']['validation']:
                    data['F']['validation'][ul] = np.vstack((data['F']['validation'][ul], getattr(c.AtomPositionManager, ff_forces_tag, None)[c.AtomPositionManager.atomLabelsList == ul]))
                else:
                    data['F']['validation'][ul] = getattr(c.AtomPositionManager, ff_forces_tag, None)[c.AtomPositionManager.atomLabelsList == ul]

        # Ensure all force data is converted to numpy arrays for consistent handling
        for key, item in data['F']['validation'].items():
            data['F']['validation'][key] = np.array(item, np.float64 )
        for key, item in data['F']['train'].items():
            data['F']['train'][key] = np.array(item, np.float64 )

        data['E']['train'] = np.array( data['E']['train'], np.float64 )
        data['E']['validation'] = np.array( data['E']['validation'], np.float64 )

        data['N']['train'] = np.array( data['N']['train'], np.float64 )
        data['N']['validation'] = np.array( data['N']['validation'], np.float64 )

        return data

    def get_bond_tracking(self, sigma:float=1.2, reference:str='Z', verbose:bool=True):
        '''
        '''
        if verbose: print(f'bond_tracking :: Sigma: {sigma} reference {reference}')
        sigma = sigma if type(sigma) in [int, float] else 1.2
        initial_bonds = []
        c0 = self.containers[0].AtomPositionManager
        r_max = np.max( [c0.covalent_radii[a] for a in c0.uniqueAtomLabels] )
        for atomo_i, atomo in enumerate(c0.atomPositions):
            max_bond_lenth = (c0.covalent_radii[c0.atomLabelsList[atomo_i]]+r_max)*sigma
            neighbors = c0.find_all_neighbors_radius(x=atomo, r=max_bond_lenth)
            for neighbor in neighbors:
                distance = c0.distance( c0.atomPositions[atomo_i], c0.atomPositions[neighbor])
                if distance < (c0.covalent_radii[c0.atomLabelsList[atomo_i]]+c0.covalent_radii[c0.atomLabelsList[neighbor]])*sigma and distance > 0.4:
                    initial_bonds.append( [atomo_i, neighbor] )

        initial_bonds = np.array(initial_bonds, np.int64)
        data = np.zeros( (len(self.containers), initial_bonds.shape[0], 2) )

        for c_i, c in enumerate(self.containers):
            reference_pos = self._calculate_reference_values(c, reference='Z')
            for n_i, n in enumerate(initial_bonds):
                data[c_i, n_i, 0] = reference_pos[n[0]]
                data[c_i, n_i, 1] = c.AtomPositionManager.distance( c.AtomPositionManager.atomPositions[n[0]], c.AtomPositionManager.atomPositions[n[1]] )

        return {'initial_bonds_index':initial_bonds, 'bonds_data':data}

    def config_molecular_subgraph(self, container, container_i, pattern, verbose):
        """
        Function to be executed in parallel. Wraps the search_molecular_subgraph method.
        
        Parameters:
        - container_i (int): Index of the container in self.containers
        
        Returns:
        - Tuple of (container_i, search results)
        """

        if verbose:
            print(f'(%) >> Config {container_i} ({float(container_i)/len(self.containers)*100}%)')
        sms = container.AtomPositionManager.search_molecular_subgraph(pattern=pattern, verbose=verbose)

        return container_i, sms

    def get_molecular_graph_tracking(self, sigma: float = None, id_filter: bool = True, pattern: dict = None, 
                                     prevent_overlapping: bool = True, prevent_shared_nodes: bool = True,
                                     prevent_repeating: bool = True, backtracking: bool = False,
                                     parallel: bool = False, verbose: bool = True) -> list:
        """
        Analyzes molecular graphs to identify specific patterns, offering options for parallel processing,
        backtracking, and other custom filters.

        Parameters:
        - sigma (float): Optional parameter for algorithm adjustment.
        - id_filter (bool): If True, applies an identifier-based filter to the analysis.
        - pattern (dict): A dictionary specifying the pattern to look for in the molecular graphs.
        - prevent_overlapping (bool): If True, prevents overlapping in pattern matching.
        - prevent_shared_nodes (bool): Prevents shared nodes in the pattern matching process.
        - prevent_repeating (bool): If True, ensures that repeating patterns are not counted.
        - backtracking (bool): Enables or disables backtracking in the search process.
        - parallel (bool): If True, enables parallel processing to speed up the analysis.
        - verbose (bool): If True, prints detailed progress and debugging information.

        Returns:
        - list: A list of results from the molecular graph tracking process.

        Note:
        The method dynamically adjusts to either parallel or sequential execution based on the `parallel` flag.
        """
        try:
            from concurrent.futures import ProcessPoolExecutor, as_completed
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing : {str(e)}\n")
            del sys

        if verbose:
            print(f'Looking for specific pattern: {pattern}')
        
        # Determine execution mode and containers based on input flags
        executor_class = ProcessPoolExecutor if parallel else None  # None signifies sequential execution
        containers_to_process = [(len(self.containers), self.containers[-1])] if backtracking else enumerate(self.containers)

        # Execute the configuration for each container, either in parallel or sequentially
        if parallel:
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self.config_molecular_subgraph, container, container_i, pattern, verbose)
                           for container_i, container in containers_to_process]
                results = [future.result() for future in futures]
        else:
            # Para ejecución secuencial, simplemente iteramos sin usar 'executor'
            results = [self.config_molecular_subgraph(container, container_i, pattern, verbose) 
                       for container_i, container in containers_to_process]

        return results

    # ========== PLOTs ========== # # ========== PLOTs ========== # # ========== PLOTs ========== # # ========== PLOTs ========== # 
    # ========== PLOTs ========== # # ========== PLOTs ========== # # ========== PLOTs ========== # # ========== PLOTs ========== # 


    def plot_count(self, count_dict, output_path:str=None, save:bool=True, verbose:bool=True ):
        diferent_species = set()
        for c in count_dict:
            for specie in c:
                diferent_species.add(specie) 
        diferent_species = list(diferent_species)

        frames = len(count_dict)
        num_specie = len(diferent_species)

        specie_count_frame = np.zeros( (frames, num_specie) )
        for j, c in enumerate(count_dict):

            for i, n in enumerate(diferent_species):
                specie_count_frame[j][i] = c.get(n, 0)

        specie_count_frame = np.array(specie_count_frame, np.int32)

        # Apply a predefined style
        plt.style.use('seaborn-darkgrid')  # Try 'ggplot', 'seaborn', etc. for different styles

        # Set up cycles for line styles and colors
        line_styles = cycle(['-', '--', '-.', ':'])  # Example line styles
        colors = cycle(['blue', 'green', 'red', 'purple', 'brown', 'black'])  # Example colors

        # Plotting each line with customized styles
        for line, label in zip(specie_count_frame.T, diferent_species):
            plt.plot(line, label=label, linestyle=next(line_styles), color=next(colors), linewidth=2)

        # Adding title and axis labels with customized fonts
        plt.title('Counting Independent Graphs', fontsize=14, fontweight='bold')
        plt.xlabel('Frame', fontsize=12)
        plt.ylabel('Count', fontsize=12)

        # Enhancing the legend
        plt.legend(loc='upper left', frameon=True, framealpha=0.9, facecolor='white')

        # Adding gridlines
        plt.grid(True, linestyle='--', alpha=0.7)

        # Fine-tuning axes
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.ylim([0, np.max(specie_count_frame) + 1])  # Adjust according to your data

        plt.tight_layout()
        if save:
            plt.savefig(f'{output_path}/count_plot.png', dpi=100)
        plt.clf()

        if verbose:
            data_shape = specie_count_frame.shape
            print(f' >> Plot :: Counting Independent Graphs - data shape {data_shape}')

    def plot_evaluation(self, data, output_path:str=None, save:bool=True, verbose:bool=False):
        """
        Generates and optionally saves plots comparing training and validation data, along with error distributions.

        Parameters:
        - data (dict): A nested dictionary containing 'train' and 'validation' keys, each associated with another dictionary
                       where keys correspond to atom types and values are Nx3 arrays of forces.
        - output_path (str): The directory path where the plots should be saved. Required if save is True.
        - save (bool): If True, saves the generated plots to the specified output_path. Default is True.
        - verbose (bool): If True, prints additional information about the plotting process. Default is False.

        The function creates scatter plots comparing training and validation data for each atom type, accompanied by
        histograms and density plots of the data distributions. Additionally, it generates histograms of the root mean
        square error between training and validation data sets for each atom type.
        """
        def _plot(data_x, data_y, data_color, data_label:str='', data_output_path:str='.', data_max:float=10, data_min:float=0):
            fig = plt.figure(figsize=(8, 8))
            grid = plt.GridSpec(4, 4, hspace=0.5, wspace=0.5)

            # Extracting data for the current atom type and filtering based on specified conditions.
            #data_x = np.linalg.norm(data['F']['train'][n],axis=1)#data['F']['train'][n][:,0]
            #data_y = np.linalg.norm(data['F']['validation'][n],axis=1)#data['F']['validation'][n][:,0]
            condition = (data_x < data_max) & (data_y < data_max) & (data_x > data_min) & (data_y > data_min)

            data_x_filtered = data_x[condition]
            data_y_filtered = data_y[condition]
            
            # Main scatter plot of training vs. validation data.
            main_ax = fig.add_subplot(grid[:-1, 1:])
            main_ax.scatter(data_x_filtered, data_y_filtered, edgecolor=None, alpha=0.4, s=10, color=data_color)
            main_ax.set(xlabel=f'Train {data_label}', ylabel=f'Validation {data_label}', xlim=(data_min, data_max), ylim=(data_min, data_max))

            # Density histogram (vertical) for validation data.
            right_ax = fig.add_subplot(grid[:-1, 0], xticklabels=[], sharey=main_ax)
            right_ax.hist(data_y_filtered, bins=20, orientation='horizontal', color='darkblue', density=True)
            right_ax.set(xlabel='Density')
            right_ax.yaxis.tick_right()

            # Adding density curve for the histogram on the right.
            density_validation, bins = np.histogram(data_y_filtered, bins=20, density=True)
            bin_centers_validation = 0.5 * (bins[:-1] + bins[1:])
            right_ax.plot(density_validation, bin_centers_validation, '-', color='grey')

            # Density histogram (horizontal) for training data.
            bottom_ax = fig.add_subplot(grid[-1, 1:], yticklabels=[], sharex=main_ax)
            bottom_ax.hist(data_x_filtered, bins=20, color='darkred', density=True)
            bottom_ax.set(ylabel='Density')

            # Adding density curve for the histogram below.
            density_train, bins = np.histogram(data_x_filtered, bins=20, density=True)
            bin_centers_train = 0.5 * (bins[:-1] + bins[1:])
            bottom_ax.plot(bin_centers_train, density_train, '-', color='grey')

            if save:
                plt.savefig(f'{data_output_path}/evaluation_{data_label}_plot.png', dpi=100)
            plt.clf()

            # Error distribution plot for the current atom type.
            fig_error = plt.figure(figsize=(6, 4))
            error = np.abs(data_x_filtered - data_y_filtered)
            error = error[error < 1]

            ax_error = fig_error.add_subplot(1, 1, 1)
            ax_error.hist(error, bins=100, color=self.element_colors[n], density=True)
            ax_error.set(title=f'Error Distribution specie {data_label}', xlabel='Error', ylabel='Density', xlim=(0, 0.7))

            # Adding density curve for the error distribution.
            density_error, bins_error = np.histogram(error, bins=100, density=True)
            bin_centers_error = 0.5 * (bins_error[:-1] + bins_error[1:])
            ax_error.plot(bin_centers_error, density_error, '-', color='darkgreen')

            # Calculamos las estadísticas
            minimo = np.min(error)
            maximo = np.max(error)
            media = np.mean(error)
            mediana = np.median(error)
            desviacion_std = np.std(error)
            varianza = np.var(error)
            rango_iqr = iqr(error)
            cuartil1 = np.percentile(error, 25)
            cuartil3 = np.percentile(error, 75)
            coef_variacion = desviacion_std / media if media != 0 else 0  # Prevenir división por cero
            mae = np.mean(np.abs(data_x - data_y))
            rmsd = np.sqrt(np.mean(np.square(data_x - data_y)))
            nrmsd = rmsd / (np.max(data_x) - np.min(data_x))

            textstr = '\n'.join((
                f'Minimum: {minimo:.2f}',
                f'Maximum: {maximo:.2f}',
                f'Mean: {media:.2f}',
                f'Median: {mediana:.2f}',
                f'Standard Deviation: {desviacion_std:.2f}',
                f'Variance: {varianza:.2f}',
                f'IQR Range: {rango_iqr:.2f}',
                f'1st Quartile: {cuartil1:.2f}',
                f'3rd Quartile: {cuartil3:.2f}',
                f'Coefficient of Variation: {coef_variacion:.2f}', 
                f'MAE: {mae:.2f}',
                f'RMSD: {rmsd:.2f}',
                f'NRMSD: {nrmsd:.2f}' ))

            # Posicionamos el texto en el plot
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            plt.text(0.65, 0.95, textstr, transform=plt.gca().transAxes, fontsize=12,
                     verticalalignment='top', bbox=props)

            plt.tight_layout()
            if save:
                plt.savefig(f'{data_output_path}/evaluation_error_{data_label}_plot.png', dpi=100)
            plt.clf()

            if verbose:
                print(f' >> Plot :: Evaluation {n} - data shape: {data["F"]["train"][n].shape}')
                print(f' >> Plot :: Error Distribution {n} - data shape: {error.shape}')


        for n in data['F']['train']:

            _plot(  data_x=np.linalg.norm(data['F']['train'][n],axis=1), 
                    data_y=np.linalg.norm(data['F']['validation'][n],axis=1), 
                    data_color=self.element_colors[n], 
                    data_label=n, data_output_path=output_path, data_max=10, data_min=0)

        data_x= data['E']['train']/data['N']['train']
        data_y= data['E']['validation']/data['N']['validation']

        _plot(  data_x=data_x, 
                data_y=data_y, 
                data_color=(0.2, 0.2, 0.2), 
                data_label='E', data_output_path=output_path, data_max=np.max(data_x)*1.2, data_min=np.min(data_x)*0.8)
        if verbose:
            print(f' >> Plot :: Evaluation E - data shape: {data["E"]["train"].shape}')
            print(f' >> Plot :: Error Distribution E - data shape: {error.shape}')

    def plot_bond_tracking(self, bond_tracking_dict, output_path:str=None, window_size:float=None, save:bool=True, verbose:bool=True):
        
        def moving_average_std(x_values, z_value, mean_x, window_size):
            """Calculate moving average and moving standard deviation."""
            # Create bins based on the range of X values and the desired window size
            bins = np.arange(min(mean_x)-window_size/2, max(mean_x) + window_size, window_size)
            bin_indices = np.digitize(mean_x, bins)  # Assign each x to a bin

            bin_averages = {}
            bin_std = {}

            for i, b in enumerate(bins[1:]):
                bin_index = i+1
                #bin_index = 
                if bin_index not in bin_averages:
                    bin_averages[bin_index] = []
                if bin_index not in bin_std:
                    bin_std[bin_index] = []

                bin_averages[bin_index].append( x_values[bin_indices==bin_index] )
                bin_std[bin_index].append( z_value[bin_indices==bin_index] )
                
            mean_y = np.array([np.mean(n) for n in bin_averages.values()])
            std_y = np.array([np.mean(n) for n in bin_std.values()])
            x = (bins[1:]+bins[:-1])/2

            return x, mean_y, std_y

        label = np.array([[self.containers[0].AtomPositionManager.atomLabelsList[m] for m in n] for n in bond_tracking_dict['initial_bonds_index']])

        window_size = window_size if type(window_size) in [float, int] else 8.0  

        # Prepare to collect all y values and their std deviations
        all_y_values = []
        all_std_y = []

        for n in self.containers[0].AtomPositionManager.uniqueAtomLabels:

            # Improved plot aesthetics
            plt.figure(figsize=(10, 6))  # Set figure size
            plt.xlabel('X Axis Label')  # Set X axis label
            plt.ylabel('Y Axis Label')  # Set Y axis label
            plt.title(f'Distance from ({n})')  # Set title
            plt.grid(True)  # Add grid

            for m in self.containers[0].AtomPositionManager.uniqueAtomLabels:

                filter_ID = (label[:,0] == n) & (label[:,1] == m) 

                if np.sum(filter_ID) > 1:
                    # Calculate mean and standard deviation for x and y
                    mean_x = np.mean(bond_tracking_dict['bonds_data'], axis=0)[filter_ID, 0]
                    std_x = np.std(bond_tracking_dict['bonds_data'], axis=0)[filter_ID, 0]
                    mean_y = np.mean(bond_tracking_dict['bonds_data'], axis=0)[filter_ID, 1]
                    std_y = np.std(bond_tracking_dict['bonds_data'], axis=0)[filter_ID, 1]

                    # Collect y values and their std deviations
                    ma_y, ma_mean_y, ma_std_y = moving_average_std(mean_y, std_y, mean_x, window_size)

                    # Plotting the moving average line and shaded area
                    plt.fill_between( ma_y, ma_mean_y - ma_std_y, ma_mean_y + ma_std_y, color=self.element_colors[m], alpha=0.4)  # Shaded area for std deviation

                    # Plot with error bars
                    plt.errorbar(mean_x, mean_y, xerr=std_x, yerr=std_y, fmt='o', color=self.element_colors[m], alpha=0.5, label=f'd({n}-{m})', capsize=5) 
                    
            # Legend
            plt.legend()

            #Show plot
            if save:
                plt.savefig(f'{output_path}/bond_tracking_{n}_plot.png', dpi=100)

    def plot_forces(self, output_path=None, save=True, verbose=True):
        """
        Plot forces for each chemical species.

        Args:
            output_path (str): Directory to save the plots.
            save (bool): Whether to save the plots or not.
            verbose (bool): Whether to print verbose output.
        """
        if output_path is None:
            output_path = '.'

        # Crear un diccionario para almacenar las fuerzas de cada especie
        species_forces = {species: [] for species in self.containers[0].AtomPositionManager.uniqueAtomLabels}

        # Recopilar todas las fuerzas para cada especie a través de todas las configuraciones
        for config_num, container in enumerate(self.containers):
            for species in container.AtomPositionManager.uniqueAtomLabels:
                species_mask = container.AtomPositionManager.atomLabelsList == species
                forces = container.AtomPositionManager.total_force[species_mask]
                force_magnitudes = np.linalg.norm(forces, axis=1)
                species_forces[species].extend([(config_num, mag) for mag in force_magnitudes])

        # Crear una figura para cada especie
        for species, forces in species_forces.items():
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle(f'Force Analysis for {species}')

            # Desempaquetar los datos
            config_nums, force_mags = zip(*forces)

            # Scatter plot
            ax1.scatter(config_nums, force_mags, alpha=0.5, s=10, color=self.element_colors[species])
            ax1.set_xlabel('Configuration Number')
            ax1.set_ylabel('Force Magnitude (eV/Å)')
            ax1.set_title('Force Magnitude vs Configuration')

            # Histograma
            ax2.hist(force_mags, bins=50, alpha=0.7, color=self.element_colors[species])
            ax2.set_xlabel('Force Magnitude (eV/Å)')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Force Magnitude Distribution')

            plt.tight_layout()
            if save:
                plt.savefig(f'{output_path}/force_analysis_{species}.png', dpi=300)
            plt.close()

            if verbose:
                print(f'Plotted force analysis for {species}')






    # ====== ====== ====== PLOTING FUNCTIONS ====== ====== ====== #
    @staticmethod
    def setup_subplot(ax, xlabel, ylabel, title):
        """
        Set up the subplot with labels and title.

        Args:
            ax (matplotlib.axes.Axes): The axes object to setup.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
            title (str): Title of the subplot.
        """
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)

    def plot_path(self, positions, bins: int = 100, output_path: str = None, transparency: bool = True,
                  wrap: bool = False, save: bool = True, verbose: bool = True):
        """
        Plot atomic path trajectories and histograms.

        For each spatial dimension (x, y, z) and unique atomic label, this method generates:
          - A time-series plot of the atomic coordinate.
          - A histogram of the coordinate values.
          - 2D histograms for each pair of spatial dimensions.

        Parameters
        ----------
        positions : np.ndarray
            Array of atomic positions with shape (time, atoms, spatial dimensions).
        bins : int, optional
            Number of bins for histogram plotting (default: 100).
        output_path : str, optional
            Directory path to save the generated plots.
        transparency : bool, optional
            Save figures with a transparent background if True.
        wrap : bool, optional
            If True, plot using point markers; otherwise, use lines.
        save : bool, optional
            Save the generated plots to disk if True.
        verbose : bool, optional
            Print progress messages if True.

        Returns
        -------
        None
        """
        # Map spatial dimensions to axis labels.
        d_name = {0: 'x', 1: 'y', 2: 'z'}
        
        # Loop over each spatial dimension.
        for d in range(3):
            # Iterate over unique atomic labels from the first container.
            for u in self.containers[0].AtomPositionManager.uniqueAtomLabels:
                # Create a boolean mask for the current atomic label.
                mask = self.containers[0].AtomPositionManager.atomLabelsList == u

                # Create subplots: one for the trajectory and one for the histogram.
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
                color = self.containers[0].AtomPositionManager.element_colors[u]

                # Choose marker style based on wrapping option.
                mark = '.' if wrap else '-'
                # Plot the atomic trajectory for the current dimension.
                ax1.plot(positions[:, mask, d], mark, ms=1, alpha=0.1, lw=0.7, color=color)
                self.setup_subplot(ax1, 'Time', f'Path {d_name[d]}', f'Path ({d_name[d]}) for {u}')

                # Plot the histogram of the coordinate values.
                ax2.hist(positions[:, mask, d].flatten(), bins=bins, alpha=0.7,
                         orientation='vertical', color=color)
                self.setup_subplot(ax2, 'Frequency', f'Path {d_name[d]}', f'Histogram ({d_name[d]}) for {u}')

                plt.tight_layout()
                if save:
                    plt.savefig(f'{output_path}/PATH_TRACKING_{u}_{d_name[d]}.png', dpi=300,
                                transparent=transparency)

                plt.clf()

                if verbose:
                    print(f' >> Plot :: PATH_TRACKING ({u}-{d_name[d]}) - data shape {positions.shape}')

                # Loop over subsequent dimensions for 2D histogram plots.
                for d2 in range(d + 1, 3):
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

                    mark = '.' if wrap else '-'
                    # Plot the 2D trajectory between dimensions d and d2.
                    ax1.plot(positions[:, mask, d], positions[:, mask, d2],
                             mark, ms=0.7, color=color, alpha=0.1, lw=0.8)
                    self.setup_subplot(ax1, f'Path {d_name[d]}', f'Path {d_name[d2]}',
                                       f'Path ({d_name[d]}-{d_name[d2]}) for {u}')

                    # Create a 2D histogram for the pair of dimensions.
                    self.setup_subplot(ax2, f'Path {d_name[d]}', f'Path {d_name[d2]}',
                                       f'Histogram ({d_name[d]}-{d_name[d2]}) for {u}')
                    h = ax2.hist2d(positions[:, mask, d].flatten(),
                                   positions[:, mask, d2].flatten(), bins=bins, cmap='Blues')

                    # Add a colorbar corresponding to the 2D histogram.
                    cbar = fig.colorbar(h[3], ax=ax2)
                    cbar.set_label('Frequency')

                    plt.tight_layout()
                    if save:
                        plt.savefig(f'{output_path}/PATH_TRACKING_{u}_{d_name[d]}-{d_name[d2]}.png',
                                    dpi=300, transparent=transparency)

                    plt.clf()

                    if verbose:
                        print(f' >> Plot :: PATH_TRACKING ({u}-{d_name[d]}-{d_name[d2]}) - data shape {positions.shape}')

    def animated_RBF(self, output_path: str = None, duration: float = 0.1, save: bool = True, verbose: bool = True):
        """
        Create animated GIFs from Radial Basis Function (RBF) images for each unique atom label.

        This method iterates through each unique atom label provided by the first container's 
        AtomPositionManager. For each label, it collects corresponding RBF images from all containers,
        assembles them into an animated sequence, and optionally saves the resulting GIF to disk.
        
        If the specified output folder does not exist, it will be created automatically.

        Parameters
        ----------
        output_path : str, optional
            The directory path where the animated GIFs will be saved. If not provided, a default folder 
            named 'MD_RBF_GIF' will be created in the current directory.
        duration : float, optional
            The time duration (in seconds) that each frame will display in the animated GIF. Default is 0.1.
        save : bool, optional
            If True, the animated GIF for each atom label will be saved to disk. Default is True.
        verbose : bool, optional
            If True, progress information will be printed to the console. Default is True.

        Returns
        -------
        None

        Raises
        ------
        IOError
            If there is an error reading an image file or writing the animated GIF.
        """
        try:
            import imageio
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing imageio: {str(e)}\n")
            del sys

        # Determine the output directory for saving GIFs.
        output_dir = output_path if output_path is not None else "MD_RBF_GIF"

        # Create the output directory if it does not exist.
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            if verbose:
                print(f"Created directory: {output_dir}")

        # Retrieve the unique atom labels.
        labels = self.containers[0].AtomPositionManager.uniqueAtomLabels
        
        # Use tqdm progress bar if verbose is enabled.
        iterator = tqdm(labels, desc="Processing atom labels") if verbose else labels

        # Iterate over each unique atom label.
        for u in iterator:
            images = []  # List to store image frames for the current atom label.

            # Loop through all containers to load images corresponding to the current atom label.
            for container_i, container in enumerate(self.containers):
                # Construct the file path for the image in the current container.
                file_path = f'MD_RBF/{container_i}/RBF_{u}.png'
                # Read the image file and append it to the images list.
                images.append( imageio.imread(file_path) )

            # Save the animated GIF if the 'save' flag is enabled.
            if save:
                gif_filename = os.path.join(output_dir, f'MD_RBF{u}.gif')
                imageio.mimsave(gif_filename, images, duration=duration)

                # Optionally output a verbose message indicating successful save.
                if verbose:
                    print(f"Saved animated GIF for atom label '{u}' as {gif_filename}")

    # ====== ====== ====== HANDELER ====== ====== ====== #
    def handleMDAnalysis(self, values:list ):
        """
        Handle molecular dynamics analysis based on specified values.

        Args:
            values (list): List of analysis types to perform.
        """
        MDA_data = {}

        for plot in values: 
            
            if plot.upper() == 'PATH_TRACKING':
                MDA_data['positions'] = self.get_positions( fractional=values[plot].get('reference', False)=='fractional', wrap=values[plot].get('wrap', False) )
                self.plot_path( positions=MDA_data['positions'], output_path=values[plot].get('output_path', '.'), transparency=False, 
                                wrap=values[plot].get('wrap', False), verbose=values[plot].get('verbose', False) )

            if plot.upper() == 'RBF':
                # RADIAL basis function
                MDA_data['RBF'] = self.plot_RBF( A_class=False, B_class=False, individual=True )
                self.animated_RBF( output_path=values[plot].get('output_path', '.'), duration=0.1, save=True, verbose=values[plot].get('verbose', False), )


            if plot.upper() == 'COUNT_SPECIES':
                #  
                MDA_data['count'] = self.get_count_species(sigma=values[plot].get('sigma', None))
                self.plot_count( count_dict=MDA_data['count'], output_path=values[plot].get('output_path', '.'), save=True, verbose=values[plot].get('verbose', False) )

            if plot.upper() == 'EVALUATE_FF':
                MDA_data['evaluation'] = self.get_evaluation(
                                                    ff_energy_tag=values[plot].get('ff_energy_tag', 'ff-energy'),
                                                    ff_forces_tag=values[plot].get('ff_forces_tag', 'ff-forces'),
                                                            )
                self.plot_evaluation(data=MDA_data['evaluation'], output_path=values[plot].get('output_path', '.'), save=True, verbose=values[plot].get('verbose', False) )

            if plot.upper() == 'BOND_DISTANCE_TRACKING':
                MDA_data['bond_tracking'] = self.get_bond_tracking(sigma=values[plot].get('sigma', None), reference=values[plot].get('reference', None))
                self.plot_bond_tracking( bond_tracking_dict=MDA_data['bond_tracking'], output_path=values[plot].get('output_path', '.'), save=True, verbose=values[plot].get('verbose', False) )

            if plot.upper() == 'MOLECULE_FORMATION_TRACKING':
                container_list = MDA_data['molecule_formation_tracking'] = self.get_molecular_graph_tracking( sigma=values[plot].get('sigma', None), pattern=self.str_to_connectivity(values[plot].get('topology', None)) )
                self.containers = [ c for c_i, c in enumerate(self.containers) if c_i in container_list]

            if plot.upper() == 'FORCES':
                self.plot_forces(
                    output_path=values[plot].get('output_path', '.'),
                    save=values[plot].get('save', True),
                    verbose=values[plot].get('verbose', False)
                )
    