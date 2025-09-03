try:
    from ...IO.structure_handling_tools.AtomPosition import AtomPosition
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys
    
try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:

    import pickle, os
    from typing import Dict, List, Tuple, Union
    from tqdm import tqdm

    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    from matplotlib.colors import LogNorm
    
    from mpl_toolkits.mplot3d import Axes3D

    from scipy.optimize import leastsq
    from scipy.constants import Boltzmann, Avogadro, hbar, pi
    from scipy.stats import linregress, gaussian_kde

except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing scipy.optimize.leastsq : {str(e)}\n")
    del sys

class Conductivity_builder(BasePartition):
    """
    A class that computes and analyzes the mean squared displacement (MSD) of ions
    from molecular dynamics (MD) trajectories to estimate diffusion coefficients 
    and related properties.

    This class provides methods to:
    - Extract atom positions and labels from MD simulation containers.
    - Compute the MSD of ions over time.
    - Identify the diffusive regime and compute the diffusion coefficient using the Einstein relation.
    - Visualize results through line plots and violin plots.
    
    Mathematical Background:
    -------------------------
    The diffusion coefficient D in three dimensions can be estimated from the MSD(t)
    using the Einstein relation:
    
        MSD(t) ≈ 2 * d * D * t

    where:
    - MSD(t) is the mean squared displacement as a function of time,
    - d is the dimensionality of the system (d = 3 for 3D),
    - D is the diffusion coefficient.
    
    Rearranging this:
    
        D = slope(MSD(t)) / (2 * d)
        
    The slope(MSD(t)) is obtained by fitting a linear function to the MSD vs. time data 
    in the diffusive regime (long-time behavior).
    """
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)
        
    @staticmethod
    def plot_violin(ax: plt.Axes, data: List[np.ndarray], positions: List[float], width: float):
        """
        Create custom violin plots on the specified axis using Gaussian kernel density estimates (KDE).

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The matplotlib axes where the violin plot will be drawn.
        data : List[np.ndarray]
            A list of arrays, each representing a distribution of values for one violin plot.
        positions : List[float]
            The x-axis positions corresponding to each violin.
        width : float
            The width scaling factor for the violins.

        Notes
        -----
        This method uses `gaussian_kde` to compute a KDE of the data and then
        constructs a violin by mirroring the KDE curve.
        """
        for d, p in zip(data, positions):
            kde = gaussian_kde(d)
            x = np.linspace(np.min(d), np.max(d), 100)
            v = kde.evaluate(x)
            # Normalize the KDE so that the maximum width is 'width'
            v = v / v.max() * width
            ax.fill_betweenx(x, p - v, p + v, alpha=0.7)

    def calculate_diffusion_coefficient(self, 
                                        msd: np.ndarray, 
                                        time_step: float, 
                                        dimensionality: int = 3,
                                        weight_data: bool = True, 
                                        verbose: bool = False
                                       ) -> Tuple[float, Tuple[int, int], float, float, float]:
        """
        Calculate the diffusion coefficient from MSD data by finding the best linear fit.

        Parameters
        ----------
        msd : np.ndarray
            Array of MSD values over time.
        time_step : float
            The time interval between consecutive MSD data points.
        dimensionality : int, optional
            The dimensionality of the system, default is 3.
        weight_data : bool, optional
            If True, slightly favor fits over longer time intervals.
        verbose : bool, optional
            If True, print detailed fitting information.

        Returns
        -------
        D : float
            Estimated diffusion coefficient.
        best_interval : tuple(int, int)
            The start and end indices of the best fit interval.
        best_slope : float
            Slope of the linear fit MSD(t) = slope * t + intercept.
        best_intercept : float
            Intercept from the linear fit.
        best_r_squared : float
            R² value (coefficient of determination) for the best linear fit.

        Notes
        -----
        The Einstein relation in 3D: MSD(t) = 6 * D * t, hence D = slope / 6 for 3D.
        More generally, D = slope/(2*d).
        """
        time = np.arange(len(msd)) * time_step
        best_slope = 0.0
        best_r_squared = -np.inf
        best_interval = (0, len(msd))
        best_intercept = 0.0

        half_length = len(msd) // 2
        interval_min_length = max(1, len(msd) // 10)

        for start in range(half_length):
            for end in range(start + interval_min_length, len(msd)):
                slope, intercept, r_value, _, _ = linregress(time[start:end], msd[start:end])
                r_squared = r_value ** 2

                # weighting
                if weight_data:
                    interval_length_factor = (end - start) / len(msd)
                    r_squared += interval_length_factor * 1e-1

                if r_squared > best_r_squared:
                    best_r_squared = r_squared
                    best_slope = slope
                    best_intercept = intercept
                    best_interval = (start, end)

        D = best_slope / (2 * dimensionality)

        if verbose:
            print(f"D: {D} Chosen interval: {best_interval}, slope: {best_slope:.2e}, R²: {best_r_squared:.2f} dimensionality:{dimensionality}")

        return D, best_interval, best_slope, best_intercept, best_r_squared

    def plot_msd(self, conductivity_data: Dict, time_step: float, max_ions_to_plot: int = 100, output_folder="output_plots"):
        """
        Plot the MSD results, including anisotropic MSD components (MSD_x, MSD_y, MSD_z) and violin plots.
        Instead of showing the plots, they are saved to the specified output folder.

        Parameters
        ----------
        conductivity_data : dict
            A dictionary with the computed MSD data, including:
            {
              'msd': {ion_label: np.ndarray (n_ions, n_times)},
              'MSD': {ion_label: np.ndarray (n_times)},
              'MSD_by_dim': {ion_label: np.ndarray (n_times, 3)},
              'labels': np.ndarray,
              'V': float (cell volume)
            }
        time_step : float
            The simulation time step used in the trajectory.
        max_ions_to_plot : int, optional
            Maximum number of individual ion trajectories to plot.
        output_folder : str
            Path to the directory where the plots will be saved.

        Notes
        -----
        The left subplot shows:
        - Individual ion MSD curves (up to max_ions_to_plot).
        - The average MSD curve and its linear fit region.
        - MSD_x, MSD_y, and MSD_z curves for anisotropic analysis.

        The right subplot shows violin plots representing the distribution of MSD values at selected times.
        """
        os.makedirs(output_folder, exist_ok=True)

        plt.style.use('seaborn-whitegrid' if 'seaborn-whitegrid' in plt.style.available else 'default')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': 'gray',
            'axes.grid': True,
            'grid.alpha': 0.3,
            'grid.color': 'gray',
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10
        })

        for ion_type in conductivity_data['msd']:
            msd_data = conductivity_data['msd'][ion_type]  # shape (n_ions, n_times)
            msd_by_dim_avg = conductivity_data['MSD_by_dim'][ion_type]  # shape (n_times, 3)
            avg_msd = conductivity_data['MSD'][ion_type]  # shape (n_times,)
            
            fig = plt.figure(figsize=(20, 10))
            gs = GridSpec(1, 2, width_ratios=[2, 1])

            ax1 = fig.add_subplot(gs[0, 0])
            ax2 = fig.add_subplot(gs[0, 1])
            fig.suptitle(f'MSD Analysis for Ion Type {ion_type}', fontsize=16)

            time = np.arange(msd_data.shape[1]) * time_step
            colors = plt.cm.viridis(np.linspace(0, 1, min(msd_data.shape[0], max_ions_to_plot)))

            # Plot individual ion MSD curves (total)
            for ion_index in range(min(msd_data.shape[0], max_ions_to_plot)):
                ax1.plot(time, msd_data[ion_index], alpha=0.1, linewidth=1, color=colors[ion_index])

            ax1.set_xlabel('Time')
            ax1.set_ylabel('MSD')
            ax1.set_title(f'Individual Ion Trajectories ({min(msd_data.shape[0], max_ions_to_plot)} shown)')

            # Violin plots for distribution
            num_violins = 15
            times_to_plot = np.linspace(0, msd_data.shape[1] - 1, num_violins, dtype=int)
            data_to_plot = [msd_data[:, t_idx] for t_idx in times_to_plot]
            positions = [t_idx * time_step for t_idx in times_to_plot]
            self.plot_violin(ax2, data_to_plot, positions, width=6.1)

            ax2.set_xlabel('Time')
            ax2.set_ylabel('MSD')
            ax2.set_title('Violin Plot of MSD at Different Times')

            # Plot average total MSD
            ax1.plot(time, avg_msd, color='red', linewidth=2, label='Average MSD (Total)')

            # Plot anisotropic MSD components
            ax1.plot(time, msd_by_dim_avg[:, 0], '--', color='blue', label='MSD_x')
            ax1.plot(time, msd_by_dim_avg[:, 1], '--', color='green', label='MSD_y')
            ax1.plot(time, msd_by_dim_avg[:, 2], '--', color='orange', label='MSD_z')

            # Compute diffusion coefficient from the total average MSD
            #D, best_interval, best_slope, best_intercept, best_r_squared = self.calculate_diffusion_coefficient(avg_msd, time_step)
            D, best_interval, best_slope, best_intercept, best_r_squared = \
                            conductivity_data['D'][ion_type], conductivity_data['best_interval'][ion_type], conductivity_data['best_slope'][ion_type], \
                            conductivity_data['best_intercept'][ion_type], conductivity_data['best_r_squared'][ion_type]

            fit_time = time[best_interval[0]:best_interval[1]]
            fit_line = best_slope * fit_time + best_intercept
            ax1.plot(fit_time, fit_line, 'k--', label=f'Best Fit: R² = {best_r_squared:.2f}')
            ax1.axvspan(fit_time[0], fit_time[-1], color='gray', alpha=0.2, label='Linear Fit Interval')
            ax1.legend()

            max_msd_val = np.max(msd_data)
            min_msd_val = np.min(msd_data)
            final_avg_msd = avg_msd[-1]

            # Annotate statistics
            stats_text = (
                f'Max MSD: {max_msd_val:.2e}\n'
                f'Min MSD: {min_msd_val:.2e}\n'
                f'Final Avg MSD: {final_avg_msd:.2e}\n'
                f'Diffusion Coefficient: {D:.2e}'
            )
            ax1.text(0.05, 0.95, stats_text, transform=ax1.transAxes, fontsize=10,
                     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            plt.tight_layout(rect=[0, 0, 1, 0.96])

            # Save the plot
            plot_file = os.path.join(output_folder, f"MSD_plot_{ion_type}.png")
            plt.savefig(plot_file)
            plt.close(fig)

    @staticmethod
    def _calculate_ionic_conductivity(D, q, N, V, T):
        """
        Calculate the ionic conductivity from diffusion coefficients, charges, and thermodynamic parameters.

        Parameters
        ----------
        D : np.ndarray
            Diffusion coefficients for the ionic species.
        q : np.ndarray
            Charges of the ions.
        N : np.ndarray
            Number of ions.
        V : float
            The volume of the simulation cell.
        T : float
            Temperature.

        Returns
        -------
        conductivity : float
            The calculated ionic conductivity.
        """
        return np.sum(q*q * N * D)/ (V*np.Kb*T)

    def save_simulation_data(self, conductivity_data: Dict, output_folder="output_data"):
        """
        Save all relevant simulation data into separate files in a designated output folder.

        Parameters:
            conductivity_data (dict): Dictionary containing the computed MSD data and other properties.
                Includes keys:
                - 'r': Atomic positions.
                - 'labels': Labels corresponding to chemical species.
                - 't': Time data for each species.
                - 'MSD': Mean squared displacement (total) for each species.
                - 'MSD_by_dim': Mean squared displacement by dimension (x, y, z).
                - 'D': Diffusion coefficients for each species.
            output_folder (str): Path to the directory where all output files will be stored.
        """
        # Ensure the output directory exists
        os.makedirs(output_folder, exist_ok=True)

        # Save MSD and diffusion data for each chemical species
        for cID in tqdm(conductivity_data['msd'], desc="Saving Data for Each Species", unit="species"):
            # Save the total MSD for the current species
            msd_total_file = os.path.join(output_folder, f"MSD_total_{cID}.txt")
            np.savetxt(
                msd_total_file,
                np.column_stack((conductivity_data['t'][cID], conductivity_data['MSD'][cID])),
                header="time(fs) MSD_total(A^2)",
                comments=""
            )

            # Save the MSD by dimensions (x, y, z) for the current species
            msd_by_dim_file = os.path.join(output_folder, f"MSD_by_dim_{cID}.txt")
            np.savetxt(
                msd_by_dim_file,
                np.column_stack((conductivity_data['t'][cID], conductivity_data['MSD_by_dim'][cID])),
                header="time(fs) MSD_x(A^2) MSD_y(A^2) MSD_z(A^2)",
                comments=""
            )

            # Append the diffusion coefficient to a shared text file
            diffusion_coefficients_file = os.path.join(output_folder, "diffusion_coefficients.txt")
            with open(diffusion_coefficients_file, "a") as f:
                f.write(f"{cID}: D = {conductivity_data['D'][cID]:.6e} A^2/fs (or native units) : D = {conductivity_data['D'][cID]*1e-1:.6e} cm^2/s : D = {conductivity_data['D'][cID]*1e-5:.6e} m^2/s\n")

        # Save the entire conductivity_data dictionary as a compressed .npz file
        data_file = os.path.join(output_folder, "conductivity_data.npz")
        np.savez(data_file, **conductivity_data)

        # Print confirmation of successful save
        print(f"All simulation data successfully saved in the folder: '{output_folder}'")

    def handle_conductivity_analysis(self, analysis_parameters: dict):
        """
        Perform conductivity-related analysis for a given set of parameters.

        This method:
        1. Extracts the positions and labels.
        2. Computes MSD and diffusion coefficients for specified chemical species.
        3. Generates plots for MSD results (including anisotropic components).
        
        Parameters
        ----------
        analysis_parameters : dict
            Dictionary with 'ANALYSIS' key, containing:
            {
              'T': Temperature,
              'q': Array of charges,
              'ID': List of chemical species,
              'dt': Time step,
              'output_path': Path to output (if needed),
              'verbose': Boolean for verbose output
            }

        Example
        -------
        analysis_parameters = {
            'ANALYSIS': {
                'T': 300.0,
                'q': np.array([...]),
                'ID': ['Li', 'O'],
                'dt': 0.5,
                'verbose': True
            }
        }

        Notes
        -----
        The computed diffusion coefficients are derived from the MSD curves 
        using the Einstein relation, and the results are visualized via
        `plot_msd()`.
        """

        # Initialize a dictionary to store all conductivity-related data.
        conductivity_data = {}

        # Loop over all keys in the analysis parameters.
        for v_key, v in analysis_parameters.items():
            verbose = v.get('verbose', False)  # Retrieve verbosity flag, default is False

            # Process only the analysis-related parameters.
            if v_key.upper() == 'ANALYSIS':
                # Retrieve various parameters from the analysis configuration.
                output_folder = v.get('output_path', 'diffusion_out')  # Output folder for saving results
                T = v['T']                  # Temperature
                atoms_charge = v['q']       # Atomic charge(s)
                chemical_ID = v['ID']       # Chemical identifiers; can be names or indices
                dt = v['dt']                # Time step (in appropriate time units, e.g., fs)
                dimensionality = v.get('dimensionality', None)  # Optional dimensionality parameter

                # Retrieve mean square displacement (MSD) data, labels, and additional variable V.
                conductivity_data['r'], conductivity_data['labels'], conductivity_data['V'] = self.get_msd_data(chemical_ID)
                
                # Initialize dictionaries to store computed data for each species.
                conductivity_data['msd'] = {}           # MSD for each species (total per ion)
                conductivity_data['t'] = {}             # Time array corresponding to MSD data
                conductivity_data['D'] = {}             # Diffusion coefficient for each species
                conductivity_data['best_interval'] = {} # Best time interval used in fitting
                conductivity_data['best_slope'] = {}    # Slope from the MSD fit (related to diffusion)
                conductivity_data['best_intercept'] = {}# Intercept from the MSD fit
                conductivity_data['best_r_squared'] = {}# R-squared value for the fit quality
                conductivity_data['MSD'] = {}           # Averaged MSD over all particles
                conductivity_data['MSD_by_dim'] = {}    # MSD computed per dimension

                # Check if chemical_ID is provided as a list.
                if isinstance(chemical_ID, list):
                    try:
                        # Try converting the first element to float. If successful,
                        # assume chemical_ID is a list of indices.
                        float(chemical_ID[0])
                        # Convert to a NumPy array of integers and wrap it in a list.
                        chemical_ID = np.array(chemical_ID, dtype=np.int64)
                        chemical_ID_list = [chemical_ID]
                    except:
                        # Otherwise, assume chemical_ID is a list of chemical names.
                        chemical_ID_list = chemical_ID

                # Loop over each chemical identifier in the list with progress tracking.
                for cID_i, cID in tqdm(enumerate(chemical_ID_list), total=len(chemical_ID), desc="Processing Chemical Species", unit="species"):

                    # Determine positions for the current chemical species:
                    # If cID is a string, filter based on labels.
                    if isinstance(cID, str):
                        name = cID
                        pos_cID = conductivity_data['r'][conductivity_data['labels'] == cID]
                    else:
                        # For indices (or list of indices), use advanced indexing.
                        # Debug print to show the shape of the positions array and the indices used.
                        name = cID_i
                        pos_cID = conductivity_data['r'][cID, :, :]

                    # Compute the Mean Squared Displacement (MSD) data.
                    # The MSD function returns:
                    #   Dt_r       : Time intervals
                    #   MSD_total  : Averaged total MSD (across all ions)
                    #   MSD_by_dim : MSD computed per dimension (e.g., x, y, z)
                    Dt_r, MSD_total, MSD_by_dim = self.MSD(pos_cID, lag=True, fft=True)
                    # Note: The comments indicate that Dt_r might be np.arange(1, n_time - 1) and
                    # MSD_by_dim has a shape of (particles, frames-2, dimensions).

                    # Store the time data in appropriate units (e.g., femtoseconds).
                    conductivity_data['t'][name] = Dt_r * dt

                    # Compute the MSD for each ion by summing over the spatial dimensions.
                    # msd_data shape: (n_ions, n_times)
                    msd_data = np.sum(MSD_by_dim, axis=-1)
                    conductivity_data['msd'][name] = msd_data
                    conductivity_data['MSD'][name] = MSD_total  # Store the averaged total MSD
                    # Compute and store the averaged MSD per dimension (mean over ions).
                    conductivity_data['MSD_by_dim'][name] = np.mean(MSD_by_dim, axis=0)

                    # If dimensionality is not provided, determine it based on the relative contribution
                    # of each dimension (using a 5% relevance criterion).
                    if dimensionality is None:
                        avg_MSD_by_dim = np.mean(MSD_by_dim, axis=(0, 1))
                        dimensionality = int(np.sum((avg_MSD_by_dim / np.sum(avg_MSD_by_dim)) > 0.05))
                        # Optionally include additional logging if verbose is True.

                    # Calculate the diffusion coefficient and related fitting parameters using the MSD data.
                    D, best_interval, best_slope, best_intercept, best_r_squared = \
                        self.calculate_diffusion_coefficient(conductivity_data['MSD'][name], dt, dimensionality=dimensionality, verbose=verbose)

                    # Store the computed diffusion coefficients and fitting parameters.
                    conductivity_data['D'][name] = D
                    conductivity_data['best_interval'][name] = best_interval
                    conductivity_data['best_slope'][name] = best_slope
                    conductivity_data['best_intercept'][name] = best_intercept
                    conductivity_data['best_r_squared'][name] = best_r_squared

                # After processing all species, save the simulation data to the output folder.
                self.save_simulation_data(conductivity_data, output_folder=output_folder)
                # Generate and display/save the MSD plots using the computed data.
                self.plot_msd(conductivity_data, time_step=dt)