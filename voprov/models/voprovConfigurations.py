# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.model import (ProvElement)
from voprov.models.constants import *


class VOProvConfig(ProvElement):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvConfigFile(VOProvConfig):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME, VOPROV_ATTR_LOCATION)
    _prov_type = VOPROV_CONFIGURATION_FILE


class VOProvParameter(VOProvConfig):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME, VOPROV_ATTR_VALUE)
    _prov_type = VOPROV_CONFIGURATION_PARAMETER
