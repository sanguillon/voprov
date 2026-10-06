# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.model` instead of ``voprov.models.model``."""
import warnings

warnings.warn("voprov.models.model is deprecated, use voprov.model", DeprecationWarning, stacklevel=2)

from voprov.constants import *  # noqa: F401,F403
from voprov.model.records import *  # noqa: F401,F403
from voprov.model.namespaces import *  # noqa: F401,F403
from voprov.model.bundle import *  # noqa: F401,F403
