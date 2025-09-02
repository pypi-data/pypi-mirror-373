#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as splinalg

from .mesh import Mesh, CompositeMesh
from .cells import Cell, Q4, T3

class FEM:
    """


    """

    def __init__(self, mesh, E, nu=0.3):
        self.mesh = mesh
        self.E = E
        self.nu = nu
        self._bcs = []
        self._loads = []
        self.bc = np.zeros(mesh.Nn*mesh.ndim, dtype='bool')
        self.U = np.zeros(mesh.Nn*mesh.ndim)
        self.Fint = np.zeros((mesh.ndim, mesh.Nn))
        self.Fext = np.zeros((mesh.ndim, mesh.Nn))

    @property
    def bcs(self):
        return self._bcs

    @bcs.setter
    def bcs(self, bcs):
        self._bcs = bcs

        for sel, uu in bcs:
            for i, u in enumerate(uu):
                if u is None:
                    continue
                if i >= self.mesh.ndim:
                    break
                self.bc.reshape((self.mesh.ndim,self.mesh.Nn))[i,sel] = True
                self.U.reshape((self.mesh.ndim,self.mesh.Nn))[i,sel] = u

    @property
    def loads(self):
        return self._loads

    @loads.setter
    def loads(self, loads):
        self._loads = loads

        for sel, F in loads:

            if self.mesh.ndim == 2:

                nods, = np.where(sel)
                vertices = self.mesh.vertices()

                vertice = vertices[np.in1d(vertices[:,0], nods) & np.in1d(vertices[:,1], nods), :]
                l = ((self.mesh.nodes[vertice[:,0],0]-self.mesh.nodes[vertice[:,1],0])**2 +
                     (self.mesh.nodes[vertice[:,0],1]-self.mesh.nodes[vertice[:,1],1])**2)**.5
                l /= l.sum()

                for i, f in enumerate(F):
                    if f is not None:
                        self.Fext[i, vertice[:,0]] += f*l/2
                        self.Fext[i, vertice[:,1]] += f*l/2


            else:

                nods, = np.where(sel)
                faces = self.mesh.faces().extract_selection(nids=nods)

                N = faces.compute_N(points=faces.gauss_points(True))

                surf = faces.surf()
                surf_tot = surf.sum()

                for i, f in enumerate(F):
                    if f is not None:
                        self.Fext[i, nods] = N.T.dot(f/surf_tot*surf)

    def solve(self):
        ""

        self.ddl = ~self.bc

        n2ddl = np.arange(self.mesh.Nn*self.mesh.ndim)
        n2ddl[self.ddl] = np.arange(self.ddl.sum())
        n2bc = np.arange(self.mesh.Nn*self.mesh.ndim)
        n2bc[self.bc] = np.arange(self.bc.sum())

        self.K = self.mesh.compute_K(self.nu, self.E)

        ind = self.ddl[self.K.col] & self.ddl[self.K.row]
        Kddl = sparse.coo_matrix((self.K.data[ind], (n2ddl[self.K.row[ind]], n2ddl[self.K.col[ind]])), shape=(self.ddl.sum(), self.ddl.sum()))

        ind = self.bc[self.K.col] & self.ddl[self.K.row]
        Kbc = sparse.coo_matrix((self.K.data[ind], (n2ddl[self.K.row[ind]], n2bc[self.K.col[ind]])), shape=(self.ddl.sum(), self.bc.sum()))

        B = self.Fint.flat[self.ddl] + self.Fext.flat[self.ddl] - Kbc.dot(self.U[self.bc])

        self.U[self.ddl] = splinalg.spsolve(Kddl.tocsr(), B)

        return self.U.reshape((self.mesh.ndim,self.mesh.Nn)).T

