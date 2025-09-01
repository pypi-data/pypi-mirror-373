#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-30
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : coordinates

"""
This file allows to test coordinates

coordinates : This function will return a ndarray corresponding to the coordinates array of the input.
"""



# %% Libraries
from corelp import debug
import pytest
import numpy as np
from arrlp import coordinates
debug_folder = debug(__file__)

print(coordinates())

# %% Returns test
@pytest.mark.parametrize("args, kwargs, expected, message", [
    #([], {}, None, ""),
    ([np.ones((5,4))], {"pixel":10, "center":(True, False), "grid":False, "origin":(0,3)}, (np.array([[-20.], [-10.], [0.], [10.], [20.]]), np.array([[3., 13., 23., 33.]])), ""),
])
def test_returns(args, kwargs, expected, message) :
    '''
    Test coordinates return values
    '''
    assert (coordinates(*args, **kwargs)[0] == expected[0]).all(), message
    assert (coordinates(*args, **kwargs)[1] == expected[1]).all(), message



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)