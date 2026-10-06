# -*- coding: utf-8 -*-
"""Deprecated import path, kept for backward compatibility: use :mod:`voprov.serializers.provyaml` instead of ``voprov.serializers.voyaml``."""
import warnings

warnings.warn("voprov.serializers.voyaml is deprecated, use voprov.serializers.provyaml", DeprecationWarning, stacklevel=2)

from voprov.serializers.provyaml import *  # noqa: F401,F403
