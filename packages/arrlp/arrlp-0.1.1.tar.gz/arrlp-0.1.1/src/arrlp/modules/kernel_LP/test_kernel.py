#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-30
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : kernel

"""
This file allows to test kernel

kernel : This funtion creates kernels small arrays, mainly for convolutions.
"""



# %% Libraries
from corelp import debug
import pytest
from matplotlib import pyplot as plt
import numpy as np
from arrlp import kernel
debug_folder = debug(__file__)



# %% Function test
@pytest.mark.parametrize("kwargs, title", [
    ({"window":500}, "Mask"),
    ({"sigma":250}, "Gaussian"),
    ({"wl":640, "NA":1.5}, "Airy"),
])
def test_function(kwargs, title) :
    '''
    Test kernel values
    '''
    k = kernel(pixel=10, **kwargs)
    assert np.isclose(k.sum(), np.float32(1.))
    plt.figure()
    plt.imshow(k, cmap="hot")
    plt.tight_layout()
    plt.colorbar()
    plt.savefig(debug_folder / f"{title}.png")



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)