from pathlib import Path
from textwrap import dedent
import numpy as np
import imageio.v3 as iio
from . import __version__
from .mesh import Mesh
from .io import read_mesh

class ParamsEntry:
    def __init__(self, doc, kind, default=None):
        self.doc = dedent(doc)+"\n\ntype: %s\n\nDefault: %s" % (kind, default)
        self.kind = kind
        self.default = False if kind is bool and default is None else default


class ParamsBase(type):
    ""

    def __new__(cls, name, bases, classdict):
        result = type.__new__(cls, name, bases, classdict)

        result._defaults = {}

        for attr_name in dir(result):
            attr = getattr(result, attr_name)
            if isinstance(attr, ParamsEntry):
                result._defaults[attr_name] = attr.default
                setattr(result, attr_name, property(cls.mk_fget(attr_name), cls.mk_fset(attr_name), doc=attr.doc))

        def params(self, all=False):
            """
            return all params as a dictionnary if all is True, only thoses set otherwise.
            """
            if all:
                params = self._defaults.copy()
                params.update(self._currents)
                return params
            else:
                return self._currents

        result.params = params

        return result

    @classmethod
    def mk_fget(cls, name):
        def fget(self):
            return self._expanded.get(name, self._currents.get(name, self._defaults[name]))
        return fget

    @classmethod
    def mk_fset(cls, name):
        def fset(self, value):
            if name in self._expanded:
                self._expanded.pop(name)
            self._currents[name] = value
        return fset


class Params(metaclass=ParamsBase):
    ""

    images = ParamsEntry(
        '''
        List of of images to correlate. The first one is the reference. If a\
        string is provided, it is resolved using regular pattern and ascending\
        sort..
        ''',
        str | list | np.ndarray
    )

    result_path = ParamsEntry(
        'If given, writes result files (VTK for the mesh, TIF for the residual).',
        str
    )
    overwrite = ParamsEntry(
        'If False, ask for overwriting if the result_path is not empty.',
        bool,
    )
    output = ParamsEntry(
        '''
        If True, return the `mesh_out`, the displacement field `U` and the
        `residual`.
        ''',
        bool,
    )
    flip_y = ParamsEntry(
        '''
        If True and only with 2D images, flip the Y axis in the results to fit
        mechanical axis plot convention.
        ''',
        bool,
        True
    )
    write_step0 = ParamsEntry(
        '''
        If True, write the step 0 (empty field + zero residual) in the result path.
        ''',
        bool,
        True
    )

    xlims = ParamsEntry(
        'Boundaries of the mesh that needs to be build.',
        tuple[float] | np.ndarray
    )
    ylims = ParamsEntry(
        'Boundaries of the mesh that needs to be build.',
        tuple[float] | np.ndarray
    )
    zlims = ParamsEntry(
        'Boundaries of the mesh that needs to be build.',
        tuple[float] | np.ndarray
    )

    elt_size = ParamsEntry(
        'Edge size of one element of the mesh.',
        int,
        16
    )
    nscales = ParamsEntry(
        'Number of coarsening scales. 1 means no coarsening.',
        int,
        3
    )
    scales = ParamsEntry(
        'Coarsening level for each step, meaning image rescaling like 1/(2^scale).',
        tuple[int]
    )
    meshes = ParamsEntry(
        'Meshes for each step in the reference image coordinate system.',
        tuple[str]
    )

    sequential = ParamsEntry(
        'If True, the `step i+1` is initialized with the result of `step i`.',
        bool,
        True
    )
    euler = ParamsEntry(
        '''
        If True, the DIC is done between successive images and the cumulative
        displacement is reported on the final result.
        ''',
        bool,
    )
    euler_remesh = ParamsEntry(
        '''
        If True, a new regular mesh based on the cumulative
        displacement of ROI is build for the nth step.
        ''',
        bool,
    )

    reg_size = ParamsEntry(
        'Cut-off for the regularisation in pixels.',
        int,
    )

    reg_kind = ParamsEntry(
        '''
        kind of regularisation:

         * equilibrium gap
         * tikhonov
        ''',
        int,
        'equilibrium gap'
    )

    reg_ddl = ParamsEntry(
        '''
        Mask for all ddl (ddl_x, ddl_y, ddl_z) where True means is regularized.
        If None, then all is regularized. It can also be rules like:

         * unreg_xmin,
         * unreg_xmax,
         * ...
        ''',
        tuple[str] | np.ndarray,
    )
    nu = ParamsEntry(
        "Poisson's ratio used by the equilibrium gap regularisation.",
        float,
        0.3
    )

    median = ParamsEntry(
        '''
        Order of neightboors taken into account to calculate the median filter
        on the displacement field.
        ''',
        'int or tuple of int',
        0
    )

    mean = ParamsEntry(
        '''
        Order of neightboors taken into account to calculate the mean filter
        on the displacement field.
        ''',
        int | tuple[int],
        0
    )

    interp_order = ParamsEntry(
        '''
        Spline order for image interpolation. 1 is linear.
        ''',
        int,
        1
    )

    gradient_order = ParamsEntry(
        '''
        Spline order for image gradient. 1 is linear.
        Not available in 3D.
        ''',
        int,
        1
    )

    mesh_order = ParamsEntry(
        '''
        Mesh order for mesh generation. 1 for linear, 2 for quadratic.
        ''',
        int,
        1
    )

    init = ParamsEntry(
        'If given, initialize the first step with this first solution.',
        (Mesh, np.ndarray)
    )
    fft_init = ParamsEntry(
        'If True, initialize the first step with fft cross correlation.',
        bool,
    )
    fft_mode = ParamsEntry(
        'Mode used by the fft cross correlation.',
        '{{"roi", "full"}}',
        "roi"
    )
    restart = ParamsEntry(
        'If given, restart from the step `restart`.',
        int,
        0
    )
    rbm = ParamsEntry(
        '''
        If given, initialize the first step with this first solution as a rigid
        body motion (translations only).
        ''',
        np.ndarray,
    )

    itermax = ParamsEntry(
        'Max number of iteration for a scale of DIC.',
        int
    )
    normed_dU_min = ParamsEntry(
        'Convergence criterion on the normed dU.',
        float
    )
    diff_discr_min = ParamsEntry(
        'Convergence criterion on the variation of discrepancy.',
        float
    )

    adjust_to_roi = ParamsEntry(
        '''
        If True, fit the mesh on the boundaries, the element size will be
        adjusted and the algorithm won't take advantage of regular mesh
        optimizations.
        ''',
        bool,
    )

    mask = ParamsEntry(
        '''
        If given, the DIC will take only the pixel that match the mask. The mask
        can be:

         * "auto": it will use reference image and apply a threshold at 0,
         * str: path of the binary file for the mask,
         * array_like: boolean ndarray of reference shape.
        ''',
        str | np.ndarray
    )
    mask_threshold = ParamsEntry(
        '''
        fraction of mask pixels that must be in an element. 1 means an element
        have to be all included in the mask. 0.5 means at least half of the
        pixels of the element have to be in the mask.
        ''',
        float,
        0.5
    )

    norm_image = ParamsEntry(
        '''
        Strategy used for image normalisation:
         * "none": no normalisation,
         * "ref": use histogramm of the first image as reference
         * "each": considere images independently.
        Area used for image normalisation:
         * "all"
         * "roi"
         * "mask"
         * "roi+mask"''',
        '({{"none", "ref", "each"}}, {{"all", "roi", "mask", "roi+mask"}}',
        ("none", "all")
    )

    solver = ParamsEntry(
        '''auto, cgs, bicgstab, spsolve, lsqr''',
        str,
        'auto'
    )

    debug = ParamsEntry(
        'If True, outputs a result file for each steps of DIC (scales and iterations).',
        bool,
    )

    def __init__(self, wd=None, **params):
        self._currents = {}
        self._expanded = {}
        self.wd = Path(wd or '')
        for k, v in params.items():
            self.__setattr__(k, v)

    def save(self, path=None):
        """
        save all params as a python file ready for run_fedic.
        """
        if path is None:
            path = self.result_path / 'params.py'
        with path.open('w') as fd:
            fd.write(f'# pyFEDIC version : {__version__}\n')
            with np.printoptions(threshold=20):
                for param, default in self._defaults.items():
                    expanded = param in self._expanded
                    is_set = param in self._currents
                    if not is_set:
                        fd.write('# ')
                    fd.write(f'params.{param} = ')
                    if is_set:
                        value = self._currents[param]
                        if isinstance(value, str):
                            v = value.replace("'", "\'")
                            fd.write(f"'{v}' # default: ")
                        else:
                            fd.write(f'{repr(value)} # default: ')

                    if isinstance(default, str):
                        v = default.replace("'", "\'")
                        fd.write(f"'{v}'\n")
                    else:
                        fd.write(f'{repr(default)}\n')
                    if is_set and expanded:
                        fd.write(f'# after expanding -> {repr(self._expanded[param])}\n')

    def expand_params(self):
        #

        if isinstance(self.images, str | Path):
            if Path(self.images).is_absolute():
                p = Path(self.images)
                self._expanded['images'] = sorted(list(Path(p.anchor).glob(str(p.relative_to(p.anchor)))))
            else:
                self._expanded['images'] = sorted(list(self.wd.glob(self.images)))
        elif isinstance(self.images[0], str | Path):
            images = []
            for image in self.images:
                if Path(image).is_absolute():
                    images.append(Path(image))
                else:
                    images.append(self.wd / image)
            self._expanded['images'] = images

        if 'images' in self._expanded and len(self._expanded['images']) == 1:
            image = iio.imread(self._expanded['images'][0])
            self._expanded['images'] = [im for im in image]

        if self.result_path is not None:
            result_path = Path(self.result_path)
            if not result_path.is_absolute():
                result_path = self.wd / result_path
            self._expanded['result_path'] = result_path

        if self.scales is None:
            self._expanded['scales'] = list(range(self.nscales)[::-1])
        else:
            self._expanded['nscales'] = len(self.scales)

        if isinstance(self.meshes, str | Path):
            if Path(self.meshes).is_absolute():
                p = Path(self.meshes)
                self._expanded['meshes'] = sorted(list(Path(p.anchor).glob(str(p.relative_to(p.anchor)))))
            else:
                self._expanded['meshes'] = sorted(list(self.wd.glob(self.meshes)))
            if len(self._expanded['meshes']) == 1:
                self._expanded['meshes'] = self._expanded['meshes'] * self.nscales

        if self.meshes is not None and len(self.meshes) != self.nscales:
            self._expanded['nscales'] = len(self.meshes)
            self._expanded['scales'] = list(range(self.nscales)[::-1])

        if isinstance(self.mask, str | Path) and self.mask != 'auto':
            if Path(self.mask).is_absolute():
                self._expanded['mask'] = Path(self.mask)
            else:
                self._expanded['mask'] = self.wd / self.mask

        if isinstance(self.images[0], np.ndarray):
            shape = self.images[0].shape
        else:
            try:
                shape = iio.improps(self.images[0]).shape
            except KeyError:
                shape = iio.improps(self.images[0], plugin='pillow').shape
            meta = iio.immeta(self.images[0])
            if meta.get('is_imagej', False) and meta.get('slices', 1) > 1:
                shape = meta.get('slices', 1), *shape
            elif meta.get('is_shaped', False):
                shape = meta['shape']


        ndim = len(shape)
        max_lims = shape[::-1]

        if self.solver == 'auto':
            if ndim == 2:
                self._currents['solver'] = 'spsolve'
            else:
                self._currents['solver'] = 'cgs'

        for max_lim, lims in zip(max_lims, ('xlims', 'ylims', 'zlims')):
            if getattr(self, lims) is None:
                self._expanded[lims] = 0, max_lim-1
            else:
                min_, max_ = getattr(self, lims)
                min_ = max(min_, 0)
                if max_ < 0:
                    max_ = max_lim + max_
                else:
                    max_ = min(max_, max_lim - 1)
                if max_ < min_:
                    raise Exception(f'params.{lims} is not well set : max ({max_}) < min ({min_})')
                self._expanded[lims] = min_, max_

        # TODO: que faire si non séquentiel et unique init
        if self.init is not None:
            if isinstance(self.init, str):
                if '*' in self.init:
                    self.init = sorted(list(self.wd.glob(self.init)))
                    if len(self.init) == len(self.images):
                        self.init = self.init[1:]
                    self.sequential = False
                else:
                    m, pd, _ = read_mesh(self.wd / self.init)
                    self.init = m, pd['U']
            elif isinstance(self.init[0], str):
                self.init = [self.wd / init for init in self.init]

        for param in [
            'median', 'mean', 'reg_size', 'elt_size', 'solver',
            'itermax', 'diff_discr_min', 'normed_dU_min', 'mesh_order',
            'solver', 'reg_kind', 'meshes', 'interp_order', 'gradient_order'
        ]:
            if isinstance(getattr(self, param), list | tuple | np.ndarray):
                continue
            self._expanded[param] = [getattr(self, param)] * self.nscales

        meshes = []
        for i, mesh in enumerate(self.meshes):
            if isinstance(mesh, str | Path):
                if Path(mesh).is_absolute():
                    mesh = Path(mesh)
                else:
                    mesh = self.wd / mesh
            meshes.append(mesh)
        self._expanded['meshes'] = meshes
