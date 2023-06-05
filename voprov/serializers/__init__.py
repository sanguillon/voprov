# -*- coding: utf-8 -*-
from voprov.serializers.provn import VOProvNSerializer
from voprov.serializers.xml import VOProvXMLSerializer
from voprov.serializers.provjson import VOProvJSONSerializer
from prov import Error

__author__ = 'Jean-Francois Sornay'
__email__ = 'jeanfrancois.sornay@gmail.com'
__all__ = [
    'get'
]


class DoNotExist(Error):
    """Exception for the case a serializer is not available."""
    pass


class Registry:
    """Registry of serializers."""

    serializers = None
    """Property caching all available serializers in a dict."""

    @staticmethod
    def load_serializers():
        """Loads all available serializers into the registry."""
        from voprov.serializers.provjson import VOProvJSONSerializer
        from voprov.serializers.provn import VOProvNSerializer
        from voprov.serializers.xml import VOProvXMLSerializer
        from prov.serializers.provrdf import ProvRDFSerializer
        from voprov.serializers.voyaml import VOProvYAMLSerializer

        Registry.serializers = {
            'json': VOProvJSONSerializer,
            'rdf': ProvRDFSerializer,
            'provn': VOProvNSerializer,
            'xml': VOProvXMLSerializer,
            'yaml': VOProvYAMLSerializer
        }


def get(format_name):
    """
    Returns the serializer class for the specified format. Raises a DoNotExist
    """
    # Lazily initialize the list of serializers to avoid cyclic imports
    if Registry.serializers is None:
        Registry.load_serializers()
    try:
        return Registry.serializers[format_name]
    except KeyError:
        raise DoNotExist(
            'No serializer available for the format "%s"' % format_name
        )
