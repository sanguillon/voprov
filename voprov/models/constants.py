# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.constants import *
from prov.model import Literal

__author__ = 'Jean-François Sornay'
__email__ = 'jean-francois.sornay@etu.umontpellier.fr'

VOPROV = Namespace('voprov', 'http://www.ivoa.net/documents/ProvenanceDM/index.html')

# Part 1 : namespace for voprov classes
# extend prov model
# PROV_ACTIVITY = VOPROV['Activity']
VOPROV_VALUE_ENTITY =                   VOPROV['ValueEntity']
VOPROV_DATASET_ENTITY =                 VOPROV['DatasetEntity']


#   voprov description
VOPROV_ACTIVITY_DESCRIPTION =           VOPROV['ActivityDescription']
VOPROV_USAGE_DESCRIPTION =              VOPROV['UsageDescription']
VOPROV_GENERATION_DESCRIPTION =         VOPROV['GenerationDescription']
VOPROV_ENTITY_DESCRIPTION =             VOPROV['EntityDescription']
VOPROV_VALUE_DESCRIPTION =              VOPROV['ValueDescription']
VOPROV_DATASET_DESCRIPTION =            VOPROV['DatasetDescription']

#   voprov configuration

#   voprov relation
VOPROV_DESCRIPTION_RELATION =           VOPROV['DescriptionRelation']
VOPROV_RELATED_TO_RELATION =            VOPROV['RelatedToRelation']
# VOPROV_CONFIGURATION_RELATION =         VOPROV['ConfigurationRelation']

# Part 2 : map for serialization usage
#   adding the voprov provn representation for the map for provn representation
PROV_N_MAP.update({
    # extend prov model
    VOPROV_VALUE_ENTITY:                u'valueEntity',
    VOPROV_DATASET_ENTITY:              u'datasetEntity',

    # voprov description
    VOPROV_ACTIVITY_DESCRIPTION:        u'activityDescription',
    VOPROV_USAGE_DESCRIPTION:           u'usageDescription',
    VOPROV_GENERATION_DESCRIPTION:      u'generationDescription',
    VOPROV_ENTITY_DESCRIPTION:          u'entityDescription',
    VOPROV_VALUE_DESCRIPTION:           u'valueDescription',
    VOPROV_DATASET_DESCRIPTION:         u'datasetDescription',

    # voprov configuration

    # voprov relation
    VOPROV_DESCRIPTION_RELATION:        u'isDescribedBy',
    VOPROV_RELATED_TO_RELATION:         u'isRelatedTo',
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
    # extend prov model
    VOPROV_VALUE_ENTITY:                VOPROV_VALUE_ENTITY,
    VOPROV_DATASET_ENTITY:              VOPROV_DATASET_ENTITY,

    # voprov description
    VOPROV_ACTIVITY_DESCRIPTION:        VOPROV_ACTIVITY_DESCRIPTION,
    VOPROV_USAGE_DESCRIPTION:           VOPROV_USAGE_DESCRIPTION,
    VOPROV_GENERATION_DESCRIPTION:      VOPROV_GENERATION_DESCRIPTION,
    VOPROV_ENTITY_DESCRIPTION:          VOPROV_ENTITY_DESCRIPTION,
    VOPROV_VALUE_DESCRIPTION:           VOPROV_VALUE_DESCRIPTION,
    VOPROV_DATASET_DESCRIPTION:         VOPROV_DATASET_DESCRIPTION,

    # voprov configuration

    # voprov relation
    VOPROV_DESCRIPTION_RELATION:        VOPROV_DESCRIPTION_RELATION,
    VOPROV_RELATED_TO_RELATION:         VOPROV_RELATED_TO_RELATION,
    # VOPROV_CONFIGURATION_RELATION:      VOPROV_CONFIGURATION_RELATION,
})


# Part 3 : Identifier for voprov's attributes
#   Identifiers for PROV's attributes
#   voprov description
VOPROV_ATTR_NAME =                      VOPROV['name']
VOPROV_ATTR_ROLE =                      VOPROV['role']
VOPROV_ATTR_VALUE_TYPE =                VOPROV['valueType']
VOPROV_ATTR_CONTENT_TYPE =              VOPROV['contentType']
#   voprov configuration

#   voprov relation
VOPROV_ATTR_DESCRIBED =                 VOPROV['described']
VOPROV_ATTR_DESCRIPTOR =                VOPROV['descriptor']
VOPROV_ATTR_RELATED =                   VOPROV['related']
VOPROV_ATTR_RELATOR =                   VOPROV['relator']
# VOPROV_ATTR_CONFIGURED =         VOPROV['configured']
# VOPROV_ATTR_CONFIGURATOR =        VOPROV['configurator']

#   adding the voprov identifier to the map for the qualified name of attribute
PROV_ATTRIBUTE_QNAMES.update({
    # voprov description
    Literal(VOPROV_ATTR_NAME),
    Literal(VOPROV_ATTR_ROLE),
    Literal(VOPROV_ATTR_VALUE_TYPE),
    Literal(VOPROV_ATTR_CONTENT_TYPE),

    # voprov configuration

    # voprov relation
    VOPROV_ATTR_DESCRIBED,
    VOPROV_ATTR_DESCRIPTOR,
    VOPROV_ATTR_RELATED,
    VOPROV_ATTR_RELATOR,
})

#   adding the voprov identifier for the literals attribute
PROV_ATTRIBUTE_LITERALS.update({
    # nothing for the moment
})
