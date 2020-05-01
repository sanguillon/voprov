from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from prov.dot import *
from voprov.models.constants import *
from voprov.models.voprovDescriptions import *

__author__ = 'Jean-François Sornay'
__email__ = 'jean-francois.sornay@etu.umontpellier.fr'


GENERIC_NODE_STYLE.update({
    # voprov description
    VOProvActivityDescription: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': 'lightgray', 'color': 'dimgray'
    },
    # voprov configuration
    # voprov relation
})

DOT_PROV_STYLE.update({
    # voprov description
    VOPROV_ACTIVITY_DESCRIPTION: {
        'shape': 'oval', 'style': 'filled',
        'fillcolor': '#FF7C47', 'color': '#808080'
    },
    # voprov configuration
    # voprov relation
    VOPROV_DESCRIPTION_RELATION: {
        'label': 'isDescribedBy', 'fontsize': '10.0',
        'color': '#FF6629', 'fontcolor': '#FF6629'
    },
})
