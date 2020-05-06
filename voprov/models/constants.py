# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.constants import *
from prov.model import Literal

__author__ = 'Jean-François Sornay'
__email__ = 'jean-francois.sornay@etu.umontpellier.fr'

VOPROV = Namespace('voprov', 'http://www.ivoa.net/documents/ProvenanceDM/index.html')

# Part 1 : namespace for voprov classes
#   voprov description
VOPROV_ACTIVITY_DESCRIPTION =           VOPROV['ActivityDescription']
VOPROV_USAGE_DESCRIPTION =              VOPROV['UsageDescription']
# VOPROV_GENERATION_DESCRIPTION =         VOPROV['GenerationDescription']

#   voprov configuration

#   voprov relation
VOPROV_DESCRIPTION_RELATION =           VOPROV['DescriptionRelation']
# VOPROV_CONFIGURATION_RELATION =         VOPROV['ConfigurationRelation']

# Part 2 : map for serialization usage
#   adding the voprov provn representation for the map for provn representation
PROV_N_MAP.update({
    # voprov description
    VOPROV_ACTIVITY_DESCRIPTION:        u'activityDescription',
    VOPROV_USAGE_DESCRIPTION:           u'usageDescription',
    # VOPROV_GENERATION_DESCRIPTION:      u'generationDescription',

    # voprov configuration

    # voprov relation
    VOPROV_DESCRIPTION_RELATION:        u'isDescribedBy',
    # VOPROV_CONFIGURATION_RELATION:      u'wasConfiguredBy',
})

#   adding records for the map of record defined as subtypes in PROV-N but top level types in for example
#   PROV XML also need a mapping.
ADDITIONAL_N_MAP.update({
    # Nothing for the moment
})

#   adding the voprov namespace for the Map of qualified names from the PROV namespace to their base class. If it
#   has no baseclass it maps to itsself. This is needed for example for PROV
#   XML (de)serializer where extended types are used a lot.
PROV_BASE_CLS.update({
    # voprov description
    VOPROV_ACTIVITY_DESCRIPTION:        VOPROV_ACTIVITY_DESCRIPTION,
    VOPROV_USAGE_DESCRIPTION:           VOPROV_USAGE_DESCRIPTION,
    # VOPROV_GENERATION_DESCRIPTION:      VOPROV_GENERATION_DESCRIPTION,

    # voprov configuration

    # voprov relation
    VOPROV_DESCRIPTION_RELATION:        VOPROV_DESCRIPTION_RELATION,
    # VOPROV_CONFIGURATION_RELATION:      VOPROV_CONFIGURATION_RELATION,
})


# Part 3 : Identifier for voprov's attributes
#   Identifiers for PROV's attributes
#   voprov description
#   voprov configuration
#   voprov relation
VOPROV_ATTR_DESCRIBED =                 VOPROV['described']
VOPROV_ATTR_DESCRIPTOR =                VOPROV['descriptor']
# VOPROV_ATTR_CONFIGURED =         VOPROV['configured']
# VOPROV_ATTR_CONFIGURATOR =        VOPROV['configurator']

#   Literal properties
VOPROV_ATTR_NAME =                      VOPROV['name']
VOPROV_ATTR_ROLE =                      VOPROV['role']

#   adding the voprov identifier to the map for the qualified name of attribute
PROV_ATTRIBUTE_QNAMES.update({
    # voprov description
    Literal(VOPROV_ATTR_NAME),
    Literal(VOPROV_ATTR_ROLE),

    # voprov configuration

    # voprov relation
    VOPROV_ATTR_DESCRIBED,
    VOPROV_ATTR_DESCRIPTOR,
})

#   adding the voprov identifier for the literals attribute
PROV_ATTRIBUTE_LITERALS.update({
    # nothing for the moment
})
