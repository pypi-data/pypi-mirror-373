import numpy as np

class CIF:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        pass

    # ──────────────────────────────────────────────────────────────────────
    def export_as_CIF(self, file_location: str = None, *, datablock: str = "SAGE"):
        """
        Write the current structure to a CIF file.

        Parameters
        ----------
        file_location : str, optional
            Destination path.  If omitted, falls back to `self._file_location`
            with a ".cif" suffix.
        datablock : str, optional
            Name of the CIF data block (default: "SAGE").
        """
        # -------- resolve path -------------------------------------------------
        if file_location is None:
            if not hasattr(self, "_file_location") or self._file_location is None:
                raise ValueError("file_location must be provided the first time.")
            file_location = f"{self._file_location}.cif"

        # -------- sanity checks -----------------------------------------------
        if not hasattr(self, "_latticeParameters") or not hasattr(self, "_latticeAngles"):
            raise AttributeError("Lattice parameters/angles are missing; run read_CIF first.")

        if not hasattr(self, "_atomPositions") or not hasattr(self, "_atomLabelsList"):
            raise AttributeError("Atomic coordinates are missing; run read_CIF first.")

        # -------- write file ---------------------------------------------------
        with open(file_location, "w") as fh:
            # data block header
            fh.write(f"data_{datablock}\n")

            # cell parameters
            a, b, c = self._latticeParameters
            alpha, beta, gamma = np.degrees(self._latticeAngles)  # back to degrees
            fh.write(f"_cell_length_a       {a:.6f}\n")
            fh.write(f"_cell_length_b       {b:.6f}\n")
            fh.write(f"_cell_length_c       {c:.6f}\n")
            fh.write(f"_cell_angle_alpha    {alpha:.6f}\n")
            fh.write(f"_cell_angle_beta     {beta:.6f}\n")
            fh.write(f"_cell_angle_gamma    {gamma:.6f}\n")

            # (optional) symmetry operators
            if getattr(self, "_symmetryEquivPositions", []):
                fh.write("loop_\n")
                fh.write("_symmetry_equiv_pos_as_xyz\n")
                for op in self._symmetryEquivPositions:
                    fh.write(f"  '{op}'\n")

            # atomic sites
            fh.write("loop_\n")
            fh.write("  _atom_site_label\n")
            fh.write("  _atom_site_fract_x\n")
            fh.write("  _atom_site_fract_y\n")
            fh.write("  _atom_site_fract_z\n")

            for lbl, (x, y, z) in zip(self._atomLabelsList, self._atomPositions):
                fh.write(f"  {lbl:<4s} {x:10.6f} {y:10.6f} {z:10.6f}\n")

        return True

    def read_CIF(self, file_location:str=None):
        try:
            import numpy as np
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
            del sys

        file_location = file_location if type(file_location) == str else self._file_location

        lines = [n for n in self.read_file() ]
        # Initialize variables
        self._latticeParameters = [0,0,0]
        self._latticeAngles = [0,0,0]
        self._atomPositions = []
        self._symmetryEquivPositions = []
        self._atomLabelsList = []

        # Flags to indicate the reading context
        reading_atoms = False
        reading_symmetry = False

        for line in lines:
            line = line.strip()

            # Lattice Parameters
            if line.startswith('_cell_length_a'):
                self._latticeParameters[0] = float(line.split()[1])
            elif line.startswith('_cell_length_b'):
                self._latticeParameters[1] = float(line.split()[1])
            elif line.startswith('_cell_length_c'):
                self._latticeParameters[2] = float(line.split()[1])

            # Lattice angles
            if line.startswith('_cell_angle_alpha'):
                self._latticeAngles[0] = np.radians(float(line.split()[1]))
            elif line.startswith('_cell_angle_beta'):
                self._latticeAngles[1] = np.radians(float(line.split()[1]))
            elif line.startswith('_cell_angle_gamma'):
                self._latticeAngles[2] = np.radians(float(line.split()[1]))


            # Symmetry Equiv Positions
            elif line.startswith('loop_'):
                reading_atoms = False  # Reset flags
                reading_symmetry = False  # Reset flags
            elif line.startswith('_symmetry_equiv_pos_as_xyz'):
                reading_symmetry = True
                continue  # Skip the line containing the column headers
            elif reading_symmetry:
                self._symmetryEquivPositions.append(line)

            # Atom positions
            elif line.startswith('_atom_site_label'):
                reading_atoms = True  # Set flag to start reading atoms
                continue  # Skip the line containing the column headers
            elif reading_atoms:
                tokens = line.split()
                if len(tokens) >= 4:  # Make sure it's a complete line
                    label, x, y, z = tokens[:4]
                    self._atomPositions.append([float(x), float(y), float(z)])
                    self._atomLabelsList.append(label)

        # Convert to numpy arrays
        self._atomPositions = np.array(self._atomPositions, dtype=np.float64)
        self._atomicConstraints = np.ones_like(self._atomPositions)
        self._atomCount = self._atomPositions.shape[0]
        self._atomCoordinateType = 'direct'
        self._selectiveDynamics = True
        self._scaleFactor = [1]

        return True
        