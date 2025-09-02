#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod
import numpy as np
import sympy

class GenericCell:
    ""

    def __init__(self, nodes):
        self.nodes = nodes

        self.normal, self._normal = self._normal, self.normal
        self.surface, self._surface = self._surface, self.surface
        self.volume, self._volume = self._volume, self.volume

    def _normal(self):
        return self._normal(np.arange(self.n_nodes)[None,:], self.nodes)

    def _surface(self):
        return self._surface(np.arange(self.n_nodes)[None,:], self.nodes)

    def _volume(self):
        return self._volume(np.arange(self.n_nodes)[None,:], self.nodes)

    @classmethod
    @abstractmethod
    def volume(cls, cells, nodes):
        """
        Returning the volume of each 3D cells.

        Parameters
        ==========
        cells: array_like of size (M, self.n_nodes)
            nodes indexes for each cell
        nodes: array_like of size N, 2|3
            x,y(,z) coordinates

        Returns
        =======
        out: ndarray of size M
            volume of each cells.

        """
        pass

    @classmethod
    @abstractmethod
    def surface(cls, cells, nodes):
        """
        Returning the surface of each 2D cells.

        Parameters
        ==========
        cells: array_like of size (M, self.n_nodes)
            nodes indexes for each cell
        nodes: array_like of size N, 2|3
            x,y(,z) coordinates

        Returns
        =======
        out: ndarray of size M
            surface of each cells.

        """
        pass

    @classmethod
    @abstractmethod
    def normal(cls, cells, nodes):
        """
        Returning the surface normal of each 2D cells.

        Parameters
        ==========
        cells: array_like of size (M, self.n_nodes)
            nodes indexes for each cell
        nodes: array_like of size N, 2|3
            x,y(,z) coordinates

        Returns
        =======
        out: ndarray of size M
            surface normal of each cells.

        """
        pass

    @classmethod
    def is_inside(cls, points):
        """
        Check for each point if it's inside the element

        Parameters
        ==========
        points: array_like of size N, 2|3
            x,y(,z) coordinates

        Returns
        =======
        out: ndarray of size N
            True if inside False if not.

        """
        test = np.ones(len(points), dtype=bool)
        for rule in cls._N:
            test &= (rule(*points.T[:cls.ndim]) >= -cls.EPSILON)
        return test

    @classmethod
    def N(cls, points):
        """
        Compute shape functions at point coordinate

        Parameters
        ==========
        points: array_like of size N, 2|3
            x,y(,z) coordinates

        Returns
        =======
        out: ndarray of shape (P, M)
            shape functions at point coordinate assuming P shape functions

        """
        return np.vstack([N(*points.T[:cls.ndim]) for N in cls._N])

    @classmethod
    def dNdv(cls, v, points):
        """
        Compute component part of Jacobian matrix of shape functions at point coordinate

        Parameters
        ==========
        v: sympy.core.symbol.Symbol
            component used for derivative calculations
        points: array_like of size N, 2|3
            x,y(,z) coordinates

        Returns
        =======
        out: ndarray of shape (P, M)
            component part of Jacobian matrix of shape functions at point coordinate assuming P shape functions

        """
        result = np.zeros((cls.n_nodes, len(points)))
        for i, dN in enumerate(cls._dN[v]):
            result[i,:] = dN(*points.T[:cls.ndim])
        return result

    @classmethod
    def dN(cls, points):
        """
        Compute Jacobian matrix of shape functions at point coordinate for all component

        Parameters
        ==========
        points: array_like of size N, 2|3
            x,y(,z) coordinates

        Returns
        =======
        out: generator
            component part of Jacobian matrix of shape functions at point coordinate assuming P shape functions for all component

        """
        return np.stack([cls.dNdv(v, points) for v in range(cls.ndim)])

    @classmethod
    def get_gauss_points(cls, weight=True, reduced_integration=False):
        """
        Returns Gauss point(s) of the Cell element

        Parameters
        ==========
        reduced_integration: boolean

        Returns
        =======
        out: tuple
            gauss point(s)
            4 tuple are used to described gauss points:

             * r values
             * s values
             * t values
             * w values

        """
        if weight:
            if reduced_integration:
                return cls.gauss_reduced, cls.gauss_reduced_w
            else:
                return cls.gauss, cls.gauss_w
        else:
            if reduced_integration:
                return cls.gauss_reduced
            else:
                return cls.gauss

    @classmethod
    def get_param_coordinate(cls, nodes, points):
        Np = len(points)

        N = cls.N(np.zeros((1, cls.ndim))).T
        dN = cls.dN(np.zeros((1, cls.ndim))).transpose(2, 0, 1)

        J = dN[0] @ nodes[:,:cls.ndim]
        invJ = np.linalg.inv(J).T

        pp = N[0] @ nodes[:,:cls.ndim]

        pg = (invJ @ (points[:,:cls.ndim] - pp).T).T

        res = (pg**2).sum(axis=1)

        is_ok = np.ones(Np, dtype=bool)

        if not cls.is_linear:

            N = np.zeros((Np, *N.shape[1:]))
            dN = np.zeros((Np, *dN.shape[1:]))
            J = np.zeros((Np, *J.shape))

            to_do = (res > 1.e-12) & is_ok

            for niter in range(1000):
                #
                N[to_do] = cls.N(pg[to_do]).T
                dN[to_do] = cls.dN(pg[to_do]).transpose(2, 0, 1)

                J[to_do] = dN[to_do] @ nodes[:,:cls.ndim]

                is_ok[to_do] = np.linalg.det(J[to_do]) > 0
                to_do = to_do & is_ok

                if (~to_do).all():
                    break

                invJ = np.linalg.inv(J[to_do]).transpose((0,2,1))

                pp = N[to_do] @ nodes[:,:cls.ndim]

                dg = (invJ @ (points[to_do,:cls.ndim] - pp)[:,:,None])[...,0]

                res[to_do] = (dg**2).sum(axis=1)

                pg[to_do] += dg

                to_do[to_do] = res[to_do] > 1.e-12

                if (~to_do).all():
                    break

        is_ok[is_ok] &= cls.is_inside(pg[is_ok])

        pg[~is_ok] = 0

        if cls.ndim == 2:
            pg = np.hstack((pg, np.zeros((Np, 1))))

        return pg, is_ok


class Cell(type):
    """
    Cell(name, vtk_id, ndim, order, shapes, gauss_reduced, gauss, surface=None, volume=None, normal=None, vertices=[], faces=[])

    A Cell object is a definition of a mesh element in term or FEM element.

    Parameters
    ==========
    name: string
        name of the cell type
    vtk_id: integer
        see [VTK File Format]
    ndim : integer
        2 for 2D, 3 for 3D
    order: integer
        1 for linear, 2 for quadratic
    shapes : tuple
        shapes function of the FEM element
        each shape is described by a sympy function of r, s and t (if 3D)
    gauss_reduced : tuple
        gauss point for reduced integration
        4 tuple are used to described gauss points:

         * r values
         * s values
         * t values
         * w values
    gauss : tuple
        gauss points for the first order
        4 tuple are used to described gauss points:

         * r values
         * s values
         * t values
         * w values
    surface : function
        function f(cells, xn, yn) returning the surface of each 2D cells
    normal : function
        function f(cells, xn, yn) returning the normal of each 2D cells
    volume : function
        function f(cells, xn, yn, zn) returning the volume of each 3D cells
    vertices : tuple
        couples of nodes indices for each vertices of the cell
    faces : tuple
        triplet of nodes indices for each triangle face of 3D cell
        quadruplet of nodes indices for each quadrangle face of 3D cell

    """
    _by_vtk_id = {}
    _by_name = {}
    _list = []
    EPSILON = 1e-12

    def __new__(cls, name, bases, classdict):
        result = type.__new__(cls, name, bases, classdict)
        symbols = set()
        if result.order > 0:
            for x in result.shapes:
                symbols = symbols.union(x.as_poly().free_symbols)
        result.symbols = list(symbols)
        result.symbols.sort(key=str)
        result._N = [sympy.lambdify(result.symbols, shape) for shape in result.shapes]
        result._dN = [[sympy.lambdify(result.symbols, shape.diff(symbol)) for shape in result.shapes] for symbol in result.symbols]
        result.n_nodes = len(result.shapes)
        result.ndim = len(result.symbols)

        if result.order > 0:
            result._N_data = np.zeros(((result.n_nodes,) + (result.order+1,) * result.ndim))
            for i, shape in enumerate(result.shapes):
                for k, v in shape.as_poly(result.symbols).as_dict().items():
                    result._N_data[(i,) + k] = v

            result._N_data = result._N_data.reshape((result.n_nodes, (result.order+1)**result.ndim))

            result._dN_data = np.zeros(((result.ndim, result.n_nodes) + (result.order+1,) * result.ndim))
            for i, symbol in enumerate(result.symbols):
                for j, shape in enumerate(result.shapes):
                    for k, v in shape.as_poly(result.symbols).diff(symbol).as_dict().items():
                        result._dN_data[(i,j) + k] = v

            result._dN_data = result._dN_data.reshape((result.ndim, result.n_nodes, (result.order+1)**result.ndim))

        if result.ndim > 0:
            result.vertices = np.array(result.vertices)
        gauss_reduced = np.array(result.gauss_reduced)
        result.gauss_reduced = gauss_reduced[:,:-1]
        result.gauss_reduced_w = gauss_reduced[:,-1]
        gauss = np.array(result.gauss)
        result.gauss = gauss[:,:-1]
        result.gauss_w = gauss[:,-1]
        result.ng = len(result.gauss)
        result.is_linear = result.n_nodes == result.ndim
        result.name = result.__name__
        cls._by_vtk_id[result.vtk_id] = result
        cls._by_name[result.__name__] = result
        cls._list.append(result)

        if result.order == 2:
            result._linear = cls.by_name(result.__name__[:-1])
            cls.by_name(result.__name__[:-1])._quad = result

        return result

    @classmethod
    def by_name(cls, name):
        return cls._by_name[name]

    @classmethod
    def by_vtk_id(cls, vtk_id):
        return cls._by_vtk_id[vtk_id]

    @classmethod
    def iter_by_celltype(cls, cell_dict):
        for T in cls._list:
            if T in cell_dict:
                yield T, cell_dict[T]


r = sympy.var('r')
s = sympy.var('s')
t = sympy.var('t')

class T3(GenericCell, metaclass=Cell):
    ""

    vtk_id = 5
    order = 1

    shapes = (
        1-r-s,
        r,
        s,
    )

    gauss_reduced = (
        (1/3, 1/3, 1/2),
    )

    gauss = (
        (1/6, 1/6, 1/6),
        (2/3, 1/6, 1/6),
        (1/6, 2/3, 1/6),
    )

    vertices = (
        (0, 1),
        (1, 2),
        (2, 0),
    )

    @classmethod
    def normal(cls, cells, nodes):
        a_b = (nodes[cells[:,1]] - nodes[cells[:,0]]).T
        a_c = (nodes[cells[:,2]] - nodes[cells[:,0]]).T

        return -np.vstack((a_c[1,:]*a_b[2,:] - a_c[2,:]*a_b[1,:],
                           a_c[2,:]*a_b[0,:] - a_c[0,:]*a_b[2,:],
                           a_c[0,:]*a_b[1,:] - a_c[1,:]*a_b[0,:]))

    @classmethod
    def surface(cls, cells, nodes):
        n = cls.normal(cells, nodes)
        return 1/2*(n[0,:]**2+n[1,:]**2+n[2,:]**2)**.5


class T3Q(GenericCell, metaclass=Cell):
    ""

    vtk_id = 22
    order = 2

    shapes = (
        -(1-r-s)*(1-2*(1-r-s)),
        -r*(1-2*r),
        -s*(1-2*s),
        4*r*(1-r-s),
        4*r*s,
        4*s*(1-r-s)
    )

    gauss_reduced = (
        (1/3, 1/3, 1/2),
    )

    gauss = (
        (      0.091576213509771,       0.091576213509771, 0.0549758718227661),
        (1 - 2*0.091576213509771,       0.091576213509771, 0.0549758718227661),
        (      0.091576213509771, 1 - 2*0.091576213509771, 0.0549758718227661),
        (      0.445948490915965, 1 - 2*0.445948490915965, 0.11169079483905),
        (      0.445948490915965,       0.445948490915965, 0.11169079483905),
        (1 - 2*0.445948490915965,       0.445948490915965, 0.11169079483905),
    )

    vertices =  (
        (0, 3),
        (3, 1),
        (1, 4),
        (4, 2),
        (2, 5),
        (5, 0),
    )

    @classmethod
    def normal(cls, cells, nodes):
        return T3.normal(cells, nodes)

    @classmethod
    def surface(cls, cells, nodes):
        return T3.surface(cells, nodes)

    @classmethod
    def is_inside(cls, points):
        return T3.is_inside(points)


class Q4(GenericCell, metaclass=Cell):
    ""

    vtk_id = 9
    order = 1

    shapes = (
        0.25*(1-r)*(1-s),
        0.25*(1+r)*(1-s),
        0.25*(1+r)*(1+s),
        0.25*(1-r)*(1+s),
    )

    gauss_reduced = (
        (0., 0., 4.),
    )

    gauss = (
        (-1/3**.5, -1/3**.5, 1.),
        ( 1/3**.5, -1/3**.5, 1.),
        ( 1/3**.5,  1/3**.5, 1.),
        (-1/3**.5,  1/3**.5, 1.),
    )

    vertices = (
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
    )

    @classmethod
    def normal(cls, cells, nodes):
        return T3.normal(cells[:,[0,1,2]], nodes) + T3.normal(cells[:,[2,3,0]], nodes)

    @classmethod
    def surface(cls, cells, nodes):
        n = cls.normal(cells, nodes)
        return 1/2*(n[0,:]**2+n[1,:]**2+n[2,:]**2)**.5


class Q4Q(GenericCell, metaclass=Cell):
    ""

    vtk_id = 23
    order = 2

    shapes = (
       (1-r)*(1-s)*(-1-r-s)/4,
       (1+r)*(1-s)*(-1+r-s)/4,
       (1+r)*(1+s)*(-1+r+s)/4,
       (1-r)*(1+s)*(-1-r+s)/4,
       (1-r**2)*(1-s)/2,
       (1+r)*(1-s**2)/2,
       (1-r**2)*(1+s)/2,
       (1-r)*(1-s**2)/2,
    )

    gauss_reduced = (
        (0., 0., 4.),
    )

    gauss = (
        (-0.774596669241483, -0.774596669241483, 25/81),
        ( 0.774596669241483, -0.774596669241483, 25/81),
        ( 0.774596669241483,  0.774596669241483, 25/81),
        (-0.774596669241483,  0.774596669241483, 25/81),
        ( 0.0              , -0.774596669241483, 40/81),
        ( 0.774596669241483,  0.0              , 40/81),
        ( 0.0              ,  0.774596669241483, 40/81),
        (-0.774596669241483,  0.0              , 40/81),
        ( 0.0              ,  0.0              , 64/81),
    )

    vertices = (
        (0, 4),
        (4, 1),
        (1, 5),
        (5, 2),
        (2, 6),
        (6, 3),
        (3, 7),
        (7, 0),
    )

    @classmethod
    def normal(cls, cells, nodes):
        return Q4.normal(cells, nodes)

    @classmethod
    def surface(cls, cells, nodes):
        return Q4.surface(cells, nodes)

    @classmethod
    def is_inside(cls, points):
        return Q4.is_inside(points)


class T4(GenericCell, metaclass=Cell):
    ""

    vtk_id = 10
    order = 1

    shapes = (
        s,
        t,
        1-r-s-t,
        r,
    )

    gauss_reduced = (
        (1/4, 1/4, 1/4, 1/6),
    )

    gauss = (
        ((5 - 5**.5)/20, (5 - 5**.5)/20, (5 - 5**.5)/20, 1/24),
        ((5 - 5**.5)/20, (5 - 5**.5)/20, (5+3*5**.5)/20, 1/24),
        ((5 - 5**.5)/20, (5+3*5**.5)/20, (5 - 5**.5)/20, 1/24),
        ((5+3*5**.5)/20, (5 - 5**.5)/20, (5 - 5**.5)/20, 1/24),
    )

    vertices = (
        (0, 1),
        (1, 2),
        (2, 0),
        (0, 3),
        (1, 3),
        (2, 3),
    )

    faces = (
        (0, 2, 1),
        (0, 3, 2),
        (2, 3, 1),
        (0, 1, 3),
    )

    @classmethod
    def volume(cls, cells, nodes):
        a_d = (nodes[cells[:,0]] - nodes[cells[:,3]]).T
        b_d = (nodes[cells[:,1]] - nodes[cells[:,3]]).T
        c_d = (nodes[cells[:,2]] - nodes[cells[:,3]]).T

        b_dxc_d = np.vstack((b_d[1,:]*c_d[2,:]-b_d[2,:]*c_d[1,:],
                            b_d[2,:]*c_d[0,:]-b_d[0,:]*c_d[2,:],
                            b_d[0,:]*c_d[1,:]-b_d[1,:]*c_d[0,:]))

        return 1/6*abs(a_d[0,:]*b_dxc_d[0,:]+a_d[1,:]*b_dxc_d[1,:]+a_d[2,:]*b_dxc_d[2,:])


class T4Q(GenericCell, metaclass=Cell):
    ""

    vtk_id = 24
    order = 2

    shapes = (
        s*(2*s-1),
        t*(2*t-1),
        (1-r-s-t)*(1-2*r-2*s-2*t),
        r*(2*r-1),
        4*s*t,
        4*t*(1-r-s-t),
        4*s*(1-r-s-t),
        4*r*s,
        4*r*t,
        4*r*(1-r-s-t)
    )

    gauss_reduced = (
        (1/4, 1/4, 1/4, 1/6),
    )

    gauss = (
        (0.25, 0.25, 0.25, 8/405),
        ((7+15**.5)/34, (7+15**.5)/34, (7+15**.5)/34, 2665-14*15**.5),
        ((7+15**.5)/34, (7+15**.5)/34, (13-3*15**.5)/34, 2665-14*15**.5),
        ((7+15**.5)/34, (13-3*15**.5)/34, (7+15**.5)/34, 2665-14*15**.5),
        ((13-3*15**.5)/34, (7+15**.5)/34, (7+15**.5)/34, 2665-14*15**.5),
        ((7-15**.5)/34, (7-15**.5)/34, (7-15**.5)/34, 2665+14*15**.5),
        ((7-15**.5)/34, (7-15**.5)/34, (13+3*15**.5)/34, 2665+14*15**.5),
        ((7-15**.5)/34, (13+3*15**.5)/34, (7-15**.5)/34, 2665+14*15**.5),
        ((13+3*15**.5)/34, (7-15**.5)/34, (7-15**.5)/34, 2665+14*15**.5),
        ((5-15**.5)/20, (5-15**.5)/20, (5+15**.5)/20, 5/567),
        ((5-15**.5)/20, (5+15**.5)/20, (5-15**.5)/20, 5/567),
        ((5+15**.5)/20, (5-15**.5)/20, (5-15**.5)/20, 5/567),
        ((5-15**.5)/20, (5+15**.5)/20, (5+15**.5)/20, 5/567),
        ((5+15**.5)/20, (5-15**.5)/20, (5+15**.5)/20, 5/567),
        ((5+15**.5)/20, (5+15**.5)/20, (5-15**.5)/20, 5/567),
    )

    vertices = (
        (0, 4),
        (4, 1),
        (1, 5),
        (5, 2),
        (2, 6),
        (6, 0),
        (0, 7),
        (7, 3),
        (1, 8),
        (8, 3),
        (2, 9),
        (9, 3),
    )

    faces = (
        (0, 2, 1),
        (0, 3, 2),
        (2, 3, 1),
        (0, 1, 3),
    )

    @classmethod
    def volume(cls, cells, nodes):
        return T4.volume(cells, nodes)

    @classmethod
    def is_inside(cls, points):
        return T4.is_inside(points)


class C8(GenericCell, metaclass=Cell):
    ""

    vtk_id = 12
    order = 1

    shapes = (
        0.125*(1-r)*(1-s)*(1-t),
        0.125*(1+r)*(1-s)*(1-t),
        0.125*(1+r)*(1+s)*(1-t),
        0.125*(1-r)*(1+s)*(1-t),
        0.125*(1-r)*(1-s)*(1+t),
        0.125*(1+r)*(1-s)*(1+t),
        0.125*(1+r)*(1+s)*(1+t),
        0.125*(1-r)*(1+s)*(1+t),
    )

    gauss_reduced = (
        (0., 0., 0., 8.,),
    )

    gauss = (
        (-1/3**.5, -1/3**.5, -1/3**.5, 1.),
        (-1/3**.5, -1/3**.5,  1/3**.5, 1.),
        (-1/3**.5,  1/3**.5, -1/3**.5, 1.),
        (-1/3**.5,  1/3**.5,  1/3**.5, 1.),
        ( 1/3**.5, -1/3**.5, -1/3**.5, 1.),
        ( 1/3**.5, -1/3**.5,  1/3**.5, 1.),
        ( 1/3**.5,  1/3**.5, -1/3**.5, 1.),
        ( 1/3**.5,  1/3**.5,  1/3**.5, 1.),
    )

    vertices = (
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    )

    faces = (
        (0, 3, 2, 1),
        (0, 1, 5, 4),
        (0, 4, 7, 3),
        (3, 7, 6, 2),
        (4, 5, 6, 7),
        (2, 6, 5, 1),
    )

    @classmethod
    def volume(cls, cells, nodes):
        pd = nodes[cells].mean(axis=1)

        vol = 0
        for i, j, k in [
            (0, 1, 2),
            (2, 3, 0),
            (4, 5, 6),
            (6, 7, 4),
            (3, 2, 7),
            (7, 6, 2),
            (2, 1, 5),
            (5, 6, 2),
            (1, 5, 4),
            (4, 0, 1),
            (0, 4, 7),
            (7, 3, 0)]:

            a_d = (nodes[cells[:,i]] - pd).T
            b_d = (nodes[cells[:,j]] - pd).T
            c_d = (nodes[cells[:,k]] - pd).T

            b_dxc_d = np.vstack((b_d[1,:]*c_d[2,:]-b_d[2,:]*c_d[1,:],
                                 b_d[2,:]*c_d[0,:]-b_d[0,:]*c_d[2,:],
                                 b_d[0,:]*c_d[1,:]-b_d[1,:]*c_d[0,:]))

            vol += 1/6*abs(a_d[0,:]*b_dxc_d[0,:]+a_d[1,:]*b_dxc_d[1,:]+a_d[2,:]*b_dxc_d[2,:])

        return vol


class C8Q(GenericCell, metaclass=Cell):
    ""

    vtk_id = 25
    order = 2

    shapes = (
        1/8*(1-r)*(1-s)*(1-t)*(-2-r-s-t), # ASTER 1
        1/8*(1+r)*(1-s)*(1-t)*(-2+r-s-t), # ASTER 2
        1/8*(1+r)*(1+s)*(1-t)*(-2+r+s-t), # ASTER 3
        1/8*(1-r)*(1+s)*(1-t)*(-2-r+s-t), # ASTER 4
        1/8*(1-r)*(1-s)*(1+t)*(-2-r-s+t), # ASTER 5
        1/8*(1+r)*(1-s)*(1+t)*(-2+r-s+t), # ASTER 6
        1/8*(1+r)*(1+s)*(1+t)*(-2+r+s+t), # ASTER 7
        1/8*(1-r)*(1+s)*(1+t)*(-2-r+s+t), # ASTER 8
        1/4*(1-r**2)*(1-s)*(1-t), # ASTER 9
        1/4*(1-s**2)*(1+r)*(1-t), # ASTER 10
        1/4*(1-r**2)*(1+s)*(1-t), # ASTER 11
        1/4*(1-s**2)*(1-r)*(1-t), # ASTER 12
        1/4*(1-r**2)*(1-s)*(1+t), # ASTER 17
        1/4*(1-s**2)*(1+r)*(1+t), # ASTER 18
        1/4*(1-r**2)*(1+s)*(1+t), # ASTER 19
        1/4*(1-s**2)*(1-r)*(1+t), # ASTER 20
        1/4*(1-t**2)*(1-r)*(1-s), # ASTER 13
        1/4*(1-t**2)*(1+r)*(1-s), # ASTER 14
        1/4*(1-t**2)*(1+r)*(1+s), # ASTER 15
        1/4*(1-t**2)*(1-r)*(1+s), # ASTER 16
    )

    gauss_reduced = (
        (0., 0., 0., 8.,),
    )

    gauss = (
        (-(3/5)**.5, -(3/5)**.5, -(3/5)**.5, (5/9)**3),
        (-(3/5)**.5, -(3/5)**.5,          0, (5/9)**2*8/9),
        (-(3/5)**.5, -(3/5)**.5,  (3/5)**.5, (5/9)**3),
        (-(3/5)**.5,          0, -(3/5)**.5, (5/9)**2*8/9),
        (-(3/5)**.5,          0,          0, (5/9)**1*8/9**2),
        (-(3/5)**.5,          0,  (3/5)**.5, (5/9)**2*8/9),
        (-(3/5)**.5,  (3/5)**.5, -(3/5)**.5, (5/9)**3),
        (-(3/5)**.5,  (3/5)**.5,          0, (5/9)**2*8/9),
        (-(3/5)**.5,  (3/5)**.5,  (3/5)**.5, (5/9)**3),

        (         0, -(3/5)**.5, -(3/5)**.5, (5/9)**2*8/9),
        (         0, -(3/5)**.5,          0, (5/9)**1*8/9**2),
        (         0, -(3/5)**.5,  (3/5)**.5, (5/9)**2*8/9),
        (         0,          0, -(3/5)**.5, (5/9)**1*8/9**2),
        (         0,          0,          0, (5/9)**3),
        (         0,          0,  (3/5)**.5, (5/9)**1*8/9**2),
        (         0,  (3/5)**.5, -(3/5)**.5, (5/9)**2*8/9),
        (         0,  (3/5)**.5,          0, (5/9)**1*8/9**2),
        (         0,  (3/5)**.5,  (3/5)**.5, (5/9)**2*8/9),

        ( (3/5)**.5, -(3/5)**.5, -(3/5)**.5, (5/9)**3),
        ( (3/5)**.5, -(3/5)**.5,          0, (5/9)**2*8/9),
        ( (3/5)**.5, -(3/5)**.5,  (3/5)**.5, (5/9)**3),
        ( (3/5)**.5,          0, -(3/5)**.5, (5/9)**2*8/9),
        ( (3/5)**.5,          0,          0, (5/9)**1*8/9**2),
        ( (3/5)**.5,          0,  (3/5)**.5, (5/9)**2*8/9),
        ( (3/5)**.5,  (3/5)**.5, -(3/5)**.5, (5/9)**3),
        ( (3/5)**.5,  (3/5)**.5,          0, (5/9)**2*8/9),
        ( (3/5)**.5,  (3/5)**.5,  (3/5)**.5, (5/9)**3),
    )

    vertices = (
        (0,  8),
        (8, 1),
        (1,  9),
        (9, 2),
        (2, 10),
        (10, 3),
        (3, 11),
        (11, 0),
        (4, 12),
        (12, 5),
        (5, 13),
        (13, 6),
        (6, 14),
        (14, 7),
        (7, 15),
        (15, 4),
        (0, 16),
        (16, 4),
        (1, 17),
        (17, 5),
        (2, 18),
        (18, 6),
        (3, 19),
        (19, 7),
    )

    faces = (
        (0, 3, 2, 1),
        (0, 1, 5, 4),
        (0, 4, 7, 3),
        (3, 7, 6, 2),
        (4, 5, 6, 7),
        (2, 6, 5, 1),
    )

    @classmethod
    def volume(cls, cells, nodes):
        return C8.volume(cells, nodes)

    @classmethod
    def is_inside(cls, points):
        return C8.is_inside(points)


class P6(GenericCell, metaclass=Cell):
    ""

    vtk_id = 13
    order = 1

    shapes = (
        0.5*s*(1-r),
        0.5*t*(1-r),
        0.5*(1-s-t)*(1-r),
        0.5*s*(1+r),
        0.5*t*(1+r),
        0.5*(1-s-t)*(1+r),
    )

    gauss_reduced = (
        (0., 1/3, 1/3, 1.,),
    )

    gauss = (
        (-0.577350269189626, 1/3, 1/3, -27/96),
        (-0.577350269189626, 0.6, 0.2,  25/96),
        (-0.577350269189626, 0.2, 0.6,  25/96),
        (-0.577350269189626, 0.2, 0.2,  25/96),
        ( 0.577350269189626, 1/3, 1/3, -27/96),
        ( 0.577350269189626, 0.6, 0.2,  25/96),
        ( 0.577350269189626, 0.2, 0.6,  25/96),
        ( 0.577350269189626, 0.2, 0.2,  25/96),
    )

    vertices = (
        (0, 1),
        (1, 2),
        (2, 0),
        (3, 4),
        (4, 5),
        (5, 3),
        (0, 3),
        (1, 4),
        (2, 5),
    )

    faces = (
        (0, 2, 1),
        (3, 4, 5),
        (0, 3, 5, 2),
        (2, 5, 4, 1),
        (1, 4, 3, 0),
    )

    @classmethod
    def volume(cls, cells, nodes):
        pd = nodes[cells].mean(axis=1)

        vol = 0

        for i, j, k in [
            (0, 1, 2),
            (0, 2, 5),
            (5, 3, 0),
            (0, 3, 4),
            (4, 1, 0),
            (1, 4, 5),
            (5, 2, 1),
            (3, 4, 5)]:

            a_d = (nodes[cells[:,i]] - pd).T
            b_d = (nodes[cells[:,j]] - pd).T
            c_d = (nodes[cells[:,k]] - pd).T

            b_dxc_d = np.vstack((b_d[1,:]*c_d[2,:]-b_d[2,:]*c_d[1,:],
                                b_d[2,:]*c_d[0,:]-b_d[0,:]*c_d[2,:],
                                b_d[0,:]*c_d[1,:]-b_d[1,:]*c_d[0,:]))

            vol += 1/6*abs(a_d[0,:]*b_dxc_d[0,:]+a_d[1,:]*b_dxc_d[1,:]+a_d[2,:]*b_dxc_d[2,:])

        return vol


class P6Q(GenericCell, metaclass=Cell):
    ""

    vtk_id = 26
    order = 2

    shapes = (
        s*(1-r)*(2*s-2-r)/2, # ASTER 1
        t*(1-r)*(2*t-2-r)/2, # ASTER 2
        (r-1)*(1-s-t)*(r+2*s+2*t)/2, # ASTER 3
        s*(1+r)*(2*s-2+r)/2, # ASTER 4
        t*(1+r)*(2*t-2+r)/2, # ASTER 5
        (-r-1)*(1-s-t)*(-r+2*s+2*t)/2, # ASTER 6
        2*s*t*(1-r), # ASTER 7
        2*t*(1-s-t)*(1-r), # ASTER 8
        2*s*(1-s-t)*(1-r), # ASTER 9
        2*s*t*(1+r), # ASTER 13
        2*t*(1-s-t)*(1+r), # ASTER 14
        2*s*(1-s-t)*(1+r), # ASTER 15
        s*(1-r**2), # ASTER 10
        t*(1-r**2), # ASTER 11
        (1-s-t)*(1-r**2), # ASTER 12
    )

    gauss_reduced = (
        (0., 1/3, 1/3, 1.,),
    )

    gauss = (
        (-(3/5)**.5,               1/3,               1/3, 5/9*9/80),
        (-(3/5)**.5,     (6+15**.5)/21,     (6+15**.5)/21, 5/9*(155+15**.5)/2400),
        (-(3/5)**.5, 1-2*(6+15**.5)/21,     (6+15**.5)/21, 5/9*(155+15**.5)/2400),
        (-(3/5)**.5,     (6+15**.5)/21, 1-2*(6+15**.5)/21, 5/9*(155+15**.5)/2400),
        (-(3/5)**.5,     (6-15**.5)/21,     (6-15**.5)/21, 5/9*(155-15**.5)/2400),
        (-(3/5)**.5, 1-2*(6-15**.5)/21,     (6-15**.5)/21, 5/9*(155-15**.5)/2400),
        (-(3/5)**.5,     (6-15**.5)/21, 1-2*(6-15**.5)/21, 5/9*(155-15**.5)/2400),
        (         0,               1/3,               1/3, 8/9*9/80),
        (         0,     (6+15**.5)/21,     (6+15**.5)/21, 8/9*(155+15**.5)/2400),
        (         0, 1-2*(6+15**.5)/21,     (6+15**.5)/21, 8/9*(155+15**.5)/2400),
        (         0,     (6+15**.5)/21, 1-2*(6+15**.5)/21, 8/9*(155+15**.5)/2400),
        (         0,     (6-15**.5)/21,     (6-15**.5)/21, 8/9*(155-15**.5)/2400),
        (         0, 1-2*(6-15**.5)/21,     (6-15**.5)/21, 8/9*(155-15**.5)/2400),
        (         0,     (6-15**.5)/21, 1-2*(6-15**.5)/21, 8/9*(155-15**.5)/2400),
        ( (3/5)**.5,               1/3,               1/3, 5/9*9/80),
        ( (3/5)**.5,     (6+15**.5)/21,     (6+15**.5)/21, 5/9*(155+15**.5)/2400),
        ( (3/5)**.5, 1-2*(6+15**.5)/21,     (6+15**.5)/21, 5/9*(155+15**.5)/2400),
        ( (3/5)**.5,     (6+15**.5)/21, 1-2*(6+15**.5)/21, 5/9*(155+15**.5)/2400),
        ( (3/5)**.5,     (6-15**.5)/21,     (6-15**.5)/21, 5/9*(155-15**.5)/2400),
        ( (3/5)**.5, 1-2*(6-15**.5)/21,     (6-15**.5)/21, 5/9*(155-15**.5)/2400),
        ( (3/5)**.5,     (6-15**.5)/21, 1-2*(6-15**.5)/21, 5/9*(155-15**.5)/2400),
    )

    vertices = (
        (0, 6),
        (6, 1),
        (1, 7),
        (7, 2),
        (2, 8),
        (8, 0),
        (3, 9),
        (9, 4),
        (4, 10),
        (10, 5),
        (5, 11),
        (11, 3),
        (0, 12),
        (12, 3),
        (1, 13),
        (13, 4),
        (2, 14),
        (14, 5),
    )

    faces = (
        (0, 2, 1),
        (3, 4, 5),
        (0, 3, 5, 2),
        (2, 5, 4, 1),
        (1, 4, 3, 0),
    )

    @classmethod
    def volume(cls, cells, nodes):
        return P6.volume(cells, nodes)

    @classmethod
    def is_inside(cls, points):
        return P6.is_inside(points)


class P1(GenericCell, metaclass=Cell):
    ""

    vtk_id = 1
    order = 0

    shapes = (sympy.core.numbers.One(),)

    gauss_reduced = (
        (0,),
    )

    gauss = (
        (0,),
    )


class S2(GenericCell, metaclass=Cell):
    ""

    vtk_id = 3
    order = 1

    shapes = (
        0.5*(1-r),
        0.5*(1+r)
    )

    gauss_reduced = (
        (0, 2,),
    )

    gauss = (
        ( 0.577350269189626, 1.0),
        (-0.577350269189626, 1.0),
    )

    vertices = (
        (0, 1),
    )

