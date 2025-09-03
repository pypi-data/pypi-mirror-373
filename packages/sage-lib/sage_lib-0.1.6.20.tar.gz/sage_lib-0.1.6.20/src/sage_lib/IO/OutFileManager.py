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
    from ..IO.KPointsManager import KPointsManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing KPointsManager: {str(e)}\n")
    del sys

try:
    from ..IO.input_handling_tools.InputFile import InputFile
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing InputFile: {str(e)}\n")
    del sys

try: 
    from ..IO.PotentialManager import PotentialManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PotentialManager: {str(e)}\n")
    del sys

try:
    from ..IO.structure_handling_tools.AtomPosition import AtomPosition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys

try:
    import re
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing re: {str(e)}\n")
    del sys

try:
    import copy
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

from typing import Dict

class OutFileManager(FileManager, AtomicProperties):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initializes the OutFileManager class, which manages the reading and processing of VASP OUTCAR files.

        Inherits from FileManager and AtomicProperties classes to utilize their functionalities.

        Parameters:
        file_location (str, optional): The path to the OUTCAR file.
        name (str, optional): A name identifier for the file.
        kwargs: Additional keyword arguments for extended functionality.
        """
        FileManager.__init__(self, name=name, file_location=file_location)
        
        # Initialize AtomicProperties
        AtomicProperties.__init__(self)

        self._comment = None  # Placeholder for comments within the file
        self._InputFileManager = InputFile(self.file_location)  # Manage the associated input file
        self._KPointsManager = KPointsManager(self.file_location)  # Manage KPoints data
        self._AtomPositionManager = []  # List to store atom position data
        self._PotentialManager = PotentialManager(self.file_location)  # Manage potential data
        
        # Dictionary to store parameters extracted from the OUTCAR file
        self._parameters = {}
        # List of recognized parameter names for parsing the OUTCAR file
        self._parameters_data = ['SYSTEM', 'POSCAR', 'Startparameter for this run:', 'NWRITE', 'PREC', 'ISTART', 
                                'ICHARG', 'ISPIN', 'LNONCOLLINEAR', 'LSORBIT', 'INIWAV', 'LASPH', 'METAGGA', 
                                'Electronic Relaxation 1', 'ENCUT', 'ENINI', 'ENAUG', 'NELM', 'EDIFF', 'LREAL', 
                                'NLSPLINE', 'LCOMPAT', 'GGA_COMPAT', 'LMAXPAW', 'LMAXMIX', 'VOSKOWN', 'ROPT', 
                                'ROPT', 'Ionic relaxation', 'EDIFFG', 'NSW', 'NBLOCK', 'IBRION', 'NFREE', 'ISIF',
                                'IWAVPR', 'ISYM', 'LCORR', 'POTIM', 'TEIN', 'TEBEG', 'SMASS', 'estimated Nose-frequenzy (Omega)', 
                                'SCALEE', 'NPACO', 'PSTRESS', 'Mass of Ions in am', 'POMASS', 'Ionic Valenz', 
                                'ZVAL', 'Atomic Wigner-Seitz radii', 'RWIGS', 'virtual crystal weights', 'VCA', 
                                'NELECT', 'NUPDOWN', 'DOS related values:', 'EMIN', 'EFERMI', 'ISMEAR', 
                                'Electronic relaxation 2 (details)', 'IALGO', 'LDIAG', 'LSUBROT', 'TURBO', 
                                'IRESTART', 'NREBOOT', 'NMIN', 'EREF', 'IMIX', 'AMIX', 'AMIX_MAG', 'AMIN', 'WC', 
                                'Intra band minimization:', 'WEIMIN', 'EBREAK', 'DEPER', 'TIME', 'volume/ion in A,a.u.', 
                                'Fermi-wavevector in a.u.,A,eV,Ry', 'Thomas-Fermi vector in A', 'Write flags', 
                                'LWAVE', 'LCHARG', 'LVTOT', 'LVHAR', 'LELF', 'LORBIT', 'Dipole corrections', 
                                'LMONO', 'LDIPOL', 'IDIPOL', 'EPSILON', 'Exchange correlation treatment:', 'GGA', 
                                'LEXCH', 'VOSKOWN', 'LHFCALC', 'LHFONE', 'AEXX', 'Linear response parameters', 
                                'LEPSILON', 'LRPA', 'LNABLA', 'LVEL', 'LINTERFAST', 'KINTER', 'CSHIFT', 'OMEGAMAX', 
                                'DEG_THRESHOLD', 'RTIME', 'Orbital magnetization related:', 'ORBITALMAG', 'LCHIMAG', 'TITEL', 
                                'DQ','type', 'uniqueAtomLabels', 'NIONS', 'atomCountByType']

        self._dynamical_eigenvalues = None  # IR positions for a finite diference avaluation. Type: FxNx3

        self._dynamical_eigenvector = None  # IR positions for a finite diference avaluation. Type: FxNx3
        self._dynamical_eigenvector_fractional = None  # IR displacement. Type: np.array or None

        self._dynamical_eigenvector_diff = None  # IR positions for a finite diference avaluation. Type: FxNx3
        self._dynamical_eigenvector_diff_fractional = None  # IR displacement. Type: np.array or None

    @property
    def dynamical_eigenvalues(self):
        """

        """
        if isinstance(self._dynamical_eigenvalues, list):
            self._dynamical_eigenvalues = np.array(self._dynamical_eigenvalues, dtype=np.float64)
            return self._dynamical_eigenvalues
        else:
            return self._dynamical_eigenvalues

    @property
    def dynamical_eigenvector(self):
        """

        """
        if isinstance(self._dynamical_eigenvector, list):
            self._dynamical_eigenvector = np.array(self._dynamical_eigenvector, dtype=np.float64)
            return self._dynamical_eigenvector
        else:
            return self._dynamical_eigenvector

    @property
    def dynamical_eigenvector_diff(self):
        """

        """
        if isinstance(self._dynamical_eigenvector_diff, list):
            self._dynamical_eigenvector_diff = np.array(self._dynamical_eigenvector_diff, dtype=np.float64)
            return self._dynamical_eigenvector_diff
        else:
            return self._dynamical_eigenvector_diff

    def _extract_variables(self, value):
        """
        Extracts variables from a string, recognizing and converting T/F to True/False, 
        and handles numerical and string values accordingly.

        Parameters:
        value (str): The string from which variables are to be extracted.

        Returns:
        str or list: A single processed value or a list of processed values.
        """
        tokens = re.split(r'[ \t]+', value.strip())  # Split the value into tokens by whitespace
        processed = []  # List to hold processed tokens
        
        for i, t in enumerate(tokens):
            # Convert T/F to True/False, numbers to numeric types, and keep strings as is
            token_value = 'True' if t == 'T' else 'False' if t == 'F' else str(t) if self.is_number(t) else t
            # Break loop if a non-numeric token is encountered after the first token
            if i > 0 and not self.is_number(t): 
                break
            processed.append(token_value)

        # Join the processed tokens into a string if there are multiple, otherwise return the single token
        return ' '.join(processed) if len(processed) > 1 else processed[0]

    def readOUTCAR(self, file_location: str = None, **kwargs):
        """
        Parses the OUTCAR file from a VASP simulation to extract various parameters and atom positions.

        This method processes the OUTCAR file line by line, extracting parameters like Fermi energy, 
        dispersion energy, lattice vectors, charges, magnetizations, total forces, and atom positions. 
        The information is stored in an AtomPosition object.

        Parameters:
        file_location (str, optional): The path to the OUTCAR file. If not specified, 
                                       uses the instance's default file location.

        Returns:
        None: The method updates the instance's _AtomPositionManager with the parsed data.
        """

        def _extract_parameter(APM_attribute, initial_j, columns_slice=slice(1, None)):
            """
            Extracts numerical data from the lines and adds them to the AtomPosition object.

            Parameters:
            APM_attribute (str): The attribute of the AtomPosition object to update.
            initial_j (int): The initial line offset from the current line to start reading data.
            columns_slice (slice, optional): The slice of columns to be extracted from each line.

            Returns:
            AtomPosition: The updated AtomPosition object.
            """
            j = initial_j
            data = []
            while True:
                if not lines[i + j].strip():break
                try:
                    data.append( list(map(float, lines[i + j].split()))[columns_slice] )
                    j += 1
                except:
                    break

            if isinstance(APM_attribute, str):
                setattr(APM, APM_attribute, np.array(data) )
    
            return data

        file_location = file_location if type(file_location) == str else self.file_location
        lines =list(self.read_file(file_location,strip=False))
        
        # Make frequently used methods local
        local_strip = str.strip
        local_split = str.split

        read_parameters = True
        APM_holder = []
        APM = None 
        uniqueAtomLabels = []

        # Precompile regular expressions for faster matching
        param_re = re.compile(r"(\w+)\s*=\s*([^=]+)(?:\s+|$)")
        keyword_re = re.compile(r'E-fermi|POTCAR|total charge|magnetization|TOTAL-FORCE|energy  without entropy=|Edisp|Ionic step|direct lattice vectors|2PiTHz')
        keyword_ion = re.compile(r'E-Ionic step|Iteration')

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            line_vec = [x for x in line.strip().split(' ') if x]
            
            if read_parameters:
                # Extracting parameters from the initial section of the file
                if keyword_ion.search(line):
                    # Switch off parameter reading after encountering ionic step
                    read_parameters = False
                    # Store unique atom labels and atom count by type
                    self.parameters['uniqueAtomLabels'] = uniqueAtomLabels[:len(uniqueAtomLabels)//2]
                    self.parameters['atomCountByType'] = self.parameters['type']
                    APM = AtomPosition()
                    APM._atomCount = self.parameters['NIONS']
                    APM._uniqueAtomLabels = self.parameters.get('uniqueAtomLabels')
                    APM._atomCountByType = [ int(n) for n in self.parameters.get('atomCountByType').split(' ') ]

                elif 'POTCAR:' in line:
                    # Extracting unique atom labels from POTCAR line
                    uniqueAtomLabels.append( list(set(re.split(r'[ _]', line)).intersection(self.atomic_id))[0] )
                elif 'NIONS' in line:
                    # Extracting total number of ions
                    self.parameters['NIONS'] = int(line_vec[11])

                else:
                    # General parameter extraction
                    for key, value in re.findall(param_re, line.strip()):
                        self._update_parameters(key, self._extract_variables(value))
  
            elif keyword_re.search(line):  # Searching for specific keywords in the line
                    
                if 'Ionic step' in line:
                    # Storing the current APM object and creating a new one for the next ionic step
                    APM_holder.append(APM)
                    APM = AtomPosition()
                    
                    APM._atomCount = self.parameters['NIONS']
                    APM._uniqueAtomLabels = self.parameters.get('uniqueAtomLabels')
                    APM._atomCountByType = [ int(n) for n in self.parameters.get('atomCountByType').split(' ') ]

                elif 'E-fermi' in line:
                    # Extracting Fermi energy
                    APM._E_fermi = float(line_vec[2])
                elif 'Edisp' in line:
                    # Extracting dispersion energy
                    APM._Edisp = float(line_vec[-1][:-1])
                elif 'energy  without entropy=' in line:
                    # Extracting energy without entropy
                    APM._E = float(line_vec[-1])
                elif 'direct lattice vectors' in line: 
                    # Extracting lattice vectors
                    _extract_parameter('_latticeVectors', 1, slice(0, 3))
                    
                elif 'total charge' in line and 'charge-density' not in line: 
                    # Extracting total charge
                    _extract_parameter('_charge', 4, slice(1, None))

                elif 'magnetization (x)' in line: 
                    # Extracting magnetization
                    _extract_parameter('_magnetization', 4, slice(1, None))

                elif 'TOTAL-FORCE' in line: 
                    # Extracting total forces and atom positions
                    _extract_parameter('_total_force', 2, slice(3, None))
                    _extract_parameter('_atomPositions', 2, slice(0, 3))

                elif '2PiTHz' in line: 

                    if not hasattr(self, '_dynamical_eigenvalues') or not isinstance(self._dynamical_eigenvalues, list):
                        setattr(self, '_dynamical_eigenvalues', [re.findall(r'\d+\.\d+', line)])
                    else:
                        self._dynamical_eigenvalues.append( re.findall(r'\d+\.\d+', line) )

                    if not hasattr(self, '_dynamical_eigenvector') or not isinstance(self._dynamical_eigenvector, list):
                        setattr(self, '_dynamical_eigenvector', [_extract_parameter(None, 2, slice(0, 3))])
                    else:
                        self._dynamical_eigenvector.append( _extract_parameter(None, 2, slice(0, 3)) )

                    if not hasattr(self, '_dynamical_eigenvector_diff') or not isinstance(self._dynamical_eigenvector_diff, list):
                        setattr(self, '_dynamical_eigenvector_diff', [_extract_parameter(None, 2, slice(3, None))] )
                    else:
                        self._dynamical_eigenvector_diff.append( _extract_parameter(None, 2, slice(3, None)) ) 

        # Append the final APM object if it exists and is not already in APM_holder
        if isinstance(APM, AtomPosition): #and not APM in APM_holder: 
            APM_holder.append(APM)

        # Updating the instance's AtomPositionManager with the extracted data
        self._AtomPositionManager = APM_holder

    def _update_parameters(self, var_name, value):
        """
        Updates parameter values in the current instance and its associated InputFileManager.

        This method is used to update the parameters dictionary of the current instance and 
        its InputFileManager with new values based on the variable name.

        Parameters:
        var_name (str): The name of the parameter to be updated.
        value: The new value to be set for the parameter.
        """
        # Update parameter in current instance if var_name is recognized
        if var_name in self.parameters_data:
            self.parameters[var_name] = value

        # Update parameter in InputFileManager if var_name is recognized
        if var_name in self._InputFileManager.parameters_data:
            self._InputFileManager.parameters[var_name] = value

    def _handle_regex_matches(self, line_vec, line):
        """
        Handles the parsing of specific lines based on regular expression matches.

        This method is responsible for extracting and setting values like Fermi energy, number of ions, 
        POTCAR information, lattice vectors, etc., based on the content of a given line.

        Parameters:
        line_vec (list): The list of words in the current line.
        line (str): The current line being processed.
        """         
        if 'E-fermi' in line:
            # Extract and set Fermi energy
            self.E_fermi = float(line_vec[2])
        elif 'NIONS' in line:
            # Extract and set the number of ions
            self.NIONS = int(line_vec[11])
            self._AtomPositionManager[-1]._atomCount = int(line_vec[11])

        elif 'POTCAR' in line: 
            # Extract and set POTCAR information
            try:    
                if not line.split(':')[1] in self.POTCAR_full:
                    self.POTCAR_full.append(line.split(':')[1])
                if not line.split(':')[1].strip().split(' ')[1] in self.POTCAR:
                    self.POTCAR.append( line.split(':')[1].strip().split(' ')[1] )
            except: pass

        elif 'direct lattice vectors' in line: 
            self._AtomPositionManager[-1]._latticeVectors = np.array((map(float, lines[i + 1 + j].split()[3:])))
            
        # The following block seems incomplete and might need additional implementation
        elif 'total charge' in line and not 'charge-density' in line: 
            TC = self.NIONS+4
            total_charge = np.zeros((self.NIONS,4))
            TC_counter = 0 

    def readDETAILED(self, file_location: str = None) -> None:
        """
        Parses the output of a DFTB+ calculation and extracts relevant information.

        Parameters:
        - file_location (str): The path to the DFTB+ output file.

        Returns:
        - None: The extracted information is stored in the instance variables.
        """
        import re

        # ————————————————————————————————————————————————————
        # 1) Compile all the regexes we’ll need
        # ————————————————————————————————————————————————————
        # Generic energy lines ("Energy H0:", "Total energy:", etc.)
        _energy_line = re.compile(
            r"^(?P<label>[^:]*[Ee]nergy[^:]*):\s*"
            r"(?P<hartree>[-+]?[0-9]*\.[0-9]+)\s*H\s+"
            r"(?P<ev>[-+]?[0-9]*\.[0-9]+)\s*eV$"
        )
        # Electron‐count blocks, capturing the label inside parentheses
        _elec_block = re.compile(
            r"^Nr\. of electrons \((?P<label>up|down|q|x|y|z)\):\s*"
            r"(?P<value>[-+]?[0-9]*\.?[0-9]+)"
        )

        # Population section headers
        _atom_pop   = re.compile(r"^Atom populations \((?P<label>up|down|q|x|y|z)\)")
        _lshell_pop = re.compile(r"^l-shell populations \((?P<label>up|down|q|x|y|z)\)")
        _orb_pop    = re.compile(r"^Orbital populations \((?P<label>up|down|q|x|y|z)\)")

        # Dipole moment lines (matches "… au" and "… Debye")
        _dipole_au    = re.compile(
            r"^Dipole moment:\s*"
            r"(?P<x>[-+]?[0-9]*\.?[0-9]+)\s+"
            r"(?P<y>[-+]?[0-9]*\.?[0-9]+)\s+"
            r"(?P<z>[-+]?[0-9]*\.?[0-9]+)\s*au$"
        )
        _dipole_debye = re.compile(
            r"^Dipole moment:\s*"
            r"(?P<x>[-+]?[0-9]*\.?[0-9]+)\s+"
            r"(?P<y>[-+]?[0-9]*\.?[0-9]+)\s+"
            r"(?P<z>[-+]?[0-9]*\.?[0-9]+)\s*Debye$"
        )

        # ————————————————————————————————————————————————————
        # 2) Read the file
        # ————————————————————————————————————————————————————
        file_location = file_location or self.file_location
        with open(file_location, 'r') as f:
            lines = f.readlines()

        # ————————————————————————————————————————————————————
        # 3) Initialize all the output containers exactly as before
        # ————————————————————————————————————————————————————
        self.total_charge = None
        self.atomic_gross_charges     = []
        self.atomic_net_populations   = []

        self.atom_populations         = {}
        self.l_shell_populations      = {}
        self.orbital_populations      = {}
        self.spin_energies            = {}
        
        self.total_energies           = {}
        self.dipole_moment            = {}

        # ————————————————————————————————————————————————————
        # 4) Main parsing loop
        # ————————————————————————————————————————————————————
        i = 0
        while i < len(lines):
            text = lines[i].strip()

            # 4.1 Total charge
            if text.startswith('Total charge:'):
                self.total_charge = float(text.split()[-1])
                i += 1
                continue

            # 4.2 Atomic gross charges
            if 'Atomic gross charges (e)' in text:
                i += 2  # skip the two header lines
                while i < len(lines) and lines[i].strip():
                    atom, charge, *_ = lines[i].split()
                    self.atomic_gross_charges.append({
                        'Atom':   int(atom),
                        'Charge': float(charge)
                    })
                    i += 1
                continue

            # 4.3 Atomic net (on-site) populations
            if 'Atomic net (on-site) populations and hybridisation ratios' in text:
                i += 2
                while i < len(lines) and lines[i].strip():
                    atom, pop, hyb, *_ = lines[i].split()
                    self.atomic_net_populations.append({
                        'Atom':         int(atom),
                        'Population':   float(pop),
                        'Hybridisation': float(hyb)
                    })
                    i += 1
                continue

            # 4.4 Generic electron‐count block
            m_elec = _elec_block.match(text)
            if m_elec:
                lbl = m_elec.group('label')
                val = float(m_elec.group('value'))
                # map x→up, y→down, up→up, down→down
                self.spin_energies[lbl] = val

                i += 1
                continue

            # 4.5 Generic "Atom populations" sections
            m_atom = _atom_pop.match(text)
            if m_atom:
                lbl = m_atom.group('label')
                # decide target list
                self.atom_populations[lbl] = []

                i += 2  # skip header
                while i < len(lines) and lines[i].strip():
                    atom, pop, *_ = lines[i].split()
                    self.atom_populations[lbl].append({
                        'Atom':       int(atom),
                        'Population': float(pop)
                    })
                    i += 1
                continue

            # 4.6 Generic l-shell populations
            m_lshell = _lshell_pop.match(text)
            if m_lshell:
                lbl = m_lshell.group('label')
                self.l_shell_populations[lbl] = []

                i += 2
                while i < len(lines) and lines[i].strip():
                    atom, shell, l, pop, *_ = lines[i].split()
                    self.l_shell_populations[lbl].append({
                        'Atom':       int(atom),
                        'Shell':      int(shell),
                        'l':          int(l),
                        'Population': float(pop)
                    })
                    i += 1
                continue

            # 4.7 Generic orbital populations
            m_orb = _orb_pop.match(text)
            if m_orb:
                lbl = m_orb.group('label')

                self.orbital_populations[lbl] = []

                i += 2
                while i < len(lines) and lines[i].strip():
                    atom, shell, l, m, pop, label = lines[i].split()
                    self.orbital_populations[lbl].append({
                        'Atom':       int(atom),
                        'Shell':      int(shell),
                        'l':          int(l),
                        'm':          int(m),
                        'Population': float(pop),
                        'Label':      label
                    })
                    i += 1
                continue

            # 4.8 Generic energy lines
            m_en = _energy_line.match(text)
            if m_en:
                while True:
                    m2 = _energy_line.match(lines[i].strip())
                    if not m2:
                        break
                    lbl = m2.group('label').replace(' ', '_')
                    self.total_energies[f"{lbl}_H"]  = float(m2.group('hartree'))
                    self.total_energies[f"{lbl}_eV"] = float(m2.group('ev'))
                    i += 1
                continue

            # 4.9 Dipole moment in au
            m_du = _dipole_au.match(text)
            if m_du:
                self.dipole_moment['x_au'] = float(m_du.group('x'))
                self.dipole_moment['y_au'] = float(m_du.group('y'))
                self.dipole_moment['z_au'] = float(m_du.group('z'))
                i += 1
                continue

            # 4.10 Dipole moment in Debye
            m_dd = _dipole_debye.match(text)
            if m_dd:
                self.dipole_moment['x_debye'] = float(m_dd.group('x'))
                self.dipole_moment['y_debye'] = float(m_dd.group('y'))
                self.dipole_moment['z_debye'] = float(m_dd.group('z'))
                i += 1
                continue

            # 4.11 Anything else
            i += 1

        # ——————————————————————————————————————————————————————————————————
        # 5) Assemble convenience arrays / scalars
        # ——————————————————————————————————————————————————————————————————
        # Gross charges: 1D array of shape (N_atoms,)
        try:
            self.atomic_gross_charges_array = np.array(
                [a['Charge'] for a in self.atomic_gross_charges],
                dtype=float
            )
        except (KeyError, ValueError, TypeError):
            # no data or malformed entries
            self.atomic_gross_charges_array = None

        # Net populations: 2D array of shape (N_atoms, 2) [Population, Hybridisation]
        try:
            self.atomic_net_populations_array = np.array(
                [[a['Population'], a['Hybridisation']] for a in self.atomic_net_populations],
                dtype=float
            )
        except (KeyError, ValueError, TypeError):
            self.atomic_net_populations_array = None

        try:
            self.atom_populations_array = {}
            for key, item in self.atom_populations.items():
                self.atom_populations_array[key] = np.array(
                    [a['Population'] for a in item],
                    dtype=float
                )

        except (KeyError, ValueError, TypeError):
            self.atom_populations_up_array = None


        try:
            self.l_shell_populations_array = {}
            for key, item in self.l_shell_populations.items():
                self.l_shell_populations_array[key] = np.array(
                    [[a['Shell'], a['l'], a['Population']] for a in item],
                    dtype=float
                )

        except (KeyError, ValueError, TypeError):
            self.l_shell_populations_array = None

        try:
            self.orbital_populations_array = {}
            for key, item in self.orbital_populations.items():
                self.orbital_populations_array[key] = np.array(
                    [[a['Shell'], a['l'], a['m'], a['Population']] for a in item],
                    dtype=float
                )

        except (KeyError, ValueError, TypeError):
            self.orbital_populations_array = None

        try:
            self.spin_energies_array = {}
            for key, item in self.spin_energies.items():
                self.spin_energies_array[key] = np.array(
                    [a['Nr_electrons_up'] for a in item],
                    dtype=float
                )

        except (KeyError, ValueError, TypeError):
            self.spin_energies_array = None
