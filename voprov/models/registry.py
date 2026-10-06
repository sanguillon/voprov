# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.registry` instead of ``voprov.models.registry``."""
import warnings

warnings.warn("voprov.models.registry is deprecated, use voprov.registry", DeprecationWarning, stacklevel=2)

from voprov.registry import *  # noqa: F401,F403
