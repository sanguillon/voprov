import io

import pytest

import voprov
from voprov import serializers
from voprov.model import VOProvDocument


def test_registry_lists_formats():
    serializers.Registry.load_serializers()
    assert set(serializers.Registry.serializers) == {"json", "rdf", "provn", "xml", "yaml"}


def test_unknown_format(doc):
    with pytest.raises(serializers.DoNotExist):
        doc.serialize(format="nope")


@pytest.mark.parametrize("fmt", ["json", "provn", "xml"])
def test_serialize_to_string(reference_doc, fmt):
    content = reference_doc.serialize(format=fmt)
    assert isinstance(content, str) and "voprov" in content


def test_serialize_to_stream_and_file(reference_doc, tmp_path):
    stream = io.StringIO()
    reference_doc.serialize(stream, format="json")
    assert stream.getvalue() == reference_doc.serialize(format="json")
    path = tmp_path / "doc.json"
    reference_doc.serialize(str(path), format="json")
    assert path.read_text() == reference_doc.serialize(format="json")


def test_json_roundtrip(reference_doc):
    content = reference_doc.serialize(format="json")
    again = VOProvDocument.deserialize(content=content, format="json")
    assert isinstance(again, VOProvDocument)
    assert again == reference_doc
    assert len(again.records) == len(reference_doc.records)
    assert len(again.bundles) == len(reference_doc.bundles)


def test_json_roundtrip_keeps_record_classes(reference_doc):
    again = VOProvDocument.deserialize(content=reference_doc.serialize(format="json"), format="json")
    assert {type(rec) for rec in again.records} == {type(rec) for rec in reference_doc.records}


def test_deserialize_from_file_and_stream(reference_doc, tmp_path):
    path = tmp_path / "doc.json"
    reference_doc.serialize(str(path), format="json")
    assert VOProvDocument.deserialize(source=str(path), format="json") == reference_doc
    with open(path) as f:
        assert VOProvDocument.deserialize(source=f, format="json") == reference_doc


def test_read_guesses_format(reference_doc, tmp_path):
    path = tmp_path / "doc.json"
    reference_doc.serialize(str(path), format="json")
    assert voprov.read(str(path)) == reference_doc
    assert voprov.read(str(path), format="JSON") == reference_doc


def test_read_unreadable_source(tmp_path):
    path = tmp_path / "garbage.txt"
    path.write_text("not provenance at all")
    with pytest.raises(TypeError):
        voprov.read(str(path))


def test_provn_mentions_voprov_records(reference_doc):
    provn = reference_doc.serialize(format="provn")
    for keyword in ("activityDescription(", "valueEntity(", "datasetEntity(", "isDescribedBy(",
                    "wasConfiguredBy(", "hadReference("):
        assert keyword in provn


def test_xml_declares_voprov_namespace(reference_doc):
    xml = reference_doc.serialize(format="xml")
    assert "http://www.ivoa.net/documents/ProvenanceDM/index.html#" in xml


def test_w3c_export_is_readable_by_plain_prov(reference_doc):
    """The prov-only view of a voprov document can be serialized and read back by prov itself."""
    import prov.model as pm
    w3c_json = reference_doc.get_w3c().serialize(format="json")
    assert "voprov" in w3c_json
    back = pm.ProvDocument.deserialize(content=w3c_json, format="json")
    assert len(back.records) == len(reference_doc.get_w3c().records)


# Known problems, tracked as strict expected failures: they start failing the suite once fixed,
# so the marker has to be removed.

@pytest.mark.xfail(strict=True, reason="XML deserializer rejects voprov elements")
def test_xml_roundtrip(reference_doc):
    again = VOProvDocument.deserialize(content=reference_doc.serialize(format="xml"), format="xml")
    assert again == reference_doc


@pytest.mark.xfail(strict=True, reason="VOProvYAMLSerializer does not implement deserialize")
def test_yaml_serialization(reference_doc):
    assert reference_doc.serialize(format="yaml")


@pytest.mark.xfail(strict=True, reason="RDF serializer has no mapping for voprov attributes (artefactType)")
def test_rdf_serialization(reference_doc):
    assert reference_doc.serialize(format="rdf")
