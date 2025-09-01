#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-30
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : convolve

"""
This function convolves two numpy arrays (1D, 2D, 3D).
"""



# %% Libraries
from arrlp import correlate
import numpy as np



# %% Function
def convolve(arr, k=None, /, out=None, **kwargs) :
    '''
    This function convolves two numpy arrays (1D, 2D, 3D).
    
    Parameters
    ----------
    arr : numpy.ndarray
        first array to correlate.
    k : numpy.ndarray
        second array to correlate, if is None is auto created.
    out : numpy.ndarray
        array where to put correlation, same shape as arr, if None is auto initialized.
    kwargs : dict
        Parameters to pass to arrlp.correlate function.

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
    >>> convolve(img, sigma=5) # Gaussian convolve
    >>> convolve(img, windowma=10) # Mask convolve
    >>> convolve(img, wl=640, NA=1.5) # Airy convolve
    '''

    if k is not None :
        for dim in len(np.shape(k)) :
            k = np.flip(k, axis=dim)
    return correlate(arr, k, out, **kwargs)
    



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)