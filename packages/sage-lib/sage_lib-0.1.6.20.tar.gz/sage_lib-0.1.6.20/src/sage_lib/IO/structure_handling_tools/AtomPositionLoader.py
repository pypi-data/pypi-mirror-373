import importlib
import sys
from functools import lru_cache
from pathlib import Path

class AtomPositionLoader:
    """
    Lazily loads structural_file_readers modules on demand
    and dispatches read/export calls via the `.read()` and `.export()` methods.

    The `.read(source, file_location)` method auto-detects the source format
    by extension if `source` is None. After reading, the loader populates protected
    `_attr` fields and only publicly sets attributes that are not defined as properties.
    """

    def __init__(self, file_location: str = None, name: str = None, **kwargs):
        self.name = name
        self.file_location = file_location
        self._reader = None

        # Mapping: format key -> (class_name, export_method, read_method)
        self._source_map = {
            'CIF':    ('CIF',    'export_as_CIF',   'read_CIF'),
            'POSCAR': ('POSCAR', 'export_as_POSCAR', 'read_POSCAR'),
            'XYZ':    ('XYZ',    'export_as_xyz',    'read_XYZ'),
            'SI':     ('SI',     'export_as_SI',     'read_SI'),
            'PDB':    ('PDB',    'export_as_PDB',    'read_PDB'),
            'ASE':    ('ASE',    'export_as_ASE',    'read_ASE'),
            'AIMS':   ('AIMS',   'export_as_AIMS',   'read_AIMS'),
            'GEN':    ('GEN',    'export_as_GEN',    'read_GEN'),
            'DUMP':   ('DUMP',   'export_as_DUMP',   'read_DUMP'),
            'LAMMPS': ('LAMMPS','export_as_LAMMPS', 'read_LAMMPS'),
        }
        # File extension -> format key map
        self._ext_map = {
            'cif': 'CIF', 'poscar': 'POSCAR', 'vasp': 'POSCAR',
            'xyz': 'XYZ', 'si': 'SI', 'pdb': 'PDB', 'ase': 'ASE',
            'aims': 'AIMS', 'gen': 'GEN', 'dump': 'DUMP',
            'lmp': 'LAMMPS', 'lammpstrj': 'LAMMPS'
        }

    @lru_cache(maxsize=None)
    def _get_reader_class(self, source: str):
        key = source.upper()
        if key not in self._source_map:
            raise ValueError(f"Unknown source format '{source}'")
        class_name, _, _ = self._source_map[key]
        module_path = (
            "sage_lib.IO.structure_handling_tools.structural_file_readers."
            f"{class_name}"
        )
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            sys.stderr.write(f"Error importing module {module_path}: {e}\n")
            return None
        if not hasattr(module, class_name):
            sys.stderr.write(f"Module '{module_path}' has no class '{class_name}'\n")
            return None
        return getattr(module, class_name)

    # ------------------------------------------------------------------
    def _inject_state(self, target):
        """
        Copy all loader fields to *target*.
        For names that start with “_”, first try the public
        property (self.attr) and pass that value on.
        Both aliases (_attr / attr) end up in *target*.
        """
        skip = {'_reader', 'name', 'file_location'}

        for key, val in self.__dict__.items():
            if key in skip or key.startswith('__'):
                continue

            if key.startswith('_') and key[1:] in [
                'uniqueAtomLabels', 
                'atomCount', 
                'atomLabelsList', 
                'atomPositions', 
                'latticeVectors',
                'timestep',
                'scaleFactor',
                'selectiveDynamics',
                'atomCoordinateType',
                'atomicConstraints',
                'latticeParameters',
                'latticeAngles',
                'E',
                'time',
                ]:

                pub = key[1:]
                # try self.attr (may trigger a property getter)
                val = getattr(self, pub, val)
                try:
                    setattr(target, pub, val)          # via setter if any
                except (AttributeError, TypeError):
                    target.__dict__[pub] = val         # read-only property
                target.__dict__[key] = val             # keep _attr alias
            else:
                # plain name first
                try:
                    setattr(target, key, val)
                except (AttributeError, TypeError):
                    target.__dict__[key] = val
                # add the protected twin
                target.__dict__.setdefault(f'_{key}', val)

        if isinstance(target, self._get_reader_class('PDB')):
            target.connection_list = self.get_connection_list(periodic=False)

    def read(self, source: str | None = None, file_location: str | None = None, **kwargs):
        """
        Detect format (if `source` is None), load file, cache the reader,
        and expose its attributes on the loader.
        """
        file_loc = file_location or self.file_location
        if not file_loc:
            raise ValueError("file_location must be specified for reading.")

        fmt_key = (source.upper() if source
                   else self._ext_map.get(Path(file_loc).suffix.lstrip('.').lower()))
        if not fmt_key:
            raise ValueError(f"Cannot detect format for '{file_loc}'")

        ReaderClass = self._get_reader_class(fmt_key)
        if ReaderClass is None:
            raise RuntimeError(f"Failed to import reader class for '{fmt_key}'")

        reader = ReaderClass(name=self.name, file_location=file_loc)
        _, _, read_method = self._source_map[fmt_key]
        if not hasattr(reader, read_method):
            raise AttributeError(f"{ReaderClass.__name__} lacks '{read_method}'")

        result = getattr(reader, read_method)(file_loc, **kwargs)

        # cache & expose reader’s state
        self._reader = reader
        for k, v in reader.__dict__.items():
            setattr(self, f"_{k}", v)
            if not isinstance(getattr(type(self), k, None), property):
                setattr(self, k, v)

        return result

    def export(self, fmt: str, file_location: str | None = None, **kwargs):
        """
        Create a fresh writer of type `fmt`, inject current state, call its exporter.
        """
        file_loc = file_location or self.file_location
        fmt_key = fmt.upper()

        WriterClass = self._get_reader_class(fmt_key)
        if WriterClass is None:
            raise ValueError(f"Writer class for '{fmt_key}' not found.")

        writer = WriterClass(name=self.name, file_location=file_loc)
        self._inject_state(writer)
        export_method = self._source_map[fmt_key][1]
        if not hasattr(writer, export_method):
            raise AttributeError(f"{WriterClass.__name__} lacks '{export_method}'")

        return getattr(writer, export_method)(file_loc, **kwargs)

    # ------------------------------------------------------------------
    # dynamic helpers (read_<fmt>, export_as_<fmt>, export_<fmt>)
    # ------------------------------------------------------------------
    def __getattr__(self, attr):
        # ------ read_<FMT> -------------------------------------------------
        if attr.startswith('read_'):
            fmt_key = attr.split('_', 1)[1].upper()
            if fmt_key in self._source_map:
                def _reader(file_location=None, **kw):
                    res = self.read(fmt_key, file_location=file_location, **kw)
                    if hasattr(self, 'group_elements_and_positions'):
                        self.group_elements_and_positions()
                    return res
                return _reader

        # ------ export_as_<FMT> -------------------------------------------
        if attr.startswith('export_as_'):
            fmt_key = attr.split('_', 2)[2].upper()
            if fmt_key in self._source_map:
                def _exporter(file_location=None, **kw):
                    return self.export(fmt_key, file_location=file_location, **kw)
                return _exporter

        # ------ export_<FMT> ----------------------------------------------
        if attr.startswith('export_') and not attr.startswith('export_as_'):
            fmt_key = attr.split('_', 1)[1].upper()
            if fmt_key in self._source_map:
                def _exp(file_location=None, **kw):
                    return self.export(fmt_key, file_location=file_location, **kw)
                return _exp

        raise AttributeError(f"{self.__class__.__name__} has no attribute '{attr}'")

