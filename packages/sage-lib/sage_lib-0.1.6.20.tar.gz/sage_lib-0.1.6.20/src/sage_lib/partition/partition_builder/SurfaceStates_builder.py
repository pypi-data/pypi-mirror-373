try:
    import copy
    import numpy as np
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

class SurfaceStates_builder(BasePartition):
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)

    def generate_adsorption_states(self, parameter:str, values:np.array=None, file_location:str = None) -> bool:
        containers = []
        directories = ['' for _ in self.containers]
        parameter = parameter.upper().strip()

        for container_index, container in enumerate(self.containers):
            if parameter.upper() == 'MONOATOMIC':
                containers += self.handle_monoatomic_specie(container, values, container_index, file_location)
                directories[container_index] = 'MONOATOMIC'

        self.containers = containers
        return containers

    def generate_disassemble_surface(self, parameter:str='', steps:int=5, final_distance:float=5.0, atoms_to_remove:int=None, file_location:str = None) -> bool:
        containers = []
        directories = ['' for _ in self.containers]
        parameter = parameter.upper().strip()

        for container_index, container in enumerate(self.containers):
            containers += self.handle_disassemble_surface(container, steps, final_distance, atoms_to_remove, file_location)
            directories[container_index] = 'disassemble_surface'

        self.containers = containers
        return containers

    def handle_monoatomic_specie(self, container, values, container_index, file_location=None):
        # values = ['O']
        sub_directories, containers = [], []

        reaction_sites = container.AtomPositionManager.get_adsorption_sites() 
        offsets = {al: np.array([0, 0, self._covalent_radii[al]*2]) for al in values}
        
        for position_group, direction in [('top', 1), ('bottom', -1)]:
            for position_id, position in enumerate(reaction_sites[position_group]):
                for al in values:
                    container_copy = self.copy_and_update_container(container, f'/adsorption_states/{position_group}_{position_id}', file_location)
                    offset = offsets[al] * direction
                    new_position = position + offset
                    container_copy.AtomPositionManager.add_atom(atomLabels=al, 
                                                                atomPosition=new_position, 
                                                                atomicConstraints=[1, 1, 1])
                    containers.append(container_copy)
                    
                    sub_directories.append(f'{position_group}_{position_id}')

        self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/adsorption_states')
        return containers

    def handle_disassemble_surface(self, container, steps:int=5, final_distance:float=5.0, atoms_to_remove:int=None, file_location=None):
        """
        Disassembles the surface by moving the topmost atom in n steps to a final distance.

        Args:
            n_steps (int): Number of steps to move the atom.
            final_distance (float): Final distance to move the atom from its original position.

        Returns:
            list of np.array: List of atom coordinates for each step.
        """
        # evaluate a feasible number of atoms to remove
        atoms_to_remove = np.min([atoms_to_remove, container.AtomPositionManager.atomCount]) if atoms_to_remove is not None else container.AtomPositionManager.atomCount

        sub_directories, containers = [], []
        step_size = float(final_distance)/steps
        container_copy = self.copy_and_update_container(container, f'/disassemble_surface', file_location)

        for n in range(atoms_to_remove):
            atom_index = np.argmax(container_copy.AtomPositionManager.atomPositions[:, 2])

            for step in range(1, steps+1):
                container_copy2 = self.copy_and_update_container(container_copy, f'/{n:04d}_{step:03d}', file_location)
                container_copy2.AtomPositionManager.move_atom(atom_index, [0,0,step*step_size]) 

                containers.append( container_copy2 )
                sub_directories.append(f'{n:04d}_{step:03d}')

            container_copy.AtomPositionManager.remove_atom(atom_index)

        self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/disassemble_surface')
        return containers


'''
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/OUTCAR'
path = '/home/akaris/Documents/code/Physics/VASP/v6.1/files/dataset/CoFeNiOOH_jingzhu/surf_CoFe_4H_4OH/MAG'
SSG = SurfaceStatesGenerator(path)
SSG.readVASPFolder(v=False)

#containers = SSG.generate_adsorption_states('MONOATOMIC', ['O'])
containers = SSG.generate_disassemble_surface(atoms_to_remove=2)
SSG.exportVaspPartition()
print( len(SSG.containers) )

'''