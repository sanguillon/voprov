# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.plotly` instead of ``voprov.visualization.plotly``."""
import warnings

warnings.warn("voprov.visualization.plotly is deprecated, use voprov.plotly", DeprecationWarning, stacklevel=2)

from voprov.plotly import *  # noqa: F401,F403
