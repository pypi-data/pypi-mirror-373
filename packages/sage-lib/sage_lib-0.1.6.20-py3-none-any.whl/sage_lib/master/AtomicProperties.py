try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class AtomicProperties:
    
    # ============================================================= #
    # Avogadro's Number (mol^-1)
    NA = 6.02214075999999987023872e23  # units: mol^-1
    N_a = NA # units: mol^-1
    
    # Elementary Charge (C)
    e = 1.602176634e-19  # units: C

    # Planck's Constant (J·s)
    h = 6.62607015e-34  # units: J·s

    # Boltzmann Constant (J·K^-1)
    k = 1.380649e-23  # units: J·K^-1

    # Speed of Light in a Vacuum (m/s)
    c = 299792458  # units: m/s

    # Vacuum Permittivity (C^2·N^-1·m^-2)
    epsilon0 = 8.8541878128e-12  # units: C^2·N^-1·m^-2

    # Vacuum Permeability (N·A^-2)
    mu0 = 4 * 3.14159265358979323846e-7  # units: N·A^-2

    # Ideal Gas Constant (J·mol^-1·K^-1)
    R = 8.314462618  # units: J·mol^-1·K^-1

    # Ideal Gas Constant (L·atm·mol^-1·K^-1)
    R_L_atm = 0.08205736608  # units: L·atm·mol^-1·K^-1

    # Electron Mass (kg)
    me = 9.10938356e-31  # units: kg

    # Proton Mass (kg)
    mp = 1.6726219e-27  # units: kg

    # Neutron Mass (kg)
    mn = 1.67492749804e-27  # units: kg

    # Hydrogen Atom Mass (kg)
    mH = 1.6735575e-27  # units: kg

    # Fine-Structure Constant
    alpha = 0.0072973525693  # units: dimensionless

    # Classical Electron Radius (m)
    re = 2.8179403267e-15  # units: m

    # Stefan-Boltzmann Constant (W·m^-2·K^-4)
    sigma = 5.670374419e-8  # units: W·m^-2·K^-4

    # Faraday's Constant (C·mol^-1)
    F = 96485.33289  # units: C·mol^-1

    # Coulomb Constant (N·m^2·C^-2)
    k_C = 8.9875517873681764e9  # units: N·m^2·C^-2

    # Bohr Radius (m)
    a0 = 5.29177210903e-11  # units: m

    # Hydrogen Ionization Energy (eV)
    ionization_H = 13.605693122994  # units: eV

    # Molar Mass of Water (g/mol)
    molar_water = 18.01528  # units: g/mol

    # Molar Volume of an Ideal Gas (L/mol) at Standard Conditions
    V_molar_std = 22.414  # units: L/mol

    # Acid Dissociation Constant of Water (K_a)
    Ka_water = 1.0e-3  # units: dimensionless

    # Base Dissociation Constant of Hydroxide Ion (K_b)
    Kb_hydroxide = 1.0e-14  # units: dimensionless

    # Ion Product Constant of Water (K_w)
    Kw_water = 1.0e-14  # units: dimensionless

    # Speed of Light in Glass (m/s)
    speed_light_glass = 2.0e8  # units: m/s

    # Rydberg Constant (m^-1)
    Rydberg = 1.0973731568539e7  # units: m^-1

    # Universal Gasoline Constant (J/(L·K))
    constant_gasoline = 2.169e7  # units: J/(L·K)
    # ============================================================= #

    plot_color = [ # pastel
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

    atomic_numbers = {
            'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
            'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29,
            'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43,
            'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50, 'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'Lu': 71,
            'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
            'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'U': 92, 'Np': 93, 'Pu': 94, 'X': 99
                            }
    atomic_name = {value: key for key, value in atomic_numbers.items()}
    
    Z = atomic_numbers

    element_names = {
        'H': 'hydrogen', 'He': 'helium', 'Li': 'lithium', 'Be': 'beryllium', 'B': 'boron', 'C': 'carbon', 'N': 'nitrogen', 'O': 'oxygen',
        'F': 'fluorine', 'Ne': 'neon', 'Na': 'sodium', 'Mg': 'magnesium', 'Al': 'aluminium', 'Si': 'silicon', 'P': 'phosphorus', 'S': 'sulfur',
        'Cl': 'chlorine', 'Ar': 'argon', 'K': 'potassium', 'Ca': 'calcium', 'Sc': 'scandium', 'Ti': 'titanium', 'V': 'vanadium', 'Cr': 'chromium',
        'Mn': 'manganese', 'Fe': 'iron', 'Co': 'cobalt', 'Ni': 'nickel', 'Cu': 'copper', 'Zn': 'zinc', 'Ga': 'gallium', 'Ge': 'germanium',
        'As': 'arsenic', 'Se': 'selenium', 'Br': 'bromine', 'Kr': 'krypton', 'Rb': 'rubidium', 'Sr': 'strontium', 'Y': 'yttrium', 'Zr': 'zirconium',
        'Nb': 'niobium', 'Mo': 'molybdenum', 'Tc': 'technetium', 'Ru': 'ruthenium', 'Rh': 'rhodium', 'Pd': 'palladium', 'Ag': 'silver', 'Cd': 'cadmium',
        'In': 'indium', 'Sn': 'tin', 'Sb': 'antimony', 'Te': 'tellurium', 'I': 'iodine', 'Xe': 'xenon', 'Cs': 'cesium', 'Ba': 'barium', 'Lu': 'lutetium',
        'Hf': 'hafnium', 'Ta': 'tantalum', 'W': 'tungsten', 'Re': 'rhenium', 'Os': 'osmium', 'Ir': 'iridium', 'Pt': 'platinum', 'Au': 'gold', 'Hg': 'mercury',
        'Tl': 'thallium', 'Pb': 'lead', 'Bi': 'bismuth', 'Po': 'polonium', 'At': 'astatine', 'Rn': 'radon', 'Fr': 'francium', 'Ra': 'radium', 'Ac': 'actinium',
        'Th': 'thorium', 'U': 'uranium', 'Np': 'neptunium', 'Pu': 'plutonium', 'X': 'X'
                    }

    valenceElectrons = {
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

    atomic_mass =  {
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
    
    atomic_mass_list = (lambda _am=atomic_mass, _an=atomic_name:
        [_am.get(_an.get(Z)) for Z in range(1,100)]
    )()

    covalent_radii = {
        'H' :  .31, 'He':  .28, 'Li': 1.28, 'Be':  .96, 'B' :  .84, 'C' :  .76, 'N' :  .71, 'O' :  .66, 'F': .57,
        'Ne':  .58, 'Na': 1.66, 'Mg': 1.41, 'Al': 1.21, 'Si': 1.11, 'P' : 1.07, 'S' : 1.05, 'Cl': 1.02,
        'Ar': 1.06, 'K' : 1.03, 'Ca': 1.76, 'Sc': 1.70, 'Ti': 1.60, 'V' : 1.53, 'Cr': 1.39, 'Mn': 1.39,
        'Fe': 1.32, 'Co': 1.26, 'Ni': 1.24, 'Cu': 1.32, 'Zn': 1.22, 'Ga': 1.22, 'Ge': 1.20, 'As': 1.19,
        'Se': 1.20, 'Br': 1.20, 'Kr': 1.16, 'Rb': 2.20, 'Sr': 1.95, 'Y' : 1.90, 'Zr': 1.75, 'Nb': 1.64,
        'Mo': 1.54, 'Tc': 1.47, 'Ru': 1.46, 'Rh': 1.42, 'Pd': 1.39, 'Ag': 1.45, 'Cd': 1.44, 'In': 1.42,
        'Sn': 1.39, 'Sb': 1.39, 'Te': 1.38, 'I' : 1.39, 'Xe': 1.40, 'Cs': 2.44, 'Ba': 2.15, 'La': 2.07,
        'Ce': 2.04, 'Pr': 2.03, 'Nd': 2.01, 'Pm': 1.99, 'Sm': 1.98, 'Eu': 1.98, 'Gd': 1.96, 'Tb': 1.94,
        'Dy': 1.92, 'Ho': 1.92, 'Er': 1.89, 'Tm': 1.90, 'Yb': 1.87, 'Lu': 1.87, 'Hf': 1.75, 'Ta': 1.70,
        'W' : 1.62, 'Re': 1.51, 'Os': 1.44, 'Ir': 1.41, 'Pt': 1.36, 'Au': 1.36, 'Hg': 1.32, 'Tl': 1.45,
        'Pb': 1.46, 'Bi': 1.48, 'Th': 1.79, 'Pa': 1.63, 'U' : 1.56, 'Np': 1.55, 'Pu': 1.53, 'Am': 1.51,
        'Cm': 1.50, 'Bk': 1.50, 'Cf': 1.50, 'Es': 1.50, 'Fm': 1.50, 'Md': 1.50, 'No': 1.50, 'Lr': 1.50,
        'Rf': 1.50, 'Db': 1.50, 'Sg': 1.50, 'Bh': 1.50, 'Hs': 1.50, 'Mt': 1.50, 'Ds': 1.50, 'Rg': 1.50,
        'Cn': 1.50, 'Nh': 1.50, 'Fl': 1.50, 'Mc': 1.50, 'Lv': 1.50, 'Ts': 1.50, 'Og': 1.50
    }

    vdw_radii = {
        'H': 1.20, 'He': 1.40, 'Li': 1.82, 'Be': 1.53, 'B': 1.92, 'C': 1.70, 'N': 1.55, 'O': 1.52, 'F': 1.47, 'Ne': 1.54, 'Na': 2.27,
        'Mg': 1.73, 'Al': 1.84, 'Si': 2.10, 'P': 1.80, 'S': 1.80, 'Cl': 1.75, 'Ar': 1.88, 'K': 2.75, 'Ca': 2.31, 'Sc': 2.11, 'Ti': 2.00,
        'V': 1.92, 'Cr': 2.09, 'Mn': 2.09, 'Fe': 1.94, 'Co': 1.92, 'Ni': 1.63, 'Cu': 1.40, 'Zn': 1.39, 'Ga': 1.87, 'Ge': 2.11,
        'As': 1.85, 'Se': 1.90, 'Br': 1.85, 'Kr': 2.02, 'Rb': 3.03, 'Sr': 2.49, 'Y': 2.19, 'Zr': 2.11, 'Nb': 1.98, 'Mo': 2.27,
        'Tc': 2.20, 'Ru': 2.20, 'Rh': 2.18, 'Pd': 2.02, 'Ag': 1.72, 'Cd': 1.58, 'In': 1.93, 'Sn': 2.17, 'Sb': 2.06, 'Te': 2.06,
        'I': 1.98, 'Xe': 2.16, 'Cs': 3.43, 'Ba': 2.68, 'Lu': 1.75, 'Hf': 2.08, 'Ta': 2.11, 'W': 1.93, 'Re': 1.88, 'Os': 1.85,
        'Ir': 1.80, 'Pt': 1.75, 'Au': 1.66, 'Hg': 1.55, 'Tl': 1.96, 'Pb': 2.02, 'Bi': 2.07, 'Po': 1.97, 'At': 2.02, 'Rn': 2.20,
        'Fr': 3.48, 'Ra': 2.83, 'Ac': 2.60, 'Th': 2.60, 'U': 2.60, 'Np': 2.60, 'Pu': 2.60, 'X': 0.00  # Placeholder for unknown elements
    }

    # Creating a dictionary for empirical atomic radii from the provided data
    atomic_radii_empirical = {
        'H': 0.25, 'He': 1.2, 'Li': 1.45, 'Be': 1.05, 'B': 0.85, 'C': 0.7,
        'N': 0.65, 'O': 0.6, 'F': 0.5, 'Ne': 1.6, 'Na': 1.8, 'Mg': 1.5,
        'Al': 1.25, 'Si': 1.1, 'P': 1.0, 'S': 1.0, 'Cl': 1.0, 'Ar': 0.71,
        'K': 2.2, 'Ca': 1.8, 'Sc': 1.6, 'Ti': 1.4, 'V': 1.35, 'Cr': 1.4,
        'Mn': 1.4, 'Fe': 1.4, 'Co': 1.35, 'Ni': 1.35, 'Cu': 1.35, 'Zn': 1.35,
        'Ga': 1.3, 'Ge': 1.25, 'As': 1.15, 'Se': 1.15, 'Br': 1.15, 'Kr': None,  
        'Rb': 2.35, 'Sr': 2.0, 'Y': 1.8, 'Zr': 1.55, 'Nb': 1.45, 'Mo': 1.45,
        'Tc': 1.35, 'Ru': 1.3, 'Rh': 1.35, 'Pd': 1.4, 'Ag': 1.6, 'Cd': 1.55,
        'In': 1.55, 'Sn': 1.45, 'Sb': 1.45, 'Te': 1.4, 'I': 1.4, 'Xe': None,  
        'Cs': 2.6, 'Ba': 2.15, 'La': 1.95, 'Ce': 1.85, 'Pr': 1.85,
        'Nd': 1.85, 'Pm': 1.85, 'Sm': 1.85, 'Eu': 1.85, 'Gd': 1.8,
        'Tb': 1.75, 'Dy': 1.75, 'Ho': 1.75, 'Er': 1.75, 'Tm': 1.75,
        'Yb': 1.75, 'Lu': 1.75, 'Hf': 1.55, 'Ta': 1.45, 'W': 1.35,
        'Re': 1.35, 'Os': 1.3, 'Ir': 1.35, 'Pt': 1.35, 'Au': 1.35,
        'Hg': 1.5, 'Tl': 1.9, 'Pb': 1.8, 'Bi': 1.6, 'Po': 1.9,
        'At': None, 'Rn': None, 'Fr': None, 'Ra': 2.15, 'Ac': 1.95,
        'Th': 1.8, 'Pa': 1.8, 'U': 1.75, 'Np': 1.75, 'Pu': 1.75,
        'Am': 1.75, 'Cm': 1.76, 'Bk': None, 'Cf': None, 'Es': None,
        'Fm': None, 'Md': None, 'No': None, 'Lr': None, 'Rf': None,
        'Db': None, 'Sg': None, 'Bh': None, 'Hs': None, 'Mt': None,
        'Ds': None, 'Rg': None, 'Cn': None, 'Nh': None, 'Fl': None,
        'Mc': None, 'Lv': None, 'Ts': None, 'Og': None
        }
        
    atomic_radii = {
        'H': 0.53, 'He': 0.31, 'Li': 1.67, 'Be': 1.12, 'B': 0.87, 'C': 0.67, 'N': 0.56, 'O': 0.48, 'F': 0.42,
        'Ne': 0.38, 'Na': 1.90, 'Mg': 1.45, 'Al': 1.18, 'Si': 1.11, 'P': 0.98, 'S': 0.88, 'Cl': 0.79,
        'Ar': 0.71, 'K': 2.43, 'Ca': 1.94, 'Sc': 1.84, 'Ti': 1.76, 'V': 1.71, 'Cr': 1.66, 'Mn': 1.61,
        'Fe': 1.56, 'Co': 1.52, 'Ni': 1.49, 'Cu': 1.45, 'Zn': 1.42, 'Ga': 1.36, 'Ge': 1.25, 'As': 1.14,
        'Se': 1.03, 'Br': 0.94, 'Kr': 0.88, 'Rb': 2.65, 'Sr': 2.19, 'Y': 2.12, 'Zr': 2.06, 'Nb': 1.98,
        'Mo': 1.90, 'Tc': 1.83, 'Ru': 1.78, 'Rh': 1.73, 'Pd': 1.69, 'Ag': 1.65, 'Cd': 1.61, 'In': 1.56,
        'Sn': 1.45, 'Sb': 1.33, 'Te': 1.23, 'I': 1.15, 'Xe': 1.08, 'Cs': 2.98, 'Ba': 2.53, 'La': 1.95,
        'Ce': 1.85, 'Pr': 2.47, 'Nd': 2.06, 'Pm': 2.05, 'Sm': 2.38, 'Eu': 2.31, 'Gd': 2.33, 'Tb': 2.25,
        'Dy': 2.28, 'Ho': 2.26, 'Er': 2.26, 'Tm': 2.22, 'Yb': 2.22, 'Lu': 2.17, 'Hf': 2.08, 'Ta': 2.00,
        'W': 1.93, 'Re': 1.88, 'Os': 1.85, 'Ir': 1.80, 'Pt': 1.77, 'Au': 1.74, 'Hg': 1.70, 'Tl': 1.55,
        'Pb': 1.54, 'Bi': 1.43, 'Th': 1.79, 'Pa': 1.61, 'U': 1.58, 'Np': 1.55, 'Pu': 1.53, 'Am': 1.51,
        'Cm': 1.50, 'Bk': 1.50, 'Cf': 1.50, 'Es': 1.50, 'Fm': 1.50, 'Md': 1.50, 'No': 1.50, 'Lr': 1.50,
        'Rf': 1.50, 'Db': 1.50, 'Sg': 1.50, 'Bh': 1.50, 'Hs': 1.50, 'Mt': 1.50, 'Ds': 1.50, 'Rg': 1.50,
        'Cn': 1.50, 'Nh': 1.50, 'Fl': 1.50, 'Mc': 1.50, 'Lv': 1.50, 'Ts': 1.50, 'Og': 1.50
    }

    electronegativity = {
        'H': 2.2, 'He': None, 'Li': 1.0, 'Be': 1.5, 'B': 2.0, 'C': 2.5, 'N': 3.1, 'O': 3.5, 'F': 4.1, 'Ne': None, 'Na': 0.9,
        'Mg': 1.2, 'Al': 1.5, 'Si': 1.7, 'P': 2.1, 'S': 2.4, 'Cl': 2.8, 'Ar': None, 'K': 0.9, 'Ca': 1.0, 'Sc': 1.2, 'Ti': 1.3,
        'V': 1.3, 'Cr': 1.6, 'Mn': None, 'Fe': 1.6, 'Co': None, 'Ni': 1.5, 'Cu': 1.8, 'Zn': 1.4, 'Ga': 1.6, 'Ge': 1.8,
        'As': 2.0, 'Se': 2.4, 'Br': 2.7, 'Kr': None, 'Rb': 0.9, 'Sr': 1.0, 'Y': None, 'Zr': None, 'Nb': None, 'Mo': 1.3,
        'Tc': None, 'Ru': 1.4, 'Rh': 1.5, 'Pd': 1.4, 'Ag': 1.4, 'Cd': 1.4, 'In': 1.4, 'Sn': 1.4, 'Sb': 1.5, 'Te': 2.1,
        'I': 2.2, 'Xe': None, 'Cs': 0.7, 'Ba': 0.9, 'Lu': None, 'Hf': 1.3, 'Ta': 1.3, 'W': 1.3, 'Re': 1.6, 'Os': 1.6,
        'Ir': 1.6, 'Pt': 1.4, 'Au': 1.4, 'Hg': 1.9, 'Tl': 1.7, 'Pb': 1.5, 'Bi': 1.5, 'Po': 1.5, 'At': 2.2, 'Rn': None,
        'Fr': 0.7, 'Ra': 0.9, 'Ac': 1.0, 'Th': 1.1, 'U': 1.2, 'Np': 1.2, 'Pu': 1.3, 'X': None  # Placeholder for unknown elements
    }

    ionization_energy_data = {
        'H': 0.0135, 'He': 24.5874, 'Li': 5.3917, 'Be': 9.3227, 'B': 8.298, 'C': 11.2603, 'N': 14.5341, 'O': 13.6181,
        'F': 17.4228, 'Ne': 21.5645, 'Na': 5.1391, 'Mg': 7.6462, 'Al': 5.9858, 'Si': 8.1517, 'P': 10.4867, 'S': 10.3600,
        'Cl': 12.9676, 'Ar': 15.7596, 'K': 4.3407, 'Ca': 6.1132, 'Sc': 6.5615, 'Ti': 6.8281, 'V': 6.7462, 'Cr': 6.7665,
        'Mn': 7.4340, 'Fe': 7.9024, 'Co': 7.8810, 'Ni': 7.6398, 'Cu': 7.7264, 'Zn': 9.3942, 'Ga': 5.9993, 'Ge': 7.8994,
        'As': 9.7886, 'Se': 9.7524, 'Br': 11.8138, 'Kr': 13.9996, 'Rb': 4.1771, 'Sr': 5.6949, 'Y': 6.2173, 'Zr': 6.6339,
        'Nb': 6.7589, 'Mo': 7.0924, 'Tc': 7.28, 'Ru': 7.3605, 'Rh': 7.4589, 'Pd': 8.3369, 'Ag': 7.5762, 'Cd': 8.9938,
        'In': 5.7864, 'Sn': 7.3439, 'Sb': 8.6084, 'Te': 9.0096, 'I': 10.4513, 'Xe': 12.1298, 'Cs': 3.8939, 'Ba': 5.2117,
        'Lu': 5.4259, 'Hf': 6.8251, 'Ta': 7.5496, 'W': 7.8640, 'Re': 7.8335, 'Os': 8.4382, 'Ir': 8.967, 'Pt': 9.131,
        'Au': 9.2255, 'Hg': 10.4375, 'Tl': 6.1082, 'Pb': 7.4167, 'Bi': 7.2855, 'Po': 8.414, 'At': 9.3, 'Rn': 10.7485,
        'Fr': 4.0727, 'Ra': 5.2784, 'Ac': 5.17, 'Th': 6.3067, 'U': 6.1941, 'Np': 6.2657, 'Pu': 6.0262
    }

    common_oxidation_states_data = {
        'H': (1, -1), 'He': (), 'Li': (1,), 'Be': (2,), 'B': (3,), 'C': (4,), 'N': (-3, 3, 5), 'O': (-2,), 'F': (-1,),
        'Ne': (), 'Na': (1,), 'Mg': (2,), 'Al': (3,), 'Si': (4,), 'P': (-3, 3, 5), 'S': (-2, 2, 4, 6), 'Cl': (-1, 1, 3, 5, 7),
        'Ar': (), 'K': (1,), 'Ca': (2,), 'Sc': (3,), 'Ti': (4,), 'V': (2, 3, 4, 5), 'Cr': (-1, 1, 2, 3, 4, 5, 6),
        'Mn': (-2, -1, 1, 2, 3, 4, 5, 6, 7), 'Fe': (-2, -1, 1, 2, 3, 4, 5, 6), 'Co': (-1, 1, 2, 3, 4), 'Ni': (-2, 1, 2, 3, 4),
        'Cu': (1, 2), 'Zn': (2,), 'Ga': (1, 2, 3), 'Ge': (-4, 1, 2, 3, 4), 'As': (-3, 2, 3, 5), 'Se': (-2, 2, 4, 6),
        'Br': (-1, 1, 3, 4, 5, 7), 'Kr': (), 'Rb': (1,), 'Sr': (2,), 'Y': (3,), 'Zr': (4,), 'Nb': (5,), 'Mo': (2, 3, 4, 5, 6),
        'Tc': (7,), 'Ru': (2, 3, 4, 5, 6, 7, 8), 'Rh': (1, 2, 3, 4, 5, 6), 'Pd': (2, 4), 'Ag': (1,), 'Cd': (2,), 'In': (1, 2, 3),
        'Sn': (-4, 2, 4), 'Sb': (-3, 3, 5), 'Te': (-2, 2, 4, 6), 'I': (-1, 1, 3, 5, 7), 'Xe': (2, 4, 6, 8), 'Cs': (1,),
        'Ba': (2,), 'Lu': (3,), 'Hf': (4,), 'Ta': (5,), 'W': (2, 4, 6), 'Re': (-3, 1, 2, 3, 4, 5, 6, 7), 'Os': (2, 4, 6, 8),
        'Ir': (1, 2, 3, 4, 6), 'Pt': (2, 4, 6), 'Au': (1, 3), 'Hg': (1, 2), 'Tl': (1, 3), 'Pb': (-4, 2, 4), 'Bi': (-3, 3, 5),
        'Po': (-2, 2, 4, 6), 'At': (-1, 1, 3, 5, 7), 'Rn': (2, 4, 6), 'Fr': (1,), 'Ra': (2,), 'Ac': (3,), 'Th': (4, 3),
        'U': (6, 4, 3), 'Np': (6, 5, 4, 3), 'Pu': (6, 5, 4)
                                        }   

    crystal_structure_data = {
        'H': 'hexagonal', 'He': 'hexagonal', 'Li': 'cubic', 'Be': 'hexagonal', 'B': 'rhombohedral', 'C': 'hexagonal',
        'N': 'hexagonal', 'O': 'cubic', 'F': 'cubic', 'Ne': 'face-centered cubic', 'Na': 'body-centered cubic',
        'Mg': 'hexagonal', 'Al': 'face-centered cubic', 'Si': 'diamond cubic', 'P': 'simple cubic', 'S': 'orthorhombic',
        'Cl': 'orthorhombic', 'Ar': 'face-centered cubic', 'K': 'body-centered cubic', 'Ca': 'face-centered cubic',
        'Sc': 'hexagonal', 'Ti': 'hexagonal', 'V': 'body-centered cubic', 'Cr': 'body-centered cubic', 'Mn': 'cubic',
        'Fe': 'body-centered cubic', 'Co': 'hexagonal', 'Ni': 'cubic', 'Cu': 'face-centered cubic', 'Zn': 'hexagonal',
        'Ga': 'orthorhombic', 'Ge': 'diamond cubic', 'As': 'rhombohedral', 'Se': 'hexagonal', 'Br': 'orthorhombic',
        'Kr': 'face-centered cubic', 'Rb': 'body-centered cubic', 'Sr': 'face-centered cubic', 'Y': 'hexagonal',
        'Zr': 'hexagonal', 'Nb': 'cubic', 'Mo': 'body-centered cubic', 'Tc': 'hexagonal', 'Ru': 'hexagonal',
        'Rh': 'face-centered cubic', 'Pd': 'cubic', 'Ag': 'face-centered cubic', 'Cd': 'hexagonal', 'In': 'tetragonal',
        'Sn': 'tetragonal', 'Sb': 'rhombohedral', 'Te': 'hexagonal', 'I': 'orthorhombic', 'Xe': 'face-centered cubic',
        'Cs': 'body-centered cubic', 'Ba': 'body-centered cubic', 'Lu': 'hexagonal', 'Hf': 'hexagonal', 'Ta': 'body-centered cubic',
        'W': 'body-centered cubic', 'Re': 'hexagonal', 'Os': 'hexagonal', 'Ir': 'face-centered cubic', 'Pt': 'cubic',
        'Au': 'face-centered cubic', 'Hg': 'rhombohedral', 'Tl': 'hexagonal', 'Pb': 'face-centered cubic', 'Bi': 'rhombohedral',
        'Po': 'rhombohedral', 'At': 'orthorhombic', 'Rn': 'face-centered cubic', 'Fr': 'body-centered cubic', 'Ra': 'body-centered cubic',
        'Ac': 'face-centered cubic', 'Th': 'face-centered cubic', 'U': 'orthorhombic', 'Np': 'orthorhombic', 'Pu': 'monoclinic'
    }

    compounds_of_elements = {
        'H': ['H2O', 'H2', 'NH3', 'CH4', 'HCl'],
        'He': ['He'],
        'Li': ['Li2O', 'LiCl', 'LiOH'],
        'Be': ['BeO', 'BeCl2'],
        'B': ['BF3', 'B2H6'],
        'C': ['CO2', 'CH4', 'C2H2'],
        'N': ['N2', 'NH3', 'NO2'],
        'O': ['O2', 'H2O', 'CO2', 'O3'],
        'F': ['F2', 'HF', 'CF4'],
        'Ne': ['Ne'],
        'Na': ['NaCl', 'NaOH', 'Na2O'],
        'Mg': ['MgO', 'MgCl2', 'MgSO4'],
        'Al': ['Al2O3', 'AlCl3'],
        'Si': ['SiO2', 'SiCl4'],
        'P': ['P4', 'PH3', 'P2O5'],
        'S': ['S8', 'H2S', 'SO2'],
        'Cl': ['Cl2', 'HCl'],
        'K': ['KCl', 'K2O', 'KO2'],
        'Ar': ['Ar'],
        'Ca': ['CaO', 'CaCl2', 'CaCO3'],
        'Ti': ['TiO2', 'TiCl4'],
        'Fe': ['Fe2O3', 'FeCl3'],
         'V': ['VO2', 'V2O5'],
        'Cr': ['Cr2O3', 'CrCl3'],
        'Mn': ['MnO2', 'MnSO4'],
        'Co': ['CoO', 'CoCl2'],
        'Ni': ['NiO', 'NiCl2'],
        'Cu': ['Cu2O', 'CuSO4'],
        'Zn': ['ZnO', 'ZnSO4'],
        'Ga': ['GaAs', 'GaCl3'],
        'Ge': ['GeO2', 'GeCl4'],
        'As': ['As2O3', 'AsCl3'],
        'Se': ['SeO2', 'H2Se'],
        'Br': ['Br2', 'HBr'],
        'Kr': ['Kr'],
        'Rb': ['RbCl', 'Rb2O'],
        'Sr': ['SrO', 'SrCl2'],
        'Y': ['Y2O3', 'YCl3'],
        'Zr': ['ZrO2', 'ZrCl4'],
        'Nb': ['Nb2O5', 'NbCl5'],
        'Mo': ['MoO3', 'MoS2'],
        'Tc': ['TcO4-'],
        'Ru': ['RuO2', 'RuCl3'],
        'Rh': ['RhCl3', 'Rhodium compounds'],
        'Pd': ['PdO', 'PdCl2'],
        'Ag': ['Ag2O', 'AgNO3'],
        'Cd': ['CdO', 'CdCl2'],
        'In': ['In2O3', 'InCl3'],
        'Sn': ['SnO2', 'SnCl2'],
        'Sb': ['Sb2O3', 'SbCl3'],
        'Te': ['TeO2', 'H2Te'],
        'I': ['I2', 'HI'],
        'Xe': ['Xe'],
        'Cs': ['CsCl', 'Cs2O'],
        'Ba': ['BaO', 'BaCl2'],
        'Lu': ['Lu2O3', 'LuCl3'],
        'Hf': ['HfO2', 'HfCl4'],
        'Ta': ['Ta2O5', 'TaCl5'],
        'W': ['WO3', 'WCl6'],
        'Re': ['ReO3', 'ReCl6'],
        'Os': ['OsO4', 'OsCl6'],
        'Ir': ['IrO2', 'IrCl3'],
        'Pt': ['PtO2', 'PtCl2'],
        'Au': ['AuCl3', 'Gold compounds'],
        'Hg': ['HgO', 'HgCl2'],
        'Tl': ['Tl2O3', 'TlCl3'],
        'Pb': ['PbO2', 'PbCl2'],
        'Bi': ['Bi2O3', 'BiCl3'],
        'Po': ['PoO2', 'PoCl2'],
        'At': ['At2O', 'AtCl'],
        'Rn': ['Rn'],
        'Fr': ['FrCl', 'Fr2O'],
        'Ra': ['RaO', 'RaCl2'],
        'Ac': ['Ac2O3', 'AcCl3'],
        'Th': ['ThO2', 'ThCl4'],
        'U': ['UO2', 'UCl4'],
        'Np': ['NpO2', 'NpCl4'],
        'Pu': ['PuO2', 'PuCl3'],
        'X': ['X-compounds'],
        }

    atomic_id = [ 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 
                        'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 
                        'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 
                        'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
                        'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 
                        'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 
                        'Lv', 'Ts', 'Og']

    valence_orbitals = {
        'H' : ['1s'],                       'He': ['1s'],                   'Li': ['2s', '2p'],              'Be': ['2s', '2p'],
        'B' : ['2s', '2p'],                 'C' : ['2s', '2p'],             'N' : ['2s', '2p'],              'O' : ['2s', '2p'],
        'F' : ['2s', '2p'],                 'Ne': ['2s', '2p'],             'Na': ['3s', '3p'],              'Mg': ['3s', '3p'],
        'Al': ['3s', '3p', '3d'],           'Si': ['3s', '3p', '3d'],       'P' : ['3s', '3p', '3d'],        'S' : ['3s', '3p', '3d'],
        'Cl': ['3s', '3p', '3d'],           'Ar': ['3s', '3p', '3d'],       'K' : ['3d', '4s', '4p'],        'Ca': ['3d', '4s', '4p'],
        'Sc': ['3d', '4s', '4p'],           'Ti': ['3d', '4s', '4p'],       'V' : ['3d', '4s', '4p'],        'Cr': ['3d', '4s', '4p'],
        'Mn': ['3d', '4s', '4p'],           'Fe': ['3d', '4s', '4p'],       'Co': ['3d', '4s', '4p'],        'Ni': ['3d', '4s', '4p'],
        'Cu': ['3d', '4s', '4p'],           'Zn': ['3d', '4s', '4p'],       'Ga': ['3d', '4s', '4p'],        'Ge': ['3d', '4s', '4p'],
        'As': ['3d', '4s', '4p'],           'Se': ['3d', '4s', '4p'],       'Br': ['3d', '4s', '4p'],        'Kr': ['3d', '4s', '4p'],
        'Rb': ['4d', '5s', '5p'],           'Sr': ['4d', '5s', '5p'],       'Y' : ['4d', '5s', '5p'],        'Zr': ['4d', '5s', '5p'],
        'Nb': ['4d', '5s', '5p'],           'Mo': ['4d', '5s', '5p'],       'Tc': ['4d', '5s', '5p'],        'Ru': ['4d', '5s', '5p'],
        'Rh': ['4d', '5s', '5p'],           'Pd': ['4d', '5s', '5p'],       'Ag': ['4d', '5s', '5p'],        'Cd': ['4d', '5s', '5p'],
        'In': ['4d', '5s', '5p'],           'Sn': ['4d', '5s', '5p'],       'Sb': ['4d', '5s', '5p'],        'Te': ['4d', '5s', '5p'],
        'I' : ['4d', '5s', '5p'],           'Xe': ['4d', '5s', '5p'],       'Cs': ['5d', '6s', '5p'],        'Ba': ['5d', '6s', '5p'],
        'Lu': ['5d', '6s', '6p'],           'Hf': ['5d', '6s', '6p'],       'Ta': ['5d', '6s', '6p'],        'W' : ['5d', '6s', '6p'],
        'Re': ['5d', '6s', '6p'],           'Os': ['5d', '6s', '6p'],       'Ir': ['5d', '6s', '6p'],        'Pt': ['5d', '6s', '6p'],
        'Au': ['5d', '6s', '6p'],           'Hg': ['5d', '6s', '6p'],       'Tl': ['5d', '6s', '6p'],        'Pb': ['5d', '6s', '6p'],
        'Bi': ['5d', '6s', '6p'],           'Po': ['5d', '6s', '6p'],       'At': ['5d', '6s', '6p'],        'Rn': ['5d', '6s', '6p'],
        'Fr': ['6d', '7s', '7p'],           'Ra': ['6d', '7s', '7p'],       'Ac': ['5f', '6d', '7s', '7p'],  'Th': ['5f', '6d', '7s', '7p'],
        'U' : ['5f', '6d', '7s', '7p'],     'Np': ['5f', '6d', '7s', '7p'], 'Pu': ['5f', '6d', '7s', '7p']
    }

    element_data = {
            'H': {'core': '', 'valence': {'1s': 1}},
            'He': {'core': '', 'valence': {'1s': 2}},
            'Li': {'core': 'He', 'valence': {'2s': 1, '2p': 0}},
            'Be': {'core': 'He', 'valence': {'2s': 2, '2p': 0}},
            'B': {'core': 'He', 'valence': {'2s': 2, '2p': 1}},
            'C': {'core': 'He', 'valence': {'2s': 2, '2p': 2}},
            'N': {'core': 'He', 'valence': {'2s': 2, '2p': 3}},
            'O': {'core': 'He', 'valence': {'2s': 2, '2p': 4}},
            'F': {'core': 'He', 'valence': {'2s': 2, '2p': 5}},
            'Ne': {'core': 'He', 'valence': {'2s': 2, '2p': 6}},
            'Na': {'core': 'Ne', 'valence': {'3s': 1, '3p': 0}},
            'Mg': {'core': 'Ne', 'valence': {'3s': 2, '3p': 0}},
            'Al': {'core': 'Ne', 'valence': {'3s': 2, '3p': 1, '3d': 0}},
            'Si': {'core': 'Ne', 'valence': {'3s': 2, '3p': 2, '3d': 0}},
            'P': {'core': 'Ne', 'valence': {'3s': 2, '3p': 3, '3d': 0}},
            'S': {'core': 'Ne', 'valence': {'3s': 2, '3p': 4, '3d': 0}},
            'Cl': {'core': 'Ne', 'valence': {'3s': 2, '3p': 5, '3d': 0}},
            'Ar': {'core': 'Ne', 'valence': {'3s': 2, '3p': 6, '3d': 0}},
            'K': {'core': 'Ar', 'valence': {'3d': 0, '4s': 1, '4p': 0}},
            'Ca': {'core': 'Ar', 'valence': {'3d': 0, '4s': 2, '4p': 0}},
            'Sc': {'core': 'Ar', 'valence': {'3d': 1, '4s': 2, '4p': 0}},
            'Ti': {'core': 'Ar', 'valence': {'3d': 2, '4s': 2, '4p': 0}},
            'V': {'core': 'Ar', 'valence': {'3d': 3, '4s': 2, '4p': 0}},
            'Cr': {'core': 'Ar', 'valence': {'3d': 5, '4s': 1, '4p': 0}},
            'Mn': {'core': 'Ar', 'valence': {'3d': 5, '4s': 2, '4p': 0}},
            'Fe': {'core': 'Ar', 'valence': {'3d': 6, '4s': 2, '4p': 0}},
            'Co': {'core': 'Ar', 'valence': {'3d': 7, '4s': 2, '4p': 0}},
            'Ni': {'core': 'Ar', 'valence': {'3d': 8, '4s': 2, '4p': 0}},
            'Cu': {'core': 'Ar', 'valence': {'3d': 10, '4s': 1, '4p': 0}},
            'Zn': {'core': 'Ar', 'valence': {'3d': 10, '4s': 2, '4p': 0}},
            'Ga': {'core': 'Ar', 'valence': {'3d': 10, '4s': 2, '4p': 1}},
            'Ge': {'core': 'Ar', 'valence': {'3d': 10, '4s': 2, '4p': 2}},
            'As': {'core': 'Ar', 'valence': {'3d': 10, '4s': 2, '4p': 3}},
            'Se': {'core': 'Ar', 'valence': {'3d': 10, '4s': 2, '4p': 4}},
            'Br': {'core': 'Ar', 'valence': {'3d': 10, '4s': 2, '4p': 5}},
            'Kr': {'core': 'Ar', 'valence': {'3d': 10, '4s': 2, '4p': 6}},
            'Rb': {'core': 'Kr', 'valence': {'4d': 0, '5s': 1, '5p': 0}},
            'Sr': {'core': 'Kr', 'valence': {'4d': 0, '5s': 2, '5p': 0}},
            'Y': {'core': 'Kr', 'valence': {'4d': 1, '5s': 2, '5p': 0}},
            'Zr': {'core': 'Kr', 'valence': {'4d': 2, '5s': 2, '5p': 0}},
            'Nb': {'core': 'Kr', 'valence': {'4d': 4, '5s': 1, '5p': 0}},
            'Mo': {'core': 'Kr', 'valence': {'4d': 5, '5s': 1, '5p': 0}},
            'Tc': {'core': 'Kr', 'valence': {'4d': 5, '5s': 2, '5p': 0}},
            'Ru': {'core': 'Kr', 'valence': {'4d': 7, '5s': 1, '5p': 0}},
            'Rh': {'core': 'Kr', 'valence': {'4d': 8, '5s': 1, '5p': 0}},
            'Pd': {'core': 'Kr', 'valence': {'4d': 10, '5s': 0, '5p': 0}},
            'Ag': {'core': 'Kr', 'valence': {'4d': 10, '5s': 1, '5p': 0}},
            'Cd': {'core': 'Kr', 'valence': {'4d': 10, '5s': 2, '5p': 0}},
            'In': {'core': 'Kr', 'valence': {'4d': 10, '5s': 2, '5p': 1}},
            'Sn': {'core': 'Kr', 'valence': {'4d': 10, '5s': 2, '5p': 2}},
            'Sb': {'core': 'Kr', 'valence': {'4d': 10, '5s': 2, '5p': 3}},
            'Te': {'core': 'Kr', 'valence': {'4d': 10, '5s': 2, '5p': 4}},
            'I': {'core': 'Kr', 'valence': {'4d': 10, '5s': 2, '5p': 5}},
            'Xe': {'core': 'Kr', 'valence': {'4d': 10, '5s': 2, '5p': 6}},
            'Cs': {'core': 'Xe', 'valence': {'5d': 0, '6s': 1, '6p': 0}},
            'Ba': {'core': 'Xe', 'valence': {'5d': 0, '6s': 2, '6p': 0}},
            'Lu': {'core': 'Xe', 'valence': {'4f': 14, '5d': 1, '6s': 2, '6p': 0}},
            'Hf': {'core': 'Xe', 'valence': {'4f': 14, '5d': 2, '6s': 2, '6p': 0}},
            'Ta': {'core': 'Xe', 'valence': {'4f': 14, '5d': 3, '6s': 2, '6p': 0}},
            'W': {'core': 'Xe', 'valence': {'4f': 14, '5d': 4, '6s': 2, '6p': 0}},
            'Re': {'core': 'Xe', 'valence': {'4f': 14, '5d': 5, '6s': 2, '6p': 0}},
            'Os': {'core': 'Xe', 'valence': {'4f': 14, '5d': 6, '6s': 2, '6p': 0}},
            'Ir': {'core': 'Xe', 'valence': {'4f': 14, '5d': 7, '6s': 2, '6p': 0}},
            'Pt': {'core': 'Xe', 'valence': {'4f': 14, '5d': 9, '6s': 1, '6p': 0}},
            'Au': {'core': 'Xe', 'valence': {'4f': 14, '5d': 10, '6s': 1, '6p': 0}},
            'Hg': {'core': 'Xe', 'valence': {'4f': 14, '5d': 10, '6s': 2, '6p': 0}},
            'Tl': {'core': 'Xe', 'valence': {'4f': 14, '5d': 10, '6s': 2, '6p': 1}},
            'Pb': {'core': 'Xe', 'valence': {'4f': 14, '5d': 10, '6s': 2, '6p': 2}},
            'Bi': {'core': 'Xe', 'valence': {'4f': 14, '5d': 10, '6s': 2, '6p': 3}},
            'Po': {'core': 'Xe', 'valence': {'4f': 14, '5d': 10, '6s': 2, '6p': 4}},
            'At': {'core': 'Xe', 'valence': {'4f': 14, '5d': 10, '6s': 2, '6p': 5}},
            'Rn': {'core': 'Xe', 'valence': {'4f': 14, '5d': 10, '6s': 2, '6p': 6}},
            'Fr': {'core': 'Rn', 'valence': {'6d': 0, '7s': 1, '7p': 0}},
            'Ra': {'core': 'Rn', 'valence': {'6d': 0, '7s': 2, '7p': 0}},
            'Ac': {'core': 'Rn', 'valence': {'5f': 0, '6d': 1, '7s': 2, '7p': 0}},
            'Th': {'core': 'Rn', 'valence': {'5f': 0, '6d': 2, '7s': 2, '7p': 0}},
            'U': {'core': 'Rn', 'valence': {'5f': 3, '6d': 1, '7s': 2, '7p': 0}},
            'Np': {'core': 'Rn', 'valence': {'5f': 4, '6d': 1, '7s': 2, '7p': 0}},
            'Pu': {'core': 'Rn', 'valence': {'5f': 6, '6d': 0, '7s': 2, '7p': 0}},
            }

    ####################################################
    ##### DFTB Part 1 parameters for free atoms ########
    ####################################################
    ## from M. Wahiduzzaman, et al. J. Chem. Theory Comput. 9, 4006-4017 (2013)
    ## (1) optimal confinement parameters (optimized for band structures of homonuclear crystals)
    ##     general form V_conf = (r/r0)**s, r0 in Bohr
    ## (2) shell resolved U-parameters (as obtained from PBE-DFT calculations)
    ##     using U parameter of occupied shell with highest l for unoccupied shells
    ## (3) Orbital energies for the neutral atoms

    PARAMETERS_QUASINANO = {
        'H':  {'dens_confinement': {'r0': 1.6,  's': 2.2 }, 'U': {'d': 0.419731, 'p': 0.419731, 's': 0.419731}, 'E': {'s': -0.238603}},
        'He': {'dens_confinement': {'r0': 1.4,  's': 11.4}, 'U': {'d': 0.742961, 'p': 0.742961, 's': 0.742961}, 'E': {'s': -0.579318}},
        'Li': {'dens_confinement': {'r0': 5.0,  's': 8.2 }, 'U': {'d': 0.131681, 'p': 0.131681, 's': 0.174131}, 'E': {'p': -0.040054, 's': -0.105624}},
        'Be': {'dens_confinement': {'r0': 3.4,  's': 13.2}, 'U': {'d': 0.224651, 'p': 0.224651, 's': 0.270796}, 'E': {'p': -0.074172, 's': -0.206152}},
        'B':  {'dens_confinement': {'r0': 3.0,  's': 10.4}, 'U': {'d': 0.296157, 'p': 0.296157, 's': 0.333879}, 'E': {'p': -0.132547, 's': -0.347026}},
        'C':  {'dens_confinement': {'r0': 3.2,  's': 8.2 }, 'U': {'d': 0.364696, 'p': 0.364696, 's': 0.399218}, 'E': {'p': -0.194236, 's': -0.505337}},
        'N':  {'dens_confinement': {'r0': 3.4,  's': 13.4}, 'U': {'d': 0.430903, 'p': 0.430903, 's': 0.464356}, 'E': {'p': -0.260544, 's': -0.682915}},
        'O':  {'dens_confinement': {'r0': 3.1,  's': 12.4}, 'U': {'d': 0.495405, 'p': 0.495405, 's': 0.528922}, 'E': {'p': -0.331865, 's': -0.880592}},
        'F':  {'dens_confinement': {'r0': 2.7,  's': 10.6}, 'U': {'d': 0.558631, 'p': 0.558631, 's': 0.592918}, 'E': {'p': -0.408337, 's': -1.098828}},
        'Ne': {'dens_confinement': {'r0': 3.2,  's': 15.4}, 'U': {'d': 0.620878, 'p': 0.620878, 's': 0.656414}, 'E': {'p': -0.490009, 's': -1.337930}},
        'Na': {'dens_confinement': {'r0': 5.9,  's': 12.6}, 'U': {'d': 0.087777, 'p': 0.087777, 's': 0.165505}, 'E': {'p': -0.027320, 's': -0.100836}},
        'Mg': {'dens_confinement': {'r0': 5.0,  's': 6.2 }, 'U': {'d': 0.150727, 'p': 0.150727, 's': 0.224983}, 'E': {'p': -0.048877, 's': -0.172918}},
        'Al': {'dens_confinement': {'r0': 5.9,  's': 12.4}, 'U': {'d': 0.186573, 'p': 0.203216, 's': 0.261285}, 'E': {'d': 0.116761, 'p': -0.099666, 's': -0.284903}},
        'Si': {'dens_confinement': {'r0': 4.4,  's': 12.8}, 'U': {'d': 0.196667, 'p': 0.247841, 's': 0.300005}, 'E': {'d': 0.113134, 'p': -0.149976, 's': -0.397349}},
        'P':  {'dens_confinement': {'r0': 4.0,  's': 9.6 }, 'U': {'d': 0.206304, 'p': 0.289262, 's': 0.338175}, 'E': {'d': 0.121111, 'p': -0.202363, 's': -0.513346}},
        'S':  {'dens_confinement': {'r0': 3.9,  's': 4.6 }, 'U': {'d': 0.212922, 'p': 0.328724, 's': 0.37561 }, 'E': {'d': 0.134677, 'p': -0.257553, 's': -0.634144}},
        'Cl': {'dens_confinement': {'r0': 3.8,  's': 9.0 }, 'U': {'d': 0.214242, 'p': 0.366885, 's': 0.412418}, 'E': {'d': 0.150683, 'p': -0.315848, 's': -0.760399}},
        'Ar': {'dens_confinement': {'r0': 4.5,  's': 15.2}, 'U': {'d': 0.207908, 'p': 0.404106, 's': 0.448703}, 'E': {'d': 0.167583, 'p': -0.377389, 's': -0.892514}},
        'K':  {'dens_confinement': {'r0': 6.5,  's': 15.8}, 'U': {'d': 0.171297, 'p': 0.081938, 's': 0.136368}, 'E': {'d': 0.030121, 'p': -0.029573, 's': -0.085219}},
        'Ca': {'dens_confinement': {'r0': 4.9,  's': 13.6}, 'U': {'d': 0.299447, 'p': 0.128252, 's': 0.177196}, 'E': {'d': -0.070887, 'p': -0.051543, 's': -0.138404}},
        'Sc': {'dens_confinement': {'r0': 5.1,  's': 13.6}, 'U': {'d': 0.32261,  'p': 0.137969, 's': 0.189558}, 'E': {'d': -0.118911, 'p': -0.053913, 's': -0.153708}},
        'Ti': {'dens_confinement': {'r0': 4.2,  's': 12.0}, 'U': {'d': 0.351019, 'p': 0.144515, 's': 0.201341}, 'E': {'d': -0.156603, 'p': -0.053877, 's': -0.164133}},
        'V':  {'dens_confinement': {'r0': 4.3,  's': 13.0}, 'U': {'d': 0.376535, 'p': 0.149029, 's': 0.211913}, 'E': {'d': -0.189894, 'p': -0.053055, 's': -0.172774}},
        'Cr': {'dens_confinement': {'r0': 4.7,  's': 3.6 }, 'U': {'d': 0.31219,  'p': 0.123012, 's': 0.200284}, 'E': {'d': -0.107113, 'p': -0.036319, 's': -0.147221}},
        'Mn': {'dens_confinement': {'r0': 3.6,  's': 11.6}, 'U': {'d': 0.422038, 'p': 0.155087, 's': 0.23074 }, 'E': {'d': -0.248949, 'p': -0.050354, 's': -0.187649}},
        'Fe': {'dens_confinement': {'r0': 3.7,  's': 11.2}, 'U': {'d': 0.442914, 'p': 0.156593, 's': 0.239398}, 'E': {'d': -0.275927, 'p': -0.048699, 's': -0.194440}},
        'Co': {'dens_confinement': {'r0': 3.3,  's': 11.0}, 'U': {'d': 0.462884, 'p': 0.157219, 's': 0.24771 }, 'E': {'d': -0.301635, 'p': -0.046909, 's': -0.200975}},
        'Ni': {'dens_confinement': {'r0': 3.7,  's': 2.2 }, 'U': {'d': 0.401436, 'p': 0.10618,  's': 0.235429}, 'E': {'d': -0.170792, 'p': -0.027659, 's': -0.165046}},
        'Cu': {'dens_confinement': {'r0': 5.2,  's': 2.2 }, 'U': {'d': 0.42067,  'p': 0.097312, 's': 0.243169}, 'E': {'d': -0.185263, 'p': -0.025621, 's': -0.169347}},
        'Zn': {'dens_confinement': {'r0': 4.6,  's': 2.2 }, 'U': {'d': 0.518772, 'p': 0.153852, 's': 0.271212}, 'E': {'d': -0.372826, 'p': -0.040997, 's': -0.219658}},
        'Ga': {'dens_confinement': {'r0': 5.9,  's': 8.8 }, 'U': {'d': 0.051561, 'p': 0.205025, 's': 0.279898}, 'E': {'d': 0.043096, 'p': -0.094773, 's': -0.328789}},
        'Ge': {'dens_confinement': {'r0': 4.5,  's': 13.4}, 'U': {'d': 0.101337, 'p': 0.240251, 's': 0.304342}, 'E': {'d': 0.062123, 'p': -0.143136, 's': -0.431044}},
        'As': {'dens_confinement': {'r0': 4.4,  's': 5.6 }, 'U': {'d': 0.127856, 'p': 0.271613, 's': 0.330013}, 'E': {'d': 0.078654, 'p': -0.190887, 's': -0.532564}},
        'Se': {'dens_confinement': {'r0': 4.5,  's': 3.8 }, 'U': {'d': 0.165858, 'p': 0.300507, 's': 0.355433}, 'E': {'d': 0.104896, 'p': -0.239256, 's': -0.635202}},
        'Br': {'dens_confinement': {'r0': 4.3,  's': 6.4 }, 'U': {'d': 0.189059, 'p': 0.327745, 's': 0.380376}, 'E': {'d': 0.126121, 'p': -0.288792, 's': -0.739820}},
        'Kr': {'dens_confinement': {'r0': 4.8,  's': 15.6}, 'U': {'d': 0.200972, 'p': 0.353804, 's': 0.404852}, 'E': {'d': 0.140945, 'p': -0.339778, 's': -0.846921}},
        'Rb': {'dens_confinement': {'r0': 9.1,  's': 16.8}, 'U': {'d': 0.180808, 'p': 0.07366,  's': 0.130512}, 'E': {'d': 0.030672, 'p': -0.027523, 's': -0.081999}},
        'Sr': {'dens_confinement': {'r0': 6.9,  's': 14.8}, 'U': {'d': 0.234583, 'p': 0.115222, 's': 0.164724}, 'E': {'d': -0.041363, 'p': -0.047197, 's': -0.129570}},
        'Y':  {'dens_confinement': {'r0': 5.7,  's': 13.6}, 'U': {'d': 0.239393, 'p': 0.127903, 's': 0.176814}, 'E': {'d': -0.092562, 'p': -0.052925, 's': -0.150723}},
        'Zr': {'dens_confinement': {'r0': 5.2,  's': 14.0}, 'U': {'d': 0.269067, 'p': 0.136205, 's': 0.189428}, 'E': {'d': -0.132380, 'p': -0.053976, 's': -0.163093}},
        'Nb': {'dens_confinement': {'r0': 5.2,  's': 15.0}, 'U': {'d': 0.294607, 'p': 0.141661, 's': 0.20028 }, 'E': {'d': -0.170468, 'p': -0.053629, 's': -0.172061}},
        'Mo': {'dens_confinement': {'r0': 4.3,  's': 11.6}, 'U': {'d': 0.317562, 'p': 0.145599, 's': 0.209759}, 'E': {'d': -0.207857, 'p': -0.052675, 's': -0.179215}},
        'Tc': {'dens_confinement': {'r0': 4.1,  's': 12.0}, 'U': {'d': 0.338742, 'p': 0.148561, 's': 0.218221}, 'E': {'d': -0.244973, 'p': -0.051408, 's': -0.185260}},
        'Ru': {'dens_confinement': {'r0': 4.1,  's': 3.8 }, 'U': {'d': 0.329726, 'p': 0.117901, 's': 0.212289}, 'E': {'d': -0.191289, 'p': -0.033507, 's': -0.155713}},
        'Rh': {'dens_confinement': {'r0': 4.0,  's': 3.4 }, 'U': {'d': 0.350167, 'p': 0.113146, 's': 0.219321}, 'E': {'d': -0.218418, 'p': -0.031248, 's': -0.157939}},
        'Pd': {'dens_confinement': {'r0': 4.4,  's': 2.8 }, 'U': {'d': 0.369605, 'p': 0.107666, 's': 0.225725}, 'E': {'d': -0.245882, 'p': -0.029100, 's': -0.159936}},
        'Ag': {'dens_confinement': {'r0': 6.5,  's': 2.0 }, 'U': {'d': 0.388238, 'p': 0.099994, 's': 0.231628}, 'E': {'d': -0.273681, 'p': -0.027061, 's': -0.161777}},
        'Cd': {'dens_confinement': {'r0': 5.4,  's': 2.0 }, 'U': {'d': 0.430023, 'p': 0.150506, 's': 0.251776}, 'E': {'d': -0.431379, 'p': -0.043481, 's': -0.207892}},
        'In': {'dens_confinement': {'r0': 4.8,  's': 13.2}, 'U': {'d': 0.156519, 'p': 0.189913, 's': 0.257192}, 'E': {'d': 0.135383, 'p': -0.092539, 's': -0.301650}},
        'Sn': {'dens_confinement': {'r0': 4.7,  's': 13.4}, 'U': {'d': 0.171708, 'p': 0.217398, 's': 0.275163}, 'E': {'d': 0.125834, 'p': -0.135732, 's': -0.387547}},
        'Sb': {'dens_confinement': {'r0': 5.2,  's': 3.0 }, 'U': {'d': 0.184848, 'p': 0.241589, 's': 0.294185}, 'E': {'d': 0.118556, 'p': -0.177383, 's': -0.471377}},
        'Te': {'dens_confinement': {'r0': 5.2,  's': 3.0 }, 'U': {'d': 0.195946, 'p': 0.263623, 's': 0.313028}, 'E': {'d': 0.114419, 'p': -0.218721, 's': -0.555062}},
        'I':  {'dens_confinement': {'r0': 6.2,  's': 2.0 }, 'U': {'d': 0.206534, 'p': 0.284168, 's': 0.33146 }, 'E': {'d': 0.112860, 'p': -0.260330, 's': -0.639523}},
        'Xe': {'dens_confinement': {'r0': 5.2,  's': 16.2}, 'U': {'d': 0.211949, 'p': 0.303641, 's': 0.349484}, 'E': {'d': 0.111715, 'p': -0.302522, 's': -0.725297}},
        'Cs': {'dens_confinement': {'r0': 10.6, 's': 13.6}, 'U': {'d': 0.159261, 'p': 0.06945,  's': 0.12059 }, 'E': {'d': -0.007997, 'p': -0.027142, 's': -0.076658}},
        'Ba': {'dens_confinement': {'r0': 7.7,  's': 12.0}, 'U': {'d': 0.199559, 'p': 0.105176, 's': 0.149382}, 'E': {'d': -0.074037, 'p': -0.045680, 's': -0.118676}},
        'La': {'dens_confinement': {'r0': 7.4,  's': 8.6 }, 'U': {'d': 0.220941, 'p': 0.115479, 's': 0.160718}, 'E': {'d': -0.113716, 'p': -0.049659, 's': -0.135171}},
        'Lu': {'dens_confinement': {'r0': 5.9,  's': 16.4}, 'U': {'d': 0.220882, 'p': 0.12648,  's': 0.187365}, 'E': {'d': -0.064434, 'p': -0.049388, 's': -0.171078}},
        'Hf': {'dens_confinement': {'r0': 5.2,  's': 14.8}, 'U': {'d': 0.249246, 'p': 0.135605, 's': 0.200526}, 'E': {'d': -0.098991, 'p': -0.051266, 's': -0.187557}},
        'Ta': {'dens_confinement': {'r0': 4.8,  's': 13.8}, 'U': {'d': 0.273105, 'p': 0.141193, 's': 0.212539}, 'E': {'d': -0.132163, 'p': -0.051078, 's': -0.199813}},
        'W':  {'dens_confinement': {'r0': 4.2,  's': 8.6 }, 'U': {'d': 0.294154, 'p': 0.144425, 's': 0.223288}, 'E': {'d': -0.164874, 'p': -0.049978, 's': -0.209733}},
        'Re': {'dens_confinement': {'r0': 4.2,  's': 13.0}, 'U': {'d': 0.313288, 'p': 0.146247, 's': 0.233028}, 'E': {'d': -0.197477, 'p': -0.048416, 's': -0.218183}},
        'Os': {'dens_confinement': {'r0': 4.0,  's': 8.0 }, 'U': {'d': 0.331031, 'p': 0.146335, 's': 0.241981}, 'E': {'d': -0.230140, 'p': -0.046602, 's': -0.225640}},
        'Ir': {'dens_confinement': {'r0': 3.9,  's': 12.6}, 'U': {'d': 0.347715, 'p': 0.145121, 's': 0.250317}, 'E': {'d': -0.262953, 'p': -0.044644, 's': -0.232400}},
        'Pt': {'dens_confinement': {'r0': 3.8,  's': 12.8}, 'U': {'d': 0.363569, 'p': 0.143184, 's': 0.258165}, 'E': {'d': -0.295967, 'p': -0.042604, 's': -0.238659}},
        'Au': {'dens_confinement': {'r0': 4.8,  's': 2.0 }, 'U': {'d': 0.361156, 'p': 0.090767, 's': 0.255962}, 'E': {'d': -0.252966, 'p': -0.028258, 's': -0.211421}},
        'Hg': {'dens_confinement': {'r0': 6.7,  's': 2.0 }, 'U': {'d': 0.393392, 'p': 0.134398, 's': 0.272767}, 'E': {'d': -0.362705, 'p': -0.038408, 's': -0.250189}},
        'Tl': {'dens_confinement': {'r0': 7.3,  's': 2.2 }, 'U': {'d': 0.11952,  'p': 0.185496, 's': 0.267448}, 'E': {'d': 0.081292, 'p': -0.087069, 's': -0.350442}},
        'Pb': {'dens_confinement': {'r0': 5.7,  's': 3.0 }, 'U': {'d': 0.128603, 'p': 0.209811, 's': 0.280804}, 'E': {'d': 0.072602, 'p': -0.128479, 's': -0.442037}},
        'Bi': {'dens_confinement': {'r0': 5.8,  's': 2.6 }, 'U': {'d': 0.14221,  'p': 0.231243, 's': 0.296301}, 'E': {'d': 0.073863, 'p': -0.167900, 's': -0.531518}},
        'Po': {'dens_confinement': {'r0': 5.5,  's': 2.2 }, 'U': {'d': 0.158136, 'p': 0.250546, 's': 0.311976}, 'E': {'d': 0.081795, 'p': -0.206503, 's': -0.620946}},
        'Ra': {'dens_confinement': {'r0': 7.0,  's': 14.0}, 'U': {'d': 0.167752, 'p': 0.093584, 's': 0.151368}, 'E': {'d': -0.047857, 'p': -0.037077, 's': -0.120543}},
        'Th': {'dens_confinement': {'r0': 6.2,  's': 4.4 }, 'U': {'d': 0.21198,  'p': 0.114896, 's': 0.174221}, 'E': {'d': -0.113604, 'p': -0.045825, 's': -0.161992}}
    }

    ## reference values for C6_AA for free atoms in Ha*Bohr**6
    C6_ref = { 'H':6.50,   'He':1.46, \
              'Li':1387.0, 'Be':214.0,   'B':99.5,    'C':46.6,    'N':24.2,   'O':15.6,   'F':9.52,   'Ne':6.38, \
              'Na':1556.0, 'Mg':627.0,  'Al':528.0,  'Si':305.0,   'P':185.0 , 'S':134.0, 'Cl':94.6,   'Ar':64.3, \
               'K':3897.0, 'Ca':2221.0, 'Sc':1383.0, 'Ti':1044.0,  'V':832.0, 'Cr':602.0, 'Mn':552.0,  'Fe':482.0, \
              'Co':408.0,  'Ni':373.0,  'Cu':253.0,  'Zn':284.0,  'Ga':498.0, 'Ge':354.0, 'As':246.0,  'Se':210.0, \
              'Br':162.0,  'Kr':129.6,  'Rb':4691.0, 'Sr':3170.0, 'Rh':469.0, 'Pd':157.5, 'Ag':339.0,  'Cd':452.0, \
              'In':779.0,  'Sn':659.0,  'Sb':492.0,  'Te':396.0,   'I':385.0, 'Xe':285.9, 'Ba':5727.0, 'Ir':359.1, \
              'Pt':347.1,  'Au':298.0,  'Hg':392.0,  'Pb':697.0,  'Bi':571.0 }

    ## reference values for static polarizabilities in Bohr**3
    alpha0_ref = { 'H':4.50,  'He':1.38, \
                  'Li':164.2, 'Be':38.0,   'B':21.0,    'C':12.0,    'N':7.4,   'O':5.4,   'F':3.8,   'Ne':2.67, \
                  'Na':162.7, 'Mg':71.0,  'Al':60.0,  'Si':37.0,   'P':25.0 , 'S':19.6, 'Cl':15.0,   'Ar':11.1, \
                   'K':292.9, 'Ca':160.0, 'Sc':120.0, 'Ti':98.0,  'V':84.0, 'Cr':78.0, 'Mn':63.0,  'Fe':56.0, \
                  'Co':50.0,  'Ni':48.0,  'Cu':42.0,  'Zn':40.0,  'Ga':60.0, 'Ge':41.0, 'As':29.0,  'Se':25.0, \
                  'Br':20.0,  'Kr':16.8,  'Rb':319.2, 'Sr':199.0, 'Rh':56.1, 'Pd':23.68, 'Ag':50.6,  'Cd':39.7, \
                  'In':75.0,  'Sn':60.0,  'Sb':44.0,  'Te':37.65,   'I':35.0, 'Xe':27.3, 'Ba':275.0, 'Ir':42.51, \
                  'Pt':39.68,  'Au':36.5,  'Hg':33.9,  'Pb':61.8,  'Bi':49.02 }


    special_lattice_points = {             
            'G': np.array([0, 0, 0], dtype=np.float64),
            'L': np.array([-0.5, 0, -0.5], dtype=np.float64),
            'M': np.array([-0.5, 0.5, 0.5], dtype=np.float64),
            'N': np.array([0, 0.5, 0], dtype=np.float64),
            'R': np.array([-0.5, 0.5, 0], dtype=np.float64),
            'X': np.array([0, 0, -0.5], dtype=np.float64),
            'Y': np.array([-0.5, 0, 0], dtype=np.float64),
            'Z': np.array([0, 0.5, 0.5], dtype=np.float64),
            }

    element_colors = {
        "H":  (0.7, 0.7, 0.7),   # White
        "He": (0.8, 0.8, 0.8),   # Light Gray
        "Li": (0.8, 0.5, 0.2),   # Light Brown
        "Be": (0.5, 1.0, 0.0),   # Light Green
        "B":  (0.0, 1.0, 0.0),   # Green
        "C":  (0.2, 0.2, 0.2),   # Dark Gray
        "N":  (0.0, 0.0, 1.0),   # Blue
        "O":  (1.0, 0.0, 0.0),   # Red
        "F":  (0.5, 1.0, 1.0),   # Light Cyan
        "Ne": (0.8, 0.8, 1.0),   # Light Blue
        "Na": (0.0, 0.0, 0.5),   # Dark Blue
        "Mg": (0.4, 0.8, 0.0),   # Olive Green
        "Al": (0.8, 0.6, 0.5),   # Pink
        "Si": (0.5, 0.5, 1.0),   # Medium Blue
        "P":  (1.0, 0.5, 0.0),   # Orange
        "S":  (1.0, 1.0, 0.0),   # Yellow
        "Cl": (0.0, 1.0, 0.5),   # Mint Green
        "Ar": (0.5, 0.0, 0.5),   # Purple
        "K":  (0.3, 0.0, 0.8),   # Purple
        "Ca": (0.3, 0.3, 0.3),   # Medium Gray
        "Sc": (0.9, 0.6, 0.9),   # Lavender
        "Ti": (0.3, 0.8, 0.8),   # Turquoise
        "V":  (0.3, 0.1, 0.1),   # Reddish Brown
        "Cr": (0.4, 0.0, 0.0),   # Dark Red
        "Mn": (0.7, 0.0, 0.7),   # Magenta
        "Fe": (0.6, 0.4, 0.0),   # Dark Orange
        "Co": (0.0, 0.6, 0.6),   # Teal
        "Ni": (0.0, 0.8, 0.2),   # Silver Gray
        "Cu": (0.7, 0.4, 0.2),   # Bronze
        "Zn": (0.5, 0.5, 0.5),   # Gray

        "Ga": (0.76, 0.56, 0.56),  # Light Red
        "Ge": (0.40, 0.56, 0.56),  # Light Teal
        "As": (0.74, 0.50, 0.89),  # Light Purple
        "Se": (1.00, 0.63, 0.00),  # Orange
        "Br": (0.65, 0.16, 0.16),  # Dark Red
        "Kr": (0.36, 0.72, 0.82),  # Greenish Blue
        "Rb": (0.44, 0.18, 0.69),  # Dark Purple
        "Sr": (0.00, 1.00, 0.78),  # Turquoise Green
        "Y":  (0.58, 1.00, 1.00),  # Cyan
        "Zr": (0.58, 0.88, 0.88),  # Light Blue
        "Nb": (0.45, 0.76, 0.79),  # Greenish Blue
        "Mo": (0.32, 0.71, 0.71),  # Dark Turquoise
        "Tc": (0.23, 0.62, 0.62),  # Teal Green
        "Ru": (0.14, 0.56, 0.56),  # Dark Green
        "Rh": (0.04, 0.49, 0.55),  # Dark Greenish Blue
        "Pd": (0.00, 0.41, 0.52),  # Navy Blue
        "Ag": (0.75, 0.75, 0.75),  # Silver
        "Cd": (1.00, 0.85, 0.56),  # Light Yellow
        "In": (0.65, 0.46, 0.45),  # Dull Red
        "Sn": (0.40, 0.50, 0.50),  # Bluish Gray
        "Sb": (0.62, 0.39, 0.71),  # Lavender
        "Te": (0.83, 0.48, 0.00),  # Dark Orange
        "I":  (0.58, 0.00, 0.58),  # Violet
        "Xe": (0.26, 0.62, 0.69),  # Sky Blue
        "Cs": (0.34, 0.09, 0.56),  # Dark Purple
        "Ba": (0.00, 0.79, 0.00),  # Green
        "La": (0.44, 0.83, 1.00),  # Light Blue
        "Ce": (1.00, 1.00, 0.78),  # Pale Yellow
        "Pr": (0.85, 1.00, 0.78),  # Light Green
        "Nd": (0.78, 1.00, 0.78),  # Lime Green
        "Pm": (0.64, 1.00, 0.78),  # Apple Green
        "Sm": (0.56, 1.00, 0.78),  # Aqua Green
        "Eu": (0.38, 1.00, 0.78),  # Mint Green
        "Gd": (0.27, 1.00, 0.78),  # Light Turquoise
        "Tb": (0.19, 1.00, 0.78),  # Emerald Green
        "Dy": (0.12, 1.00, 0.78),  # Dark Green
        "Ho": (0.00, 1.00, 0.61),  # Sea Green
        "Er": (0.00, 0.90, 0.46),  # Forest Green
        "Tm": (0.00, 0.83, 0.32),  # Olive Green
        "Yb": (0.00, 0.75, 0.22),  # Moss Green
        "Lu": (0.00, 0.67, 0.14),  # Grass Green
        "Hf": (0.30, 0.76, 1.00),  # Sky Blue
        "Ta": (0.30, 0.65, 1.00),  # Steel Blue
        "W":  (0.13, 0.58, 0.84),  # Petroleum Blue
        "Re": (0.15, 0.49, 0.67),  # Denim Blue
        "Os": (0.15, 0.40, 0.59),  # Navy Blue
        "Ir": (0.09, 0.33, 0.53),  # Dark Blue
        "Pt": (0.82, 0.82, 0.88),  # Pearl Gray
        "Au": (1.00, 0.82, 0.14),  # Gold
        "Hg": (0.72, 0.72, 0.82),  # Metallic Gray
        "Tl": (0.65, 0.33, 0.30),  # Copper Red
        "Pb": (0.34, 0.35, 0.38),  # Lead Gray
        "Bi": (0.62, 0.31, 0.71),  # Purple Pink
        "Po": (0.67, 0.36, 0.00),  # Copper Orange
        "At": (0.46, 0.31, 0.27),  # Brick Brown
        "Rn": (0.26, 0.51, 0.59),  # Greenish Blue
        "Fr": (0.26, 0.00, 0.40),  # Dark Violet
        "Ra": (0.00, 0.49, 0.00),  # Dark Green
        "Ac": (0.44, 0.67, 0.98),  # Medium Blue
        "Th": (0.00, 0.73, 1.00),  # Cyan
        "Pa": (0.00, 0.63, 1.00),  # Azure
        "U":  (0.00, 0.56, 1.00),  # Ultramarine Blue
        "Np": (0.00, 0.50, 1.00),  # Royal Blue
        "Pu": (0.00, 0.42, 1.00),  # Sapphire Blue
        "Am": (0.33, 0.36, 0.95),  # Lavender Blue
        "Cm": (0.47, 0.36, 0.89),  # Blue Violet
        "Bk": (0.54, 0.31, 0.89),  # Purple
        "Cf": (0.63, 0.21, 0.83),  # Magenta
        "Es": (0.70, 0.12, 0.83),  # Fuchsia Pink
        "Fm": (0.70, 0.12, 0.65),  # Dark Pink
        "Md": (0.70, 0.05, 0.65),  # Eggplant Pink
        "No": (0.74, 0.05, 0.53),  # Crimson Red
        "Lr": (0.78, 0.00, 0.40),  # Blood Red
    }
    '''
    'X': np.array([0.5, 0, 0], dtype=np.float64),
    'W': np.array([0.5, 0.25, 0], dtype=np.float64),
    'K': np.array([0.375, 0.375, 0.75], dtype=np.float64),
    #'L': np.array([0.5, 0.5, 0.5], dtype=np.float64),
    'L': np.array([0.5, 0.0, 0.5], dtype=np.float64),
    'A': np.array([0.5, 0.5, 0.5], dtype=np.float64),
    'U': np.array([0.625, 0.25, 0], dtype=np.float64),
    
    'M': np.array([0.0, -0.5, 0.0], dtype=np.float64),
    'N': np.array([0.5, -0.5, -0.5], dtype=np.float64),
    #'R': np.array([0.0, 0.5, 0.5], dtype=np.float64),
    'R': np.array([0.5, -0.5, 0.0], dtype=np.float64),
    'Y': np.array([0.0, 0.0, 0.5], dtype=np.float64),
    'Z': np.array([0.0, -0.5, -0.5], dtype=np.float64),

    'H': np.array([0.5, -0.5, 0.5], dtype=np.float64),
    #'N': np.array([0, 0, 0.5], dtype=np.float64),
    'P': np.array([0.25, 0.25, 0.25], dtype=np.float64),
    'B': np.array([0, 0.25, 0], dtype=np.float64),
    'C': np.array([0, 0, 0.25], dtype=np.float64),
    'D': np.array([0.25, 0.25, 0], dtype=np.float64),
    'E': np.array([0.25, 0, 0.25], dtype=np.float64),
    'F': np.array([0, 0.25, 0.25], dtype=np.float64),
    'Gp': np.array([0.25, 0.25, 0.25], dtype=np.float64),
    'H': np.array([0.5, 0, 0], dtype=np.float64),
    'I': np.array([0, 0.5, 0], dtype=np.float64),
    'J': np.array([0, 0, 0.5], dtype=np.float64),  
    '''
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)