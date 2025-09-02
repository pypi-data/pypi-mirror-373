import numpy as np
from functools import cache

from ..cells import Q4, C8, P6, T3
from .base_mesh import BaseMesh

class CompositeBaseMesh(BaseMesh):
    ''

    def __init__(self, nodes, cells_by_type, nodes_ids=None):
        self.nodes = nodes
        self.cells_by_type = cells_by_type
        if nodes_ids is None:
            self.nodes_ids = np.arange(len(self.nodes))
        self.reduced_integration = False
        self._Nc = sum(len(v) for k,v in self.cells_by_type.items())
        self._Nn = len(nodes)
        self._ndim = np.max([cell_type.ndim for cell_type in self.cells_by_type])
        if self._ndim == 2 and self.nodes[:,2].std() > 0:
            self._ndim = 3

    def __repr__(self):
        result = f"{self.__class__.__name__} with {self.Nc} cells and {self.Nn} nodes"
        is_reduced = {True: 'r', False: ''}[self.reduced_integration]
        if len(self.cells_by_type) == 1:
            result += " of type %s%s." % (next(iter(self.cells_by_type)).name, is_reduced)
        else:
            result += " :"
            for cell_type, cells in self.cells_by_type.items():
                result += "\n    * %d cells of type %s%s." % (len(cells), cell_type.name, is_reduced)
        return result

    def copy_as_2d(self):
        #
        idx = np.unique(np.hstack([c.flat for T, c in self.cells_by_type.items() if T.ndim == 2]))

        new_nid = -np.ones(idx.max()+1, dtype='i8')
        new_nid[idx] = np.arange(len(idx), dtype='i8')

        nodes = self.nodes[idx].copy()
        cells_by_type = {T:new_nid[c] for T, c in self.cells_by_type.items() if T.ndim == 2}

        mesh = self.new(nodes, cells_by_type)
        mesh.reduced_integration = self.reduced_integration

        return mesh

    def copy_as_3d(self):
        #
        idx = np.unique(np.hstack([c.flat for T, c in self.cells_by_type.items() if T.ndim == 3]))

        new_nid = -np.ones(idx.max()+1, dtype='i8')
        new_nid[idx] = np.arange(len(idx), dtype='i8')

        nodes = self.nodes[idx].copy()
        cells_by_type = {T:new_nid[c] for T, c in self.cells_by_type.items() if T.ndim == 3}

        mesh = self.new(nodes, cells_by_type)
        mesh.reduced_integration = self.reduced_integration

        return mesh

    def extrude(self, length, parts):
        if self.ndim != 2:
            raise Exception('extrusion only works for 2D mesh')

        h = length / parts

        nodes = np.tile(self.nodes, (parts+1, 1))
        nodes[:,2] = np.tile(np.linspace(0, length, parts+1), (self.Nn,1)).T.flat
        cells_by_type = {}
        for T, c in self.cells_by_type.items():
            cells_by_type[{T3:P6, Q4:C8}[T]] = np.vstack([np.hstack((c + self.Nn*n, c+self.Nn*(n+1))) for n in range(parts)])
        return self.new(nodes, cells_by_type)

    @cache
    def surf(self):
        return np.hstack([T.surface(c, self.nodes) for T, c in self.cells_by_type.items()])

    @cache
    def vol(self):
        return np.hstack([T.volume(c, self.nodes) for T, c in self.cells_by_type.items()])

    @cache
    def gauss_points(self, reduced_integration=None):
        if reduced_integration is None:
            reduced_integration = self.reduced_integration

        if reduced_integration:
            n = self.Nc
        else:
            n = np.sum([T.ng*len(c) for T, c in self.cells_by_type.items()])

        pg = np.zeros((n, 3))
        ngt = 0
        for T, c in self.cells_by_type.items():
            N = T.N(T.get_gauss_points(weight=False, reduced_integration=reduced_integration))
            ng = N.shape[1]*len(c)
            pg[ngt:ngt+ng].flat = (N.T @ self.nodes[c]).flat
            ngt += ng

        return pg

    @cache
    def outline(self):
        # works only on 2D mesh.
        lines = []

        for T, c in self.cells_by_type.items():
            if T.ndim == 2:
                lines.append(c[:,T.vertices].reshape((len(c)*len(T.vertices), 2)))
        lines = np.vstack(lines)
        lines.sort(axis=1)
        ind = np.lexsort((lines[:,1],lines[:,0]))
        lines = lines[ind,:]
        lines = lines[:,0]+self.Nn*lines[:,1]
        lines, counts = np.unique(lines, return_counts=True)
        lines = lines[counts==1]
        lines = np.vstack((lines // self.Nn, lines % self.Nn)).T
        idx = np.zeros(lines.shape[0], dtype='i8')
        used = np.zeros(lines.shape, dtype='bool')
        idx[0] = lines[0,0]
        idx[1] = lines[0,1]
        used[0,:] = True
        for i in range(2,lines.shape[0]):
            r, c = np.where(np.logical_and(lines==idx[i-1],used==False))
            idx[i] = lines[r,abs(c-1)]
            used[r,:] = True

        return idx

    @cache
    def vertices(self):
        #
        lines = np.array([], dtype='i').reshape((0,2))

        for T, c in self.cells_by_type.items():
            lines = np.vstack([lines] + [c[:,v] for v in T.vertices])

        lines.sort(axis=1)
        return np.unique(lines, axis=0)

    def _pre_compute_faces(self):
        #
        t3 = np.array([], dtype='i').reshape((0,3))
        q4 = np.array([], dtype='i').reshape((0,4))

        for T, c in self.cells_by_type.items():
            for f in T.faces:
                if len(f) == 3:
                    t3 = np.vstack((t3, c[:,f]))
                elif len(f) == 4:
                    q4 = np.vstack((q4, c[:,f]))

        return t3, q4

    def split_by_celltype(self, V):
        R = {}
        i = 0
        for T, c in self.cells_by_type.items():
            R[T] = V[i:i+len(c)]
            i += len(c)
        return R

    @property
    def order(self):
        """
        Element order

        Returns
        =======
        out: int
            1 for linear, 2 for quadratic.

        """
        order = np.unique([T.order for T in self.cells_by_type])
        if len(order) == 1:
            return int(order[0])
        return -1


    @property
    def cell_type(self):
        return None

    def change_order(self, order):
        if self.order != -1 and self.order == order:
            return self.copy()

        if order in [1, 2]:
            order_to_transform = {1: 2, 2: 1}[order]
            new_nodes = np.zeros((0,3))

            cells_by_type = {}

            for cell_type, cells in self.cells_by_type.items():
                nids = np.unique(cells)
                nids.sort()
                new_nids = -np.ones(self.Nn+1, dtype='i8')
                new_nids[nids] = np.arange(nids.shape[0], dtype='i8')
                cells = new_nids[cells]
                nodes = self.nodes[nids]

                if cell_type.order == order_to_transform and cell_type.ndim > 1:
                    cell_type, cells, nodes = {
                        1: self._to_linear,
                        2: self._to_quad,
                    }[order](cell_type, cells, nodes)

                cells_by_type[cell_type] = cells + len(new_nodes)
                new_nodes = np.vstack((new_nodes, nodes))

            nodes, nids = np.unique(new_nodes, return_inverse=True, axis=0)
            cells_by_type = {T:nids[c] for T, c in cells_by_type.items()}

            return self.new(nodes, cells_by_type)


