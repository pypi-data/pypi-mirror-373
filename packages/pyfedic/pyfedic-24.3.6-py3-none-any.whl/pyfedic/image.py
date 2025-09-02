#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

def binning(im_input):
    """
    Compute the pixel aggregation 2 by 2 in all direction.

    Parameters
    ----------
    im_input: array_like
        image to aggregate.

    Returns
    -------
    im_output: array_like
        aggregated image.

    Note
    ----
    All odd dimensions of the original are truncated to compute the aggregated
    image.

    """
    if im_input.ndim == 2:
        ny, nx = im_input.shape
        nx -= nx % 2
        ny -= ny % 2
        return (im_input[:ny:2,:nx:2] + im_input[1:ny:2,:nx:2] + im_input[:ny:2,1:nx:2] + im_input[1:ny:2,1:nx:2])/4
    elif im_input.ndim == 3:
        nz, ny, nx = im_input.shape
        nx -= nx % 2
        ny -= ny % 2
        nz -= nz % 2
        return (im_input[:nz:2,:ny:2,:nx:2] + im_input[:nz:2,1:ny:2,:nx:2] +
                im_input[:nz:2,:ny:2,1:nx:2] + im_input[:nz:2,1:ny:2,1:nx:2] +
                im_input[1:nz:2,:ny:2,:nx:2] + im_input[1:nz:2,1:ny:2,:nx:2] +
                im_input[1:nz:2,:ny:2,1:nx:2] + im_input[1:nz:2,1:ny:2,1:nx:2])/8

#def normim(im):
    #sel = ~np.isnan(im)
    #return ((im-im[sel].mean())/im[sel].std()+10).astype('f4')

def enhance_contrast(im_input, mask=None, saturation=0.35, cast_to=float):
    """
    Enhance contrast of the image by saturation of percentiles.

    Parameters
    ----------
    im_input: array_like
        image to enhance.
    mask: None or array_like
        pixels to use for computation of the percentiles
    saturation: float or tuple of float
        percentiles to saturate. If a float is provided, saturation is
        symmetric. For asymmetric saturation, provide a tuple with two floats.
    cast_to: str or type or np.dtype
        dtype to use for the result after saturation.

    Returns
    -------
    im_output: array_like
        enhanced image.

    """
    if mask is None:
        mask = ~np.isnan(im_input)
    if type(saturation) != tuple:
        saturation = float(saturation), 100 - float(saturation)
    else:
        saturation = float(saturation[0]), 100 - float(saturation[1])
    rmin, rmax = np.percentile(im_input[mask], saturation)
    im_output = (im_input - rmin)/(rmax - rmin)
    im_output[~mask] = 0
    im_output[im_output<0] = 0
    im_output[im_output>1] = 1
    dtype = np.iinfo(cast_to)
    if dtype.kind in ['u', 'i']:
        im_output *= (dtype.max - dtype.min)
        im_output += dtype.min
        return im_output.astype(dtype.dtype)
    im_output[~mask] = np.NaN
    return im_output
