# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.dot` instead of ``voprov.visualization.dot``."""
import warnings

warnings.warn("voprov.visualization.dot is deprecated, use voprov.dot", DeprecationWarning, stacklevel=2)

from voprov.dot import *  # noqa: F401,F403
