# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.serializers.provxml` instead of ``voprov.serializers.xml``."""
import warnings

warnings.warn("voprov.serializers.xml is deprecated, use voprov.serializers.provxml", DeprecationWarning, stacklevel=2)

from voprov.serializers.provxml import *  # noqa: F401,F403
