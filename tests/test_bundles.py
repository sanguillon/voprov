import pytest
from prov.model import ProvException

from voprov.model import VOProvBundle, VOProvDocument


def test_document_and_bundle_kinds(doc):
    b = doc.bundle("ex:b")
    assert doc.is_document() and not doc.is_bundle()
    assert b.is_bundle() and not b.is_document()
    assert isinstance(b, VOProvBundle)
    assert doc.has_bundles() and list(doc.bundles) == [b]


def test_bundle_requires_identifier(doc):
    with pytest.raises(ProvException):
        doc.bundle(None)


def test_duplicate_bundle_is_rejected(doc):
    doc.bundle("ex:b")
    with pytest.raises(ProvException, match="already exists"):
        doc.bundle("ex:b")


def test_records_in_bundle_are_not_in_document(doc):
    b = doc.bundle("ex:b")
    b.entity("ex:inside")
    doc.entity("ex:outside")
    assert [str(rec.identifier) for rec in doc.records] == ["ex:outside"]
    assert [str(rec.identifier) for rec in b.records] == ["ex:inside"]


def test_add_bundle(doc):
    b = VOProvBundle(identifier=doc.valid_qualified_name("ex:b"), namespaces=doc.namespaces)
    b.entity("ex:inside")
    doc.add_bundle(b)
    assert doc.bundles and str(next(iter(doc.bundles)).identifier) == "ex:b"


def test_add_bundle_without_identifier(doc):
    with pytest.raises(ProvException):
        doc.add_bundle(VOProvBundle())


def test_add_non_bundle(doc):
    with pytest.raises(ProvException):
        doc.add_bundle("not a bundle")


def test_flattened(doc):
    doc.entity("ex:outside")
    doc.bundle("ex:b").entity("ex:inside")
    flat = doc.flattened()
    assert {str(rec.identifier) for rec in flat.records} == {"ex:outside", "ex:inside"}
    assert not flat.has_bundles()


def test_update_merges_records_and_bundles(doc):
    other = VOProvDocument()
    other.add_namespace("ex", "http://example.org/")
    other.entity("ex:other")
    other.bundle("ex:b").entity("ex:inside")
    doc.entity("ex:mine")
    doc.update(other)
    assert {str(rec.identifier) for rec in doc.records} == {"ex:mine", "ex:other"}
    assert len(doc.bundles) == 1


def test_update_rejects_non_documents(doc):
    with pytest.raises(ProvException):
        doc.update("nope")


def test_unified_merges_same_identifier(doc):
    doc.entity("ex:e", name="first")
    doc.entity("ex:e", location="/somewhere")
    assert len(doc.records) == 2
    unified = doc.unified()
    assert isinstance(unified, VOProvDocument)
    assert len(unified.records) == 1


def test_unified_relations_drops_duplicates(doc):
    doc.usage("ex:a", "ex:e")
    doc.usage("ex:a", "ex:e")
    doc.usage("ex:a", "ex:other")
    doc.unified_relations()
    assert len(doc.records) == 2


def test_equality(doc):
    other = VOProvDocument()
    other.add_namespace("ex", "http://example.org/")
    assert doc == other
    doc.entity("ex:e")
    assert doc != other
    other.entity("ex:e")
    assert doc == other
    assert doc != "a string"


def test_bundle_label(doc):
    assert doc.bundle("ex:b", ).label is not None


def test_get_w3c_gives_plain_prov(reference_doc):
    import prov.model as pm
    w3c = reference_doc.get_w3c()
    assert type(w3c) is pm.ProvDocument
    assert all(type(rec).__module__ == "prov.model" for rec in w3c.records)
    assert len(w3c.bundles) == 1
    # voprov concepts are kept as prov:type
    types = {str(t) for rec in w3c.get_records(pm.ProvEntity) for t in rec.get_asserted_types()}
    assert {"voprov:Entity", "voprov:ValueEntity", "voprov:ActivityDescription"} <= types
