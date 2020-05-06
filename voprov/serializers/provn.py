# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.serializers.provn import *

__author__ = 'Jean-Francois Sornay'
__email__ = 'jean-francois.sornay@etu.umontpellier.fr'


class ProvNSerializer(ProvNSerializer):
    """PROV-N serializer for ProvDocument

    """
    def serialize(self, stream, **kwargs):
        """
        Serializes a :class:`prov.model.ProvDocument` instance to a
        `PROV-N <http://www.w3.org/TR/prov-n/>`_.

        :param stream: Where to save the output.
        """
        provn_content = self.document.get_provn()
        if not isinstance(stream, io.TextIOBase):
            provn_content = provn_content.encode('utf-8')
        stream.write(provn_content)

    def deserialize(self, stream, **kwargs):
        super(self).deserialize(stream, **kwargs)
