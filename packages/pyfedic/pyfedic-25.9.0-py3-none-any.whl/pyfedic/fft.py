#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import ndimage

from .tictoc import tictoc

@tictoc
def fft_cc(imref, imdef, refine=False, refine_factor=100, refine_order=3):
    if imref.ndim == 2:
        im = np.fft.fftshift(np.abs(np.fft.irfft2(
            np.fft.rfft2(imref)
            * np.conj(np.fft.rfft2(imdef)))))
        y0, x0 = [int(x) for x in np.where(im==im.max())]
        if refine:
            imz = ndimage.zoom(im[y0-1:y0+2,x0-1:x0+2], refine_factor, order=refine_order)
            y0z, x0z = [int(x) for x in np.where(imz==imz.max())]
            y0, x0 = y0 - 1.5 + y0z/refine_factor, x0 - 1.5 + x0z/refine_factor
        ux = imref.shape[1]//2 - x0
        uy = imref.shape[0]//2 - y0
        return ux, uy
    else:
        im = np.fft.fftshift(np.abs(np.fft.irfftn(
            np.fft.rfftn(imref)
            * np.conj(np.fft.rfftn(imdef)))))
        z0, y0, x0 = [int(x) for x in np.where(im==im.max())]
        if refine:
            imz = ndimage.zoom(im[z0-1:z0+2,y0-1:y0+2,x0-1:x0+2], refine_factor, order=refine_order)
            z0z, y0z, x0z = [int(x) for x in np.where(imz==imz.max())]
            z0, y0, x0 = z0 - 1.5 + z0z/refine_factor, y0 - 1.5 + y0z/refine_factor, x0 - 1.5 + x0z/refine_factor
        ux = imref.shape[2]//2 - x0
        uy = imref.shape[1]//2 - y0
        uz = imref.shape[0]//2 - z0
        return ux, uy, uz
