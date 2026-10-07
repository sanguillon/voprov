"""JSON serialization: standard PROV-JSON, read back identical by voprov and readable by any PROV-JSON tool."""
import datetime
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import prov.model as pm
from prov.identifier import Identifier

from voprov.model import VOProvDocument
from voprov.model import records as r

LEGACY_FILE = Path(__file__).parent / "data" / "reference_legacy.json"

#: the sections of PROV-JSON (https://www.w3.org/Submission/prov-json/), plus the prefixes and the bundles
PROV_JSON_SECTIONS = {
    "prefix", "bundle", "entity", "activity", "agent", "wasGeneratedBy", "used", "wasInformedBy", "wasStartedBy",
    "wasEndedBy", "wasInvalidatedBy", "wasDerivedFrom", "wasAttributedTo", "wasAssociatedWith", "actedOnBehalfOf",
    "wasInfluencedBy", "specializationOf", "alternateOf", "mentionOf", "hadMember",
}
QNAME = {"type": "prov:QUALIFIED_NAME"}


def written(doc, **options):
    return json.loads(doc.serialize(format="json", **options))


def records_of(section):
    """The records of a section: an identifier holds a list when several records have it (identical anonymous ones)."""
    return [c for content in section.values() for c in (content if isinstance(content, list) else [content])]


def marker(name, datatype="prov:QUALIFIED_NAME"):
    return {"$": "voprov:" + name, "type": datatype}


# -- Format ---------------------------------------------------------------------------------------------------------

def test_the_file_is_standard_prov_json(reference_doc):
    content = written(reference_doc)
    assert set(content) <= PROV_JSON_SECTIONS
    assert set(content["bundle"]["ex:b1"]) <= PROV_JSON_SECTIONS


def test_voprov_elements_are_entities_marked_with_their_type(reference_doc):
    entities = written(reference_doc)["entity"]
    assert entities["ex:v1"]["prov:type"] == marker("ValueEntity")
    assert entities["ex:ds1"]["prov:type"] == marker("DatasetEntity")
    assert entities["ex:cf1"]["prov:type"] == marker("ConfigFile")
    assert entities["ex:p1"]["prov:type"] == marker("Parameter")
    assert entities["ex:ad1"]["prov:type"] == marker("ActivityDescription")
    assert entities["ex:ud1"]["prov:type"] == marker("UsageDescription")
    assert entities["ex:pd1"]["prov:type"] == marker("ParameterDescription")


def test_records_that_prov_json_has_are_written_as_before(reference_doc):
    """No marker on the VOProv records that are PROV records: the file has the PROV-JSON of the PROV part."""
    content = written(reference_doc)
    assert "prov:type" not in content["entity"]["ex:e1"]
    assert "prov:type" not in content["activity"]["ex:a1"]
    assert "prov:type" not in content["agent"]["ex:ag1"]
    assert all("prov:type" not in u for u in records_of(content["used"]))
    assert content["used"]["ex:u1"]["prov:role"] == "input"
    # the asserted types are the ones of the record, nothing more
    assert content["entity"]["ex:coll1"]["prov:type"] == {"$": "voprov:Collection", **QNAME}


def test_voprov_relations_are_influences_marked_with_their_type(reference_doc):
    influences = written(reference_doc)["wasInfluencedBy"]
    by_type = {}
    for content in records_of(influences):
        types = content.get("prov:type", [])
        for t in (types if isinstance(types, list) else [types]):
            by_type.setdefault(t["$"], []).append(content)
    described = {(c["prov:influencee"], c["prov:influencer"]) for c in by_type["voprov:DescriptionRelation"]}
    assert ("ex:a1", "ex:ad1") in described and ("ex:e1", "ex:ed1") in described
    configured = by_type["voprov:ConfigurationRelation"]
    assert {c["voprov:artefactType"] for c in configured} == {"Parameter", "ConfigFile"}
    assert {"voprov:RelatedToRelation", "voprov:HadReference"} <= set(by_type)
    # a plain influence is not marked
    assert any("prov:type" not in c for c in records_of(influences))


def test_bundle_content_is_marked_too(doc):
    doc.bundle("ex:b").valueEntity("ex:v", 3, name="in a bundle")
    content = written(doc)
    assert content["bundle"]["ex:b"]["entity"]["ex:v"]["prov:type"] == marker("ValueEntity")
    assert VOProvDocument.deserialize(content=doc.serialize(format="json"), format="json") == doc


# -- Reading --------------------------------------------------------------------------------------------------------

def test_roundtrip(reference_doc):
    again = VOProvDocument.deserialize(content=reference_doc.serialize(format="json"), format="json")
    assert again == reference_doc
    assert len(again.records) == len(reference_doc.records)
    assert len(again.bundles) == len(reference_doc.bundles)
    assert {type(rec) for rec in again.records} == {type(rec) for rec in reference_doc.records}
    assert any(isinstance(rec, r.VOProvValueEntity) for rec in again.records)
    assert any(isinstance(rec, r.VOProvWasConfiguredBy) for rec in again.records)


def test_the_files_of_the_former_format_are_read(reference_doc):
    """Before, each VOProv record had a section of its own (valueEntity, isDescribedBy, ...)."""
    legacy = json.loads(LEGACY_FILE.read_text())
    assert not set(legacy) <= PROV_JSON_SECTIONS  # this is the former format
    assert VOProvDocument.deserialize(content=LEGACY_FILE.read_text(), format="json") == reference_doc


def test_the_export_to_prov_is_read_back_as_the_same_document(reference_doc):
    """get_w3c() gives a plain prov document, whose JSON (with the type of every record) is read as VOProv."""
    exported = reference_doc.get_w3c().serialize(format="json")
    assert VOProvDocument.deserialize(content=exported, format="json") == reference_doc


@pytest.mark.parametrize("datatype", ["prov:QUALIFIED_NAME", "xsd:QName"])
def test_both_spellings_of_a_qualified_name_are_read(datatype):
    """prov 2 writes prov:QUALIFIED_NAME, and the PROV-JSON specification (and prov 3) xsd:QName."""
    text = json.dumps({"prefix": {"ex": "http://example.org/"},
                       "entity": {"ex:v": {"voprov:value": 3, "prov:type": marker("ValueEntity", datatype)}}})
    doc = VOProvDocument.deserialize(content=text, format="json")
    record = next(iter(doc.records))
    assert isinstance(record, r.VOProvValueEntity)
    assert pm.PROV_TYPE not in [attr for attr, _ in record.attributes]


def test_a_marker_in_the_wrong_section_is_only_an_attribute():
    text = json.dumps({"prefix": {"ex": "http://example.org/"},
                       "activity": {"ex:a": {"prov:type": marker("ValueEntity")}}})
    record = next(iter(VOProvDocument.deserialize(content=text, format="json").records))
    assert type(record) is r.VOProvActivity
    assert [str(v) for a, v in record.attributes if a == pm.PROV_TYPE] == ["voprov:ValueEntity"]


def test_the_type_of_a_record_is_not_an_attribute():
    """Some tools write the type of every record (voprov:Entity on an entity): it is redundant."""
    text = json.dumps({"prefix": {"ex": "http://example.org/"},
                       "entity": {"ex:e": {"prov:name": "x", "prov:type": [marker("Entity"), marker("Kind")]}}})
    record = next(iter(VOProvDocument.deserialize(content=text, format="json").records))
    assert [str(v) for a, v in record.attributes if a == pm.PROV_TYPE] == ["voprov:Kind"]


def test_with_two_markers_the_first_is_the_type():
    text = json.dumps({"prefix": {"ex": "http://example.org/"},
                       "entity": {"ex:e": {"prov:type": [marker("DatasetEntity"), marker("ValueEntity")]}}})
    record = next(iter(VOProvDocument.deserialize(content=text, format="json").records))
    assert type(record) is r.VOProvDataSetEntity
    assert [str(v) for a, v in record.attributes if a == pm.PROV_TYPE] == ["voprov:ValueEntity"]


def test_a_voprov_relation_has_its_identifier_and_attributes(doc):
    doc.description("ex:a", "ex:ad", identifier="ex:d1")
    doc.configuration("ex:a", "ex:p", artefactType="ConfigFile", identifier="ex:c1")
    content = written(doc)
    assert set(content["wasInfluencedBy"]) == {"ex:d1", "ex:c1"}
    assert content["wasInfluencedBy"]["ex:c1"]["voprov:artefactType"] == "ConfigFile"
    again = VOProvDocument.deserialize(content=doc.serialize(format="json"), format="json")
    assert again == doc and {str(rec.identifier) for rec in again.records} == {"ex:d1", "ex:c1"}


def test_value_types(doc):
    doc.add_namespace("other", "http://other.org/ns#")
    values = {
        "ex:int": 3, "ex:float": 0.25, "ex:bool": False, "ex:str": 'text é "quoted"',
        "ex:when": datetime.datetime(2023, 5, 1, 12, 30, tzinfo=datetime.timezone.utc),
        "ex:ref": doc.valid_qualified_name("other:thing"), "ex:uri": Identifier("http://x.org/a b"),
        "ex:lang": pm.Literal("bonjour", langtag="fr"),
        "ex:typed": pm.Literal("42", datatype=doc.valid_qualified_name("other:code")),
    }
    doc.valueEntity("ex:e", 7, other_attributes=dict(values))  # the builders add to the dictionary they get
    again = VOProvDocument.deserialize(content=doc.serialize(format="json"), format="json")
    record = next(iter(again.records))
    assert isinstance(record, r.VOProvValueEntity)
    attributes = {str(k): v for k, v in record.attributes}
    for key, expected in values.items():
        assert attributes[key] == expected and type(attributes[key]) is type(expected), key


def test_multiple_values_and_asserted_types(doc):
    record = doc.valueEntity("ex:e", 7)
    record.add_attributes([("prov:type", doc.valid_qualified_name("ex:Kind")), ("ex:tag", "a"), ("ex:tag", "b")])
    content = written(doc)
    assert content["entity"]["ex:e"]["prov:type"][0]["$"] == "ex:Kind"
    assert content["entity"]["ex:e"]["prov:type"][1] == marker("ValueEntity")
    assert VOProvDocument.deserialize(content=doc.serialize(format="json"), format="json") == doc


def test_identical_anonymous_relations_are_both_kept(doc):
    doc.usage("ex:a", "ex:e")
    doc.usage("ex:a", "ex:e")
    assert len(records_of(written(doc)["used"])) == 2
    assert len(VOProvDocument.deserialize(content=doc.serialize(format="json"), format="json").records) == 2


def test_membership_of_several_entities_is_read(doc):
    text = json.dumps({"prefix": {"ex": "http://example.org/"},
                       "hadMember": {"_:id1": {"prov:collection": "ex:c", "prov:entity": ["ex:e1", "ex:e2"]}}})
    again = VOProvDocument.deserialize(content=text, format="json")
    assert sorted(str(dict(rec.formal_attributes)[pm.PROV_ATTR_ENTITY]) for rec in again.records) == ["ex:e1", "ex:e2"]


def test_options_of_json_are_passed(reference_doc):
    text = reference_doc.serialize(format="json", indent=2, sort_keys=True)
    assert text.count("\n") > 50 and list(json.loads(text)) == sorted(json.loads(text))


# -- With other tools -----------------------------------------------------------------------------------------------

def test_prov_reads_the_file(reference_doc, tmp_path):
    """A plain prov, in a process where voprov is not imported, reads the file: the voprov types are prov:type."""
    path = tmp_path / "doc.json"
    path.write_text(reference_doc.serialize(format="json"))
    script = textwrap.dedent("""
        import collections, json, sys, warnings
        warnings.simplefilter("ignore")
        import prov.model as pm
        doc = pm.ProvDocument.deserialize(content=open(sys.argv[1]).read(), format="json")
        assert "voprov" not in sys.modules
        records = list(doc.records) + [rec for b in doc.bundles for rec in b.records]
        types = [str(v) for rec in records for a, v in rec.attributes if a == pm.PROV_TYPE]
        print(json.dumps({"records": len(records), "bundles": len(doc.bundles),
                          "marked": sorted(t for t in types if t.startswith("voprov:ValueEntity"))}))
    """)
    result = subprocess.run([sys.executable, "-c", script, str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    seen = json.loads(result.stdout)
    assert seen["records"] == len(reference_doc.records) + sum(len(b.records) for b in reference_doc.bundles)
    assert seen["bundles"] == 1 and seen["marked"] == ["voprov:ValueEntity"]


def test_json_of_prov_is_read():
    """PROV-JSON written by prov gives VOProv records (the sections of PROV-JSON are the ones of VOProv too)."""
    prov_doc = pm.ProvDocument()
    prov_doc.add_namespace("ex", "http://example.org/")
    activity = prov_doc.activity("ex:a", datetime.datetime(2023, 1, 1, 10), datetime.datetime(2023, 1, 1, 11))
    e_in, e_out = prov_doc.entity("ex:in"), prov_doc.entity("ex:out", {"prov:type": "ex:Kind"})
    prov_doc.used(activity, e_in, other_attributes={"prov:role": "input"})
    prov_doc.wasGeneratedBy(e_out, activity, datetime.datetime(2023, 1, 1, 10, 30), identifier="ex:g")
    prov_doc.wasDerivedFrom(e_out, e_in)
    prov_doc.agent("ex:ag")
    prov_doc.wasAssociatedWith(activity, "ex:ag", None, None, {"prov:role": "op"})
    again = VOProvDocument.deserialize(content=prov_doc.serialize(format="json"), format="json")
    assert len(again.records) == len(prov_doc.records)
    assert {type(rec) for rec in again.records} <= {
        r.VOProvActivity, r.VOProvEntity, r.VOProvAgent, r.VOProvUsage, r.VOProvGeneration, r.VOProvDerivation,
        r.VOProvAssociation}
    assert {str(rec.identifier) for rec in again.records} == {str(rec.identifier) for rec in prov_doc.records}
