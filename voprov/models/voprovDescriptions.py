from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.model import (ProvElement)
from voprov.models.constants import *


class VOProvDescription(ProvElement):
    """Base class for VOProvDescription classes"""
    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvActivityDescription(VOProvDescription):
    """Class for VOProv activity description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_NAME,)
    _prov_type = VOPROV_ACTIVITY_DESCRIPTION

    def add_relation_to_an_activity(self, activity, identifier=None):
        """
        Creates a new relation between an activity and this activity description.

        :param activity:            Identifier or object of the activity described by this activity description.
        :param identifier:          Identifier for the relation between this activity description and the activity
                                    (default: None).
        """
        return self._bundle.description(activity, self, identifier)

    def usageDescription(self, identifier, role, description=None, type=None,
                         multiplicity=None, other_attributes=None):
        """
        Creates a new usage description.

        :param identifier:          Identifier for new usage description.
        :param role:                Function of the entity with respect to the activity.
        :param description:         A descriptive text for this kind of usage (default: None).
        :param type:                Type of relation (default: None).
        :param multiplicity:        Number of expected input entities to be used with the given role (default: None).
        :param other_attributes:    Optional other attributes as a dictionary or list
                                    of tuples to be added to the record optionally (default: None).
        """
        return self._bundle.usageDescription(identifier, self, role, description, type, multiplicity, other_attributes)


class VOProvGenerationDescription(VOProvDescription):
    """Class for VOProv generation description"""

    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvUsageDescription(VOProvDescription):
    """Class for VOProv usage description"""

    FORMAL_ATTRIBUTES = (VOPROV_ATTR_ROLE,)
    _prov_type = VOPROV_USAGE_DESCRIPTION

    def add_relation_to_an_usage(self, used, identifier=None):
        """
        Creates a new relation between an usage and this usage description.

        :param used:                The used relation described by this usage description.
        :param identifier:          Identifier for new usage description (default: None).
        """
        return self._bundle.description(used, self, identifier)


class VOProvEntityDescription(VOProvDescription):
    """Base class for VOProv entity description classes"""

    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvValueDescription(VOProvEntityDescription):
    """Class for VOProv value entity description"""

    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvDataSetDescription(VOProvEntityDescription):
    """Class for VOProv data set entity description"""

    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvConfigFileDescription(VOProvEntityDescription):
    """Class for VOProv configuration file description"""

    FORMAL_ATTRIBUTES = None
    _prov_type = None


class VOProvParameterDescription(VOProvDescription):
    """Class for VOProv parameter description"""

    FORMAL_ATTRIBUTES = None
    _prov_type = None
