import itertools
from typing import Tuple, Union

import numpy as np
import torch
from torch import nn, Tensor
from torch.autograd.functional import jacobian

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

    def _forward(self, r):
        return 1.0 / torch.linalg.norm(r[:, 0] - r[:, 1], dim=-1) ** 2

    def _div(self, r):
        diff = r[:, 0] - r[:, 1]
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

    def __init__(self, ls):
        super().__init__()
        self.ls = ls

    def _forward(self, r):
        ri, rj, rk = r[:, 0], r[:, 1], r[:, 2]
        norms = (
            torch.linalg.norm(ri - rj, dim=-1)
            + torch.linalg.norm(ri - rk, dim=-1)
            + torch.linalg.norm(rj - rk, dim=-1)
        )
        return torch.exp(-norms / self.ls)


class GeomFunc2BodyInvDist(ScalarFunc):
    """
    Geometry function that takes the form of:

    .. math::
        G(R_i, R_j) = \\frac{1}{|R_i - R_j|}
    """

    k = 2

    def _forward(self, r):
        print(r)
        return 1.0 / torch.linalg.norm(r[:, 0] - r[:, 1], dim=-1)

    def _div(self, r):
        diff = r[:, 0] - r[:, 1]
        #print(r) ### distancia
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
        dotuv = torch.sum((ra - rb) * (rc - rb), dim=-1)
        denominator = torch.linalg.norm(ra - rb, dim=-1) * torch.linalg.norm(
            rc - rb, dim=-1
        )
        return torch.arccos(torch.clamp(dotuv / denominator, min=-1.0, max=1.0))

    def _div(self, r):
        ra, rb, rc = r[:, 0], r[:, 1], r[:, 2]
        vab = ra - rb
        vcb = rc - rb

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
        dotuv = torch.tensordot(ra - rb, rc - rb, dims=([1], [1]))
        denominator = torch.linalg.norm(ra - rb, dim=-1) * torch.linalg.norm(
            rc - rb, dim=-1
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



'''
from mbtr_grad.mbtr_python_torch import (
    mbtr_python,
    WeightFunc2BodyInvDist,
    GeomFunc2BodyInvDist,
    DistFuncGaussian,
)
'''

aspirin = {
    'z': np.asarray([6, 6, 6, 6, 6, 6, 6, 8, 8, 8, 6, 6, 8, 1, 1, 1, 1, 1, 1, 1, 1]),
    'r': np.asarray([
        [+1.967773, -1.138310, -0.543556],
        [+0.645441, +0.992465, -1.702570],
        [+2.234543, -0.777031, -1.830163],
        [+1.581020, +0.289498, -2.446978],
        [-3.016591, +1.741695, +0.612453],
        [+0.878228, -0.578833, +0.189787],
        [+0.263598, +0.519752, -0.384926],
        [+1.503426, -1.267264, +2.463581],
        [-2.236631, +0.279797, -1.121948],
        [-0.715723, -1.175512, +1.929332],
        [+0.633549, -0.964428, +1.667591],
        [-2.016979, +0.998229, -0.174489],
        [-0.753226, +1.137627, +0.363041],
        [-0.693787, -1.606394, +2.839317],
        [+2.522198, -1.999940, -0.132890],
        [+0.118692, +1.850180, -2.156963],
        [+3.099397, -1.279973, -2.334072],
        [+1.852263, +0.669541, -3.409804],
        [-4.006237, +1.796931, +0.063728],
        [-3.090694, +1.158956, +1.570798],
        [-2.624328, +2.785921, +0.842982] 
    ])
}

aspirin_range = np.linspace(0, 1.1, 500)
aspirin_rep, aspirin_rep_div = mbtr_python(
    z=aspirin['z'], r=aspirin['r'][None],
    order=2, grid=aspirin_range,
    weightf=WeightFunc2BodyInvDist(), 
    geomf=GeomFunc2BodyInvDist(),
    distf=DistFuncGaussian(2**-4.5)
)

print(aspirin_rep.shape, aspirin_rep_div.shape)
import matplotlib.pyplot as plt 
plt.plot( aspirin_rep[0,0,:,:].T )
plt.show()
plt.plot( aspirin_rep[0,1,:,:].T )
plt.show()
plt.plot( aspirin_rep[0,2,:,:].T )
plt.show()
# Should display:
# (1, 3, 3, 500) (1, 3, 3, 500, 21, 3)