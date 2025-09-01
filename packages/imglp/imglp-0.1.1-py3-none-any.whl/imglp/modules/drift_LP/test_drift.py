#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-31
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : imgLP
# Module        : drift

"""
This file allows to test drift

drift : This function calculates the drift between two close images.
"""



# %% Libraries
from corelp import print, debug
import pytest
from imglp import drift
debug_folder = debug(__file__)



# %% Function test
def test_function() :
    '''
    Test drift function
    '''
    print('Hello world!')



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)