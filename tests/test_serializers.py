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


def test_xml_roundtrip(reference_doc):
    again = VOProvDocument.deserialize(content=reference_doc.serialize(format="xml"), format="xml")
    assert isinstance(again, VOProvDocument)
    assert again == reference_doc
    assert len(again.records) == len(reference_doc.records)
    assert len(again.bundles) == len(reference_doc.bundles)
    assert {type(rec) for rec in again.records} == {type(rec) for rec in reference_doc.records}


def test_xml_roundtrip_through_file(reference_doc, tmp_path):
    path = tmp_path / "doc.xml"
    reference_doc.serialize(str(path), format="xml")
    assert VOProvDocument.deserialize(source=str(path), format="xml") == reference_doc
    assert voprov.read(str(path)) == reference_doc


def test_xml_keeps_value_types(doc):
    import datetime
    doc.entity("ex:e", other_attributes={"ex:count": 3, "ex:ratio": 0.5, "ex:flag": True,
                                         "ex:when": datetime.datetime(2023, 1, 1, 12), "ex:label": "text é"})
    again = VOProvDocument.deserialize(content=doc.serialize(format="xml"), format="xml")
    values = {str(k): v for k, v in next(iter(again.records)).attributes}
    assert values["ex:count"] == 3 and isinstance(values["ex:count"], int)
    assert values["ex:ratio"] == 0.5
    assert values["ex:flag"] is True
    assert values["ex:when"] == datetime.datetime(2023, 1, 1, 12)
    assert values["ex:label"] == "text é"


def test_xml_keeps_bundle_contents(doc):
    doc.bundle("ex:b").entity("ex:inside", name="in bundle")
    again = VOProvDocument.deserialize(content=doc.serialize(format="xml"), format="xml")
    bundle = next(iter(again.bundles))
    assert str(bundle.identifier) == "ex:b"
    assert [str(rec.identifier) for rec in bundle.records] == ["ex:inside"]


def test_xml_rejects_other_namespaces():
    from prov.serializers.provxml import ProvXMLException
    foreign = '<document xmlns="http://example.org/other"><entity/></document>'
    with pytest.raises(ProvXMLException):
        VOProvDocument.deserialize(content=foreign, format="xml")


def test_yaml_is_a_readable_summary(reference_doc):
    import yaml
    content = reference_doc.serialize(format="yaml")
    data = yaml.safe_load(content)
    assert {"entity", "activity", "agent", "activity_description", "entity_description"} <= set(data)
    assert data["activity"]["ex:a1"]["name"] == "cal run"
    assert data["activity"]["ex:a1"]["used"] == "ex:e1"
    assert data["activity"]["ex:a1"]["generated"] == "ex:e2"
    assert data["activity"]["ex:a1"]["parameters"] == {"threshold": 5}
    assert data["agent"]["ex:ag1"]["name"] == "Alice"
    assert data["entity"]["ex:e2"]["attributed"] == {"ex:ag1": {"role": "author"}}


def test_yaml_to_text_stream(reference_doc):
    stream = io.StringIO()
    reference_doc.serialize(stream, format="yaml")
    assert stream.getvalue() == reference_doc.serialize(format="yaml")


def test_yaml_handles_relations_without_elements(doc):
    """A usage whose activity has no attributes, or is not in the document, must not break the export."""
    import yaml
    doc.usage("ex:a", "ex:e1")
    doc.usage("ex:a", "ex:e2")
    doc.activity("ex:bare")
    doc.generation("ex:e3", "ex:bare")
    data = yaml.safe_load(doc.serialize(format="yaml"))
    assert data["activity"]["ex:a"]["used"] == ["ex:e1", "ex:e2"]
    assert data["activity"]["ex:bare"]["generated"] == "ex:e3"


def test_yaml_cannot_be_read_back(reference_doc):
    """The YAML export is a summary, not a complete representation."""
    with pytest.raises(NotImplementedError):
        VOProvDocument.deserialize(content=reference_doc.serialize(format="yaml"), format="yaml")


# Known problem, tracked as a strict expected failure: it starts failing the suite once fixed,
# so the marker has to be removed.

@pytest.mark.xfail(strict=True, reason="RDF: voprov attributes are not mapped (artefactType), voprov relations are "
                                       "written in the prov namespace and are lost when reading back")
def test_rdf_roundtrip(reference_doc):
    again = VOProvDocument.deserialize(content=reference_doc.serialize(format="rdf"), format="rdf")
    assert again == reference_doc
