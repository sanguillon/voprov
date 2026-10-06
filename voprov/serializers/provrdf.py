from prov.serializers.provrdf import *

from voprov.models.constants import (
    PROV_ID_ATTRIBUTES_MAP,
    PROV_N_MAP,
    PROV_BASE_CLS,
    VOPROV_ATTR_ARTEFACT_TYPE,
)

class VOProvRDFSerializer(ProvRDFSerializer):
    pass

def new_attr2rdf(attr):
    print("modified attr2rdf")
    return URIRef(PROV[PROV_ID_ATTRIBUTES_MAP[attr].split("prov:")[1]].uri)

attr2rdf = new_attr2rdf
