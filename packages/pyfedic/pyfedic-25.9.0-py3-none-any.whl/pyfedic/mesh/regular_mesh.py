import numpy as np
from functools import cache

from ..cells import Q4, C8, Q4Q, C8Q
from .base_mesh import BaseMesh

class RegularBaseMesh(BaseMesh):
    """

    """

    def __init__(self, xlims, ylims, zlims=None, elt_size=16, order=1):
        ""

        if zlims is None:
            nex, ney = int((xlims[1]-xlims[0]) // elt_size), int((ylims[1]-ylims[0]) // elt_size)
            nnx, nny = nex+1, ney+1
            c00 = np.array([0, 1, nnx+1, nnx])
            c0 = np.arange(nex).repeat(4).reshape(nex,4) + c00.reshape(1,4).repeat(nex, axis=0)
            cell_type = Q4
            cells = np.arange(ney).repeat(4*nex).reshape(nex*ney,4)*nnx + np.tile(c0, (ney, 1))
        else:
            nex, ney, nez = int((xlims[1]-xlims[0]) // elt_size), int((ylims[1]-ylims[0]) // elt_size), int((zlims[1]-zlims[0]) // elt_size)
            nnx, nny, nnz = nex+1, ney+1, nez+1
            c000 = np.array([0, 1, nnx+1, nnx, nnx*nny, nnx*nny+1, nnx*nny+nnx+1, nnx*nny+nnx])
            c00 = np.arange(nex).repeat(8).reshape(nex,8) + c000.reshape(1,8).repeat(nex, axis=0)
            c0 = np.arange(ney).repeat(8*nex).reshape(nex*ney,8)*nnx + np.tile(c00, (ney, 1))
            cell_type = C8
            cells = np.arange(nez).repeat(8*nex*ney).reshape(nex*ney*nez,8)*nnx*nny + np.tile(c0, (nez, 1))

        offset_x = xlims[0] + ((xlims[1]-xlims[0]) - nex*elt_size) / 2
        offset_x = np.round(offset_x) - 0.5
        offset_y = ylims[0] + ((ylims[1]-ylims[0]) - ney*elt_size) / 2
        offset_y = np.round(offset_y) - 0.5

        xn = np.arange(nnx)*elt_size + offset_x
        yn = np.arange(nny)*elt_size + offset_y
        if zlims is None:
            zn = [0]
            regular = (ney, nex), elt_size
        else:
            offset_z = zlims[0] + ((zlims[1]-zlims[0]) - nez*elt_size) / 2
            offset_z = np.round(offset_z) - 0.5
            zn = np.arange(nnz)*elt_size + offset_z
            regular = (nez, ney, nex), elt_size

        zn, yn, xn = np.meshgrid(zn, yn, xn, indexing='ij')
        nodes = np.vstack((xn.flat, yn.flat, zn.flat)).T

        if order == 2:
            cell_type, cells, nodes = self._to_quad(cell_type, cells, nodes)

        super().__init__(nodes, cells, cell_type)
        self.regular = regular

    @cache
    def _get_regular_base(self):
        ndim = self.ndim
        nelems, elt_size = self.regular
        pix_coords = np.mgrid[(slice(0,elt_size),)*ndim].reshape((ndim, elt_size**ndim)).T
        coords = ((pix_coords - (elt_size-1)/2)*2/elt_size)[:,::-1]
        Ne = self.cell_type.N(coords).astype('f4').reshape((self.cell_type.n_nodes, elt_size**ndim))
        coefs = np.array([np.prod(np.array(nelems)[idim+1:]*elt_size) for idim in range(ndim)])
        return pix_coords, Ne, coefs

    def iter_Nc(self):
        nelems, elt_size = self.regular
        n = len(nelems)
        mv = nelems[::-1]
        ks = [0]*n
        while True:
            if ks[n-1] >= mv[n-1]:
                break
            yield np.array(ks[::-1])*elt_size
            ks[0] += 1
            for i in range(n-1):
                if ks[i] >= mv[i]:
                    ks[i] = 0
                    ks[i+1] += 1

    def change_order(self, order):
        if self.order == order:
            return self.copy()
        if order == 1:
            cell_type = {
                Q4Q: Q4,
                C8Q: C8
            }[self.cell_type]
            cells = self.cells[:,:cell_type.n_nodes]
            nodes = self.nodes[:cells.max()+1]
            return self.new(nodes, {cell_type: cells})
        if order == 2:
            cell_type, cells, nodes = self._to_quad(self.cell_type, self.cells, self.nodes)
            return self.new(nodes, {cell_type: cells})
