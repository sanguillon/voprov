from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.model import (ProvElement)
from voprov.models.constants import *


class VOProvDescription(ProvElement):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvActivityDescription(VOProvDescription):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME,)
    _prov_type = VOPROV_ACTIVITY_DESCRIPTION


class VOProvGenerationDescription(VOProvDescription):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvUsageDescription(VOProvDescription):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvEntityDescription(VOProvDescription):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvValueDescription(VOProvEntityDescription):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvConfigFileDescription(VOProvEntityDescription):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvParameterDescription(VOProvDescription):
    FORMAL_ATTRIBUTES = None
    _prov_type = None
