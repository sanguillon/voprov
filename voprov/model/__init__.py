# -*- coding: utf-8 -*-
"""VOProv model, organised like :mod:`prov.model`.

* :mod:`voprov.model.records`: records (elements, relations, descriptions, configurations)
* :mod:`voprov.model.namespaces`: namespace manager
* :mod:`voprov.model.bundle`: bundle and document
"""
from voprov.model.records import *
from voprov.model.namespaces import VOProvNamespaceManager
from voprov.model.bundle import VOProvBundle, VOProvDocument

# register voprov records in prov's tables
from voprov.registry import register  # noqa: E402

register()
