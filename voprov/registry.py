# -*- coding: utf-8 -*-
"""Registration of voprov's types in prov's global tables.

prov looks up record classes, PROV-N names, base classes and attribute names in module-level tables
(``prov.model.PROV_REC_CLS``, ``prov.constants.PROV_N_MAP``, ...) and offers no hook to extend them.
This module is the single place where voprov extends them. :func:`register` is idempotent and is
called when :mod:`voprov.model` is imported.
"""
import prov.constants
import prov.model

from voprov import constants as c


def voprov_record_classes():
    """Mapping from record type to the voprov class implementing it (imported lazily, as they need prov)."""
    from voprov.model.records import (
        VOProvEntity, VOProvActivity, VOProvAgent, VOProvUsage, VOProvGeneration, VOProvCommunication,
        VOProvStart, VOProvEnd, VOProvInvalidation, VOProvDerivation, VOProvAttribution, VOProvAssociation,
        VOProvDelegation, VOProvInfluence, VOProvSpecialization, VOProvAlternate, VOProvMention,
        VOProvMembership, VOProvValueEntity, VOProvDataSetEntity,
        VOProvActivityDescription, VOProvUsageDescription, VOProvGenerationDescription,
        VOProvEntityDescription, VOProvValueDescription, VOProvDataSetDescription,
        VOProvConfigFileDescription, VOProvParameterDescription,
        VOProvConfigFile, VOProvParameter,
        VOProvIsDescribedBy, VOProvWasConfiguredBy, VOProvIsRelatedTo, VOProvHadReference)
    return {
        # link prov class to their voprov representation
        c.VOPROV_ENTITY: VOProvEntity,
        c.VOPROV_ACTIVITY: VOProvActivity,
        c.VOPROV_AGENT: VOProvAgent,
        c.VOPROV_USAGE: VOProvUsage,
        c.VOPROV_GENERATION: VOProvGeneration,
        c.VOPROV_COMMUNICATION: VOProvCommunication,
        c.VOPROV_START: VOProvStart,
        c.VOPROV_END: VOProvEnd,
        c.VOPROV_INVALIDATION: VOProvInvalidation,
        c.VOPROV_DERIVATION: VOProvDerivation,
        c.VOPROV_ATTRIBUTION: VOProvAttribution,
        c.VOPROV_ASSOCIATION: VOProvAssociation,
        c.VOPROV_DELEGATION: VOProvDelegation,
        c.VOPROV_INFLUENCE: VOProvInfluence,
        c.VOPROV_SPECIALIZATION: VOProvSpecialization,
        c.VOPROV_ALTERNATE: VOProvAlternate,
        c.VOPROV_MENTION: VOProvMention,
        c.VOPROV_MEMBERSHIP: VOProvMembership,

        # extend prov model
        c.VOPROV_VALUE_ENTITY: VOProvValueEntity,
        c.VOPROV_DATASET_ENTITY: VOProvDataSetEntity,

        # voprov description
        c.VOPROV_ACTIVITY_DESCRIPTION: VOProvActivityDescription,
        c.VOPROV_USAGE_DESCRIPTION: VOProvUsageDescription,
        c.VOPROV_GENERATION_DESCRIPTION: VOProvGenerationDescription,
        c.VOPROV_ENTITY_DESCRIPTION: VOProvEntityDescription,
        c.VOPROV_VALUE_DESCRIPTION: VOProvValueDescription,
        c.VOPROV_DATASET_DESCRIPTION: VOProvDataSetDescription,
        c.VOPROV_CONFIG_FILE_DESCRIPTION: VOProvConfigFileDescription,
        c.VOPROV_PARAMETER_DESCRIPTION: VOProvParameterDescription,

        # voprov configuration
        c.VOPROV_CONFIGURATION_FILE: VOProvConfigFile,
        c.VOPROV_CONFIGURATION_PARAMETER: VOProvParameter,

        # voprov relation
        c.VOPROV_DESCRIPTION_RELATION: VOProvIsDescribedBy,
        c.VOPROV_CONFIGURATION_RELATION: VOProvWasConfiguredBy,
        c.VOPROV_RELATED_TO_RELATION: VOProvIsRelatedTo,
        c.VOPROV_REFERENCE_RELATION: VOProvHadReference,
    }


def register():
    """Extend prov's global tables with the voprov types (safe to call several times)."""
    prov.constants.PROV_N_MAP.update(c.VOPROV_N_MAP)
    prov.constants.ADDITIONAL_N_MAP.update(c.VOPROV_ADDITIONAL_N_MAP)
    prov.constants.PROV_BASE_CLS.update(c.VOPROV_BASE_CLS)
    prov.constants.PROV_ATTRIBUTE_QNAMES.update(c.VOPROV_ATTRIBUTE_QNAMES)
    prov.constants.PROV_ATTRIBUTE_LITERALS.update(c.VOPROV_ATTRIBUTE_LITERALS)
    prov.model.PROV_REC_CLS.update(voprov_record_classes())
