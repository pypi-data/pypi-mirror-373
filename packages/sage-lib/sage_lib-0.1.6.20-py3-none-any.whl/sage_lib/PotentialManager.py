try:
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class PotentialManager(FileManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(file_location=file_location, name=name)
        self._comment = None
        self._PotentialFiles = None
        self._atom_parameters = None
        self._atom_types = None
        
        self._parameters_data = {
            'VRHFIN': {
                'class': 'Atom Information',
                'type': 'string',
                'description': 'Specifies the valence configuration of the atom. For Mg, it is s2p0.'
            },
            'LEXCH': {
                'class': 'Exchange-Correlation',
                'type': 'string',
                'description': 'Defines the exchange-correlation functional. "PE" likely refers to PBE.'
            },
            'EATOM': {
                'class': 'Atom Information',
                'type': 'float',
                'description': 'Total energy of the atom in eV or Rydberg units.'
            },
            'TITEL': {
                'class': 'Metadata',
                'type': 'string',
                'description': 'Title or identification of the pseudopotential used.'
            },
            'IUNSCR': {
                'class': 'Screening',
                'type': 'integer',
                'description': 'Defines the unscreening method: 0 for linear, 1 for nonlinear, 2 for none.'
            },
            'RPACOR': {
                'class': 'Core',
                'type': 'float',
                'description': 'Partial core radius in atomic units.'
            },
            'POMASS': {
                'class': 'Atom Information',
                'type': 'float',
                'description': 'Mass of the atom in atomic mass units.'
            },
            'ZVAL': {
                'class': 'Atom Information',
                'type': 'float',
                'description': 'Valence charge of the atom.'
            },
            'RCORE': {
                'class': 'Core',
                'type': 'float',
                'description': 'Outermost cutoff radius in atomic units.'
            },
            'RCLOC': {
                'class': 'Local Potential',
                'type': 'float',
                'description': 'Cutoff radius for the local potential in atomic units.'
            },
            'LCOR': {
                'class': 'Correction',
                'type': 'boolean',
                'description': 'Whether to correct the augmentation charges.'
            },
            'LPAW': {
                'class': 'Pseudopotential',
                'type': 'boolean',
                'description': 'Whether the pseudopotential is of the PAW type.'
            },
            'EAUG': {
                'class': 'Augmentation',
                'type': 'float',
                'description': 'Total energy contribution from the augmentation charges.'
            },
            'DEXC': {
                'class': 'Exchange-Correlation',
                'type': 'float',
                'description': 'Additional exchange-correlation energy.'
            },
            'RMAX': {
                'class': 'Core',
                'type': 'float',
                'description': 'Core radius for the projection operators.'
            },
            'RAUG': {
                'class': 'Augmentation',
                'type': 'float',
                'description': 'Factor for determining the augmentation sphere radius.'
            },
            'RDEP': {
                'class': 'Grid',
                'type': 'float',
                'description': 'Radius for the radial grid in atomic units.'
            },
            'RDEPT': {
                'class': 'Augmentation',
                'type': 'float',
                'description': 'Core radius for the augmentation charge.'
            }
        }

    @property
    def atom_types(self):
        if not self._atom_types is None:
            return self._atom_types
        elif self._atom_parameters is not None:
            self._atom_types = list(self._atom_parameters.keys())
            return self._atom_types
        elif self._PotentialFiles is not None:
            self._atom_types = list(self._PotentialFiles.keys())
            return self._atom_types           
        elif '_atom_parameters' not in self.__dict__ or '_PotentialFiles' not in self.__dict__:
            raise AttributeError("Attributes _atom_parameters or _PotentialFiles must be initialized before accessing latticeParameters.")

    def readPOTCAR(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self.file_location
        reading_parameters = False
        atom_parameters = {}  # Dictionary to store parameters for each atom type
        parameters = {}

        current_atom_type = None  # Variable to store the current atom type

        lines =list(self.read_file(file_location,strip=False))

        PotentialFiles = {}
        potential_init = 0

        for i, line in enumerate(lines): # read the file {file_name} line by line
            if "End of Dataset" in line:  # End of a POTCAR dataset

                if current_atom_type:
                    atom_parameters[current_atom_type] = parameters
                    PotentialFiles[current_atom_type] = lines[potential_init:i+1]
                parameters = {}
                current_atom_type = None
                potential_init = i+1

            elif "TITEL" in line:  # Identify the atom type
                current_atom_type = line.split()[3]

            elif "parameters from PSCTR are:" in line:
                reading_parameters = True
                continue  # Skip the current line 
            
            elif "END of PSCTR-controll parameters" in line:
                reading_parameters = False
            
            if reading_parameters and line.strip():  # Check if line is not empty
                param_data = line.split('=')  # Split parameter and value
                if len(param_data) >= 2:  # Ensure there is a parameter and a value
                    param, value = param_data[0].strip(), param_data[1].strip()

                    # Store the parameter in the parameters dictionary
                    if param in parameters:
                        parameters[param].append(value)
                    else:
                        parameters[param] = [value]

        self.PotentialFiles = PotentialFiles
        self.atom_parameters = atom_parameters  # Store the complete dictionary in the object

    def exportAsPOTCAR(self, file_location:str=None, uniqueAtomLabels:list=None):
        # Determine the file location
        file_location = file_location if file_location is not None else self.file_location

        # Open the file in write mode
        with open(file_location, 'w') as f:
            for ual in uniqueAtomLabels:
                key = next((key for key in self.PotentialFiles if ual in key), None)
                for line in self.PotentialFiles[key]:
                    f.write(line)

    def summary(self, ):
        text_str = ''
        for p, v in self.parameters.items():
            if p in self.parameters_data:
                description = self.parameters_data[p]['description']
                text_str += f'{p:<10.10s} : {description:<80.80s} \n'
                for n in v: 
                    text_str += f'{n}, '
                text_str += '\n'
            else:
                text_str += f'{p:<10.10s}\n' 

        return text_str

'''
pot = PotentialManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/POTCAR/POTCAR')
pot.readPOTCAR()
print(pot.PotentialFiles)
print( pot.summary() )
pot.exportAsPOTCAR('/home/akaris/Documents/code/Physics/VASP/v6.1/files/POTCAR/POTCAR_export')
'''

