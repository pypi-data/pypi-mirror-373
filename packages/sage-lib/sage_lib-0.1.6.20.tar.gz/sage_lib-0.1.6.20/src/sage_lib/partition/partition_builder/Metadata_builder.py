try:
    import numpy as np
    from typing import List, Tuple, Optional, Dict
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sklearn.manifold: {str(e)}\n")
    del sys

class Metadata_builder(BasePartition):
    def __init__(self, *args, **kwargs):
        """
        """
        self.property_info = None
        self.composition_data = None
        self.energy_data = None
        self.area_data = None
        self.lattice_data = None

        super().__init__(*args, **kwargs)

    def handle_metadata(self, values: Dict[str, bool], file_location: str = None, save_to_file: bool = True, verbose: bool = True) -> str:
        """
        Export atomistic information in the XYZ format.

        This function generates a string representation of the atomistic information in XYZ format and optionally
        saves it to a file. It dynamically determines which properties (lattice, species, energy) to include based
        on the provided `values` dictionary.

        Parameters:
            values (Dict[str, bool]): Dictionary indicating which properties to include (e.g., lattice, species, energy).
            file_location (str): The location where the XYZ file will be saved. If not provided, defaults to `self.file_location`.
            save_to_file (bool): Flag to control whether to save the XYZ content to a file.
            verbose (bool): Flag to print additional information, if True.

        Returns:
            str: The generated XYZ content as a string.
        """
        # Set default file location if not provided
        file_location = file_location if file_location else (self.file_location + 'metadata.dat' if isinstance(self.file_location, str) else None)

        # Determine which properties to include in the XYZ file
        include_lattice = values.get('lattice', True)
        include_species = values.get('species', True)
        include_energy = values.get('energy', True)

        # Extract composition data
        composition_data = self.get_composition_data(values.get('verbose', True))

        # Prepare the header for the XYZ content
        header_parts = []
        if include_lattice:
            header_parts += [f'l{n}' for n in range(9)] 
        if include_species:
            header_parts.append(','.join(composition_data['uniqueAtomLabels']))
        if include_energy:
            header_parts.append('E')
        header = ','.join(header_parts)

        # Prepare the body of the XYZ content
        body = []
        for c_i in range(len(self.containers)):
            line = []
            if include_lattice:
                line.append(','.join(map(str, self.lattice_data[c_i, :])))
            if include_species:
                line.append(','.join(map(str, self.composition_data[c_i, :])))
            if include_energy:
                line.append(str(self.energy_data[c_i]))
            body.append(','.join(line))

        # Combine header and body to create the complete XYZ content
        metadata_content = header + '\n' + '\n'.join(body)

        # Save the content to a file if required
        if save_to_file and file_location:
            with open(file_location, 'w') as f:
                f.write(metadata_content)
            if verbose:
                print(f"METADATA content saved to {file_location}")

        return metadata_content


