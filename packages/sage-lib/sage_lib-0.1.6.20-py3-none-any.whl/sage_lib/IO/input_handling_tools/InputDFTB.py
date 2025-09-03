try:
    from .InputFileManager import InputFileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing sage_lib.IO.input_handling_tools.InputFileManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

import re

class InputDFTB(InputFileManager):
    """
    A class to parse and manipulate DFTB+ .hsd input files.
    """
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)

        self.data = {}

    def read_hsd(self):
        """
        Reads the .hsd file and parses its contents.
        """
        if not self.file_location:
            raise ValueError("No file location provided.")

        try:
            with open(self.file_location, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            print(f"File not found: {self.file_location}")
            return False

        self.data = self.parse_hsd(content)
        return True

    def parse_hsd(self, content):
        """
        Parses the content of an .hsd file and returns a nested dictionary.
        """
        lines = content.splitlines()
        data = {}
        stack = [data]
        path = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('//'):
                i += 1
                continue

            # Handle block opening
            block_match = re.match(r'^(\w+)\s*\{', line)
            if block_match:
                block_name = block_match.group(1)
                new_block = {}
                stack[-1][block_name] = new_block
                stack.append(new_block)
                path.append(block_name)
                # Check if the block opens and closes on the same line
                if line.endswith('}'):
                    stack.pop()
                    path.pop()
                i += 1
                continue

            # Handle block closing
            elif line == '}':
                if stack:
                    stack.pop()
                    path.pop()
                i += 1
                continue

            # Handle attributes
            else:
                # Split at the first '='
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    # Check for block that opens inline
                    if value.endswith('{'):
                        value = value[:-1].strip()
                        new_block = {}
                        if value:
                            stack[-1][key] = {value: new_block}
                        else:
                            stack[-1][key] = new_block
                        stack.append(new_block)
                        path.append(key)
                    else:
                        # Store the value
                        stack[-1][key] = self.convert_value(value)
                else:
                    # Handle inline arrays or values without '='
                    key = line.strip()
                    # Check if the next line is a block or value
                    i += 1
                    next_line = lines[i].strip()
                    if next_line == '{':
                        new_block = {}
                        stack[-1][key] = new_block
                        stack.append(new_block)
                        path.append(key)
                    else:
                        stack[-1][key] = self.convert_value(next_line)
                        #i += 1
                        continue
            i += 1
        return data

    def convert_value(self, value):
        """
        Attempts to convert a string value to int, float, or keeps as string.
        """
        # Handle arrays
        if value.startswith('[') and value.endswith(']'):
            items = value[1:-1].split()
            return [self.convert_value(item) for item in items]

        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            pass

        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value


    def view(self):
        """
        Prints the parsed data in a readable format.
        """
        import json
        print(json.dumps(self.data, indent=2))

    def write_hsd(self, file_location=None):
        """
        Writes the current data back to an .hsd file.
        """
        file_location = file_location or self.file_location
        with open(file_location, 'w') as file:
            content = self.serialize_hsd(self.data)
            file.write(content)

    def serialize_hsd(self, data, indent=0):
        """
        Serializes the nested dictionary back into .hsd format.
        """
        lines = []
        indent_str = '  ' * indent
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key} {{")
                lines.append(self.serialize_hsd(value, indent + 1))
                lines.append(f"{indent_str}}}")
            else:
                lines.append(f"{indent_str}{key} = {value}")
        return '\n'.join(lines)

if __name__ == "__main__":
    # Read the .hsd file
    dftb_input = InputDFTB(file_location='../../test/DFTB/out_test/dftb_in.hsd')
    if dftb_input.read_hsd():
        # View the data
        dftb_input.view()

        # Modify a parameter
        dftb_input.data['Options']['WriteDetailedXML'] = 'Yes'

        # Write back to a new .hsd file
        #dftb_input.write_hsd('modified_dftb_input.hsd')

