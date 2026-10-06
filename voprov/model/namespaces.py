# -*- coding: utf-8 -*-
from prov.model import NamespaceManager
from voprov.constants import DEFAULT_NAMESPACES

__author__ = 'Jean-Francois Sornay'
__email__ = 'jeanfrancois.sornay@gmail.com'


class VOProvNamespaceManager(NamespaceManager):
    """Manages namespaces for VOPROV documents and bundles."""

    def __init__(self, namespaces=None, default=None, parent=None):
        """
        Constructor.

        :param namespaces: Optional namespaces to add to the manager
            (default: None).
        :param default: Optional default namespace to use (default: None).
        :param parent: Optional parent :py:class:`NamespaceManager` to make this
            namespace manager a child of (default: None).
        """
        super(VOProvNamespaceManager, self).__init__(default=default, parent=parent)
        # register all default namespaces (including voprov) as declared namespaces
        self._default_namespaces = DEFAULT_NAMESPACES
        for namespace in self._default_namespaces.values():
            self._namespaces[namespace.prefix] = namespace
            self[namespace.prefix] = namespace
            self._uri_map[namespace.uri] = namespace
        self.add_namespaces(namespaces)
