import importlib
import sys
from .BasePartition import BasePartition

_lazy_imports = {
    # Star imports: the entire module will be imported and its public names injected.
    "data_mining": ("...miscellaneous.data_mining", None),
    "SOAP_tools": ("..miscellaneous.SOAP_tools", None),
    
    # Standard lazy imports.
    "np": ("numpy", None),
    "svd_scipy": ("scipy.linalg", "svd"),
    "svd_np": ("numpy.linalg", "svd"),
    "qr": ("numpy.linalg", "qr"),
    "norm": ("numpy.linalg", "norm"),
    "heapq": ("heapq", None),
    "deque": ("collections", "deque"),
    "tqdm": ("tqdm", None),
    "linear_sum_assignment": ("scipy.optimize", "linear_sum_assignment"),
    "cdist": ("scipy.spatial.distance", "cdist"),
    
    # Typing
    "List": ("typing", "List"),
    "Tuple": ("typing", "Tuple"),
    "Optional": ("typing", "Optional"),
    "Dict": ("typing", "Dict"),
}

def __getattr__(name):
    if name in _lazy_imports:
        module_path, attribute = _lazy_imports[name]
        try:
            # Handle relative imports using __package__ if the path starts with a dot.
            if module_path.startswith('.'):
                mod = importlib.import_module(module_path, package=__package__)
            else:
                mod = importlib.import_module(module_path)
            value = getattr(mod, attribute) if attribute is not None else mod

            # For modules that were originally imported using a star import,
            # inject their public names into globals() to emulate "from ... import *"
            if name in ("data_mining", "SOAP_tools"):
                globals().update({k: v for k, v in mod.__dict__.items() if not k.startswith("_")})
                globals()[name] = mod
            else:
                globals()[name] = value  # Cache the value for future accesses
            return value
        except ImportError as e:
            sys.stderr.write(f"An error occurred while lazily importing {name}: {e}\n")
            raise
    raise AttributeError(f"module {__name__} has no attribute {name}")

class Network_builder(BasePartition):
    """

    """

    def __init__(self, file_location: str = None, name: str = None, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)

    def aligned_euclidean_distance(self, M1, M2):
        """
        Calcula la distancia Euclídea total mínima entre dos matrices M1 y M2
        (con N muestras y M variables) teniendo en cuenta que las muestras pueden
        no estar alineadas, mediante asignación óptima.

        Parámetros:
        -----------
        M1, M2 : numpy.ndarray
            Matrices de tamaño (N, M) a comparar.

        Retorna:
        --------
        total_distance : float
            Suma de las distancias Euclidianas entre las muestras emparejadas.
        """
        # Calcula la matriz de distancias entre todas las muestras de M1 y M2.
        D = cdist(M1, M2, metric='euclidean')
        
        # Aplica el algoritmo húngaro para obtener la asignación óptima.
        row_ind, col_ind = linear_sum_assignment(D)
        
        # Suma de las distancias correspondientes a la asignación.
        total_distance = D[row_ind, col_ind].sum()
        
        return total_distance

    def minimax_dijkstra(self, distance_matrix, start, goal):
        """
        Finds the minimax path between 'start' and 'goal' using a modified Dijkstra's algorithm,
        where the path cost is defined as the maximum edge weight along the path.

        Parameters:
        -----------
        distance_matrix : numpy.ndarray
            A symmetric distance matrix where distance_matrix[i, j] is the cost of the edge between
            nodes i and j. If there is no connection, it should be set to np.inf.
        start : int
            The index of the starting node.
        goal : int
            The index of the goal node.

        Returns:
        --------
        tuple (path, cost) or (None, np.inf)
            'path' is a list of nodes representing the found path, and 'cost' is the minimax cost
            (i.e., the maximum edge weight along the path).
        """
        n = distance_matrix.shape[0]
        # d[i] holds the minimax cost (i.e. best maximum edge weight) found to reach node i.
        d = np.full(n, np.inf)
        d[start] = 0
        # parent pointer for reconstructing the path
        parent = [-1] * n
        # Priority queue: each element is (current minimax cost, current node)
        heap = [(0, start)]
        
        while heap:
            cost, u = heapq.heappop(heap)
            # If we already found a better path to u, skip this one.
            if cost > d[u]:
                continue
            # Check all neighbors of u.
            for v in range(n):
                if v == u or distance_matrix[u, v] == np.inf:
                    continue
                # The cost to reach v via u is the maximum of the cost so far and the edge u-v.
                new_cost = max(cost, distance_matrix[u, v])
                if new_cost < d[v]:
                    d[v] = new_cost
                    parent[v] = u
                    heapq.heappush(heap, (new_cost, v))
        
        if d[goal] == np.inf:
            return None, np.inf
        
        # Reconstruct the path from start to goal.
        path = []
        cur = goal
        while cur != -1:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        
        return path, d[goal]

    def bfs_threshold(self, distance_matrix, start, goal, threshold):
        """
        Performs a BFS to check if there is a path from 'start' to 'goal'
        using only edges with weight <= threshold.
        """
        n = distance_matrix.shape[0]
        visited = [False] * n
        q = deque([start])
        visited[start] = True
        while q:
            u = q.popleft()
            if u == goal:
                return True
            for v in range(n):
                if not visited[v] and distance_matrix[u, v] <= threshold:
                    visited[v] = True
                    q.append(v)
        return False

    def minimax_bfs(self, distance_matrix, start, goal):
        """
        Finds the minimax path between 'start' and 'goal' using binary search over the unique
        edge weights and BFS for connectivity testing.

        Returns:
        --------
        tuple (path, threshold) or (None, np.inf)
            'path' is the list of nodes representing the found path, and 'threshold' is the minimax cost.
        """
        # Get all unique finite edge weights.
        unique_weights = np.unique(distance_matrix[distance_matrix != np.inf])
        unique_weights.sort()
        
        low, high = 0, len(unique_weights) - 1
        best_threshold = None
        # Binary search to find the minimal threshold that allows a path.
        while low <= high:
            mid = (low + high) // 2
            if self.bfs_threshold(distance_matrix, start, goal, unique_weights[mid]):
                best_threshold = unique_weights[mid]
                high = mid - 1
            else:
                low = mid + 1
        
        if best_threshold is None:
            return None, np.inf
        
        # Reconstruct the path using BFS, keeping track of parent pointers.
        n = distance_matrix.shape[0]
        parent = [-1] * n
        visited = [False] * n
        q = deque([start])
        visited[start] = True
        
        while q:
            u = q.popleft()
            if u == goal:
                break
            for v in range(n):
                if not visited[v] and distance_matrix[u, v] <= best_threshold:
                    visited[v] = True
                    parent[v] = u
                    q.append(v)
        
        if parent[goal] == -1:
            return None, np.inf
        
        # Reconstruct the path.
        path = []
        cur = goal
        while cur != -1:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        
        return path, best_threshold


    def minimax_astar(self, distance_matrix, start, goal):
        """
        Finds the minimax path between 'start' and 'goal' using the A* algorithm,
        where the cost of a path is defined as the maximum edge weight along that path.
        
        Parameters:
        -----------
        distance_matrix : numpy.ndarray
            A symmetric distance matrix where distance_matrix[i, j] is the cost of the edge
            between nodes i and j. If there is no connection, it should be set to np.inf.
        start : int
            The index of the starting node.
        goal : int
            The index of the goal node.
        
        Returns:
        --------
        tuple (path, cost) or (None, np.inf)
            'path' is a list of nodes representing the found path, and 'cost' is the minimax cost
            (i.e., the maximum edge weight along the path).
        """
        n_nodes = distance_matrix.shape[0]
        
        # Each element in the priority queue (open set) is a tuple:
        # (f, g, current_node, path) where:
        #   g: maximum edge cost along the path from 'start' to the current node
        #   h: heuristic (we use the direct edge cost from the current node to the goal)
        #   f = max(g, h)
        open_set = []
        
        # Initialize the start node.
        # If a direct edge from start to goal exists, use it as the heuristic; otherwise, use 0.
        h_start = distance_matrix[start, goal] if distance_matrix[start, goal] != np.inf else 0
        f_start = max(0, h_start)
        heapq.heappush(open_set, (f_start, 0, start, [start]))
        
        # best_cost keeps track of the minimum g (minimax cost) found for each node.
        best_cost = {start: 0}
        
        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            
            # If we have reached the goal, return the path and its minimax cost.
            if current == goal:
                return path, g
            
            # Explore all neighbors of the current node.
            for neighbor in range(n_nodes):
                # Skip self-loops and non-existent edges.
                if neighbor == current or distance_matrix[current, neighbor] == np.inf:
                    continue
                
                # The new cost (new_g) is the maximum of the current cost and the edge cost.
                edge_cost = distance_matrix[current, neighbor]
                new_g = max(g, edge_cost)
                
                # Heuristic: use the direct edge from neighbor to goal if available, or 0 otherwise.
                h = distance_matrix[neighbor, goal] if distance_matrix[neighbor, goal] != np.inf else 0
                new_f = max(new_g, h)
                
                # Update only if this path to the neighbor is better than any previously found.
                if neighbor not in best_cost or new_g < best_cost[neighbor]:
                    best_cost[neighbor] = new_g
                    heapq.heappush(open_set, (new_f, new_g, neighbor, path + [neighbor]))
        
        # If no path is found, return None.
        return None, np.inf

    def principal_angles(self,M1, M2):
        """
        Calcula los ángulos principales entre los subespacios generados por las columnas de M1 y M2.

        Parámetros:
        -----------
        M1 : numpy.ndarray
            Matriz de tamaño [muestras, variables] cuyo span se compara.
        M2 : numpy.ndarray
            Matriz de tamaño [muestras, variables] cuyo span se compara.

        Retorna:
        --------
        angles : numpy.ndarray
            Array con los ángulos principales (en radianes) entre los subespacios.
        """
        # Asegurarse de que M1 y M2 sean matrices 2D.
        M1 = np.atleast_2d(M1)
        M2 = np.atleast_2d(M2)
        
        # Obtener bases ortonormales de los espacios columna usando descomposición QR.
        Q1, _ = qr(M1)
        Q2, _ = qr(M2)
        
        # Calcular la matriz de cosenos entre las bases.
        C = np.dot(Q1.T, Q2)
        
        # Obtener los valores singulares de C, que son los cosenos de los ángulos principales.
        _, s, _ = svd(C)
        
        # Corregir posibles errores numéricos asegurando que s se encuentre en [-1, 1].
        s = np.clip(s, -1, 1)
        
        # Calcular los ángulos principales (en radianes)
        angles = np.arccos(s)
        
        return angles

    def build_networks(self, ):
        """
        """
        r_cut_list = np.linspace(3, 6, 10)
        r_cut_mu, r_cut_sd = 2, 5
        r_cut_weigth = np.exp(-0.5 * ((r_cut_list - r_cut_mu) / r_cut_sd) ** 2)
        path_relevance = np.zeros( (self.N,self.N) )

        for r_cut_idx, r_cut_val in tqdm(enumerate(r_cut_list), desc="r_cut"):

            composition_data = self.get_composition_data()
            uniqueAtomLabels = composition_data['uniqueAtomLabels']
            compositions = composition_data['composition_data']
            energies = composition_data['energy_data']

            params = {}

            # =========== =========== =========== =========== #
            r_cut = params.get('r_cut', r_cut_val)
            n_max, l_max = params.get('n_max', 4), params.get('l_max', 4)
            sigma = params.get('sigma', 0.01)
            cache = params.get('cache', False)
            descriptors_by_species, atom_info_by_species = self.get_SOAP( 
                    r_cut=r_cut, 
                    n_max=n_max, 
                    l_max=l_max, 
                    sigma=sigma, 
                    save=False,
                    cache=cache )

            # =========== =========== =========== =========== #
            n_components = params.get('components', 5) 
            compress_model = params.get('compress_model', 'umap') 
            print(f" >< Compress model {compress_model} ({n_components}).")
            compressor = Compress(unique_labels=self.uniqueAtomLabels)
            compressed_data = compressor.verify_and_load_or_compress(descriptors_by_species, method=compress_model, n_components= {k:n_components for k, d in descriptors_by_species.items()}, 
                                load=False, save=False )

            # =========== =========== =========== =========== #
            '''
            cluster_model = params.get('cluster_model', 'dbscan')
            eps, min_samples = params.get('eps', 0.7), params.get('min_samples', 2) 
            print(f" >< Cluster model {cluster_model} (eps:{eps}, samples:{min_samples}).")
            cluster_analysis_results = {}
            for species_idx, species in enumerate(self.uniqueAtomLabels):
                analyzer = ClusteringAnalysis()
                cluster_analysis_results[species] = analyzer.cluster_analysis(compressed_data[species], params={'eps':eps, 'min_samples':min_samples}, 
                                                output_dir=f'./cluster_results/{species}', use_cache=False, methods=[cluster_model])
                print( f' Especie: {species} {cluster_model} clusters: { len(set(cluster_analysis_results[species][cluster_model]))}')
            '''

            #SOAP_compress_matrix = [ np.zeros( (c1.AtomPositionManager.atomCount, n_components) ) for i1, c1 in enumerate(self.containers) ]
            SOAP_compress_matrix = [ np.zeros( (c1.AtomPositionManager.atomCount, descriptors_by_species['C'].shape[1]) ) for i1, c1 in enumerate(self.containers) ]

            for specie_i, specie in enumerate(self.uniqueAtomLabels):
                for aibs_i, aibs in enumerate(atom_info_by_species[specie]):
                    SOAP_compress_matrix[aibs[0]][aibs[1],:] = descriptors_by_species[specie][aibs_i,:]
                    #SOAP_compress_matrix[aibs[0]][aibs[1],:] = compressed_data[specie][aibs_i,:]

            distance_matrix = np.zeros( (self.N,self.N) )
            for i1, c1 in enumerate(self.containers):
                for i2, c2 in enumerate(self.containers):
                    if i1 <= i2:
                        
                        if np.sum(np.abs(c1.AtomPositionManager.atomCountByType - c2.AtomPositionManager.atomCountByType)) < 0.01:
                            for specie in self.uniqueAtomLabels:

                                SCM_c1 = SOAP_compress_matrix[i1][np.array(c1.AtomPositionManager.atomLabelsList) == specie]
                                SCM_c2 = SOAP_compress_matrix[i2][np.array(c2.AtomPositionManager.atomLabelsList) == specie]
                                #dist_c1c2 = np.linalg.norm(self.principal_angles(SCM_c1.T, SCM_c2.T))
                                dist_c1c2 = self.aligned_euclidean_distance(SCM_c1, SCM_c2)

                                distance_matrix[i1, i2] += dist_c1c2
                                distance_matrix[i2, i1] += dist_c1c2

                        else:
                            distance_matrix[i1, i2] = np.inf
                            distance_matrix[i2, i1] = np.inf
            
            start_node, goal_node = 0, 6
            print("Minimax Dijkstra approach:")
            path, cost = self.minimax_dijkstra(distance_matrix, start_node, goal_node)
            print("Path:", path)
            print("Minimax cost (maximum edge on the path):", cost)
            
            print("Minimax A* approach:")
            path, cost = self.minimax_astar(distance_matrix, start_node, goal_node)
            print("Path:", path)
            print("Minimax cost (maximum edge on the path):", cost)
            
            print("\nMinimax BFS with binary search approach:")
            path, cost = self.minimax_bfs(distance_matrix, start_node, goal_node)
            print("Path:", path)
            print("Minimax cost (threshold):", cost)

            for n1,n2 in zip(path[:-1], path[1:]):
                path_relevance[n1,n2] += 1#r_cut_weigth[r_cut_i]
                path_relevance[n2,n1] += 1#r_cut_weigth[r_cut_i]

        import matplotlib.pyplot as plt
        plt.matshow(path_relevance)
        plt.show()

        return distance_matrix





























