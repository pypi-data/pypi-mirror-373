# En __init__.py del paquete que contiene AtomPositionManager
try:
    from sage_lib.PeriodicSystem import PeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PeriodicSystem: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import copy 
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

class CrystalDefectGenerator(PeriodicSystem):
    def __init__(self, file_location:str=None, name:str=None, Periodic_Object:object=None, **kwargs):
        if Periodic_Object is not None:
            self.__dict__.update(Periodic_Object.__dict__)
        else:
            super().__init__(name=name, file_location=file_location)
        
        self._Vacancy = None 

    def introduce_vacancy(self, atom_index: int, tolerance=3):
        """
        Introduce a vacancy by removing an atom.
        """
        # Remove the atom at the specified index
        removed_atom_position = self.atomPositions[atom_index]
        removed_atom_label = self.atomLabelsList[atom_index]
        self.remove_atom(atom_index)

        if self.is_surface:
            opposite_atom_index = self.find_opposite_atom(removed_atom_position, removed_atom_label)
            if opposite_atom_index is not None:
                self.remove_atom(opposite_atom_index)

    def introduce_self_interstitial(self, position: np.array):
        """
        Introduce a self-interstitial defect.
        
        A self-interstitial is a type of point defect where an extra atom is added to an interstitial site.
        This method adds an atom to a specified interstitial position and updates the associated metadata.
        """
        self._atomPositions = np.vstack([self._atomPositions, position])
        self._atomLabelsList.append("SomeLabel")  # Replace with appropriate label
        self._atomCount += 1

        # Update _atomCountByType here similar to introduce_vacancy
        
    def introduce_substitutional_impurity(self, atom_index: int, new_atom_label: str):
        """
        Introduce a substitutional impurity.
        
        A substitutional impurity is a type of point defect where an atom is replaced by an atom of a different type.
        This method modifies the type of atom at the specified index to a new type.
        """
        self._atomLabelsList[atom_index] = new_atom_label

        # Update _atomCountByType here similar to introduce_vacancy

    def introduce_interstitial_impurity(self, position: np.array, atom_label: str):
        """
        Introduce an interstitial impurity.
        
        An interstitial impurity is a type of point defect where an atom of a different element is inserted at an interstitial site.
        This method adds an atom of a specified type to a specified interstitial position.
        """
        self._atomPositions = np.vstack([self._atomPositions, position])
        self._atomLabelsList.append(atom_label)
        self._atomCount += 1

        # Update _atomCountByType here similar to introduce_vacancy

    def generate_all_vacancies(self, atomlabel:list=None):
        """
        Generate all possible vacancy configurations for the system.
        
        Parameters:
        - atomlabel (list): Specifies the type of atom (e.g., 'Fe', 'N') for which vacancies should be generated.
                           If None, vacancies for all types of atoms are generated.
        
        Returns:
        - list: A list of AtomSystem objects, each representing a unique vacancy configuration.
        """
        atomlabel = list(atomlabel) if atomlabel is str else atomlabel

        # Initialize a list to hold all possible vacancy configurations
        all_vacancy_configs = []
        all_vacancy_label = []

        # Determine the indices at which vacancies should be introduced
        if atomlabel:
            indices = [i for i, label in enumerate(self.atomLabelsList) if label in atomlabel]
        else:
            indices = np.array(range(self._atomCount), dtype=np.int64)


        # Loop through each atom index to introduce a vacancy at that index
        for i in indices:
            # Clone the current object to preserve the original configuration
            temp_manager = copy.deepcopy(self)
            
            # Introduce a vacancy at index i
            temp_manager.introduce_vacancy(i)

            # Save or output the new configuration
            # For the purpose of this example, we'll append it to a list
            redundancy = lambda all_vacancy_configs, temp_manager: any(np.array_equal(alvc.atomPositions, temp_manager.atomPositions) for alvc in all_vacancy_configs)
            #print(redundancy( all_vacancy_configs, temp_manager) )
                    
            if not redundancy(all_vacancy_configs, temp_manager): 
                all_vacancy_label.append(self.atomLabelsList[i])
                all_vacancy_configs.append(copy.deepcopy(temp_manager))
            
            # The original object remains unchanged, and can be used for the next iteration
        
        # Now, all_vacancy_configs contains all possible vacancy configurations.
        # You could choose to return them, write them to files, analyze them further, etc.
        return all_vacancy_configs, all_vacancy_label

'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk FeOOH with β-NiOOH structure (Fe(LS))'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk FeOOH with β-NiOOH structure (Fe(HS))'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/Bulk β-NiOOH doped with 1 Fe(HS)'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/*OH surface for pure NiOOH'
ap = CrystalDefectGenerator(file_location=path+'/SUPERCELL')
ap.readSIFile()
ap.is_surface = True
print( ap.latticeType )
#ap.introduce_vacancy(atom_index=10)
res,_ = ap.generate_all_vacancies()

ap.exportAsPOSCAR(path+'/POSCAR_d1')
for i, n in enumerate(res):
    n.exportAsPOSCAR(path+f'/POSCAR_d{i}')
'''
