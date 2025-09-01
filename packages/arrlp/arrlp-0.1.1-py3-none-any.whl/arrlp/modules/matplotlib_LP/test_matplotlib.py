#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-30
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : matplotlib

"""
This file allows to test matplotlib

matplotlib : 
"""



# %% Libraries
from corelp import print, debug
import pytest
from arrlp import matplotlib
debug_folder = debug(__file__)



# %% Function test
def test_function() :
    '''
    Test matplotlib function
    '''
    print('Hello world!')



# %% Instance fixture
@pytest.fixture()
def instance() :
    '''
    Create a new instance at each test function
    '''
    return matplotlib()

def test_instance(instance) :
    '''
    Test on fixture
    '''
    pass


# %% Returns test
@pytest.mark.parametrize("args, kwargs, expected, message", [
    #([], {}, None, ""),
    ([], {}, None, ""),
])
def test_returns(args, kwargs, expected, message) :
    '''
    Test matplotlib return values
    '''
    assert matplotlib(*args, **kwargs) == expected, message



# %% Error test
@pytest.mark.parametrize("args, kwargs, error, error_message", [
    #([], {}, None, ""),
    ([], {}, None, ""),
])
def test_errors(args, kwargs, error, error_message) :
    '''
    Test matplotlib error values
    '''
    with pytest.raises(error, match=error_message) :
        matplotlib(*args, **kwargs)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)