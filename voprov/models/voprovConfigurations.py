# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.model import (ProvElement)


class VOProvConfig(ProvElement):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvConfigFile(VOProvConfig):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvParameter(VOProvConfig):
    FORMAL_ATTRIBUTES = None
    _prov_type = None