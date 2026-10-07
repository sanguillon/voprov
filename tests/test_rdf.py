"""RDF serialization: PROV-O compatible, and complete (a document is read back identical)."""
import datetime
import subprocess
import sys
import textwrap

import pytest

rdflib = pytest.importorskip("rdflib")

import prov.model as pm  # noqa: E402
from prov.identifier import Identifier  # noqa: E402
from rdflib import BNode, Dataset, Namespace, RDF  # noqa: E402
from rdflib.compare import isomorphic  # noqa: E402

import voprov  # noqa: E402
from voprov.model import VOProvDocument  # noqa: E402

PROV = Namespace("http://www.w3.org/ns/prov#")
VOPROV = Namespace("http://www.ivoa.net/documents/ProvenanceDM/index.html#")
EX = Namespace("http://example.org/")


def graphs_of(dataset):
    return list(dataset.graphs()) if hasattr(dataset, "graphs") else list(dataset.contexts())


def read_trig(text):
    dataset = Dataset()
    dataset.parse(data=text, format="trig")
    return dataset


def default_graph(dataset):
    """The graph of the document: rdflib 6 names it with a blank node, rdflib 7 makes it the default graph."""
    return next(g for g in graphs_of(dataset)
                if str(g.identifier) == "urn:x-rdflib:default" and len(g) or isinstance(g.identifier, BNode))


def roundtrip(doc, **options):
    return VOProvDocument.deserialize(content=doc.serialize(format="rdf", **options), format="rdf")


# -- Round trip -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("shortcuts", [True, False])
def test_roundtrip(reference_doc, shortcuts):
    again = roundtrip(reference_doc, shortcuts=shortcuts)
    assert isinstance(again, VOProvDocument)
    assert again == reference_doc
    assert len(again.records) == len(reference_doc.records)
    assert len(again.bundles) == len(reference_doc.bundles)
    assert {type(r) for r in again.records} == {type(r) for r in reference_doc.records}


@pytest.mark.parametrize("rdf_format", ["trig", "nquads", "json-ld"])
def test_formats_with_named_graphs(reference_doc, rdf_format):
    again = VOProvDocument.deserialize(content=reference_doc.serialize(format="rdf", rdf_format=rdf_format),
                                       format="rdf", rdf_format=rdf_format)
    assert again == reference_doc


@pytest.mark.parametrize("rdf_format", ["turtle", "xml", "nt"])
def test_formats_without_named_graphs_merge_the_bundles(reference_doc, rdf_format, caplog):
    content = reference_doc.serialize(format="rdf", rdf_format=rdf_format)
    assert "merged" in caplog.text
    again = VOProvDocument.deserialize(content=content, format="rdf", rdf_format=rdf_format)
    assert again == reference_doc.flattened()


def test_second_serialization_is_the_same_graph(reference_doc):
    """Nothing is lost or added by reading: writing the document read back gives the same graphs."""
    first = read_trig(reference_doc.serialize(format="rdf"))
    second = read_trig(roundtrip(reference_doc).serialize(format="rdf"))
    def by_role(dataset):
        # the document graph is anonymous (a random blank node with rdflib 6), the bundles are named
        return {("document" if str(g.identifier) == "urn:x-rdflib:default" or isinstance(g.identifier, BNode)
                 else str(g.identifier)): g for g in graphs_of(dataset) if len(g)}

    graphs, other = by_role(first), by_role(second)
    assert set(graphs) == set(other) and "document" in graphs and str(EX.b1) in graphs
    for name, graph in graphs.items():
        assert isomorphic(graph, other[name]), name


def test_empty_document(doc):
    again = roundtrip(doc)
    assert again == doc and not again.records


def test_output_is_reproducible(reference_doc):
    """Blank nodes are numbered: the same document gives the same text (useful to follow changes in a repository)."""
    assert reference_doc.serialize(format="rdf") == reference_doc.serialize(format="rdf")
    assert roundtrip(reference_doc).serialize(format="rdf") == reference_doc.serialize(format="rdf")


def test_to_file_and_stream(reference_doc, tmp_path):
    import io
    stream = io.StringIO()
    reference_doc.serialize(stream, format="rdf")
    assert stream.getvalue() == reference_doc.serialize(format="rdf")
    path = tmp_path / "doc.trig"
    reference_doc.serialize(str(path), format="rdf")
    assert VOProvDocument.deserialize(source=str(path), format="rdf") == reference_doc
    assert voprov.read(str(path)) == reference_doc


def test_records_with_the_same_identifier_are_one_resource(doc):
    """In RDF, as in PROV-JSON, two records with one identifier are one resource: unified() merges them."""
    doc.entity("ex:e", name="a")
    doc.entity("ex:e", location="/x")
    assert roundtrip(doc) == doc.unified()


# -- Values ---------------------------------------------------------------------------------------------------------

def test_value_types(doc):
    doc.add_namespace("other", "http://other.org/ns#")
    values = {
        "ex:int": 3, "ex:float": 0.25, "ex:bool": False, "ex:str": 'text é "quoted"\nline 2',
        "ex:when": datetime.datetime(2023, 5, 1, 12, 30, tzinfo=datetime.timezone.utc),
        "ex:naive": datetime.datetime(2023, 5, 1, 12, 30), "ex:date": datetime.date(2023, 5, 1),
        "ex:ref": doc.valid_qualified_name("other:thing"), "ex:uri": Identifier("http://x.org/a b"),
        "ex:lang": pm.Literal("bonjour", langtag="fr"),
        "ex:typed": pm.Literal("42", datatype=doc.valid_qualified_name("other:code")),
    }
    doc.entity("ex:e", other_attributes=values)
    again = {str(k): v for k, v in next(iter(roundtrip(doc).records)).attributes}
    for key, expected in values.items():
        assert again[key] == expected, key
        assert type(again[key]) is type(expected), key


def test_multiple_values_and_asserted_types(doc):
    doc.entity("ex:e", other_attributes=[("prov:type", doc.valid_qualified_name("ex:Kind")),
                                         ("prov:type", "free text"), ("ex:tag", "a"), ("ex:tag", "b")])
    assert roundtrip(doc) == doc


def test_times_roles_and_identifiers_of_relations(doc):
    doc.usage("ex:a", "ex:e", role="input", time="2023-01-01T10:00:00", identifier="ex:u1")
    doc.generation("ex:e2", "ex:a", role="output")
    again = roundtrip(doc)
    assert again == doc
    assert {str(r.identifier) for r in again.records} == {"ex:u1", "None"}


# -- PROV-O ---------------------------------------------------------------------------------------------------------

@pytest.fixture
def written(reference_doc):
    return read_trig(reference_doc.serialize(format="rdf"))


def test_elements_are_prov_o_instances(written):
    graph = default_graph(written)
    assert (EX.e1, RDF.type, PROV.Entity) in graph and (EX.e1, RDF.type, VOPROV.Entity) in graph
    assert (EX.ds1, RDF.type, VOPROV.DatasetEntity) in graph and (EX.ds1, RDF.type, PROV.Entity) in graph
    assert (EX.a1, RDF.type, PROV.Activity) in graph and (EX.a1, RDF.type, VOPROV.Activity) in graph
    assert (EX.ag1, RDF.type, PROV.Agent) in graph
    assert (EX.ad1, RDF.type, VOPROV.ActivityDescription) in graph  # a description is a prov:Entity
    assert (EX.ad1, RDF.type, PROV.Entity) in graph


def test_relations_have_a_shortcut_and_a_qualified_node(written):
    graph = default_graph(written)
    assert (EX.a1, PROV.used, EX.e1) in graph
    assert (EX.e2, PROV.wasGeneratedBy, EX.a1) in graph
    assert (EX.a1, PROV.qualifiedUsage, EX.u1) in graph
    usage = EX.u1
    assert (usage, RDF.type, PROV.Usage) in graph and (usage, RDF.type, VOPROV.Usage) in graph
    assert (usage, PROV.entity, EX.e1) in graph
    assert any(graph.objects(usage, PROV.hadRole)) and any(graph.objects(usage, PROV.atTime))
    # a relation with no identifier is a blank node
    nodes = list(graph.objects(EX.a1, PROV.qualifiedAssociation))
    assert len(nodes) == 1 and isinstance(nodes[0], BNode)


def test_voprov_relations_use_the_voprov_namespace(written):
    graph = default_graph(written)
    assert (EX.a1, VOPROV.isDescribedBy, EX.ad1) in graph
    node = next(graph.objects(EX.a1, VOPROV.qualifiedIsDescribedBy))
    assert (node, VOPROV.descriptor, EX.ad1) in graph and (node, RDF.type, VOPROV.DescriptionRelation) in graph
    assert (EX.a1, VOPROV.wasConfiguredBy, EX.p1) in graph


def test_no_shortcuts_option(reference_doc):
    graph = default_graph(read_trig(reference_doc.serialize(format="rdf", shortcuts=False)))
    assert not list(graph.triples((None, PROV.used, None)))
    assert list(graph.triples((None, PROV.qualifiedUsage, None)))
    # PROV-O has no qualified form for these: the shortcut is all there is
    assert (EX.e2, PROV.specializationOf, EX.e1) in graph
    assert (EX.coll1, PROV.hadMember, EX.e1) in graph


def test_bundles_are_named_graphs(written):
    assert (EX.b1, RDF.type, PROV.Bundle) in default_graph(written)
    bundle = next(g for g in graphs_of(written) if str(g.identifier) == str(EX.b1))
    assert (EX.be1, RDF.type, PROV.Entity) in bundle
    assert (EX.be1, RDF.type, PROV.Entity) not in default_graph(written)


def test_sparql_on_prov_o_terms(reference_doc):
    """The result can be queried with PROV-O only, without knowing about voprov."""
    dataset = Dataset(default_union=True)  # the query sees the graphs of the document and of its bundles
    dataset.parse(data=reference_doc.serialize(format="rdf"), format="trig")
    rows = dataset.query("""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?activity ?input WHERE { ?activity a prov:Activity ; prov:used ?input . ?input a prov:Entity }""")
    assert (str(EX.a1), str(EX.e1)) in {(str(a), str(i)) for a, i in rows}


def test_namespaces_are_declared(reference_doc):
    text = reference_doc.serialize(format="rdf")
    for prefix in ("ex", "prov", "voprov"):
        assert "@prefix %s:" % prefix in text


# -- Other vocabularies ---------------------------------------------------------------------------------------------

def test_reads_prov_o_written_by_prov():
    """RDF written by prov (plain PROV-O) is read as the same document, with plain prov records."""
    prov_doc = pm.ProvDocument()
    prov_doc.add_namespace("ex", "http://example.org/")
    activity = prov_doc.activity("ex:a", datetime.datetime(2023, 1, 1, 10), datetime.datetime(2023, 1, 1, 11),
                                 {"prov:label": "run"})
    e_in = prov_doc.entity("ex:in")
    e_out = prov_doc.entity("ex:out", {"prov:type": pm.PROV["Collection"], "prov:location": "/x"})
    prov_doc.used(activity, e_in, other_attributes={"prov:role": "input"})
    prov_doc.wasGeneratedBy(e_out, activity, datetime.datetime(2023, 1, 1, 10, 30), identifier="ex:g")
    prov_doc.wasDerivedFrom(e_out, e_in)
    prov_doc.agent("ex:ag")
    prov_doc.wasAssociatedWith(activity, "ex:ag", None, None, {"prov:role": "op"})
    prov_doc.specializationOf(e_out, e_in)
    prov_doc.hadMember(e_out, e_in)
    prov_doc.wasStartedBy(activity, "ex:in", "ex:a", datetime.datetime(2023, 1, 1, 10))
    again = VOProvDocument.deserialize(content=prov_doc.serialize(format="rdf"), format="rdf")
    assert again == prov_doc
    assert all(type(r).__module__.startswith("prov.model") for r in again.records)


def test_reads_unknown_vocabularies():
    """Resources in namespaces that the document does not know are declared, and shortcuts alone give relations."""
    text = textwrap.dedent("""
        @prefix prov: <http://www.w3.org/ns/prov#> .
        @prefix lab: <http://lab.example/terms#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <http://lab.example/data/run1> a prov:Activity ; prov:used <http://lab.example/data/raw> ;
            lab:operator "Alice" ; lab:duration "PT5M"^^xsd:duration ; lab:count "7"^^lab:counter .
        <http://lab.example/data/raw> a prov:Entity .
    """)
    doc = VOProvDocument.deserialize(content=text, format="rdf", rdf_format="turtle")
    kinds = sorted(type(r).__name__ for r in doc.records)
    assert kinds == ["ProvActivity", "ProvEntity", "ProvUsage"]
    assert "http://lab.example/terms#" in {ns.uri for ns in doc.namespaces}
    activity = next(r for r in doc.records if r.is_element() and r.get_type() == pm.PROV_ACTIVITY)
    attributes = {str(k): v for k, v in activity.attributes}
    assert [v for k, v in attributes.items() if k.endswith(":operator")] == ["Alice"]
    assert any(isinstance(v, pm.Literal) and v.datatype is not None for v in attributes.values())


def test_a_plain_prov_reads_voprov_rdf_without_duplicates():
    """With shortcuts=False, the RDF of voprov can be read by prov (in its own process, not aware of voprov)."""
    script = textwrap.dedent("""
        import sys, warnings, collections
        warnings.simplefilter("ignore")
        import prov.model as pm
        from voprov.model import VOProvDocument
        d = VOProvDocument(); d.add_namespace("ex", "http://example.org/")
        d.activity("ex:a", startTime="2023-01-01T10:00:00"); d.entity("ex:e", name="x"); d.agent("ex:ag")
        d.usage("ex:a", "ex:e", role="input"); d.generation("ex:e", "ex:a", time="2023-01-01T11:00:00")
        d.start("ex:a", trigger="ex:e", starter="ex:a"); d.end("ex:a", trigger="ex:e", ender="ex:a")
        d.association("ex:a", "ex:ag", role="op"); d.derivation("ex:e", "ex:e", "ex:a")
        text = d.serialize(format="rdf", shortcuts=False)
        # a clean interpreter, where voprov is not imported: prov reads plain PROV-O
        import subprocess
        code = ("import sys, warnings, collections; warnings.simplefilter('ignore')\\n"
                "import prov.model as pm\\n"
                "p = pm.ProvDocument.deserialize(content=sys.stdin.read(), format='rdf')\\n"
                "assert 'voprov' not in sys.modules\\n"
                "print(sorted(collections.Counter(r.get_type().localpart for r in p.records).items()))")
        out = subprocess.run([sys.executable, "-c", code], input=text, capture_output=True, text=True)
        print(out.stdout.strip() or out.stderr[-300:])
    """)
    result = subprocess.run([sys.executable, "-W", "ignore", "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    counts = dict(eval(result.stdout.strip()))
    assert counts == {"Activity": 1, "Entity": 1, "Agent": 1, "Usage": 1, "Generation": 1, "Start": 1, "End": 1,
                      "Association": 1, "Derivation": 1}, result.stdout


def test_without_rdflib_the_format_is_missing_with_a_hint():
    code = ("import sys; sys.modules['rdflib'] = None\n"
            "from voprov import serializers\n"
            "try:\n    serializers.get('rdf')\nexcept serializers.DoNotExist as e:\n    print(e)\n")
    result = subprocess.run([sys.executable, "-W", "ignore", "-c", code], capture_output=True, text=True)
    assert "voprov[rdf]" in result.stdout, result.stderr
