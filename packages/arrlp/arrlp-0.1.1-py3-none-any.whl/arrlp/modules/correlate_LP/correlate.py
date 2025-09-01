#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-30
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : correlate

"""
This function correlates two numpy arrays (1D, 2D, 3D).
"""



# %% Libraries
from arrlp import kernel
from numba import njit, prange
import numpy as np
import astropy



# %% Function
def correlate(arr, k=None, /, out=None, *, method="mean", **kernel_kwargs) :
    '''
    This function correlates two numpy arrays (1D, 2D, 3D).
    
    Parameters
    ----------
    arr : numpy.ndarray
        first array to correlate.
    k : numpy.ndarray
        second array to correlate, if is None is auto created.
    out : numpy.ndarray
        array where to put correlation, same shape as arr, if None is auto initialized.
    method : str
        define function to use for correlation. Should be in ["astro", "mean", "std", "min", "max", "sum", "prod"].
    kernel_kwargs : dict
        Parameters passed to kernel function for auto-creation.

    Returns
    -------
    out : numpy.ndarray
        Correlated array.

    Raises
    ------
    TypeError
        if output shape does not match array shape.

    Examples
    --------
    >>> from arrlp import correlate
    ...
    >>> correlate(img, sigma=5) # Gaussian correlation
    >>> correlate(img, windowma=10) # Mask correlation
    >>> correlate(img, wl=640, NA=1.5) # Airy correlation
    '''

    # Method
    ndims = len(np.shape(arr))
    method = f"{method}{ndims}"

    # Kernel
    if k is None :
        k = kernel(ndims, **kernel_kwargs)
    
    # Output
    if out is None :
        out = np.empty_like(arr)
    if np.shape(out) != np.shape(arr) :
        raise TypeError('Output shape does not match array shape')
    
    # Function
    function = function_factory(method)
    function(arr, k, out)
    
    return out



_cached = {}
funcs = {
    'mean' : np.nanmean,
    'std' : np.nanstd,
    'min' : np.nanmin,
    'max' : np.nanmax,
    'sum' : np.nansum,
    'prod' : np.nanprod,
    }

def function_factory(method) :
    function = _cached.get(method, None)
    if function is not None :
        return function

    if method.startswith("astro") :
        if method.endswith("1") :
            def invert(k) :
                return k[::-1]
        elif method.endswith("2") :
            def invert(k) :
                return k[::-1, ::-1]
        elif method.endswith("3") :
            def invert(k) :
                return k[::-1, ::-1, ::-1]
        else :
            raise SyntaxError(f'Correlation error cannot be {method}')

        def function(arr, k, out, *, kernel_limit=2**12) :
            k = invert(k)
            if k.size > kernel_limit :
                out[:] = astropy.convolution.convolve_fft(arr, k, normalize_kernel=False)
            else :
                out[:] = astropy.convolution.convolve(arr, k, boundary='extend', normalize_kernel=False)
        _cached[method] = function
        return function

    func = funcs[method[:-1]]

    if method.endswith("1") :
        @njit(parallel=True)
        def function(arr, k, out):
            xlim, = np.shape(arr)
            xp, = np.shape(k)
            xp = int(xp / 2)
            sum = np.sum(k)
            sizep = k.size
            for i in prange(xlim):
                x = i
                xmin, xmax = max(0, x - xp), min(xlim, x + xp + 1)
                n = (xmax - xmin)
                if n != sizep :
                    ksum = np.sum(k[xmin - x + xp: xmax - x + xp])
                    if ksum != 0 :
                        n = n * sum / ksum
                crop = arr[xmin:xmax] * k[xmin - x + xp: xmax - x + xp] * n
                out[x] = func(crop)

    elif method.endswith("2") :
        
        @njit(parallel=True)
        def function(arr, k, out):
            ylim, xlim = np.shape(arr)
            yp, xp = np.shape(k)
            yp, xp = int(yp / 2),int(xp / 2)
            sum = np.sum(k)
            sizep = k.size
            for y in prange(ylim):
                for x in range(xlim) :
                    ymin, ymax = max(0, y - yp), min(ylim,y + yp + 1)
                    xmin, xmax = max(0, x - xp), min(xlim,x + xp + 1)
                    n = (ymax - ymin) * (xmax - xmin)
                    if n != sizep :
                        ksum = np.sum(k[ymin - y + yp: ymax - y + yp, xmin - x + xp: xmax - x + xp])
                        if ksum != 0 :
                            n = n * sum / ksum
                    crop = arr[ymin:ymax, xmin:xmax] * k[ymin - y + yp: ymax - y + yp, xmin - x + xp: xmax - x + xp] * n
                    out[y, x] = func(crop)

    elif method.endswith("3") :
        
        @njit(parallel=True)
        def function(arr, k, out):
            zlim, ylim, xlim = np.shape(arr)
            zp, yp, xp = np.shape(k)
            zp, yp, xp = int(zp / 2), int(yp / 2), int(xp / 2)
            sum = np.sum(k)
            sizep = k.size
            for z in prange(zlim) :
                for y in range(ylim) :
                    for x in range(xlim) :
                        zmin, zmax = max(0, z - zp), min(zlim, z + zp + 1)
                        ymin, ymax = max(0, y - yp), min(ylim, y + yp + 1)
                        xmin, xmax = max(0, x - xp), min(xlim, x + xp + 1)
                        n = (zmax - zmin) * (ymax - ymin) * (xmax - xmin)
                        if n != sizep :
                            ksum = np.sum(k[zmin - z + zp: zmax - z + zp, ymin - y + yp: ymax - y + yp, xmin - x + xp: xmax - x + xp])
                            if ksum != 0 :
                                n = n * sum / ksum
                        crop = arr[zmin: zmax, ymin: ymax, xmin: xmax] * k[zmin - z + zp: zmax - z + zp, ymin - y + yp: ymax - y + yp, xmin - x + xp: xmax - x + xp] * n
                        out[z, y, x] = func(crop)
        
    else :
        raise SyntaxError(f'Correlation error cannot be {method}')
    _cached[method] = function
    return function



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)