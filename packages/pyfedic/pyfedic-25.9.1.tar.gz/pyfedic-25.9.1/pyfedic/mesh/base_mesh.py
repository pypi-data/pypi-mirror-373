import numpy as np
from numpy import linalg
from scipy import sparse
from functools import cache

from ..cells import Cell, T3, T3Q, Q4, Q4Q, T4, T4Q, C8, C8Q, P6, P6Q
from ..tictoc import tictoc

try:
    from pyfedic_cython.mesh import compute_N_by_type
except ModuleNotFoundError:
    compute_N_by_type = None

class BaseMesh:
    """
    Mesh()

    A mesh of 2D or 3D cells.

    """
    CYTHON = True

    @classmethod
    def new(cls, nodes, cells_by_type):
        from . import Mesh, RegularMesh, CompositeMesh
        cells_by_type = {k:v for k, v in cells_by_type.items() if len(v) > 0}
        if len(cells_by_type) == 1:
            cell_type, cells = next(iter(cells_by_type.items()))
            mesh = Mesh(nodes, cells, cell_type)
            if cell_type not in [Q4, C8, Q4Q, C8Q]:
                return mesh
            p = [np.diff(np.unique(mesh.nodes[:,x])) for x in range(3)]
            elt_size = np.unique(np.hstack(p)) * cell_type.order
            if elt_size.size == 1 and elt_size[0] % 1 == 0:
                elt_size = int(elt_size[0])
                nelems = tuple(len(x)/cell_type.order for x in p[:mesh.ndim][::-1])
                x0, y0, z0 = mesh.nodes[0]
                xlims = x0, x0+nelems[-1]*elt_size
                ylims = y0, y0+nelems[-2]*elt_size
                if mesh.ndim == 2:
                    mesh = RegularMesh(xlims, ylims, elt_size=elt_size, order=cell_type.order)
                else:
                    zlims = z0, z0+nelems[-3]*elt_size
                    mesh = RegularMesh(xlims, ylims, zlims, elt_size=elt_size, order=cell_type.order)
            return mesh
        return CompositeMesh(nodes, cells_by_type)

    def __init__(self, nodes, cells, cell_type, nodes_ids=None):
        self.cells = cells
        self.nodes = nodes
        self.cell_type = cell_type
        self.cells_by_type = {cell_type: cells}
        if nodes_ids is None:
            self.nodes_ids = np.arange(len(self.nodes))
        self.reduced_integration = False
        self._Nc = len(self.cells)
        self._Nn = len(self.nodes)
        self._ndim = self.cell_type.ndim
        self._nbh = {}
        if self._ndim == 2 and self.nodes[:,2].std() > 0:
            self._ndim = 3

    @property
    def ndim(self):
        """
        Number of dimension of the mesh

        Returns
        =======
        out: int
            2 for 2D, 3 for 3D.

        """
        return self._ndim

    @property
    def order(self):
        """
        Element order

        Returns
        =======
        out: int
            1 for linear, 2 for quadratic.

        """
        return self.cell_type.order

    @property
    def Nn(self):
        """
        Number of nodes of the mesh

        Returns
        =======
        out: int

        """
        return self._Nn

    @property
    def Nc(self):
        """
        Number of Cells (or elements) of the mesh

        Returns
        =======
        out: int

        """
        return self._Nc

    def __repr__(self):
        result = f"{self.__class__.__name__} with {self.Nc} cells and {self.Nn} nodes"
        is_reduced = {True: 'r', False: ''}[self.reduced_integration]
        result += " of type %s%s." % (self.cell_type.name, is_reduced)
        return result

    def copy(self):
        """
        Returns a copy of itself but all properties must be recomputed.
        """
        mesh = self.new(self.nodes.copy(), {T: c.copy() for T, c in self.cells_by_type.items()})
        mesh.reduced_integration = self.reduced_integration
        return mesh

    def warp(self, U):
        if U.shape[1] == 2:
            U = np.hstack((U, np.zeros((self.Nn, 1))))
        mesh = self.new(self.nodes + U, {T: c.copy() for T, c in self.cells_by_type.items()})
        mesh.reduced_integration = self.reduced_integration
        return mesh

    def scale(self, scale_factor):
        mesh = self.new(self.nodes * scale_factor, {T: c.copy() for T, c in self.cells_by_type.items()})
        mesh.reduced_integration = self.reduced_integration
        return mesh

    def extract_selection(self, nids=None, cids=None, keep_orphaned_nodes=False, return_ids=False): #TODO
        """
        Return a new Mesh object
        """
        if nids is None and cids is None:
            raise Exception('missing argument : nids or cids should be provide')

        if cids is not None:
            nids_from_cids = []
            for T, ids in cids.items():
                nids_from_cids.append(self.cells_by_type[T][ids].ravel())
            nids_from_cids = np.hstack(nids_from_cids)
            if nids is None:
                if keep_orphaned_nodes:
                    nids = np.arange(self.Nn)
                else:
                    nids = nids_from_cids
            else:
                nids = np.hstack((nids, nids_from_cids))

        nids = np.unique(nids)
        nids = nids[nids>=0]
        nids.sort()

        new_nids = -np.ones(self.Nn+1, dtype=int)
        new_nids[nids] = np.arange(nids.shape[0], dtype=int)

        cells_by_type = {T:new_nids[c] for T, c in self.cells_by_type.items()}

        if cids is None:
            cids = {}
            for T, c in cells_by_type.items():
                cids[T] = ~(c < 0).any(axis=1)

        nodes = self.nodes[nids].copy()
        cells_by_type = {T:c[cids[T]] for T, c in cells_by_type.items()}

        mesh = self.new(nodes, cells_by_type)
        mesh.reduced_integration = self.reduced_integration

        if return_ids:
            return mesh, nids, cids
        return mesh

    def extrude(self, length, parts):
        if self.ndim != 2:
            raise Exception('extrusion only works for 2D mesh')

        h = length / parts

        nodes = np.tile(self.nodes, (parts+1, 1))
        nodes[:,2] = np.tile(np.linspace(0, length, parts+1), (self.Nn,1)).T.flat
        cells = np.vstack([np.hstack((self.cells + self.Nn*n, self.cells+self.Nn*(n+1))) for n in range(parts)])
        cell_type = {T3:P6, Q4:C8}[self.cell_type]
        return self.new(nodes, {cell_type: cells})

    @cache
    def surf(self):
        """
        Area of the mesh in case of 2D mesh

        Returns
        =======
        out: double
            Area of the mesh in case of 2D mesh, 0 if 3D.

        """
        return self.cell_type.surface(self.cells, self.nodes)

    @cache
    def vol(self):
        """
        Volume of the mesh in case of 3D mesh

        Returns
        =======
        out: double
            Volume of the mesh in case of 3D mesh, 0 if 2D.

        """
        return self.cell_type.volume(self.cells, self.nodes)

    @cache
    def gauss_points(self, reduced_integration=None):
        if reduced_integration is None:
            reduced_integration = self.reduced_integration

        if reduced_integration:
            n = self.Nc
        else:
            n = self.Nc*self.cell_type.ng

        N = self.cell_type.N(self.cell_type.get_gauss_points(weight=False, reduced_integration=reduced_integration))

        return (N.T @ self.nodes[self.cells]).reshape((n, 3))

    @cache
    def outline(self):
        """
        Vertices of the mesh part of only one cell.

        Returns
        =======
        out: ndarray
            out[i,:] correspond to the point indices [a_i, b_i] of the vertice (AB)

        """
        # works only on 2D mesh.
        lines = []

        if self.cell_type.ndim == 2:
            lines.append(self.cells[:,self.cell_type.vertices].reshape((self.Nc*len(self.cell_type.vertices), 2)))
        lines = np.vstack(lines)
        lines.sort(axis=1)
        ind = np.lexsort((lines[:,1],lines[:,0]))
        lines = lines[ind,:]
        lines = lines[:,0]+self.Nn*lines[:,1]
        lines, counts = np.unique(lines, return_counts=True)
        lines = lines[counts==1]
        lines = np.vstack((lines // self.Nn, lines % self.Nn)).T
        idx = np.zeros(lines.shape[0], dtype=int)
        used = np.zeros(lines.shape, dtype=bool)
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
        """
        Vertices of the mesh.

        Returns
        =======
        out: ndarray
            out[i,:] correspond to the point indices [a_i, b_i] of the vertice (AB)

        """
        lines = np.vstack([self.cells[:,v] for v in self.cell_type.vertices])
        lines.sort(axis=1)
        return np.unique(lines, axis=0)

    @tictoc
    def compute_nbh(self, order=1, use_cells=False, only_last=False):
        #
        if (order, use_cells) in self._nbh:
            return self._nbh[(order, use_cells)]

        links = self.vertices()

        if use_cells:
            lines = np.array([], dtype=int).reshape((0,2))

            for T, c in self.cells_by_type.items():
                a = sparse.coo_array(np.ones((T.n_nodes,T.n_nodes)))
                cpls = np.vstack((a.row, a.col)).T
                cpls.sort(axis=1)
                np.unique(cpls.copy(), axis=0)

                lines = np.vstack([lines] + [c[:,v] for v in cpls])

            lines.sort(axis=1)
            links = np.unique(lines, axis=0)

        adj = sparse.coo_array(
            (
                np.ones(links.shape[0]*2, dtype=bool),
                (
                    links.T.ravel(),
                    links[:,::-1].T.ravel()
                )
            ), shape=(self.Nn,self.Nn)).tocsr()
        adj_res = adj.copy()
        adj += sparse.csr_array((np.ones(self.Nn, dtype=bool), np.arange(self.Nn), np.arange(self.Nn+1)))
        adj_prev = sparse.csr_array((np.ones(self.Nn, dtype=bool), np.arange(self.Nn), np.arange(self.Nn+1)))

        nb = np.array((adj>0).sum(axis=1)).ravel()

        indices = np.tile(np.arange(nb.max()), (self.Nn, 1))
        indices = indices[indices < np.tile(nb, (nb.max(), 1)).T]

        nbh0 = sparse.csr_array((adj.indices+1, indices, np.cumsum(np.hstack((0, nb)))), shape=(self.Nn, nb.max()), dtype=int)

        nbh = nbh0

        current_order = 1

        while order > current_order:

            col = nbh0[nbh.data-1,:]

            row = np.repeat(np.repeat(np.arange(nbh0.shape[0])+1, np.diff(nbh.indptr)), np.diff(col.indptr))

            adj2_col = col.data-1
            adj2_row = row-1

            adj_prev = adj
            adj += sparse.coo_array(
                (
                    np.ones(adj2_col.shape[0]*2, dtype=bool),
                    (
                        np.hstack((adj2_col.astype(int), adj2_row.astype(int))),
                        np.hstack((adj2_row.astype(int), adj2_col.astype(int))),
                    )
                ), shape=(self.Nn,self.Nn)).tocsr()

            nb = np.array((adj>0).sum(axis=1)).ravel()

            indices = np.tile(np.arange(nb.max()), (self.Nn, 1))
            indices = indices[indices < np.tile(nb, (nb.max(), 1)).T]

            nbh = sparse.csr_array((adj.indices+1, indices, np.cumsum(np.hstack((0, nb)))), shape=(self.Nn, nb.max()), dtype=int)

            current_order += 1

        if only_last:
            adj = adj - adj_prev
            nb = np.array((adj>0).sum(axis=1)).ravel()

            indices = np.tile(np.arange(nb.max()), (self.Nn, 1))
            indices = indices[indices < np.tile(nb, (nb.max(), 1)).T]

            nbh = sparse.csr_array((adj.indices+1, indices, np.cumsum(np.hstack((0, nb)))), shape=(self.Nn, nb.max()), dtype=int)

        nbh.data -= 1

        self._nbh[(order, use_cells)] = nbh

        return nbh

    def _pre_compute_faces(self):
        #

        t3 = np.array([], dtype=int).reshape((0,3))
        q4 = np.array([], dtype=int).reshape((0,4))

        for f in self.cell_type.faces:
            if len(f) == 3:
                t3 = np.vstack((t3, self.cells[:,f]))
            elif len(f) == 4:
                q4 = np.vstack((q4, self.cells[:,f]))

        return t3, q4

    def faces(self, keep_only_free=False):
        #

        t3, q4 = self._pre_compute_faces()

        if t3.any():
            idx = (np.tile(np.arange(3), (t3.shape[0], 1)) + np.tile(np.argmin(t3, axis=1), (3,1)).T) % 3 + np.tile(np.arange(t3.shape[0])*3,(3,1)).T
            t3 = t3.ravel()[idx.ravel()].reshape(t3.shape)
            if keep_only_free:
                t3s = np.sort(t3, axis=1)
                _, idx, cnt = np.unique(t3s, return_index=True, return_counts=True, axis=0)
                t3 = t3[idx[cnt==1]]
            else:
                t3 = np.unique(t3, axis=0)

        if q4.any():
            idx = (np.tile(np.arange(4), (q4.shape[0], 1)) + np.tile(np.argmin(q4, axis=1), (4,1)).T) % 4 + np.tile(np.arange(q4.shape[0])*4,(4,1)).T
            q4 = q4.ravel()[idx.ravel()].reshape(q4.shape)
            if keep_only_free:
                q4s = np.sort(q4, axis=1)
                _, idx, cnt = np.unique(q4s, return_index=True, return_counts=True, axis=0)
                q4 = q4[idx[cnt==1]]
            else:
                q4 = np.unique(q4, axis=0)

        return self.new(self.nodes, {T3: t3, Q4: q4})

    def free_faces(self):
        #
        return self.faces(True)

    def compute_N(self, points, raw=False):
        """
        compute_N(self, points=None)
        """

        if isinstance(points, np.ndarray):
            Np = len(points)
            Nt = Np*10**3
        else:
            Np, Nt = points._compute_pixN_get_sizes()

        indn = np.zeros(Nt, dtype='i4')
        indp = np.zeros(Nt, dtype='i4')
        val = np.zeros(Nt, dtype='f4')
        done = np.zeros(Np, dtype='i4')

        indni = 0
        iii = 0

        for T, c in self.cells_by_type.items():

            ppp = self.nodes[c]

            if self.CYTHON and compute_N_by_type is not None and not (T.ndim == 2 and ppp[:,:,2].std() != 0):
                iii, indni = compute_N_by_type(points, self.nodes, c, T, indp, indn, val, done, indni, iii)

            else:
                import logging
                custom_enumerate = enumerate
                if logging.getLogger().level < logging.INFO:
                    try:
                        from tqdm import tqdm
                    except ModuleNotFoundError:
                        pass
                    else:
                        bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
                        custom_enumerate = lambda x:enumerate(tqdm(x, desc=T.__name__, bar_format=bar_format, smoothing=0.1))
                for i, pp in custom_enumerate(ppp):
                    iii += 1

                    if isinstance(points, np.ndarray):
                        xx, yy, zz = pp.T
                        if points.shape[1] == 2:
                            xd, yd = points.T
                            zd = np.zeros_like(xd)
                        else:
                            xd, yd, zd = points.T
                        if self.ndim == 3:
                            ipix = ((xd >= xx.min()-T.EPSILON) & (xd <= xx.max()+T.EPSILON) &
                                    (yd >= yy.min()-T.EPSILON) & (yd <= yy.max()+T.EPSILON) &
                                    (zd >= zz.min()-T.EPSILON) & (zd <= zz.max()+T.EPSILON))
                        else:
                            ipix = (xd >= xx.min()) & (xd <= xx.max()) & (yd >= yy.min()) & (yd <= yy.max())
                        ipix, = np.where(ipix)
                        xyzpix = points[ipix]
                    else:
                        ipix, xyzpix = points._compute_pixN_get_pix(pp)

                    if xyzpix.size == 0:
                        continue

                    if T.ndim == 2 and self.ndim == 3:
                        #
                        pc = pp.mean(axis=0)

                        v = pp - pc

                        nz = T.normal(np.arange(T.n_nodes)[None,:], pp).ravel()
                        nz /= (nz.dot(nz))**.5
                        ny = v[0,:].copy()
                        ny /= (ny.dot(ny))**.5
                        nx = np.cross(ny, nz)

                        xx, yy, zz = pp.T
                        xx = v.dot(nx)
                        yy = v.dot(ny)
                        zz = xx*0
                        pp = np.vstack((xx, yy, zz)).T

                        vpix = xyzpix - pc

                        _xyzpix = xyzpix

                        xpix, ypix, zpix = xyzpix.T
                        xpix = vpix.dot(nx)
                        ypix = vpix.dot(ny)
                        zpix = vpix.dot(nz)
                        xyzpix = np.vstack((xpix, ypix, zpix)).T

                    pg, is_ok = T.get_param_coordinate(pp, xyzpix)

                    if T.ndim == 2 and self.ndim == 3:
                        is_ok[is_ok] = np.abs(zpix[is_ok]) <= 0.5
                        xyzpix = _xyzpix

                    ind = is_ok & (done[ipix]==0)
                    pg = pg[ind]

                    N = T.N(pg)

                    n = ind.sum()

                    for j in range(N.shape[0]):
                        indp[indni:indni+n] = ipix[ind]
                        indn[indni:indni+n] = c[i,j]
                        val[indni:indni+n] = N[j,:]
                        indni += n

                    done[ipix[ind]] = iii

        N = sparse.csc_array((val[:indni], (indp[:indni], indn[:indni])), shape=(Np, self.Nn))

        if raw:
            return N, done

        return N

    def compute_dN(self, reduced_integration=None, selection=None):
        """Jacobian Matrix for all Cells.

        The function return 4 sparses matrix:

        * dN/dr of shape (mesh.Nc*(number of shape by Cell), mesh.Nn)
        * dN/ds of shape (mesh.Nc*(number of shape by Cell), mesh.Nn)
        * dN/dt of shape (mesh.Nc*(number of shape by Cell), mesh.Nn)
        * wDetJ of shape (mesh.Nc*(number of shape by Cell), mesh.Nc*(number of shape by Cell))

        Parameters
        ----------
        reduced_integration : bool
            use one Gauss point if True

        Returns
        -------
        out : tuple of :class:`scipy.sparse.coo.coo_array`
            Jacobian matrices for each cells of the mesh.

        See Also
        --------
        :meth:`Mesh.dN`

        """
        if reduced_integration is None:
            reduced_integration = self.reduced_integration

        Gpt = Gptn = 0
        for T, c in self.cells_by_type.items():
            Npg = 1 if reduced_integration else T.ng
            Gpt += len(c)*Npg
            Gptn += len(c)*T.n_nodes*Npg

        indg = np.zeros(Gptn)
        indn = np.zeros(Gptn)
        result = np.zeros((3, Gptn))
        result_wdetj = np.zeros(Gpt)

        indni = 0
        ii = 0
        i_cell = 0

        for T, c in self.cells_by_type.items():
            pg, wg = T.get_gauss_points(reduced_integration=reduced_integration)
            dN = T.dN(pg).transpose(2, 0, 1)
            Npg = len(pg)

            for nods in c:
                if selection is not None and not selection[i_cell]:
                    for gi in range(Npg):
                        indni += T.n_nodes
                    ii += Npg
                    i_cell += 1
                    continue

                J = dN @ self.nodes[nods,:T.ndim]
                J = J.transpose((0,2,1))

                detJ = np.linalg.det(J)
                invJ = np.linalg.inv(J).transpose((0,2,1))

                result_wdetj[ii:ii+Npg] = wg*detJ
                result[:T.ndim, indni:indni+T.n_nodes*Npg] = np.hstack(invJ @ dN)
                indn[indni:indni+T.n_nodes*Npg] = np.tile(nods, Npg)
                indg[indni:indni+T.n_nodes*Npg] = np.repeat(ii + np.arange(Npg), T.n_nodes)
                indni += T.n_nodes*Npg
                ii += Npg
                i_cell += 1

        return (
            sparse.coo_array((result[0], (indg, indn)), shape=(Gpt, self.Nn)),
            sparse.coo_array((result[1], (indg, indn)), shape=(Gpt, self.Nn)),
            sparse.coo_array((result[2], (indg, indn)), shape=(Gpt, self.Nn)),
            sparse.coo_array((result_wdetj, (np.arange(Gpt),np.arange(Gpt))), shape=(Gpt, Gpt))
        )

    def compute_K(self, nu=0.3, E=1, reduced_integration=None, hyp="plane stress", selection=None, dN=None):
        if dN is None:
            dN = self.compute_dN(reduced_integration, selection)
        dNdx, dNdy, dNdz, wdetJ = dN

        zero = sparse.coo_array(([], ([],[])), shape=dNdx.shape)

        if self.ndim == 2:
            epsxx = sparse.hstack((dNdx, zero))
            epsyy = sparse.hstack((zero, dNdy))
            epsxy = sparse.hstack((dNdy, dNdx))
        else:
            epsxx = sparse.hstack((dNdx, zero, zero))
            epsyy = sparse.hstack((zero, dNdy, zero))
            epszz = sparse.hstack((zero, zero, dNdz))
            epsxy = sparse.hstack((dNdy, dNdx, zero))
            epsyz = sparse.hstack((zero, dNdz, dNdy))
            epsxz = sparse.hstack((dNdz, zero, dNdx))

        mu = 1/2/(1+nu)
        lbd = nu/(1+nu)/(1-2*nu)

        if self.ndim == 2:
            if hyp == "plane strain":
                ltr = lbd*(epsxx+epsyy)
                sxx = 2*mu*epsxx+ltr
                syy = 2*mu*epsyy+ltr
                sxy = mu*epsxy
            elif hyp == "plane stress":
                sxx = (epsxx+nu*epsyy)/(1-nu**2)
                syy = (epsyy+nu*epsxx)/(1-nu**2)
                sxy = epsxy*(1-nu)/(1-nu**2)/2

            return (epsxx.T.dot(wdetJ).dot(sxx) + epsyy.T.dot(wdetJ).dot(syy) + epsxy.T.dot(wdetJ).dot(sxy)).tocoo()*E
        else:
            ltr = lbd*(epsxx+epsyy+epszz)
            sxx = 2*mu*epsxx+ltr
            syy = 2*mu*epsyy+ltr
            szz = 2*mu*epszz+ltr
            sxy = mu*epsxy
            syz = mu*epsyz
            sxz = mu*epsxz
            return (epsxx.T.dot(wdetJ).dot(sxx) +
                    epsyy.T.dot(wdetJ).dot(syy) +
                    epszz.T.dot(wdetJ).dot(szz) +
                    epsxy.T.dot(wdetJ).dot(sxy) +
                    epsyz.T.dot(wdetJ).dot(syz) +
                    epsxz.T.dot(wdetJ).dot(sxz)).tocoo()*E

    def save(self, filename, U=None, compute_eps=False, point_values=None, cell_values=None, dN=None, **kwargs):
        from ..io import write_mesh

        if U is None:
            write_mesh(filename, self, cell_values, point_values, **kwargs)
            return

        sel = ~np.isnan(U).any(axis=1)
        xc, yc, zc = self.nodes.mean(axis=0)

        zzz = self.nodes[sel,0]*0

        if U.shape[1] == 2:
            ux, uy = U.T
            uz = ux*0

            L = np.hstack((
                np.vstack((zzz+1, zzz  ,  (self.nodes[sel,1] - yc))),
                np.vstack((zzz  , zzz+1, -(self.nodes[sel,0] - xc))),
            )).T

        else:
            ux, uy, uz = U.T

            L = np.hstack((
                np.vstack((zzz+1, zzz  , zzz  ,  zzz                      , -(self.nodes[sel,2] - zc),  (self.nodes[sel,1] - yc))),
                np.vstack((zzz  , zzz+1, zzz  ,  (self.nodes[sel,2] - zc),   zzz                     , -(self.nodes[sel,0] - xc))),
                np.vstack((zzz  , zzz  , zzz+1, -(self.nodes[sel,1] - yc),  (self.nodes[sel,0] - xc),   zzz                     ))
            )).T

        UU = U.T.ravel()
        if U.shape[1] == 2:
            SEL = np.hstack((sel, sel))
        else:
            SEL = np.hstack((sel, sel, sel))

        A = linalg.lstsq(L, UU[SEL], rcond=None)[0]

        U_norbm = UU.copy()
        U_norbm[SEL] -= L.dot(A)

        if U.shape[1] == 2:
            UU = np.hstack((UU, uz))
            U_norbm = np.hstack((U_norbm, uz))

        if point_values is None:
            point_values = {}
        else:
            point_values = point_values.copy()

        if cell_values is None:
            cell_values = {}
        else:
            cell_values = cell_values.copy()

        point_values.update({
            'U': UU.reshape((3, self.Nn)).T,
            'U_without_RBM': U_norbm.reshape((3, self.Nn)).T
        })

        if compute_eps:
            if dN is None:
                dNdx, dNdy, dNdz, _ = self.compute_dN(True)
            else:
                dNdx, dNdy, dNdz = dN

            dNu_xx = dNdx.dot(ux)
            dNu_xy = dNdx.dot(uy)
            dNu_xz = dNdx.dot(uz)
            dNu_yx = dNdy.dot(ux)
            dNu_yy = dNdy.dot(uy)
            dNu_yz = dNdy.dot(uz)
            dNu_zx = dNdz.dot(ux)
            dNu_zy = dNdz.dot(uy)
            dNu_zz = dNdz.dot(uz)

            epsxx = dNu_xx
            epsyy = dNu_yy
            epszz = dNu_zz
            epsxy = 0.5*(dNu_yx+dNu_xy)
            epsyz = 0.5*(dNu_zy+dNu_yz)
            epszx = 0.5*(dNu_zx+dNu_xz)

            Fxx = dNu_xx + 1
            Fxy = dNu_xy
            Fxz = dNu_xz
            Fyx = dNu_yx
            Fyy = dNu_yy + 1
            Fyz = dNu_yz
            Fzx = dNu_zx
            Fzy = dNu_zy
            Fzz = dNu_zz + 1

            gl_xx = 0.5 * (Fxx*Fxx + Fyx*Fyx + Fzx*Fzx - 1)
            gl_yy = 0.5 * (Fxy*Fxy + Fyy*Fyy + Fzy*Fzy - 1)
            gl_zz = 0.5 * (Fxz*Fxz + Fyz*Fyz + Fzz*Fzz - 1)
            gl_xy = 0.5 * (Fxx*Fxy + Fyx*Fyy + Fzx*Fzy)
            gl_yz = 0.5 * (Fxy*Fxz + Fyy*Fyz + Fzy*Fzz)
            gl_zx = 0.5 * (Fxx*Fxz + Fyx*Fyz + Fzx*Fzz)

            cell_values.update({
                'Eps': np.vstack((epsxx, epsxy, epszx, epsxy, epsyy, epsyz, epszx, epsyz, epszz)).T,
                'Eps_eq': 2**.5/3*((epsxx-epsyy)**2+(epsyy-epszz)**2+(epszz-epsxx)**2+6*(epsxy**2+epsyz**2+epszx**2))**.5,
                'Green_Lagrange': np.vstack((gl_xx, gl_xy, gl_zx, gl_xy, gl_yy, gl_yz, gl_zx, gl_yz, gl_zz)).T,
                'Green_Lagrange_eq': 2**.5/3*((gl_xx-gl_yy)**2+(gl_yy-gl_zz)**2+(gl_zz-gl_xx)**2+6*(gl_xy**2+gl_yz**2+gl_zx**2))**.5,
            })

        write_mesh(filename, self, cell_values, point_values, **kwargs)

        if compute_eps:
            return dNdx, dNdy, dNdz

    def plot_mesh(self, *args, ax=None, keep_axis=False, **kwargs):
        if ax is None:
            import matplotlib.pyplot as plt
            ax = plt.gca()
        if keep_axis:
            _axis = ax.axis()
        x, y, z = np.insert(self.nodes[self.vertices()], 2, np.nan, axis=1).transpose(2,0,1)
        if 'zaxis' in dir(ax):
            result = ax.plot(x.ravel(), y.ravel(), z.ravel(), *args, **kwargs)
        else:
            result = ax.plot(x.ravel(), y.ravel(), *args, **kwargs)
        if keep_axis:
            ax.axis(_axis)
        return result

    def plot_field(self, U, *args, ax=None, **kwargs):
        if self.ndim != 2:
            raise Exception('not available in 3D')

        if U.shape == (self.Nn,):
            shading = 'gouraud'
        elif U.shape == (self.Nc,):
            shading = 'flat'
        else:
            raise Exception('wrong field shape to display')

        if ax is None:
            import matplotlib.pyplot as plt
            ax = plt.gca()

        import matplotlib.tri as tri

        cells = self.cells_by_type.get(T3, np.zeros((0, 3), int))

        if Q4 in self.cells_by_type:
            Nc_T3 = len(cells)
            Nc_Q4 = len(self.cells_by_type[Q4])

            nodes = np.vstack((
                self.nodes,
                self.nodes[self.cells_by_type[Q4]].mean(axis=1)
            ))

            cells = np.vstack((
                cells,
                np.hstack((
                    self.cells_by_type[Q4][:,[[0,1],[1,2],[2,3],[3,0]]].reshape((Nc_Q4*4,2)),
                    np.repeat(np.arange(self.Nn, self.Nn+Nc_Q4), 4)[:,None]
                ))
            ))

            mesh = self.new(nodes, {T3: cells})

            if shading == 'gouraud':
                U = np.hstack((
                    U,
                    U[self.cells_by_type[Q4]].mean(axis=1)
                ))
            else:
                U = np.hstack((
                    U[:Nc_T3],
                    np.repeat(U[Nc_T3:], 4)
                ))

        else:
            mesh = self

        mpl_tri = tri.Triangulation(mesh.nodes[:,0], mesh.nodes[:,1], mesh.cells)

        return ax.tripcolor(mpl_tri, U, shading=shading, *args, **kwargs)

    def cell_values_to_node_values(self, V):
        flat = False
        if V.ndim == 1:
            flat = True
            V = V[:,None]

        cc = []

        for T, c in self.cells_by_type.items():
            cc.append(
                sparse.coo_array(
                (
                    np.ones(c.size),
                    (np.arange(c.shape[0]).repeat(c.shape[1]), c.flat)
                ), shape=(self.Nc, self.Nn))
            )

        cc = sparse.vstack(cc).tocsc()
        w = np.diff(cc.indptr)

        R = []
        for v in V.T:
            cc.data = v[cc.indices]
            R.append(np.array(cc.sum(axis=0)) / w)
        R = np.vstack(R).T

        if flat == 1:
            return R.ravel()
        return R

    @tictoc
    def interp_V(self, V, points, coef=1, out='closest', mask_out=None, mask_in=None, N=None, keep_N=False):
        """
        Interpolate vector fields `V` linked on the mesh at the point
        coordinates.

        Parameters
        ----------
        V: array_like
            vector fields of size (n, mesh_in.Nn) where n is the number of the
            vector components and mesh_in.Nn the number of nodes of the mesh.
        points: pyFEDIC.mesh.Mesh or array_like
            mesh holding the coordinates where to interpolate the fields `V` or
            just the nodes coordinates as (x, y, z).
        coef : int, optional
            scaling factor between the `mesh_in` and the `mesh_out`.
        out : None or float or 'closest' or ('mean', m), optional
            define the behavior for `mesh_out` points out of the `mesh_in`.
        mask_out : array_like, optional
            point mask to exclude points form the `mesh_out`.
        mask_in : array_like, optional
            point mask to exclude points form the `mesh_in`.

        Returns
        -------
        R: array_like
            vector fields of size (n, mesh_out.Nn) correspond of the interpolated
            values.

        """
        flat = False
        if V.ndim == 1:
            flat = True
            V = V[:,None]
        if isinstance(points, BaseMesh):
            points, mesh_out = points.nodes, points
        else:
            mesh_out = None
        Nn = len(points)
        if N is None:
            N = self.compute_N(points=points/coef)

        if mask_out is not None:
            N = N[:,mask_in].tocsr()[mask_out,:].tocsc()
            V = V[mask_in,:]
            R = np.full((Nn, V.shape[1]), np.nan)
            R[mask_out,:] = np.vstack([N.dot(v*coef) for v in V.T]).T
        else:
            R = np.vstack([N.dot(v*coef) for v in V.T]).T
            mask_in = slice(None)

        nin = np.ones(Nn, dtype=bool)
        nin[np.unique(N.indices)] = 0
        if mask_out is not None:
            nin = nin & ~mask_out

        if np.sum(nin) > 0:

            if type(out) in [float, int]:
                R[nin,:] = float(out)

            elif out == 'closest':

                if isinstance(mesh_out, BaseMesh):
                    R[nin,:] = np.nan
                    mesh_out.extrap_V(R, inplace=True)

                else:
                    points_out = points[nin]/coef

                    closest = np.argmin((
                        ((points_out[:,None] - self.nodes[mask_in][None,:])**2).sum(axis=2)
                    ), axis=1).ravel()

                    R[nin,:] = V[closest,:]*coef

            elif type(out) == tuple and out[0] == 'mean':

                if isinstance(mesh_out, BaseMesh):
                    R[nin,:] = mesh_out.mean_V(R, order=out[1])[nin,:]

        if flat:
            R = R.ravel()

        if keep_N:
            return R, N
        return R

    @tictoc
    def extrap_V(self, V, method='mean', inplace=False):
        ""

        flat = False
        nbh = self.compute_nbh()
        if V.ndim == 1:
            flat = True
            V = V[:,None]

        if len(V) != self.Nn:
            raise Exception('Wrong size for `V` !')

        if not inplace:
            V = V.copy()

        last_s_sum = -1
        while True:
            s = np.isnan(V[:,0])
            #print(s.sum())
            if s.sum() == 0:
                break
            if s.sum() == last_s_sum:
                print("pourquoi ça stagne ????")
                #FIXME: pourquoi ça stagne ????
                V[s] = 0
                break
            last_s_sum = s.sum()

            p = sparse.csr_array(
                ((~s)[nbh.data], nbh.indices, nbh.indptr),
                nbh.shape
            ).sum(axis=1)

            V[s] = 0

            W = np.vstack([sparse.csr_array(
                (v[nbh.data], nbh.indices, nbh.indptr),
                nbh.shape
            ).sum(axis=1).ravel() for v in V.T]).T

            W[p==0] = np.nan
            W[p>0] /= p[p>0][:,None]

            V[s] = W[s]

        if not inplace:
            if flat:
                return V.ravel()
            return V

    @tictoc
    def median_V(self, V, order=1):
        """
        Apply a median filter to the vector field `V` according the distance in
        terms of neightbooring.

        Parameters
        ----------
        V : array_like
            vector field to filter.
        order : int, optional
            number of neightboor to reach.

        Returns
        -------
        R: array_like
            filtered vector field.

        """
        if V.ndim == 1:
            flat = True
            V = V[:,None]

        R = []

        nbh = self.compute_nbh(order, use_cells=True).copy()
        nbh.data += 1
        nbh = nbh.todense() - 1

        for v in V.T:

            # shape = (nbr of values in v, nbr of neightboor)
            res = np.hstack((v, np.nan))[nbh]

            # ascending sort with nan values at the end
            res = np.sort(res, axis=1)

            # count of real values for each values of v
            n = (~np.isnan(res)).sum(axis=1)

            # if no real value take one of nan attribution
            n[n==0] = 1

            # hack for median value when even number of values
            sel = sparse.coo_array(
                (
                    np.ones(res.shape[0]*2, dtype=bool),
                    (
                        np.hstack((np.arange(res.shape[0]),np.arange(res.shape[0]))),
                        np.hstack((np.floor((n-1)/2),np.ceil((n-1)/2))).astype(int)
                    )
                ),
                shape=res.shape).toarray()

            res[~sel] = 0

            r = res.sum(axis=1)/sel.sum(axis=1)

            R.append(r.astype(V.dtype))

        return np.vstack(R).T

    @tictoc
    def mean_V(self, V, order=1):
        """
        Apply a mean filter to the vector field `V` according the distance in
        terms of neightbooring.

        Parameters
        ----------
        V : array_like
            vector field to filter.
        order : int, optional
            number of neightboor to reach.

        Returns
        -------
        R: array_like
            filtered vector field.

        """
        if V.ndim == 1:
            flat = True
            V = V[:,None]

        R = []

        nbh = self.compute_nbh(order, use_cells=True).copy()
        nbh.data += 1
        nbh = nbh.todense() - 1

        for v in V.T:

            res = np.hstack((v, np.nan))[nbh]

            n = (~np.isnan(res)).sum(axis=1)

            res[np.isnan(res)] = 0

            r = np.zeros_like(v)*np.nan
            r[n>0] = res.sum(axis=1)[n>0]/n[n>0]

            R.append(r)

        return np.vstack(R).T

    @classmethod
    def _to_quad(cls, cell_type, cells, nodes):
        new_cell_type = {
            T3: T3Q,
            Q4: Q4Q,
            T4: T4Q,
            P6: P6Q,
            C8: C8Q,
        }[cell_type]
        a = nodes[cells[:,cell_type.vertices]].mean(axis=2)
        b = a.reshape((len(cells)*len(cell_type.vertices), 3))
        c, d = np.unique(b, axis=0, return_inverse=True)
        e = np.arange(c.shape[0])
        f = e[d].reshape((len(cells), len(cell_type.vertices)))
        new_cells = np.hstack((cells, f+len(nodes)))
        new_nodes = np.vstack((nodes, c))
        return new_cell_type, new_cells, new_nodes

    @classmethod
    def _to_linear(cls, cell_type, cells, nodes):
        new_cell_type = {
            T3Q: T3,
            Q4Q: Q4,
            T4Q: T4,
            P6Q: P6,
            C8Q: C8,
        }[cell_type]
        new_cells = cells[:,:new_cell_type.n_nodes]
        nids = np.unique(new_cells)
        nids.sort()
        new_nids = -np.ones(len(nodes)+1, dtype=int)
        new_nids[nids] = np.arange(nids.shape[0], dtype=int)
        new_cells = new_nids[new_cells]
        new_nodes = nodes[nids]
        return new_cell_type, new_cells, new_nodes


    def change_order(self, order):
        if self.order == order:
            return self.copy()

        if order in [1, 2]:
            cell_type, cells, nodes = {
                1: self._to_linear,
                2: self._to_quad,
            }[order](self.cell_type, self.cells, self.nodes)
            return self.new(nodes, {cell_type: cells})

