try:
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    from sage_lib.KPointsManager import KPointsManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing KPointsManager: {str(e)}\n")
    del sys

try:
    from sage_lib.InputDFT import InputDFT
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing InputDFT: {str(e)}\n")
    del sys

try:
    from sage_lib.PotentialManager import PotentialManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PotentialManager: {str(e)}\n")
    del sys

try:
    from sage_lib.PeriodicSystem import PeriodicSystem
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PeriodicSystem: {str(e)}\n")
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

class OutFileManager(FileManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initialize OutFileManager class.
        :param file_location: Location of the file to be read.
        :param name: Name identifier for the file.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(name=name, file_location=file_location)
        self._comment = None
        self._InputFileManager = InputDFT(self.file_location)
        self._KPointsManager = KPointsManager(self.file_location)
        self._AtomPositionManager = [ ]
        self._PotentialManager = PotentialManager(self.file_location)
        
        self._parameters = {}
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

    def _extract_variables(self, value):
        tokens = re.split(r'[ \t]+', value.strip())
        processed = []
        
        for i, t in enumerate(tokens):
            token_value = 'True' if t == 'T' else 'False' if t == 'F' else str(t) if self.is_number(t) else t
            if i > 0 and not self.is_number(t): break
            processed.append(token_value)

        return ' '.join(processed) if len(processed) > 1 else processed[0]


    def readOUTCAR(self, file_location:str=None):
        
        def _extract_parameter(APM_attribute, initial_j, columns_slice=slice(1, None)):
            j = initial_j
            setattr(APM, APM_attribute, [])
            while True:
                if not lines[i + j].strip():break
                try:
                    getattr(APM, APM_attribute).append( list(map(float, lines[i + j].split()))[columns_slice] )
                    j += 1
                except:
                    break
            setattr(APM, APM_attribute, np.array(getattr(APM, APM_attribute)))

            return APM

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
        keyword_re = re.compile(r'E-fermi|POTCAR|total charge|magnetization|TOTAL-FORCE|energy  without entropy=|Edisp|Ionic step|direct lattice vectors')
        keyword_ion = re.compile(r'E-Ionic step|Iteration')

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            line_vec = [x for x in line.strip().split(' ') if x]
            
            if read_parameters:
                if keyword_ion.search(line):
                    read_parameters = False
                    self.parameters['uniqueAtomLabels'] = uniqueAtomLabels[:len(uniqueAtomLabels)//2]
                    self.parameters['atomCountByType'] = self.parameters['type']
                    APM = PeriodicSystem()

                elif 'POTCAR:' in line:
                    uniqueAtomLabels.append( list(set(re.split(r'[ _]', line)).intersection(self.atomic_id))[0] )

                elif 'NIONS' in line:
                    self.parameters['NIONS'] = int(line_vec[11])

                else:
                    for key, value in re.findall(param_re, line.strip()):
                        self._update_parameters(key, self._extract_variables(value))
  
            elif keyword_re.search(line):  # Usa el método `search` para buscar cualquiera de las palabras clave en la línea
                    
                if 'Ionic step' in line:
                    if APM:
                        APM._atomCount = self.parameters['NIONS']
                        APM._uniqueAtomLabels = self.parameters.get('uniqueAtomLabels')
                        APM._atomCountByType = [ int(n) for n in self.parameters.get('atomCountByType').split(' ') ]
                        APM_holder.append(APM)
                    APM = PeriodicSystem()

                elif 'E-fermi' in line:
                    APM._E_fermi = float(line_vec[2])
                elif 'Edisp' in line:
                    APM._Edisp = float(line_vec[-1][:-1])
                elif 'energy  without entropy=' in line:
                    APM._E = float(line_vec[-1])
                elif 'direct lattice vectors' in line: 
                    _extract_parameter('_latticeVectors', 1, slice(0, 3))
                    
                elif 'total charge' in line and not 'charge-density' in line: 
                    _extract_parameter('_charge', 4, slice(1, None))

                elif 'magnetization (x)' in line: 
                    _extract_parameter('_magnetization', 4, slice(1, None))

                elif 'TOTAL-FORCE' in line: 
                    _extract_parameter('_total_force', 2, slice(3, None))
                    _extract_parameter('_atomPositions', 2, slice(0, 3))

                elif '2PiTHz' in line: 
                    _extract_parameter('_IRdisplacement', 2, slice(3, None))

        self._AtomPositionManager = APM_holder

    def _update_parameters(self, var_name, value):
        #print(var_name)
        if var_name in self.parameters_data:
            self.parameters[var_name] = value

        if var_name in self._InputFileManager.parameters_data:
            self._InputFileManager.parameters[var_name] = value

    def _handle_regex_matches(self, line_vec, line):
        if 'E-fermi' in line:
            self.E_fermi = float(line_vec[2])
        elif 'NIONS' in line:
            self.NIONS = int(line_vec[11])
            self._AtomPositionManager[-1]._atomCount = int(line_vec[11])

        elif 'POTCAR' in line: 
            try:    
                if not line.split(':')[1] in self.POTCAR_full:
                    self.POTCAR_full.append(line.split(':')[1])
                if not line.split(':')[1].strip().split(' ')[1] in self.POTCAR:
                    self.POTCAR.append( line.split(':')[1].strip().split(' ')[1] )
            except: pass

        elif 'direct lattice vectors' in line: 
            self._AtomPositionManager[-1]._latticeVectors = np.array((map(float, lines[i + 1 + j].split()[3:])))
            
        elif 'total charge' in line and not 'charge-density' in line: 
            TC = self.NIONS+4
            total_charge = np.zeros((self.NIONS,4))
            TC_counter = 0 

    def export_configXYZ(self, file_location:str=None, save_to_file:str='w', verbose:bool=False):
        file_location  = file_location if file_location else self.file_location+'_config.xyz'

        with open(file_location, save_to_file) as f:
            for APM in self.AtomPositionManager:
                f.write(APM.export_as_xyz(file_location, save_to_file=False, verbose=False))

        if verbose:
            print(f"XYZ content has been saved to {file_location}")


'''
o = OutFileManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/OUTCAR/OUTCAR')
o.readOUTCAR()
print( o.InputFileManager.exportAsINCAR() )

o.export_configXYZ()

print(o.AtomPositionManager)
#print( [ APM.E for APM in o._AtomPositionManager ])
for n in o.AtomPositionManager:
    print(n.total_force[0])

'''
