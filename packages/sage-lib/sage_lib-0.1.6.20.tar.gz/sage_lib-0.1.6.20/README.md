sage_lib

Overview

sage_lib is a versatile library designed for advanced scientific computations and visualization. It enables users to process atomic structures, perform thermodynamic analyses, generate band structures, and handle various tasks commonly required in quantum mechanical and molecular dynamics studies. The primary focus of this library is to simplify complex workflows, enabling researchers to conduct simulations, generate graphical representations, and export data in multiple formats with ease.

Features

Atomic Position Export: Converts atomic position files from one format to another, making data compatible with different simulation tools or visualization software.

Plot Generation: Generates plots based on simulation data, such as band structures or molecular arrangements. This includes support for visualizing results from popular tools like VASP.

Thermodynamic Analysis: Provides methods to calculate thermodynamic properties based on ab initio data. This includes phase diagrams, ensemble analysis, and more.

Blender Integration for Rendering: Uses Blender to render atomic structures and molecular arrangements. Supports customization like resolution, camera angles, and the addition of fog effects.

Dynamic Molecular Analysis: Analyzes molecular dynamics data, tracking species counts, evaluating force fields, and computing properties such as diffusion coefficients and bond distances.

Configuration Generation and Editing: Reads atomic structures and configurations, applies specified editing operations, and exports new structures. This includes operations like creating supercells, rattling atomic positions, and applying compressions.

Solvent Environment Generation: Creates a solvent environment around a given molecular or atomic structure, supporting various solvents and configurations to simulate realistic environments.

Dimer Search and Analysis: Facilitates dimer search to analyze interactions between specific pairs of atoms, which is useful for studying catalytic activity and other atomic-scale interactions.

Surface Disassembly: Generates configurations that allow the disassembly of surfaces, which is particularly useful for understanding surface stability and catalysis.

Customizable File Management: Provides functionalities for handling, reading, and exporting files in different formats including VASP, XYZ, and others.

Installation

To install sage_lib, use the following command:

pip install sage_lib

Ensure that you have Python 3.7 or higher.

Usage

sage_lib can be used from the command line or programmatically.

Command Line Usage

The library includes a console command sage which can be used to execute various subcommands:

sage export --path ./data --source VASP --output_path ./converted --output_source PDB

This command will convert atomic position files from VASP format to PDB format, saving the output in the ./converted directory.

Another example for generating a plot:

sage plot --path ./data --plot bands --fermi 5.0 --output_path ./plots

This command generates a band structure plot using the data found in the specified directory.

Programmatic Usage

Below is a Python example that demonstrates how to use sage_lib programmatically:

from sage_lib.partition import Partition

# Initialize a Partition object
PT = Partition(path='./data')

# Read files from a specified location
PT.read_files(file_location='./data', source='VASP', verbose=True)

# Export files in a different format
PT.export_files(file_location='./output', source='PDB', verbose=True)

This example initializes a Partition object, reads files from a directory, and exports them to a different format.

Dependencies

sage_lib requires the following packages:

numpy: for numerical operations

matplotlib: for plotting and visualization

scipy: for scientific computations

imageio: for managing image files

Optional dependencies include:

pytest: for testing

flake8: for code linting

sphinx: for generating documentation

License

sage_lib is licensed under the MIT License. For more details, refer to the LICENSE file.

Contributing

Contributions are welcome! Please feel free to open an issue or a pull request on the GitHub repository to contribute to the project.

Contact

For questions, please contact the author via email: lombardi@fhi-berlin.mpg.de

For bug reports or feature requests, visit the issues page.

