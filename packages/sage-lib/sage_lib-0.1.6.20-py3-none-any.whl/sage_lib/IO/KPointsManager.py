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
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class KPointsManager(FileManager, AtomicProperties):
    """
    A class to manage k-point data for use in electronic structure calculations (e.g., VASP).

    The KPointsManager class provides utilities for parsing, managing, and exporting
    k-point grids, band paths, and special points. It supports different k-point generation
    schemes, including regular grids (e.g., Monkhorst-Pack), automatic meshes, explicit k-points,
    and band structure paths.

    Attributes:
    ----------
    _num_kpoints : int
        Number of k-points in the grid or path.
    _coordinate_system : str
        The coordinate system used (e.g., Cartesian, Reciprocal).
    _kpoints : list
        List of k-points with optional weights.
    _mesh_type : str
        Type of k-point mesh ('Regular', 'Automatic', 'Explicit', etc.).
    _centering : str
        Centering of the mesh ('Gamma', 'Monkhorst-Pack').
    _subdivisions : list
        Subdivisions along the reciprocal lattice vectors.
    _shift : list
        Shift of the grid from the origin.
    _points_per_line : int
        Number of points per line in band structure calculations.
    _numberOfTetrahedra : int
        Number of tetrahedra in the grid (for tetrahedron integration).
    _volumeWeight : list
        Volume weights associated with the tetrahedra.
    _paths : list
        High-symmetry paths for band structure calculations.
    _special_lattice_points : dict
        Dictionary of special lattice points in reciprocal space.
    """
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initialize the KPointsManager class.

        Parameters:
        ----------
        file_location : str, optional
            Path to the KPOINTS file to read.
        name : str, optional
            Name identifier for the k-point set.
        """
        FileManager.__init__(self, name=name, file_location=file_location)
        AtomicProperties.__init__(self)

        self._num_kpoints = None
        self._coordinate_system = None
        self._kpoints = []
        self._mesh_type = None
        self._centering = None
        self._subdivisions = None
        self._shift = None
        self._points_per_line = None

        self._numberOfTetrahedra = None
        self._volumeWeight = None
        self._KPOINTmesh = None

        self._paths = []  # Stores band path as segments of pairs
        self._special_lattice_points = {}  # Predefined special points

    @property
    def band_path(self):
        """Getter for band path."""
        return self._paths

    @band_path.setter
    def band_path(self, path):
        """
        Setter for band path. Converts a list of points into path segments.

        Parameters:
        ----------
        path : list
            List of point labels corresponding to a predefined set of special points.
        """
        if not isinstance(path, list):
            raise ValueError("Band path must be a list of point labels.")
        if len(path) < 2:
            raise ValueError("Band path must contain at least two points.")

        self._paths = []
        for i in range(len(path) - 1):  # Crear segmentos consecutivos
            start_label, end_label = path[i], path[i + 1]
            if start_label not in self._special_lattice_points or end_label not in self._special_lattice_points:
                raise ValueError(f"Labels {start_label} or {end_label} not found in special points.")
            start_point = self._special_lattice_points[start_label] + [start_label]
            end_point = self._special_lattice_points[end_label] + [end_label]
            self._paths.append([start_point, end_point])

    @property
    def special_points(self):
        """Getter for special points."""
        return self._special_lattice_points

    @special_points.setter
    def special_points(self, points_dict):
        """
        Setter for special lattice points.

        Parameters:
        ----------
        points_dict : dict
            A dictionary of special lattice points with labels as keys
            and reciprocal coordinates as values.
        """
        if not isinstance(points_dict, dict):
            raise ValueError("Special points must be provided as a dictionary.")
        self._special_lattice_points = points_dict


    def readKPOINTS(self, file_location:str=None):
        """
        Reads a KPOINTS file and parses its content.

        Parameters:
        ----------
        file_location : str, optional
            Path to the KPOINTS file. If not provided, the class instance's `file_location` is used.

        Notes:
        -----
        - The KPOINTS file determines the sampling of reciprocal space for electronic
          structure calculations. Depending on the mesh type, different parsing logic
          is applied.
        """
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

    def exportAsKPOINTS(self, file_location: str = None):
        """
        Exports the k-point information to a VASP-compatible `KPOINTS` file.

        Parameters:
        ----------
        file_location : str, optional
            The path to save the exported `KPOINTS` file. If not provided,
            the instance's `file_location` will be used.

        Notes:
        -----
        - The format of the exported file depends on the `mesh_type`:
            - 'Regular': Gamma or Monkhorst-Pack mesh.
            - 'Automatic': A single number specifying the mesh density.
            - 'Line Mode': High-symmetry paths for band structure calculations.
            - 'Explicit': A manually specified list of k-points.
        - Each path in 'Line Mode' includes comments with the corresponding
          special point labels.
        """
        # Determine the output file location, using the instance's `file_location` as fallback
        file_location = file_location or self.file_location
        
        # Initialize the lines list with the comment and number of k-points
        lines = [self.comment, str(self.num_kpoints)]

        # Handle different k-point mesh types
        if self.mesh_type == 'Regular':
            # Regular mesh (Gamma or Monkhorst-Pack)
            lines.append(self.centering)
            lines.append(" ".join(map(str, self.subdivisions)))
            if self.shift:  # Include shift if defined
                lines.append(" ".join(map(str, self.shift)))

        elif self.mesh_type == 'Automatic':
            # Automatic mesh with density specified by `self.length`
            lines.extend(['Auto', str(self.length)])

        elif self.mesh_type == 'Line Mode':
            # Band structure paths along high-symmetry points
            lines.extend(['Line Mode', self._coordinate_system])
            # Construct path lines with special point labels
            path_lines = [
                f"{start[0]} {start[1]} {start[2]} ! {start[3]}\n{end[0]} {end[1]} {end[2]} ! {end[3]}\n"
                for start, end in self._paths
            ]
            lines.extend(path_lines)

        elif self.mesh_type == 'Explicit':
            # Explicitly specified k-points with weights
            lines.append(self.coordinate_system)
            lines.extend(
                f"{kpoint['kx']} {kpoint['ky']} {kpoint['kz']} {kpoint['weight']}"
                for kpoint in self.kpoints
            )

        # Write the collected lines to the output file
        with open(file_location, 'w') as f:
            f.write("\n".join(lines) + "\n")  # Ensure proper newline formatting


    def set_band_path(self, special_points: dict, segments: list, divisions:int=30):
        """
        Configure the band path using special points and connecting segments.

        Parameters:
        ----------
        special_points : dict
            Dictionary of special points in reciprocal space.
        segments : list
            List of tuples representing the path segments [(label1, label2), ...].
        divisions : int
            Number of points per segment.
        """
        self.comment = 'KPOINTS for band structure'
        self.num_kpoints = divisions
        self.mesh_type = 'Line Mode'
        self.coordinate_system = 'Reciprocal'

        self._special_lattice_points = special_points  # Store the special points
        self._paths = []  # Clear existing paths

        for start_label, end_label in segments:
            if start_label not in special_points or end_label not in special_points:
                raise ValueError(f"Labels {start_label} or {end_label} not found in special points.")
            start_point = special_points[start_label] + [start_label]
            end_point = special_points[end_label] + [end_label]
            self._paths.append([start_point, end_point])

        return True

    def summary(self, ) -> str:
        """
        Provides a summary of the parsed k-point information.

        Returns:
        -------
        str
            A formatted string describing the k-point setup.
        """
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

        elif self._mesh_type == 'Line Mode':
            text_str += f"Mesh Type: {self._mesh_type}\n"
            text_str += f"Comment: {self.comment}\n"
            text_str += f"Points per Line: {self._points_per_line}\n"
            text_str += f"Coordinate System: {self._coordinate_system}\n"
            text_str += f"Paths:\n"
            for i, path in enumerate(self._paths):
                k0, k1 = path[0], path[1]
                text_str += f' ({i}) {k0[0]:<4.2f},{k0[1]:<4.2f},{k0[2]:<4.2f} ({k0[3]}) >> {k1[0]:<4.2f},{k1[1]:<4.2f},{k1[2]:<4.2f} ({k1[3]})\n'
         
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

if __name__ == "__main__":
    # Example: Hexagonal cell
    cell_hex = np.array([[1.0, 0.0, 0.0],               # Vector a
                         [-0.5, np.sqrt(3) / 2, 0.0],   # Vector b
                         [0.0, 0.0, 2.0]])              # Vector c

    # Identify the hexagonal lattice
    try:
        from ..miscellaneous.get_bravais_lattice import identify_lattice, ibz_points, sc_special_points, special_segments
        lattice, operation = identify_lattice(cell_hex, eps=1e-4, pbc=[True, True, True])
        print(ibz_points[lattice.name], sc_special_points[lattice.name], special_segments[lattice.name])
        print(f"The identified lattice type is: {lattice.name}")
        print (  )
        KPOITNS = KPointsManager()
        KPOITNS.set_band_path( sc_special_points[lattice.name], special_segments[lattice.name] )
        #KPOITNS.exportAsKPOINTS('KPOINTS')

    except RuntimeError as e:
        print(f"Could not identify the lattice: {e}")

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
