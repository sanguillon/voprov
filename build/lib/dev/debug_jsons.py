import subprocess
from rdflib import Graph, ConjunctiveGraph
from prov.tests.examples import primer_example, bundles1
from prov.model import ProvDocument, PROV_AGENT

doc = ProvDocument.deserialize('/Users/tdh/Downloads/history.json')
# doc.serialize('bindings20_v2.json-ld.json', format='jsonld', indent=2)


class ProvConvertException(Exception):
    def __init__(self, msg=None):
        self.msg = msg


def provconvert(content, toextension, fromextension='json'):
    stderr = None
    try:
        p = subprocess.Popen(
                [
                    '/usr/local/bin/provconvert',
                    '-infile', '-', '-informat', fromextension,
                    '-outfile', '-', '-outformat', toextension
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
        )
        p.stdin.write(content.encode('utf8'))
        stdout, stderr = p.communicate()
        return stdout
    except IOError as e:
        # The output file cannot be read, reporting any error
        raise ProvConvertException(stderr)

doc1 = primer_example()
doc1.serialize('primer.json', format='jsonld', indent=2)
json_str = doc1.serialize(format='jsonld')
g = Graph().parse(data=json_str, format='json-ld')
g2 = ConjunctiveGraph(store=g.store)
ttl_content = g2.serialize(format='turtle')
converted_provjson = provconvert(ttl_content, 'json', 'ttl')
doc2 = ProvDocument.deserialize(content=converted_provjson)

assert(doc1 == doc2)

primer_example().serialize(format='jsonlds', beautify=True)

bundles1().serialize('bundles1.json', format='jsonld', indent=2)
json_str = bundles1().serialize(format='jsonld')
g = Graph().parse(data=json_str, format='json-ld')
g2 = ConjunctiveGraph(store=g.store)
g2.serialize('bundles1.trig', format='trig')


doc1 = ProvDocument(namespaces={'ex': 'http://www.example.com/'})
doc1.entity('ex:e1', {'prov:type': PROV_AGENT})
doc1.wasGeneratedBy('ex:e1', 'ex:a1')
print(doc1.serialize(format='jsonld', indent=2))
