# Import necessary libraries and handle import errors
try:
    from sage_lib.partition.PartitionManager import PartitionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
    del sys

try:
    from sage_lib.IO.structure_handling_tools.AtomPosition import AtomPosition
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
    import os
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing os: {str(e)}\n")
    del sys

class SupercellEmbedding_builder(PartitionManager):
    """
    A class for managing supercell embeddings in computational materials science.

    This class extends PartitionManager and facilitates the manipulation and analysis
    of crystal structures, specifically for creating and handling supercells with defects.
    It supports reading structure data from various file formats, manipulating atomic positions,
    and exporting the modified structures.

    Attributes:
        _unitcell: Container for the unit cell structure.
        _defect_supercell_relax: Container for the relaxed supercell with a defect.
        _defect_supercell_unrelax: Container for the unrelaxed supercell with a defect.
        # Additional attributes...

    Methods:
        read_unitcell: Read the unit cell structure from a file.
        read_defect_supercell_relax: Read the relaxed supercell with a defect.
        read_defect_supercell_unrelax: Read the unrelaxed supercell with a defect.
        # Other methods...
    """

    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initialize the SupercellEmbedding_builder object.

        Parameters:
            file_location (str): Default directory for reading and writing files.
            name (str): Name identifier for the builder instance.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(name=name, file_location=file_location)
        self.AtomPositionManager_constructor = AtomPosition

        self._unitcell = None
        self._defect_supercell_relax = None
        self._defect_supercell_unrelax = None
        
        self._defect_supercell_unrelax_Np1 = None
        self._supercell_Nlayer = None

        self.read_dict = {
                'VASP':'read_POSCAR',
                'PDB':'read_PDB',
                'ASE':'read_ASE',
                'XYZ':'read_XYZ',
                'AIMS':'read_AIMS',
                    }

    def read_unitcell(self, file_location:str=None, file_name:str=None, source:str='VASP'):
        """
        Read the unit cell structure from a specified file.

        Parameters:
            file_location (str): Directory of the file.
            file_name (str): Name of the file containing the unit cell data.
            source (str): Type of the source file format (e.g., 'VASP', 'PDB').

        Raises:
            IOError: If the file cannot be read.
        """
        self.read(file_location=file_location, file_name=file_name, atributte='_unitcell', source=source)

    def read_defect_supercell_relax(self, file_location:str=None, file_name:str=None, source:str='VASP'):
        self.read(file_location=file_location, file_name=file_name, atributte='_defect_supercell_relax', source=source)

    def read_defect_supercell_unrelax(self, file_location:str=None, file_name:str=None, source:str='VASP'):
        self.read(file_location=file_location, file_name=file_name, atributte='_defect_supercell_unrelax', source=source)

    def read(self, file_location:str=None, file_name:str=None, atributte=None, source:str='VASP', verbose:bool=False):
        if file_name is None:
            file_location, file_name = os.path.split(file_location)
        file_location = '.' if file_location == '' else file_location
        self.file_location = file_location
        self.loadStoreManager(self.AtomPositionManager_constructor, f'{file_name}', f'{atributte}', f'{self.read_dict[source.upper()]}', verbose)

    @property
    def supercell_Nlayer(self, ):
        """
        Calculate and return the number of layers in the supercell.

        Returns:
            int: The number of layers in the supercell.

        Raises:
            ValueError: If the layers cannot be determined consistently.
        """
        # Asegúrate de que no haya división por cero o por NaN
        safe_divide = np.divide(self._defect_supercell_unrelax.latticeVectors, self.unitcell.latticeVectors, out=np.zeros_like(self._defect_supercell_unrelax.latticeVectors), where=self.unitcell.latticeVectors!=0)

        # Procesamiento posterior
        rounded_vector = np.nan_to_num(safe_divide, nan=0).round().flatten()
        rounded_vector = rounded_vector[rounded_vector != 0]  # Filtrar ceros

        # 
        if np.all(rounded_vector == rounded_vector[0]):
            # 
            self._supercell_Nlayer = int(rounded_vector[0])
        else:
            # 
            raise ValueError("Los elementos del vector no son todos iguales.")

        return self._supercell_Nlayer


    def make_supercell_embedding(self, ):
        """
        Constructs the supercell embedding by combining different structural components.

        This method initiates the process of creating a supercell embedding by instantiating an AtomPosition object,
        generating an onion layer around the defect, correcting the defect structure, and adding the inner structure of the supercell.
        """
        self._defect_supercell_unrelax_Np1 = AtomPosition()  # Initialize AtomPosition for the new supercell
        self.generate_onion_layer()  # Generate the outer layers of the supercell
        self.correct_defect_structure()  # Correct the structure for any defects
        self.add_inner_structure()  # Add the inner atomic structure to the supercell

    def correct_defect_structure(self, ):
        """
        Corrects the defect structure in the supercell.

        This method adjusts the positions of atoms in the relaxed defect supercell to account for any discrepancies caused by relaxation.
        It ensures that the positions in the relaxed supercell match those in the unrelaxed supercell after accounting for any fractional changes.
        """
        catomPositions_fractional_before_wrap = self.defect_supercell_unrelax_Np1.atomPositions_fractional 
        #self.defect_supercell_relax.wrap()
        fractional_correction = np.round(self._defect_supercell_relax.atomPositions_fractional - self._defect_supercell_unrelax.atomPositions_fractional)
        self._defect_supercell_relax.set_atomPositions_fractional( self._defect_supercell_relax.atomPositions_fractional - fractional_correction )

        # Store initial fractional positions before correction
        catomPositions_fractional_before_wrap = self.defect_supercell_unrelax_Np1.atomPositions_fractional 
        
        # Calculate the fractional correction needed
        fractional_correction = np.round(self._defect_supercell_relax.atomPositions_fractional - self._defect_supercell_unrelax.atomPositions_fractional)
        
        # Apply the fractional correction to the relaxed supercell
        self._defect_supercell_relax.set_atomPositions_fractional( self._defect_supercell_relax.atomPositions_fractional - fractional_correction )

    def add_inner_structure(self, ):
        """
        Adds the inner structure of the defect supercell.

        This method iterates through the atoms in the relaxed defect supercell and adds them to the unrelaxed supercell.
        It effectively combines the inner atomic structure with the supercell embedding.
        """
        for inner_atom_label, inner_atom_position in zip(self.defect_supercell_relax.atomLabelsList, self.defect_supercell_relax.atomPositions):
            self._defect_supercell_unrelax_Np1.add_atom( atomLabels=inner_atom_label, atomPosition=inner_atom_position, )

    def generate_onion_layer(self, repeat:np.array=np.array([1,1,1], dtype=np.int64), supercell_Nlayer:int=None ):
        """
        Generates an 'onion layer' structure for a supercell.

        This method creates a supercell by replicating the unit cell in three dimensions. It allows for an additional layer of atoms,
        known as an onion layer, to be added around the supercell for simulation purposes.

        Parameters:
            repeat (np.array): A 3-element array indicating the number of times to replicate the unit cell in each dimension.
            supercell_Nlayer (int): The number of layers in the supercell.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        supercell_Nlayer = supercell_Nlayer if isinstance(supercell_Nlayer, int) else self.supercell_Nlayer
        a, b, c = self.unitcell.latticeVectors  # Extract lattice vectors
        nx, ny, nz = repeat  # Replication factors

        # Create displacement vectors for the onion layer
        displacement_vectors = [a * i + b * j + c * k for i in range(supercell_Nlayer+nx) for j in range(supercell_Nlayer+ny) for k in range(supercell_Nlayer+nz) if i>=supercell_Nlayer or j>=supercell_Nlayer or k>=supercell_Nlayer]

        # Replicate and position atoms in the supercell
        atom_positions = np.array(self.unitcell.atomPositions)
        supercell_positions = np.vstack([atom_positions + dv for dv in displacement_vectors])

        # Replicate atom labels and constraints for the supercell
        supercell_atomLabelsList = np.tile(self.unitcell.atomLabelsList, len(displacement_vectors))
        supercell_atomicConstraints = np.tile(self.unitcell.atomicConstraints, (len(displacement_vectors), 1))

        # Set the attributes for the unrelaxed supercell with the new layer
        self._defect_supercell_unrelax_Np1._atomLabelsList = supercell_atomLabelsList
        self._defect_supercell_unrelax_Np1._atomicConstraints = supercell_atomicConstraints
        self._defect_supercell_unrelax_Np1._atomPositions = supercell_positions
        self._defect_supercell_unrelax_Np1._latticeVectors = self.unitcell._latticeVectors*(np.array(repeat) + supercell_Nlayer)

        # Resetting other related attributes
        self._defect_supercell_unrelax_Np1._atomPositions_fractional = None
        self._defect_supercell_unrelax_Np1._atomCount = None
        self._defect_supercell_unrelax_Np1._atomCountByType = None
        self._defect_supercell_unrelax_Np1._fullAtomLabelString = None

        return True

    def export_defect_supercell_unrelax_Np1(self, source:str='VASP', file_location:str=None):
        """
        Exports the unrelaxed defect supercell.

        This method allows the export of the unrelaxed defect supercell in various file formats, facilitating further analysis or simulation.

        Parameters:
            source (str): The format to export the supercell in (e.g., 'VASP', 'AIMS').
            file_location (str): The directory to save the exported file.
        """
        self.defect_supercell_unrelax_Np1.export(source='AIMS', file_location=file_location)
