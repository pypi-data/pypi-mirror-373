try:
    from ..master.FileManager import FileManager
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
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import json
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing json: {str(e)}\n")
    del sys

class EigenvalueFileManager(FileManager, AtomicProperties):
    def __init__(self, file_location:str=None, name:str=None, cell:np.array=None, fermi:float=None, **kwargs):
        """
        Initialize OutFileManager class.
        :param file_location: Location of the file to be read.
        :param name: Name identifier for the file.
        :param kwargs: Additional keyword arguments.
        """
        FileManager.__init__(self, name=name, file_location=file_location)
        AtomicProperties.__init__(self)
        self._comment = None

        self._n_electron, self._num_kpoints, self._num_bands = None, None, None

        self._eigenvals = None
        self._occupancies = None
        self._kpoints = None
        self._weight = None
        self._k_distance = None

        self._fermi = fermi if fermi is not None else None
        self._cell = cell
        self._spins = None

    @property
    def cell(self):
        if self._cell is not None:
            return np.array(self._cell, dtype=np.float64)
        else:
            return None
    @property
    def fermi(self):
        """
        Getter for the Fermi energy level.
        Returns 0.0 if not set.
        """
        return self._fermi if self._fermi is not None else 0.0

    @fermi.setter
    def fermi(self, value):
        """
        Setter for the Fermi energy level.
        """
        self._fermi = value

    def read_EIGENVALmatrix(self, lines:list=None):
        if lines is None or self.are_all_lines_empty(lines): return 0

        KPOINTn_eigenvals = np.zeros( (self.num_bands, 2 if self.ISPIN == 2 else 1), dtype=np.float64 )
        KPOINTn_occupancies = np.zeros( (self.num_bands, 2 if self.ISPIN == 2 else 1), dtype=np.float64 )

        for i, n in enumerate(lines):
            vec = [float(m) for m in n.split(' ') if self.is_number(m) ] 
            
            KPOINTn_eigenvals[i,:] = np.array([ vec[1], vec[2] ]) if self.ISPIN == 2 else np.array([ vec[1] ]) 
            KPOINTn_occupancies[i,:] = np.array([ vec[3], vec[4] ]) if self.ISPIN == 2 else np.array([ vec[2] ]) 

        return KPOINTn_eigenvals, KPOINTn_occupancies

    def read_EIGENVAL(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self._file_location
        lines = [n for n in self.read_file(file_location) ]

        var = 0
        for i, n in enumerate(lines):
            vec = [float(m) for m in n.split(' ') if self.is_number(m) ] 
            if   i == 0: self._NIONS, self._ISPIN = vec[0], vec[-1]
            elif i == 1: self._cellVolumen = vec[0]
            elif i == 2: self.T = vec[0]
            elif i == 5: 
                self._n_electron, self._num_kpoints, self._num_bands = int(vec[0]), int(vec[1]), int(vec[2])
                self._eigenvals = np.zeros( (self.num_kpoints, self.num_bands, 2 if self.ISPIN == 2 else 1), dtype=np.float64 )
                self._occupancies = np.zeros( (self.num_kpoints, self.num_bands, 2 if self.ISPIN == 2 else 1), dtype=np.float64 )
                self._kpoints = np.zeros( (self.num_kpoints, 3), dtype=np.float64 )
                self._weight = np.zeros( (self.num_kpoints, 1), dtype=np.float64 )

            if len(vec) == 4 and i>5: 
                self._kpoints[var, :] = vec[:3]
                self._weight[var]  = vec[3]
                self._eigenvals[var, :], self._occupancies[var, :] = self.read_EIGENVALmatrix(lines=lines[i+1:i+self.num_bands+1])
                var+=1

        self.k_distance = np.zeros((len(self.kpoints)), dtype=np.float64)
        var = 0
        for n in range(len(self.k_distance)-1): 
            var += ((self.kpoints[n][0]-self.kpoints[n+1][0])**2+(self.kpoints[n][1]-self.kpoints[n+1][1])**2+(self.kpoints[n][2]-self.kpoints[n+1][2])**2)**0.5
            self.k_distance[n+1] = var

        return True

    def read_band_out(self, file_location: str = None):
        file_location = file_location if isinstance(file_location, str) else self._file_location
        lines = [n for n in self.read_file(file_location) ]
        
        kpoint_data = {}
        self._num_bands = 0
        self._weight = []
        self._kpoints = []
        self._spins = set()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('KPT'):
                tokens = line.split()
                kpt_index = int(tokens[1]) - 1  # Los índices comienzan desde 0
                spin = int(tokens[3]) - 1       # Los índices de spin comienzan desde 0
                kweight = float(tokens[5])
                
                self._spins.add(spin)
                if kpt_index not in kpoint_data:
                    kpoint_data[kpt_index] = {'kweight': kweight, 'energies': {}, 'occupancies': {}}
                else:
                    # Verificar coherencia de kweight
                    if kpoint_data[kpt_index]['kweight'] != kweight:
                        print(f"Advertencia: discrepancia en KWEIGHT en kpt_index {kpt_index}")
                i += 1
                energies_kpt = []
                occupancies_kpt = []
                while i < len(lines) and not lines[i].strip().startswith('KPT'):
                    tokens = lines[i].strip().split()
                    if len(tokens) >= 3:
                        # tokens: [band_index, energy, occupancy]
                        energy = float(tokens[1])
                        occupancy = float(tokens[2])
                        energies_kpt.append(energy)
                        occupancies_kpt.append(occupancy)
                        i += 1
                    else:
                        i += 1
                kpoint_data[kpt_index]['energies'][spin] = energies_kpt
                kpoint_data[kpt_index]['occupancies'][spin] = occupancies_kpt
                # Actualizar el número de bandas si es necesario
                if len(energies_kpt) > self._num_bands:
                    self._num_bands = len(energies_kpt)
            else:
                i += 1
        
        # Ahora, organizamos los datos en arrays
        num_kpoints = len(kpoint_data)
        num_spins = max(self._spins) + 1  # Asumiendo spins 0 y 1
        self.ISPIN = num_spins
        
        # Inicializar arrays
        self._eigenvals = np.zeros((num_kpoints, self._num_bands, num_spins))
        self._occupancies = np.zeros((num_kpoints, self._num_bands, num_spins))
        self._weight = np.zeros(num_kpoints)
        self._kpoints = np.zeros(num_kpoints)
        
        for kpt_index in sorted(kpoint_data.keys()):
            self._weight[kpt_index] = kpoint_data[kpt_index]['kweight']
            self._kpoints[kpt_index] = kpt_index  # Puedes ajustar esto si tienes coordenadas reales de k-points
            for spin in range(num_spins):
                energies = kpoint_data[kpt_index]['energies'].get(spin, [0.0]*self._num_bands)
                occupancies = kpoint_data[kpt_index]['occupancies'].get(spin, [0.0]*self._num_bands)
                # Asegurarse de que las listas tengan el tamaño de self._num_bands
                energies += [0.0]*(self._num_bands - len(energies))
                occupancies += [0.0]*(self._num_bands - len(occupancies))
                self._eigenvals[kpt_index, :, spin] = energies
                self._occupancies[kpt_index, :, spin] = occupancies
        
        return True

    def _ndarray_2_list(self, array):
        return [list(array.shape), str(array.dtype), list(array.flatten(order='C'))]

    def _ndarray_2_dict(self, array):
        return {'__ndarray__':self._ndarray_2_list(array)}

    def _get_specialpoints(self, kpoints:np.array) -> list:
        """Check if points in a kpoints matrix exist in a lattice points dictionary."""
        found_points = []

        for point in kpoints:
            for label, special_lattice_point in self.special_lattice_points.items():
                # Compare only the first three elements (x, y, z coordinates)
                if self.is_close(point[:3], special_lattice_point[:3]):
                    found_points.append( label )
                    break

        return found_points
    
    def _subtract_fermi(self, fermi: float = None):
        """
        Subtract the Fermi level from eigenvalues.
        """
        fermi = fermi if fermi is not None else self.fermi
        if self._eigenvals is not None:
            self._eigenvals -= fermi
            self._fermi = 0.0
        return True 

    def _transform_bands(self, eigenvals:np.array=None):
        eigenvals = self.eigenvals
        return matrix.reshape(1, *eigenvals.shape) if eigenvals.ndim == 2 else (eigenvals.transpose(2, 0, 1).reshape(2, *eigenvals.shape[:2]) if eigenvals.ndim == 3 and eigenvals.shape[2] == 2 else None)

    def export_as_json(self, file_location:str=None, subtract_fermi:bool=True) -> True:
        file_location = file_location if type(file_location) == str else self._file_location+'data.json'

        if subtract_fermi: self._subtract_fermi()

        SP = self._get_specialpoints(self.kpoints)

        # Crear el formato JSON
        json_data = {
            "path": {
                "kpts": self._ndarray_2_dict(self.kpoints[:,:3]),
                "special_points": {sp:self._ndarray_2_dict(self.special_lattice_points[sp]) for sp in SP},
                "labelseq": ''.join(SP),
                "cell": {"array": self._ndarray_2_dict(self.cell), "__ase_objtype__": "cell"},
                "__ase_objtype__": "bandpath"

                    },
            "energies": self._ndarray_2_dict( self._transform_bands() ), # SPIN x KPOINT x Nband
            "reference": self.fermi,
            "__ase_objtype__": "bandstructure"
        }

        self.save_to_json(json_data, file_location)
        
        return True

    def plot(self, file_location: str = None, subtract_fermi: bool = True, save: bool = False, emin: float = -5, emax: float = 5) -> bool:
        """
        Plot the band structure based on the eigenvalues stored in the object.
        
        Parameters
        ----------
        file_location : str, optional
            The file path to save the plotted image. If None is provided, the default file 
            location will be used (same as self._file_location + 'img_band.png').
        subtract_fermi : bool, optional
            If True, subtract the Fermi level from the eigenvalues before plotting.
        save : bool, optional
            If True, the figure will be saved to the specified file location. Otherwise, the 
            figure will be displayed on screen.
        emin : float, optional
            The minimum energy value for the y-axis.
        emax : float, optional
            The maximum energy value for the y-axis.

        Returns
        -------
        bool
            True if plotting was successful, False if no eigenvalues are available.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # Determine file location
        file_location = file_location if isinstance(file_location, str) else self._file_location + 'img_band.png'

        # Ensure emin and emax defaults
        emin = emin if emin is not None else -5
        emax = emax if emax is not None else 5

        # Subtract Fermi level if requested
        if subtract_fermi:
            self._subtract_fermi()

        # Check if eigenvalues are available
        if self._eigenvals is None:
            print("No eigenvalues to plot.")
            return False

        num_kpoints = self._eigenvals.shape[0]
        num_bands = self._eigenvals.shape[1]

        # Determine x-axis values based on k-points
        if hasattr(self, 'kpoints') and self.kpoints is not None and self.kpoints.size > 0:
            if self.kpoints.ndim == 2:
                # Calculate distances between real k-points
                kpoints = self.kpoints
                k_distances = np.linalg.norm(kpoints[1:] - kpoints[:-1], axis=1)
                X = np.concatenate(([0], np.cumsum(k_distances)))
            else:
                # If k-points are already one-dimensional, use them directly
                X = self.kpoints
        else:
            # Use simple integer indices if no k-points are provided
            X = np.arange(num_kpoints)

        # Use a built-in style for a cleaner look
        plt.style.use('ggplot')

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plot eigenvalues
        # If non-spin-polarized or eigenvals are 2D
        if self.ISPIN == 1 or self._eigenvals.ndim == 2:
            for band in range(num_bands):
                ax.plot(X, self._eigenvals[:, band], color='blue', linewidth=1)
        elif self.ISPIN == 2 and self._eigenvals.ndim == 3:
            # If spin-polarized data is present
            for spin in range(self._eigenvals.shape[2]):
                spin_color = 'red' if spin == 0 else 'blue'
                for band in range(num_bands):
                    ax.plot(X, self._eigenvals[:, band, spin], linewidth=1, color=spin_color)

        # Add vertical dashed lines for special k-points if available
        if hasattr(self, 'special_lattice_points') and self.special_lattice_points:
            SP = []
            for idx, point in enumerate(self.kpoints):
                for label, special_point in self.special_lattice_points.items():
                    if self.is_close(point, special_point):
                        SP.append((X[idx], label))
            for pos, label in SP:
                ax.axvline(x=pos, color='gray', linestyle='--', alpha=0.8, linewidth=1)
            if SP:
                positions, labels = zip(*SP)
                ax.set_xticks(positions)
                ax.set_xticklabels(labels)

        # Add a horizontal line at zero (if subtracting Fermi, zero is the Fermi level)
        if subtract_fermi:
            ax.axhline(y=0, color='black', linewidth=1, linestyle='--', alpha=0.8)

        # Set labels, title and limits
        ax.set_xlabel('K-point', fontsize=12)
        ax.set_ylabel('Energy (eV)', fontsize=12)
        ax.set_title('Band Structure', fontsize=14)
        ax.set_ylim(emin, emax)

        # Enable a grid for better readability
        ax.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.7)

        # Improve layout
        plt.tight_layout()

        # Save or show plot
        if save:
            plt.savefig(file_location, dpi=350)
            plt.close(fig)
        else:
            plt.show()

        return True


if __name__ == "__main__":
    # Read the .hsd file
    vasp_input = EigenvalueFileManager(file_location='../test/VASP/PDOS/EIGENVAL')
    vasp_input.read_EIGENVAL()
    vasp_input.plot()

    dftb_input = EigenvalueFileManager(file_location='../test/DFTB/out_test/band.out')
    if dftb_input.read_band_out():
        # View the data
        dftb_input.plot()

        # Modify a parameter
        dftb_input.data['Options']['WriteDetailedXML'] = 'Yes'

        # Write back to a new .hsd file
        #dftb_input.write_hsd('modified_dftb_input.hsd')

