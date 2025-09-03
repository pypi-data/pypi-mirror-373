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

try:
    from datetime import datetime
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing datetime: {str(e)}\n")
    del sys

class FileManager:
    def __init__(self, file_location:str=None, name:str=None):
        if name is not None and not isinstance(name, str):
            raise TypeError("(!) name must be a string")
        self._name = name
        self._metaData = {}
        self._comment = ''
        if file_location is not None and not isinstance(file_location, str):
            raise TypeError("(!) file_location must be a string")
        self._file_location = file_location   
        self._original_file_location = None

        self._plot_color = [ # pastel
            '#FFABAB',  # Salmon (Pastel)       #FFABAB    (255,171,171)
            '#A0C4FF',  # Sky Blue (Pastel)     #A0C4FF    (160,196,255)
            '#B4F8C8',  # Mint (Pastel)         #B4F8C8    (180,248,200)
            '#FFE156',  # Yellow (Pastel)       #FFE156    (255,225,86)
            '#FBE7C6',  # Peach (Pastel)        #FBE7C6    (251,231,198)
            '#AB83A1',  # Mauve (Pastel)        #AB83A1    (171,131,161)
            '#6C5B7B',  # Thistle (Pastel)      #6C5B7B    (108,91,123)
            '#FFD1DC',  # Pink (Pastel)         #FFD1DC    (255,209,220)
            '#392F5A',  # Purple (Pastel)       #392F5A    (57,47,90)
            '#FF677D',  # Watermelon (Pastel)   #FF677D    (255,103,125)
            '#FFC3A0',  # Coral (Pastel)        #FFC3A0    (255,195,160)
            '#6A057F',  # Lavender (Pastel)     #6A057F    (106,5,127)
            '#D4A5A5',  # Rose (Pastel)         #D4A5A5    (212,165,165)
            '#ACD8AA',  # Sage (Pastel)         #ACD8AA    (172,216,170)
        ]

        self._valenceElectrons = {
                "H": 1, "He": 2,
                "Li": 1, "Be": 2, "B": 3, "C": 4, "N": 5, "O": 6, "F": 7, "Ne": 8,
                "Na": 1, "Mg": 2, "Al": 3, "Si": 4, "P": 5, "S": 6, "Cl": 7, "Ar": 8,
                "K": 1, "Ca": 2, "Sc": 3, "Ti": 4, "V": 5, "Cr": 6, "Mn": 7, "Fe": 8, "Co": 9, "Ni": 10, "Cu": 11, "Zn": 12,
                "Ga": 3, "Ge": 4, "As": 5, "Se": 6, "Br": 7, "Kr": 8,
                "Rb": 1, "Sr": 2, "Y": 3, "Zr": 4, "Nb": 5, "Mo": 6, "Tc": 7, "Ru": 8, "Rh": 9, "Pd": 10, "Ag": 11, "Cd": 12,
                "In": 3, "Sn": 4, "Sb": 5, "Te": 6, "I": 7, "Xe": 8,
                "Cs": 1, "Ba": 2, "La": 3, "Ce": 4, "Pr": 5, "Nd": 6, "Pm": 7, "Sm": 8, "Eu": 9, "Gd": 10, "Tb": 11, "Dy": 12, 
                "Ho": 13, "Er": 14, "Tm": 15, "Yb": 16, "Lu": 17, "Hf": 4, "Ta": 5, "W": 6, "Re": 7, "Os": 8, "Ir": 9, 
                "Pt": 10, "Au": 11, "Hg": 12, "Tl": 13, "Pb": 14, "Bi": 15, "Th": 16, "Pa": 17, "U": 18, "Np": 19, "Pu": 20
                                }

        self._atomic_mass =  {
            'H': 1.00794, 'He': 4.002602, 'Li': 6.941, 'Be': 9.0122, 'B': 10.81, 'C': 12.01, 'N': 14.007, 'O': 15.999, 'F': 18.998403163,
            'Ne': 20.1797, 'Na': 22.98976928, 'Mg': 24.305, 'Al': 26.9815386, 'Si': 28.085, 'P': 30.973761998, 'S': 32.06, 'Cl': 35.45,
            'Ar': 39.948, 'K': 39.0983, 'Ca': 40.078, 'Sc': 44.955908, 'Ti': 47.867, 'V': 50.9415, 'Cr': 51.9961, 'Mn': 54.938044,
            'Fe': 55.845, 'Co': 58.933194, 'Ni': 58.6934, 'Cu': 63.546, 'Zn': 65.38, 'Ga': 69.723, 'Ge': 72.63, 'As': 74.921595,
            'Se': 78.971, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.4678, 'Sr': 87.62, 'Y': 88.90584, 'Zr': 91.224, 'Nb': 92.90637,
            'Mo': 95.95, 'Tc': 98.0, 'Ru': 101.07, 'Rh': 102.9055, 'Pd': 106.42, 'Ag': 107.8682, 'Cd': 112.414, 'In': 114.818,
            'Sn': 118.71, 'Sb': 121.76, 'Te': 127.6, 'I': 126.90447, 'Xe': 131.293, 'Cs': 132.90545196, 'Ba': 137.327, 'La': 138.90547,
            'Ce': 140.116, 'Pr': 140.90766, 'Nd': 144.242, 'Pm': 145.0, 'Sm': 150.36, 'Eu': 151.964, 'Gd': 157.25, 'Tb': 158.92535,
            'Dy': 162.5, 'Ho': 164.93033, 'Er': 167.259, 'Tm': 168.93422, 'Yb': 173.04, 'Lu': 174.9668, 'Hf': 178.49, 'Ta': 180.94788,
            'W': 183.84, 'Re': 186.207, 'Os': 190.23, 'Ir': 192.217, 'Pt': 195.084, 'Au': 196.966569, 'Hg': 200.592, 'Tl': 204.38,
            'Pb': 207.2, 'Bi': 208.98040, 'Th': 232.03805, 'Pa': 231.03588, 'U': 238.05078, 'Np': 237.0, 'Pu': 244.0, 'Am': 243.0,
            'Cm': 247.0, 'Bk': 247.0, 'Cf': 251.0, 'Es': 252.0, 'Fm': 257.0, 'Md': 258.0, 'No': 259.0, 'Lr': 262.0, 'Rf': 267.0,
            'Db': 270.0, 'Sg': 271.0, 'Bh': 270.0, 'Hs': 277.0, 'Mt': 276.0, 'Ds': 281.0, 'Rg': 280.0, 'Cn': 285.0, 'Nh': 284.0,
            'Fl': 289.0, 'Mc': 288.0, 'Lv': 293.0, 'Ts': 294.0, 'Og': 294.0
                                }

        self._atomic_id = [ 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 
                            'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 
                            'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 
                            'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
                            'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 
                            'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 
                            'Lv', 'Ts', 'Og']

        self._FM_attrs = set(vars(self).keys())
    def __getattr__(self, name):
        # Check if the attribute exists with a leading underscore
        private_name = f"_{name}"
        if private_name in self.__dict__:
            return getattr(self, private_name)
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        # Check if the attribute exists with a leading underscore
        private_name = f"_{name}"
        if private_name in self.__dict__:
            setattr(self, private_name, value)
        else:
            super().__setattr__(name, value)
            
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("(!) name must be a string")
        self._name = value

    @name.deleter
    def name(self):
        print("Deleting name")
        del self._name

    @property
    def file_location(self):
        return self._file_location

    @file_location.setter
    def file_location(self, value):
        if not isinstance(value, str):
            raise TypeError("(!) file_location must be a string")
        self._file_location = value
        if self._original_file_location == None: 
            self._original_file_location = self._file_location

    @file_location.deleter
    def file_location(self):
        print("Deleting file_location")
        del self._file_location

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def isINT(self, num): return self.is_number(num) and abs(num - int(num)) < 0.0001 

    def file_exists(self, file_path:str) -> bool:
        """Check if a file exists."""
        return os.path.exists(file_path)

    def create_directories_for_path(self, path:str):
        """
        Create any directories needed to ensure that the given path is valid.

        Parameters:
        - path (str): The file or directory path to validate.
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except PermissionError:
                print(f"Permission denied: Could not create directory at {path}")
                # Exit or handle the error appropriately
                exit(1)

    def read_file(self, file_location:str=None, strip=True):
        file_location = file_location if type(file_location) == str else self._file_location

        if file_location is None:
            raise ValueError("(!) File location is not set.")
        
        try:
            with open(file_location, 'r') as file:
                if strip:
                    for line in file:
                        yield line.strip()  # strip() elimina espacios y saltos de línea al principio y al final
                else:
                    for line in file:
                        yield line  # strip() elimina espacios y saltos de línea al principio y al final
        except FileNotFoundError:
            raise FileNotFoundError(f"(!) File not found at {file_location}")
        except IOError:
            raise IOError(f"(!) Error reading file at {file_location}")
        except Exception as e:
            print(f"Error inesperado: {e}")

    def loadStoreManager(self, manager_class, file_name:str, attribute_name: str, read_method:str, v:bool=False):
        """Generic function to read a VASP file."""
        file_path = f"{self.file_location}/{file_name}"
        if not self.file_exists(file_path):
            return

        try:
            manager = manager_class(file_path)
            getattr(manager, read_method)()  # Call the appropriate read method
            setattr(self, attribute_name, manager)
            self._loaded[file_name] = True
            if v:
                print(f'File readed : {file_name}')
        except Exception as e:
            if v:
                print(f"ERROR :: Cannot load {file_name}. Reason: {e}")

    def copy(self, file_location:str=None, original_file_location:str=None, buffer_size=1024*1024) -> bool:
        """
        Universal copy method that chooses an available copy method.
        
        Parameters:
        - dest_path (str): The destination path where the file will be copied.
        - buffer_size (int): The buffer size for manual copy if needed.
        
        Returns:
        - bool: True if the file was successfully copied, otherwise False.
        """
        file_location  = file_location if file_location else self.file_location
        original_file_location  = original_file_location if original_file_location else self.original_file_location

        if original_file_location is None:
            print("Original file path is not set.")
            return False
        try:
            os.system(f"cp {original_file_path} {file_location}")
            return True
        except Exception as e:
            if verbosity: print(f"An error occurred while copying the file: {e}")
            return False 

    def copy_file_manual(self, file_location:str=None, original_file_location:str=None, buffer_size:int=1024*1024) -> bool:
        """
        Manually copy a file in a memory-efficient manner.
        
        Parameters:
        - dest_path (str): The destination path where the file will be copied.
        - buffer_size (int): The buffer size for the copy operation.
        
        Returns:
        - bool: True if the file was successfully copied, otherwise False.
        """
        try:
            with open(self.original_file_path, 'rb') as src, open(dest_path, 'wb') as dest:
                chunk = src.read(buffer_size)
                while chunk:
                    dest.write(chunk)
                    chunk = src.read(buffer_size)
            return True
        except Exception as e:
            print(f"An error occurred while copying the file: {e}")
            return False
