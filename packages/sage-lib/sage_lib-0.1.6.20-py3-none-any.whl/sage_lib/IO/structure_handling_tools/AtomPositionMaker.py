import importlib
from functools import cached_property

class AtomPositionMaker:
    """
    Lazily builds and manipulates molecular structures (mono-, di-, and triatomic).

    Attributes are computed on first access to minimize initial import overhead.
    """

    def __init__(self, file_location: str = None, name: str = None, **kwargs):
        self.file_location = file_location
        self.name = name
        # other attributes (e.g. atomPositions, mass_list) will be set when building

    @cached_property
    def atomic_compounds(self):
        # Single-atom entries; uses self.atomic_numbers if defined
        nums = getattr(self, 'atomic_numbers', [])
        return {str(a): {'atomLabels': [str(a)], 'atomPositions': [[0, 0, 0]]} for a in nums}

    @cached_property
    def diatomic_compounds(self):
        return {
            'H2':  {'atomLabels': ['H', 'H'],   'atomPositions': [[0, 0, 0], [0, 0, 0.74]]},  
            'O2':  {'atomLabels': ['O', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.21]]},  
            'OH':  {'atomLabels': ['O', 'H'],   'atomPositions': [[0, 0, 0], [0, 0, 0.97]]},  
            'N2':  {'atomLabels': ['N', 'N'],   'atomPositions': [[0, 0, 0], [0, 0, 1.10]]},  
            'F2':  {'atomLabels': ['F', 'F'],   'atomPositions': [[0, 0, 0], [0, 0, 1.42]]},  
            'Cl2': {'atomLabels': ['Cl', 'Cl'], 'atomPositions': [[0, 0, 0], [0, 0, 1.99]]},  
            'Br2': {'atomLabels': ['Br', 'Br'], 'atomPositions': [[0, 0, 0], [0, 0, 2.28]]},  
            'I2':  {'atomLabels': ['I', 'I'],   'atomPositions': [[0, 0, 0], [0, 0, 2.66]]},  
            'HF':  {'atomLabels': ['H', 'F'],   'atomPositions': [[0, 0, 0], [0, 0, 0.92]]},  
            'CO':  {'atomLabels': ['C', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.13]]},  
            'NO':  {'atomLabels': ['N', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.15]]},  
            'CN':  {'atomLabels': ['C', 'N'],   'atomPositions': [[0, 0, 0], [0, 0, 1.17]]},  
            'BO':  {'atomLabels': ['B', 'O'],   'atomPositions': [[0, 0, 0], [0, 0, 1.21]]},  
            'SiO': {'atomLabels': ['Si', 'O'],  'atomPositions': [[0, 0, 0], [0, 0, 1.52]]},  
            'CuO': {'atomLabels': ['Cu', 'O'],  'atomPositions': [[0, 0, 0], [0, 0, 1.82]]}   
        }

    @cached_property
    def triatomic_compounds(self):
        # lazy import numpy only when needed
        np = importlib.import_module('numpy')
        to_rad = np.radians
        return {
            'CO2': {'atomLabels': ['C', 'O', 'O'], 'atomPositions': [[0, 0, 0], [0, 0, 1.16], [0, 0, -1.16]]},
            'H2O': {'atomLabels': ['O', 'H', 'H'], 'atomPositions': [
                [0, 0, 0], 
                [0.96 * np.cos(np.radians(104.5 / 2)), 0, 0.96 * np.sin(np.radians(104.5 / 2))], 
                [0.96 * np.cos(np.radians(104.5 / 2)), 0, -0.96 * np.sin(np.radians(104.5 / 2))]]},
            'SO2': {'atomLabels': ['S', 'O', 'O'], 'atomPositions': [
                [0, 0, 0], 
                [1.43 * np.cos(np.radians(119.5)), 0, 1.43 * np.sin(np.radians(119.5))], 
                [-1.43 * np.cos(np.radians(119.5)), 0, -1.43 * np.sin(np.radians(119.5))]]},  
            'O3':  {'atomLabels': ['O', 'O', 'O'], 'atomPositions': [
                [0, 0, 0], 
                [1.28 * np.cos(np.radians(116.8)), 0, 1.28 * np.sin(np.radians(116.8))], 
                [-1.28 * np.cos(np.radians(116.8)), 0, -1.28 * np.sin(np.radians(116.8))]]},
            'HCN': {'atomLabels': ['H', 'C', 'N'], 'atomPositions': [[0, 0, 1.06], [0, 0, 0], [0, 0, -1.16]]},
            'H2S': {'atomLabels': ['S', 'H', 'H'], 'atomPositions': [
                [0, 0, 0], 
                [0.96 * np.cos(np.radians(92.1 / 2)), 0, 0.96 * np.sin(np.radians(92.1 / 2))], 
                [0.96 * np.cos(np.radians(92.1 / 2)), 0, -0.96 * np.sin(np.radians(92.1 / 2))]]},  
            'CS2': {'atomLabels': ['C', 'S', 'S'], 'atomPositions': [[0, 0, 0], [0, 0, 1.55], [0, 0, -1.55]]},  
            'NO2': {'atomLabels': ['N', 'O', 'O'], 'atomPositions': [
                [0, 0, 0], 
                [1.20 * np.cos(np.radians(134.1)), 0, 1.20 * np.sin(np.radians(134.1))], 
                [-1.20 * np.cos(np.radians(134.1)), 0, -1.20 * np.sin(np.radians(134.1))]]},  
            'HCO': {'atomLabels': ['H', 'C', 'O'], 'atomPositions': [[0, 0, 1.10], [0, 0, 0], [0, 0, -1.12]]}, 
            'HOF': {'atomLabels': ['H', 'O', 'F'], 'atomPositions': [[0, 0, 1.10], [0, 0, 0], [0, 0, -1.44]]}, 
            'C2H2': {'atomLabels': ['C', 'C', 'H', 'H'], 'atomPositions': [[0, 0, 0], [1.20, 0, 0], [0, 0, 1.08], [1.20, 0, -1.08]]}  
        }

    def get_triatomic_compound(self, name: str):
        return self.triatomic_compounds.get(name)

    def build_molecule(self, atomLabels: list, atomPositions, center: str = 'mass_center'):
        # add atoms, compute mass_list etc before centering
        for label, pos in zip(atomLabels, atomPositions):
            self.add_atom(label, pos, [1, 1, 1])

        if center in ('mass_center', 'gravity_center'):
            disp = (self.atomPositions.T * self.mass_list).sum(axis=1) / self.mass_list.sum()
        elif center in ('geometric_center', 'baricenter'):
            disp = self.atomPositions.mean(axis=1)
        else:
            disp = [0, 0, 0]

        self.set_atomPositions(self.atomPositions - disp)

    def build(self, name: str, center: str = 'mass_center'):
        if name in self.atomic_compounds:
            labels = self.atomic_compounds[name]['atomLabels']
            pos = self.atomic_compounds[name]['atomPositions']
        elif name in self.diatomic_compounds:
            labels = self.diatomic_compounds[name]['atomLabels']
            pos = self.diatomic_compounds[name]['atomPositions']
        elif name in self.triatomic_compounds:
            labels = self.triatomic_compounds[name]['atomLabels']
            pos = self.triatomic_compounds[name]['atomPositions']
        else:
            raise ValueError(f"Unknown molecule '{name}'")

        self.build_molecule(labels, pos, center)

