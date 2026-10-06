# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.model.records` instead of ``voprov.models.voprovConfigurations``."""
import warnings

warnings.warn("voprov.models.voprovConfigurations is deprecated, use voprov.model.records", DeprecationWarning, stacklevel=2)

from voprov.model.records import *  # noqa: F401,F403
