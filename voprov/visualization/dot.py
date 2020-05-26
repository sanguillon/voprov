# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.dot import *

from voprov.models.voprovDescriptions import *
from voprov.models.voprovConfigurations import *
from voprov.models.model import *
from voprov.visualization.graph import *

__author__ = 'Jean-Francois Sornay'
__email__ = 'jean-francois.sornay@etu.umontpellier.fr'


# updating the generic node style map which is used when the object used in a relation is not declared
GENERIC_NODE_STYLE.update({
    # voprov description
    VOProvDescription: {
        'shape': 'star', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'blue'
    },
    VOProvActivityDescription: {
        'shape': 'box', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
    VOProvEntityDescription: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
    VOProvUsageDescription: {
        'shape': 'invtrapezium', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
    VOProvGenerationDescription: {
        'shape': 'trapezium', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
    VOProvConfigFileDescription: {
        'shape': 'trapezium', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
    VOProvParameterDescription: {
        'shape': 'trapezium', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
    # voprov configuration
    VOProvConfigFile: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
    VOProvParameter: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
})

# updating the style of the different prov record
DOT_PROV_STYLE.update({
    # extend prov model
    VOPROV_VALUE_ENTITY: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': '#FFFC87', 'color': '#808080'
    },
    VOPROV_DATASET_ENTITY: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': '#FFFC87', 'color': '#808080'
    },

    # voprov description
    VOPROV_ACTIVITY_DESCRIPTION: {
        'shape': 'box', 'style': 'filled',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },
    VOPROV_USAGE_DESCRIPTION: {
        'shape': 'invtrapezium', 'style': 'filled', 'margin': '0 0', 'fixedsize': 'false',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },
    VOPROV_GENERATION_DESCRIPTION: {
        'shape': 'trapezium', 'style': 'filled', 'margin': '0 0', 'fixedsize': 'false',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },
    VOPROV_ENTITY_DESCRIPTION: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },
    VOPROV_VALUE_DESCRIPTION: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },
    VOPROV_DATASET_DESCRIPTION: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },
    VOPROV_CONFIG_FILE_DESCRIPTION: {
        'shape': 'box3d', 'style': 'filled',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },
    VOPROV_PARAMETER_DESCRIPTION: {
        'shape': 'note', 'style': 'filled',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },

    # voprov configuration
    VOPROV_CONFIGURATION_FILE: {
        'shape': 'box3d', 'style': 'filled',
        'fillcolor': '#4CDD4C', 'color': '#808080'
    },
    VOPROV_CONFIGURATION_PARAMETER: {
        'shape': 'note', 'style': 'filled',
        'fillcolor': '#4CDD4C', 'color': '#808080'
    },

    # voprov relation
    VOPROV_DESCRIPTION_RELATION: {
        'label': 'isDescribedBy', 'fontsize': '10.0',
        'color': '#FF6629', 'fontcolor': '#FF6629'
    },
    VOPROV_RELATED_TO_RELATION: {
        'label': 'isRelatedTo', 'fontsize': '10.0',
        'color': '#BFC9BF', 'fontcolor': '#BFC9BF'
    },
    VOPROV_CONFIGURATION_RELATION: {
        'label': 'wasConfiguredBy', 'fontsize': '10.0',
        'color': '#57B857', 'fontcolor': '#57B857'
    },
})
