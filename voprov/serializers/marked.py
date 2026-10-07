# -*- coding: utf-8 -*-
"""The VOProv records that PROV does not have, in the PROV-JSON and PROV-XML files.

Those files are standard: they only have the records of PROV. A record of VOProv that PROV does not have is written
as the PROV record that it specializes, marked with a ``prov:type`` of the ``voprov`` namespace:

* the elements (value and dataset entities, parameters, configuration files, descriptions) are entities,
* the relations of VOProv (described, related, configured, referenced) are influences, between the first two ends of
  the relation.

When the file is read, the marker gives its class back to the record.
"""
import prov.model

from voprov.constants import *

#: VOProv elements that are written as a PROV entity, marked with their type
MARKED_ENTITIES = [
    VOPROV_VALUE_ENTITY, VOPROV_DATASET_ENTITY, VOPROV_CONFIGURATION_FILE, VOPROV_CONFIGURATION_PARAMETER,
    VOPROV_ACTIVITY_DESCRIPTION, VOPROV_ENTITY_DESCRIPTION, VOPROV_VALUE_DESCRIPTION, VOPROV_DATASET_DESCRIPTION,
    VOPROV_USAGE_DESCRIPTION, VOPROV_GENERATION_DESCRIPTION, VOPROV_CONFIG_FILE_DESCRIPTION,
    VOPROV_PARAMETER_DESCRIPTION,
]
#: VOProv relations that are written as a PROV influence, marked with their type
MARKED_RELATIONS = [
    VOPROV_DESCRIPTION_RELATION, VOPROV_RELATED_TO_RELATION, VOPROV_CONFIGURATION_RELATION,
    VOPROV_REFERENCE_RELATION,
]
#: the marked types, and the type of the PROV record that they are written as
MARKED_TYPES = dict([(t, VOPROV_ENTITY) for t in MARKED_ENTITIES] + [(t, VOPROV_INFLUENCE) for t in MARKED_RELATIONS])


def formal_attributes(rec_type):
    """Formal attributes of a type of record."""
    return prov.model.PROV_REC_CLS[rec_type].FORMAL_ATTRIBUTES


def written_as(rec_type):
    """Type of the PROV record that is written for a record, and its marker (None if it has no marker)."""
    if rec_type in MARKED_TYPES:
        return MARKED_TYPES[rec_type], rec_type
    return rec_type, None


def relation_ends(marker):
    """Attributes that are the ends of the influence written for a relation of VOProv: (formal attribute, attribute
    of the influence) for the first two formal attributes of the relation."""
    formal = formal_attributes(marker)
    return [(formal[0], PROV_ATTR_INFLUENCEE), (formal[1], PROV_ATTR_INFLUENCER)]


def find_marker(rec_type, types):
    """The marker among the types of a record that is read as ``rec_type`` (None if it is not marked)."""
    return next((t for t in types if MARKED_TYPES.get(t) == rec_type), None)
