try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import re
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing re: {str(e)}\n")
    del sys

class POSCAR:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        self._atomCountByType = None

    @property
    def atomCountByType(self):
        return self._atomCountByType

    @atomCountByType.setter
    def atomCountByType(self, value):
        """Allow external or internal code to overwrite the cached counts."""
        self._atomCountByType = np.asarray(value, dtype=int)

    def group_elements_and_positions(self, atomLabelsList:list=None, atomPositions:list=None):
        # Verificar que la longitud de element_labels coincide con el número de filas en position_matrix
        atomLabelsList = atomLabelsList if atomLabelsList is not None else self.atomLabelsList
        atomPositions = atomPositions if atomPositions is not None else self.atomPositions
        # Crear un diccionario para almacenar los índices de cada tipo de elemento
        element_indices = {}

        for i, label in enumerate(atomLabelsList):
            if label not in element_indices:
                element_indices[label] = []
            element_indices[label].append(i)

        # Crear una nueva lista de etiquetas y una nueva matriz de posiciones
        atomLabelsList_new = []
        atomPositions_new = []
        uniqueAtomLabels_new = element_indices.keys()
        for label in element_indices:
            atomLabelsList_new.extend([label] * len(element_indices[label]))
            atomPositions_new.extend(atomPositions[element_indices[label]])

        self.atomLabelsList = np.array(atomLabelsList_new, dtype=object)
        self.atomPositions = np.array(atomPositions_new)
        self.uniqueAtomLabels = set(atomLabelsList)

        unique_labels, count = np.unique(self.atomLabelsList, return_counts=True)

        self.atomCountByType = count

        return True

    def export_as_POSCAR(self, file_location:str=None, v:bool=False) -> bool:
        file_location  = file_location  if not file_location  is None else self.file_location+'POSCAR' if self.file_location is str else self.file_location

        self.group_elements_and_positions()

        with open(file_location, 'w') as file:
            # Comentario inicial
            file.write(f'POSCAR : JML code \n')

            # Factor de escala
            file.write(f"{' '.join(map(str, self.scaleFactor))}\n")

            # Vectores de la celda unitaria
            for lv in self.latticeVectors:
                file.write('{:>18.15f}\t{:>18.15f}\t{:>18.15f}\n'.format(*lv))

            # Tipos de átomos y sus números
            file.write('    '.join(self.uniqueAtomLabels) + '\n')
            file.write('    '.join(map(str, self.atomCountByType)) + '\n')

            # Opción para dinámica selectiva (opcional)
            if self.selectiveDynamics:     file.write('Selective dynamics\n')
            # Tipo de coordenadas (Direct o Cartesian)
            aCT = 'Cartesian' if self.atomCoordinateType[0].capitalize() in ['C', 'K'] else 'Direct'
            file.write(f'{aCT}\n')

            # Coordenadas atómicas y sus restricciones
            for i, atom in enumerate(self.atomPositions if self.atomCoordinateType[0].capitalize() in ['C', 'K'] else self.atomPositions_fractional):
                coords = '\t'.join(['{:>18.15f}'.format(n) for n in atom])
                constr = '\t'.join(['T' if n else 'F' for n in self.atomicConstraints[i]]) if self.selectiveDynamics else ''
                file.write(f'\t{coords}\t{constr}\n')

            # Comentario final (    opcional)
            file.write('Comment_line\n')
            if hasattr(self, 'dynamical_eigenvector_diff') and not self.dynamical_eigenvector_diff is None: 
                for i, atom in enumerate(self.dynamical_eigenvector_diff if self.atomCoordinateType[0].capitalize() in ['C', 'K'] else self.dynamical_eigenvector_diff_fractional):
                    coords = '\t'.join(['{:>18.15f}'.format(n) for n in atom])
                    file.write(f'\t{coords}\n')
                
    def read_POSCAR(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self.file_location
        lines = [n for n in self.read_file(file_location) ]
        
        self._comment = lines[0].strip()
        self._scaleFactor = list(map(float, lines[1].strip().split()))
        
        # Reading lattice vectors
        self._latticeVectors = np.array([list(map(float, line.strip().split())) for line in lines[2:5]])
        
        # Species names (optional)
        if self.is_number(lines[5].strip().split()[0]):
            self._uniqueAtomLabels = None
            offset = 0
        else:
            self._uniqueAtomLabels = lines[5].strip().split()
            offset = 1
  
        # Ions per species
        self._atomCountByType = np.array(list(map(int, lines[5+offset].strip().split())))
        
        # Selective dynamics (optional)
        if not self.is_number(lines[6+offset].strip()[0]):
            if lines[6+offset].strip()[0].capitalize() == 'S':
                self._selectiveDynamics = True
                offset += 1
            else:
                self._selectiveDynamics = False
        
        # atomic coordinated system
        if lines[6+offset].strip()[0].capitalize() in ['C', 'K']:
            self._atomCoordinateType = 'cartesian'
        else:
            self._atomCoordinateType = 'direct'

        # Ion positions
        self._atomCount = np.array(sum(self._atomCountByType))
        if self._atomCoordinateType == 'cartesian':
            self._atomPositions = np.array([list(map(float, line.strip().split()[:3])) for line in lines[7+offset:7+offset+self._atomCount]])
        else:
            self._atomPositions_fractional = np.array([list(map(float, line.strip().split()[:3])) for line in lines[7+offset:7+offset+self._atomCount]])

        self._atomicConstraints = (np.array([list(map(str, line.strip().split()[3:])) for line in lines[7+offset:7+offset+self._atomCount]]) == 'T').astype(int) if self.selectiveDynamics else None
        # Check for lattice velocities
        # Check for ion velocities

    def read_CONTCAR(self, file_location:str=None):
        self.read_POSCAR(file_location)

