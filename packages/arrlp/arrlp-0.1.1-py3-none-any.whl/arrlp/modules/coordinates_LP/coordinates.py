#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-30
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : coordinates

"""
This function will return a ndarray corresponding to the coordinates array of the input.
"""



# %% Libraries
import numpy as np



# %% Function
def coordinates(shape, pixel=1., *, ndims=1, center=True, grid=False, origin=0.) :
    '''
    This function will return a ndarray corresponding to the coordinates array of the input.
    
    Parameters
    ----------
    shape : int or tuple or np.ndarray
        Describes the shape of the coordinates.
        If int, all dimensions will have this value.
        If tuple, corresponds to the shape.
        If array, will take the shape attribute of the array
    pixel : float, tuple(float)
        Says what is the size of one bin, default is 1.
        If tuple, corresponds to the pixel for each dimension.
    ndims : int
        Number of dimensions if input shape is int.
        Will be overriden by any other input dimension.
    center : bool or tuple(bool)
        True to center origin, False to start by origin.
        If tuple, defines how to place origin for each dimension.
    grid : bool
        True to return full meshgrid for each dimensions, False for broadcastable arrays.
    origin : float or tuple(float)
        Value of origin (default 0).
        If tuple, value for each dimension.

    Returns
    -------
    coords : np.ndarray or tuple(np.ndarray)
        for 1 dimensional shape, returns coordinates array.
        else, return a tuple of arrays for each dimensions.

    Raises
    ------
    ValueError
        if input or passed as tuples that do not have the good number of dimensions.

    Examples
    --------
    >>> from arrlp import coordinates
    ...
    >>> array = np.ones((5,4))
    >>> coordinates = coordinates(array, pixel=10, center=(True, False), grid=False, origin=(0,3))
    ... array([[-20.], [-10.], [0.], [10.], [20.]]), array([[3., 13., 23., 33.]])
    '''

    # Manage shape argument
    if isinstance(shape, int) :
        shape = (shape,) * ndims
    elif isinstance(shape, tuple) :
        pass
    else :
        shape = np.shape(shape)

    # Correct ndims
    ndims = len(shape)

    # Correct input dimensions
    pixel = iterable(pixel, ndims)
    center = iterable(center, ndims)
    origin = iterable(origin, ndims)

    #looping on shape
    coords = []
    for dim, (n, pix, cent, orig) in enumerate(zip(shape, pixel, center, origin)) :
        coord = n2coord(n, pixel=pix, center=cent, origin=orig)
        reshape = np.ones(ndims, dtype=int)
        reshape[dim] = len(coord)
        coord = coord.reshape(tuple(reshape))
        coords.append(coord)

    #Meshgrid
    if ndims == 1 :
        return coords[0]
    elif grid :
        return np.meshgrid(*coords, indexing='ij')
    else :
        return coords



def iterable(arg, ndims) :
    try :
        if len(arg) != ndims :
            raise ValueError('Argument does not have good number of dimensions')
        else :
            return arg
    except TypeError :
        return (arg,) * ndims



def n2coord(n, pixel=1., center=False, origin=0.) :
    if center :
        start, stop = -(n - 1) / 2,(n - 1) / 2
    else :
        start,stop = 0, n - 1
    return np.linspace(start, stop, n) * pixel + origin



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)