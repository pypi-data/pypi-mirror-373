#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-31
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : relabel

"""
This file allows to test relabel

relabel : This function redefines a label array to fill potential holes inside.
"""



# %% Libraries
from corelp import print, debug
import pytest
from arrlp import relabel
debug_folder = debug(__file__)



# %% Function test
def test_function() :
    '''
    Test relabel function
    '''
    print('Hello world!')



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)