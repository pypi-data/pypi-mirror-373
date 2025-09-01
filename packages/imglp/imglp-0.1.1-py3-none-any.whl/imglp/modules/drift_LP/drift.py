#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-31
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : imgLP
# Module        : drift

"""
This function calculates the drift between two close images.
"""



# %% Libraries
import numpy as np
from imglp import crosscorrelate



# %% Function
def drift(image, image2, /, drift_max=None, *, fact=1, xp=np) :
    '''
    This function calculates the drift between two close images.
    
    Parameters
    ----------
    image : numpy.ndarray or cupy.ndarray
        first image to use.
    image2 : numpy.ndarray or cupy.ndarray
        second image to use.
    drift_max : float
        maximum drift in pixels.
    fact : float
        factor to apply to change maximum drift.
    xp : numpy or cupy
        if cupy will calculate on GPU
    

    Returns
    -------
    dx : float
        drift in x : x1 = x0 + dx [pix].
    dy : float
        drift in y : y1 = y0 + dy [pix].

    Examples
    --------
    >>> from imglp import drift
    ...
    >>> dx, dy = drift(img1, img2) # TODO
    '''

    # Getting crop shape
    if drift_max is not None :
        drift_max = int(round(drift_max))
        drift_max = drift_max * fact
        cs = drift_max * 2 + 1
        shape = min(image.shape)
        shape = shape if shape%2==1 else shape-1
        cs = cs if cs < shape else shape
        cropshape = (cs, cs)
    else :
        cropshape = None

    # Calculating crosscorrelation
    cc = crosscorrelate(image, image2, cropshape=cropshape, xp=xp)

    # Find peak
    iy, ix = xp.unravel_index(int(xp.argmax(cc)), cc.shape) # integer position
    if 0 < iy < cc.shape[0] - 1:
        dy_sub = subpixel_peak_1d(cc[iy-1:iy+2, ix])
    else :
        raise ValueError('Drift CC peak is on border, probably drift_max is not big enough.')
    if 0 < ix < cc.shape[1] - 1:
        dx_sub = subpixel_peak_1d(cc[iy, ix-1:ix+2])
    else :
        raise ValueError('Drift CC peak is on border, probably drift_max is not big enough.')

    # Convert peak position to shift
    dy = (iy - cc.shape[0] // 2) + dy_sub
    dx = (ix - cc.shape[1] // 2) + dx_sub

    return dx, dy, cc



def subpixel_peak_1d(vals):
    denom = 2 * vals[1] - vals[0] - vals[2]
    if denom == 0:
        raise ValueError('Denominator should not be 0')
    return 0.5 * (vals[0] - vals[2]) / denom



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)