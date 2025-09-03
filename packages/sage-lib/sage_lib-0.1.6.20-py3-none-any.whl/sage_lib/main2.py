import argparse
import os
from sage_lib.partition.Partition import Partition 
from sage_lib.IO.structure_handling_tools.AtomPosition import AtomPosition 
from sage_lib.IO.EigenvalueFileManager import EigenvalueFileManager 
from sage_lib.IO.DOSManager import DOSManager 

from sage_lib.IO.OutFileManager import OutFileManager 

def generate_defects(path:str, source:str=None, forces_tag:str=None, energy_tag:str=None, subfolders:bool=False, conteiner_index:int=None, output_path:str=None, output_source:str=None, verbose:bool=False,  
                    species:list=None, new_species:list=None, defect:str=None, 
                    distribution:str=None, fill:bool=None, atom_groups:list=None, group_numbers:list=None, repetitions:bool=None,
                    iterations:int=None):
    """
    Generate configurations with vacancies for computational chemistry simulations.

    Parameters:
    - path (str): Path to the directory containing input files.
    - source (str, optional): Type of source files, default is 'VASP'.
    - subfolders (bool, optional): Flag to include subdirectories in the search.
    - verbose (bool, optional): If True, prints additional information during execution.

    Uses the Partition class from the sage_lib to read, process, and generate
    DFT (Density Functional Theory) variants with vacancies.
    """
    # Initialize a Partition object with the given path
    PT = Partition(path)
    # Read files and generate DFT variants with vacancies
    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)

    #PT.generate_variants('DEFECTS', values= [ {'defect':defect, 'species':species, 'new_species':new_species} ] )
    
    values = {  'iterations': iterations, 
                'repetitions': repetitions,
                'distribution':distribution, 
                'fill':fill, 
                'atom_groups':atom_groups, 
                'group_numbers':group_numbers}
                
    PT.generate_configurational_space(values=values, verbose=verbose) 
    
    # Export the generated files back to the specified path
    PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

def generate_disassemble_surface(path, steps=5, final_distance=5.0, atoms_to_remove=None, subfolders=False, verbose=False):
    """
    Generate configurations for disassembling the surface.

    Parameters:
    - path (str): Path to the VASP files directory.
    - steps (int): Number of steps in the disassembly process.
    - final_distance (float): Final distance between layers or atoms.
    - atoms_to_remove (int or None): Specific number of atoms to remove.
    - verbose (bool): If True, prints additional information.
    """
    SSG = SurfaceStatesGenerator(path)
    read_files(partition=SSG, path=path, subfolders=subfolders)

    SSG.generate_disassemble_surface(steps=steps, final_distance=final_distance, atoms_to_remove=atoms_to_remove)
    SSG.exportVaspPartition()

def generate_dimers(path: str = None, source: str = None, forces_tag:str=None, energy_tag:str=None, subfolders: bool = None, 
                    labels: list = None, steps: int = 10, initial_distance: float = None, final_distance: float = None, 
                    vacuum_tolerance: float = 18.0, 
                    output_path: str = None, output_source: str = None, conteiner_index:int=None, verbose: bool = False):
    """
    Generate configurations for a dimer search in a computational chemistry context.

    This function is designed to set up and export multiple configurations of dimers (pairs of atoms or molecules) 
    based on specified parameters. It is useful in simulations where interactions between two specific atoms or molecules
    are of interest, particularly in the context of Density Functional Theory (DFT) or similar computational methods.

    Parameters:
    - path (str, optional): Path to the directory containing the initial data files.
    - source (str, optional): Source type of the initial data files (e.g., 'VASP', 'xyz').
    - subfolders (bool, optional): Flag to include subfolders in the search for data files.
    - labels (list of str, optional): List of atom labels to include in the dimer search. 
      For example, ['O', 'H'] to create dimers involving oxygen and hydrogen.
    - steps (int, optional): Number of iterative steps in the generation process. 
      Determines the granularity of the dimer configuration changes (default: 10).
    - initial_distance (float, optional): Initial distance between atoms in the dimer configuration.
    - final_distance (float, optional): Final distance after configuration adjustments.
    - vacuum_tolerance (float, optional): The vacuum distance around the dimer structure (default: 18.0 Ångströms).
    - output_path (str, optional): Path for exporting the generated dimer configuration files.
    - output_source (str, optional): Format for exporting the files (e.g., 'VASP', 'POSCAR').
    - verbose (bool, optional): If set to True, enables verbose output for debugging purposes.

    The function initializes a Partition object, reads files, generates dimer variants with specified distances,
    and exports the files to the specified output path. It utilizes the Partition class's methods to handle
    the file operations and variant generations.

    Example Usage:
    generate_dimers(path='./data', source='VASP', labels=['H', 'O'], steps=5, 
                    initial_distance=0.7, final_distance=1.5, output_path='./output', output_source='VASP')
    """
    # Initialize the Partition object with the given path
    PT = Partition(path)

    # Read files from the specified location, considering subfolders if specified
    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)

    # Generate dimer variants based on the provided parameters
    PT.handleDimers(values=[{'AtomLabels': labels, 'initial_distance': initial_distance, 
                                    'final_distance': final_distance, 'steps': steps, 
                                    'vacuum_tolerance': vacuum_tolerance}], 
                    file_location=output_path)

    # Export the generated files to the specified output location and format
    PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

def generate_config(path: str = None, source: str = None, forces_tag:str=None, energy_tag:str=None, subfolders: bool = None, 
                    config_path: str = None, config_source: str = None, 
                    output_path: str = None, output_source: str = None, verbose: bool = False):
    """
    Generates a configuration by reading, processing, and exporting files.

    This function orchestrates the workflow of partitioning data, reading configuration setup, 
    and exporting files with enumeration. It provides verbose output for debugging and tracking.

    Parameters:
    - path (str): Path to the data files.
    - source (str): Source identifier for the data files.
    - subfolders (bool): Flag to include subfolders in the data reading process.
    - config_path (str): Path to the configuration setup files.
    - config_source (str): Source identifier for the configuration files.
    - output_path (str): Path for exporting the processed files.
    - output_source (str): Source identifier for the exported files.
    - verbose (bool): Flag for verbose output.

    Returns:
    None
    """

    PT = Partition(path)
    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)
    PT.read_Config_Setup(file_location=config_path, source=config_source, verbose=verbose)
    PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

    if verbose:
        print(f">> Config generated successfully.")
        print(f"Position: {path}({source})(subfolders: {subfolders}) + \n InputFiles: {config_path}({output_path}) >> Output: \n {output_path}({output_source})")

def generate_band_calculation(path:str, points:int, special_points:str, source:str=None, subfolders:bool=False, output_path:str=None, verbose:bool=False):
    """
    Generate and export band structure calculation files.

    This function creates the necessary files for performing band structure calculations using Density Functional Theory (DFT) data. It sets up the calculation parameters and exports them in a format suitable for VASP.

    Parameters:
    path (str): Path to the directory containing VASP files.
    points (int): Number of k-points in each segment of the band path.
    special_points (str): String representing high-symmetry points in the Brillouin zone.
    source (str, optional): Source of the files (default is None, typically set to 'VASP').
    subfolders (bool, optional): Whether to include subfolders in the search (default False).
    output_path (str, optional): Directory path where the output files will be saved.
    verbose (bool, optional): If True, provides detailed output during execution.

    Returns:
    None
    """
    DP = Partition(path)
    read_files(partition=DP, path=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)

    DP.generate_variants('band_structure', values=[{'points':points, 'special_points':special_points}])
    DP.exportVaspPartition()

def generate_json_from_bands(path:str, fermi:float, source:str=None, forces_tag:str=None, energy_tag:str=None, subfolders:bool=False, output_path:str=None, verbose:bool=False):
    """
    Generate a JSON file from band structure data.

    This function reads the band structure data from VASP output files, processes it, and exports it to a JSON file. This is useful for further analysis or visualization of the band structure.

    Parameters:
    path (str): Path to the directory containing VASP files.
    fermi (float): Fermi level energy. If not provided, it will be read from the DOSCAR file.
    source (str, optional): Source of the files ('VASP' is a common option).
    subfolders (bool, optional): Whether to include subfolders in the search (default False).
    output_path (str, optional): Directory path where the JSON file will be saved.
    verbose (bool, optional): If True, provides detailed output during execution.

    Returns:
    None
    """
    if source.upper() == 'VASP':
        # read fermi level from DOSCAR
        if fermi is None:
            # === read DOCAR === #
            DM = DOSManager(path + "/DOSCAR")
            DM.read_DOSCAR()
            fermi = DM.fermi

        # === read POSCAR === #
        PC = AtomPosition(path + "/POSCAR")
        PC.read_POSCAR()
        cell = PC.latticeVectors

        # === read EIGENVAL === #
        EFM = EigenvalueFileManager(file_location=path + "/EIGENVAL", fermi=fermi, cell=cell)
        EFM.read_EIGENVAL()

    EFM.export_as_json(output_path+'/band_structure.json')

def generate_export_files(path:str, source:str=None, forces_tag:str=None, energy_tag:str=None,
                        subfolders:bool=False, output_path:str=None, output_source:str=None, verbose:bool=False, bond_factor:float=None):
    """
    Export atomic position files from a specified source format to another format.

    This function is used to convert the format of atomic position files, which is often necessary for compatibility with different simulation tools or visualization software.

    Parameters:
    path (str): Path to the directory containing source format files.
    source (str, optional): Source format of the files (e.g., 'VASP').
    subfolders (bool, optional): Whether to include subfolders in the search (default False).
    output_path (str, optional): Directory path where the converted files will be saved.
    output_source (str, optional): Target format for exporting (e.g., 'PDB').
    verbose (bool, optional): If True, provides detailed output during execution.

    Returns:
    None
    """
    PT = Partition(path)
    PT.read_files( file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)
    PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

def generate_plot(path:str, source:str=None, forces_tag:str=None, energy_tag:str=None, subfolders:bool=False, output_path:str=None, 
                    plot:str=None, verbose:bool=False, conteiner_index:int=None,
                    fermi:float=None, emin:float=None, emax:float=None,
                    cutoff:float=None, number_of_bins:int=None):
    """
    Generate plots from simulation data.

    This function processes simulation data and generates plots, such as band structure or molecular structures, based on the data and specified plot type.

    Parameters:
    path (str): Path to the directory containing the simulation data files.
    source (str, optional): Source of the files (e.g., 'VASP').
    subfolders (bool, optional): Whether to include subfolders in the search (default False).
    output_path (str, optional): Directory path where the plots will be saved.
    plot (str, optional): Type of plot to generate (e.g., 'band').
    verbose (bool, optional): If True, provides detailed output during execution.
    fermi (float, optional): Fermi level energy, important for certain types of plots.

    Returns:
    None
    """
    output_path = output_path if output_path is not None else '.'
    PT = Partition(path)
    PT.read_files( file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)

    if plot.upper() == 'BANDS':
        if fermi is None:
            # === read DOCAR === #
            DM = DOSManager(path + "/DOSCAR")
            DM.read_DOSCAR()
            fermi = DM.fermi

        # === read EIGENVAL === #
        EFM = EigenvalueFileManager(file_location=path+"/EIGENVAL", fermi=fermi )
        EFM.read_EIGENVAL()

        EFM.plot(subtract_fermi=True, save=True, emin=emin, emax=emax)

    elif plot.upper() == 'RBF':
        if isinstance(conteiner_index,int): 
            file_location = output_path+f'/frame{conteiner_index}'
            PT.create_directories_for_path(file_location)
            PT.containers[conteiner_index].AtomPositionManager.plot_RBF(periodic_image=0, cutoff=cutoff, number_of_bins=number_of_bins, output_path=file_location,
                                                        bin_volume_normalize=True, number_of_atoms_normalize=True, density_normalize=True)
        else:
            for conteiner_index, conteiner in enumerate(PT.containers):
                file_location = output_path+f'/frame{conteiner_index}'
                PT.create_directories_for_path(file_location)
                conteiner.AtomPositionManager.plot_RBF(periodic_image=0, cutoff=cutoff, number_of_bins=number_of_bins, output_path=file_location,
                                                        bin_volume_normalize=True, number_of_atoms_normalize=True, density_normalize=True)

def generate_MD(path:str, source:str=None, subfolders:bool=False, forces_tag:str=None, energy_tag:str=None, output_path:str=None, output_source: str = None,
                    plot:str=None, reference:str=None, ff_energy_tag:str=None, ff_forces_tag:str=None, sigma:float=None, topology:str=None, wrap:bool=None,
                    verbose:bool=False, conteiner_index:int=None, tranparency:bool=None, bins:int=None, save:bool=None):
    """
    Generate plots from simulation data.

    This function processes simulation data and generates plots, such as band structure or molecular structures, based on the data and specified plot type.

    Parameters:
    path (str): Path to the directory containing the simulation data files.
    source (str, optional): Source of the files (e.g., 'VASP').
    subfolders (bool, optional): Whether to include subfolders in the search (default False).
    output_path (str, optional): Directory path where the plots will be saved.
    plot (str, optional): Type of plot to generate (e.g., 'band').
    verbose (bool, optional): If True, provides detailed output during execution.
    fermi (float, optional): Fermi level energy, important for certain types of plots.

    Returns:
    None
    """
    # 'count_species', 'displacements', 'RBF', 'evaluate_ff', 'bond_distance_tracking', 'molecule_formation_tracking'
    output_path = output_path if output_path is not None else '.'
    PT = Partition(path)
    PT.read_files( file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)

    if plot.upper() == 'PATH_TRACKING':
        PT.handleMDAnalysis( values= {'PATH_TRACKING':{'wrap':wrap, 'tranparency':tranparency, 'bins':bins, 'verbose':verbose, 'save':save} }  )

    elif plot.upper() == 'RBF':
        PT.handleMDAnalysis( values= {'RBF':{'output_path':output_path, 'verbose':verbose} }  )

    elif plot.upper() == 'COUNT_SPECIES':
        PT.handleMDAnalysis( values= {'COUNT_SPECIES':{'output_path':output_path, 'verbose':verbose, 'sigma':sigma} }  )

    elif plot.upper() == 'EVALUATE_FF':
        PT.handleMDAnalysis( values= {'EVALUATE_FF':{'output_path':output_path, 'ff_energy_tag':ff_energy_tag, 'ff_forces_tag':ff_forces_tag, 'verbose':verbose} }  )

    elif plot.upper() == 'BOND_DISTANCE_TRACKING':
        PT.handleMDAnalysis( values= {'BOND_DISTANCE_TRACKING':{'reference':reference, 'sigma':sigma, 'output_path':output_path, 'verbose':verbose} }  )
    
    elif plot.upper() == 'MOLECULE_FORMATION_TRACKING':
        PT.handleMDAnalysis( values= {'MOLECULE_FORMATION_TRACKING':{'sigma':sigma, 'topology':topology, 'verbose':verbose} }  )
        PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

def generate_AbInitioThermodynamics(path:str, source:str=None, subfolders:bool=False, forces_tag:str=None, energy_tag:str=None, output_path:str=None, 
                plot:str=None, reference_ID:list=None, especie:str=None, mu_max:float=None, mu_min:float=None,
                verbose:bool=False, conteiner_index:int=None):
    """
    .
    """
    output_path = output_path if output_path is not None else '.'
    PT = Partition(path)
    PT.read_files( file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)
    
    if plot.upper() == 'PHASE_DIAGRAM':
        PT.handleABITAnalysis( values= {'phase_diagram':{'reference_ID':reference_ID, 'especie':especie, 'mu_max':mu_max, 'mu_min':mu_min, 
                                                        'output_path':output_path, 'verbose':verbose} }  )

def generate_edit_positions(path: str, source: str = None, forces_tag:str=None, energy_tag:str=None, subfolders: bool = False, output_path: str = None, 
                            output_source: str = None, verbose: bool = False, edit: str = None, N: int = None, direction:str=None, 
                            std: float = None, repeat: list = None, compress_min: list = None, compress_max: list = None,
                            init_index:int=None, mid_index:int=None, end_index:int=None, degree:int=None, first_neighbor:bool=None):
    """
    Modifies and exports atomic positions based on specified editing operations.

    This function applies various editing operations like 'rattle', 'supercell', or 'compress' to the atomic positions
    in the provided path and exports the modified structures.

    Parameters:
        path (str): Path to the input files.
        source (str, optional): Source type of the input files.
        subfolders (bool, optional): Flag to include subfolders in file reading.
        output_path (str, optional): Path for exporting the edited files.
        output_source (str, optional): Source type for exporting files.
        verbose (bool, optional): Enables verbose output.
        edit (str, optional): Type of editing operation ('rattle', 'supercell', 'compress').
        N (int, optional): Parameter specific to the 'rattle' and 'compress' edit.
        std (float, optional): Standard deviation parameter for the 'rattle' edit.
        repeat (list, optional): Repetition vector for the 'supercell' edit.
        compress_min (list, optional): Minimum compression factor for the 'compress' edit.
        compress_max (list, optional): Maximum compression factor for the 'compress' edit.
    
    Raises:
        ValueError: If required parameters for specific edits are not provided.
    """
    # Initialize the DFTPartition object
    PT = Partition(path)

    # Read files from the specified path
    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)

    # Apply the specified movement to the atomic positions
    if edit.lower() == 'rattle':
        # Ensure that N and std are provided for the 'rattle' move
        if N is None or std is None:
            raise ValueError("For the 'rattle' edit, both 'N' and 'std' parameters must be provided.")
        
        values = {'N': N, 'std': [std]}
        PT.containers = PT.handleRattle(values=values)
        PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

    elif edit.lower() == 'supercell':
        # Ensure that N and std are provided for the 'rattle' move
        if repeat is None:
            raise ValueError("For the 'supercell' edit, the 'repeat' parameter must be provided.") 

        for container in PT.containers:
            container.AtomPositionManager.generate_supercell(repeat=repeat)
            name  = '_'.join( [ str(r) for r in repeat ] )
            container.file_location += f'/{name}'
        PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

    elif edit.lower() == 'compress':
        #
        if compress_min is None and compress_max is None:
            raise ValueError("For the 'compress' edit, the 'compress_factor' parameter must be provided.") 

        PT.generate_variants(parameter='compress', values={'N': N, 'compress_min': compress_min, 'compress_max': compress_max} )
        PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

    elif edit.lower() == 'widening':
        #
        PT.containers = PT.handleWidening(values=[{'direction': direction, 'N':N, 'init_index': init_index, 'mid_index': mid_index, 'end_index': end_index}])
        PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

    elif edit.lower() == 'interpolation':
        ''' 
        '''
        value = {'images':N, 'degree':degree, 'first_neighbor':first_neighbor}
        PT.containers = PT.handleInterpolation(values=value)
        PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

def generate_edit_configuration(path:str, source:str=None, forces_tag:str=None, energy_tag:str=None, subfolders:bool=False, output_path:str=None, output_source:str=None, verbose:bool=False, edit:str=None,
                            atom_index:list=None, atom_ID:list=None, new_atom_ID:list=None, weights:list=None, N:int=None, search:str=None, seed:int=None):
    """
    Edits the configuration of atomic structures by changing atomic IDs and exports the modified structures.

    This function changes the IDs of atoms in the provided structures based on the specified edit operations and 
    then exports these modified structures to the defined output path.

    Parameters:
        path (str): Path to the input files.
        source (str, optional): Source type of the input files.
        subfolders (bool, optional): Flag to include subfolders in file reading.
        output_path (str, optional): Path for exporting the edited files.
        output_source (str, optional): Source type for exporting files.
        verbose (bool, optional): Enables verbose output.
        edit (str, optional): Type of editing operation ('ATOM_ID').
        atom_ID (list, optional): Original atom ID to be changed.
        new_atom_ID (list, optional): New atom ID to replace the original.
        weights (list, optional): New atom wrights probabilities to replace the original.
    Raises:
        ValueError: If required parameters for specific edits are not provided.
    """

    # Initialize the DFTPartition object
    PT = Partition(path)

    # Read files based on provided parameters
    PT.read_files( file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)

    values = {
        'search': search,
        'atom_index': atom_index,
        'atom_ID': atom_ID,
        'new_atom_ID': new_atom_ID,
        'N': N,
        'weights':weights,
        'seed':seed,
        'verbose':verbose
                }

    PT.handleAtomIDChange( values={f'{edit}':values} )

    # Export the edited files
    PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

def generate_filter(path:str, source:str=None, forces_tag:str=None, energy_tag:str=None, subfolders:bool=False, output_path:str=None, output_source:str=None, verbose:bool=False, 
                    filter_class:str=None, container_property:str=None, filter_type:str=None, value:float=None, ID:str=None, traj:bool=False, N:int=None):
    """
    Filters atomic structures based on specified criteria and exports the filtered structures.

    This function applies filtering operations to atomic structures based on various properties like class,
    type, value, etc., and then exports these filtered structures to the defined output path.

    Parameters:
        path (str): Path to the input files.
        source (str, optional): Source type of the input files.
        subfolders (bool, optional): Flag to include subfolders in file reading.
        output_path (str, optional): Path for exporting the filtered files.
        output_source (str, optional): Source type for exporting files.
        verbose (bool, optional): Enables verbose output.
        filter_class (str, optional): Class of filter to apply.
        container_property (str, optional): Property of the container to filter by.
        filter_type (str, optional): Type of filter to apply.
        value (float, optional): Value threshold for filtering.
        ID (str, optional): Specific ID to filter by.
        traj (bool, optional): Flag to indicate trajectory filtering.
        N (int, optional): Number of structures to select.

    Raises:
        ValueError: If required parameters for specific filters are not provided.
    """
    # Initialize the DFTPartition object
    PT = Partition(path)

    # Read files and apply filters
    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)
    PT.filter_conteiners(filter_class=filter_class, container_property=container_property, filter_type=filter_type, 
                        value=value, traj=traj, selection_number=N, ID=ID, verbosity=verbose)

    # Export the filtered files
    PT.export_files(file_location=output_path, source=source, label='enumerate', verbose=verbose)

def generate_dataset(path:str, source:str=None, forces_tag:str=None, energy_tag:str=None, subfolders:bool=False, output_path:str=None, output_source:str=None, verbose:bool=False, conteiner_index:int=None, 
                    operation:str=None, ):
    """
    """
    # Initialize the DFTPartition object
    PT = Partition(path)

    # Read files and apply filters
    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)
    if operation.upper() == 'SORT':
        PT.handleDataset( values= {'sort':{'verbose':verbose} }  )

    # Export the filtered files
    PT.export_files(file_location=output_path, source=source, label='enumerate', verbose=verbose)


def generate_supercell_embedding(
                        unitcell_path:str=None,              unitcell_source:str=None, forces_tag:str=None, energy_tag:str=None,
                        relax_supercell_path:str=None,       relax_supercell_source:str=None, 
                        unrelax_supercell_path:str=None,     unrelax_supercell_source:str=None, 
                        output_path:str=None,                output_source:str=None, verbose:bool=False, ):
    """
    Generates a supercell embedding from given unitcell and supercell structures and exports the result.

    This function reads the unitcell and both relaxed and unrelaxed supercell structures, generates a supercell
    embedding by combining these structures, and then exports the embedded supercell.

    Parameters:
        unitcell_path (str): Path to the unitcell file.
        unitcell_source (str): Source type of the unitcell file.
        relax_supercell_path (str): Path to the relaxed supercell file.
        relax_supercell_source (str): Source type of the relaxed supercell file.
        unrelax_supercell_path (str): Path to the unrelaxed supercell file.
        unrelax_supercell_source (str): Source type of the unrelaxed supercell file.
        output_path (str, optional): Path for exporting the embedded supercell.
        output_source (str, optional): Source type for exporting the supercell.
        verbose (bool, optional): Enables verbose output.

    Raises:
        ValueError: If required parameters for embedding are not provided.
    """
    # Initialize the DFTPartition object
    PT = Partition(relax_supercell_path)

    # Read unitcell and supercell structures
    PT.read_unitcell(file_location=unitcell_path, source=unitcell_source)

    PT.read_defect_supercell_unrelax(file_location=unrelax_supercell_path, source=unrelax_supercell_source )
    PT.read_defect_supercell_relax(file_location=relax_supercell_path, source=relax_supercell_source )

   # Generate supercell embedding
    PT.make_supercell_embedding()

    # Export the embedded supercell
    PT.export_defect_supercell_unrelax_Np1(source=output_source, file_location=output_path)

def generate_solvent(path:str, source:str=None, forces_tag:str=None, energy_tag:str=None, subfolders:bool=False, conteiner_index:int=None, output_path:str=None, output_source:str=None, verbose:bool=False, 
                    density:float=None, solvent:list=None, slab:bool=None, 
                    shape:str=None, size:list=None, vacuum_tolerance:float=None, 
                    seed:float=None,
                    colition_tolerance:float=None, translation:list=None, wrap:bool=None):
    """
    Generates a solvent environment for molecular dynamics or quantum mechanics simulations.

    Parameters:
    - path (str): Path to the directory containing input files for the simulation.
    - source (str, optional): Source format of the input files (e.g., 'VASP', 'OUTCAR', etc.).
    - subfolders (bool, optional): If True, includes subfolders in the file search.
    - conteiner_index (int, optional): Index of the container to apply the solvent generation.
    - output_path (str, optional): Path for exporting the modified files with the solvent environment.
    - output_source (str, optional): Format for exporting the modified files (e.g., 'VASP', 'xyz').
    - verbose (bool, optional): If True, provides detailed output during execution.

    Solvent-related parameters:
    - density (float, optional): Density of the solvent, important for accurately modeling liquid environments.
    - solvent (list, optional): List of solvents to use (e.g., ['H2O', 'H2'] for water and hydrogen).
    - slab (bool, optional): Indicates whether the simulation involves a slab geometry, typically used in surface studies.
    - shape (str, optional): Shape of the simulation region ('box' or 'sphere').
    - size (list, optional): Dimensions of the simulation box (length, width, height), applicable if shape is 'box'.
    - vacuum_tolerance (float, optional): Tolerance for vacuum spaces in the simulation, usually in Angstroms.
    - colition_tolerance (float, optional): Collision tolerance, defining the minimum distance between atoms or molecules.
    - translation (list, optional): Translation vector for positioning the system within the simulation box.
    - wrap (bool, optional): If True, enables wrapping of atoms within the simulation boundaries, useful for periodic boundary conditions.

    This function initializes a DFTPartition object, reads files, applies solvent-related configurations,
    generates variants based on these configurations, and exports the results.
    """
    # Initialize the DFTPartition object
    PT = Partition()

    # Read files and apply configurations
    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)
    
    values = {
        'density': density,
        'solvent': solvent,
        'slab': slab,
        'shape': shape,
        'size': size,
        'vacuum_tolerance': vacuum_tolerance,
        'colition_tolerance': colition_tolerance,
        'translation': translation,
        'wrap': wrap,
        'seed':seed,
        'verbose':verbose
    }
    PT.handleCLUSTER( values= {'ADD_SOLVENT':values}  )

    # Export the modified files
    PT.export_files(file_location=output_path, source=output_source, label='enumerate', verbose=verbose)

def generate_BLENDER(path:str, source:str=None, subfolders:bool=False, forces_tag:str=None, energy_tag:str=None, output_path:str=None, 
                plot:str=None, resolution:list=None, samples:int=None, fog:bool=None, render:bool=False, 
                sigma:float=None, scale:float=None, camera:list=None, repeat:list=None, 
                verbose:bool=False, conteiner_index:int=None):

    # Initialize the DFTPartition object
    PT = Partition()

    # Read files and apply configurations
    PT.read_files(file_location=path, source=source, energy_tag=energy_tag, forces_tag=forces_tag, subfolders=subfolders, verbose=verbose)
    
    values = {
        'samples': samples,
        'resolution_x': resolution[0],
        'resolution_y': resolution[1],
        'fog': fog,
        'render':render,
        'sigma': sigma,
        'scale': scale,
        'camera': camera,
        'repeat': repeat,
        'verbose': verbose,
    }

    PT.handleBLENDER( values={f'{plot}':values}  )

def add_arguments(parser):
    """
    Adds common arguments to the given subparser. This includes arguments for file paths, 
    verbosity, and other common settings used across various sub-commands.
    """
    structure_list = ['VASP', 'OUTCAR', 'xyz', 'traj', 'cif', 'AIMS', 'gen', 'POSCAR', 'ASE', 'PDB', 'DUMP', 'LAMMPS']
    parser.add_argument('--path', type=str, default='.', help='Path to the files directory')
    parser.add_argument('--source', type=str, choices=structure_list, help='Source of calculation from which the files originate')
    parser.add_argument('--forces-tag', type=str, default='forces', help='Tag for forces data')
    parser.add_argument('--energy-tag', type=str, default='E', help='Tag for energy data')
    parser.add_argument('--output-path', type=str, default='.', help='Path for exporting VASP partition and scripts')
    parser.add_argument('--output-source', type=str, choices=structure_list, help='Source for exporting partition and scripts')
    parser.add_argument('--verbose', default=False, action='store_true', help='Display additional information')
    parser.add_argument('--subfolders', default=False, action='store_true', help='Read from all subfolders under the specified path')
    parser.add_argument('--container-index', type=int, help='Index of the container to process')

def parse_dynamic_groups(args):
    """
    Parses dynamic group arguments from the parsed arguments and returns atom groups and their counts.

    Parameters:
        args (argparse.Namespace): The parsed arguments.

    Returns:
        tuple: A tuple containing lists of atom groups and their counts.
    """
    atom_groups = [None] * 10
    group_numbers = [None] * 10

    for key, value in vars(args).items():
        if key.startswith('g') and not key.startswith('gn') and value is not None:
            index = int(key[1:]) - 1  # Obtener el índice del grupo
            atom_groups[index] = value
            continue

        if key.startswith('gn') and value is not None:
            index = int(key[2:]) - 1  # Obtener el índice del número del grupo
            group_numbers[index] = value
            continue
    
    # Eliminar valores None
    atom_groups = [group for group in atom_groups if group is not None]
    group_numbers = [num for num in group_numbers if num is not None]

    return atom_groups, group_numbers

def main():
    """
    Main function to handle command line arguments and execute respective functions.
    This tool is designed for theoretical calculations in quantum mechanics and molecular dynamics,
    providing various sub-commands for different types of calculations and manipulations.
    """
    parser = argparse.ArgumentParser(description='Tool for theoretical calculations in quantum mechanics and molecular dynamics.')
    subparsers = parser.add_subparsers(dest='command', help='Available sub-commands')

    # =========== Sub-command to generate new configurations ===========
    parser_config = subparsers.add_parser('configuration', help='Generate configurations for materials.')
    add_arguments(parser_config)

    subsubparsers = parser_config.add_subparsers(dest='subcommand', help='Sub-commands for configuration generation')

    # Sub-command: edit
    parser_rattle = subsubparsers.add_parser('rattle', help='Modify atomic positions')
    parser_rattle.add_argument('--std', type=float, help='Standard deviation for displacement distribution in "rattle" operation')
    parser_rattle.add_argument('--N', type=int, default=1, help='Number of repetitions')

    # Sub-command: compress
    parser_compress = subsubparsers.add_parser('compress', help='Modify atomic positions')
    parser_compress.add_argument('--compress-min', type=float, nargs=3, help='Minimum compression factors in x, y, z. Format: x y z')
    parser_compress.add_argument('--compress-max', type=float, nargs=3, help='Maximum compression factors in x, y, z. Format: x y z')
    parser_compress.add_argument('--N', type=int, default=1, help='Number of repetitions')

    # Sub-command: supercell
    parser_supercell = subsubparsers.add_parser('supercell', help='')
    parser_supercell.add_argument('--repeat', type=int, nargs=3, help='Repeat the unit cell in x, y, z dimensions. Format: x y z')

    # Sub-command: widening
    parser_widening = subsubparsers.add_parser('widening', help='')
    parser_widening.add_argument('--init-id', type=int, help='Initial atom ID for operations')
    parser_widening.add_argument('--mid-id', type=int, help='Mid atom ID for operations')
    parser_widening.add_argument('--end-id', type=int, help='End atom ID for operations')
    parser_widening.add_argument('--direction', type=str, choices=['x', 'y', 'z'], help='Direction for modifications')

    # Sub-command: interpolation
    parser_interpolation = subsubparsers.add_parser('interpolation', help='')
    parser_interpolation.add_argument('--N', type=int, default=1, help='Number of repetitions')
    parser_interpolation.add_argument('--degree', type=int, help='Degree for polynomial operations')
    parser_interpolation.add_argument('--first-neighbor', default=False, action='store_true', help='Consider only first neighbors in operations')

    # Sub-command: dimer
    parser_dimer = subsubparsers.add_parser('dimer', help='Search for optimal dimer configurations')
    parser_dimer.add_argument('--N', type=int, default=10, help='Number of iterative steps in the dimer search')
    parser_dimer.add_argument('--vacuum', type=float, default=6.0, help='Vacuum distance around the dimer structure in Ångströms')
    parser_dimer.add_argument('--d0', type=float, help='Initial distance between the two atoms in a dimer in Ångströms')
    parser_dimer.add_argument('--df', type=float, help='Final distance between the two atoms in a dimer in Ångströms')

    # Sub-command: dimer
    parser_remove = subsubparsers.add_parser('remove', help='Search for optimal dimer configurations')
    parser_remove.add_argument('--N', type=int, default=10, help='Number of iterative steps in the dimer search')
    parser_remove.add_argument('--distribution', choices=['uniform', 'distance', 'distance-1', 'random'], help='Distribution type')
    parser_remove.add_argument('--fill', default=False, action='store_true', help='Fill vacancies with specified species')
    parser_remove.add_argument('--iterations', type=int, default=1, help='Number of iterations')
    for i in range(1, 10):  # Assuming up to 10 groups
        parser_remove.add_argument(f'--g{i}', nargs='+', help=f'List of atom indices for group {i}')
        parser_remove.add_argument(f'--gn{i}', type=int, help=f'Number of atoms in group {i}')

    # Sub-command: dimer
    parser_substitution = subsubparsers.add_parser('substitution', help='Search for optimal dimer configurations')
    parser_substitution.add_argument('--N', type=int, default=10, help='Number of iterative steps in the dimer search')
    parser_substitution.add_argument('--distribution', choices=['uniform', 'distance', 'distance-1', 'random'], help='Distribution type')
    parser_substitution.add_argument(f'--g{i}', nargs='+', help=f'List of atom indices for group {i}')
    parser_substitution.add_argument(f'--gn{i}', nargs='+', help=f'List of atom indices for group {i}')
    parser_substitution.add_argument(f'--gf{i}', nargs='+', help=f'List of atom indices for group {i}')

    # =========== Sub-comando para generar script ===========
    parser_config = subparsers.add_parser('configurate', help='Read Position data from "path", read Configurtion data from "config_path" and export to "output_path".')
    add_arguments(parser_config)
    parser_config.add_argument('--config_path', type=str, required=True, help='')
    parser_config.add_argument('--config_source', type=str, required=True, help='')

    # =========== Sub-command for export files from SOURCE format to OUTPUT format ===========
    parser_export_position = subparsers.add_parser('export', help='Export atomic positions from a specified source format to a desired output format. This is useful for converting file formats for compatibility with various simulation and visualization tools.')
    add_arguments(parser_export_position)
    parser_export_position.add_argument('--bond_factor', type=float, default=1.1, required=False, help='')

    # =========== Sub-command for PLOT files from SOURCE format to OUTPUT format ===========
    parser_plot = subparsers.add_parser('plot', help='Generates plots based on data from a specified source. This can include plotting energy bands, density of states, or molecular structures, depending on the input data and specified plot type.')
    add_arguments(parser_plot)
    parser_plot.add_argument('--plot', type=str, required=True, choices=['bands', 'RBF', 'path_tracking', 'count_species', 'evaluate_ff', 'bond_distance_tracking', 'molecule_formation_tracking'], help='Specifies the type of plot to generate. "bands" for band structure plots and "RBF" for radial basis function (RBF) plots.')
    parser_plot.add_argument('--fermi', type=float, help='Specifies the Fermi energy level (in eV). This is crucial for accurate band structure plots as it sets the reference energy level around which the band structure is visualized.')
    parser_plot.add_argument('--emin', type=float, help='Specifies the minimum energy (in eV) for the plot range. Used to limit the plot to a specific energy range, enhancing focus on regions of interest.')
    parser_plot.add_argument('--emax', type=float, help='Specifies the maximum energy (in eV) for the plot range. Similar to --emin, it allows focusing on a specific energy interval in the plot.')
    parser_plot.add_argument('--cutoff', type=float, default=6.0, help='Defines the cutoff distance (in Ångströms) for RBF plots. This parameter is crucial for determining the extent of spatial interactions to be considered in the plot.')
    parser_plot.add_argument('--number_of_bins', type=int, default=100, help='Sets the number of bins for the histogram in RBF plots. A higher number of bins can lead to finer details in the plot, but may also increase computational load.')

    parser_plot.add_argument('--specie', type=str, required=False, help='')
    parser_plot.add_argument('--sigma', type=float, required=False, default=1.2, help='bonda factor')
    parser_plot.add_argument('--reference', type=str, required=False, help='')
    parser_plot.add_argument('--topology', type=str, required=False, help='')

    parser_plot.add_argument('--ff-forces-tag', type=str, required=False, help='')
    parser_plot.add_argument('--ff-energy-tag', type=str, required=False, help='')
    parser_plot.add_argument('--wrap', default=False, action='store_true', help='.')
    parser_plot.add_argument('--save', default=False, action='store_true', help='.')
    parser_plot.add_argument('--tranparency', default=False, action='store_true', help='.')
    parser_plot.add_argument('--bins', type=int, default=100, required=False, help='')
    
    # ========== Sub-command: filter ===========
    parser_filter = subparsers.add_parser('filter', help='Apply filters to select specific data based on various criteria.')
    add_arguments(parser_filter)
    parser_filter.add_argument('--filter', choices=['sort', 'random', 'flat_histogram', 'binary', 'index'], type=str, help='Type of filter to apply: random, flat_histogram, or binary.')
    parser_filter.add_argument('--property', choices=['E', 'E/N', 'forces', 'has_ID', 'has_not_ID'], type=str, help='Property to use for filtering: Energy (E), forces, or atom IDs.')
    parser_filter.add_argument('--type', choices=['max', 'min', 'equipartition', 'tail', 'uniform'], type=str, help='Filter type: max (maximum value) or min (minimum value).')
    parser_filter.add_argument('--value', type=float, required=False, help='Value to compare against for the filter.')
    parser_filter.add_argument('--ID', type=str, required=False, help='Atom ID for filtering, if applicable.')
    parser_filter.add_argument('--traj', default=False, action='store_true', help='Enable trajectory-based filtering.')
    parser_filter.add_argument('--N', default=1, type=float, help='Number of elements to select when filtering.')

    # ========== ADD - solvent ===========
    parser_solvent = subparsers.add_parser('solvent', help='Configure solvent environment for molecular dynamics or quantum mechanics simulations. This includes setting solvent type, density, and the geometry of the simulation environment.')
    add_arguments(parser_solvent)
    parser_solvent.add_argument('--density', type=float, default='.', help='Specify the density of the solvent in the simulation. The unit of density should align with the simulation system.')
    parser_solvent.add_argument('--solvent', type=str, nargs='+', choices=['H2O', 'H2'], default='H2O', help='Select the type of solvent to be used. Options include "H2O" for water and "H2" for hydrogen. Multiple solvents can be specified.')
    parser_solvent.add_argument('--slab', default=False, action='store_true', help='Enable this flag to indicate a slab geometry in the simulation, typically used in surface studies.')
    parser_solvent.add_argument('--shape', type=str, choices=['box', 'sphere', 'cell', 'parallelepiped'], default='cell', help='Define the shape of the simulation box. Options are "box" for a rectangular prism and "sphere" for spherical geometry.')
    parser_solvent.add_argument('--size', type=float, nargs=3, default=[10, 10, 10], help='Set the dimensions of the simulation box, specified as length, width, and height. Applicable when the shape is "box".')
    parser_solvent.add_argument('--vacuum_tolerance', type=float, default=0.0, help='Set the vacuum tolerance for the simulation, defining the minimum allowed spacing between atoms or molecules.')
    parser_solvent.add_argument('--colition_tolerance', type=float, default=1.6, help='Specify the collision tolerance, which is the minimum distance allowed between atoms or molecules to avoid overlaps.')
    parser_solvent.add_argument('--seed', type=float, default=0, help='')
    parser_solvent.add_argument('--translation', type=float, nargs=3, default=[0, 0, 0], help='Provide a translation vector to adjust the position of the system within the simulation box. Format: x-offset y-offset z-offset.')
    parser_solvent.add_argument('--wrap', default=True, action='store_true', help='Enable or disable wrapping of atoms or molecules within the simulation box boundaries. Useful for periodic boundary conditions.')

    # ========== AbInitioThermodynamics ===========
    parser_AbIT = subparsers.add_parser('thermodynamic', help='')
    add_arguments(parser_AbIT)
    parser_AbIT.add_argument('--plot', type=str, choices=['phase_diagram'], default='phase_diagram', help='')
    parser_AbIT.add_argument('--especie', type=str, default='O', help='')
    parser_AbIT.add_argument('--reference_ID', type=int, nargs='+', help='')
    parser_AbIT.add_argument('--mu_max', type=float, default=0.0, help='')
    parser_AbIT.add_argument('--mu_min', type=float, default=-10.0, help='')

    # ========== BLENDER ===========
    parser_blender = subparsers.add_parser('blender', help='')
    add_arguments(parser_blender)
    parser_blender.add_argument('--plot', type=str, choices=['render'], default='xyz', required=False, help='')
    parser_blender.add_argument('--resolution', type=int, nargs=2, default=[1920, 1920], required=False, help='')
    parser_blender.add_argument('--samples', type=int, default=15, required=False, help='')
    parser_blender.add_argument('--fog', action='store_true', default=False, required=False, help='')
    parser_blender.add_argument('--render', action='store_true', default=False, required=False, help='')
    parser_blender.add_argument('--sigma', type=float, default=1.1, required=False, help='')
    parser_blender.add_argument('--scale', type=float, default=1.0, required=False, help='')
    parser_blender.add_argument('--camera', type=str, nargs='+', default=['x', 'y', 'z'], choices=['x', '-x', 'y', '-y', 'z', '-z'], required=False, help='')
    parser_blender.add_argument('--repeat', type=int, nargs=3, default=[0,0,0], required=False, help='')
    
    args = parser.parse_args()


    # Handle execution based on the specified sub-command
    if args.command == 'configuration':
        if args.subcommand == 'rattle':
            print(f"Rattle: std={args.std}, N={args.N}")
        elif args.subcommand == 'compress':
            print(f"Compress: compress_min={args.compress_min}, compress_max={args.compress_max}, N={args.N}")
        elif args.subcommand == 'supercell':
            print(f"Supercell: repeat={args.repeat}")
        elif args.subcommand == 'widening':
            print(f"Widening: init_id={args.init_id}, mid_id={args.mid_id}, end_id={args.end_id}, direction={args.direction}")
        elif args.subcommand == 'interpolation':
            print(f"Interpolation: N={args.N}, degree={args.degree}, first_neighbor={args.first_neighbor}")
        elif args.subcommand == 'dimer':
            print(f"Dimer: N={args.N}, vacuum={args.vacuum}, d0={args.d0}, df={args.df}")
        elif args.subcommand == 'remove':
            atom_groups, group_numbers = parse_dynamic_groups(args)
            print(f"Remove: N={args.N}, distribution={args.distribution}, fill={args.fill}, iterations={args.iterations}, atom_groups={atom_groups}, group_numbers={group_numbers}")
        elif args.subcommand == 'substitution':
            atom_groups, group_numbers = parse_dynamic_groups(args)
            print(f"Substitution: N={args.N}, distribution={args.distribution}, atom_groups={atom_groups}, group_numbers={group_numbers}")


    # Handle execution based on the specified sub-command
    if args.command == 'configuration':
        args2 = subsubparsers.parse_args() 
        if args2 == 'dimer'
        atom_groups, group_numbers = parse_dynamic_groups(args)
        generate_defects(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, conteiner_index=args.conteiner_index,
            output_path=args.output_path, output_source=args.output_source,
            verbose=args.verbose,
            defect=args.defect, species=args.species, new_species=args.new_species, 
            atom_groups=atom_groups, group_numbers=group_numbers, fill=args.fill, repetitions=args.repetitions, iterations=args.iterations, distribution=args.distribution)
 
    elif args.command == 'disassemble':
        generate_disassemble_surface(args.path, steps=args.steps, final_distance=args.final_distance, atoms_to_remove=args.atoms_to_remove, subfolders=args.subfolders, verbose=args.verbose)
    
    elif args.command == 'dimer':
        generate_dimers(path=args.path,     source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, 
                        subfolders=args.subfolders, conteiner_index=args.conteiner_index,
                        labels=args.labels, steps=args.steps, initial_distance=args.d0, final_distance=args.df, vacuum_tolerance=args.vacuum,
                        output_path=args.output_path,       output_source=args.output_source,
                        verbose=args.verbose )
        
    elif args.command == 'config':
        generate_config(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, 
                        config_path=args.config_path, config_source=args.config_source,
                        output_path=args.output_path, output_source=args.output_source, verbose=args.verbose)
    
    elif args.command == 'bands':
        generate_band_calculation(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, points=args.points, special_points=args.special_points, 
                        subfolders=args.subfolders, verbose=args.verbose, output_path=args.output_path)
    
    elif args.command == 'bands2json':
        generate_json_from_bands(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, fermi=args.fermi,
                        subfolders=args.subfolders, verbose=args.verbose, output_path=args.output_path)

    elif args.command == 'export':
        generate_export_files(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders,
            verbose=args.verbose, output_path=args.output_path, output_source=args.output_source, bond_factor=args.bond_factor)

    elif args.command == 'plot':
        generate_plot(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, conteiner_index=args.conteiner_index,
            verbose=args.verbose, output_path=args.output_path, plot=args.plot, fermi=args.fermi,
            emin=args.emin, emax=args.emax, cutoff=args.cutoff, number_of_bins=args.number_of_bins)

    elif args.command == 'MD':
        generate_MD(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, conteiner_index=args.conteiner_index,
            output_path=args.output_path, output_source=args.output_source,
            verbose=args.verbose, plot=args.plot,  sigma=args.sigma, topology=args.topology, wrap=args.wrap,
            reference=args.reference, ff_energy_tag=args.ff_energy_tag, ff_forces_tag=args.ff_forces_tag, 
            tranparency=args.tranparency, save=args.save)

    elif args.command == 'edit_positions':
        generate_edit_positions(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, verbose=args.verbose, 
            output_path=args.output_path, output_source=args.output_source, 
            edit=args.edit, std=args.std, N=args.N, direction=args.direction, repeat=args.repeat, compress_min=args.compress_min, compress_max=args.compress_max,
            init_index=args.init_index, mid_index=args.mid_index, end_index=args.end_index, degree=args.degree, first_neighbor=args.first_neighbor)

    elif args.command == 'edit_configuration':
        generate_edit_configuration(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, verbose=args.verbose, 
            output_path=args.output_path, output_source=args.output_source, 
            edit=args.edit, search=args.search, atom_index=args.index, atom_ID=args.ID, new_atom_ID=args.new_ID, weights=args.weights, N=args.N, seed=args.seed)

    elif args.command == 'filter':
        generate_filter(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, verbose=args.verbose, output_path=args.output_path, output_source=args.output_source,
                filter_class=args.filter, container_property=args.property, filter_type=args.type, value=args.value, traj=args.traj, N=args.N, ID=args.ID)

    elif args.command == 'dataset':
        generate_dataset(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, conteiner_index=args.conteiner_index,
            verbose=args.verbose, output_path=args.output_path, operation=args.operation, )

    elif args.command == 'supercell_embedding':
        generate_supercell_embedding(
                        relax_supercell_path=args.path,     relax_supercell_source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, 
                        unrelax_supercell_path=args.notrelax_supercell_path,   unrelax_supercell_source=args.notrelax_supercell_source, 
                        unitcell_path=args.unitcell_path,            unitcell_source=args.unitcell_source, 
                        output_path=args.output_path,       output_source=args.output_source,
                        verbose=args.verbose )

    elif args.command == 'solvent':
        generate_solvent(
                        path=args.path,     source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, 
                        subfolders=args.subfolders, conteiner_index=args.conteiner_index,
    
                        density=args.density, solvent=args.solvent, slab=args.slab, 
                        shape=args.shape, size=args.size, vacuum_tolerance=args.vacuum_tolerance, 
                        colition_tolerance=args.colition_tolerance, translation=args.translation, wrap=args.wrap, 
                        seed=args.seed, 

                        output_path=args.output_path,       output_source=args.output_source,
                        verbose=args.verbose )

    elif args.command == 'thermodynamic':
        generate_AbInitioThermodynamics(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, conteiner_index=args.conteiner_index,
            verbose=args.verbose, output_path=args.output_path, plot=args.plot, 
            reference_ID=args.reference_ID, especie=args.especie, mu_max=args.mu_max, mu_min=args.mu_min)

    elif args.command == 'blender':
        generate_BLENDER(path=args.path, source=args.source, forces_tag=args.forces_tag, energy_tag=args.energy_tag, subfolders=args.subfolders, conteiner_index=args.conteiner_index,
            verbose=args.verbose, output_path=args.output_path, 
            plot=args.plot, resolution=args.resolution, samples=args.samples, fog=args.fog, render=args.render,
            scale=args.scale, camera=args.camera, repeat=args.repeat, 
            sigma=args.sigma, )

if __name__ == '__main__':
    main()