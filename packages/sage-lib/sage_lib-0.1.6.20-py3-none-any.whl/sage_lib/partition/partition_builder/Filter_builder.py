try:
    import numpy as np
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class Filter_builder(BasePartition):
    """
    A class for building filters related to simulations or theoretical calculations.
    Extends PartitionManager and provides methods to filter containers based on various criteria.
    """
    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)

    def filter_conteiners(self, filter_function:str, container_property:str=None, 
                          value:float=None, temperature:float=0, selection_number:int=None, ID:str=None,
                          traj:bool=False, verbose:bool=False, stochastic:bool=False) -> bool:
        """
        Filters the containers based on a given criterion.

        Parameters
        ----------
        filter_function : str
            One of 'over', 'below', 'close', 'far'.
        container_property : str, optional
            The property of the containers to base the filter on.
        value : float, optional
            The reference value for comparison.
        temperature : float, default=0
            Controls the "softness" of the selection. If 0, step function. If >0 and stochastic, use sigmoidal weights.
        selection_number : int, optional
            Number of structures to select. 
            - If deterministic and N is an integer, select N structures.
            - If deterministic and N is None, select all that meet the criterion.
            - If stochastic, select N structures according to probabilities. 
        ID : str, optional
            Atom ID if required by the property retrieval function.
        traj : bool, optional
            Not used in this example.
        verbose : bool, default=False
            Print verbose output.
        stochastic : bool, default=False
            If True, perform stochastic selection (probabilistic).
            If False, perform deterministic selection (step function).

        Returns
        -------
        bool
            True after filtering.
        """
        # Get the property values
        values = self.get_property(container_property, ID)

        # Determine the mask or probabilities based on the mode
        if not stochastic:

            # Deterministic mode: use step function
            mask = self._deterministic_mask(filter_function, values, value, temperature)

            # Now select according to selection_number
            selected_indices = np.where(mask)[0]

            if selection_number is not None and isinstance(selection_number, int):
                # If we want exactly N and N < number of selected, we can truncate
                # In pure deterministic mode, if there are more selected than needed, 
                # we just take the first N (or another criterion could be applied).
                if len(selected_indices) > selection_number:
                    selected_indices = selected_indices[:selection_number]
            # If selection_number is not provided or not an integer, 
            # we just take all that meet the criterion.

        else:
            # Stochastic mode
            # If temperature = 0, we use a step function and then choose uniformly
            # If temperature > 0, we use a sigmoidal (soft) function to define probabilities

            if temperature == 0:
                # Step function
                mask = self._deterministic_mask(filter_function, values, value, temperature=0)
                selected_indices = np.where(mask)[0]
                if selection_number is not None and isinstance(selection_number, int):
                    # Randomly choose N from those that meet the criterion
                    if len(selected_indices) > selection_number:
                        selected_indices = np.random.choice(selected_indices, size=selection_number, replace=False)
                # If selection_number not provided, select all
            else:
                # temperature > 0, use sigmoidal probabilities
                weights = self._stochastic_weights(filter_function, values, value, temperature)
                weights_sum = np.sum(weights)
                if weights_sum < 1e-10:
                    # Avoid division by zero
                    weights += 1e-4
                    weights_sum = np.sum(weights)
                
                # Probabilistic selection
                if selection_number is not None and isinstance(selection_number, int):
                    selected_indices = np.random.choice(len(values), size=selection_number, replace=False, p=weights/weights_sum)
                else:
                    # If no selection_number provided, one might select all but weighted by probability doesn't make sense without N.
                    # For simplicity, if no selection_number is given, select all indices with weight > 0.
                    selected_indices = np.where(weights > 0)[0]

        # Apply the selection
        final_mask = np.zeros(len(self.containers), dtype=bool)
        final_mask[selected_indices] = True
        if verbose:
            print(f"Filtering with function={filter_function}, property={container_property}, value={value}, T={temperature}, stochastic={stochastic}")
            print(f"Selected {len(selected_indices)} out of {len(self.containers)}")

        self.apply_filter_mask(final_mask)
        return True

    def sort_containers(self, sort_property: str, ID: str = None, ascending: bool = True, verbose: bool = False) -> list:
        """
        Sorts the containers based on a given property.

        Parameters
        ----------
        sort_property : str
            The property of the containers to sort by.
        ID : str, optional
            Atom ID if required by the property retrieval function.
        ascending : bool, default=True
            If True, sort in ascending order. If False, sort in descending order.
        verbose : bool, default=False
            Print verbose output.
l
        -------
        list
            Indices of the containers sorted based on the property.
        """
        # Get the property values
        values = self.get_property(sort_property, ID)

        # Generate indices sorted based on the values
        sorted_indices = np.argsort(values)

        # Reverse the order if descending is required
        if not ascending:
            sorted_indices = sorted_indices[::-1]

        if verbose:
            sort_order = "ascending" if ascending else "descending"
            print(f"Sorting containers by '{sort_property}' in {sort_order} order.")

        self.apply_sorting_order(sorted_indices)
        
        return sorted_indices

    def _deterministic_mask(self, filter_function:str, values:np.ndarray, value:float, temperature:float=0):
        """
        Create a boolean mask for deterministic filtering.
        If temperature=0, it acts like a strict threshold-based step function.
        """
        # Define step criteria based on filter_function
        if filter_function.lower() == 'over':
            mask = values > value
        elif filter_function.lower() == 'below':
            mask = values < value
        elif filter_function.lower() == 'close':
            # For temperature=0, treat close as exact match (or near match)
            # In practice, one may define a tolerance. For now, exact:
            # If needed, one could do something like: mask = np.abs(values - value) < 1e-8
            mask = np.isclose(values, value)
        elif filter_function.lower() == 'far':
            # Far: not close (assuming close means exactly equal at T=0)
            mask = ~np.isclose(values, value)
        else:
            raise ValueError(f"Unknown filter_function: {filter_function}")
        return mask

    def _stochastic_weights(self, filter_function:str, values:np.ndarray, value:float, temperature:float):
        """
        Compute weights (probabilities) for stochastic selection using a sigmoidal-like function.
        If filter_function is:
            'over':   w = 1/(1+exp(-(values - value)/T))
            'below':  w = 1/(1+exp((values - value)/T))
            'close':  w = exp(-((values - value)^2)/(2T^2))
            'far':    w = 1 - exp(-((values - value)^2)/(2T^2))
        """
        if filter_function.lower() == 'over':
            weights = 1 / (1 + np.exp(-(values - value)/temperature))
        elif filter_function.lower() == 'below':
            weights = 1 / (1 + np.exp((values - value)/temperature))
        elif filter_function.lower() == 'close':
            weights = np.exp(-((values - value)**2)/(2*temperature**2))
        elif filter_function.lower() == 'far':
            weights = 1 - np.exp(-((values - value)**2)/(2*temperature**2))
        else:
            raise ValueError(f"Unknown filter_function: {filter_function}")
        
        return weights

    def get_property(self, container_property:str=None, ID:str=None):
        """
        Retrieves the property values of containers for filtering.
        """
        
        # TODO:    SHUFFLE  SPLIT
        # Create the filter mask
        if container_property.upper() == 'FORCES':
            # Calculate the magnitude of the total force for each container
            values = [np.linalg.norm(c.AtomPositionManager.total_force) for c in self.containers]

        elif container_property.upper() == 'E':
            # Calculate the magnitude of the total force for each container
            values = [ c.AtomPositionManager.E for c in self.containers ]

        elif container_property.upper() == 'E/N':
            # Calculate the magnitude of the total force for each container
            values = [ c.AtomPositionManager.E/c.AtomPositionManager.atomCount for c in self.containers ]

        elif container_property.upper() == 'ID':
            # 
            values = [ c.AtomPositionManager.atom_ID_amount(ID) for c in self.containers ]

        elif container_property.upper() == 'IDX':
            values = list(range(len(self.containers)))

        elif container_property.upper() == 'N':
            values = [ c.AtomPositionManager.atomCount for c in self.containers ]

        elif container_property.upper() == 'EF':
            from sklearn.linear_model import Ridge
            
            composition_data = self.get_composition_data()
    
            atom_labels = composition_data['uniqueAtomLabels']
            # Compute the composition matrix X
            X = composition_data['composition_data']

            # Extract energies
            y = np.array([structure.AtomPositionManager.E for structure in self.containers])

            # Fit a Ridge regression model to obtain chemical potentials
            model = Ridge(alpha=1e-5, fit_intercept=False)
            model.fit(X, y)
            chemical_potentials = model.coef_
            formation_energies = y - X.dot(chemical_potentials)
            values = formation_energies

        else:
            raise ValueError(f"Unknown property: {container_property}")

        return np.array(values)

