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

class KPointsManager(FileManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._num_kpoints = None
        self._coordinate_system = None
        self._kpoints = []
        self._mesh_type = None
        self._centering = None
        self._subdivisions = None
        self._shift = None
        self._points_per_line = None
        self._paths = []
        self._numberOfTetrahedra = None
        self._volumeWeight = None
        self._KPOINTmesh = None

    def readKPOINTS(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self.file_location

        lines = [n for n in self.read_file(file_location) ]

        self.comment = lines[0].strip()
        self.num_kpoints = int(float(lines[1].strip().split()[0]))

        mesh_type_flag = lines[2].strip().split()[0].lower()[0]    

        if self.num_kpoints == 0:
            if mesh_type_flag in ['g', 'm']:
                self.mesh_type = 'Regular'
                self.centering = 'Gamma' if mesh_type_flag == 'g' else 'Monkhorst-Pack'
                self.subdivisions = [int(float(n)) for n in lines[3].strip().split()[:3] ] #list(map(float, lines[3].strip().split()[:3]) )
                if len(lines) > 4:
                    try: self.shift = list(map(float, lines[4].strip().split()[:3] ))
                    except: pass

            elif mesh_type_flag in ['a']:
                self.mesh_type = 'Automatic'
                self.length = float(lines[3].strip())

            else:
                self.mesh_type = 'Generalized'
                self.coordinate_system = 'Cartesian' if mesh_type_flag in ['c', 'k'] else 'Fractional' if mesh_type_flag == 'r' else None
                self.KPOINTmesh = []
                for i, line in enumerate(lines[3:]):  
                    line_split = line.strip().split()
                    if len(line_split) > 2:
                        self.KPOINTmesh.append(line_split[:3]) 

        elif mesh_type_flag == 'l':
            self.mesh_type = 'Line Mode'
            self.points_per_line = self.num_kpoints
            self.coordinate_system = lines[3].strip()
            path = []
            for line in lines[4:]:
                if line.strip():  # Skip empty lines
                    coords, label = line.strip().rsplit(maxsplit=1)
                    kx, ky, kz = map(float, coords.split())
                    path.append({'kx': kx, 'ky': ky, 'kz': kz, 'label': label})
                else:
                    if path:
                        self.paths.append(path)
                        path = []
            if path:
                self.paths.append(path)  # Append remaining path if any

        else:
            self.mesh_type = 'Explicit'

            if mesh_type_flag == 'c' or mesh_type_flag == 'k':
                self.coordinate_system = 'Cartesian'
            else:        
                self.coordinate_system = 'Fractional'

            for i, line in enumerate(lines[3:]):  
                if line.strip().split()[0][0].lower() == 't': # Tetrahedron case
                    self.numberOfTetrahedra = lines[i+1].strip().split(' ')[0]
                    self.volumeWeight = lines[i+1].strip().split(' ')[1:]
                    break
                else:
                    kx, ky, kz, weight = map(float, line.split()[:4])
                    self.kpoints.append({'kx': kx, 'ky': ky, 'kz': kz, 'weight': weight})

    def exportAsKPOINTS(self, file_location:str=None):
        file_location = file_location if file_location is not None else self.file_location
        lines = []

        # Write the comment line
        lines.append(self.comment)

        # Write the number of k-points
        lines.append(str(self.num_kpoints))

        # Handle different mesh types
        if self.mesh_type == 'Regular':
            lines.append(self.centering)
            lines.append(" ".join(map(str, self.subdivisions)))
            if hasattr(self, 'shift'):
                lines.append(" ".join(map(str, self.shift)))

        elif self.mesh_type == 'Automatic':
            lines.append('Auto')
            lines.append(str(self.length))

        elif self.mesh_type == 'Line Mode':
            lines.append('Line Mode')
            lines.append(self.coordinate_system)
            for path in self.paths:
                for point in path:
                    lines.append("{kx} {ky} {kz} {label}".format(**point))
                lines.append("")  # Empty line to separate different paths

        elif self.mesh_type == 'Explicit':
            lines.append(self.coordinate_system)
            for kpoint in self.kpoints:
                lines.append("{kx} {ky} {kz} {weight}".format(**kpoint))

        # Write to file
        with open(file_location, 'w') as f:
            for line in lines:
                f.write(line + "\n")

    def summary(self, ) -> str:
        text_str = ''
        # Display parsed information based on the mesh type
        if self.mesh_type == 'Explicit':
            text_str +=f"Mesh Type: {self.mesh_type}\n"
            text_str += f"Comment: {self.comment}\n"
            text_str += f"Number of k-points: {self.num_kpoints}\n"
            text_str += f"Coordinate System: {self.coordinate_system}\n"
            text_str += f"K-points: {self.kpoints}\n"
            text_str += f"NumberOfTetrahedra: {self.numberOfTetrahedra}\n"
            text_str += f"VolumeWeight: {self.volumeWeight}\n"

        elif self.mesh_type == 'Line Mode':
            text_str += f"Mesh Type: {self.mesh_type}\n"
            text_str += f"Comment: {self.comment}\n"
            text_str += f"Points per Line: {self.points_per_line}\n"
            text_str += f"Coordinate System: {self.coordinate_system}\n"
            text_str += f"Paths:\n"
            for i, p in enumerate(self.paths):
                k0x,k0y,k0z,  k1x,k1y,k1z = p[0]['kx'],p[0]['ky'],p[0]['kz'],  p[1]['kx'],p[1]['ky'],p[1]['kz']  
                text_str +=  f' ({i})  {k0x:<4.2f},{k0y:<4.2f},{k0z:<4.2f} >> {k1x:<4.2f},{k1y:<4.2f},{k1z:<4.2f}\n'
 
        elif self.mesh_type == 'Automatic':
            text_str += f"Mesh Type: {self.mesh_type}\n"
            text_str += f"Comment: {self.comment}\n"
            text_str += f"Length: {self.length}\n"

        elif self.mesh_type == 'Generalized':
            text_str += f"Mesh Type: {self.mesh_type}\n"
            text_str += f"Comment: {self.comment}\n"
            text_str += f"Length: {self.coordinate_system}\n"
            text_str += f"Length: {self.KPOINTmesh}\n"
        else:
            text_str += f"Mesh Type: {self.mesh_type}\n"
            text_str += f"Comment: {self.comment}\n"
            text_str += f"Centering: {self.centering}\n"
            text_str += f"Subdivisions: {self.subdivisions}\n"
            if self.shift:
                text_str += f"Shift: {self.shift}\n"
        return text_str 
'''
kpoints_manager = KPointsManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/KPOINTS/example/KPOINTband')
kpoints_manager = KPointsManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/KPOINTS/example/KPOINTSgeneralized')
kpoints_manager = KPointsManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/KPOINTS/example/KPOINTregular')
kpoints_manager = KPointsManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/KPOINTS/example/KPOINTSexplicitTetrahedron')
kpoints_manager = KPointsManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/KPOINTS/example/KPOINTSexplicit')
kpoints_manager.readKPOINTS()
print(kpoints_manager.summary())
kpoints_manager.exportKPOINTS('/home/akaris/Documents/code/Physics/VASP/v6.1/files/KPOINTS/example/KPOINTexportation')
'''
