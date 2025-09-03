try:
    from sage_lib.InputFileManager import InputFileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing InputFileManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class InputDFT(InputFileManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)

        self._parameters = {}
    # "Here is a short overview of all parameters currently supported. Parameters which are used frequently are emphasized.
        self._parameters_data = {
    'NGX': {'Default': 'Automatic', 'Class': 'FFT', 'Help': 'FFT mesh for orbitals along the x-axis.', 'Values': 'Positive integers or Automatic'},
    'NGY': {'Default': 'Automatic', 'Class': 'FFT', 'Help': 'FFT mesh for orbitals along the y-axis.', 'Values': 'Positive integers or Automatic'},
    'NGZ': {'Default': 'Automatic', 'Class': 'FFT', 'Help': 'FFT mesh for orbitals along the z-axis.', 'Values': 'Positive integers or Automatic'},
    'NGXF': {'Default': 'Automatic', 'Class': 'FFT', 'Help': 'FFT mesh for charges along the x-axis.', 'Values': 'Positive integers or Automatic'},
    'NGYF': {'Default': 'Automatic', 'Class': 'FFT', 'Help': 'FFT mesh for charges along the y-axis.', 'Values': 'Positive integers or Automatic'},
    'NGZF': {'Default': 'Automatic', 'Class': 'FFT', 'Help': 'FFT mesh for charges along the z-axis.', 'Values': 'Positive integers or Automatic'},
    'NBANDS': {'Default': 'Automatic', 'Class': 'Electronic Structure', 'Help': 'Specifies the number of bands included in the calculation.', 'Values': 'Positive integers or Automatic'},
    'NBLK': {'Default': '1', 'Class': 'Performance', 'Help': 'Blocking factor used for some BLAS calls.', 'Values': 'Positive integers'},
    'INIWAV': {'Default': '1', 'Class': 'Initial Condition', 'Help': 'Initial electronic wavefunction. 0 for lowest eigenvalue, 1 for random initialization.', 'Values': '0 or 1'},
    'NELMIN': {'Default': '4', 'Class': 'Electronic Optimization', 'Help': 'Minimum number of electronic steps.', 'Values': 'Positive integers'},
    'NELMDL': {'Default': 'Automatic', 'Class': 'Electronic Optimization', 'Help': 'Number of initial electronic steps where the algorithm starts linear mixing.', 'Values': 'Integers or Automatic'},
    'NBLOCK': {'Default': '1', 'Class': 'Ionic Update', 'Help': 'Number of steps for ionic update.', 'Values': 'Positive integers'},
    'KBLOCK': {'Default': '1', 'Class': 'Ionic Update', 'Help': 'Inner blocking steps during ionic update.', 'Values': 'Positive integers'},
    'ISIF': {'Default': '2', 'Class': 'Geometry Optimization', 'Help': 'Determines what to calculate and relax: stress tensor, cell shape, etc.', 'Values': '0 to 7'},
    'IWAVPR': {'Default': '10', 'Class': 'Electronic Structure', 'Help': 'Predicts the initial wave function. Options include 0, 1, 2, and 3 for different methods.', 'Values': '0, 1, 2, 3'},
    'ISYM': {'Default': '2', 'Class': 'Symmetry', 'Help': 'Determines whether symmetry is considered. 0 for no symmetry, 1 for use symmetry.', 'Values': '0, 1'},
    'SYMPREC': {'Default': '1E-5', 'Class': 'Symmetry', 'Help': 'Precision in symmetry routines.', 'Values': 'Floating point numbers'},
    'LCORR': {'Default': 'False', 'Class': 'Correction', 'Help': 'Applies Harris-correction to forces.', 'Values': 'True or False'},
    'TEBEG': {'Default': '0', 'Class': 'Molecular Dynamics', 'Help': 'Starting temperature for a molecular dynamics run.', 'Values': 'Floating point numbers or 0 for NVT ensemble'},
    'TEEND': {'Default': 'TEBEG', 'Class': 'Molecular Dynamics', 'Help': 'Ending temperature for a molecular dynamics run.', 'Values': 'Floating point numbers or TEBEG'},
    'SMASS': {'Default': '-3', 'Class': 'Molecular Dynamics', 'Help': 'Nose mass-parameter for thermostat.', 'Values': 'Floating point numbers or -1 for NVE ensemble'},
    'NPACO': {'Default': '256', 'Class': 'Performance', 'Help': 'Number of slots for pair-correlation histogram.', 'Values': 'Positive integers'},
    'APACO': {'Default': '16.0', 'Class': 'Performance', 'Help': 'Distance for pair-correlation histogram.', 'Values': 'Floating point numbers'},
    'POMASS': {'Default': 'From POTCAR', 'Class': 'Atomic Properties', 'Help': 'Mass of ions in atomic mass units. Typically obtained from POTCAR.', 'Values': 'From POTCAR or manual input'},
    'ZVAL': {'Default': 'From POTCAR', 'Class': 'Atomic Properties', 'Help': 'Ionic valence. Typically obtained from POTCAR.', 'Values': 'From POTCAR or manual input'},
    'RWIGS': {'Default': 'From POTCAR', 'Class': 'Atomic Properties', 'Help': 'Wigner-Seitz radii for each atom type.', 'Values': 'From POTCAR or manual input'},
    'NELECT': {'Default': 'Automatic', 'Class': 'Electronic Structure', 'Help': 'Total number of electrons in the system.', 'Values': 'Automatic or manual input'},
    'NUPDOWN': {'Default': '0', 'Class': 'Spin Polarization', 'Help': 'Fixes the total magnetic moment to a specified value.', 'Values': 'Integers'},
    'EMIN': {'Default': 'Automatic', 'Class': 'DOS', 'Help': 'Minimum energy for DOSCAR file.', 'Values': 'Floating point numbers or Automatic'},
    'EMAX': {'Default': 'Automatic', 'Class': 'DOS', 'Help': 'Maximum energy for DOSCAR file.', 'Values': 'Floating point numbers or Automatic'},
    'IALGO': {'Default': '38', 'Class': 'Algorithm', 'Help': 'Specifies the algorithm for electronic minimization. Common choices are 8 for Conjugate Gradient and 48 for RMM-DIIS.', 'Values': 'Integers'},
    'GGA': {'Default': 'PE', 'Class': 'XC Functional', 'Help': 'Specifies the type of Generalized Gradient Approximation. Options include PE, AM, 91 etc.', 'Values': 'PE, AM, 91, ...'},
    'VOSKOWN': {'Default': '1', 'Class': 'XC Functional', 'Help': 'Use Vosko, Wilk, and Nusair interpolation for Ceperley-Alder data.', 'Values': '0 or 1'},
    'DIPOL': {'Default': 'Center of Cell', 'Class': 'Dipole Correction', 'Help': 'Specifies the center of the cell for dipole corrections.', 'Values': 'Cartesian coordinates or Center of Cell'},
    'AMIX': {'Default': '0.4', 'Class': 'Mixing', 'Help': 'Linear mixing parameter for SCF iterations.', 'Values': 'Floating point numbers between 0 and 1'},
    'BMIX': {'Default': '1.0', 'Class': 'Mixing', 'Help': 'Parameter for Kerker-type density mixing.', 'Values': 'Floating point numbers'},
    'WEIMIN': {'Default': '0.02', 'Class': 'Mixing', 'Help': 'Minimum weight for a band to be updated in the SCF iteration.', 'Values': 'Floating point numbers'},
    'EBREAK': {'Default': '1E-5', 'Class': 'Electronic Optimization', 'Help': 'Energy change between two SCF steps below which the calculation is considered converged.', 'Values': 'Floating point numbers'},
    'DEPER': {'Default': '0.3', 'Class': 'Electronic Optimization', 'Help': 'Maximum allowed change of eigenvalues between two SCF steps.', 'Values': 'Floating point numbers'},
    'TIME': {'Default': '0.4', 'Class': 'Performance', 'Help': 'Scaling factor for the time-step in the Born-Oppenheimer Molecular Dynamics.', 'Values': 'Floating point numbers'},
    'LWAVE': {'Default': 'True', 'Class': 'File Control', 'Help': 'Determines whether the WAVECAR file is written.', 'Values': 'True or False'},
    'LCHARG': {'Default': 'True', 'Class': 'File Control', 'Help': 'Determines whether the CHGCAR file is written.', 'Values': 'True or False'},
    'LVTOT': {'Default': 'False', 'Class': 'File Control', 'Help': 'Determines whether the total potential is written to LOCPOT.', 'Values': 'True or False'},
    'LVHAR': {'Default': 'False', 'Class': 'File Control', 'Help': 'Determines whether the Hartree potential is written to LOCPOT.', 'Values': 'True or False'},
    'LELF': {'Default': 'False', 'Class': 'File Control', 'Help': 'Determines whether the ELFCAR file is written.', 'Values': 'True or False'},
    'LORBIT': {'Default': '11', 'Class': 'File Control', 'Help': 'Determines whether the PROCAR or PROOUT files are written. Needs an appropriate RWIGS value.', 'Values': 'Integer values; commonly 10 or 11'},
    'LSCALAPACK': {'Default': 'True', 'Class': 'Performance', 'Help': 'Switches ScaLAPACK on or off.', 'Values': 'True or False'},
    'LSCALU': {'Default': 'False', 'Class': 'Performance', 'Help': 'Switches LU decomposition on or off.', 'Values': 'True or False'},
    'LASYNC': {'Default': 'False', 'Class': 'Performance', 'Help': 'Allows for overlap of communication and calculations.', 'Values': 'True or False'},
    'SYSTEM': {'Default': 'Unknown System', 'Class': 'Meta', 'Help': 'Name of the system under study.', 'Values': 'Any string'},
    'NWRITE': {'Default': '2', 'Class': 'File Control', 'Help': 'Controls the verbosity of the written output.', 'Values': 'Integers'},
    'ICHARG': {'Default': '2', 'Class': 'Initial Condition', 'Help': 'Determines how initial charge density is obtained.', 'Values': '0, 1, 2, 4, 10, 11, 12'},
    'ISTART': {'Default': '0', 'Class': 'Initial Condition', 'Help': 'Determines how the job starts. 0 for new, 1 for continue, 2 for same cut-off.', 'Values': '0, 1, 2'},
    'ISMEAR': {'Default': '0', 'Class': 'Electronic Structure', 'Help': 'Determines how the Fermi level is smoothened.', 'Values': '-5, -4, -1, 0, integers > 0'},
    'ISPIN': {'Default': '1', 'Class': 'Spin Polarization', 'Help': 'Determines if the calculation is spin-polarized.', 'Values': '1 or 2'},
    'MAGMOM': {'Default': '0.6', 'Class': 'Spin Polarization', 'Help': 'Initial magnetic moment for each atom.', 'Values': 'List of floats'},
    'ENCUT': {'Default': 'From POTCAR', 'Class': 'Electronic Structure', 'Help': 'Plane-wave energy cutoff.', 'Values': 'Floats or from POTCAR'},
    'ALGO': {'Default': 'Normal', 'Class': 'Algorithm', 'Help': 'Electronic minimization algorithm.', 'Values': 'Normal, Fast, Very_Fast, All, etc.'},
    'NELM': {'Default': '60', 'Class': 'Electronic Optimization', 'Help': 'Maximum number of electronic self-consistency steps.', 'Values': 'Positive integers'},
    'EDIFF': {'Default': '1E-5', 'Class': 'Electronic Optimization', 'Help': 'Stopping criterion for electronic updates.', 'Values': 'Floats'},
    'SIGMA': {'Default': '0.2', 'Class': 'Electronic Structure', 'Help': 'Smearing width in eV.', 'Values': 'Floats'},
    'EDIFFG': {'Default': '-1E-2', 'Class': 'Ionic Relaxation', 'Help': 'Stopping criterion for ionic updates.', 'Values': 'Floats'},
    'NSW': {'Default': '0', 'Class': 'Ionic Relaxation', 'Help': 'Maximum number of ionic steps.', 'Values': 'Positive integers'},
    'IBRION': {'Default': '1', 'Class': 'Ionic Relaxation', 'Help': 'Algorithm used for ionic updates.', 'Values': '-1, 0, 1, 2, 3, 5, 6, 7, 8'},
    'POTIM': {'Default': '0.5', 'Class': 'Ionic Relaxation', 'Help': 'Time step for ionic motion in fs.', 'Values': 'Floats'},
    'KSPACING': {'Default': '0.5', 'Class': 'k-points', 'Help': 'Determines spacing between k-points if KPOINTS file is not present.', 'Values': 'Floats'},
    'KGAMMA': {'Default': 'True', 'Class': 'k-points', 'Help': 'Includes Gamma point in k-point grid.', 'Values': 'True or False'},
    'PREC': {'Default': 'Normal', 'Class': 'Precision', 'Help': 'Determines the precision level of the calculation.', 'Values': 'Low, Medium, High, Normal, Accurate'},
    'ROPT': {'Default': 'Automatic', 'Class': 'Performance', 'Help': 'Controls the real-space representation of projectors.', 'Values': 'Floats or Automatic'},
    'KPAR': {'Default': '1', 'Class': 'Performance', 'Help': 'Number of k-points to be treated in parallel.', 'Values': 'Positive integers'},
    'LPLANE': {'Default': '.TRUE.', 'Class': 'Performance', 'Help': 'switches on the plane-wise data distribution in real space.', 'Values': 'True or False'},
    'NCORE': {'Default': '1', 'Class': 'Performance', 'Help': 'Number of compute cores working on an individual orbital.', 'Values': 'Positive integers'},
    'LREAL': {'Default': 'Auto', 'Class': 'Performance', 'Help': 'Controls whether projection operators are evaluated in real-space or reciprocal space.', 'Values': 'True, False, Auto'},
    'NPAR': {'Default': 'Automatic', 'Class': 'Performance', 'Help': 'Parallelization over bands.', 'Values': 'Positive integers or Automatic'},
    'IVDW': {'Default': '0', 'Class': 'Van der Waals', 'Help': 'Specifies a van der Waals correction method.', 'Values': '0, 1, 11, 12, 21'},
    'LAECHG': {'Default': 'False', 'Class': 'File Control', 'Help': 'Determines whether AECCAR files are written.', 'Values': 'True or False'},
    'LUSE_VDW': {'Default': 'False', 'Class': 'Van der Waals', 'Help': 'Determines whether to use precomputed van der Waals kernels.', 'Values': 'True or False'},
    'AGGAC': {'Default': '0.0000', 'Class': 'Van der Waals', 'Help': 'Damping parameter in Grimme DFT-D2 method.', 'Values': 'Floating point numbers'},
    'LASPH': {'Default': 'False', 'Class': 'Spherical Harmonics', 'Help': 'Controls whether aspherical contributions within the muffin-tin spheres are taken into account.', 'Values': 'True or False'},
    'PARAM1': {'Default': 'N/A', 'Class': 'User Defined', 'Help': 'User defined parameter for certain functionals or methods.', 'Values': 'Floating point numbers or N/A'},
    'PARAM2': {'Default': 'N/A', 'Class': 'User Defined', 'Help': 'Second user-defined parameter for certain functionals or methods.', 'Values': 'Floating point numbers or N/A'},
    'Zab_vdW': {'Default': 'N/A', 'Class': 'Van der Waals', 'Help': 'Scaling factors for DFT-D3 method.', 'Values': 'Floating point numbers or N/A'},
    'BPARAM': {'Default': 'N/A', 'Class': 'User Defined', 'Help': 'User-defined parameter for specific models or functionals.', 'Values': 'Floating point numbers or N/A'},
    'METAGGA': {'Default': 'None', 'Class': 'XC Functional', 'Help': 'Specifies the type of meta-GGA functional to be used.', 'Values': 'None, SCAN, TPSS, ...'},
    'LDAU': {'Default': 'False', 'Class': 'Electron Correlation', 'Help': 'Controls whether the DFT+U (Hubbard U) correction is applied.', 'Values': 'True or False'},
    'LDAUL': {'Default': '-1 for all ions', 'Class': 'Electron Correlation', 'Help': 'Specifies the angular momentum quantum number l for which the DFT+U corrections are applied.', 'Values': 'Integers or a list of integers'},
    'LDAUJ': {'Default': '0.0 for all ions', 'Class': 'Electron Correlation', 'Help': 'Specifies the value of the exchange parameter J in the DFT+U method.', 'Values': 'Floating point numbers or a list of floating point numbers'},
    'LDAUU': {'Default': '0.0 for all ions', 'Class': 'Electron Correlation', 'Help': 'Specifies the value of the effective U parameter in the DFT+U method.', 'Values': 'Floating point numbers or a list of floating point numbers'},
    'LHFCALC': {'Default': 'False', 'Class': 'Hybrid Functional', 'Help': 'Specifies whether a Hartree-Fock/DFT hybrid functional type calculation is performed.', 'Values': 'True or False'},
    'HFLMAX': {'Default': '4', 'Class': 'Hybrid Functional', 'Help': 'To be compatible w.r.t. old releases, VASP also reads the flag HFLMAX to the same effect as LMAXFOCK.', 'Values': 'Integer'},
    'HFSCREEN': {'Default': '0 (none)', 'Class': 'Hybrid Functional', 'Help': 'Specifies the range-separation parameter in range-separated hybrid functionals.', 'Values': 'Floating point numbers'},
    'ADDGRID': {'Default': 'False', 'Class': 'Grid', 'Help': 'Determines whether an additional support grid is used for the evaluation of the augmentation charges.', 'Values': 'True or False'},
    'LMAXMIX': {'Default': '2', 'Class': 'Mixer', 'Help': 'Controls up to which l-quantum number the one-center PAW charge densities are passed through the charge density mixer and written to the CHGCAR file.', 'Values': 'Integer'},
    'LDAUPRINT': {'Default': '0', 'Class': 'Electron Correlation', 'Help': 'Controls the verbosity of a DFT+U calculation.', 'Values': '0 or 1'},
    'LDAUTYPE': {'Default': '2', 'Class': 'Electron Correlation', 'Help': 'Specifies the DFT+U variant that will be used.', 'Values': '1, 2, or 4'},
    'ENAUG': {'Default': 'largest EAUG read from the POTCAR file', 'Class': 'Plane Wave Energy Cutoff', 'Help': 'ENAUG specifies the cut-off energy of the plane wave representation of the augmentation charges in eV. ENAUG determines NGXF, NGYF, and NGZF in accordance with the PREC tag.','Values': '[real]','Deprecated': 'ENAUG is considered as deprecated and should not be used anymore.'}
}
        '''
        # -------------------------------------------------------------------------- #
        # The GGA tag is further used to choose the appropriate exchange functional. #

        # -- original vdW-DF of Dion et al uses revPBE -- # 
        GGA = RE
        LUSE_VDW = .TRUE.
        AGGAC = 0.0000
        LASPH = .TRUE.

        # --  For optPBE-vdW set -- #
        #GGA = OR
        #LUSE_VDW = .TRUE.
        #AGGAC = 0.0000
        #LASPH = .TRUE.

        # -- optB88-vdW set: -- # 
        #GGA = BO
        #PARAM1 = 0.1833333333
        #PARAM2 = 0.2200000000
        #LUSE_VDW = .TRUE.
        #AGGAC = 0.0000
        #LASPH = .TRUE.

        # -- optB86b-vdW: -- #
        #GGA = MK 
        #PARAM1 = 0.1234 
        #PARAM2 = 1.0000
        #LUSE_VDW = .TRUE.
        #AGGAC = 0.0000
        #LASPH = .TRUE.

        # -- vdW-DF2, set: -- #
        #GGA = ML
        #LUSE_VDW = .TRUE.
        #Zab_vdW = -1.8867
        #AGGAC = 0.0000
        #LASPH = .TRUE.

        # -- The rev-vdW-DF2 functional of Hamada, 
        # also known as vdW-DF2-B86R -- #
        #GGA      = MK
        #LUSE_VDW = .TRUE.
        #PARAM1   = 0.1234
        #PARAM2   = 0.711357
        #Zab_vdW  = -1.8867
        #AGGAC    = 0.0000
        #LASPH = .TRUE.

        # -- the SCAN + rVV10 functional set -- #
        #METAGGA  = SCAN
        #LUSE_VDW = .TRUE.
        #BPARAM = 15.7
        #LASPH = .TRUE.
        # it is NOT  possible to combine SCAN with vdW-DFT functionals other than rVV10.


        # Bader
        #LAECHG = T
        '''

        self.attr_dic = {}
        self.parametersClass = set(value['Class'] for key, value in self.parameters_data.items() )

    def readINCAR(self, file_location=None):
        self.file_location = file_location if type(file_location) == str else self.file_location
        lines = [n for n in self.read_file() ]
        parameters = {}

        for i, line in enumerate(lines):
            if "#" in line: line = line.split("#")[0].strip()
            if "!" in line: line = line.split("!")[0].strip()
            if not line or not '=' in line:    continue

            parts = [l.strip() for l in line.split('=')[0].strip().split(' ') if l.strip() != '' ] + [l.strip() for l in line.split('=')[1].strip().split(' ') if l.strip() != '' ]              

            if len(parts) < 2: 
                continue

            else:
                parameters[parts[0]] = ' '.join(parts[1:]) 

        self.parameters = parameters

    def view(self, ):
        parametersClasification = {**{p: [] for p in self.parametersClass}, 'Others': []}
        text_str = ''

        for p, value in self.parameters.items():
            if p in self.parameters_data:
                pClass = self.parameters_data[p]['Class']
                parametersClasification[pClass].append(p)
            else:
                parametersClasification['Others'].append(p)

        for p, value in parametersClasification.items():
            if len(value) > 0:
                text_str += f'\n ==== {p.center(25)} ====\n'

                for n in value:
                    Help = self.parameters_data[n]['Help']
                    text_str += f"{n:<9} = {self.parameters[n]:<9} # {Help[:40]:<40}\n"

        for n in self.attr_dic.keys():
            if n in self.help.keys():   info = self.help[n]
            else:                       info = 'unknow'
            if self.isINT(self.attr_dic[n]):

                text_str += f'{n:<10.10s} : {int(self.attr_dic[n]):<10} : {info:<80.80s}[...]\n' 
            else:
                text_str += f'{n:<10.10s} : {self.attr_dic[n]:<10.10} : {info:<80.80s}[...]\n' 

        return text_str

    def summary(self, ): return self.view()

    def exportAsINCAR(self, file_location:str=None):
        file_location  = file_location  if not file_location  is None else self.file_location+'INCAR'

        with open(file_location, 'w') as f:
            # Classify parameters
            parametersClasification = {**{p: [] for p in self.parametersClass}, 'Others': []}
            for p, value in self.parameters.items():
                if p in self.parameters_data:
                    pClass = self.parameters_data[p]['Class']
                    parametersClasification[pClass].append(p)
                else:
                    parametersClasification['Others'].append(p)

            # Write classified parameters to the file
            for p, value in parametersClasification.items():
                if len(value) > 0:
                    f.write( f'\n ==== {p.center(25)} ====\n' )
                    for n in value:
                        Help = self.parameters_data[n]['Help']
                        f.write( f"{n:<9} = {self.parameters[n]:<9} # {Help[:80]:<80} [...]\n" )

            # Write attributes to the file
            for n in self.attr_dic.keys():
                if n in self.help.keys():   info = self.help[n]
                else:                       info = 'unknow'
                if self.isINT(self.attr_dic[n]):
                    f.write( f'{n:<10.10s} : {int(self.attr_dic[n]):<10} : {info:<100.100s}[...]\n' )
                else:
                    f.write( f'{n:<10.10s} : {self.attr_dic[n]:<10.10} : {info:<100.100s}[...]\n' )

if __name__ == "__main__":
    # How to...     
    incar = InputDFT()
    incar.readINCAR('/home/akaris/Documents/code/Physics/VASP/v6.1/files/INCAR/INCAR')
    incar.summary()
    incar.exportAsINCAR('/home/akaris/Documents/code/Physics/VASP/v6.1/files/INCAR/INCAR2')
    print( incar.summary() )






