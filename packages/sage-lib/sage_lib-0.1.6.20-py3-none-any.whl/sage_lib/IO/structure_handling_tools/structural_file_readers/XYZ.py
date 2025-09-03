import json
import re
import numpy as np
from typing import Optional, List, Dict, Any

class XYZ:
    def __init__(self, file_location: str = None, name: str = None, **kwargs):
        """
        Initializes the XYZ object.

        Parameters:
            file_location (str): The default path for reading/writing XYZ files.
            name (str): An identifier for this XYZ object.
            **kwargs: Additional keyword arguments passed to the parent constructor.
        """
        self.property_info = None
        self.metadata = None  # Initialize metadata; can hold a dict of lists or any structured data.

    def export_as_xyz(
        self,
        file_location: str = None,
        save_to_file: str = "w",
        verbose: bool = False,
        species: bool = True,
        position: bool = True,
        energy: bool = True,
        forces: bool = True,
        charge: bool = True,
        magnetization: bool = True,
        lattice: bool = True,
        pbc: bool = True,
        time: bool = True,
        fixed: bool = True,
        class_ID: bool = True,
        position_tag: str = "pos",
        forces_tag: str = "forces",
        charge_tag: str = "charge",
        magnetization_tag: str = "magnetization",
        energy_tag: str = "energy",
        fixed_tag: str = "fixed",
        time_tag: str = "time",
        pbc_tag: str = "pbc",
        classID_tag: str = "class_ID",
    ) -> str:
        out = file_location or self.file_location

        # 1) group elements if needed
        #if hasattr(self, "group_elements_and_positions"):
        #    self.group_elements_and_positions()
        # Convenience: choose constraints source if present
        ac = getattr(self, "atomicConstraints", None)
        if ac is None:
            ac = getattr(self, fixed_tag, None)  # allow self.fixed as source too

        # 2) precompute booleans
        inc = {
            "lattice":   lattice   and getattr(self, "latticeVectors", None) is not None,
            "species":   species   and getattr(self, "atomLabelsList", None) is not None,
            "pos":       position  and getattr(self, "atomPositions", None) is not None,
            "forces":    forces    and getattr(self, "total_force", None) is not None,
            "charge":    charge    and getattr(self, "charge", None) is not None,
            "magnet":    magnetization and getattr(self, "magnetization", None) is not None,
            "energy":    energy    and getattr(self, "E", None) is not None,
            "pbc":       pbc       and getattr(self, "latticeVectors", None) is not None,
            "time":      time      and getattr(self, "time", None) is not None,
            "fixed":     fixed     and getattr(self, "selectiveDynamics", False),
            "classID":   class_ID  and getattr(self, "class_ID", None) is not None,
            "meta":      getattr(self, "metadata", None) is not None
        }

        # Determine number of fixed columns (1 for (N,), 3 for (N,3))
        n_fixed_cols = 0
        if inc["fixed"]:
            ac_arr = np.asarray(ac)
            if ac_arr.ndim == 1:
                n_fixed_cols = 1
            elif ac_arr.ndim == 2 and ac_arr.shape[1] in (1, 3):
                n_fixed_cols = int(ac_arr.shape[1])
            else:
                # Fallback: flatten one row to decide; keep it general
                n_fixed_cols = int(np.asarray(ac_arr[0]).size)
        
        # 3) build header
        hdr = []
        if inc["lattice"]:
            vals = " ".join(map(str, self.latticeVectors.flatten()))
            hdr.append(f'Lattice="{vals}"')

        props = []
        if inc["species"]: props.append("species:S:1")
        if inc["pos"]:      props.append(f"{position_tag}:R:3")
        if inc["forces"]:   props.append(f"{forces_tag}:R:3")
        if inc["charge"]:   props.append(f"{charge_tag}:R:1")
        if inc["magnet"]:   props.append(f"{magnetization_tag}:R:1")
        if inc["fixed"]:    props.append(f"{fixed_tag}:I:1")
        if inc["classID"]:  props.append(f"{classID_tag}:I:1")
        if props:
            hdr.append("Properties=" + ":".join(props))
        if inc["energy"]:
            hdr.append(f"{energy_tag}={self.E}")
        if inc["pbc"]:
            hdr.append(f'{pbc_tag}="T T T"')
        if inc["time"]:
            hdr.append(f"{time_tag}={self.time}")
        if inc["meta"]:
            hdr.append(" ".join(f"{k}={json.dumps(v)}" for k, v in self.metadata.items()))

        header_line = " ".join(hdr)

        # 4) build atom lines
        lines = []
        for i in range(self.atomCount):
            cols = []
            if inc["species"]:
                cols.append(self.atomLabelsList[i])
            if inc["pos"]:
                x, y, z = self.atomPositions[i]
                cols += [f"{c:.10f}" for c in (x, y, z)]
            if inc["forces"]:
                cols += [f"{f:.10f}" for f in self.total_force[i]]
            if inc["charge"]:
                ch = self.charge[i] if np.ndim(self.charge) == 1 else self.charge[i, -1]
                cols.append(f"{ch:.10f}")
            if inc["magnet"]:
                mg = self.magnetization[i] if np.ndim(self.magnetization) == 1 else self.magnetization[i, -1]
                cols.append(f"{mg:.10f}")
            #if inc["fixed"]:
            #    cols += str(int(self.atomicConstraints[i])) 
            if inc["fixed"]:
                row = np.asarray(ac[i])
                if row.shape == ():  # numpy scalar
                    cols.append(str(int(bool(row.item()))))
                else:
                    row = row.reshape(-1)
                    # Normalise any bool/float to 0/1 ints
                    cols += [str(int(bool(x))) for x in row[:n_fixed_cols]]

            if inc["classID"]:
                cid = self.class_ID[i] if i < len(self.class_ID) else -1
                cols.append(str(cid))
            lines.append(" ".join(cols))

        # 5) assemble
        content = f"{self.atomCount}\n{header_line}\n" + "\n".join(lines) + "\n"

        # 6) write if needed
        if out and save_to_file != "none":
            with open(out, save_to_file) as f:
                f.write(content)
            if verbose:
                print(f"XYZ content saved to {out}")
        return content

    def read_XYZ(self,
                 file_location: Optional[str] = None,
                 lines: Optional[List[str]] = None,
                 verbose: bool = False,
                 tags: Optional[Dict[str, str]] = None,
                 **kwargs) -> Dict[str, Any]:
        path = file_location or self.file_location
        if not path:
            raise ValueError("Must provide a file_location")

        # Read raw lines if caller passed them, else open file
        if lines is None:
            with open(path, 'r') as f:
                # 1) atom count
                atomCount = int(f.readline().strip())
                # 2) header
                header = f.readline().strip()
                self._parse_header(header)
                # 3) now f yields exactly the atomCount lines (or more; we stop at atomCount)
                raw_lines = (next(f) for _ in range(atomCount))
        else:
            atomCount = int(lines[0].strip())
            self._parse_header(lines[1].strip())
            raw_lines = iter(lines[2:2+atomCount])

        # Build storage lists
        props = self.property_info  # list of (name, dtype, ncols)
        storage: Dict[str, List[Any]] = { name: [] for name,_,_ in props }

        # Single‐pass parse
        for raw in raw_lines:
            tok = raw.split()
            idx = 0
            for name, dtype, ncols in props:
                chunk = tok[idx:idx+ncols]
                idx += ncols
                if dtype == 'S':
                    # string property
                    storage[name].append(chunk[0] if ncols == 1 else chunk)
                else:
                    # numeric property
                    nums = list(map(float, chunk))
                    storage[name].append(nums[0] if ncols == 1 else nums)

        # Bulk convert to numpy arrays
        for name, dtype, ncols in props:
            data = storage[name]
            if dtype == 'S':
                arr = np.array(data, dtype=object)
            elif dtype == 'R':
                arr = np.array(data, dtype=float).reshape(atomCount, ncols)
            else:  # 'I'
                arr = np.array(data, dtype=int).reshape(atomCount, ncols)
            setattr(self, name, arr)

        # Aliases for downstream code
        self.atomLabelsList = getattr(self, 'species', None)
        self.atomPositions  = getattr(self, 'pos', None)
        self.total_force     = getattr(self, 'forces', None)
        self.charge          = getattr(self, 'charge', None)
        self.magnetization   = getattr(self, 'magnetization', None)
        self.atomCount       = atomCount

        return {
            'position':      self.atomPositions,
            'atomCount':     self.atomCount,
            'species':       self.atomLabelsList,
            'forces':        self.total_force,
            'charge':        self.charge,
            'magnetization': self.magnetization,
            'latticeVectors': getattr(self, 'latticeVectors', None),
            'energy':         getattr(self, 'E', None),
            'pbc':            getattr(self, 'pbc', None),
            'metadata':       getattr(self, 'metadata', None)
        }

    def _parse_header(self, header_line: str) -> None:
        """
        Parses the header line of the extended XYZ format, extracting information such as
        Lattice, Properties, energy, pbc, and metadata (if present).
        """
        # Use a regex to find key=value pairs. Values may be in quotes or unquoted.
        header_parts = re.findall(r'(\w+)=("[^"]+"|[^\s]+)', header_line)

        for key, value in header_parts:
            if key == 'Lattice':
                # Convert the flattened numeric string into a 3x3 numpy array
                self.latticeVectors = np.array(list(map(float, value.strip('"').split()))).reshape(3, 3)
            elif key == 'Properties':
                # This sets self.property_info so we know how many columns each property occupies
                self._parse_properties(value.strip('"'))
            elif key == 'energy':
                self.E = float(value)
            elif key == 'pbc':
                # Expecting strings like "T T T" to indicate True/False for each dimension
                self.pbc = [v.lower() == 't' for v in value.strip('"').split()]
            elif key == 'metadata':
                # Attempt to parse JSON back into a Python object
                self.metadata = json.loads(value.strip('"'))
            else:
                # If we have other custom keys, store them in an info dictionary
                if not hasattr(self, 'info_system'):
                    self.info_system = {}
                self.info_system[key] = value

    def _parse_properties(self, properties_str: str) -> None:
        """
        Parses the 'Properties=' definition to understand the data columns that follow
        in the atomic section.

        E.g., a string like: species:S:1:pos:R:3:forces:R:3
        tells us that the columns are:

            1) species (string)  # 1 column
            2) pos (real)        # 3 columns
            3) forces (real)     # 3 columns
        """
        self.property_info = []
        parts = properties_str.split(':')
        for i in range(0, len(parts), 3):
            name, dtype, ncols = parts[i:i+3]
            self.property_info.append((name, dtype, int(ncols)))

    def _parse_atom_data(self, atom_lines: List[str]) -> None:
        """
        Parses the per-atom data lines according to the structure defined
        in self.property_info from the header line.

        Parameters:
            atom_lines (List[str]): The lines following the header in the extended XYZ file.
        """
        # Split each line by whitespace and form a 2D array
        clean_lines = [line.strip() for line in atom_lines if line.strip()]
        data = np.array([line.split() for line in clean_lines])

        if len(data) != self.atomCount:
            raise ValueError(f"Number of data lines ({len(data)}) does not match atomCount ({self.atomCount})")

        col_index = 0
        for name, dtype, ncols in self.property_info:
            end_index = col_index + ncols
            if end_index > data.shape[1]:
                raise ValueError(f"Not enough columns in data for property '{name}'")

            if dtype == 'S':
                # String columns
                setattr(self, name, data[:, col_index])
            elif dtype == 'R':
                # Float columns
                setattr(self, name, data[:, col_index:end_index].astype(float))
            elif dtype == 'I':
                # Integer columns
                if ncols == 1:
                    setattr(self, name, data[:, col_index].astype(int))
                else:
                    setattr(self, name, data[:, col_index:end_index].astype(int))
            col_index = end_index

        # Assign aliases to known property names
        self.atomLabelsList = getattr(self, 'species', None)
        self.atomPositions = getattr(self, 'pos', None)
        self.total_force = getattr(self, 'forces', None)
        self.charge = getattr(self, 'charge', None)
        self.magnetization = getattr(self, 'magnetization', None)

    @staticmethod
    def read_file(file_location: str, strip: bool = True) -> List[str]:
        """
        Reads the content of a file and returns its lines.

        Parameters:
            file_location (str): The location of the file to read.
            strip (bool): If True, strips whitespace from each line.

        Returns:
            List[str]: All lines from the file.
        """
        with open(file_location, 'r') as f:
            if strip:
                return [line.strip() for line in f]
            else:
                return [line for line in f]
