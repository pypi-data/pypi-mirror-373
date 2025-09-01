#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-31
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : imgLP
# Module        : crosscorrelate

"""
This function will calculated the image crosscorrelation between two images.
"""



# %% Libraries
from numba import njit, cuda, prange
import numpy as np



# %% Function
def crosscorrelate(image, image2=None, /, *, out=None, cropshape=None, xp=np) :
    '''
    This function will calculated the image crosscorrelation between two images.
    
    Parameters
    ----------
    image : numpy.ndarray or cupy.ndarray
        First image to use.
    image2 : numpy.ndarray or cupy.ndarray
        Second image to use, if None will calculate autocorrelation.
    out : numpy.ndarray or cupy.ndarray
        Output array, if None will be initialized automatically.
    cropshape : tuple
        shape to use for output, if smaller than shape of images, will correspond to the middle crop
    xp : numpy or cupy
        if cupy, will calculate on GPU

    Returns
    -------
    out : numpy.ndarray or cupy.ndarray
        Crosscorrelation image [cropped].

    Examples
    --------
    >>> from imglp import crosscorrelate
    ...
    >>> out = crosscorrelate(img1, img2)
    '''

    if out is not None :
        cropshape = out.shape
    H, W = image.shape
    full_H, full_W = 2*H - 1, 2*W - 1
    if cropshape is None:
        out_shape = (H, W)
        y0 = (full_H - H) // 2
        x0 = (full_W - W) // 2
    else :
        h, w = cropshape
        if h%2 != 1 : #if even
            h -= 1
            if out is not None :
                out = out[:-1, :]
        if w%2 != 1 : #if even
            w -= 1
            if out is not None :
                out = out[:, :-1]
        out_shape = (h, w)
        y0 = (full_H - h) // 2
        x0 = (full_W - w) // 2
    image2 = image if image2 is None else image2
    if out is None :
        out = xp.zeros(out_shape, dtype=np.float64)

    #CPU
    if xp is np :
        cc_cpu(image, image2, out, y0, x0)

    #GPU
    else :
        image = xp.asarray(image)
        image2 = xp.asarray(image2)
        img = image - np.mean(image)
        img2 = image2 - np.mean(image2)
        norm = np.sqrt(np.sum(img ** 2) * np.sum(img2 ** 2)).item()

        # Launch parameters
        threadsperblock = (16, 16)
        blockspergrid_x = (out_shape[1] + threadsperblock[0] - 1) // threadsperblock[0]
        blockspergrid_y = (out_shape[0] + threadsperblock[1] - 1) // threadsperblock[1]
        blockspergrid = (blockspergrid_x, blockspergrid_y)

        # Run kernel
        cc_gpu[blockspergrid, threadsperblock](img, img2, out, y0, x0, norm)

    return out



@njit(parallel=True)
def cc_cpu(image1, image2, out, y0, x0):

    #initialization
    h, w = image1.shape
    image1 = image1 - np.mean(image1)
    image2 = image2 - np.mean(image2)
    norm1 = np.sum(image1 ** 2)
    norm2 = np.sum(image2 ** 2)
    norm = np.sqrt(norm1 * norm2)

    # Shift ranges: dy in [y0 - (h-1), y1 - (h-1)]
    # Output index: i in [0, y1 - y0)
    for yy in prange(out.shape[0]):
        dy = (y0 - (h - 1)) + yy
        for xx in range(out.shape[1]):
            dx = (x0 - (w - 1)) + xx
            acc = 0.0
            for y in range(h):
                ny = y + dy
                if 0 <= ny < h:
                    for x in range(w):
                        nx = x + dx
                        if 0 <= nx < w:
                            acc += image1[y, x] * image2[ny, nx]
            out[yy, xx] = acc / norm if norm != 0 else 0.0



@cuda.jit
def cc_gpu(image1, image2, out, y0, x0, norm):
    h, w = image1.shape
    xx, yy = cuda.grid(2)  # get thread index (x, y)

    if xx >= out.shape[1] or yy >= out.shape[0]:
        return

    dx = (x0 - (w - 1)) + xx
    dy = (y0 - (h - 1)) + yy
    acc = 0.0

    for y in range(h):
        ny = y + dy
        if 0 <= ny < h:
            for x in range(w):
                nx = x + dx
                if 0 <= nx < w:
                    acc += image1[y, x] * image2[ny, nx]

    out[yy, xx] = acc / norm if norm != 0 else 0.0



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)