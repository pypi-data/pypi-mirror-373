try:
    from sage_lib.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

class ChargeFileManager(FileManager):
    """
    ChargeFileManager Class
    
    This class is designed to manage computational charge files, particularly for programs like VASP.
    It includes methods to efficiently copy large files and to store the path of the original file.
    """
    
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        self.data = None

    def exportFile(self, file_location:str=None, original_file_location:str=None) -> bool:
        self.copy(file_location, original_file_location)
        return True

    def importFileLocation(self, file_location:str=None) -> bool:
        self.file_location = file_location
        return True
