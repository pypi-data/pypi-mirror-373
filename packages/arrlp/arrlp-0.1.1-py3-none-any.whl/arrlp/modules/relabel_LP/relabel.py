#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-31
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : relabel

"""
This function redefines a label array to fill potential holes inside.
"""



# %% Libraries

import numpy as np
from numba import njit

@njit()
def relabel(array):
    '''
    This function redefines a label array to fill potential holes inside.
    
    Parameters
    ----------
    labels : np.ndarray
        array of labels (ints where each number > 0 corresponds to one object).

    Returns
    -------
    labels : np.ndarray
        1D version of the corrected labels array.

    Examples
    --------
    >>> from arrlp import relabel
    ...
    >>> relabel(labels)
    '''

    array = array.ravel()  # Flatten array
    unique_values = np.unique(array)  # Get sorted unique values
    mapping = np.zeros(unique_values[-1] + 1, dtype=np.uint32)  # Create mapping array

    # Assign new sequential labels
    for new_label, old_value in enumerate(unique_values):
        mapping[old_value] = new_label  # Map old value to new one

    # Apply relabeling
    for i in range(len(array)):
        array[i] = mapping[array[i]]

    return array.reshape((-1,))  # Return as 1D array


# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)