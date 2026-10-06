# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.graph` instead of ``voprov.visualization.graph``."""
import warnings

warnings.warn("voprov.visualization.graph is deprecated, use voprov.graph", DeprecationWarning, stacklevel=2)

from voprov.graph import *  # noqa: F401,F403
