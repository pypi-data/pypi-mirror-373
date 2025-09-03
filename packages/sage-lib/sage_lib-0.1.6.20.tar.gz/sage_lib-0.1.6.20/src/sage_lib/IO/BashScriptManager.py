try:
    from ..master.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import subprocess
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing subprocess: {str(e)}\n")
    del sys
    
class BashScriptManager(FileManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(file_location=file_location, name=name)
        self._comment = None
        self._parameters = {'srun':[], 'module':[], 'export':[] }
        self._BatchFile = None

        self._parameter_descriptions = {
        "--nodes": "Number of nodes to be used in the job.",
        "--ntasks-per-node": "Number of tasks to run per node.",
        "--time": "Wall clock time limit for the job.",
        "-o": "File to which standard output will be redirected.",
        "-e": "File to which standard error will be redirected.",
        "--mem": "Memory to be allocated for the job.",
        "--array": "Specifies the indexes of the job array elements.",
        "--mail-type": "Event types to notify the user.",
        "--mail-user": "Email address for job notifications.",
        "--cpus-per-task": "Number of CPU cores to be allocated per task.",
        "--ntasks": "Total number of tasks across all nodes.",
        "--ntasks-per-core": "Number of tasks to be launched per core.",
        "--constraint": "Node feature constraints (e.g., gpu).",
        "--gres": "Generic resources (e.g., GPUs) to allocate.",
                                        }
        
    def readBashScript(self, file_location:str=None):
        file_location = file_location if type(file_location) == str else self.file_location
        lines =list(self.read_file(file_location,strip=False))
        self.BatchFile = lines

        for line in lines:
            line = line.strip()
            if line.startswith("#SBATCH"):
                param = line.split(" ", 1)[1]
                self._parameters[param.split("=")[0]] = param.split("=")[1] if "=" in param else None
            if line.startswith("export"):
                self._parameters['export'].append( line[7:] )
            if line.startswith("srun"):
                self._parameters['srun'].append( line[5:] )
            if line.startswith("module"):
                self._parameters['module'].append( line[7:] )
            elif line.startswith("#"):
                self._comment = line[1:].strip()

    def exportAsBash(self, file_location:str=None):
        # Determine the file location
        file_location = file_location if file_location is not None else self.file_location

        # Open the file in write mode
        with open(file_location, 'w') as f:
            for line in self.BatchFile:
                f.write(line)
        # Give execute permission to the VASPscript.sh file
        subprocess.run(['chmod', '+x', file_location])

    def makeBash(self, file_location=None, job_name='SAGE_Bash_Script', output_file='SAGE_OutPut.out', error_file='SAGE_error.err', 
                        nodes:int=None, tasks_per_node:int=None, time_limit=None, conda_env=None, commands=None):
        file_location = file_location if file_location is not None else self.file_location if self.file_location is not None else '.'
        conda_env = conda_env if conda_env is not None else []
        commands = commands if commands is not None else []
        
        with open(script_filename, 'w') as file:
            file.write("#!/bin/bash\n")
            file.write(f"#SBATCH --job-name={job_name}\n")
            file.write(f"#SBATCH --output={output_file}\n")
            file.write(f"#SBATCH --error={error_file}\n")
            file.write(f"#SBATCH --nodes={nodes}\n")
            file.write(f"#SBATCH --ntasks-per-node={tasks_per_node}\n")
            file.write(f"#SBATCH --time={time_limit}\n")
            file.write("\n")
            
            file.write("# Activate the Python environment\n")
            for env in conda_env:
                file.write(f"source activate {env}\n")
            
            file.write("\n")
            for command in commands:
                file.write(f"{command}\n")

    def summary(self):
        text_str = "Batch Script Summary:\n"
        for param, value in self._parameters.items():
            if not type(value) == list:
                description = self.parameter_descriptions.get(param, "No description available.")
                text_str += f"{str(param)[:15].ljust(10, ' ') }: {str(value)[:10].ljust(10, ' ') } ({description})\n"
        return text_str

'''
pot = BashScriptManager('/home/akaris/Documents/code/Physics/VASP/v6.1/files/BASH/QUIP.sh')
pot.readBashScript()

pot.exportAsBash('/home/akaris/Documents/code/Physics/VASP/v6.1/files/bulk_optimization/Pt/FCC100/script1.sh')
print(pot.parameters)
print( pot.summary() )
pot.exportAsPOTCAR('/home/akaris/Documents/code/Physics/VASP/v6.1/files/POTCAR/POTCAR_export')
'''

