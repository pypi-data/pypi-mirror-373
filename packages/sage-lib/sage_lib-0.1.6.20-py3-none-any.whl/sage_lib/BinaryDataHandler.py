try:
    # Try importing the FileManager class from the FileManager module.
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    # Write the import error message to standard error output and exit.
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    import os 
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing os: {str(e)}\n")
    del sys

'''
Important technical remarks
The calculation of the nonlocal correlation functional of Dion et al. (used in all
functionals listed above except rVV10 and SCAN+rVV10) requires a precalculated kernel 
which is distributed via the VASP download portal (VASP -> src -> vdw_kernel.bindat). 
If VASP does not find this file, the kernel will be calculated, which is however 
rather demanding. The kernel needs to be either copied to the VASP run directory for 
each calculation or can be stored in a central location and read from there. The 
location needs to be set in routine PHI_GENERATE. This does not work on some clusters
and the kernel needs to be copied into the run directory in such cases. The distributed
file uses little endian convention and won't be read on big endian machines. The big 
endian version of the file is available from the VASP team. In the case of the rVV10
nonlocal correlation functional, no precalculated kernel is required and it is 
calculated on the fly, which is however not as demanding as in the case of the functional
of Dion et al..
'''

class BinaryDataHandler(FileManager):
    """
    BinaryDataHandler Class
    
    Inherits from FileManager. This class is designed to handle
    binary data, specifically for reading and writing VASP VDW Kernel files.
    """
    
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Constructor method.
        
        Initializes the data attribute to None.
        """
        super().__init__(name=name, file_location=file_location)
        self.data = None

    def read_binary_file(self, file_location:str=None) -> bool:
        """
        Read a binary file.
        
        Parameters:
        - file_location (str): The path to the binary file to be read.
        
        Returns:
        - bool: True if the file is successfully read, otherwise False.
        """
        file_location = file_location if type(file_location) == str else self.file_location

        try:
            with open(file_location, 'rb') as f:
                self.data = f.read()
            return True
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return False

    def export_binary_file(self, file_location:str=None) -> bool:
        """
        Write to a binary file.
        
        Parameters:
        - file_location (str): The path where the binary file will be written.
        
        Returns:
        - bool: True if the file is successfully written, otherwise False.
        """
        file_location = file_location if type(file_location) == str else self.file_location

        if self.data is None:
            raise ValueError("No data available to write.")
        
        try:
            with open(file_location, 'wb') as f:
                f.write(self.data)
            return True
        except Exception as e:
            print(f"An error occurred while writing the file: {e}")
            return False

    def read_VASP_VDW_Kernel(self, file_location:str=None) -> bool:
        return self.read_binary_file(file_location)

    def export_VASP_VDW_Kernel(self, file_location:str=None) -> bool:
        return self.export_binary_file(self.ensure_filename_is_vdw_kernel(file_location))

    def ensure_filename_is_vdw_kernel(self, file_location):
        dir_name, file_name = os.path.split(file_location)
        if file_name:
            # Ignorar el nombre de archivo original y usar 'vdw_kernel.bindat'
            return os.path.join(dir_name, 'vdw_kernel.bindat')
        else:
            # El path ya es un directorio, así que simplemente añadir 'vdw_kernel.bindat'
            return os.path.join(file_location, 'vdw_kernel.bindat')
