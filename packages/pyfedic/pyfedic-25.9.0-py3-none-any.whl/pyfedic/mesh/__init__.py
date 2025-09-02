# -*- coding: utf-8 -*-
"""

The :py:class:`pyFEDIC.mesh.Mesh` object is a key element for **pyFEDIC** but can also be used for other purposes like reading
and vritting ``.vtk`` file or do some finite element manipulation using the shape function to interpolate values.

You can build automatically a mesh using :py:meth:`pyFEDIC.mesh.gen_mesh` or load a mesh using :py:meth:`pyFEDIC.io.read_mesh`.

"""
import numpy as np

from .base_mesh import BaseMesh
from .composite_mesh import CompositeBaseMesh
from .regular_mesh import RegularBaseMesh
from .image_mesh import ImageMesh
from ..cells import Q4, C8, Q4Q, C8Q

class Mesh(BaseMesh, ImageMesh):
    """
    """

    def __init__(self, nodes, cells, cell_type, nodes_ids=None):
        BaseMesh.__init__(self, nodes, cells, cell_type, nodes_ids)
        ImageMesh.__init__(self)

class RegularMesh(RegularBaseMesh, ImageMesh):
    """
    """

    def __init__(self, xlims, ylims, zlims=None, elt_size=16, order=1):
        RegularBaseMesh.__init__(self, xlims, ylims, zlims, elt_size, order)
        ImageMesh.__init__(self)

class CompositeMesh(CompositeBaseMesh, ImageMesh):
    """
    """

    def __init__(self, nodes, cells_by_type, nodes_ids=None):
        CompositeBaseMesh.__init__(self, nodes, cells_by_type, nodes_ids)
        ImageMesh.__init__(self)

def gen_mesh(xlims, ylims, zlims=None, elt_size=16, adjust_to_roi=False, order=1):
    mesh = RegularMesh(xlims, ylims, zlims, elt_size, order)

    if adjust_to_roi:
        xmin, xmax = xlims
        _xmin, _xmax = mesh.nodes[:,0].min(), mesh.nodes[:,0].max()
        mesh.nodes[:,0] = (mesh.nodes[:,0] - _xmin) / (_xmax - _xmin) * (xmax - xmin) + xmin

        ymin, ymax = ylims
        _ymin, _ymax = mesh.nodes[:,1].min(), mesh.nodes[:,1].max()
        mesh.nodes[:,1] = (mesh.nodes[:,1] - _ymin) / (_ymax - _ymin) * (ymax - ymin) + ymin

        if zlims is not None:
            zmin, zmax = zlims
            _zmin, _zmax = mesh.nodes[:,2].min(), mesh.nodes[:,2].max()
            mesh.nodes[:,2] = (mesh.nodes[:,2] - _zmin) / (_zmax - _zmin) * (zmax - zmin) + zmin

        mesh = Mesh.new(mesh.nodes, mesh.cells_by_type)

    return mesh

__all__ = [
    'Mesh',
    'CompositeMesh',
    'RegularMesh',
    'gen_mesh'
]
