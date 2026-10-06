import datetime

import pytest

from voprov import constants as c
from voprov.model import records as r

ELEMENTS = [
    (lambda d: d.entity("ex:e"), r.VOProvEntity, c.VOPROV_ENTITY),
    (lambda d: d.valueEntity("ex:v", 3.5), r.VOProvValueEntity, c.VOPROV_VALUE_ENTITY),
    (lambda d: d.datasetEntity("ex:ds"), r.VOProvDataSetEntity, c.VOPROV_DATASET_ENTITY),
    (lambda d: d.configFile("ex:cf", "conf", "/conf.txt"), r.VOProvConfigFile, c.VOPROV_CONFIGURATION_FILE),
    (lambda d: d.parameter("ex:p", "threshold", 5), r.VOProvParameter, c.VOPROV_CONFIGURATION_PARAMETER),
    (lambda d: d.activity("ex:a"), r.VOProvActivity, c.VOPROV_ACTIVITY),
    (lambda d: d.agent("ex:ag"), r.VOProvAgent, c.VOPROV_AGENT),
    (lambda d: d.activityDescription("ex:ad", "Calibrate"), r.VOProvActivityDescription,
     c.VOPROV_ACTIVITY_DESCRIPTION),
    (lambda d: d.entityDescription("ex:ed", "Raw"), r.VOProvEntityDescription, c.VOPROV_ENTITY_DESCRIPTION),
    (lambda d: d.valueDescription("ex:vd", "Offset", "float"), r.VOProvValueDescription,
     c.VOPROV_VALUE_DESCRIPTION),
    (lambda d: d.datasetDescription("ex:dd", "Image", "fits"), r.VOProvDataSetDescription,
     c.VOPROV_DATASET_DESCRIPTION),
    (lambda d: d.usageDescription("ex:ud", "ex:ad", "input"), r.VOProvUsageDescription,
     c.VOPROV_USAGE_DESCRIPTION),
    (lambda d: d.generationDescription("ex:gd", "ex:ad", "output"), r.VOProvGenerationDescription,
     c.VOPROV_GENERATION_DESCRIPTION),
    (lambda d: d.configFileDescription("ex:cfd", "ex:ad", "conf", "text"), r.VOProvConfigFileDescription,
     c.VOPROV_CONFIG_FILE_DESCRIPTION),
    (lambda d: d.parameterDescription("ex:pd", "ex:ad", "threshold", "float"), r.VOProvParameterDescription,
     c.VOPROV_PARAMETER_DESCRIPTION),
]

RELATIONS = [
    (lambda d: d.usage("ex:a", "ex:e"), r.VOProvUsage, c.VOPROV_USAGE),
    (lambda d: d.generation("ex:e", "ex:a"), r.VOProvGeneration, c.VOPROV_GENERATION),
    (lambda d: d.start("ex:a"), r.VOProvStart, c.VOPROV_START),
    (lambda d: d.end("ex:a"), r.VOProvEnd, c.VOPROV_END),
    (lambda d: d.invalidation("ex:e"), r.VOProvInvalidation, c.VOPROV_INVALIDATION),
    (lambda d: d.communication("ex:a", "ex:b"), r.VOProvCommunication, c.VOPROV_COMMUNICATION),
    (lambda d: d.attribution("ex:e", "ex:ag"), r.VOProvAttribution, c.VOPROV_ATTRIBUTION),
    (lambda d: d.association("ex:a", "ex:ag"), r.VOProvAssociation, c.VOPROV_ASSOCIATION),
    (lambda d: d.delegation("ex:ag", "ex:ag2"), r.VOProvDelegation, c.VOPROV_DELEGATION),
    (lambda d: d.influence("ex:e", "ex:e2"), r.VOProvInfluence, c.VOPROV_INFLUENCE),
    (lambda d: d.derivation("ex:e", "ex:e2"), r.VOProvDerivation, c.VOPROV_DERIVATION),
    (lambda d: d.revision("ex:e", "ex:e2"), r.VOProvDerivation, c.VOPROV_DERIVATION),
    (lambda d: d.quotation("ex:e", "ex:e2"), r.VOProvDerivation, c.VOPROV_DERIVATION),
    (lambda d: d.primary_source("ex:e", "ex:e2"), r.VOProvDerivation, c.VOPROV_DERIVATION),
    (lambda d: d.specialization("ex:e", "ex:e2"), r.VOProvSpecialization, c.VOPROV_SPECIALIZATION),
    (lambda d: d.alternate("ex:e", "ex:e2"), r.VOProvAlternate, c.VOPROV_ALTERNATE),
    (lambda d: d.membership("ex:coll", "ex:e"), r.VOProvMembership, c.VOPROV_MEMBERSHIP),
    (lambda d: d.description("ex:a", "ex:ad"), r.VOProvIsDescribedBy, c.VOPROV_DESCRIPTION_RELATION),
    (lambda d: d.configuration("ex:a", "ex:p"), r.VOProvWasConfiguredBy, c.VOPROV_CONFIGURATION_RELATION),
    (lambda d: d.relate("ex:e", "ex:e2"), r.VOProvIsRelatedTo, c.VOPROV_RELATED_TO_RELATION),
    (lambda d: d.reference("ex:e", "ex:e2"), r.VOProvHadReference, c.VOPROV_REFERENCE_RELATION),
]


@pytest.mark.parametrize("build, cls, prov_type", ELEMENTS + RELATIONS)
def test_builder_creates_voprov_record(doc, build, cls, prov_type):
    record = build(doc)
    assert type(record) is cls
    assert record.get_type() == prov_type
    assert record in doc.records


def test_prov_style_aliases(doc):
    """prov's PROV-N style names are still available and build voprov records."""
    assert type(doc.wasGeneratedBy("ex:e", "ex:a")) is r.VOProvGeneration
    assert type(doc.used("ex:a", "ex:e")) is r.VOProvUsage
    assert type(doc.wasAttributedTo("ex:e", "ex:ag")) is r.VOProvAttribution
    assert type(doc.wasAssociatedWith("ex:a", "ex:ag")) is r.VOProvAssociation
    assert type(doc.wasDerivedFrom("ex:e", "ex:e2")) is r.VOProvDerivation
    assert type(doc.wasInformedBy("ex:a", "ex:b")) is r.VOProvCommunication


def attribute(record, qname):
    values = record.get_attribute(qname)
    return next(iter(values)) if values else None


def test_activity_attributes(doc):
    a = doc.activity("ex:a", name="cal run", startTime="2023-01-01T10:00:00",
                     endTime=datetime.datetime(2023, 1, 1, 11), comment="a run")
    assert attribute(a, c.VOPROV_ATTR_NAME) == "cal run"
    assert attribute(a, c.VOPROV_ATTR_STARTTIME) == datetime.datetime(2023, 1, 1, 10)
    assert attribute(a, c.VOPROV_ATTR_ENDTIME) == datetime.datetime(2023, 1, 1, 11)
    assert attribute(a, c.VOPROV["comment"]) == "a run"


def test_entity_attributes(doc):
    e = doc.entity("ex:e", name="raw", location="/data/raw", comment="c")
    assert attribute(e, c.VOPROV_ATTR_NAME) == "raw"
    assert attribute(e, c.VOPROV["location"]) == "/data/raw"
    assert attribute(e, c.VOPROV["comment"]) == "c"


def test_agent_attributes(doc):
    ag = doc.agent("ex:ag", name="Alice", type="Person", email="a@x.org", affiliation="Obs")
    assert attribute(ag, c.VOPROV_ATTR_NAME) == "Alice"
    assert attribute(ag, c.VOPROV["email"]) == "a@x.org"
    assert attribute(ag, c.VOPROV["affiliation"]) == "Obs"


def test_value_entity_and_parameter(doc):
    v = doc.valueEntity("ex:v", 3.5, name="offset")
    assert attribute(v, c.VOPROV["value"]) == 3.5
    p = doc.parameter("ex:p", "threshold", 5)
    assert attribute(p, c.VOPROV_ATTR_VALUE) == 5
    assert attribute(p, c.VOPROV_ATTR_NAME) == "threshold"


def test_usage_attributes(doc):
    u = doc.usage("ex:a", "ex:e", role="input", time="2023-01-01T10:01:00", identifier="ex:u1")
    assert str(u.identifier) == "ex:u1"
    assert attribute(u, c.VOPROV_ATTR_ROLE) == "input"
    assert attribute(u, c.VOPROV_ATTR_TIME) == datetime.datetime(2023, 1, 1, 10, 1)
    assert str(attribute(u, c.VOPROV_ATTR_ACTIVITY)) == "ex:a"
    assert str(attribute(u, c.VOPROV_ATTR_ENTITY)) == "ex:e"


def test_description_attributes(doc):
    ad = doc.activityDescription("ex:ad", "Calibrate", version="1.0", description="d", docurl="http://doc")
    assert attribute(ad, c.VOPROV_ATTR_NAME) == "Calibrate"
    assert attribute(ad, c.VOPROV["version"]) == "1.0"
    assert attribute(ad, c.VOPROV["docurl"]) == "http://doc"


def test_set_methods(doc):
    e = doc.entity("ex:e")
    e.set_name("renamed")
    e.set_location("/somewhere")
    assert attribute(e, c.VOPROV_ATTR_NAME) == "renamed"
    assert attribute(e, c.VOPROV["location"]) == "/somewhere"
    a = doc.activity("ex:a")
    a.set_time(startTime=datetime.datetime(2023, 5, 1))
    assert attribute(a, c.VOPROV_ATTR_STARTTIME) == datetime.datetime(2023, 5, 1)


@pytest.mark.xfail(strict=True, reason="set_time keeps strings as is, although its docstring says they are parsed "
                                       "(the activity() builder does parse them)")
def test_set_time_parses_strings(doc):
    a = doc.activity("ex:a")
    a.set_time(startTime="2023-05-01T00:00:00")
    assert attribute(a, c.VOPROV_ATTR_STARTTIME) == datetime.datetime(2023, 5, 1)


def test_is_described_by(doc):
    """Activity.isDescribedBy links an activity to its description."""
    a = doc.activity("ex:a")
    doc.activityDescription("ex:ad", "Calibrate")
    link = a.isDescribedBy("ex:ad")
    assert type(link) is r.VOProvIsDescribedBy


def test_ensure_datetime():
    from voprov.model.bundle import _ensure_datetime
    now = datetime.datetime(2023, 1, 1)
    assert _ensure_datetime(now) is now
    assert _ensure_datetime("2023-01-01") == now
    assert _ensure_datetime(None) is None
