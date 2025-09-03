try:
    from ..master.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

# Defining the ChargeFileManager class which extends from FileManager.
class ChargeFileManager(FileManager):
    """
    ChargeFileManager Class

    A specialized file manager designed to handle computational charge files,
    particularly useful for VASP-related operations. It includes advanced
    functionalities like efficient copying of large files and storing the path
    of original files for reference.

    Attributes:
        file_location (str): The location of the file being managed.
        name (str): The name of the file or the identifier.
        data: An attribute to store additional data if required.
    """

    def __init__(self, file_location: str = None, name: str = None, **kwargs):
        """
        Initialize the ChargeFileManager instance.

        Args:
            file_location (str, optional): Initial location of the file to manage.
            name (str, optional): Name or identifier for the file.
            **kwargs: Arbitrary keyword arguments for future extensions.
        """
        # Initialize the parent class FileManager with provided arguments.
        super().__init__(name=name, file_location=file_location)
        # Additional data attribute for storing any related data.
        self.data = None

    def exportFile(self, file_location: str = None, original_file_location: str = None) -> bool:
        """
        Export the managed file to a specified location.

        This method copies the file from its original location to a new location,
        providing a way to effectively distribute or backup the file.

        Args:
            file_location (str, optional): The destination location to copy the file.
            original_file_location (str, optional): The original location of the file,
                defaults to the current file location stored in the instance.

        Returns:
            bool: True if the operation is successful, otherwise False.
        """
        # Determine the original file location.
        original_file_location = original_file_location if original_file_location is not None else self.file_location

        # Perform the file copy operation.
        self.copy(file_location, original_file_location)

        return True

    def importFileLocation(self, file_location:str = None) -> bool:
        """
        Update the file location in the instance.

        This method allows updating the file location, enabling the management
        of different files or changing the reference to the current file.

        Args:
            file_location (str, optional): The new location of the file to manage.

        Returns:
            bool: True if the operation is successful, otherwise False.
        """
        # Update the file_location attribute with the new file location.
        file_location = file_location if type(file_location) == str else self.file_location
        self._file_location = file_location

        return True
