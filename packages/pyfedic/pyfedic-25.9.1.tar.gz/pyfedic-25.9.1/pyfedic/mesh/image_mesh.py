#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import ndimage
from scipy import sparse

from ..cells import Q4Q, C8Q
from .regular_mesh import RegularBaseMesh
from ..tictoc import tictoc

class Roi:
    """

    """

    def __init__(self, offset=None, shape=None):
        self.offset = tuple(offset)
        self.shape = tuple(shape)
        self.ndim = len(self.offset)

    def __repr__(self):
        return "Roi with origin at %s and shape %s." % (str(self.offset), str(self.shape))

    @property
    def slices(self):
        return tuple([slice(o, s+o) for o, s in zip(self.offset[:self.ndim], self.shape[:self.ndim])])

    @classmethod
    def from_mesh(cls, mesh):
        ndim = mesh.ndim
        offset = np.floor(mesh.nodes[:,ndim-1::-1].min(axis=0)+0.5).astype(int)
        shape = np.ceil(mesh.nodes[:,ndim-1::-1].max(axis=0)+0.5).astype(int)-offset
        return cls(offset, shape)

    def from_coords(xn, yn, zn=None):
        ndim = 2 if zn is None else 3
        if xn.ndim == 1:
            nodes = np.vstack((xn, yn, zn)).T
            offset = np.floor(nodes[:,ndim-1::-1].min(axis=0)+0.5).astype(int)
            shape = np.ceil(nodes[:,ndim-1::-1].max(axis=0)+0.5).astype(int)-offset
            return Roi(offset, shape)
        else: # xn.shape = (nbr of cell, nbr to bounding) -> (Np, Nc) -> (Nc, 3, Np)
            # (Np*3, Nc) -> (Nc, Np*3)
            nodes = np.vstack((xn, yn, zn)).T.reshape((xn.shape[1], 3, xn.shape[0]))
            offset = np.floor(nodes[:,:,ndim-1::-1].min(axis=0)+0.5).astype(int)
            shape = np.ceil(nodes[:,:,ndim-1::-1].max(axis=0)+0.5).astype(int)
            return [Roi(offset[i,:], shape[i,:]) for i in range(offset.shape[0])]

    def copy(self):
        return Roi(tuple(self.offset), tuple(self.shape))


class ImageMesh:
    ""

    def __init__(self):
        self._roi = Roi.from_mesh(self)
        self._pixN = None
        self._pixmask = None
        self._pixelt = None

    @property
    def roi(self):
        """Bounding box of the mesh. TODO: update this !

        :Exemple:

        >>> mesh = gen_mesh([5, 10], [3, 7.5], elt_size=2)
        >>> mesh
        Mesh with 4 cells and 9 nodes of type Q4.
        >>> mesh.xn
        array([ 5.5,  7.5,  9.5,  5.5,  7.5,  9.5,  5.5,  7.5,  9.5])
        >>> mesh.roi.slices
        (slice(3, 9, None), slice(5, 11, None))

        Returns
        -------
        out : tuple of slice
            a slice is returned for each dimension in zyx convention.

        """
        return self._roi

    @property
    def pixN(self):
        """

        Returns
        =======
        out: ndarray

        """

        return self._pixN

    @property
    def pixmask(self):
        """
        Mask for all pixels/voxels inside the mesh.

        Returns
        =======
        out: ndarray
            binary mask.

        """

        return self._pixmask

    @property
    def pixelt(self):
        """

        Returns
        =======
        out: ndarray

        """

        return self._pixelt

    def _pixsum_by_cells_regular(self, image, by_type=False):
        """
        see pixsum_by_cells.
        """
        pix_coords, _, coefs = self._get_regular_base()

        result = np.zeros(self.Nc)
        for i_cell, zyx in enumerate(self.iter_Nc()):
            x = ((pix_coords + zyx[None,:])*coefs[None,:]).sum(axis=1)
            result[i_cell] = image[self.roi.slices].flat[x].sum()

        if not by_type:
            return result

        return {self.cell_type: result}

    @tictoc
    def pixsum_by_cells(self, image, by_type=False):
        """
        Sum all pixel values included in each cells of the mesh.

        Returns
        -------
        result: array_like
            pixel sum for each cells.

        """
        if isinstance(self, RegularBaseMesh):
            return self._pixsum_by_cells_regular(image, by_type)

        im = image[self.roi.slices].flat
        result = np.zeros(self.Nc)

        if self.pixelt is None:
            self.compute_pixN()

        for c in range(self.Nc):
            result[c] = im[self.pixelt.indices[self.pixelt.indptr[c]:self.pixelt.indptr[c+1]]].sum()

        if not by_type:
            return result

        offset = 0
        result_by_type = {}
        for T, cells in self.cells_by_type.items():
            result_by_type[T] = result[offset:offset+len(cells)]
            offset = len(cells)

        return result_by_type

    def _compute_pixN_get_sizes(self):
        Np = np.prod(self.roi.shape)
        cs = (Np/self.Nc)**(1/self.ndim)
        order = max([T.order for T in self.cells_by_type])
        Nt = int((np.array(self.roi.shape)/cs*(cs+1)).prod()*(order+1)**self.ndim)
        return Np, Nt

    def _compute_pixN_get_pix(self, pp):
        xx, yy, zz = pp.T

        zpix, ypix, xpix = np.meshgrid(
            np.arange(np.ceil(zz.min()), np.floor(zz.max())+1),
            np.arange(np.ceil(yy.min()), np.floor(yy.max())+1),
            np.arange(np.ceil(xx.min()), np.floor(xx.max())+1),
            indexing='ij'
        )

        if self.ndim == 3:
            ipix = (zpix-self.roi.offset[0])*self.roi.shape[1]*self.roi.shape[2] + \
                    (ypix-self.roi.offset[1])*self.roi.shape[2]+xpix-self.roi.offset[2]
        else:
            ipix = (ypix-self.roi.offset[0])*self.roi.shape[1]+xpix-self.roi.offset[1]

        ipix = ipix.astype('i').ravel()
        xpix = xpix.astype('f8').ravel()
        ypix = ypix.astype('f8').ravel()
        zpix = zpix.astype('f8').ravel()

        return ipix, np.vstack((xpix, ypix, zpix)).T

    def _compute_pixN_regular(self, method=1):
        ""
        pix_coords, Ne, coefs = self._get_regular_base()

        nelems, elt_size = self.regular
        nelems = np.array(nelems)

        dimNe = Ne.size

        data = np.zeros(dimNe*np.prod(nelems), dtype='f4')
        col = np.zeros(dimNe*np.prod(nelems), dtype=int)
        row = np.zeros(dimNe*np.prod(nelems), dtype=int)

        for i_cell, zyx in enumerate(self.iter_Nc()):
            x = ((pix_coords + zyx[None,:])*coefs[None,:]).sum(axis=1)

            data[dimNe*i_cell:dimNe*(i_cell+1)] = Ne.ravel()
            row[dimNe*i_cell:dimNe*(i_cell+1)] = np.tile(x, self.cell_type.n_nodes)
            col[dimNe*i_cell:dimNe*(i_cell+1)] = np.repeat(self.cells[i_cell], elt_size**self.ndim)

        #N = sparse.csc_matrix((data, (row, col)), (np.prod(nelems*elt_size), np.prod(nelems+1)))
        N = sparse.csc_matrix((data, (row, col)), (np.prod(nelems*elt_size), self.cells.max()+1))
        del data, row, col
        N.eliminate_zeros()

        self._pixN = N
        self._pixmask = np.ones(np.prod(nelems*elt_size), dtype='bool')
        self._pixelt = np.repeat(np.arange(np.prod(nelems)), elt_size**self.ndim)

    @tictoc
    def compute_pixN(self):
        ""
        if isinstance(self, RegularBaseMesh):
            return self._compute_pixN_regular()

        self._pixN, done = self.compute_N(points=self, raw=True)
        Np = self._pixN.shape[0]

        pixelt_row = np.arange(Np)[done>0]
        pixelt_col = done[done>0]-1
        pixelt_val = np.ones(pixelt_col.shape, dtype='bool')

        self._pixmask = done.astype('bool')
        self._pixelt = sparse.csc_array((pixelt_val, (pixelt_row, pixelt_col)), shape=(Np, self.Nc))

    def save_pixN(self, filename):
        np.savez(filename, pixN=self._pixN, pixmask=self._pixmask, pixelt=self._pixelt)

    def load_pixN(self, filename):
        data = np.load(filename, allow_pickle=True)
        self._pixN, = data['pixN'].flat
        self._pixmask = data['pixmask']
        self._pixelt, = data['pixelt'].flat

    def _interp_regular(self, image, U, order=1, out=np.nan, inaccessible=np.inf):
        """
        see interp
        """
        pix_coords, Ne, coefs = self._get_regular_base()

        U = U[:,:image.ndim].copy()
        U[np.isnan(U)] = 0

        im_output = np.full_like(image, out, dtype='f4')

        for i_cell, zyx in enumerate(self.iter_Nc()):
            x = ((pix_coords + zyx[None,:])*coefs[None,:]).sum(axis=1)

            new_coords = np.vstack([pix_coords[:,j] + zyx[j] + self.roi.offset[j] + Ne.T @ U.T[::-1][j][self.cells[i_cell]] for j in range(self.ndim)])

            im_output[self.roi.slices].flat[x] = ndimage.map_coordinates(image, new_coords, im_output.dtype, cval=inaccessible, order=order)

        return im_output

    @tictoc
    def interp(self, image, U, order=1, out=np.nan, inaccessible=np.inf):
        """
        Interpolate the image as it was located on the mesh after
        the displacement field `U` was applied.

        Parameters
        ----------
        U : array_like
            displacement field of size (self.mesh.Nn, self.ndim).
        order : int, optional
            order of the interpolation (default value 1 means linear).
        out : float, optional
            value to set for pixels out of the self.mesh.

        Returns
        -------
        im_output: array_like
            deformed image of the same size as input image according the
            displacement field.

        """
        if isinstance(self, RegularBaseMesh):
            return self._interp_regular(image, U, order, out, inaccessible)

        U = U[:,:image.ndim].copy()
        U[np.isnan(U)] = 0

        im_output = np.full_like(image, out, dtype='f4')

        if self.pixN is None:
            self.compute_pixN()
        N = self.pixN

        # np.mgrid[self.roi.slices]   => ensemble des pixels de la boîte englobante
        #                                coordonnées Z, Y, x
        # x.ravel() + N.dot(u)        => warping des coordonnées des pixels
        # /!\ ça inclue des pixels hors mesh !
        new_coords = np.vstack([x.ravel() + N.dot(u) for x, u in zip(np.mgrid[self.roi.slices], U.T[::-1])])

        # redéfinition d'une ROI dans l'image
        slices = tuple(slice(max(0,s.start), min(d,s.stop)) for s, d in zip(self.roi.slices, image.shape))
        # définition d'un crop en cas d'une image plus petite que la ROI
        crop = tuple(slice(y.start - x.start, y.stop - x.start) for x, y in  zip(self.roi.slices, slices))

        # pixel dans le maillage et dans l'image
        pixmask = np.zeros(self.roi.shape, dtype=bool)
        pixmask[crop] = self.pixmask.reshape(self.roi.shape)[crop]

        im_output[slices].flat[pixmask[crop].ravel()] = ndimage.map_coordinates(image, new_coords[:,pixmask.flat], im_output.dtype, cval=inaccessible, order=order)
        return im_output

    @tictoc
    def transform(self, image, U, order=1, out=np.nan):
        """
        transform the image using the displacement field `U` holded by
        the mesh.

        In a manner, this function do the opposite to what the
        :func:`pyFEDIC.image.Image.interp` does.

        Parameters
        ----------
        U : array_like
            displacement field of size (self.mesh.Nn, self.ndim).
        order : int, optional
            order of the interpolation (default value 1 means linear).
        out : float, optional
            value to set for pixels out of the self.mesh.

        Returns
        -------
        im_output: array_like
            transformed image of the same size as input image according the
            displacement field.

        """
        return self.warp(U).interp(image, -U, order=order, out=out)

