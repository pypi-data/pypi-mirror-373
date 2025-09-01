#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-30
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : kernel

"""
This funtion creates kernels small arrays, mainly for convolutions.
"""



# %% Libraries
from arrlp import coordinates
import numpy as np
from scipy.special import erf, erfinv, j1



# %% Function
def kernel(ndims=2, pixel=1, *, dtype=np.float32, atrou=0, window=None, sigma=None, wl=None, NA=None) :
    '''
    This funtion creates kernels small arrays, mainly for convolutions.
    
    Parameters
    ----------
    ndims : int
        Number of dimensions.
    pixel : int
        Size of pixel for each dimension.
    dtype : np.dtype
        data type of kernel.
    atrou : int
        Number of trou to put for atrou algorithm, None for normal kernel.
    window : float
        Size of window for mask kernel.
    sigma : float
        Size of sigma for gaussian kernel.
    wl : float
        wavelength for Airy kernel.
    NA : float
        Numerical Aperture for Airy kernel.

    Returns
    -------
    k : np.array
        kernel generated.

    Raises
    ------
    SyntaxError
        One keyword input must be put that defines type of kernel, if not will raise Error.

    Examples
    --------
    >>> from arrlp import kernel
    ...
    >>> kernel(window=10) # Mask
    >>> kernel(sigma=5) # Gaussian
    >>> kernel(wl=640, NA=1.5) # Airy
    '''

    #kernel
    if sigma is not None :
        k = kernel_gaus(sigma, pixel, ndims)
    elif window is not None :
        k = kernel_mask(window, pixel, ndims)
    elif wl is not None and NA is not None :
        k = kernel_airy(wl, NA, pixel, ndims)
    else :
        raise SyntaxError('Kernel was not recognized')

    #"à trou" kernel
    if atrou is not None and atrou != 0 :
        k = kernel_atrou(k, atrou)

    k = k.astype(dtype)
    k /= k.sum()
    return k



def kernel_gaus(sigma, pixel=1, ndims=1, tol_zero=1/100) :
    '''gets a n dimensions gaussian kernel'''

    # Coordinates
    sigma = np.asarray(iterable(sigma, ndims))
    pixel = np.asarray(iterable(pixel, ndims))
    shape = np.ceil(sigma * 6 / pixel)
    shape = tuple((shape + 1 - shape % 2).astype(int)) #odd number shape
    coords = coordinates(shape, center=True, pixel=pixel)

    # Apply Gaussian on each dimension and calculates distance from origin in sigmas
    k = 1
    r2 = 0 # (r/sigma)²
    for coord, sig, pix in zip(coords, sigma, pixel) :
        mini = (coord - pix/2) / np.sqrt(2) / sig
        maxi = (coord + pix/2) / np.sqrt(2) / sig
        k = k * ((erf(mini) - erf(maxi)) / 2)
        r2 = r2 + (coord / sig)**2

    # Apply mask
    mask = r2 > 2 * erfinv((1 - tol_zero)**(1/ndims))**2 # r² > (n**(1/ndims)*sqrt(2))**2
    k[mask] = 0
    return k



def kernel_mask(window, pixel=1, ndims=1) :
    '''gets a n dimensions mask kernel'''

    # Coordinates
    window = np.asarray(iterable(window, ndims))
    pixel = np.asarray(iterable(pixel, ndims))
    shape = np.ceil(window / pixel)
    shape = tuple((shape + 1 - shape % 2).astype(int)) #odd number shape
    coords = coordinates(shape, center=True, pixel=pixel)

    # Calculates distance from origin in windows
    k = np.ones(shape)
    r2 = 0 # (r/window)²
    for coord, win, pix in zip(coords, window, pixel) :
        r2 = r2 + (coord / win)**2

    # Apply mask
    mask = r2 > 1/4 #r² > (1/2)**2
    k[mask] = 0
    return k



def kernel_airy(wl, NA, pixel=1, ndims=1) :
    '''gets a n dimensions mask kernel'''

    # Coordinates
    pixel = np.asarray(iterable(pixel, ndims))
    shape = np.ceil((2.44 * wl / NA) / pixel)
    shape = tuple((shape + 1 - shape % 2).astype(int)) #odd number shape
    coords = coordinates(shape, center=True, pixel=pixel)

    # Calculates distance from origin in nm and pixel apply Airy function
    r2 = 0 # r²
    for coord in coords :
        r2 = r2 + coord**2
    r = np.sqrt(r2)
    z = 2 * np.pi * r * NA / wl
    ma = r < 1 # < 1 nm
    k = np.empty(shape, dtype=np.float32)
    k[~ma] = (2 * j1(z[~ma]) / z[~ma])**2
    k[ma] = 1

    # Apply mask
    mask = r2 > (1.22 * wl / NA)**2 #r² > (1.22 * wl/NA)**2
    k[mask] = 0
    return k



def kernel_atrou(k, order) :
    if order == 0 :
        return k
    shape = k.shape
    newshape = tuple([s + (s - 1) * order for s in shape])
    newkernel = np.zeros(newshape)
    slices = [slice(None,None,order+1) for _ in range(k.ndim)]
    newkernel[*slices] = k
    return newkernel



def iterable(arg, ndims) :
    try :
        if len(arg) != ndims :
            raise ValueError('Argument does not have good number of dimensions')
        else :
            return arg
    except TypeError :
        return (arg,) * ndims



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)