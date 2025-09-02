#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from shutil import copyfile
from pathlib import Path

from .mesh import gen_mesh, BaseMesh, CompositeMesh
from .io import read_mesh, imwrite, imread
from .tictoc import tictoc, summary, TICTOC
from .dic import DIC
from .fft import fft_cc
from .image import binning
from .params import Params

import logging
from logging import FileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s :: %(message)s"
)

def run_DIC(images, debug_level=0, **params):
    """
    DIC function that handles most cases.

    Compute the DIC for all deformed images compared to the reference.

    Parameters
    ----------
    images
        see Params.images
    params: Params
        see Params

    Returns
    -------
    mesh_out: Mesh
        Mesh used by the DIC for all steps at full scale.
        Only provided if `output` is True.
    U: list of (array_like)
        Displacement field for each step. Only provided if `output` is True.
    residual: list of (array_like)
        Residual for each step. Only provided if `output` is True.

    """

    if debug_level > 0:
        logging.getLogger().setLevel(TICTOC)

    if isinstance(images, Params):
        params = images
        images = params.images
    else:
        params = Params(**params)
        params.images = images

    params.expand_params()

    if params.euler == True:
        return _run_DIC_euler(params)

    reference = params.images[0]
    file_handler = None

    if params.result_path is not None:
        result_path = params.result_path

        try:
            result_path.mkdir(parents=True, exist_ok=True)
        except NotADirectoryError:
            raise Exception(f"part of `{result_path}` exists and is not a directory")

        (result_path / 'fields').mkdir(exist_ok=True)
        (result_path / 'residuals').mkdir(exist_ok=True)

        if not params.overwrite:
            if len(list((result_path / 'fields').glob('*.vtk')) + list((result_path / 'residuals').glob('*.tif'))) > 0:
                if input(f"`{result_path}` is not empty. Don't care ? [oN] ").lower() != 'o':
                    raise Exception("Abort....")

        if params.debug:
            (result_path / 'debug').mkdir(exist_ok=True)

        file_handler = FileHandler(result_path / 'dic.log', 'a' if params.restart else 'w')
        file_handler.setFormatter(logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s"))
        file_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(file_handler)

    if params.output:
        result_U = []
        result_residual = []






    if isinstance(reference, Path):
        imrefs = [imread(reference)]
    else:
        imrefs = [reference]

    if isinstance(params.mask, np.ndarray) or params.mask is None:
        masks = [params.mask]
    elif params.mask == 'auto':
        masks = [imrefs[0] > 0]
    else:
        masks = [imread(params.mask) > 0]

    for s in range(max(params.scales)):
        imrefs.append(binning(imrefs[-1]))
        if params.mask is not None:
            masks.append(binning(masks[-1].astype(int)) >= 0.5)
        else:
            masks.append(None)


    imref = imrefs[0]

    if np.max(np.array(imref.shape) / 2**max(params.scales) % 1) > 0:
        logging.warning('WARNING: image shape %s is not multiple of 2^(max_scale) (2^%d = %d) !' % (imref.shape, max(params.scales), 2**max(params.scales)))

    if imref.ndim == 3:
        lims = np.vstack((params.xlims, params.ylims, params.zlims)).astype(float)
    else:
        lims = np.vstack((params.xlims, params.ylims)).astype(float)




    dic = []

    for si, s in enumerate(params.scales):
        mesh = params.meshes[si]
        if mesh is None:
            mesh = gen_mesh(*(lims/2**s), elt_size=params.elt_size[si], adjust_to_roi=params.adjust_to_roi, order=params.mesh_order[si])
        elif isinstance(mesh, Path):
            mesh = read_mesh(mesh, False)
            if isinstance(mesh, CompositeMesh):
                if imref.ndim == 3:
                    mesh = mesh.copy_as_3d()
                else:
                    mesh = mesh.copy_as_2d()
            mesh = mesh.scale(1/(2**s))
        elif isinstance(mesh, BaseMesh):
            mesh = mesh.scale(1/(2**s))
        dic.append(DIC(imrefs[s], mesh))
        if params.result_path is not None and params.debug:
            dic[si].debug_path = result_path / "debug" / f"im01_i{si:02d}_s{s:02d}"
            dic[si].scale = s
        dic[si].set_interp_order(params.interp_order[si])
        dic[si].compute_gradient(params.gradient_order[si])
        dic[si].set_convergence_params(params.itermax[si], params.normed_dU_min[si], params.diff_discr_min[si])
        dic[si].set_solver(params.solver[si])
        if params.reg_size[si] != None:
            if params.reg_ddl is not None:
                if type(params.reg_ddl[0]) == str:
                    unreg_ddl = np.zeros(mesh.Nn, dtype=bool)
                    if 'unreg_xmin' in params.reg_ddl:
                        unreg_ddl |= mesh.nodes[:,0] == mesh.nodes[:,0].min()
                    if 'unreg_xmax' in params.reg_ddl:
                        unreg_ddl |= mesh.nodes[:,0] == mesh.nodes[:,0].max()
                    if 'unreg_ymin' in params.reg_ddl:
                        unreg_ddl |= mesh.nodes[:,1] == mesh.nodes[:,1].min()
                    if 'unreg_ymax' in params.reg_ddl:
                        unreg_ddl |= mesh.nodes[:,1] == mesh.nodes[:,1].max()
                    if 'unreg_zmin' in params.reg_ddl:
                        unreg_ddl |= mesh.nodes[:,2] == mesh.nodes[:,2].min()
                    if 'unreg_zmax' in params.reg_ddl:
                        unreg_ddl |= mesh.nodes[:,2] == mesh.nodes[:,2].max()
                else:
                    raise Exception("TODO") # TODO
                reg_ddl = ~unreg_ddl
            else:
                reg_ddl = None
        if params.median[si] > 0:
            dic[si].set_median(params.median[si])
        if params.mean[si] > 0:
            dic[si].set_mean(params.mean[si])
        if masks[s] is not None:
            dic[si].set_mask(masks[s], params.mask_threshold)
        if params.reg_size[si] != None:
            dic[si].set_regularisation(params.reg_size[si], params.reg_kind[si], params.nu, reg_ddl)
        strategy, area = params.norm_image
        dic[si].set_normim_params(strategy=strategy, use_mesh="roi" in area, use_mask="mask" in area)

    if params.result_path is not None:
        params.save(result_path / 'params.py')

    if params.sequential:
        if params.restart > 0:
            mesh_init, point_data, cell_data = read_mesh(result_path / 'fields' / f'dic{params.restart:05d}.vtk')
            mesh_init, U_init = mesh_init, point_data['U'][:,:mesh_init.ndim]
            if params.flip_y and dic[-1].mesh.ndim == 2:
                U_init[1] *= -1
                mesh_init.nodes[:,1] *= -1
                mesh_init.nodes[:,1] += dic[-1].imref.shape[0]
        elif params.init is not None:
            mesh_init, U_init = params.init

    if params.result_path is not None:
        cell_values = {}
        if params.mask is not None:
            cell_values['mask'] = dic[-1].mask_cell.astype('u1')

        if params.flip_y and dic[-1].mesh.ndim == 2:
            mesh_out = dic[-1].mesh.copy()
            mesh_out.nodes[:,1] *= -1
            mesh_out.nodes[:,1] += dic[-1].imref.shape[0]
        else:
            mesh_out = dic[-1].mesh
        if params.write_step0:
            mesh_out.save(result_path / 'fields' / f'dic{0:05d}.vtk', np.zeros((mesh_out.Nn,3)), compute_eps=True, cell_values=cell_values)
            imwrite(result_path / 'residuals' / f'res{0:05d}.tif', np.zeros(imref.shape, dtype='u1'))

    nsteps = len(params.images) - 1

    for i in range(params.restart, nsteps):
        if nsteps > 1:
            logging.info("=== image %d / %d ===" % (i+1, nsteps))
        if isinstance(params.images[i+1], Path):
            imdef = [imread(params.images[i+1])]
        else:
            imdef = [params.images[i+1]]
        for s in range(max(params.scales)):
            imdef.append(binning(imdef[-1]))
        for si, s in enumerate(params.scales):
            logging.info("=== scale %d / %d ===" % (si+1, params.nscales))
            if params.result_path is not None and params.debug:
                dic[si].debug_path = result_path / "debug" / f"im{i+1:02d}_i{si:02d}_s{s:02d}"
            if si == 0:
                if i == 0 and params.init is not None and isinstance(params.init[0], BaseMesh):
                    dic[si].set_init(U_init, mesh_init, 1/2**s)
                elif params.sequential and i > 0:
                    if i == params.restart:
                        dic[si].set_init(U_init, mesh_init, 1/2**s)
                    else:
                        if params.mask is not None:
                            dic[si].set_init(U, dic[-1].mesh, 1/2**s, mask=dic[-1].mask_node)
                        else:
                            dic[si].set_init(U, dic[-1].mesh, 1/2**s)
                elif params.fft_init and params.rbm is None:
                    #TODO: fix This !
                    try:
                        if params.fft_mode == 'roi':
                            u_fft = fft_cc(imref[dic[-1].mesh.roi.slices], imdef[0][dic[-1].mesh.roi.slices])
                        else:
                            u_fft = fft_cc(imref, imdef[0])
                    except:
                        logging.warning("Failed to find one maximum with FFT cross correlation (or sommething else appears...)")
                        if imref.ndim == 2:
                            u_fft = (0, 0)
                        else:
                            u_fft = (0, 0, 0)
                    logging.info("fft: %s" % repr(u_fft))
                    U = np.zeros((dic[si].mesh.Nn, imref.ndim)) + np.array(u_fft)[None, :]/2**s
                    dic[si].set_init(U)
                elif params.fft_init:
                    if params.fft_mode == 'roi':
                        slices = [slc.indices(dim) for dim, slc in zip(imref.shape, dic[-1].mesh.roi.slices)]
                    else:
                        slices = [slice(None).indices(dim) for dim in imref.shape]
                    slices = [slice(slc[0]+int(t),slc[1]+int(t)) for slc, t in zip(slices, params.rbm[::-1])]
                    u_fft = fft_cc(imref[dic[-1].mesh.roi.slices], imdef[0][slices])
                    logging.info("fft: %s" % repr(u_fft))
                    uuu = tuple(np.array(params.rbm)+np.array(u_fft))
                    logging.info("fft+rbm: %s" % repr(uuu))
                    U = np.zeros((dic[si].mesh.Nn, imref.ndim)) + np.array(uuu)[None, :]/2**s
                    dic[si].set_init(U)
                elif params.rbm is not None:
                    U = np.zeros((dic[si].mesh.Nn, imref.ndim)) + np.array(params.rbm)[None, :]/2**s
                    dic[si].set_init(U)
                elif not params.sequential and params.init is not None:
                    if isinstance(params.init[i], Path):
                        m, pd, _ = read_mesh(params.init[i])
                        mesh_init, U_init = m, pd['U']
                    else:
                        mesh_init, U_init = params.init[i]
                    dic[si].set_init(U_init, mesh_init, 1/2**s)
                else:
                    # We have to reset the displacement field as it is stored in the DIC object
                    dic[si].set_init(None)

            else:
                if params.mask is not None:
                    dic[si].set_init(U, dic[si-1].mesh, 2**(params.scales[si-1]-s), mask=dic[si-1].mask_node[:dic[si-1].mesh.Nn])
                else:
                    dic[si].set_init(U, dic[si-1].mesh, 2**(params.scales[si-1]-s))

            if hasattr(params, '_prompt'):
                prompt = params._prompt
            else:
                prompt = '['
            if nsteps > 1:
                N1 = f'{int(np.log10(nsteps))+1}d'
                N2 = f'{int(np.log10(params.nscales))+1}d'
                prompt += f'{i+1:{N1}}/{nsteps:{N1}}|{si+1:{N2}}/{params.nscales:{N2}}]'
            else:
                N2 = f'{int(np.log10(params.nscales))+1}d'
                prompt += f'{si+1:{N2}}/{params.nscales:{N2}}]'

            U = dic[si].compute(imdef[s], prompt=prompt)

        if s != 0:

            mesh_s0 = dic[-1].mesh.scale(2**s)
            U *= 2**s

        else:
            mesh_s0 = dic[-1].mesh



        res = abs(imref-mesh_s0.interp(imdef[0], U))/(imref.max()-imref.min())
        if params.mask is not None:
            res[~masks[0]] = 0
        if params.result_path is not None:
            cell_values = {}
            if params.mask is not None:
                norm = mesh_s0.pixsum_by_cells(masks[0])
                cell_values['residual'] = np.full(mesh_s0.Nc, np.nan)
                cell_values['residual'][norm>0] = mesh_s0.pixsum_by_cells(res)[norm>0]/norm[norm>0]*100
            else:
                if mesh_s0.ndim == 2:
                    cell_values['residual'] = mesh_s0.pixsum_by_cells(res)/mesh_s0.surf()*100
                else:
                    cell_values['residual'] = mesh_s0.pixsum_by_cells(res)/mesh_s0.vol()*100
            if params.mask is not None:
                cell_values['mask'] = dic[-1].mask_cell.astype('u1')

            if params.flip_y and mesh_s0.ndim == 2:
                mesh_out = mesh_s0.copy()
                mesh_out.nodes[:,1] *= -1
                mesh_out.nodes[:,1] += dic[-1].imref.shape[0]
                U_out = np.hstack((U[:,[0]], -U[:,[1]]))
            else:
                mesh_out = mesh_s0
                U_out = U
            point_values = {}
            if params.reg_size[-1] != None and reg_ddl is not None:
                point_values['reg_ddl'] = reg_ddl
            mesh_out.save(result_path / 'fields' / f'dic{i+1:05d}.vtk',
                          U_out, compute_eps=True, cell_values=cell_values, point_values=point_values)
            imwrite(result_path / 'residuals' / f'res{i+1:05d}.tif', np.nan_to_num(res*100, copy=False).astype('u1'))

        if params.output:
            result_U.append(U)
            result_residual.append(res)

    if params.debug:
        summary()

    if file_handler is not None:
        logging.getLogger().removeHandler(file_handler)

    logging.info("Done with success !")

    if params.output:
        return dic[-1].mesh, result_U, result_residual

def _run_DIC_euler(images, **params_euler):
    """

    """

    if type(images) == Params:
        params_euler = images
        images = params_euler.images
    else:
        params_euler = Params(**params_euler)
        params_euler.images = images

    params_euler.expand_params()

    if isinstance(params_euler.images[0], Path):
        imref = imread(params_euler.images[0])
    else:
        imref = params_euler.images[0]
    if type(params_euler.mask) == str and params_euler.mask == 'auto':
        mask = imref > 0
    elif isinstance(params_euler.mask, (str, Path)):
        mask = imread(params_euler.mask) > 0
    else:
        mask = params_euler.mask

    result_path = params_euler.result_path

    try:
        result_path.mkdir(parents=True, exist_ok=True)
    except NotADirectoryError:
        raise Exception("part of `%s` exists and is not a directory" % result_path)

    (result_path / 'fields').mkdir(exist_ok=True)
    (result_path / 'residuals').mkdir(exist_ok=True)

    if not params_euler.overwrite:
        if len(
            list((result_path / 'fields').glob('*.vtk')) +
            list((result_path / 'residuals').glob('*.tif')) +
            list((result_path / 'fields').glob('step*'))
        ) > 0:
            if input("`%s` is not empty. Don't care ? [oN] " % result_path).lower() != 'o':
                raise Exception("Abort....")

    params_euler.save(result_path / 'params.py')

    file_handler = FileHandler(result_path / 'dic.log', 'a' if params_euler.restart else 'w')
    file_handler.setFormatter(logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s"))
    file_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(file_handler)

    params = Params(**params_euler.params())
    if mask is not None:
        params.mask = mask
        if params.zlims is None and mask.ndim == 3:
            params.zlims = np.where(mask.max(axis=-1).max(axis=-1))[0][[0,-1]] + [-params.elt_size*(1-params.mask_threshold),params.elt_size*(1-params.mask_threshold)]
        if params.ylims is None and mask.ndim == 3:
            params.ylims = np.where(mask.max(axis=0).max(axis=-1))[0][[0,-1]] + [-params.elt_size*(1-params.mask_threshold),params.elt_size*(1-params.mask_threshold)]
        elif params.ylims is None:
            params.ylims = np.where(mask.max(axis=-1))[0][[0,-1]] + [-params.elt_size*(1-params.mask_threshold),params.elt_size*(1-params.mask_threshold)]
        if params.xlims is None and mask.ndim == 3:
            params.xlims = np.where(mask.max(axis=0).max(axis=0))[0][[0,-1]] + [-params.elt_size*(1-params.mask_threshold),params.elt_size*(1-params.mask_threshold)]
        elif params.xlims is None:
            params.xlims = np.where(mask.max(axis=0))[0][[0,-1]] + [-params.elt_size*(1-params.mask_threshold),params.elt_size*(1-params.mask_threshold)]
    params.euler = False
    params.output = True
    params.restart = 0
    params.result_path = result_path / f"step_{0:04d}_{1:04d}"
    params.overwrite = True
    params.images = params_euler.images[0:2]

    nsteps = len(params_euler.images) - 1

    N1 = int(np.log10(nsteps))+1
    prompt = "[%"+str(N1)+"d/%"+str(N1)+"d|"
    params._prompt = prompt % (1, nsteps)

    if params_euler.restart == 0:

        logging.info("=== image %d / %d ===" % (1, nsteps))
        mesh_step0, U, residual = run_DIC(params)

        copyfile(
            params.result_path / 'fields' / f'dic{0:05d}.vtk',
            result_path / 'fields' / f'dic{0:05d}.vtk'
        )
        copyfile(
            params.result_path / 'fields' /  f'dic{1:05d}.vtk',
            result_path / 'fields' / f'dic{1:05d}.vtk'
        )
        copyfile(
            params.result_path / 'residuals' / f'res{0:05d}.tif',
            result_path / 'residuals' / f'res{0:05d}.tif'
        )
        copyfile(
            params.result_path / 'residuals' / f'res{1:05d}.tif',
            result_path / 'residuals' / f'res{1:05d}.tif'
        )

    mesh_step0, pd, cd = read_mesh(result_path / f'step_{0:04d}_{1:04d}' / 'fields' /  f'dic{1:05d}.vtk')
    Ucum = mesh_step0.extrap_V(pd['U'])

    if mask is not None:
        mask_cell_0 = cd['mask']

    if params.flip_y and mesh_step0.ndim == 2:
        mesh_step0_out = mesh_step0.copy()
        mesh_step0_out.nodes[:,1] *= -1
        mesh_step0_out.nodes[:,1] += imref.shape[0]
    else:
        mesh_step0_out = mesh_step0

    if not params_euler.euler_remesh:
        if imref.ndim == 3:
            lims = np.vstack((params.xlims, params.ylims, params.zlims)).astype(float)
        else:
            lims = np.vstack((params.xlims, params.ylims)).astype(float)

        for si, s in enumerate(params_euler.scales):
            if params_euler.meshes[si] is None:
                mesh_s = gen_mesh(*(lims/2**s), elt_size=params_euler.elt_size[si], adjust_to_roi=params_euler.adjust_to_roi, order=params_euler.mesh_order[si])
                mesh_s.nodes *= 2**s
                params_euler.meshes[si] = mesh_s

    params.write_step0 = False

    for i in range(1, nsteps):
        if i >= params_euler.restart:
            logging.info("=== image %d / %d ===" % (i+1, nsteps))

            if mask is not None:
                params.mask = mesh_step0.interp(mask.astype('f4'), -Ucum, out=0) >= 0.5

        mesh_init = mesh_step0.warp(Ucum)

        if i >= params_euler.restart:
            params.images = params_euler.images[i:i+2]

            if params_euler.euler_remesh:
                params.xlims = (mesh_init.xn.min(), mesh_init.xn.max())
                params.ylims = (mesh_init.yn.min(), mesh_init.yn.max())
                params.zlims = (mesh_init.zn.min(), mesh_init.zn.max())
            else:
                params.xlims = None
                params.ylims = None
                params.zlims = None
                params.meshes = [None] * params_euler.nscales
                for si, s in enumerate(params_euler.scales):
                    if isinstance(params_euler.meshes[si], (str, Path)):
                        params_euler.meshes = tuple([read_mesh(fff, False) for fff in params_euler.meshes])
                    Ucum_s = mesh_step0.interp_V(Ucum, params_euler.meshes[si], out='mean')

                    #TODO This in not OK : we cannot cumulate if the nodes are moving
                    #if mesh_step0.ndim == 2:
                        #from .fem import FEM
                        #fem = FEM(params_euler.meshes[si], 1)

                        #fem.bcs = [
                            #(params_euler.meshes[si].outline(), Ucum_s[:,params_euler.meshes[si].outline()])
                        #]

                        #Uf = fem.solve()

                        #params.meshes[si] = params_euler.meshes[si].warp(Uf)

                    #else:
                        #params.meshes[si] = params_euler.meshes[si].warp(Ucum_s)

                    params.meshes[si] = params_euler.meshes[si].warp(Ucum_s)

            params.result_path = result_path / f"step_{i:04d}_{i+1:04d}"

            params.rbm = None

            params._prompt = prompt % (i+1, nsteps)

            mesh_out, (U, ), _ = run_DIC(params)
        else:
            mesh_out, pd, _ = read_mesh(result_path / f'step_{i:04d}_{i+1:04d}' / 'fields' / f'dic{1:05d}.vtk')
            U = pd['U']

        U = mesh_out.extrap_V(U)

        if params_euler.euler_remesh:
            Ucum += mesh_init.interp_V(U, mesh_out)
        else:
            Ucum[:,:U.shape[1]] += U

        if i >= params_euler.restart:

            cell_values = {}
            if mask is not None:
                cell_values['mask'] = mask_cell_0

            if isinstance(params.images[1], (str, Path)):
                imdef = imread(params.images[1])
            else:
                imdef = params.images[1]

            res = abs(imref-mesh_step0.interp(imdef, Ucum))/(imref.max()-imref.min())
            if mask is not None:
                res[~params.mask] = 0

            if mask is not None:
                norm = mesh_step0.pixsum_by_cells(mask)
                cell_values['residual'] = np.full(mesh_step0.Nc, np.nan)
                cell_values['residual'][norm>0] = mesh_step0.pixsum_by_cells(res)[norm>0]/norm[norm>0]*100
            else:
                if mesh_step0.ndim == 2:
                    cell_values['residual'] = mesh_step0.pixsum_by_cells(res)/mesh_step0.surf()*100
                else:
                    cell_values['residual'] = mesh_step0.pixsum_by_cells(res)/mesh_step0.vol()*100

            if params.flip_y and mesh_out.ndim == 2:
                mesh_step0_out.save(result_path / "fields" / f'dic{i+1:05d}.vtk',
                                    np.vstack((Ucum[0], -Ucum[1])), compute_eps=True, cell_values=cell_values)
            else:
                mesh_step0_out.save(result_path / "fields" / f'dic{i+1:05d}.vtk',
                                    Ucum, compute_eps=True, cell_values=cell_values)

            imwrite(result_path / 'residuals' / f'res{i+1:05d}.tif', (res*100).astype('u1'))

def run_fedic(params_file=None, debug_level=0):
    """
    Function used for standalone `run_fedic` console command.
    """

    from sys import exit

    if params_file is None:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("PARAMS_FILE", help="path to params file", type=str)
        parser.add_argument('-v', '--verbose', action='count', default=debug_level)

        args = parser.parse_args()

        params_file = args.PARAMS_FILE
        debug_level = args.verbose

    params_file = Path(params_file)

    if not params_file.is_file():
        print('no valid param file to process')
        exit(1)

    params = Params()

    exec(open(params_file).read(), dict(params=params))

    if 'result_path' not in params.params():
        params.result_path = params_file.with_name('output_' + params_file.stem)

    run_DIC(params, debug_level)


