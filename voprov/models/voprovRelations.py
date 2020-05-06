# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.model import (ProvRelation)
from voprov.models.constants import *


class VOProvRelation(ProvRelation):
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvIsDescribedBy(VOProvRelation):
    FORMAL_ATTRIBUTES = (VOPROV_ATTR_DESCRIBED, VOPROV_ATTR_DESCRIPTOR)
    _prov_type = VOPROV_DESCRIPTION_RELATION


class VOProvWasConfiguredBy(VOProvRelation):
    FORMAL_ATTRIBUTES = None
    _prov_type = None