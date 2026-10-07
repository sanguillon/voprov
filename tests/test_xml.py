"""XML serialization: standard PROV-XML, read back identical by voprov and readable by any PROV-XML tool."""
import datetime
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
from lxml import etree

import prov.model as pm
from prov.identifier import Identifier
from prov.serializers.provxml import ProvXMLException

from voprov.model import VOProvDocument
from voprov.model import records as r

LEGACY_FILE = Path(__file__).parent / "data" / "reference_legacy.xml"
PROV = "http://www.w3.org/ns/prov#"
VOPROV = "http://www.ivoa.net/documents/ProvenanceDM/index.html#"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
EX = "http://example.org/"


def written(doc):
    return etree.fromstring(doc.serialize(format="xml").encode("utf-8"))


def prov_element(parent, name, identifier=None):
    """Elements of PROV-XML with this name (and this prov:id)."""
    found = parent.findall("{%s}%s" % (PROV, name))
    if identifier is not None:
        found = [e for e in found if e.get("{%s}id" % PROV) == identifier]
    return found


def types_of(element):
    return [t.text for t in element.findall("{%s}type" % PROV)]


def xml_with(body, extra=""):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<prov:document xmlns:prov="%s" xmlns:xsi="%s" xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
            'xmlns:ex="%s" xmlns:voprov="%s">%s</prov:document>' % (PROV, XSI, EX, VOPROV, body))


def marker(name):
    return '<prov:type xsi:type="xsd:QName">voprov:%s</prov:type>' % name


# -- Format ---------------------------------------------------------------------------------------------------------

def test_the_file_is_standard_prov_xml(reference_doc):
    root = written(reference_doc)
    assert root.tag == "{%s}document" % PROV
    # every record is an element of the PROV namespace, and so are the id and ref attributes of PROV-XML
    for element in root:
        assert etree.QName(element).namespace == PROV, element.tag
    for element in root.iter():
        for name in element.attrib:
            assert not name.startswith("{%s}" % VOPROV), (element.tag, name)
    assert len(prov_element(root, "bundleContent")) == 1


def test_voprov_elements_are_entities_marked_with_their_type(reference_doc):
    root = written(reference_doc)
    expected = {"ex:v1": "ValueEntity", "ex:ds1": "DatasetEntity", "ex:cf1": "ConfigFile", "ex:p1": "Parameter",
                "ex:ad1": "ActivityDescription", "ex:ud1": "UsageDescription", "ex:pd1": "ParameterDescription"}
    for identifier, name in expected.items():
        (element,) = prov_element(root, "entity", identifier)
        assert "voprov:" + name in types_of(element), identifier
        assert element.find("{%s}type" % PROV).get("{%s}type" % XSI) == "xsd:QName"


def test_records_that_prov_has_are_written_as_before(reference_doc):
    """No marker on the VOProv records that are PROV records: that part of the file is the PROV-XML of any tool."""
    root = written(reference_doc)
    (entity,) = prov_element(root, "entity", "ex:e1")
    assert types_of(entity) == []
    assert not any(types_of(e) for e in prov_element(root, "activity") + prov_element(root, "agent"))
    assert not any(types_of(e) for e in prov_element(root, "used") + prov_element(root, "wasGeneratedBy"))
    (usage,) = prov_element(root, "used", "ex:u1")
    assert usage.find("{%s}activity" % PROV).get("{%s}ref" % PROV) == "ex:a1"
    assert usage.find("{%s}role" % PROV).text == "input"
    # the subtypes of PROV-XML are written with their own element, as in prov
    assert prov_element(root, "wasRevisionOf") and prov_element(root, "wasQuotedFrom")


def test_voprov_relations_are_influences_marked_with_their_type(reference_doc):
    influences = prov_element(written(reference_doc), "wasInfluencedBy")
    by_type = {}
    for influence in influences:
        for t in types_of(influence):
            by_type.setdefault(t, []).append(influence)
    ends = set()
    for influence in by_type["voprov:DescriptionRelation"]:
        ends.add((influence.find("{%s}influencee" % PROV).get("{%s}ref" % PROV),
                  influence.find("{%s}influencer" % PROV).get("{%s}ref" % PROV)))
    assert ("ex:a1", "ex:ad1") in ends and ("ex:e1", "ex:ed1") in ends
    configured = by_type["voprov:ConfigurationRelation"]
    assert {c.find("{%s}artefactType" % VOPROV).text for c in configured} == {"Parameter", "ConfigFile"}
    assert {"voprov:RelatedToRelation", "voprov:HadReference"} <= set(by_type)


def test_bundle_content_is_marked_too(doc):
    doc.bundle("ex:b").valueEntity("ex:v", 3, name="in a bundle")
    (bundle,) = prov_element(written(doc), "bundleContent")
    assert bundle.get("{%s}id" % PROV) == "ex:b"
    assert "voprov:ValueEntity" in types_of(prov_element(bundle, "entity", "ex:v")[0])
    assert VOProvDocument.deserialize(content=doc.serialize(format="xml"), format="xml") == doc


# -- Reading --------------------------------------------------------------------------------------------------------

def test_roundtrip(reference_doc):
    again = VOProvDocument.deserialize(content=reference_doc.serialize(format="xml"), format="xml")
    assert again == reference_doc
    assert len(again.records) == len(reference_doc.records)
    assert len(again.bundles) == len(reference_doc.bundles)
    assert {type(rec) for rec in again.records} == {type(rec) for rec in reference_doc.records}
    assert any(isinstance(rec, r.VOProvValueEntity) for rec in again.records)
    assert any(isinstance(rec, r.VOProvWasConfiguredBy) for rec in again.records)


def test_the_files_of_the_former_format_are_read(reference_doc):
    """Before, the elements, the id and the ref were in the voprov namespace, with an element for each VOProv record."""
    legacy = etree.fromstring(LEGACY_FILE.read_bytes())
    assert legacy.tag == "{%s}document" % VOPROV  # this is the former format
    assert VOProvDocument.deserialize(content=LEGACY_FILE.read_text(), format="xml") == reference_doc


def test_the_export_to_prov_is_read_back_as_the_same_document(reference_doc):
    """get_w3c() gives a plain prov document, whose XML (with the type of every record) is read as VOProv."""
    exported = reference_doc.get_w3c().serialize(format="xml")
    assert VOProvDocument.deserialize(content=exported, format="xml") == reference_doc


def test_a_marker_in_the_wrong_element_is_only_an_attribute():
    text = xml_with('<prov:activity prov:id="ex:a">%s</prov:activity>' % marker("ValueEntity"))
    record = next(iter(VOProvDocument.deserialize(content=text, format="xml").records))
    assert type(record) is r.VOProvActivity
    assert [str(v) for a, v in record.attributes if a == pm.PROV_TYPE] == ["voprov:ValueEntity"]


def test_the_type_of_a_record_is_not_an_attribute():
    """Some tools write the type of every record (voprov:Entity on an entity): it is redundant."""
    text = xml_with('<prov:entity prov:id="ex:e">%s<prov:type xsi:type="xsd:QName">ex:Kind</prov:type></prov:entity>'
                    % marker("Entity"))
    record = next(iter(VOProvDocument.deserialize(content=text, format="xml").records))
    assert [str(v) for a, v in record.attributes if a == pm.PROV_TYPE] == ["ex:Kind"]


def test_with_two_markers_the_first_is_the_type():
    text = xml_with('<prov:entity prov:id="ex:e">%s%s</prov:entity>' % (marker("DatasetEntity"), marker("ValueEntity")))
    record = next(iter(VOProvDocument.deserialize(content=text, format="xml").records))
    assert type(record) is r.VOProvDataSetEntity
    assert [str(v) for a, v in record.attributes if a == pm.PROV_TYPE] == ["voprov:ValueEntity"]


def test_a_voprov_relation_has_its_identifier_and_attributes(doc):
    doc.description("ex:a", "ex:ad", identifier="ex:d1")
    doc.configuration("ex:a", "ex:p", artefactType="ConfigFile", identifier="ex:c1")
    root = written(doc)
    assert {e.get("{%s}id" % PROV) for e in prov_element(root, "wasInfluencedBy")} == {"ex:d1", "ex:c1"}
    again = VOProvDocument.deserialize(content=doc.serialize(format="xml"), format="xml")
    assert again == doc and {str(rec.identifier) for rec in again.records} == {"ex:d1", "ex:c1"}


def test_value_types(doc):
    doc.add_namespace("other", "http://other.org/ns#")
    values = {
        "ex:int": 3, "ex:float": 0.25, "ex:bool": False, "ex:str": 'text é "quoted" <&>',
        "ex:when": datetime.datetime(2023, 5, 1, 12, 30, tzinfo=datetime.timezone.utc),
        "ex:ref": doc.valid_qualified_name("other:thing"), "ex:uri": Identifier("http://x.org/a b"),
        "ex:lang": pm.Literal("bonjour", langtag="fr"),
        "ex:typed": pm.Literal("42", datatype=doc.valid_qualified_name("other:code")),
    }
    doc.valueEntity("ex:e", 7, other_attributes=dict(values))
    again = VOProvDocument.deserialize(content=doc.serialize(format="xml"), format="xml")
    record = next(iter(again.records))
    assert isinstance(record, r.VOProvValueEntity)
    attributes = {str(k): v for k, v in record.attributes}
    for key, expected in values.items():
        assert attributes[key] == expected and type(attributes[key]) is type(expected), key


def test_multiple_values_and_asserted_types(doc):
    record = doc.valueEntity("ex:e", 7)
    record.add_attributes([("prov:type", doc.valid_qualified_name("ex:Kind")), ("ex:tag", "a"), ("ex:tag", "b")])
    (entity,) = prov_element(written(doc), "entity", "ex:e")
    assert types_of(entity) == ["ex:Kind", "voprov:ValueEntity"]
    assert VOProvDocument.deserialize(content=doc.serialize(format="xml"), format="xml") == doc


def test_identical_anonymous_relations_are_both_kept(doc):
    doc.usage("ex:a", "ex:e")
    doc.usage("ex:a", "ex:e")
    assert len(prov_element(written(doc), "used")) == 2
    assert len(VOProvDocument.deserialize(content=doc.serialize(format="xml"), format="xml").records) == 2


def test_a_file_that_is_not_prov_is_rejected():
    foreign = '<document xmlns="http://example.org/other"><entity/></document>'
    with pytest.raises(ProvXMLException):
        VOProvDocument.deserialize(content=foreign, format="xml")


# -- With other tools -----------------------------------------------------------------------------------------------

def test_prov_reads_the_file(reference_doc, tmp_path):
    """A plain prov, in a process where voprov is not imported, reads the file: the voprov types are prov:type."""
    path = tmp_path / "doc.xml"
    path.write_text(reference_doc.serialize(format="xml"))
    script = textwrap.dedent("""
        import json, sys, warnings
        warnings.simplefilter("ignore")
        import prov.model as pm
        doc = pm.ProvDocument.deserialize(content=open(sys.argv[1]).read(), format="xml")
        assert "voprov" not in sys.modules
        records = list(doc.records) + [rec for b in doc.bundles for rec in b.records]
        types = [str(v) for rec in records for a, v in rec.attributes if a == pm.PROV_TYPE]
        print(json.dumps({"records": len(records), "bundles": len(doc.bundles),
                          "marked": sorted(t for t in types if t == "voprov:ValueEntity")}))
    """)
    result = subprocess.run([sys.executable, "-c", script, str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    seen = json.loads(result.stdout)
    assert seen["records"] == len(reference_doc.records) + sum(len(b.records) for b in reference_doc.bundles)
    assert seen["bundles"] == 1 and seen["marked"] == ["voprov:ValueEntity"]


def test_xml_of_prov_is_read():
    """PROV-XML written by prov gives VOProv records (the elements of PROV-XML are the ones of VOProv too)."""
    prov_doc = pm.ProvDocument()
    prov_doc.add_namespace("ex", "http://example.org/")
    activity = prov_doc.activity("ex:a", datetime.datetime(2023, 1, 1, 10), datetime.datetime(2023, 1, 1, 11))
    e_in, e_out = prov_doc.entity("ex:in"), prov_doc.entity("ex:out", {"prov:type": "ex:Kind"})
    prov_doc.used(activity, e_in, other_attributes={"prov:role": "input"})
    prov_doc.wasGeneratedBy(e_out, activity, datetime.datetime(2023, 1, 1, 10, 30), identifier="ex:g")
    prov_doc.wasDerivedFrom(e_out, e_in)
    prov_doc.agent("ex:ag")
    prov_doc.wasAssociatedWith(activity, "ex:ag", None, None, {"prov:role": "op"})
    again = VOProvDocument.deserialize(content=prov_doc.serialize(format="xml"), format="xml")
    assert len(again.records) == len(prov_doc.records)
    assert {type(rec) for rec in again.records} <= {
        r.VOProvActivity, r.VOProvEntity, r.VOProvAgent, r.VOProvUsage, r.VOProvGeneration, r.VOProvDerivation,
        r.VOProvAssociation}
    assert {str(rec.identifier) for rec in again.records} == {str(rec.identifier) for rec in prov_doc.records}
