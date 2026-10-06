# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.model` instead of ``voprov.models``."""
import warnings

warnings.warn("voprov.models is deprecated, use voprov.model", DeprecationWarning, stacklevel=2)

from voprov.model import *  # noqa: F401,F403
