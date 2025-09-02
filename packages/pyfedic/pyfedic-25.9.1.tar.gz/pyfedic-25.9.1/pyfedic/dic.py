#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as splinalg
from scipy.interpolate import RectBivariateSpline
import platform
import logging
import warnings
from functools import cache

from .tictoc import Tictoc, tictoc, TICTOC
from .cells import Q4, C8, Cell
from .mesh import RegularMesh

try:
    from pyfedic_cython.spfast import spmul
except ModuleNotFoundError:
    def spmul(sp, d):
        return sparse.csc_array((
                sp.data*d[sp.indices],
                sp.indices,
                sp.indptr
            ), sp.shape)

class DIC:
    #
    def __init__(self, imref, mesh):
        self.set_normim_params()
        self.debug_path = None
        self.scale = 0
        self.imref = self.normim(imref)
        self.mesh = mesh
        self.reg = None
        self.median = 0
        self.mean = 0
        self.itermax = 100
        self.normed_dU_min = 0.001
        self.diff_discr_min = 0.001
        self.interp_order = 1
        self.mask = None
        self.mask_node = None
        self.mask_cell = None
        self.gradref = None
        self.solver = 'cgs'
        self.U_init = np.zeros((self.mesh.Nn, self.imref.ndim), dtype='f4')

    def compute_gradient(self, order=1):
        if order == 1 or self.imref.ndim == 3:
            self.gradref = np.array([g[self.mesh.roi.slices].ravel() for g in np.gradient(self.imref)[::-1]])
        else:
            itp = RectBivariateSpline(np.arange(self.imref.shape[0]), np.arange(self.imref.shape[1]), self.imref)
            itp_x = itp.partial_derivative(0, 1)
            itp_y = itp.partial_derivative(1, 0)
            self.gradref = np.array([
                itp_x(np.arange(self.imref.shape[0]), np.arange(self.imref.shape[1]))[self.mesh.roi.slices].ravel(),
                itp_y(np.arange(self.imref.shape[0]), np.arange(self.imref.shape[1]))[self.mesh.roi.slices].ravel(),
            ])

    def set_normim_params(self, strategy="none", use_mesh=False, use_mask=False):
        self._normim_strategy = strategy
        self._normim_use_mesh = use_mesh
        self._normim_use_mask = use_mask
        self._normim_stats = None

    def normim(self, im):
        if self._normim_strategy == 'none':
            return im.astype('f4')
        if self._normim_stats is not None:
            return ((im-self._normim_stats[0])/self._normim_stats[1]/3+10).astype('f4')
        sel = ~np.isnan(im)
        if self._normim_use_mesh:
            sel[self.mesh.bounding_box.slices] &= True
        if self._normim_use_mask and self.mask is not None:
            sel &= self.mask
        stats = im[sel].mean(), im[sel].std()
        if self._normim_strategy == 'ref':
            self._normim_stats = stats
        return ((im-stats[0])/stats[1]/3+10).astype('f4')

    @tictoc(speak=False)
    def _compute_M_regular(self):
        #
        pix_coords, Ne, coefs = self.mesh._get_regular_base()

        data = []
        col = []
        row = []

        for i_cell, zyx in enumerate(self.mesh.iter_Nc()):
            if self.mask is not None and not self.mask_cell[i_cell]:
                continue

            x = ((pix_coords + zyx[None,:])*coefs[None,:]).sum(axis=1)
            r, c = np.meshgrid(self.mesh.cells[i_cell], self.mesh.cells[i_cell])
            for idim, g in enumerate(self.gradref):
                Mes = g[x]*Ne
                Me = Mes @ Mes.T
                data.append(Me.ravel())
                row.append(r.ravel()+self.mesh.Nn*idim)
                col.append(c.ravel()+self.mesh.Nn*idim)

        M = sparse.csc_array((np.hstack(data), (np.hstack(row), np.hstack(col))), (self.mesh.Nn*self.mesh.ndim,self.mesh.Nn*self.mesh.ndim))
        M.eliminate_zeros()

        return M

    @cache
    @tictoc
    def compute_M(self):
        #
        if self.gradref is None:
            self.compute_gradient()

        if isinstance(self.mesh, RegularMesh):
            return self._compute_M_regular()

        if self.mesh.pixN is None:
            self.mesh.compute_pixN()

        M = []
        for g in self.gradref:
            A = spmul(self.mesh.pixN, g)
            M.append(A.T @ A)

        M = sparse.block_diag(M)

        return M.tocsc()

    @tictoc(speak=False)
    def _compute_B_regular(self, diff):
        #
        pix_coords, Ne, coefs = self.mesh._get_regular_base()

        B = np.zeros(self.mesh.Nn*self.mesh.ndim, dtype='f4')

        for i_cell, zyx in enumerate(self.mesh.iter_Nc()):
            if self.mask is not None and not self.mask_cell[i_cell]:
                continue

            x = ((pix_coords + zyx[None,:])*coefs[None,:]).sum(axis=1)
            for idim, g in enumerate(self.gradref):
                B[self.mesh.cells[i_cell]+self.mesh.Nn*idim] += (g[x]*Ne) @ diff.flat[x]

        return B

    @tictoc
    def compute_B(self, diff):
        #

        if isinstance(self.mesh, RegularMesh):
            return self._compute_B_regular(diff)

        B = []
        for g in self.gradref:
            A = spmul(self.mesh.pixN, g)
            B.append(A.T @ diff.flat)

        return np.hstack(B)

    def set_interp_order(self, interp_order):
        self.interp_order = interp_order

    def set_regularisation(self, size, kind='equilibrium gap', nu=0.3, ddl=None):
        """

        # FIXME : ddl is not working => TODO
        ddl sould size: mesh.Nn
        with True if used by regularization.

        """
        M = self.compute_M()

        if kind == 'tikhonov':
            dNdx, dNdy, dNdz, wdetJ = self.mesh.compute_dN(selection=self.mask_cell)

            zero = sparse.coo_array(([], ([],[])), shape=dNdx.shape)

            if self.mesh.ndim == 2:
                epsxx = sparse.hstack((dNdx, zero))
                epsyy = sparse.hstack((zero, dNdy))
                epsxy = sparse.hstack((dNdy, dNdx))
                K = (epsxx.T @ wdetJ @ epsxx + epsyy.T @ wdetJ @ epsyy + epsxy.T @ wdetJ @ epsxy).tocoo()
            else:
                epsxx = sparse.hstack((dNdx, zero, zero))
                epsyy = sparse.hstack((zero, dNdy, zero))
                epszz = sparse.hstack((zero, zero, dNdz))
                epsxy = sparse.hstack((dNdy, dNdx, zero))
                epsyz = sparse.hstack((zero, dNdz, dNdy))
                epsxz = sparse.hstack((dNdz, zero, dNdx))
                K = (
                    epsxx.T @ wdetJ @ epsxx +
                    epsyy.T @ wdetJ @ epsyy +
                    epszz.T @ wdetJ @ epszz +
                    epsxy.T @ wdetJ @ epsxy +
                    epsyz.T @ wdetJ @ epsyz +
                    epsxz.T @ wdetJ @ epsxz
                ).tocoo()
        elif kind == 'equilibrium gap':
            K = self.mesh.compute_K(nu, selection=self.mask_cell)

        k = 1/(self.mesh.nodes.max(axis=0) - self.mesh.nodes.min(axis=0))[:self.mesh.ndim].min()
        V = np.cos(2*np.pi*self.mesh.nodes[:,:self.mesh.ndim]*k).T.ravel()[:,None]

        R = K.T @ K
        A = ((V.T @ M @ V) / ( V.T @ R @ V)).squeeze()
        wm = (size*k)**4
        alpha = wm*A
        M = M + alpha*R

        self.reg = (M, R, alpha)

    def set_median(self, median):
        self.median = median

    def set_mean(self, mean):
        self.mean = mean

    def set_mask(self, mask, mask_threshold): #TODO
        self.mask = mask

        if isinstance(self.mesh, RegularMesh):
            norm = self.mesh.regular[1]**self.mesh.ndim
        elif self.mesh.ndim == 2:
            norm = self.mesh.surf()
        else:
            norm = self.mesh.vol()

        self.mask_cell = {T:ps >= mask_threshold*norm for T, ps in self.mesh.pixsum_by_cells(mask.astype(int), by_type=True).items()}
        self.mask_node = np.zeros(self.mesh.Nn, dtype='bool')
        nodes = []
        for T, sel in self.mask_cell.items():
            nodes.append(self.mesh.cells_by_type[T][sel])
        self.mask_cell = np.hstack(list(self.mask_cell.values()))
        nodes = np.hstack(nodes)
        self.mask_node[np.unique(nodes)] = True
        self.mask_M = np.tile(self.mask_node, (self.imref.ndim, 1)).ravel()

    def set_init(self, U_init, mesh=None, coef=1, mask=None):
        if U_init is None:
            self.U_init = np.zeros((self.mesh.Nn, self.imref.ndim), dtype='f4')
            return
        U_init = U_init[:,:self.imref.ndim].astype('f8')
        if mesh is None:
            self.U_init = U_init
        else:
            if mask is not None:
                self.U_init = mesh.interp_V(U_init, self.mesh, coef, mask_out=self.mask_node, mask_in=mask, out=('mean', 2))
            else:
                self.U_init = mesh.interp_V(U_init, self.mesh, coef)
        if mask is not None:
            self.U_init[~self.mask_node] = np.nan

    def set_convergence_params(self, itermax=None, normed_dU_min=None, diff_discr_min=None):
        if itermax is not None:
            self.itermax = itermax
        if normed_dU_min is not None:
            self.normed_dU_min = normed_dU_min
        if diff_discr_min is not None:
            self.diff_discr_min = diff_discr_min

    def set_solver(self, solver):
        self.solver = solver

    def compute(self, imdef, prompt=""): #TODO
        #

        #imdef = self.normim(imdef)

        if self.imref.ndim == 2:
            norm = self.mesh.surf().sum()
        else:
            norm = self.mesh.vol().sum()

        M = self.compute_M()

        if self.reg is not None:
            M, R, alpha = self.reg

        if self.mask is not None:
            M = M[:,self.mask_M].tocsr()[self.mask_M,:].tocsc()
            if self.reg is not None:
                R = R[:,self.mask_M].tocsr()[self.mask_M,:].tocsc()

        U_full = self.U_init

        if self.mask is not None:
            U = U_full[self.mask_node].T.ravel()
        else:
            U = U_full.T.ravel()

        dU = np.zeros_like(U)

        if self.debug_path is not None:
            if self.mask is not None:
                cell_values = {'mc': self.mask_cell}
                point_values = {'mn': self.mask_node}
            else:
                cell_values = {}
                point_values = {}
            debug_mesh = self.mesh.copy()
            debug_mesh.nodes *= 2**self.scale

        M = M.astype('f8')

        for c in range(self.itermax + 1):

            def_uv = self.mesh.interp(imdef, U_full, order=self.interp_order)
            def_uv[np.isnan(def_uv)] = 0

            bad_pix = np.isinf(def_uv)
            if bad_pix.sum():
                logging.warning(f"U gives position outside of imdef {int(bad_pix.sum())}")
                def_uv[bad_pix] = 0

            diff = self.imref[self.mesh.roi.slices] - def_uv[self.mesh.roi.slices]
            del def_uv

            if self.mask is not None:
                diff_mask = diff[self.mask[self.mesh.roi.slices]]
                residual = ((diff_mask[~np.isnan(diff_mask)]**2).sum()/norm)**.5
            else:
                residual = ((diff[~np.isnan(diff)]**2).sum()/norm)**.5

            if self.debug_path is not None:
                debug_mesh.save(
                    f'{self.debug_path}_i{c:03d}.vtk', U_full*2**self.scale,
                    cell_values=cell_values, point_values=point_values
                )

            if c > 0:
                diff_discr = residual - last_residual

                normed_dU = (dU.dot(dU) / (U.dot(U)))**.5

                logging.info(f"{prompt} {c:3d}: |dU/U| = {normed_dU:9.5f} ddiscr. = {diff_discr:+9.5f} discr. = {residual:9.5f}")

                if c == self.itermax - 1:
                    break
                if normed_dU < self.normed_dU_min:
                    break
                if abs(diff_discr) < self.diff_discr_min:
                    break

            last_residual = residual

            B = self.compute_B(diff).astype('f8')

            if self.mask is not None:
                B = B[self.mask_M]

            if self.reg is not None:
                B = B - alpha*(R @ U).reshape(B.shape)

            with Tictoc("solving"):
                if self.solver == 'spsolve':
                    X = splinalg.spsolve(M, B)
                elif hasattr(splinalg, self.solver):
                    N = [0]
                    def callback(X):
                        N[0] += 1
                        if logging.getLogger().level == TICTOC:
                            print(f'  {N[0]: 5d}\r', end='', flush=True)
                    X, _ = getattr(splinalg, self.solver)(M, B, maxiter=10000, callback=callback)
                    if logging.getLogger().level == TICTOC:
                        print('')

            if np.isnan(X).any():
                logging.warning(f"solver `{self.solver}` number of NaNs: {int(np.isnan(X).sum())} / {len(X)}")
                raise Exception('DIC failed')

            dU[:] = X
            U += dU

            if self.mask is not None:
                U_full[self.mask_node] = U.reshape((self.mesh.ndim, len(U)//self.mesh.ndim)).T
            else:
                U_full[:] = U.reshape((self.mesh.ndim, len(U)//self.mesh.ndim)).T

            if self.median > 0:
                if self.mask is not None:
                    U_full[~self.mask_node] = np.nan
                U_full[:] = self.mesh.median_V(U_full, self.median)
                if self.mask is not None:
                    U_full[~self.mask_node] = np.nan

            if self.mean > 0:
                if self.mask is not None:
                    U_full[~self.mask_node] = np.nan
                U_full[:] = self.mesh.mean_V(U_full, self.mean)
                if self.mask is not None:
                    U_full[~self.mask_node] = np.nan

            if self.mask is not None:
                U = U_full[self.mask_node].T.ravel()
            else:
                U = U_full.T.ravel()



        return U_full

