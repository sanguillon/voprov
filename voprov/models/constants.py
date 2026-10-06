# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.constants` instead of ``voprov.models.constants``."""
import warnings

warnings.warn("voprov.models.constants is deprecated, use voprov.constants", DeprecationWarning, stacklevel=2)

from voprov.constants import *  # noqa: F401,F403
