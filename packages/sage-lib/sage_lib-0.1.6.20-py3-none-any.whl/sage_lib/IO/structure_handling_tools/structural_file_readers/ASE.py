class ASE:
    """
    ASE class inherits from Atoms and FileManager, facilitating operations related
    to atomic structures and file management.
    """

    def __init__(self, name:str=None, file_location:str=None ):    
        """
        Initialize the ASE class by initializing parent classes.
        :param name: Name of the file.
        :param file_location: Location of the file.
        """
        #FileManager.__init__(self, name=name, file_location=file_location)
        # Initialize Atoms with default values, including PBC
        #Atoms.__init__(self, pbc=np.array([True, True, True]))
        pass
    def export_as_ASE(self, file_location:str=None, verbose:bool=False) -> bool:
        """
        Exports the ASE object to a specified file location.
        :param file_location: The file path to save the object.
        :param verbose: If True, enables verbose output.
        :return: Boolean indicating successful export.
        """
        try:
            import pickle
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing pickle: {str(e)}\n")
            del sys

        file_location = file_location if file_location is not None else 'ASE.obj'

        try:
            with open(file_location, 'wb') as file:
                pickle.dump(self, file)
            return True
        except Exception as e:
            if verbose:
                print(f"Error exporting ASE object: {e}")
            return False

    def read_ASE(self, file_location:str=None, ase_atoms:object=None, **kwargs):
        """
        Reads an ASE object either from an existing Atoms object or from a file.
        :param ase_atoms: An existing Atoms object.
        :param file_location: The file path to read the object from.
        :return: Boolean indicating successful read.
        """
        if ase_atoms is not None:
            self.ASE_2_SAGE(ase_atoms=ase_atoms)
            return True

        elif file_location is not None: 
            from ase.io import read
            self = read(file_path)
            self.ASE_2_SAGE(ase_atoms=ase_atoms)
            return True

        return False

    def ASE_2_SAGE(self, ase_atoms:object=None):
        """
        Transforms an ASE Atoms object to the SAGE internal representation.
        :param ase_atoms: An ASE Atoms object.
        """

        # Configuración básica
        self._atomCount = len(ase_atoms)
        self._uniqueAtomLabels = list(set(ase_atoms.get_chemical_symbols()))
        self._atomCountByType = [ase_atoms.get_chemical_symbols().count(x) for x in self._uniqueAtomLabels]
        self._atomPositions = ase_atoms.get_positions()
        self._atomLabelsList = ase_atoms.get_chemical_symbols()
        self._latticeVectors = ase_atoms.get_cell()
        self._cellVolumen = ase_atoms.get_volume()
        self._pbc = ase_atoms.get_pbc()
        self._atomCoordinateType = 'Cartesian'

        # --- Constraints ---
        if ase_atoms.constraints:
            import numpy as np
            idx = np.asarray(ase_atoms.constraints[0].get_indices(), dtype=np.intp)
            self._atomicConstraints = np.isin(np.arange(len(ase_atoms), dtype=np.intp), idx)

        try:
            self._E = ase_atoms.get_total_energy() 
        except (AttributeError, RuntimeError):
            self._E = None  # O algún valor predeterminado si es más apropiado

        try:
            self._K = ase_atoms.get_kinetic_energy()
        except (AttributeError, RuntimeError):
            self._K = None

        # Para la energía potencial, verifica si tanto E como K están disponibles
        if self._E is not None and self._K is not None:
            self._U = self._E - self._K
        else:
            self._U = None  # O algún valor predeterminado
            
        self._total_force = np.sum(ase_atoms.get_forces(), axis=0) if 'forces' in ase_atoms.arrays else None

