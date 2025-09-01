#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-30
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : correlate

"""
This file allows to test correlate

correlate : This function correlates two numpy arrays (1D, 2D, 3D).
"""



# %% Libraries
from corelp import debug
import pytest
from matplotlib import pyplot as plt
from arrlp import kernel, correlate
debug_folder = debug(__file__)



# %% Function test
@pytest.mark.parametrize("kwargs, title", [
    ({"window":10}, "Mask"),
    ({"sigma":5}, "Gaussian"),
    ({"wl":640, "NA":1.5}, "Airy"),
])
def test_function(kwargs, title) :
    '''
    Test correlate values
    '''

    img = kernel(pixel=5, window=1000)
    
    plt.figure()
    plt.imshow(img, cmap="hot")
    plt.tight_layout()
    plt.colorbar()
    plt.savefig(debug_folder / f"{title}_before.png")

    out = correlate(img, pixel=5, **kwargs)

    plt.figure()
    plt.imshow(out, cmap="hot")
    plt.tight_layout()
    plt.colorbar()
    plt.savefig(debug_folder / f"{title}.png")



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)