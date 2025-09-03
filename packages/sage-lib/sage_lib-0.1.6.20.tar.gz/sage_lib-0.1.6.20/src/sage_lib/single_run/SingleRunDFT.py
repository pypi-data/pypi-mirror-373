try:
    from .SingleRunManager import SingleRunManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing SingleRunManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys


class SingleRunDFT(SingleRunManager): # el nombre no deberia incluir la palabra DFT tieneu qe ser ma general
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)

    def read_AIMS(self, file_location:str=None, file_name:str=None, v:bool=False):
        '''
        '''
        self.file_location = file_location if type(file_location) == str else self.file_location
        self.loadStoreManager(self.AtomPositionManager_constructor, f'{file_name}', '_AtomPositionManager', 'read_AIMS', v) 
           
    def readXYZfile(self, file_location:str=None, file_name:str=None, lines:list=None, v:bool=False):
        self.file_location = file_location if type(file_location) == str else self.file_location

        if lines is not None:
            self.AtomPositionManager = self.AtomPositionManager_constructor()
            self.AtomPositionManager.read_XYZ(lines=lines)
        else:
            self.loadStoreManager(self.AtomPositionManager_constructor, f'{file_name}', '_AtomPositionManager', 'read_XYZ', v) 

    def read_ASE(self, file_location:str=None, ase_atoms:object=None, v:bool=False):
        '''
        '''
        self.file_location = file_location if type(file_location) == str else self.file_location

        if ase_atoms is not None:
            self.AtomPositionManager = self.AtomPositionManager_constructor(file_location)
            self.AtomPositionManager.read_ASE(file_location=file_location, ase_atoms=ase_atoms, )
        else:
            self.loadStoreManager(self.AtomPositionManager_constructor, f'{file_name}', '_AtomPositionManager', 'read_ASE', v) 
           
    def readVASPDirectory(self, file_location:str=None, v:bool=False):
        self.file_location = file_location if type(file_location) == str else self.file_location

        self.loadStoreManager(self.AtomPositionManager_constructor, 'POSCAR', '_AtomPositionManager', 'read_POSCAR', v)
        self.loadStoreManager(self.AtomPositionManager_constructor, 'CONTCAR', '_Out_AtomPositionManager', 'read_CONTCAR', v)
        self.loadStoreManager(self.PotentialManager_constructor, 'POTCAR', '_PotentialManager', 'readPOTCAR', v)
        self.loadStoreManager(self.InputFileManager_constructor, 'INCAR', '_InputFileManager', 'readINCAR', v)
        self.loadStoreManager(self.KPointsManager_constructor, 'KPOINTS', '_KPointsManager', 'readKPOINTS', v)
        self.loadStoreManager(self.BashScriptManager_constructor, 'RUNscript.sh', '_BashScriptManager', 'readBashScript', v)
        self.loadStoreManager(self.BinaryDataHandler_constructor, 'vdw_kernel.bindat', '_vdw_kernel_Handler', 'read_VASP_VDW_Kernel', v)
        
        self.loadStoreManager(self.OutFileManager_constructor, 'OUTCAR', '_OutFileManager', 'readOUTCAR', v)
        self.loadStoreManager(self.WaveFileManager_constructor, 'WAVECAR', '_WaveFileManager', 'importFileLocation', v)
        self.loadStoreManager(self.ChargeFileManager_constructor, 'CHGCAR', '_ChargeFileManager', 'importFileLocation', v)
           
    def readDFTBDirectory(self, file_location:str=None, v:bool=False):
        self.file_location = file_location if type(file_location) == str else self.file_location

        self.loadStoreManager(self.OutFileManager_constructor, 'detailed.out', '_OutFileManager', 'readDETAILED', v)
        self.loadStoreManager(self.AtomPositionManager_constructor, 'geo_end.gen', '_AtomPositionManager', 'read_GEN', v)

        #self.loadStoreManager(self.AtomPositionManager_constructor, 'band.out', '_Out_AtomPositionManager', 'read_CONTCAR', v)


    def _export_file(self, export_function, file_name, *args, **kwargs):
        """
        Helper function to export a file and handle any errors.

        Args:
            export_function (callable): The function to call for exporting.
            file_name (str): The name of the file to be exported.
            args: Positional arguments to pass to the export function.
            kwargs: Keyword arguments to pass to the export function.
        """
        try:
            export_function(*args, **kwargs)
        except Exception as e:
            print(f"Failed to export {file_name}: {e}")

    def exportVASP(self, file_location:str=None, CHGCAR:bool=True, WAVECAR:bool=True, kernel:bool=True):
        """
        Exports data in VASP format for running DFT calculations.

        This function prepares the necessary files for a VASP computation, handling the
        export of POSCAR, POTCAR, INCAR, KPOINTS, and optional files like CHGCAR, WAVECAR,
        and kernel data. It ensures continuous execution even if certain exports fail.

        Args:
            file_location (str, optional): The target directory for exported files.
            CHGCAR (bool): Flag to indicate whether to export the CHGCAR file.
            WAVECAR (bool): Flag to indicate whether to export the WAVECAR file.
            kernel (bool): Flag to indicate whether to export kernel data.
        """
        file_location = file_location if type(file_location) == str else self.file_location
        self.create_directories_for_path(file_location)

        # Export POSCAR
        if self.AtomPositionManager is not None:
            self.AtomPositionManager.NonPeriodic_2_Periodic()
            self._export_file(self.AtomPositionManager.export_as_POSCAR, 'POSCAR', file_location + '/POSCAR')

        # Export additional files with the helper method
        if self.PotentialManager:
            self._export_file(self.PotentialManager.exportAsPOTCAR, 'POTCAR', file_location + '/POTCAR', self.AtomPositionManager.uniqueAtomLabels)
        if self.InputFileManager:
            self._export_file(self.InputFileManager.exportAsINCAR, 'INCAR', file_location + '/INCAR', self.AtomPositionManager.uniqueAtomLabels)
        if self.KPointsManager:
            self._export_file(self.KPointsManager.exportAsKPOINTS, 'KPOINTS', file_location + '/KPOINTS')
        if self.BashScriptManager:
            self._export_file(self.BashScriptManager.exportAsBash, 'RUNscript.sh', file_location + '/RUNscript.sh')
        if self.vdw_kernel_Handler and kernel:
            self._export_file(self.vdw_kernel_Handler.export_VASP_VDW_Kernel, 'vdw_kernel.bindat', file_location + '/vdw_kernel.bindat')
        if self.WaveFileManager and WAVECAR:
            self._export_file(self.WaveFileManager.exportFile, 'WAVECAR', file_location + '/WAVECAR')
        if self.ChargeFileManager and CHGCAR:
            self._export_file(self.ChargeFileManager.exportFile, 'CHGCAR', file_location + '/CHGCAR')

    def recommend_vasp_parameters(self, num_cores, num_nodes, num_atoms:int=None, system_type:str="multi-core", network_type:str="fast"):
        """
        Recommends optimal VASP parameters based on the number of cores, nodes, and system type.

        Parameters:
            num_cores (int): Total number of compute cores available.
            num_nodes (int): Total number of nodes in the cluster.
            num_atoms (int): Number of atoms in the unit cell.
            system_type (str): Type of system ("multi-core" or "massive-parallel").
            network_type (str): Type of network ("fast" or "slow").

        Returns:
            dict: Recommended VASP parameters.
        """
        num_atoms = num_atoms if num_atoms is not None else self.AtomPositionManager.atomCount 
        recommendations = {}

        # General recommendations
        kpar = 1  # Default value
        if num_nodes > 1:
            kpar = num_nodes  # Usually set KPAR equal to the number of nodes for multi-node jobs

        # NCORE recommendations
        if system_type == "multi-core":
            ncore = min(4, num_cores // kpar)  # 2-4 is generally good for modern multi-core systems
        elif system_type == "massive-parallel":
            ncore = max(1, int((num_cores ** 0.5) // kpar))  # Square root of the total number of cores
        else:
            ncore = 1  # Default value for unknown system type

        # NPAR recommendations
        npar = max(1, num_cores // (kpar * ncore))

        # LPLANE and NSIM recommendations
        if network_type == "fast":
            lplane = ".TRUE."
            nsim = 4
        else:
            lplane = ".FALSE."
            nsim = 1

        # LSCALU recommendations
        lscalu = ".FALSE."

        # Populate recommendations dictionary
        recommendations["KPAR"] = kpar
        recommendations["NCORE"] = ncore
        recommendations["NPAR"] = npar
        recommendations["LPLANE"] = lplane
        recommendations["NSIM"] = nsim
        recommendations["LSCALU"] = lscalu

        return recommendations
    
    def estimate_vasp_memory(self, num_atoms:int=None, num_kpoints:int=None, num_bands:int=None, ncore:int=1, unit:str='GB'):
        """
        Estimate the amount of RAM needed per node for a VASP calculation.

        Parameters:
            num_atoms (int): Number of atoms in the unit cell.
            num_bands (int): Number of electronic bands in the calculation.
            num_kpoints (int): Number of k-points in the Brillouin zone sampling.
            ncore (int): Number of cores working on each orbital (NCORE).
            unit (str): Desired unit for memory estimation ('KB', 'MB', 'GB').

        Returns:
            float: Estimated RAM needed per node in specified unit.
        """
        
        if not all(isinstance(x, (int, type(None))) for x in [num_atoms, num_kpoints, num_bands, ncore]):
            raise ValueError("All numerical inputs must be integers.")
        
        conversion_factors = {'KB': 2 ** 0, 'MB': 2 ** 10, 'GB': 2 ** 19}
        if unit not in conversion_factors:
            raise ValueError("Invalid unit. Choose among 'KB', 'MB', 'GB'.")

        ncore = ncore if ncore is not None else int(self.InputDFT.parameters.get('NCORE', 1))
        num_bands = num_bands if num_bands is not None else self.estimateNumberOfBands()
        num_kpoints = num_kpoints if num_kpoints is not None else self.estimateNumberOfKPOINTS()
        num_atoms = num_atoms if num_atoms is not None else self.AtomPositionManager.atomCount

        # Estimate the RAM needed for wavefunctions (complex numbers, 16 bytes each for safety)
        wavefunction_memory = num_atoms * num_bands * num_kpoints * 16  # in bytes

        # Estimate memory for Hamiltonian and overlap matrices (using double precision, 8 bytes)
        hamiltonian_memory = num_bands * num_bands * num_kpoints * 8  # in bytes
        
        # Summing up all contributions
        total_memory = wavefunction_memory + hamiltonian_memory  # in bytes

        # Add a safety factor (e.g., 1.2 for 20% extra)
        safety_factor = 1.2

        # Convert to specified unit and multiply by NCORE
        memory_per_node = (wavefunction_memory / conversion_factors[unit]) * ncore * safety_factor # in specified unit

        return memory_per_node

    def estimate_vasp_runtime(self, num_cores, num_atoms:int=None, num_kpoints:int=None, num_bands:int=None, scaling_factor:float=1e-6):
        """
        Estimate the runtime needed for a VASP calculation.

        Parameters:
            num_atoms (int): Number of atoms in the unit cell.
            num_bands (int): Number of electronic bands in the calculation.
            num_kpoints (int): Number of k-points in the Brillouin zone sampling.
            num_cores (int): Number of cores used for the calculation.
            scaling_factor (float): An arbitrary scaling factor to fine-tune the estimate.

        Returns:
            float: Estimated runtime in hours.
        """

        # Estimate the runtime based on the number of atoms, bands, and k-points
        num_bands = num_bands if num_bands is not None else self.estimateNumberOfBands()
        num_kpoints = num_kpoints if num_kpoints is not None else self.estimateNumberOfKPOINTS()
        num_atoms = num_atoms if num_atoms is not None else self.AtomPositionManager.atomCount

        estimated_runtime = (num_atoms * num_bands * num_kpoints) / num_cores * scaling_factor  # in hours

        return estimated_runtime

    def estimateNumberOfBands(self, ):
        """
        Estimate the number of bands needed for a VASP calculation based on the POSCAR file content.

        Parameters:
            poscar_content (str): Content of the POSCAR file as a string.
            valence_electrons (dict): Dictionary mapping element symbols to the number of valence electrons.

        Returns:
            int: Estimated number of bands.
        """
        
        total_electrons = 0

        for element, count in zip(self.AtomPositionManager.uniqueAtomLabels , self.AtomPositionManager.atomCountByType):
            if element not in self.valenceElectrons:
                raise ValueError(f"Valence electrons for element {element} not provided.")
            total_electrons += self.valenceElectrons[element] * count

        num_bands = -(-total_electrons // 2)  # Equivalent to ceil(total_electrons / 2)
        
        return num_bands

    def estimateNumberOfKPOINTS(self,):
        return np.prod(self.KPointsManager.subdivisions)

'''          
path ='/home/akaris/Documents/code/Physics/VASP/v6.2/files/dataset/CoFeNiOOH_jingzhu/bulk_NiFe'
DSR = SingleRunDFT(path)
DSR.readVASPDirectory(v=True)
print(DSR.AtomPositionManager.atomPositions)

DSR.AtomPositionManager

print(DSR.recommend_vasp_parameters(num_cores=80, num_nodes=1))
print( DSR.estimateNumberOfBands() )

print(DSR.estimate_vasp_memory())
print(DSR.estimate_vasp_runtime(40))
'''
