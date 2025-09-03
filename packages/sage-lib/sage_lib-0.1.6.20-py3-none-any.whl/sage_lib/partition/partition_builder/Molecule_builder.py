"""
Molecule Builder Library

A Python library for constructing molecular structures, supporting diatomic and triatomic molecules.
Molecular geometries are based on experimental data.

Dependencies:
- numpy for numerical operations
- sage_lib for partition management and atomic position handling

Part of the sage_lib framework.
"""
try:
    from ...IO.structure_handling_tools.AtomPosition import AtomPosition
    from .BasePartition import BasePartition
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

class Molecule_builder(BasePartition):
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        """

        self._diatomic_compounds = {
            'H2':  {'atomLabels': ['H', 'H'],   'atomPositions': [[0, 0, 0], [0, 0,  .62]]},
            'O2':  {'atomLabels': ['O', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.32]]},
            'N2':  {'atomLabels': ['N', 'N'],   'atomPositions': [[0, 0, 0], [0, 0, 1.42]]},
            'F2':  {'atomLabels': ['F', 'F'],   'atomPositions': [[0, 0, 0], [0, 0, 1.14]]},
            'Cl2': {'atomLabels': ['Cl', 'Cl'], 'atomPositions': [[0, 0, 0], [0, 0, 2.04]]},
            'Br2': {'atomLabels': ['Br', 'Br'], 'atomPositions': [[0, 0, 0], [0, 0, 2.40]]},
            'I2':  {'atomLabels': ['I', 'I'],   'atomPositions': [[0, 0, 0], [0, 0, 2.78]]},
            'HF':  {'atomLabels': ['H', 'F'],   'atomPositions': [[0, 0, 0], [0, 0,  .88]]},
            'CO':  {'atomLabels': ['C', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.42]]},
            'NO':  {'atomLabels': ['N', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.37]]}
                            }
                            
        self._triatomic_compounds = {
            'CO2': {'atomLabels': ['C', 'O', 'O'], 
                    'atomPositions': [[0, 0, 0], 
                                    [0, 0, 1.16], 
                                    [0, 0, -1.16]]},
            'H2O': {'atomLabels': ['O', 'H', 'H'], 
                    'atomPositions': [[0, 0, 0], 
                                    [.9584 * np.cos(np.radians(104.5/2)), .9584 * np.sin(np.radians(104.5/2))], 
                                    [.9584 * np.cos(np.radians(104.5/2)), -.9584 * np.cos(np.radians(104.5/2))]]},
            'SO2': {'atomLabels': ['S', 'O', 'O'], 
                    'atomPositions': [[0, 0, 0], 
                                    [1.57 * np.sin(np.radians(119.5/2)), 0, -1.57 * np.cos(np.radians(119.5/2))], 
                                    [-1.57 * np.sin(np.radians(119.5/2)), 0, -1.57 * np.cos(np.radians(119.5/2))]]},
            'O3': {'atomLabels': ['O', 'O', 'O'], 
                'atomPositions': [[0, 0, 0], 
                                    [1.28 * np.sin(np.radians(116.8/2)), 0, -1.28 * np.cos(np.radians(116.8/2))], 
                                    [-1.28 * np.sin(np.radians(116.8/2)), 0, -1.28 * np.cos(np.radians(116.8/2))]]},
            'HCN': {'atomLabels': ['H', 'C', 'N'], 
                    'atomPositions': [[0, 0, 1.20], 
                                    [0, 0, 0], 
                                    [0, 0, -1.16]]},
            'NO2': {'atomLabels': ['N', 'O', 'O'],  # Nitrógeno dióxido
                    'atomPositions': [[0, 0, 0], 
                                    [1.19 * np.sin(np.radians(134.0/2)), 0, -1.19 * np.cos(np.radians(134.0/2))], 
                                    [-1.19 * np.sin(np.radians(134.0/2)), 0, -1.19 * np.cos(np.radians(134.0/2))]]},
            'OCS': {'atomLabels': ['O', 'C', 'S'],  # Carbonyl sulfide
                    'atomPositions': [[0, 0, 1.16],  # O
                                    [0, 0, 0],     # C
                                    [0, 0, -1.19]]},  # S
            'HCO': {'atomLabels': ['H', 'C', 'O'],  # Hidrogenocarbó
                    'atomPositions': [[0, 0, 1.12], 
                                    [0, 0, 0], 
                                    [0, 0, -1.13]]},
            'HNO': {'atomLabels': ['H', 'N', 'O'],  # Ácido nitroso
                    'atomPositions': [[0, 0, 1.07], 
                                    [0, 0, 0], 
                                    [0, 0, -1.16]]},
            'HOCl': {'atomLabels': ['H', 'O', 'Cl'],  # Ácido hipocloroso
                    'atomPositions': [[0, 0, 0], 
                                    [0.98 * np.cos(np.radians(102.5/2)), 0.98 * np.sin(np.radians(102.5/2)), 0], 
                                    [1.47 * np.cos(np.radians(102.5/2)), 1.47 * np.sin(np.radians(102.5/2)), 0]]},
            'NH2': {'atomLabels': ['N', 'H', 'H'],  # Amonia (estado reactivo)
                    'atomPositions': [[0, 0, 0], 
                                    [1.01 * np.cos(np.radians(106.6/2)), 1.01 * np.sin(np.radians(106.6/2)), 0], 
                                    [1.01 * np.cos(np.radians(106.6/2)), -1.01 * np.sin(np.radians(106.6/2)), 0]]},
            'HOO': {'atomLabels': ['H', 'O', 'O'],  # Radical hidroxilo
                    'atomPositions': [[0, 0, 0], 
                                    [0.95 * np.cos(np.radians(119.0/2)), 0.95 * np.sin(np.radians(119.0/2)), 0], 
                                    [0.95 * np.cos(np.radians(119.0/2)), -0.95 * np.sin(np.radians(119.0/2)), 0]]},
            'C3': {'atomLabels': ['C', 'C', 'C'],  # Tricarbono
                'atomPositions': [[0, 0, 0], 
                                    [1.20, 0, 0], 
                                    [2.40, 0, 0]]},
            'LiO2': {'atomLabels': ['Li', 'O', 'O'],  # Superoxido de litio
                    'atomPositions': [[0, 0, 0], 
                                        [1.10 * np.cos(np.radians(117.0/2)), 1.10 * np.sin(np.radians(117.0/2)), 0], 
                                        [1.10 * np.cos(np.radians(117.0/2)), -1.10 * np.sin(np.radians(117.0/2)), 0]]},
            'NaO2': {'atomLabels': ['Na', 'O', 'O'],  # Superoxido de sodio
                    'atomPositions': [[0, 0, 0], 
                                    [1.32 * np.cos(np.radians(117.0/2)), 1.32 * np.sin(np.radians(117.0/2)), 0], 
                                    [1.32 * np.cos(np.radians(117.0/2)), -1.32 * np.sin(np.radians(117.0/2)), 0]]},
            'KO2': {'atomLabels': ['K', 'O', 'O'],  # Superoxido de potasio
                    'atomPositions': [[0, 0, 0], 
                                    [1.47 * np.cos(np.radians(117.0/2)), 1.47 * np.sin(np.radians(117.0/2)), 0], 
                                    [1.47 * np.cos(np.radians(117.0/2)), -1.47 * np.sin(np.radians(117.0/2)), 0]]},
            'MgO2': {'atomLabels': ['Mg', 'O', 'O'],  # Óxido de magnesio
                    'atomPositions': [[0, 0, 0], 
                                    [1.30 * np.cos(np.radians(120.0/2)), 1.30 * np.sin(np.radians(120.0/2)), 0], 
                                    [1.30 * np.cos(np.radians(120.0/2)), -1.30 * np.sin(np.radians(120.0/2)), 0]]},
            'CH2': {'atomLabels': ['C', 'H', 'H'],  # Metilideno
                    'atomPositions': [[0, 0, 0], 
                                    [0.77 * np.cos(np.radians(135.0/2)), 0.77 * np.sin(np.radians(135.0/2)), 0], 
                                    [0.77 * np.cos(np.radians(135.0/2)), -0.77 * np.sin(np.radians(135.0/2)), 0]]},
            'BH2': {'atomLabels': ['B', 'H', 'H'],  # Boro hidruro
                    'atomPositions': [[0, 0, 0], 
                                    [1.18 * np.cos(np.radians(120.0/2)), 1.18 * np.sin(np.radians(120.0/2)), 0], 
                                    [1.18 * np.cos(np.radians(120.0/2)), -1.18 * np.sin(np.radians(120.0/2)), 0]]},
            'AlO': {'atomLabels': ['Al', 'O'],  # Óxido de aluminio (diccionario existente)
                    'atomPositions': [[0, 0, 0], 
                                    [0, 0, 1.61]]}
        }

        super().__init__(*args, **kwargs)

    def build_molecule(self, atomLabels:list, atomPositions:np.array):
        molecule = AtomPosition()

        for al, ap in zip(atomLabels, atomPositions):
            molecule.add_atom(al, ap, [1,1,1])
        
        return molecule

    def build(self, name:str):

        if name in self.diatomic_compounds:
            atomLabels = self.diatomic_compounds[name]['atomLabels']
            atomPositions = self.diatomic_compounds[name]['atomPositions']
            molecule = self.build_molecule(atomLabels, atomPositions)

        if name in self.triatomic_compounds:
            atomLabels = self.triatomic_compounds[name]['atomLabels']
            atomPositions = self.triatomic_compounds[name]['atomPositions']
            molecule = self.build_molecule(atomLabels, atomPositions)

        return molecule

'''
mb = MoleculeBuilder()
mb.build('H2O')
print( mb.atomPositions )
'''