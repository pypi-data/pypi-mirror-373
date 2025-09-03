import numpy as np
import re
import os
import matplotlib.pyplot as plt

try:
    from ..master.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

class DOSManager(FileManager):
    """
    Class to manage and analyze Density of States (DOS) data from VASP's DOSCAR file.

    Inherits from FileManager and provides methods to read and parse total and partial DOS data,
    plot the DOS with improved styling, save the extracted data into text files in a descriptive folder,
    and perform additional analyses to understand the system at a physical and chemical level.
    """

    def __init__(self, file_location: str = None, name: str = None, **kwargs):
        """
        Initialize DOSManager with an optional file location and descriptive name.

        Parameters
        ----------
        file_location : str
            Path to the DOSCAR file.
        name : str
            Descriptive name for the DOS dataset.
        **kwargs : dict
            Additional keyword arguments for the base FileManager.
        """
        super().__init__(name=name, file_location=file_location)
        self._spin_polarized = None   # Determined from the DOS data (True/False)
        self._dos_total = None        # Dictionary to store total DOS data
        self._dos_ion = []            # List to store partial DOS data for each ion
        self._fermi_energy = None
        self._atom_count = None
        self._NEDOS = None
        self._system_name = None
        self._E_max = None
        self._E_min = None
        # Additional header information (e.g., volume, basis vectors, POTIM, TEBEG)
        self._volume = None
        self._basis_vectors = None
        self._potim = None
        self._tebeg = None
        # Store header info for later saving/analysis
        self._header_info = {}

    @property
    def fermi_energy(self):
        """Returns the Fermi energy."""
        return self._fermi_energy

    @property
    def spin_polarized(self):
        """Indicates whether the calculation is spin-polarized."""
        return self._spin_polarized

    @property
    def dos_total(self):
        """Returns the total DOS data."""
        return self._dos_total

    @property
    def dos_ion(self):
        """Returns the partial DOS data for each ion."""
        return self._dos_ion

    def _fix_number_format(self, line: str) -> str:
        """
        Correct the number format by inserting an 'E' in scientific notation when missing.

        Parameters
        ----------
        line : str
            A line from the DOSCAR file.

        Returns
        -------
        str
            The corrected line.
        """
        corrected_line = re.sub(
            r'(\d+\.\d+)([\+\-]\d+)',
            r'\1E\2',
            line.strip()
        )
        return corrected_line

    def _read_header(self, lines: list):
        """
        Parse the header information from the DOSCAR file.

        Expected header information includes the number of ions, partial DOS flag, volume, basis vectors,
        POTIM, initial temperature (TEBEG), system name, and energy grid parameters.

        Parameters
        ----------
        lines : list
            The first few lines of the DOSCAR file.
        """
        tokens = lines[0].split()
        self._atom_count = int(tokens[1])
        self._partial_DOS = int(tokens[2])
        
        try:
            tokens2 = list(map(float, lines[1].split()))
            self._volume = tokens2[0]
            self._basis_vectors = tokens2[1:4]  # Placeholder; adjust as needed
            if len(tokens2) > 4:
                self._potim = tokens2[4]
        except ValueError:
            pass
        
        try:
            self._tebeg = float(lines[2].strip())
        except ValueError:
            pass

        self._system_name = lines[4].strip()
        
        self._header_info = {
            "atom_count": self._atom_count,
            "partial_DOS": self._partial_DOS,
            "volume": self._volume,
            "basis_vectors": self._basis_vectors,
            "potim": self._potim,
            "tebeg": self._tebeg,
            "system_name": self._system_name
        }

        tokens6 = lines[5].split()
        self._E_max = float(tokens6[0])
        self._E_min = float(tokens6[1])
        self._NEDOS = int(float(tokens6[2]))
        self._fermi_energy = float(tokens6[3])

        self._header_info.update({
            "E_max": self._E_max,
            "E_min": self._E_min,
            "NEDOS": self._NEDOS,
            "fermi_energy": self._fermi_energy
        })

    def _read_total_dos(self, lines: list) -> dict:
        """
        Parse the total DOS data from the provided lines.

        Supports both spin-polarized (5 columns per line) and non-spin-polarized (3 columns) formats.

        Parameters
        ----------
        lines : list
            List of lines containing the total DOS data.

        Returns
        -------
        dict
            A dictionary containing arrays for energy, DOS, and integrated DOS.
        """
        energies = []
        dos_up = []
        dos_down = []
        integrated_dos_up = []
        integrated_dos_down = []

        for line_number, line in enumerate(lines, start=1):
            original_line = line.strip()
            corrected_line = self._fix_number_format(original_line)
            try:
                values = list(map(float, corrected_line.split()))
            except ValueError as e:
                print(f"Error parsing line {line_number}: {corrected_line}")
                raise e

            num_values = len(values)
            if num_values == 5:
                self._spin_polarized = True
                energies.append(values[0])
                dos_up.append(values[1])
                dos_down.append(values[2])
                integrated_dos_up.append(values[3])
                integrated_dos_down.append(values[4])
            elif num_values == 3:
                self._spin_polarized = False
                energies.append(values[0])
                dos_up.append(values[1])
                integrated_dos_up.append(values[2])
            else:
                raise ValueError(f"Unexpected number of columns in total DOS: {num_values}")

        dos_total = {
            'energies': np.array(energies),
            'dos_up': np.array(dos_up),
            'integrated_dos_up': np.array(integrated_dos_up)
        }
        if self._spin_polarized:
            dos_total['dos_down'] = np.array(dos_down)
            dos_total['integrated_dos_down'] = np.array(integrated_dos_down)

        return dos_total

    def _read_ion_dos(self, lines: list) -> dict:
        """
        Parse the partial DOS data for a single ion.

        Auto-detects the DOS format based on the number of data columns and returns the ion's DOS data.

        Parameters
        ----------
        lines : list
            Lines corresponding to the ion DOS block (header + NEDOS data lines).

        Returns
        -------
        dict
            Dictionary with the ion's DOS data stored as NumPy arrays.
        """
        header = lines[0].strip()
        try:
            _, _, NEDOS, _, _ = map(float, header.split())
        except ValueError as e:
            raise ValueError("Error parsing header for ion DOS data.") from e
        NEDOS = int(NEDOS)

        first_data_line = self._fix_number_format(lines[1])
        first_values = list(map(float, first_data_line.split()))
        num_orbitals = len(first_values) - 1

        if self.spin_polarized:
            if num_orbitals == 18:
                orbital_labels = [
                    's_up', 's_down',
                    'p_y_up', 'p_y_down',
                    'p_z_up', 'p_z_down',
                    'p_x_up', 'p_x_down',
                    'd_xy_up', 'd_xy_down',
                    'd_yz_up', 'd_yz_down',
                    'd_z2r2_up', 'd_z2r2_down',
                    'd_xz_up', 'd_xz_down',
                    'd_x2y2_up', 'd_x2y2_down'
                ]
            elif num_orbitals == 6:
                orbital_labels = ['s_up', 's_down', 'p_up', 'p_down', 'd_up', 'd_down']
            else:
                raise ValueError(f"Unsupported number of orbital contributions for spin-polarized ion DOS: {num_orbitals}")
        else:
            if num_orbitals == 9:
                orbital_labels = [
                    's', 'p_y', 'p_z', 'p_x',
                    'd_xy', 'd_yz', 'd_z2r2', 'd_xz', 'd_x2y2'
                ]
            elif num_orbitals == 3:
                orbital_labels = ['s', 'p', 'd']
            else:
                raise ValueError(f"Unsupported number of orbital contributions for non-spin-polarized ion DOS: {num_orbitals}")

        energies = []
        orbitals = {label: [] for label in orbital_labels}

        for line in lines[1:]:
            line = self._fix_number_format(line)
            values = list(map(float, line.split()))
            energies.append(values[0])
            for idx, label in enumerate(orbital_labels):
                orbitals[label].append(values[idx + 1])

        dos_ion = {'energies': np.array(energies)}
        for label in orbital_labels:
            dos_ion[label] = np.array(orbitals[label])

        return dos_ion

    def _read_ions_dos(self, lines: list):
        """
        Parse the partial DOS data for all ions.

        Each ion block consists of (NEDOS + 1) lines (a header line plus NEDOS data lines).

        Parameters
        ----------
        lines : list
            Lines containing all ions' partial DOS data.
        """
        ion_block_size = self._NEDOS + 1
        num_ions = self._atom_count
        for n in range(num_ions):
            start = ion_block_size * n
            end = start + ion_block_size
            ion_lines = lines[start:end]
            dos_ion = self._read_ion_dos(ion_lines)
            self._dos_ion.append(dos_ion)

    def read_DOSCAR(self, file_location: str = None) -> bool:
        """
        Load and parse the DOS data from a DOSCAR file.

        Reads the file, extracts header information, total DOS data,
        and, if available, partial DOS data for each ion.

        Parameters
        ----------
        file_location : str
            Path to the DOSCAR file. If not provided, uses the initialized file location.

        Returns
        -------
        bool
            True if the file was successfully loaded and parsed.
        """
        file_location = file_location if isinstance(file_location, str) else self._file_location
        if not file_location:
            raise ValueError("No file location provided for DOSCAR.")

        with open(file_location, 'r') as f:
            lines = f.readlines()

        self._read_header(lines[:6])
        total_dos_start = 6
        total_dos_end = total_dos_start + self._NEDOS
        self._dos_total = self._read_total_dos(lines[total_dos_start:total_dos_end])

        if len(lines) > total_dos_end and self._partial_DOS == 1:
            ion_dos_lines = lines[total_dos_end:]
            self._read_ions_dos(ion_dos_lines)

        return True

    def plot(self, plot_total: bool = True, ion_index=None, save: bool = False, filename: str = None, output_dir: str = None):
        """
        Plot the Density of States (DOS) data with improved formatting.

        Generates a larger figure with gridlines and descriptive titles (including system name and Fermi energy).
        The plot can be saved in a specified output directory.

        Parameters
        ----------
        plot_total : bool
            If True, plot the total DOS.
        ion_index : int or list of int, optional
            Ion index/indices for which to plot the partial DOS. If None, only total DOS is plotted.
        save : bool
            If True, the plot will be saved to a file.
        filename : str, optional
            Filename for the plot (default is 'dos_plot.png').
        output_dir : str, optional
            Directory where the plot file will be saved. If not provided, a folder is created using a descriptive name.
        """
        plt.figure(figsize=(10, 8))
        plotted = False

        if plot_total and self._dos_total is not None:
            energies = self._dos_total['energies']
            if self.spin_polarized:
                plt.plot(energies, self._dos_total['dos_up'], label='Total DOS (up)', lw=2)
                plt.plot(energies, self._dos_total['dos_down'], label='Total DOS (down)', lw=2)
            else:
                plt.plot(energies, self._dos_total['dos_up'], label='Total DOS', lw=2)
            plt.xlabel("Energy (eV)", fontsize=14)
            plt.ylabel("DOS (states/eV)", fontsize=14)
            title_str = "Total DOS"
            if self._system_name:
                title_str += f" for {self._system_name}"
            if self._fermi_energy is not None:
                title_str += f"\nFermi Energy = {self._fermi_energy:.3f} eV"
            plt.title(title_str, fontsize=16)
            plt.grid(True)
            plt.legend(fontsize=12)
            plotted = True

        if ion_index is not None and len(self._dos_ion) > 0:
            if isinstance(ion_index, int):
                ion_index = [ion_index]
            for idx in ion_index:
                if idx < 0 or idx >= len(self._dos_ion):
                    print(f"Ion index {idx} out of range.")
                    continue
                ion_data = self._dos_ion[idx]
                energies = ion_data['energies']
                for key in ion_data:
                    if key != 'energies':
                        plt.plot(energies, ion_data[key], label=f"Ion {idx} - {key}", lw=1.5)
            plt.xlabel("Energy (eV)", fontsize=14)
            plt.ylabel("Partial DOS (states/eV)", fontsize=14)
            plt.title("Partial DOS", fontsize=16)
            plt.grid(True)
            plt.legend(fontsize=12)
            plotted = True

        if not plotted:
            print("No DOS data available to plot.")
            return

        if output_dir is None:
            desc = self._system_name if self._system_name else "DOSCAR_results"
            output_dir = f"./{desc}_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if filename is None:
            filename = "dos_plot.png"
        full_path = os.path.join(output_dir, filename)
        if save:
            plt.savefig(full_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {full_path}")
        #plt.show()

    def save_data(self, prefix: str = "DOSCAR_data", output_dir: str = None):
        """
        Save the extracted DOS data into text files with improved organization.

        Saves header information, total DOS, partial DOS for each ion, and computed d-band centers.
        All files are stored in a new folder with a descriptive name.

        Parameters
        ----------
        prefix : str
            Prefix for the output filenames.
        output_dir : str, optional
            Directory where the files will be saved. If not provided, a folder is created using the system name.
        """
        if output_dir is None:
            desc = self._system_name if self._system_name else "DOSCAR_results"
            output_dir = f"./{desc}_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        header_filename = os.path.join(output_dir, f"{prefix}_header.txt")
        with open(header_filename, "w") as f:
            for key, value in self._header_info.items():
                f.write(f"{key}: {value}\n")
        print(f"Header information saved to {header_filename}")

        total_data = self._dos_total
        if total_data is not None:
            header_items = ["Energy", "DOS_up"]
            if self.spin_polarized:
                header_items.append("DOS_down")
            header_items.append("Integrated_DOS_up")
            if self.spin_polarized:
                header_items.append("Integrated_DOS_down")
            header = "\t".join(header_items)
            key_mapping = {
                "Energy": "energies",
                "DOS_up": "dos_up",
                "DOS_down": "dos_down",
                "Integrated_DOS_up": "integrated_dos_up",
                "Integrated_DOS_down": "integrated_dos_down"
            }
            try:
                total_array = np.column_stack([total_data[key_mapping[item]] for item in header_items])
            except KeyError as e:
                raise KeyError(f"Key error while mapping header items to total DOS data: {e}")
            total_filename = os.path.join(output_dir, f"{prefix}_total.txt")
            np.savetxt(total_filename, total_array, header=header, comments='')
            print(f"Total DOS data saved to {total_filename}")

        for i, ion_data in enumerate(self._dos_ion):
            headers = "\t".join(ion_data.keys())
            columns = [ion_data[key] for key in ion_data.keys()]
            ion_array = np.column_stack(columns)
            ion_filename = os.path.join(output_dir, f"{prefix}_ion_{i}.txt")
            np.savetxt(ion_filename, ion_array, header=headers, comments='')
            print(f"Ion {i} DOS data saved to {ion_filename}")

        d_band_centers = []
        for i, ion_data in enumerate(self._dos_ion):
            energies = ion_data.get('energies')
            d_dos = None
            for key, value in ion_data.items():
                if key.lower() != 'energies' and key.lower().startswith('d'):
                    if d_dos is None:
                        d_dos = np.array(value)
                    else:
                        d_dos += np.array(value)
            if d_dos is not None:
                numerator = np.trapz(energies * d_dos, energies)
                denominator = np.trapz(d_dos, energies)
                center = numerator / denominator if denominator != 0 else np.nan
            else:
                center = np.nan
            d_band_centers.append(center)

        d_centers_array = np.column_stack((np.arange(len(d_band_centers)), d_band_centers))
        header_d = "Ion\tD_band_center (eV)"
        d_center_filename = os.path.join(output_dir, f"{prefix}_d_band_centers.txt")
        np.savetxt(d_center_filename, d_centers_array, header=header_d, comments='', fmt=['%d', '%.6f'])
        print(f"D-band centers saved to {d_center_filename}")

    # --- Additional Analysis Methods ---

    def compute_band_gap(self, threshold: float = 0.05, min_gap_width: float = 0.1) -> dict:
        """
        Estimate the band gap from the total DOS data.

        Examines the DOS near the Fermi level to identify an energy window with low DOS.
        If a valid gap is found, returns the valence and conduction band edges and the gap width.

        Parameters
        ----------
        threshold : float
            DOS value below which states are considered negligible (default is 0.05 states/eV).
        min_gap_width : float
            Minimum gap width (in eV) to be considered valid (default is 0.1 eV).

        Returns
        -------
        dict
            Dictionary with keys 'valence_band_edge', 'conduction_band_edge', and 'band_gap'.
        """
        if self._dos_total is None:
            raise ValueError("Total DOS data is not available.")
        energies = self._dos_total['energies']
        if self.spin_polarized:
            total_dos = self._dos_total['dos_up'] + self._dos_total['dos_down']
        else:
            total_dos = self._dos_total['dos_up']

        below_threshold = total_dos < threshold
        fermi = self._fermi_energy
        idx_fermi = np.argmin(np.abs(energies - fermi))
        
        valence_edge = None
        for i in range(idx_fermi, -1, -1):
            if not below_threshold[i]:
                valence_edge = energies[i+1] if i+1 < len(energies) else energies[i]
                break

        conduction_edge = None
        for i in range(idx_fermi, len(energies)):
            if not below_threshold[i]:
                conduction_edge = energies[i-1] if i-1 >= 0 else energies[i]
                break
        
        band_gap = 0.0
        if valence_edge is not None and conduction_edge is not None:
            gap = conduction_edge - valence_edge
            if gap >= min_gap_width:
                band_gap = gap
        
        return {
            'valence_band_edge': valence_edge,
            'conduction_band_edge': conduction_edge,
            'band_gap': band_gap
        }

    def compute_magnetic_moment(self) -> float:
        """
        Compute the magnetic moment from the total DOS data for spin-polarized systems.

        The moment is estimated as the difference between the integrated DOS for up and down spins
        at the Fermi level.

        Returns
        -------
        float
            The computed magnetic moment (in µ_B). Returns 0 for non-spin-polarized systems.
        """
        if not self.spin_polarized:
            return 0.0
        energies = self._dos_total['energies']
        up = self._dos_total['integrated_dos_up']
        down = self._dos_total['integrated_dos_down']
        fermi = self._fermi_energy
        int_up = np.interp(fermi, energies, up)
        int_down = np.interp(fermi, energies, down)
        return int_up - int_down

    def analyze_orbital_contributions(self, orbital_type: str = 'd', energy_window: tuple = None) -> dict:
        """
        Analyze the contributions of a specific orbital type from the partial DOS data.

        For each ion, computes the weighted average energy (orbital band center) and the standard deviation
        of the orbital DOS. An optional energy window may be applied.

        Parameters
        ----------
        orbital_type : str
            Orbital type to analyze (e.g., 'd', 'p', or 's'); comparison is case-insensitive.
        energy_window : tuple of (float, float), optional
            (E_min, E_max) to restrict the analysis.

        Returns
        -------
        dict
            Dictionary with keys for each ion containing 'band_center' and 'std_dev', plus an overall average.
        """
        results = {}
        for i, ion_data in enumerate(self._dos_ion):
            energies = ion_data.get('energies')
            keys = [key for key in ion_data if key.lower().startswith(orbital_type.lower())]
            if not keys:
                continue
            dos_sum = np.zeros_like(energies)
            for key in keys:
                dos_sum += ion_data[key]
            if energy_window is not None:
                E_min, E_max = energy_window
                mask = (energies >= E_min) & (energies <= E_max)
                if np.sum(mask) == 0:
                    continue
                E_sel = energies[mask]
                dos_sel = dos_sum[mask]
            else:
                E_sel = energies
                dos_sel = dos_sum
            band_center = np.trapz(E_sel * dos_sel, E_sel) / np.trapz(dos_sel, E_sel)
            variance = np.trapz(((E_sel - band_center)**2) * dos_sel, E_sel) / np.trapz(dos_sel, E_sel)
            std_dev = np.sqrt(variance)
            results[f'ion_{i}'] = {'band_center': band_center, 'std_dev': std_dev}
        if results:
            centers = [val['band_center'] for val in results.values()]
            overall_avg = np.mean(centers)
            results['overall_average'] = overall_avg
        return results

    def summary(self) -> str:
        """
        Generate a summary report of the DOS analysis.

        The summary includes system name, Fermi energy, estimated band gap, magnetic moment (if applicable),
        and key orbital contributions (e.g., d-band centers).

        Returns
        -------
        str
            A formatted string summary of the analysis.
        """
        lines = []
        lines.append(f"System: {self._system_name}")
        lines.append(f"Fermi Energy: {self._fermi_energy:.3f} eV")
        gap_info = self.compute_band_gap()
        lines.append(f"Estimated Band Gap: {gap_info['band_gap']:.3f} eV")
        if self.spin_polarized:
            mag = self.compute_magnetic_moment()
            lines.append(f"Magnetic Moment: {mag:.3f} µB")
        d_analysis = self.analyze_orbital_contributions(orbital_type='d')
        if d_analysis:
            overall_d = d_analysis.get('overall_average', np.nan)
            lines.append(f"Average d-band Center: {overall_d:.3f} eV")
        return "\n".join(lines)

    # --- New Plotting Analysis Methods ---

    def plot_band_gap(self, threshold: float = 0.05, min_gap_width: float = 0.1, save: bool = True,
                      output_dir: str = None, filename: str = None):
        """
        Plot the total DOS data with the estimated band gap region highlighted.

        Overlays a shaded region corresponding to the band gap (if found)
        and annotates the gap value on the plot.

        Parameters
        ----------
        threshold : float
            DOS value below which states are considered negligible.
        min_gap_width : float
            Minimum gap width to be considered valid.
        save : bool
            If True, the plot is saved to a file.
        output_dir : str, optional
            Directory where the plot will be saved.
        filename : str, optional
            Filename for the saved plot.
        """
        if self._dos_total is None:
            raise ValueError("Total DOS data is not available for plotting band gap.")

        plt.figure(figsize=(10, 8))
        energies = self._dos_total['energies']
        if self.spin_polarized:
            total_dos = self._dos_total['dos_up'] + self._dos_total['dos_down']
        else:
            total_dos = self._dos_total['dos_up']
        plt.plot(energies, total_dos, label="Total DOS", lw=2, color='black')
        gap_info = self.compute_band_gap(threshold=threshold, min_gap_width=min_gap_width)
        if gap_info['band_gap'] > 0:
            plt.axvspan(gap_info['valence_band_edge'], gap_info['conduction_band_edge'],
                        color='red', alpha=0.3, label=f"Band Gap: {gap_info['band_gap']:.2f} eV")
        plt.xlabel("Energy (eV)", fontsize=14)
        plt.ylabel("DOS (states/eV)", fontsize=14)
        title_str = "Total DOS with Estimated Band Gap"
        if self._system_name:
            title_str += f"\n{self._system_name}"
        plt.title(title_str, fontsize=16)
        plt.grid(True)
        plt.legend(fontsize=12)
        if output_dir is None:
            desc = self._system_name if self._system_name else "DOSCAR_results"
            output_dir = f"./{desc}_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if filename is None:
            filename = "dos_band_gap.png"
        full_path = os.path.join(output_dir, filename)
        if save:
            plt.savefig(full_path, dpi=300, bbox_inches="tight")
            print(f"Band gap plot saved to {full_path}")

    def plot_orbital_analysis(self, orbital_type: str = 'd', energy_window: tuple = None, save: bool = True,
                              output_dir: str = None, filename: str = None):
        """
        Plot the orbital contributions analysis for the specified orbital type across all ions.

        Generates a scatter plot with error bars showing each ion's orbital band center and spread.
        An overall average is displayed as a horizontal dashed line.

        Parameters
        ----------
        orbital_type : str
            The orbital type to analyze (e.g., 'd', 'p', or 's').
        energy_window : tuple, optional
            Energy window (E_min, E_max) to restrict the analysis.
        save : bool
            If True, the plot will be saved to a file.
        output_dir : str, optional
            Directory where the plot will be saved.
        filename : str, optional
            Filename for the plot.
        """
        results = self.analyze_orbital_contributions(orbital_type=orbital_type, energy_window=energy_window)
        if not results:
            print(f"No data available for orbital type '{orbital_type}'.")
            return

        ion_indices = []
        centers = []
        errors = []
        for key, data in results.items():
            if key.startswith('ion_'):
                ion_idx = int(key.split('_')[1])
                ion_indices.append(ion_idx)
                centers.append(data['band_center'])
                errors.append(data['std_dev'])
        ion_indices = np.array(ion_indices)
        centers = np.array(centers)
        errors = np.array(errors)

        plt.figure(figsize=(10, 6))
        plt.errorbar(ion_indices, centers, yerr=errors, fmt='o', capsize=5, label=f"{orbital_type.upper()} band center")
        if 'overall_average' in results:
            overall_avg = results['overall_average']
            plt.axhline(overall_avg, color='red', linestyle='--', label=f"Overall Average = {overall_avg:.2f} eV")
        plt.xlabel("Ion Index", fontsize=14)
        plt.ylabel(f"{orbital_type.upper()} Band Center (eV)", fontsize=14)
        plt.title(f"Orbital Analysis ({orbital_type.upper()})", fontsize=16)
        plt.grid(True)
        plt.legend(fontsize=12)
        if output_dir is None:
            desc = self._system_name if self._system_name else "DOSCAR_results"
            output_dir = f"./{desc}_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if filename is None:
            filename = f"orbital_analysis_{orbital_type}.png"
        full_path = os.path.join(output_dir, filename)
        if save:
            plt.savefig(full_path, dpi=300, bbox_inches="tight")
            print(f"Orbital analysis plot saved to {full_path}")

    def plot_dos_derivative(self, save: bool = True, output_dir: str = None, filename: str = None):
        """
        Plot the derivative of the total DOS with respect to energy.

        Helps identify features such as peak positions and rapid changes in DOS.

        Parameters
        ----------
        save : bool
            If True, the plot is saved to a file.
        output_dir : str, optional
            Directory where the plot will be saved.
        filename : str, optional
            Filename for the plot.
        """
        if self._dos_total is None:
            raise ValueError("Total DOS data is not available for derivative plotting.")
        energies = self._dos_total['energies']
        if self.spin_polarized:
            total_dos = self._dos_total['dos_up'] + self._dos_total['dos_down']
        else:
            total_dos = self._dos_total['dos_up']
        derivative = np.gradient(total_dos, energies)
        plt.figure(figsize=(10, 6))
        plt.plot(energies, derivative, lw=2, color='purple', label="d(DOS)/dE")
        plt.xlabel("Energy (eV)", fontsize=14)
        plt.ylabel("d(DOS)/dE", fontsize=14)
        title_str = "Derivative of Total DOS"
        if self._system_name:
            title_str += f" - {self._system_name}"
        plt.title(title_str, fontsize=16)
        plt.grid(True)
        plt.legend(fontsize=12)
        if output_dir is None:
            desc = self._system_name if self._system_name else "DOSCAR_results"
            output_dir = f"./{desc}_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if filename is None:
            filename = "dos_derivative.png"
        full_path = os.path.join(output_dir, filename)
        if save:
            plt.savefig(full_path, dpi=300, bbox_inches="tight")
            print(f"DOS derivative plot saved to {full_path}")

    # --- New Method: Save Analysis Results as Text Files ---

    def save_analysis_results(self, output_dir: str = None):
        """
        Perform DOS analysis and save the results into descriptive text files.

        This method computes the band gap, magnetic moment (if applicable), orbital contributions,
        and generates an overall summary of the DOS analysis. Each result is saved in a separate text file
        with a descriptive filename.

        Parameters
        ----------
        output_dir : str, optional
            Directory where the analysis result files will be saved. If not provided, a folder is created
            based on the system name or a default.
        """
        if output_dir is None:
            desc = self._system_name if self._system_name else "DOSCAR_results"
            output_dir = f"./{desc}_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save band gap analysis results
        band_gap_info = self.compute_band_gap()
        band_gap_file = os.path.join(output_dir, "band_gap_analysis.txt")
        with open(band_gap_file, "w") as f:
            f.write("Band Gap Analysis Results\n")
            f.write("-------------------------\n")
            f.write(f"Valence Band Edge: {band_gap_info.get('valence_band_edge', 'N/A')}\n")
            f.write(f"Conduction Band Edge: {band_gap_info.get('conduction_band_edge', 'N/A')}\n")
            f.write(f"Estimated Band Gap: {band_gap_info.get('band_gap', 0)} eV\n")
        print(f"Band gap analysis saved to {band_gap_file}")
        
        # Save magnetic moment analysis results (if spin-polarized)
        if self.spin_polarized:
            magnetic_moment = self.compute_magnetic_moment()
            magnetic_file = os.path.join(output_dir, "magnetic_moment_analysis.txt")
            with open(magnetic_file, "w") as f:
                f.write("Magnetic Moment Analysis Results\n")
                f.write("--------------------------------\n")
                f.write(f"Computed Magnetic Moment: {magnetic_moment} µB\n")
            print(f"Magnetic moment analysis saved to {magnetic_file}")
        
        # Save orbital contributions analysis results for d orbitals
        orbital_results = self.analyze_orbital_contributions(orbital_type='d')
        orbital_file = os.path.join(output_dir, "orbital_contributions_analysis.txt")
        with open(orbital_file, "w") as f:
            f.write("Orbital Contributions Analysis Results (d orbitals)\n")
            f.write("-----------------------------------------------------\n")
            for key, data in orbital_results.items():
                if key.startswith('ion_'):
                    f.write(f"{key}: Band Center = {data['band_center']:.3f} eV, Std Dev = {data['std_dev']:.3f} eV\n")
            if 'overall_average' in orbital_results:
                f.write(f"\nOverall Average d-band Center: {orbital_results['overall_average']:.3f} eV\n")
        print(f"Orbital contributions analysis saved to {orbital_file}")
        
        # Save overall DOS summary
        summary_text = self.summary()
        summary_file = os.path.join(output_dir, "dos_summary.txt")
        with open(summary_file, "w") as f:
            f.write("DOS Analysis Summary\n")
            f.write("--------------------\n")
            f.write(summary_text)
        print(f"DOS summary saved to {summary_file}")
