try:
    from ..ForceFieldManager import ForceFieldManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing ForceFieldManager: {str(e)}\n")
    del sys

class GAPTrainer(ForceFieldManager):
    """
    Clase para entrenar un modelo GAP (Gaussian Approximation Potential).
    """

    def __init__(self, name="GAP_model", file_location="."):
        """
        Inicializa la clase GAPTrainer con valores predeterminados o proporcionados.

        gap (list of Descriptors) – Initialisation string for GAPs
        default_sigma (float) – Error in [energies forces virials hessians]
        config_type_sigma (str) – What sigma values to choose for each type of data. Format: {type:energy:force:virial:hessian}
        core_ip_args (str) – QUIP init string for a potential to subtract from data (and added back after prediction)
        core_param_file (str) – QUIP XML file for a potential to subtract from data (and added back after prediction)
        do_e0_avg (bool) – Method of calculating e0 if not explicitly specified. If true, computes the average atomic energy in input data. If false, sets e0 to the lowest atomic energy in the input data.
        do_ip_timing (bool) – To enable or not timing of the interatomic potential.
        e0 (str) – Atomic energy value to be subtracted from energies before fitting (and added back on after prediction). Specifiy a single number (used for all species) or by species: {Ti:-150.0:O:-320}. energy = core + GAP + e0
        e0_offset (float) – Offset of baseline. If zero, the offset is the average atomic energy of the input data or the e0 specified manually.
        hessian_delta (float) – Delta to use in numerical differentiation when obtaining second derivative for the Hessian covariance
        sigma_parameter_name (str) – Sigma parameters (error hyper) for a given configuration in the database. Overrides the command line sigmas. In the XYZ, it must be prepended by energy_, force_, virial_ or hessian_
        sigma_per_atom (bool) – Interpretation of the energy and virial sigmas specified in >>default_sigma<< and >>config_type_sigma<<. If >>T<<, they are interpreted as per-atom errors, and the variance will be scaled according to the number of atoms in the configuration. If >>F<< they are treated as absolute errors and no scaling is performed. NOTE: sigmas specified on a per-configuration basis (see >>sigma_parameter_name<<) are always absolute.
        sparse_jitter (float) – Intrisic error of atomic/bond energy, used to regularise the sparse covariance matrix
        sparse_use_actual_gpcov (bool) – Use actual GP covariance for sparsification methods
        template_file (str) – Template XYZ file for initialising object
        verbosity (Verbose) – Verbosity control.

        """
        super().__init__(name, file_location)
        self.parameters = {
            "e0": {"H": 3.21, "O": 4.6},
            "energy_parameter_name": "energy",
            "force_parameter_name": "forces",
            "do_copy_at_file": "F",
            "sparse_separate_file": "T",
            "gp_file": "GAP.xml",
            "at_file": "train.xyz",
            "default_sigma": [0.008, 0.04, 0, 0],
            "gap": {
                "distance_2b": {
                    "cutoff": 4.0,
                    "covariance_type": "ard_se",
                    "delta": 0.5,
                    "theta_uniform": 1.0,
                    "sparse_method": "uniform",
                    "add_species": "T",
                    "n_sparse": 10
                }
            }
        }

    def set_parameters(self, **kwargs):
        """
        Establece o actualiza los parámetros para el entrenamiento del modelo GAP.
        """
        for key, value in kwargs.items():
            if key in self.parameters:
                self.parameters[key] = value
            else:
                raise KeyError(f"Parameter {key} not recognized.")

    def get_parameter_description(self):
        """
        Devuelve una descripción de los parámetros.
        """
        descriptions = {
            "e0": "Energías de los átomos aislados.",
            # Añadir descripciones para el resto de los parámetros aquí
        }
        return "\n".join(f"{key}: {desc}" for key, desc in descriptions.items())

    def train(self):
        """
        Entrena el modelo GAP utilizando los parámetros establecidos.
        """
        command = self._build_command()
        print(f"Executing: {command}")
        # Aquí se ejecutaría el comando en un entorno real
        # os.system(command)

    def _build_command(self):
        """
        Construye el comando de bash para el entrenamiento GAP.
        """
        command = ["gap_fit"]
        for key, value in self.parameters.items():
            if isinstance(value, dict):
                subcommand = self._build_subcommand(key, value)
                command.append(subcommand)
            else:
                command.append(f"{key}={value}")
        return " ".join(command)

    def _build_subcommand(self, key, value_dict):
        """
        Construye un subcomando para parámetros complejos.
        """
        parts = [f"{key}="]
        for subkey, subvalue in value_dict.items():
            if isinstance(subvalue, dict):
                parts.append(self._build_subcommand(subkey, subvalue))
            else:
                parts.append(f"{subkey}={subvalue}")
        return ":".join(parts)

'''
 gap_fit 

 energy_parameter_name=E_dftbplus_d4 
 force_parameter_name=F_dftbplus_d4 
 do_copy_at_file=F 
 sparse_separate_file=T 
 gp_file=GAP.xml 
 at_file=train.xyz 
 default_sigma={0.008 0.04 0 0} 

 gap_fit 
 energy_parameter_name=energy 
 force_parameter_name=forces 
 do_copy_at_file=F 
 sparse_separate_file=T 
 gp_file=GAP.xml 
 at_file=train.xyz 
 default_sigma={0.008 0.04 0 0} 
 gap={distance_2b cutoff=4.0 covariance_type=ard_se delta=0.5 theta_uniform=1.0 sparse_method=uniform add_species=T n_sparse=10}

gap_fit 
energy_parameter_name=energy 
force_parameter_name=forces 
do_copy_at_file=F 
sparse_separate_file=T 
gp_file=GAP_3b.xml 
at_file=train.xyz 
default_sigma={0.008 0.04 0 0} 
gap={distance_2b cutoff=4.0 covariance_type=ard_se delta=0.5 theta_uniform=1.0 sparse_method=uniform add_species=T n_sparse=10 : 
        angle_3b cutoff=3.5 covariance_type=ard_se delta=0.5 theta_fac=0.5 add_species=T n_sparse=30 sparse_method=uniform}



quip E=T F=T atoms_filename=train.xyz param_filename=GAP.xml | grep AT | sed 's/AT//' > quip_train.xyz

'''