
from prov.tests.examples import primer_example

doc = primer_example()


def test_jsonld():
    doc = primer_example()
    doc.serialize(format='jsonld')


def test_jsonlds():
    doc = primer_example()
    doc.serialize(format='jsonlds')