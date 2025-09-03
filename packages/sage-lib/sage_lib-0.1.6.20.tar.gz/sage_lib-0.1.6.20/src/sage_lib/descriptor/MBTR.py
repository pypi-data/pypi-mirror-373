import itertools
from typing import Tuple, Union

import numpy as np
import torch
from torch import nn, Tensor
from torch.autograd.functional import jacobian
from scipy.spatial.distance import cdist

try:
    from ..master.FileManager import FileManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing FileManager: {str(e)}\n")
    del sys

try:
    from ..master.AtomicProperties import AtomicProperties
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomicProperties: {str(e)}\n")
    del sys


__all__ = [
    "WeightFunc2BodyIdentity",
    "WeightFunc2BodyInvDist",
    "WeightFunc3BodyUnity",
    "WeightFunc3BodyExpInvDist",
    "GeomFunc2BodyInvDist",
    "GeomFunc3BodyAngle",
    "GeomFunc3BodyCosAngle",
    "DistFuncGaussian",
    "mbtr_python",
]


class ScalarFunc(nn.Module):
    """
    Base class for all scalar functions (geometry and weight functions).
    If an algebraic derivative function is not defined, we use PyTorch's
    auto-differentiation function to calculate a derivative value.
    """

    k = 1

    def _check_r_shape(self, r):
        if len(r.shape) != 3:
            raise ValueError("r must have a shape of [batch_size, k=%d, xyz]" % self.k)
        if r.shape[1] != self.k:
            raise ValueError(
                "The second dim of r must be %d, got %d" % (self.k, r.shape[1])
            )
        if r.shape[2] != 3:
            raise ValueError(
                "Expected %d Cartesian coordinates, got %d" % (3, r.shape[2])
            )

    def forward(self, r):
        self._check_r_shape(r)
        return self._forward(r)

    def div(self, r):
        """Fallback to PyTorch auto-differentiation if not implemented."""
        self._check_r_shape(r)

        try:
            return self._div(r)
        except NotImplemented:
            return jacobian(lambda x: self(x).sum(dim=0), r, vectorize=True)

    def _forward(self, r):
        raise NotImplemented()

    def _div(self, r):
        raise NotImplemented()

class Lattice(nn.Module):
    def __init__(self, lattice_vectors):
        super().__init__()
        self.latticeVectors = torch.tensor(lattice_vectors, dtype=torch.float64)

    def minimum_image_distance(self, r1, r2, n_max=1, return_vector=False):
        # Ensure r1 and r2 are PyTorch tensors
        r1 = r1.to(torch.float64)
        r2 = r2.to(torch.float64)

        # Generate all combinations of cell indices
        n_values = torch.arange(-n_max, n_max + 1, dtype=torch.float64)
        n_combinations = torch.cartesian_prod(n_values, n_values, n_values)
        
        # Calculate all images of the second point
        r2_images = r2 + torch.matmul(n_combinations, self.latticeVectors.T)
        
        # Calculate distances between r1 and all images of r2
        distances = torch.norm(r1 - r2_images, dim=1)
        
        # Find and return the minimum distance
        min_index = torch.argmin(distances)
        d_min = distances[min_index]

        # Si se solicita el vector, devuélvelo junto con la distancia
        if return_vector:
            closest_point = r2_images[min_index]
            return d_min, closest_point - r1

        return d_min

class WeightFunc2BodyIdentity(ScalarFunc):
    """
    2-body weighting function of constant 1.
    """

    k = 2

    def _forward(self, r):
        return torch.ones_like(r[:, 0, 0])

    def _div(self, r):
        return torch.zeros_like(r)


class WeightFunc2BodyInvDist(ScalarFunc):
    """
    2-body weighting function that takes the form of:

    .. math::
        w(R_i, R_j) = \\frac{1}{|R_i - R_j|^2}
    """
    k = 2

    def __init__(self, lattice_vectors):
        super().__init__()
        self.lattice = Lattice(lattice_vectors)

    def _forward(self, r):
        batch_size = r.shape[0]
        distances = torch.empty(batch_size, dtype=torch.float32)

        for i in range(batch_size):
            r1 = r[i, 0]
            r2 = r[i, 1]
            distances[i] = self.lattice.minimum_image_distance(r1, r2)**2

        return 1.0 / distances

    def _div(self, r):
        d_min, diff = self.lattice.minimum_image_distance(r[:, 0], r[:, 1], return_vector=True)
        norm = torch.linalg.norm(diff, dim=-1, keepdim=True)
        d = -2.0 / norm**4 * diff
        return torch.cat([d.unsqueeze(1), -d.unsqueeze(1)], dim=1)


class WeightFunc3BodyUnity(ScalarFunc):
    """
    3-body weighting function that always returns 1.0:
    """

    k = 3

    def _forward(self, r):
        return torch.ones_like(r[:, 0, 0])

    def _div(self, r):
        return torch.zeros_like(r)


class WeightFunc3BodyExpInvDist(ScalarFunc):
    """
    3-body weighting function that takes the form of:

    .. math::
        w(R_i, R_j, R_k) = exp\\left(-\\frac{|R_i-R_j|+|R_j-R_k|+|R_k-R_i|}{ls}
        \\right)
    """

    k = 3

    def __init__(self, ls, lattice_vectors):
        super().__init__()
        self.ls = ls
        self.lattice = Lattice(lattice_vectors)

    def _forward(self, r):
        ri, rj, rk = r[:, 0], r[:, 1], r[:, 2]
        dist_ri_rj = self.lattice.minimum_image_distance(ri, rj)
        dist_ri_rk = self.lattice.minimum_image_distance(ri, rk)
        dist_rj_rk = self.lattice.minimum_image_distance(rj, rk)
        pr
        norms = dist_ri_rj + dist_ri_rk + dist_rj_rk
        return torch.exp(-norms / self.ls)

class GeomFunc2BodyInvDist(ScalarFunc):
    """
    Geometry function that takes the form of:

    .. math::
        G(R_i, R_j) = \\frac{1}{|R_i - R_j|}
    """

    k = 2

    def __init__(self, lattice_vectors):
        super().__init__()
        self.lattice = Lattice(lattice_vectors)

    def _forward(self, r):
        batch_size = r.shape[0]
        distances = torch.empty(batch_size, dtype=torch.float32)

        for i in range(batch_size):
            r1 = r[i, 0]
            r2 = r[i, 1]
            distances[i] = self.lattice.minimum_image_distance(r1, r2)

        return 1.0 / distances

    def _div(self, r):
        d_min, diff = self.lattice.minimum_image_distance(r[:, 0], r[:, 1], return_vector=True)
        norm = torch.linalg.norm(diff, dim=-1, keepdim=True)
        d = -1.0 / norm**3 * diff
        return torch.cat([d.unsqueeze(1), -d.unsqueeze(1)], dim=1)

class GeomFunc3BodyAngle(ScalarFunc):
    """
    Geometry function of angle function:

    .. math::
        G(R_i, R_j, R_k) = \\arccos(\\frac{(R_i-R_j)\\cdot(R_k-R_j)}{|R_i-R_j|
        \\cdot|R_k-R_j|})
    """

    k = 3

    def _forward(self, r):
        ra, rb, rc = r[:, 0], r[:, 1], r[:, 2]

        d_min_ab, diff_ab = self.lattice.minimum_image_distance(ra, rb, return_vector=True)
        d_min_cb, diff_cb = self.lattice.minimum_image_distance(rc, rb, return_vector=True)

        dotuv = torch.sum(diff_ab * diff_cb, dim=-1)
        denominator = torch.linalg.norm(diff_ab, dim=-1) * torch.linalg.norm(
            diff_cb, dim=-1
        )
        return torch.arccos(torch.clamp(dotuv / denominator, min=-1.0, max=1.0))

    def _div(self, r):
        ra, rb, rc = r[:, 0], r[:, 1], r[:, 2]

        d_min_ab, diff_ab = self.lattice.minimum_image_distance(ra, rb, return_vector=True)
        d_min_cb, diff_cb = self.lattice.minimum_image_distance(rc, rb, return_vector=True)

        vab = diff_ab # ra - rb
        vcb = diff_cb # rc - rb

        dotuv = torch.sum(vab * vcb, dim=-1)
        dab = torch.linalg.norm(vab, dim=-1)
        dcb = torch.linalg.norm(vcb, dim=-1)
        cos = dotuv / (dab * dcb)

        factor = -1 / torch.sqrt(1 - torch.clamp(cos**2, min=0.0, max=1 - 1e-7))
        da = (dab**2 * vcb - dotuv * vab) / (dab**3 * dcb)
        db = (
            dab * dcb * (-vab - vcb) + dotuv * (dcb / dab * vab + dab / dcb * vcb)
        ) / (dab**2 * dcb**2)
        dc = (dcb**2 * vab - dotuv * vcb) / (dcb**3 * dab)

        return factor * torch.cat(
            [da.unsqueeze(1), db.unsqueeze(1), dc.unsqueeze(1)], dim=1
        )


class GeomFunc3BodyCosAngle(ScalarFunc):
    """
    Geometry function of cosine function:

    .. math::
        G(R_i, R_j, R_k) = \\frac{(R_i-R_j)\\cdot(R_k-R_j)}{|R_i-R_j|
        \\cdot|R_k-R_j|}
    """

    k = 3

    def _forward(self, r):
        ra, rb, rc = r[:, 0], r[:, 1], r[:, 2]

        d_min_ab, diff_ab = self.lattice.minimum_image_distance(ra, rb, return_vector=True)
        d_min_cb, diff_cb = self.lattice.minimum_image_distance(rc, rb, return_vector=True)

        dotuv = torch.tensordot(diff_ab, diff_cb, dims=([1], [1]))
        denominator = torch.linalg.norm(diff_ab, dim=-1) * torch.linalg.norm(
            diff_cb, dim=-1
        )
        return torch.maximum(-1.0, torch.minimum(1.0, dotuv / denominator))


class DistFuncGaussian(nn.Module):
    """
    Gaussian distribution function.
    """

    def __init__(self, sigma):
        super().__init__()
        self.const = float(1.0 / (sigma * np.sqrt(2.0)))

    def _check_shapes(self, val_range, geom_mean):
        assert len(val_range.shape) == 1, "val_range must be a 1d tensor."
        assert (
            len(geom_mean.shape) == 1
        ), "geom_mean must be a 1d tensor with first dim as batch size."

    def forward(self, val_range, geom_mean, *, dx):
        self._check_shapes(val_range, geom_mean)

        val_range = val_range.unsqueeze(0)
        geom_mean = geom_mean.unsqueeze(1)
        right = torch.erf((val_range + dx - geom_mean) * self.const)
        left = torch.erf((val_range - geom_mean) * self.const)
        return (right - left) / 2

    def div(self, val_range: Tensor, geom_mean: Tensor, *, dx):
        self._check_shapes(val_range, geom_mean)

        val_range = val_range.unsqueeze(0)
        geom_mean = geom_mean.unsqueeze(1)

        zr: Tensor = (val_range + dx - geom_mean) * self.const
        zl: Tensor = (val_range - geom_mean) * self.const

        return (-self.const / np.sqrt(np.pi)) * (
            torch.exp(-(zr**2)) - torch.exp(-(zl**2))
        )


class MBTR(nn.Module):
    def __init__(self, order, geomf, weightf, distf, grid):
        super().__init__()

        self.geomf = geomf
        self.weightf = weightf
        self.distf = distf

        self.order = order
        self.grid = nn.Parameter(torch.tensor(grid), requires_grad=False)

    def forward(self, r, z, compute_div=True):
        # z: torch.tensor((n_atoms,))
        # r: torch.tensor((batch, n_atoms, 3))
        elements = sorted(set(z))
        b_size = r.shape[0]
        grid_size = self.grid.size(0)
        coord_size = r.shape[2]
        n_atom = r.shape[1]
        dx = self.grid[1] - self.grid[0]
        full = slice(None, None, None)

        mbtr_shape = (b_size,) + (len(elements),) * self.order + (grid_size,)

        mbtr = torch.zeros(mbtr_shape, dtype=r.dtype, device=self.grid.device)
        mbtr_div = (
            torch.zeros(
                mbtr_shape + (n_atom, coord_size),
                dtype=r.dtype,
                device=self.grid.device,
            )
            if compute_div
            else None
        )

        for atom_ids in itertools.product(*([range(n_atom)] * self.order)):
            if len(set(atom_ids)) != len(atom_ids):
                # Contains duplicates
                continue

            zs = [elements.index(z[x]) for x in atom_ids]
            rs = r[:, atom_ids]

            gf = self.geomf(rs)
            wf = self.weightf(rs).unsqueeze(1)
            grid_values = self.distf(self.grid, gf, dx=dx)

            indexer = (full,) + tuple(zs) + (full,)
            mbtr[indexer] += wf * grid_values

            if compute_div:
                wf_div = self.weightf.div(rs)
                gf_div = self.geomf.div(rs)
                grid_div = self.distf.div(self.grid, gf, dx=dx)

                div = (
                    torch.bmm(
                        grid_values.unsqueeze(2),
                        wf_div.reshape((b_size, -1)).unsqueeze(1),
                    )
                    + torch.bmm(
                        grid_div.unsqueeze(2), gf_div.reshape((b_size, -1)).unsqueeze(1)
                    )
                    * wf.unsqueeze(2)
                ).reshape((b_size, grid_size, self.order, coord_size))
                mbtr_div[(indexer + (atom_ids, full))] += div

        if compute_div:
            return mbtr, mbtr_div
        return mbtr


@torch.no_grad()
def mbtr_python(
    z: "np.ndarray",
    r: "np.ndarray",
    grid: Union["np.ndarray", Tuple],
    order: int,
    weightf: nn.Module,
    distf: nn.Module,
    geomf: nn.Module,
    flatten=False,
    device="cpu",
    as_numpy=True,
) -> Tuple["np.ndarray", "np.ndarray"]:
    """
    Compute MBTR using PyTorch tensor library.

    :param z: Element types. (NAtom)
    :param r: Coordinates of atoms. (Batch, NAtom, 3)
    :param order: Order of MBTR.
    :param weightf: Weighting function.
    :param distf: Distribution function.
    :param geomf: Geometry function.
    :param grid: Grid definition.
    :param flatten: Whether to flatten representation.
    :param device: Device.
    :param as_numpy: As numpy array.
    :return: MBTR tensor.
    """
    if isinstance(grid, tuple):
        grid = np.linspace(*grid)

    model = MBTR(
        order=order,
        weightf=weightf,
        distf=distf,
        geomf=geomf,
        grid=grid,
    ).to(device)

    torch_r = torch.tensor(r).to(device)
    rep, rep_div = model(torch_r, z, compute_div=True)

    if as_numpy:
        rep, rep_div = rep.cpu().numpy(), rep_div.cpu().numpy()

    if flatten:
        return (
            rep.reshape((len(rep), -1)),
            rep_div.reshape((len(rep_div), -1, r.shape[1], r.shape[2])),
        )
    return rep, rep_div


class MDTR(FileManager, AtomicProperties):
    """
    """

    def __init__(self, lattice_vectors:np.array=None, atomLabelsList:np.array=None, AtomicNumberList:np.array=None, atomPositions:np.array=None):
        '''
        '''
        FileManager.__init__(self, )
        AtomicProperties.__init__(self)

        self._lattice_vectors = lattice_vectors
        self._atomLabelsList = atomLabelsList
        self._AtomicNumberList = AtomicNumberList
        self._atomPositions = atomPositions

        self._weightf = None
        self._geomf = None
        self._distf = None
        self._grid = None

        self._order = None
        self._flatten = True

        self.rep, self.rep_div = None, None

        self._similarity_matrix = None

    @property
    def atomLabelsList(self):
        """

        """
        if type(self._atomLabelsList) is not None:
            return np.array(self._atomLabelsList)
        elif type(self._AtomicNumberList) is not None: 
            self._atomLabelsList = np.array([self.atomic_id[num] for num in self._AtomicNumberList])
            return np.array(self._atomLabelsList)
        elif'_atomLabelsList' not in self.__dict__:
            raise AttributeError("Attribute _atomLabelsList must be initialized.")
        else:
            return None

    @property
    def AtomicNumberList(self):
        """

        """
        if not self._AtomicNumberList is None:
            return np.array(self._AtomicNumberList)
        elif not self._atomLabelsList is None: 
            self._AtomicNumberList = np.asarray([self._atomic_numbers[num] for num in self._atomLabelsList])
            return np.array(self._AtomicNumberList)
        elif'_atomLabelsList' not in self.__dict__:
            raise AttributeError("Attribute _AtomicNumberList must be initialized.")
        else:
            return None

    @property
    def rep_div(self):
        """

        """
        if self._rep_div is None:
            self._rep, self._rep_div =  self.get_mdtr()
            return self._rep_div
        else:
            return self._rep_div

    @property
    def rep(self):
        """

        """
        if self._rep is None:
            self._rep, self._rep_div =  self.get_mdtr()
            return self._rep
        else:
            return self._rep

    @property
    def similarity_matrix(self):
        """

        """
        if self._similarity_matrix is None:
            self._similarity_matrix =  self.get_selfsimilarity_matrix( (np.sum( self.rep_div[0,:,:,:]**2, axis=2)**0.5).T )
            return self._similarity_matrix
        else:
            return self._similarity_matrix

    def set_parameters(self, order:int=2, flatten:bool=True):
        '''
        '''
        if order == 2:
            self._weightf = WeightFunc2BodyInvDist(self.lattice_vectors)
            self._geomf = GeomFunc2BodyInvDist(self.lattice_vectors)
            self._distf = DistFuncGaussian(2**-4.5)
            self._order = order
            self._flatten = flatten
            self._grid = np.linspace(0, 1.1, 500)

    def get_mdtr(self, order:int=2, flatten:bool=True, store:bool=True):
        self.set_parameters(order=order, flatten=flatten)

        rep, rep_div = mbtr_python(
            z=self.AtomicNumberList, r=self.atomPositions[None],
            order=self.order, grid=self.grid,
            weightf=self.weightf, 
            geomf=self.geomf,
            distf=self.distf,
            flatten=self.flatten
        )

        if store:
            self.rep, self.rep_div = rep, rep_div

        return rep, rep_div

    def get_selfsimilarity_matrix(self, descriptor):

        return self.get_similarity_matrix(descriptor, descriptor)

    def get_similarity_matrix(self, descriptor_A, descriptor_B, normalize:bool=False, metric='cosine'):

        # Normalizar los vectores para que sean de magnitud unitaria

        vectors_A = descriptor_A / np.linalg.norm(descriptor_A, axis=1, keepdims=True) if normalize else descriptor_A
        vectors_B = descriptor_B / np.linalg.norm(descriptor_B, axis=1, keepdims=True) if normalize else descriptor_B

        # Calcular la matriz de similitud utilizando distancia de coseno
        similarity_matrix = 1 - cdist(vectors_A, vectors_B, metric)

        return similarity_matrix

    def find_related_atoms_groups(self, similarity_matrix=None, ID=None, threshold:float=0.82, ID_filter:bool=True):
        """
        Encuentra grupos de átomos relacionados basados en una matriz de similitud y un umbral.

        Parámetros:
        similarity_matrix : np.array
            Matriz de similitud de los átomos.
        threshold : float
            Umbral para considerar que dos átomos están relacionados.

        Retorna:
        groups : list of sets
            Lista de conjuntos, donde cada conjunto contiene índices de átomos relacionados.
        """
        ID = ID if ID is not None else self.AtomicNumberList
        similarity_matrix = self.similarity_matrix if similarity_matrix is None else similarity_matrix

        n_atoms = similarity_matrix.shape[0]
        visited = np.zeros(n_atoms, dtype=bool)
        groups = []

        def dfs(atomo, grupo_actual):
            """Recorrido en profundidad para encontrar átomos relacionados."""
            for neighbor in range(n_atoms):
                if similarity_matrix[atomo, neighbor] > threshold and not visited[neighbor]:
                    if ID_filter and ID[atomo] == ID[neighbor]:
                        visited[neighbor] = True
                        grupo_actual.add(neighbor)
                        dfs(neighbor, grupo_actual)

        for atomo in range(n_atoms):
            if not visited[atomo]:
                visited[atomo] = True
                grupo_actual = {atomo}
                dfs(atomo, grupo_actual)
                groups.append(grupo_actual)

        return groups

'''
from mbtr_grad.mbtr_python_torch import (
    mbtr_python,
    WeightFunc2BodyInvDist,
    GeomFunc2BodyInvDist,
    DistFuncGaussian,
)
'''



'''
import matplotlib.pyplot as plt 

from sklearn.cluster import DBSCAN

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def dbscan_clustering(vectors, eps=0.5, min_samples=5):
    """
    Realiza clustering con DBSCAN.

    Args:
    - vectors (np.ndarray): Array de vectores.
    - eps (float): La distancia máxima entre dos muestras para que se consideren en el mismo vecindario.
    - min_samples (int): El número mínimo de muestras en un vecindario para que un punto sea considerado como punto central.

    Returns:
    - labels (np.ndarray): Etiquetas de cluster para cada punto.
    """
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(vectors)
    labels = clustering.labels_
    return labels

def optimal_number_of_clusters(vectors):
    sum_of_squared_distances = []
    silhouette_avg = []
    K = range(2, 3)  # Asumiendo un rango de 2 a 10 clusters

    for k in K:
        kmeans = KMeans(n_clusters=k)
        kmeans = kmeans.fit(vectors)
        sum_of_squared_distances.append(kmeans.inertia_)
        silhouette_avg.append(silhouette_score(vectors, kmeans.labels_))

    # Método del codo
    plt.figure(1)
    plt.plot(K, sum_of_squared_distances, 'bx-')
    plt.xlabel('Número de clusters')
    plt.ylabel('Suma de las distancias cuadradas')
    plt.title('Método del Codo para el número óptimo de clusters')
    
    # Índice de Silhouette
    plt.figure(2)
    plt.plot(K, silhouette_avg, 'bx-')
    plt.xlabel('Número de clusters')
    plt.ylabel('Promedio del índice de Silhouette')
    plt.title('Índice de Silhouette para el número óptimo de clusters')

    plt.show()

for n in range(-2,3):
    aspirin = {
        'z': np.asarray([1,1,1,1,8]),
        'r': np.asarray([
            [+6.0, -0.00, -0.00],
            [+3.0, +0.00, -0.00],       
            [+997.0, -0.00, -0.00],
            [+994.0, +0.00, -0.00],       
            [+1*n, +0.00, -0.00],
        ])
    }

    lattice_vectors = [[1000, 0, 0], [0, 1000, 0], [0, 0, 1000]]

    aspirin_range = np.linspace(0, 1.1, 500)
    aspirin_rep, aspirin_rep_div = mbtr_python(
        z=aspirin['z'], r=aspirin['r'][None],
        order=2, grid=aspirin_range,
        weightf=WeightFunc2BodyInvDist(lattice_vectors), 
        geomf=GeomFunc2BodyInvDist(lattice_vectors),
        distf=DistFuncGaussian(2**-4.5),
        flatten=True,
    )

    print(n, aspirin_rep.shape, aspirin_rep_div.shape)
    plt.figure(n)
    plt.plot(aspirin_rep[0,:] )
    #plt.plot( aspirin_rep[0,:] )
        # Plot 1
    for m in [0,3]:#range(4):
        #plt.figure(m)
        plt.plot( np.abs(aspirin_rep_div[0, :, m, 0]) )
        plt.title("Plot 1")
        plt.xlabel("x-axis label")
        plt.ylabel("y-axis label")
 

    #print( optimal_number_of_clusters( np.abs(aspirin_rep_div[0, :, :, 0]).T ) )

plt.show()

'''




