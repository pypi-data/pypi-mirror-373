#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-31
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : imgLP
# Module        : crosscorrelate

"""
This file allows to test crosscorrelate

crosscorrelate : This function will calculated the image crosscorrelation between two images.
"""



# %% Libraries
from corelp import print, debug
import pytest
from imglp import crosscorrelate
debug_folder = debug(__file__)



# %% Function test
def test_function() :
    '''
    Test crosscorrelate function
    '''
    print('Hello world!')



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)