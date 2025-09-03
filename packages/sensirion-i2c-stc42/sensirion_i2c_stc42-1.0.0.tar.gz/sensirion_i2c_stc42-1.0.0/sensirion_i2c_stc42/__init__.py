#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from .version import version as __version__  # noqa: F401

from sensirion_i2c_stc42.device import Stc42Device  # noqa: F401

__all__ = ['Stc42Device']
