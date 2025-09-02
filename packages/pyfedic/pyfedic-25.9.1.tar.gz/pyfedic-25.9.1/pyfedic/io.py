#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from os import path
from numpy import linalg
import imageio.v3 as iio
import logging

from .cells import Cell, T4, T3
from .mesh import Mesh, CompositeMesh

types = {
    np.dtype('bool'): 'char',
    np.dtype('>u1'): 'unsigned_char',
    np.dtype('>i1'): 'char',
    np.dtype('>u2'): 'unsigned_short',
    np.dtype('>i2'): 'short',
    np.dtype('>u4'): 'unsigned_int',
    np.dtype('>i4'): 'int',
    np.dtype('>u8'): 'unsigned_long',
    np.dtype('>i8'): 'long',
    np.dtype('>f4'): 'float',
    np.dtype('>f8'): 'double'
}

r_types = dict(zip(types.values(),types.keys()))

def ctype_to_dtype(ctype):
    try:
        return r_types[ctype]
    except KeyError:
        for x, y in zip(types.values(),types.keys()):
            if ctype.startswith(x):
                return y
        raise KeyError

def imread(filename, dtype='f4', plugin=None):
    try:
        filename = str(filename)
        if iio.immeta(filename) in ['RGB', 'RGBA']:
            return iio.imread(filename, plugin=plugin)[...,:3].astype('f4').mean(axis=-1)
        return iio.imread(filename, plugin=plugin).astype('f4').squeeze()
    except:
        return imread(filename, dtype, 'pillow')

imwrite = iio.imwrite

def write_mesh(filename, mesh, cell_values=None, point_values=None, is_ascii=False, header='Writen by pyFEDIC'):
    #

    filename = str(filename)

    if cell_values is None:
        cell_values = {}
    if point_values is None:
        point_values = {}

    def big(a):
        return a.astype('>%s%d' %(a.dtype.kind, a.dtype.itemsize))

    if not filename.endswith('.vtk'):
        filename += '.vtk'

    fd = open(filename, 'w')
    fd.write('# vtk DataFile Version 2.0\n')
    fd.write(header[:256] + '\n')
    fd.write({True:'ASCII', False:'BINARY'}[is_ascii] + '\n')
    fd.write('DATASET UNSTRUCTURED_GRID\n')

    fd.write(f'POINTS {len(mesh.nodes)} float\n')
    if is_ascii:
        for p in mesh.nodes:
            fd.write(f'{" ".join(map(str, p))}\n')
    else:
        mesh.nodes.astype('>f4').tofile(fd)
        fd.write('\n')

    cell_types = []
    cell_nodes_count = 0
    for T, c in mesh.cells_by_type.items():
        cell_types.append(np.full(len(c), T.vtk_id))
        cell_nodes_count += len(c)*T.n_nodes
    cell_types = np.hstack(cell_types)

    fd.write(f'CELLS {mesh.Nc} {cell_nodes_count+mesh.Nc}\n')

    for T, c in mesh.cells_by_type.items():
        if is_ascii:
            for ci in c:
                fd.write(f'{T.n_nodes} {" ".join(map(str, ci))}\n')
        else:
            np.hstack((np.full((len(c), 1), T.n_nodes), c)).astype('>u4').tofile(fd)

    if not is_ascii:
        fd.write('\n')

    fd.write(f'CELL_TYPES {mesh.Nc}\n')

    if is_ascii:
        for ct in cell_types:
            fd.write(f'{ct}\n')
    else:
        cell_types.astype('>u4').tofile(fd)

    if not is_ascii:
        fd.write('\n')

    if len(point_values):
        fd.write(f'POINT_DATA {mesh.Nn}\n')
        for d in point_values:
            raw = big(point_values[d])
            if raw.ndim == 1:
                fd.write(f'SCALARS {d} {types[raw.dtype]} 1\n')
                fd.write('LOOKUP_TABLE default\n')
            elif raw.shape == (3, mesh.Nn):
                fd.write(f'COLOR_SCALARS {d} 3\n')
                raw = raw.T
            elif raw.shape == (mesh.Nn, 3):
                fd.write(f'VECTORS {d} {types[raw.dtype]}\n')
            elif raw.shape == (mesh.Nn, 9):
                fd.write(f'TENSORS {d} {types[raw.dtype]}\n')
            if is_ascii:
                for k, v in enumerate(raw.flat):
                    fd.write(f'{v} ')
                    if (k+1) % 10 == 0:
                        fd.write('\n')
            else:
                raw.tofile(fd)
            fd.write('\n')

    if len(cell_values):
        fd.write(f'CELL_DATA {mesh.Nc}\n')
        for d in cell_values:
            raw = big(cell_values[d])
            if raw.ndim == 1:
                fd.write(f'SCALARS {d} {types[raw.dtype]}\n')
                fd.write('LOOKUP_TABLE default\n')
            elif raw.ndim == 2 and raw.shape[1] == 3:
                fd.write(f'VECTORS {d} {types[raw.dtype]}\n')
            elif raw.ndim == 2 and raw.shape[1] == 9:
                fd.write(f'TENSORS {d} {types[raw.dtype]}\n')
            if is_ascii:
                for k, v in enumerate(raw.flat):
                    fd.write(f'{v} ')
                    if (k+1) % 10 == 0:
                        fd.write('\n')
            else:
                raw.tofile(fd)
            fd.write('\n')

    fd.close()

class FileFormatError(Exception):
    def __init__(self, why=None):
        if why is not None:
            why = ' (%s)' % why
        else:
            why = ''
        expression = 'Wrong file format%s.' % why
        Exception.__init__(self, expression)

def read_mesh(filename, return_data=True):
    """
    Read a ``.vtk`` or a ``.msh`` file as a :py:class:`pyFEDIC.mesh.Mesh` object.

    Parameters
    ----------
    filename : str
        path of the mesh file to read
    return_data : bool
        if True, read data link to the mesh if it exists

    Returns
    -------
    mesh : :class:`pyFEDIC.mesh.Mesh`
        mesh object
    point_data : dict or None
        data linked to each node, None if no data (only if return_data is True)
    cell_data : dict or None
        data linked to each cell, None if no data (only if return_data is True)


    """
    filename = str(filename)

    if filename.endswith('.msh'):
        m = MSHReader(filename).to_mesh()

        if return_data:
            return m, None, None
        else:
            return m

    if not filename.endswith('.vtk'):
        raise FileFormatError(filename)

    fd = open(filename, 'r', errors='replace')

    version = float(fd.readline().strip().split()[-1])
    header = fd.readline().strip()
    is_ascii = fd.readline().strip()=='ASCII'
    dataset = fd.readline().split()[-1]

    if version >= 5 and dataset != 'POLYDATA':
        import meshio
        fd.close()
        m = meshio.read(filename)
        cells_by_type = {Cell.by_vtk_id(meshio._vtk_common.meshio_to_vtk_type[k]):v.astype(int)
                         for k, v in m.cells_dict.items()}
        nodes = m.points.astype('f8')
        mesh = CompositeMesh.new(nodes, cells_by_type)

        if not return_data:
            return mesh

        pd = m.point_data

        cd = {}
        for k, v in m.cell_data.items():
            cd[k] = np.squeeze(np.concatenate(v))

        return mesh, pd, cd


    Nn = None
    Nc = None
    cells = []
    cell_types = []
    points = None
    point_data = {}
    cell_data = {}

    if dataset == 'UNSTRUCTURED_GRID':

        line = fd.readline()
        while not line.startswith('POINTS'):
            line = fd.readline()
            if len(line) == 0:
                raise Exception("VTK corrupted.")
        _, Nn, stype = line.split()

        Nn = int(Nn)
        dtype = ctype_to_dtype(stype)

        if is_ascii:
            points = np.fromfile(fd, sep=" ", count=Nn*3).reshape((Nn, 3))
        else:
            points = np.fromfile(fd, dtype=dtype, count=Nn*3).reshape((Nn, 3))

        line = fd.readline()
        while not line.startswith('CELLS'):
            line = fd.readline()
            if len(line) == 0:
                raise Exception("VTK corrupted.")
        _, Nc, Nv = line.split()

        Nc = int(Nc)
        Nv = int(Nv)

        if is_ascii:
            raw_cells = np.fromfile(fd, dtype=int, sep=" ", count=Nv)
        else:
            raw_cells = np.fromfile(fd, dtype='>u4', count=Nv).astype(int)

        c = 0
        while c < Nv:
            cells.append(raw_cells[c+1:c+1+raw_cells[c]])
            c += 1 + raw_cells[c]

        line = fd.readline()
        while not line.startswith('CELL_TYPES'):
            line = fd.readline()
            if len(line) == 0:
                raise Exception("VTK corrupted.")

        if is_ascii:
            cell_types = np.fromfile(fd, sep=" ", count=Nc).astype('i')
        else:
            cell_types = np.fromfile(fd, dtype='>u4', count=Nc).astype('i')

    elif dataset == 'POLYDATA':

        line = fd.readline()
        while not line.startswith('POINTS'):
            line = fd.readline()
            if len(line) == 0:
                raise Exception("VTK corrupted.")
        _, Nn, stype = line.split()

        Nn = int(Nn)
        dtype = ctype_to_dtype(stype)

        if is_ascii:
            points = np.fromfile(fd, sep=" ", count=Nn*3).reshape((Nn, 3))
        else:
            points = np.fromfile(fd, dtype=dtype, count=Nn*3).reshape((Nn, 3))

        line = fd.readline()
        while not line.startswith('POLYGONS'):
            line = fd.readline()
            if len(line) == 0:
                raise Exception("VTK corrupted.")
        _, Nc, Nv = line.split()

        Nc = int(Nc)
        Nv = int(Nv)

        if version < 5:
            if is_ascii:
                raw_cells = np.fromfile(fd, sep=" ", count=Nv)
            else:
                raw_cells = np.fromfile(fd, dtype='>u4', count=Nv)

            cells = -np.ones((Nc, 8), dtype='i8')
            cell_types = -np.ones(Nc, dtype='i8')
            ci = -1
            vi = 0
            vc = 0

            for v in raw_cells:
                if vi == vc:
                    vc = v
                    vi = 0
                    ci += 1
                    if vc == 3:
                        cell_types[ci] = 5
                    elif vc == 4:
                        cell_types[ci] = 9
                    else:
                        cell_types[ci] = 7
                else:
                    cells[ci,vi] = v
                    vi += 1
        else:
            line = fd.readline()
            if is_ascii:
                offsets = np.fromfile(fd, dtype=int, sep=" ", count=Nc)
            else:
                offsets = np.fromfile(fd, dtype='>i8', count=Nc)

            line = fd.readline()
            while not line.startswith('CONNECTIVITY'):
                line = fd.readline()
                if len(line) == 0:
                    raise Exception("VTK corrupted.")
            if is_ascii:
                raw_cells = np.fromfile(fd, dtype=int, sep=" ", count=Nv)
            else:
                raw_cells = np.fromfile(fd, dtype='>i8', count=Nv)

            for o1, o2 in zip(offsets[:-1], offsets[1:]):
                cell_types.append({3: 5, 4: 9}[o2-o1])
                cells.append(raw_cells[o1:o2])

    else:
        raise Exception("`%s` dataset is not supported yet." % dataset)

    nodes = points.astype('f8')

    cells_by_type = {
        Cell.by_vtk_id(x):np.vstack(
            [cell for vtk_id, cell in zip(cell_types, cells) if vtk_id == x]
        )
        for x in np.unique(cell_types)
    }

    mesh = CompositeMesh.new(nodes, cells_by_type)

    if not return_data:
        return mesh

    line = fd.readline()
    while True:
        if line.startswith('POINT_DATA'):
            point_data = read_mesh_data(fd, Nn, is_ascii)
        elif line.startswith('CELL_DATA'):
            cell_data = read_mesh_data(fd, Nc, is_ascii)
        elif len(line) == 0:
            break
        line = fd.readline()

    return mesh, point_data, cell_data

def read_mesh_data(fd, Nv, is_ascii):
    data = {}
    line = fd.readline()
    while True:
        if line.startswith('SCALARS'):
            _, key, stype = line.split()[:3]
            dtype = ctype_to_dtype(stype)
            line = fd.readline()
            if is_ascii:
                raw_data = np.fromfile(fd, sep=" ", count=Nv)
            else:
                raw_data = np.fromfile(fd, dtype=dtype, count=Nv)
            data[key] = raw_data
        elif line.startswith('VECTORS'):
            _, key, stype = line.split()
            dtype = ctype_to_dtype(stype)
            if is_ascii:
                raw_data = np.fromfile(fd, sep=" ", count=Nv*3)
            else:
                raw_data = np.fromfile(fd, dtype=dtype, count=Nv*3)
            data[key] = raw_data.reshape((Nv, 3))
        elif line.startswith('TENSORS'):
            _, key, stype = line.split()
            dtype = ctype_to_dtype(stype)
            if is_ascii:
                raw_data = np.fromfile(fd, sep=" ", count=Nv*9)
            else:
                raw_data = np.fromfile(fd, dtype=dtype, count=Nv*9)
            data[key] = raw_data.reshape((Nv, 9))
        ptr = fd.tell()
        line = fd.readline()
        if line.startswith('POINT_DATA') or line.startswith('CELL_DATA'):
            fd.seek(ptr)
            break
        elif len(line) == 0:
            break
    return data


class MSHError(Exception):
    def __init__(self, why=None):
        if why is not None:
            why = ' (%s)' % why
        else:
            why = ''
        expression = 'Wrong MSH file%s.' % why
        Exception.__init__(self, expression)

def parse(line, *types):
    if type(line) == str:
        values = line.split()
    elif type(line) == list:
        values = line
    if len(types) > 1:
        return [type_(v) for v, type_ in zip(values[:len(types)], types)] + values[len(types):]
    else:
        return [types[0](v) for v in values]

class MSHReader:
    """
    GMSH file format .msh reader.
    It handle only Point, Line, Triangle and Tetrahedron. But it handle PhysicalNames !
    """

    def to_mesh(self):
        node_ids = []
        coords = []
        i = 0
        for dim in self.Nodes:
            for s in self.Nodes[dim]:
                node_ids.append(self.Nodes[dim][s]['nodeTag'])
                coords.append(self.Nodes[dim][s]['coords'])
        node_ids = np.hstack(node_ids)
        coords = np.vstack(coords)

        sets = {}

        for k, v in self.PhysicalNames.items():
            if type(k) != str:
                continue
            sets[k] = []
            for e in v['entities']:
                sets[k].append(self.Entities[v['dimension']][e])

        cells = []
        cell_sets = {}
        cell_types = []
        i = 0
        vtk_id = {
            2: Cell.by_name['T3'].id,
            3: Cell.by_name['Q4'].id,
            4: Cell.by_name['T4'].id,
            15: Cell.by_name['P1'].id,
            1: Cell.by_name['S2'].id,
        }
        for sid, ss in sets.items():
            i0 = i
            for s in ss:
                c = s['nodeTag']
                nc = np.full((c.shape[0], 4), -1, dtype=int)
                nc[:,:c.shape[1]] = c
                cells.append(nc)
                cell_types.append(np.full(c.shape[0], vtk_id[s['elementType']], dtype=int))
                i += c.shape[0]
            cell_sets[sid] = np.arange(i0, i)
        cells = np.vstack(cells)
        cell_types = np.hstack(cell_types)
        m = Mesh(*coords.T, cells-1, cell_types)
        m.cell_sets = cell_sets
        return m

    def __init__(self, filename):

        fd = open(filename)

        line = fd.readline()

        if not line.startswith('$MeshFormat'):
            raise MSHError('$MeshFormat tag missing')

        self.version, self.file_type, self.data_type, *extra = parse(fd.readline(), str, int, int)

        if len(extra) == 1:
            self.endianness = int(extra[0])

        if not fd.readline().startswith('$EndMeshFormat'):
            raise MSHError('$EndMeshFormat tag missing')

        line = fd.readline()

        self.PhysicalNames = {}

        if line.startswith('$PhysicalNames'):

            numPhysicalNames, = parse(fd.readline(), int)

            for _ in range(numPhysicalNames):
                dimension, physicalTag, name = parse(fd.readline(), int, int, str)
                name = name[1:-1]
                dico = dict(
                    dimension = dimension,
                    physicalTag = physicalTag,
                    name = name,
                    entities = []
                )
                self.PhysicalNames[physicalTag] = dico
                self.PhysicalNames[name] = dico

            if not fd.readline().startswith('$EndPhysicalNames'):
                raise MSHError('$EndPhysicalNames tag missing')

            line = fd.readline()

        if line.startswith('$Entities'):

            numPoints, numCurves, numSurfaces, numVolumes = parse(fd.readline(), int)

            Points = {}
            for _ in range(numPoints):
                pointTag, X, Y, Z, numPhysicalTags, *extra = parse(fd.readline(), int, float, float, float, int)
                physicalTag = parse(extra, int)
                Points[pointTag] = dict(
                    pointTag = pointTag,
                    coords = np.array((X, Y, Z)),
                    numPhysicalTags = numPhysicalTags,
                    physicalTag = physicalTag
                )
                for k in physicalTag:
                    self.PhysicalNames[k]["entities"].append(pointTag)

            Curves = {}
            for _ in range(numCurves):
                curveTag, minX, minY, minZ, maxX, maxY, maxZ, numPhysicalTags, *extra = parse(fd.readline(), int, float, float, float, float, float, float, int)
                physicalTag = parse(extra[:numPhysicalTags], int)
                numBoundingPoints, *pointTag = parse(extra[numPhysicalTags:], int)
                Curves[curveTag] = dict(
                    curveTag = curveTag,
                    min = np.array((minX, minY, minZ)),
                    max = np.array((maxX, maxY, maxZ)),
                    numPhysicalTags = numPhysicalTags,
                    physicalTag = physicalTag,
                    numBoundingPoints = numBoundingPoints,
                    pointTag = pointTag,
                )
                for k in physicalTag:
                    self.PhysicalNames[k]["entities"].append(curveTag)

            Surfaces = {}
            for _ in range(numSurfaces):
                surfaceTag, minX, minY, minZ, maxX, maxY, maxZ, numPhysicalTags, *extra = parse(fd.readline(), int, float, float, float, float, float, float, int)
                physicalTag = parse(extra[:numPhysicalTags], int)
                numBoundingCurves, *curveTag = parse(extra[numPhysicalTags:], int)
                Surfaces[surfaceTag] = dict(
                    surfaceTag = surfaceTag,
                    min = np.array((minX, minY, minZ)),
                    max = np.array((maxX, maxY, maxZ)),
                    numPhysicalTags = numPhysicalTags,
                    physicalTag = physicalTag,
                    numBoundingCurves = numBoundingCurves,
                    curveTag = curveTag,
                )
                for k in physicalTag:
                    self.PhysicalNames[k]["entities"].append(surfaceTag)

            Volumes = {}
            for _ in range(numVolumes):
                volumeTag, minX, minY, minZ, maxX, maxY, maxZ, numPhysicalTags, *extra = parse(fd.readline(), int, float, float, float, float, float, float, int)
                physicalTag = parse(extra[:numPhysicalTags], int)
                numBoundngSurfaces, *surfaceTag = parse(extra[numPhysicalTags:], int)
                Volumes[volumeTag] = dict(
                    volumeTag = volumeTag,
                    min = np.array((minX, minY, minZ)),
                    max = np.array((maxX, maxY, maxZ)),
                    numPhysicalTags = numPhysicalTags,
                    physicalTag = physicalTag,
                    numBoundngSurfaces = numBoundngSurfaces,
                    surfaceTag = surfaceTag,
                )
                for k in physicalTag:
                    self.PhysicalNames[k]["entities"].append(volumeTag)

            self.Entities = dict(Points = Points, Curves = Curves, Surfaces = Surfaces, Volumes = Volumes)
            self.Entities.update({0: Points, 1: Curves, 2: Surfaces, 3: Volumes})

            if not fd.readline().startswith('$EndEntities'):
                raise MSHError('$EndEntities tag missing')

            line = fd.readline()

        if line.startswith('$PartitionedEntities'):

            logging.warning('$PartitionedEntities is not handled.')

            while True:
                line = fd.readline()
                if line.startswith('$EndPartitionedEntities'):
                    break
                if line == '':
                    raise MSHError('$EndPartitionedEntities tag missing')

            #if not fd.readline().startswith('$EndPartitionedEntities'):
                #raise MSHError('$EndPartitionedEntities tag missing')

            line = fd.readline()

        if not line.startswith('$Nodes'):
            raise MSHError('$Nodes tag missing')

        self.Nodes = {0: {}, 1: {}, 2: {}, 3: {}}

        if self.version == '2.2':
            numNodes, = parse(fd.readline(), int)
            entityDim = 3
            entityTag = 0
            parametric = 0
            numNodesInBlock = numNodes
            data = [parse(fd.readline(), int, float, float, float) for _ in range(numNodes)]
            nodeTag = np.array([x[0] for x in data])
            coords = np.array([x[1:] for x in data])
            self.Nodes[entityDim][entityTag] = dict(
                entityDim = entityDim,
                entityTag = entityTag,
                parametric = parametric,
                numNodesInBlock = numNodesInBlock,
                nodeTag = nodeTag,
                coords = coords,
            )

        elif self.version.startswith('4'):
            numEntityBlocks, numNodes, minNodeTag, maxNodeTag = parse(fd.readline(), int)
            for _ in range(numEntityBlocks):
                entityDim, entityTag, parametric, numNodesInBlock = parse(fd.readline(), int)
                if numNodesInBlock > 0:
                    nodeTag = np.hstack([int(fd.readline()) for _ in range(numNodesInBlock)])
                    coords = np.vstack([parse(fd.readline(), float) for _ in range(numNodesInBlock)])
                else:
                    nodeTag = np.array([], dtype=int)
                    coords = np.zeros((0,3))
                if entityTag in self.Nodes[entityDim]:
                    raise MSHError('ducplicate entityTag %d !' % entityTag)
                self.Nodes[entityDim][entityTag] = dict(
                    entityDim = entityDim,
                    entityTag = entityTag,
                    parametric = parametric,
                    numNodesInBlock = numNodesInBlock,
                    nodeTag = nodeTag,
                    coords = coords,
                )

        if not fd.readline().startswith('$EndNodes'):
            raise MSHError('$EndNodes tag missing')

        line = fd.readline()

        if not line.startswith('$Elements'):
            raise MSHError('$Elements tag missing')

        if self.version == '2.2':
            self.Elements = {}

            numElements, = parse(fd.readline(), int)

            for _ in range(numElements):
                elm_number, elm_type, number_of_tags, *extra = parse(fd.readline(), int, int, int)

                tags = np.unique([int(x) for x in extra[:number_of_tags]])
                nodeTag = [int(x) for x in extra[number_of_tags:]]

                for entityTag in tags:
                    if entityTag not in self.Elements:
                        self.Elements[entityTag] = dict(
                            entityTag = entityTag,
                            entityDim = 3,
                            elementType = elm_type,
                            numElementsInBlockn = 1,
                            elementTag = [elm_number],
                            nodeTag = [nodeTag]
                        )
                    else:
                        self.Elements[entityTag]['numElementsInBlockn'] += 1
                        self.Elements[entityTag]['elementTag'].append(elm_number)
                        self.Elements[entityTag]['nodeTag'].append(nodeTag)

            for x in self.Elements:
                self.Elements[x]['elementTag'] = np.array(self.Elements[x]['elementTag'])
                self.Elements[x]['nodeTag'] = np.array(self.Elements[x]['nodeTag'])

        elif self.version.startswith('4'):
            numEntityBlocks, numElements, minElementTag, maxElementTag = parse(fd.readline(), int)
            for _ in range(numEntityBlocks):
                entityDim, entityTag, elementType, numElementsInBlockn = parse(fd.readline(), int)
                idx = np.vstack([parse(fd.readline(), int) for _ in range(numElementsInBlockn)])
                self.Entities[entityDim][entityTag].update(dict(
                    elementType = elementType,
                    elementTag = idx[:,0],
                    nodeTag = idx[:,1:]
                ))

        if not fd.readline().startswith('$EndElements'):
            raise MSHError('$EndElements tag missing')

        line = fd.readline()

        if line.startswith('$Periodic'):

            logging.warning('$Periodic is not handled.')

            while True:
                line = fd.readline()
                if line.startswith('$EndPeriodic'):
                    break
                if line == '':
                    raise MSHError('$EndPeriodic tag missing')

            #if not fd.readline().startswith('$EndPeriodic'):
                #raise MSHError('$EndPeriodic tag missing')

            line = fd.readline()

        if line.startswith('$GhostElements'):

            logging.warning('$GhostElements is not handled.')

            while True:
                line = fd.readline()
                if line.startswith('$EndGhostElements'):
                    break
                if line == '':
                    raise MSHError('$EndGhostElements tag missing')

            #if not fd.readline().startswith('$EndGhostElements'):
                #raise MSHError('$EndGhostElements tag missing')

            line = fd.readline()

        if line.startswith('$Parametrizations'):

            logging.warning('$Parametrizations is not handled.')

            while True:
                line = fd.readline()
                if line.startswith('$EndParametrizations'):
                    break
                if line == '':
                    raise MSHError('$EndParametrizations tag missing')

            #if not fd.readline().startswith('$EndParametrizations'):
                #raise MSHError('$EndParametrizations tag missing')

            line = fd.readline()

        if line.startswith('$NodeData'):

            logging.warning('$NodeData is not handled.')

            while True:
                line = fd.readline()
                if line.startswith('$EndNodeData'):
                    break
                if line == '':
                    raise MSHError('$EndNodeData tag missing')

            #if not fd.readline().startswith('$EndNodeData'):
                #raise MSHError('$EndNodeData tag missing')

            line = fd.readline()

        if line.startswith('$ElementData'):

            logging.warning('$ElementData is not handled.')

            while True:
                line = fd.readline()
                if line.startswith('$EndElementData'):
                    break
                if line == '':
                    raise MSHError('$EndElementData tag missing')

            #if not fd.readline().startswith('$EndElementData'):
                #raise MSHError('$EndElementData tag missing')

            line = fd.readline()

        if line.startswith('$ElementNodeData'):

            logging.warning('$ElementNodeData is not handled.')

            while True:
                line = fd.readline()
                if line.startswith('$EndElementData'):
                    break
                if line == '':
                    raise MSHError('$EndElementData tag missing')

            #if not fd.readline().startswith('$EndElementData'):
                #raise MSHError('$EndElementData tag missing')

            line = fd.readline()

        if line.startswith('$InterpolationScheme'):

            logging.warning('$InterpolationScheme is not handled.')

            while True:
                line = fd.readline()
                if line.startswith('$EndInterpolationScheme'):
                    break
                if line == '':
                    raise MSHError('$EndInterpolationScheme tag missing')

            #if not fd.readline().startswith('$EndInterpolationScheme'):
                #raise MSHError('$EndInterpolationScheme tag missing')
