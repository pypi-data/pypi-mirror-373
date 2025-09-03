
from __future__ import annotations
import importlib

"""
Examples:
    # Generate XYZ from OUTCAR
    generate_from_outcar("/path/to/OUTCAR", source='VASP', subfolders=True, verbose=True)

    # Generate configurations with vacancies
    generate_vacancy("/path/to/VASP_files")

    # Generate configurations for disassembling a surface
    generate_disassemble_surface("/path/to/VASP_files", steps=5, final_distance=10.0)

    # Generate dimer configurations
    generate_dimers("/path/to/VASP_files", labels=['C', 'O'], steps=10, vacuum=15.0)

    # Generate VASP partition and execution script
    generate_config("/path/to/VASP_files", config_path="/path/to/config", output_path="/path/to/output")

    # Generate band calculation files
    generate_band_calculation("/path/to/VASP_files", points=100, special_points='GMMLLXXG')

Note:
    - The 'sage_lib' package is primarily designed for use with VASP simulation data.
    - It is recommended to have a thorough understanding of DFT and materials simulation before using this package.
    - Ensure all paths provided to the functions are absolute paths.

Attributes:
    - Comprehensive support for various stages of simulation: setup, execution, and analysis.
    - Integration with VASP for efficient management of simulation data.
    - Versatile tools for creating, modifying, and analyzing simulation data.

Todo:
    - Expand support for other simulation software beyond VASP.
    - Implement more advanced data analysis tools for post-simulation analysis.
    - Enhance the user interface for ease of use in an interactive environment.

Authors:
    Dr. Juan Manuel Lombardi
    Fritz-Haber-Institut der Max-Planck-Gesellschaft
    Contact: lombardi@fhi-berlin.mpg.de
"""

# ==== Import statements for key modules ==== # 
"""
sage_lib - Advanced Scientific Simulations and Data Processing

This package provides tools for setting up, executing, and analyzing simulations in computational physics and materials science, focusing on DFT and force-field methods.

Modules:
- `partition`: Core functionalities for managing simulation partitions and configurations.
- `IO`: Tools for handling input/output files, including atomic positions, eigenvalues, and DOS data.
- `single_run`: Manage individual simulation runs.
- `ensemble`: Tools for ensemble simulations.
- `miscellaneous`: General-purpose utilities and tools.
- `test`: Testing tools for validating implementations.
"""

_lazy_imports = {
    "np": ("numpy", None),
    "plt": ("matplotlib.pyplot", None),
    "LinearSegmentedColormap": ("matplotlib.colors", "LinearSegmentedColormap"),
    "tqdm": ("tqdm", None),
    "os": ("os", None),
    "datetime": ("datetime", None),
    "KFold": ("sklearn.model_selection", "KFold"),
    "StandardScaler": ("sklearn.preprocessing", "StandardScaler"),
    "KMeans": ("sklearn.cluster", "KMeans"),
    "DBSCAN": ("sklearn.cluster", "DBSCAN"),
    "HDBSCAN": ("hdbscan", "HDBSCAN"),
    "AgglomerativeClustering": ("sklearn.cluster", "AgglomerativeClustering"),
    "MiniBatchKMeans": ("sklearn.cluster", "MiniBatchKMeans"),
    "GaussianMixture": ("sklearn.mixture", "GaussianMixture"),
    "mean_squared_error": ("sklearn.metrics", "mean_squared_error"),
    "silhouette_score": ("sklearn.metrics", "silhouette_score"),
    "calinski_harabasz_score": ("sklearn.metrics", "calinski_harabasz_score"),
    "davies_bouldin_score": ("sklearn.metrics", "davies_bouldin_score"),
    "r2_score": ("sklearn.metrics", "r2_score"),
    "mean_absolute_error": ("sklearn.metrics", "mean_absolute_error"),
    "mean_absolute_percentage_error": ("sklearn.metrics", "mean_absolute_percentage_error"),
    "NearestNeighbors": ("sklearn.neighbors", "NearestNeighbors"),
    "PCA": ("sklearn.decomposition", "PCA"),
    "FactorAnalysis": ("sklearn.decomposition", "FactorAnalysis"),
    "TSNE": ("sklearn.manifold", "TSNE"),
    "umap": ("umap", None),
    "torch": ("torch", None),
    "pdist": ("scipy.spatial.distance", "pdist"),
    "squareform": ("scipy.spatial.distance", "squareform"),
    "stats": ("scipy", None),
    "spearmanr": ("scipy.stats", "spearmanr"),
    "gaussian_kde": ("scipy.stats", "gaussian_kde"),
    "KneeLocator": ("kneed", "KneeLocator"),
    "Dict": ("typing", "Dict"),
    "List": ("typing", "List"),
    "Tuple": ("typing", "Tuple"),
    "Union": ("typing", "Union"),
    "Optional": ("typing", "Optional"),
    "Any": ("typing", "Any"),
    "joblib": ("joblib", None),
}

def __getattr__(name):
    if name in _lazy_imports:
        module_name, attr_name = _lazy_imports[name]
        mod = importlib.import_module(module_name)
        value = getattr(mod, attr_name) if attr_name is not None else mod
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__} has no attribute {name}")

# === Initialization Function ===
def initialize_sage_lib(verbose: bool = False):
    """
    Initialize the Sage library with optional configurations.

    Parameters:
    - verbose (bool): If True, prints initialization details.
    """
    if verbose:
        print(f"Initializing Sage Library (v{__version__}) - Advanced tools for materials science simulations.")



# Any initialization code your package requires 
global_seed = 42

#__all__ = ["Partition", "OutFileManager", "DFTSingleRun", "CrystalDefectGenerator"]

# Código de inicialización, si es necesario
def initialize_sage_lib():
    print("Inicializando sage_lib...")


# Version of the sage_lib package
__version__ = "0.1.5.31"

# Author of the package
__author__ = "Juan Manuel Lombardi"

# License of the package
__license__ = "MIT"

# End of __init__.py

