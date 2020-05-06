# -*- coding: ISO-8859-1 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from prov.serializers import (Registry)
from prov.serializers import *
from voprov.serializers.provn import ProvNSerializer

__author__ = 'Jean-Francois Sornay'
__email__ = 'jean-francois.sornay@etu.umontpellier.fr'


Registry.load_serializers()
Registry.serializers.update()

Registry.serializers.update({
            'provn': ProvNSerializer,
})
