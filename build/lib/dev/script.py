from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from prov.model import ProvDocument, Namespace
from prov.dot import prov_to_dot
import requests

# Configure ProvStore API Wrapper with your API Key
from provstore.api import Api
# see your API key at https://provenance.ecs.soton.ac.uk/store/account/developer/
api = Api(username='tdh', api_key='64d26d6e74a3303976cb967429a12ec0c0e35a80')

retrieved_document = api.document.get(34494)

# json_content = u'{"wasDerivedFrom": {"_:id1": {"prov:usedEntity": "template:10", "prov:generatedEntity": "b:6153", "prov:type": {"type": "prov:QualifiedName", "$": "pic:Expansion"}}, "_:id3": {"prov:usedEntity": "bindings:5695", "prov:generatedEntity": "b:6153", "prov:type": {"type": "prov:QualifiedName", "$": "pic:BindingsDerivation"}}}, "prefix": {"b": "https://provenance.ecs.soton.ac.uk/picaso/bundles/", "pic": "http://www.ipaw.info/ns/picaso#", "u": "https://provenance.ecs.soton.ac.uk/picaso/account/", "template": "https://provenance.ecs.soton.ac.uk/picaso/templates/", "prov-o": "http://www.w3.org/ns/prov#", "bindings": "https://provenance.ecs.soton.ac.uk/picaso/bindings/"}, "entity": {"bindings:5695": {"prov:generatedAtTime": {"type": "xsd:dateTime", "$": "2014-09-17T13:50:41.653593+00:00"}, "prov:type": {"type": "prov:QualifiedName", "$": "pic:Bindings"}}, "b:6153": {"prov:type": {"type": "prov:QualifiedName", "$": "prov:Bundle"}, "prov:label": "Derivation (1 \u2190 n) #6153"}}, "bundle": {"b:6153": {"wasDerivedFrom": {"_:id1": {"prov:usedEntity": "eprints:13/Summary2.pdf", "prov:generatedEntity": "w3c:REC-prov-dm-20130430/uml/essentials.png"}}, "prefix": {"tmpl": "http://openprovenance.org/tmpl#", "w3c": "http://www.w3.org/TR/2013/", "b": "https://provenance.ecs.soton.ac.uk/picaso/bundles/", "eprints": "http://eprints.soton.ac.uk/361113/", "ui": "http://openprovenance.org/ui#", "xsd_1": "http://www.w3.org/2001/XMLSchema"}, "entity": {"eprints:13/Summary2.pdf": {}, "w3c:REC-prov-dm-20130430/uml/essentials.png": {}}}}, "wasAttributedTo": {"_:id2": {"prov:entity": "bindings:5695", "prov:agent": "u:1"}}}'
json_content = '''
{
  "prefix": {
    "ex": "http://example.org/"
  },
  "activity": {
    "ex:a6": {
      "prov:location": [
        {
          "$": "London",
          "type": "xsd:string"
        },
        {
          "$": "1",
          "type": "xsd:int"
        },
        {
          "$": "1.0",
          "type": "xsd:float"
        },
        {
          "$": "true",
          "type": "xsd:boolean"
        },
        {
          "$": "ex:london",
          "type": "xsd:QName"
        },
        {
          "$": "2014-06-23T12:28:53.858+01:00",
          "type": "xsd:dateTime"
        },
        {
          "$": "http://example.org/london",
          "type": "xsd:anyURI"
        },
        {
          "$": "2002",
          "type": "xsd:gYear"
        }
      ],
      "prov:label": "activity6"
    }
  }
}
'''

# r = requests.get('https://provenance.ecs.soton.ac.uk/store/documents/29316.json')
# json_content = r.text
# doc = ProvDocument.deserialize(content=json_content)
# e = doc.flattened().get_record('crowdreport/166')
# doc = ProvDocument(e)
# json_content = doc.serialize(encoding='utf8')
# print json_content

# json_content = '{"prefix": {"default": "https://provenance.ecs.soton.ac.uk/atomicorchid/data/12/", "ao": "https://provenance.ecs.soton.ac.uk/atomicorchid/ns#"}, "entity": {"crowdreport/166": {"ao:report": "please help a mom rescue her children who are still alive\u001a??", "ao:name": "crowdreporter_4", "ao:latitude": "221.0", "ao:longitude": "283.0"}}}'

# doc = ProvDocument.deserialize(content=json_content)
doc = ProvDocument.deserialize('prov/tests/json/attr_association_one_role_attr44.json')
print(doc.get_provn())

# dot = prov_to_dot(doc)
#
# dot.write_raw('test.dot')

# prov_doc = ProvDocument()
# ex = Namespace('ex', 'http://www.example.org/')
# prov_doc.add_namespace(ex)
# ex1 = Namespace('ex1', 'http://www.example1.org/')  # ex1 is not added to the document
#
# an_xsd_qname = XSDQName(ex['a_value'])
# another_xsd_qname = XSDQName(ex1['another_value'])
#
# e1 = prov_doc.entity('ex:e1', {'prov:value': an_xsd_qname, 'prov:type': another_xsd_qname})
# for _, attr_value in e1.attributes:
#     print isinstance(attr_value, XSDQName)
#
# xml_content = prov_doc.serialize(format='xml')
# new_doc = ProvDocument.deserialize(content=xml_content, format='xml')
# print new_doc.get_provn()
# print new_doc == prov_doc

# entity(ex:e1, [prov:type="ex1:another_value" %% xsd:QName, prov:value="ex:a_value" %% xsd:QName])
# entity(ex:e1, [prov:type='ex1:another_value', prov:value='ex:a_value'])