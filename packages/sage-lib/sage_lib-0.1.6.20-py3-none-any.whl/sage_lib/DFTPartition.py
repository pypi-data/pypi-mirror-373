try:
    from sage_lib.DFTSingleRun import DFTSingleRun
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing DFTSingleRun: {str(e)}\n")
    del sys

try:
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    from sage_lib.CrystalDefectGenerator import CrystalDefectGenerator
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing CrystalDefectGenerator: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import os 
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing os: {str(e)}\n")
    del sys

try:
    import copy
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

class DFTPartition(FileManager): # el nombre no deberia incluir la palabra DFT tieneu qe ser ma general
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self._containers = []

    def add_container(self, container:object):
        self.containers.append(container)

    def remove_container(self, container:object):
        self.containers.remove(container)

    def empty_container(self, container:object):
        self.containers = []

    def readVASPSubFolder(self, file_location:str=None, v=False):
        file_location = file_location if type(file_location) == str else self.file_location
                
        for root, dirs, files in os.walk(file_location):
            DFT_SR = self.readVASPFolder(root, v)
            self.add_container(container=DFT_SR)
            if v: print(root, dirs, files)

    def readVASPFolder(self, file_location:str=None, v=False):
        file_location = file_location if type(file_location) == str else self.file_location

        DFT_SR = DFTSingleRun(file_location)
        DFT_SR.readVASPDirectory()        
        self.add_container(container=DFT_SR)
        return DFT_SR

    def writePartition(self, file_location:str=None): 
        for container in self.containers:
            container.exportVASP()

    def summary(self, ) -> str:
        text_str = ''
        text_str += f'{self.file_location}\n'
        text_str += f'> Conteiners : { len(self.containers) }\n'
        return text_str
    
    def generateDFTVariants(self, parameter: str, values: np.array, is_surface:bool=False, file_location: str = None) -> bool:
        containers = []
        directories = ['' for _ in self.containers]
        
        for container_index, container in enumerate(self.containers):
            if parameter.upper() == 'KPOINTS':
                containers += self.handleKPoints(container, container_index, values, file_location) 
                directories[container_index] = 'KPOINTConvergence'

            elif parameter.upper() in container.InputFileManager.parameters_data:
                containers += self.handleInputFile(container, parameter, values, container_index, file_location)
                directories[container_index] = f'{parameter}_analysis'

            elif parameter.upper() == 'VACANCY':
                containers += self.handleVacancy(container, values, container_index, file_location, is_surface)
                directories[container_index] = 'Vacancy'

        self.containers = containers
        self.generate_master_script_for_all_containers(directories, file_location if not file_location is None else container.file_location )

    def handleKPoints(self, container, container_index, values, file_location=None):
        sub_directories, containers = [], []

        for v in values:
            container_copy = self.copy_and_update_container(container, f'/KPOINTConvergence/{v[0]}_{v[1]}_{v[2]}', file_location)
            container_copy.KPointsManager.subdivisions = [v[0], v[1], v[2]]
            sub_directories.append(f'{v[0]}_{v[1]}_{v[2]}')
            containers.append(container_copy)

        self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/KPOINTConvergence')
        return containers

    def handleInputFile(self, container, parameter, values, container_index, file_location=None):
        sub_directories, containers = [], []

        for v in values:
            container_copy = self.copy_and_update_container(container, f'/{parameter}_analysis/{v}', file_location)
            container_copy.InputFileManager.parameters[parameter.upper()] = ' '.join(v) if v is list else v 
            sub_directories.append('_'.join(map(str, v)) if isinstance(v, list) else str(v))
            containers.append(container_copy)

        self.generate_execution_script_for_each_container(sub_directories, container.file_location + f'/{parameter}_analysis')
        return containers

    def handleVacancy(self, container, values, container_index, file_location=None, is_surface=False):
        sub_directories, containers = [], []

        container_copy = self.copy_and_update_container(container, '/Vacancy', file_location)
        container_copy.AtomPositionManager.is_surface = True
        container_copy.AtomPositionManager = CrystalDefectGenerator(Periodic_Object=container_copy.AtomPositionManager)
        all_vacancy_configs, all_vacancy_label = container_copy.AtomPositionManager.generate_all_vacancies()

        for cv_i, (vacancy_configs, vacancy_label) in enumerate(zip(all_vacancy_configs, all_vacancy_label)):
            container_copy2 = copy.deepcopy(container_copy)
            container_copy2.AtomPositionManager = vacancy_configs
            container_copy2.file_location = f'{container_copy.file_location}/{cv_i}_{vacancy_label}'
            sub_directories.append(f'{cv_i}_{vacancy_label}')
            containers.append(container_copy2)
        
        self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/Vacancy')
        return containers

    def copy_and_update_container(self, container, sub_directory: str, file_location=None):
        copy.deepcopy(container._atomic_mass)
        container_copy = copy.deepcopy(container)
        container_copy.file_location = f'{container.file_location}{sub_directory}' if file_location is None else file_location
        return container_copy

    def generate_execution_script_for_each_container(self, directories: list = None, file_location: str = None):
        self.create_directories_for_path(file_location)
        script_content = self.generate_script_content('VASPscript.sh', directories)
        self.write_script_to_file(script_content, f"{file_location}/execution_script_for_each_container.py")


    def generate_master_script_for_all_containers(self, directories: list = None, file_location: str = None):
        self.create_directories_for_path(file_location)
        script_content = self.generate_script_content('execution_script_for_each_container.py', directories)
        self.write_script_to_file(script_content, f"{file_location}/master_script_for_all_containers.py")


    def generate_script_content(self, script_name: str, directories: list = None) -> str:
        directories_str = "\n".join([f"    '{directory}'," for directory in directories])
        return f'''#!/usr/bin/env python3
import os
import subprocess

original_directory = os.getcwd()

directories = [
{directories_str}
]

for directory in directories:
    os.chdir(directory)
    subprocess.run(['chmod', '+x', '{script_name}'])
    subprocess.run(['sbatch', '{script_name}'])
    os.chdir(original_directory)
'''

    def write_script_to_file(self, script_content: str, file_path: str):
        with open(file_path, "w") as f:
            f.write(script_content)

    def export_configXYZ(self, file_location:str=None, verbose:bool=False):
        file_location  = file_location if file_location else self.file_location+'_config.xyz'
        with open(file_location, 'w'):pass # Create an empty file
        
        for container_index, container in enumerate(self.containers):
            if container.OutFileManager is not None:    
                container.OutFileManager.export_configXYZ(file_location=file_location, save_to_file='a', verbose=False)

        if verbose:
            print(f"XYZ content has been saved to {file_location}")

        return True

'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/OUTCAR'
DP = DFTPartition(path)
DP.readVASPFolder(v=True)
print( DP.containers[0].OutFileManager.AtomPositionManager[0] )
DP.export_configXYZ()

path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/dataset/CoFeNiOOH_jingzhu/surf_CoFe_4H_4OH/MAG'

DP = DFTPartition(path)

DP.readVASPFolder(v=True)

DP.generateDFTVariants('Vacancy', [1], is_surface=True)
#DP.generateDFTVariants('KPOINTS', [[n,n,1] for n in range(1, 15)] ) 
DP.writePartition()


path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/dataset/CoFeNiOOH_jingzhu/surf_CoFe_4H_4OH/MAG'
DP = DFTPartition(path)
DP.readVASPFolder(v=True)
DP.generateDFTVariants('NUPDOWN', [n for n in range(0, 10, 1)] )
DP.writePartition()

path = '/home/akaris/DocumeEENnts/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/*OH surface with Fe(HS)'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/POSCAR/Cristals/NiOOH/*OH surface for pure NiOOH'
#DP = DFTPartition('/home/akaris/Documents/code/Physics/VASP/v6.1/files/bulk_optimization/Pt/parametros/ENCUT_optimization_252525_FCC')
DP = DFTPartition(path)
#DP.readVASPSubFolder(v=True)
DP.readVASPFolder(v=True)

#DP.generateDFTVariants('Vacancy', [1], is_surface=True)
#DP.generateDFTVariants('KPOINTS', [[n,n,1] for n in range(1, 15)] )    
DP.generateDFTVariants('ENCUT', [n for n in range(200, 1100, 45)] )

DP.writePartition()

DP.generateDFTVariants('ENCUT', [ E for E in range(400,700,30)] )
print( DP.summary() )

print( DP.containers[0].AtomPositionManager.summary() )
'''

