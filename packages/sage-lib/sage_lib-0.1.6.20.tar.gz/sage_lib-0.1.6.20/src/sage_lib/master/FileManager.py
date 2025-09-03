try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import traceback
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing traceback: {str(e)}\n")
    del sys

try:
    import os
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing os: {str(e)}\n")
    del sys

try:
    from datetime import datetime
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing datetime: {str(e)}\n")
    del sys

try:
    import json
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing datetime: {str(e)}\n")
    del sys

try:
    import logging
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing logging: {str(e)}\n")
    del sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def error_handler(func):
    """
    Decorator for consistent error handling across methods.
    
    This decorator wraps the function in a try-except block, logging any
    errors that occur and re-raising them for further handling.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug("Detailed traceback:", exc_info=True)
            print(f"An error occurred in {func.__name__}. Check the log for details.")
            raise
    return wrapper
    
class FileManager:
    
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):

        if name is not None and not isinstance(name, str):
            raise TypeError("(!) name must be a string")
        self._name = name
        self._metaData = {}
        self._comment = ''
        if file_location is not None and not isinstance(file_location, str):
            raise TypeError("(!) file_location must be a string")
        self._file_location = file_location   
        self._original_file_location = None
        
        #self._FM_attrs = set(vars(self).keys())
        super().__init__(*args, **kwargs)
        
    def __getattr__(self, name):
        # Check if the attribute exists with a leading underscore
        private_name = f"_{name}"
        if private_name in self.__dict__:
            return getattr(self, private_name)
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        # Check if the attribute exists with a leading underscore
        private_name = f"_{name}"
        if private_name in self.__dict__:
            setattr(self, private_name, value)
        else:
            super().__setattr__(name, value)
            
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("(!) name must be a string")
        self._name = value

    @name.deleter
    def name(self):
        print("Deleting name")
        del self._name

    @property
    def file_location(self):
        return self._file_location

    @file_location.setter
    def file_location(self, value):
        if not isinstance(value, str):
            raise TypeError("(!) file_location must be a string")
        self._file_location = value
        if self._original_file_location == None: 
            self._original_file_location = self._file_location

    @file_location.deleter
    def file_location(self):
        print("Deleting file_location")
        del self._file_location

    @staticmethod
    def is_number(s):
        if s is None:
            return False
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False
        
    def is_numpy_array_Nx3(self, variable):
        if variable is not False:  # Asegúrate de que la variable no es False
            variable = np.array(variable)  # Convierte la variable a un array de NumPy si aún no lo es
            if variable.ndim == 2 and variable.shape[1] == 3:  # Verifica que sea 2D y de tamaño Nx3
                return True
        return False

    def isINT(self, num): return self.is_number(num) and abs(num - int(num)) < 0.0001 

    def is_close(self, point_a, point_b, threshold:float=1e-5) -> bool:
        """Check if two points are close to each other within a specified threshold."""
        return np.linalg.norm(point_a - point_b) < threshold

    def are_all_lines_empty(self, lines):
        """
        Check if all lines in a list are empty or if the list itself is empty.

        This function iterates over each element in the provided list, checking if each element (line)
        is empty. An empty line is defined as a string with no characters or only whitespace characters.
        The function returns True if all lines are empty or if the list itself is empty. Otherwise, it returns False.

        Parameters:
        lines (list of str): A list of strings (lines) to be checked.

        Returns:
        bool: True if all lines are empty or the list is empty, False otherwise.
        """
        # Check if the list itself is empty first
        if not lines:
            return True

        # Iterate through each line in the list
        for line in lines:
            # Check if the line is not empty (contains non-whitespace characters)
            if line.strip():
                return False  # Return False as soon as a non-empty line is found

        # Return True if all lines are empty or the list is empty
        return True
        
    def file_exists(self, file_path:str) -> bool:
        """Check if a file exists."""
        return os.path.exists(file_path)

    def create_directories_for_path(self, path:str):
        """
        Create any directories needed to ensure that the given path is valid.

        Parameters:
        - path (str): The file or directory path to validate.
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except PermissionError:
                print(f"Permission denied: Could not create directory at {path}")
                # Exit or handle the error appropriately
                exit(1)

    def read_file(self, file_location:str=None, strip=True):
        file_location = file_location if type(file_location) == str else self._file_location

        if file_location is None:
            raise ValueError("(!) File location is not set.")
        
        try:
            with open(file_location, 'r') as file:
                if strip:
                    for line in file:
                        yield line.strip()  # strip() elimina espacios y saltos de línea al principio y al final
                else:
                    for line in file:
                        yield line  # strip() elimina espacios y saltos de línea al principio y al final
        except FileNotFoundError:
            raise FileNotFoundError(f"(!) File not found at {file_location}")
        except IOError:
            raise IOError(f"(!) Error reading file at {file_location}")
        except Exception as e:
            print(f"Error inesperado: {e}")

    def save_to_json(self, data, file_path:str) -> bool:
        """
        Save data to a JSON file.

        Args:
            data (dict): The data to be saved as a Python dictionary.
            file_path (str): The path to the JSON file where the data will be saved.

        Returns:
            bool: True if the data was successfully saved, False otherwise.

        Raises:
            FileNotFoundError: If the directory specified in 'file_path' does not exist.
            IOError: If there was an issue writing the data to the JSON file.

        Example:
            data = {"name": "John", "age": 30, "city": "New York"}
            success = save_to_json(data, "data.json")
            if success:
                print("Data saved successfully.")
            else:
                print("Failed to save data.")
        """
        try:
            # Serialize the data as JSON and write it to the file
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            return True
        except FileNotFoundError:
            raise FileNotFoundError("The directory specified in 'file_path' does not exist.")
        except MemoryError:
            print("Memory Error occurred")
        except IOError as e:
            print(f"There was an issue writing the data to the JSON file. I/O error({e.errno}): {e.strerror}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return True

    def loadStoreManager(self, manager_class, file_name:str, attribute_name: str, read_method:str, v:bool=False):
        """Generic function to read a VASP file."""
        file_path = f"{self.file_location}/{file_name}"
        if not self.file_exists(file_path):
            return
        try:
            manager = manager_class(file_path)
            getattr(manager, read_method)()  # Call the appropriate read method
            setattr(self, attribute_name, manager)
            self._loaded[file_name] = True

            if v:
                print(f'File readed : {file_name}')
        except Exception as e:
            tb = traceback.format_exc()
            print(
                f"ERROR :: Cannot load {file_name}.\n"
                f"Exception type: {type(e).__name__}\n"
                f"Exception message: {e}\n"
                f"Stack trace:\n{tb}"
            )
            
    def copy(self, file_location:str=None, original_file_location:str=None, buffer_size=1024*1024) -> bool:
        """
        Universal copy method that chooses an available copy method.
        
        Parameters:
        - dest_path (str): The destination path where the file will be copied.
        - buffer_size (int): The buffer size for manual copy if needed.
        
        Returns:
        - bool: True if the file was successfully copied, otherwise False.
        """
        file_location  = file_location if file_location else self.file_location
        original_file_location  = original_file_location if original_file_location else self.original_file_location

        if original_file_location is None:
            print("Original file path is not set.")
            return False
        try:
            os.system(f"cp {original_file_location} {file_location}")
            return True
        except Exception as e:
            if verbosity: print(f"An error occurred while copying the file: {e}")
            return False 

    def copy_file_manual(self, file_location:str=None, original_file_location:str=None, buffer_size:int=1024*1024) -> bool:
        """
        Manually copy a file in a memory-efficient manner.
        
        Parameters:
        - dest_path (str): The destination path where the file will be copied.
        - buffer_size (int): The buffer size for the copy operation.
        
        Returns:
        - bool: True if the file was successfully copied, otherwise False.
        """
        try:
            with open(self.original_file_path, 'rb') as src, open(dest_path, 'wb') as dest:
                chunk = src.read(buffer_size)
                while chunk:
                    dest.write(chunk)
                    chunk = src.read(buffer_size)
            return True
        except Exception as e:
            print(f"An error occurred while copying the file: {e}")
            return False

    def _copy_shared_attributes(self, shared_attributes, source, destination):
        """
        Copies shared attributes from the source object to the destination object.

        :param shared_attributes: List of attribute names to be copied.
        :param source: The source object from which to copy attributes.
        :param destination: The destination object to which attributes are copied.
        """
        for attr in shared_attributes:
            if hasattr(source, attr):
                setattr(destination, attr, getattr(source, attr))

    def interpolate_vectors(self, vec1, vec2, steps):
        """
        Interpolates between two 3-component vectors in a specified number of steps.

        Parameters:
        - vec1 (list or numpy.ndarray): The starting 3-component vector.
        - vec2 (list or numpy.ndarray): The ending 3-component vector.
        - steps (int): The number of interpolation steps, including the starting and ending vectors.

        Returns:
        numpy.ndarray: A matrix where each row is an interpolated vector.
        """

        # Convert vectors to numpy arrays for easy computation
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        # Check if both vectors have 3 components
        if vec1.shape[0] != 3 or vec2.shape[0] != 3:
            raise ValueError("Both vectors must have exactly 3 components.")

        # Create a sequence of interpolated vectors
        interpolated_vectors = np.array([vec1 + (vec2 - vec1) * step / (steps - 1) for step in range(steps)])

        return interpolated_vectors

    def _handle_error(self, message: str, verbose: bool):
        """
        Handles errors by printing the message and optionally the traceback.

        Args:
            message (str): The error message to be printed.
            verbose (bool): If True, prints the full traceback of the error.
        """
        if verbose:
            print(message)
            traceback.print_exc()  # Print the full traceback

            # Optionally, store or log the traceback for further investigation
            error_traceback = traceback.format_exc()
            # Here, you can add code to log error_traceback to a file or database
