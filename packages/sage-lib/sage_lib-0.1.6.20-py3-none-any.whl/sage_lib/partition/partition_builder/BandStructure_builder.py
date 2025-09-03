try:
    import numpy as np
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class BandStructure_builder(BasePartition):
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)
   
    def handleBandStruture(self, container, values, container_index, file_location=None):
        sub_directories, containers = [], []

        for v in values:
            points, special_points = v.get('points', 20), v.get('special_points', None)
            container_copy = self.copy_and_update_container(container, f'/band_structure/{special_points}_{points}', file_location)

            if special_points==None:
                PG = BandPathGenerator(Periodic_Object=container_copy.AtomPositionManager)
                special_points = PG.high_symmetry_points_path

            container_copy.KPointsManager.set_band_path(special_points, points)
            container_copy.InputFileManager.parameters['ISMEAR'] = -5     # ISMEAR = -5 (Método de ensanchamiento de Fermi para cálculos de bandas)
            container_copy.InputFileManager.parameters['SIGMA'] =  0.05   # SIGMA = 0.05 (Valor más pequeño debido al método de ensanchamiento)
            container_copy.InputFileManager.parameters['IBRION'] = -1     # IBRION = -1 (No relajación de iones, cálculos estáticos)
            container_copy.InputFileManager.parameters['NSW'] =  0        # NSW = 0 (Sin optimización de geometría)
            container_copy.InputFileManager.parameters['LORBIT'] =  11    # LORBIT = 11 (Si se desea calcular y escribir los caracteres de las bandas)
            container_copy.InputFileManager.parameters['ICHARG'] =  11    # ICHARG = 11 (Usa la densidad de carga de un cálculo previo y no actualiza la densidad de carga durante el cálculo)
            container_copy.InputFileManager.parameters['ISIF'] =  2       # ISIF = 2 (Mantiene fija la celda durante el cálculo)
            sub_directories.append(f'/{special_points}_{points}')
            containers.append(container_copy)

        self.generate_execution_script_for_each_container(sub_directories, container.file_location + '/band_structure')
        return containers