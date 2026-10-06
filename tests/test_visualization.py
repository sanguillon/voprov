import pytest

pydot = pytest.importorskip("pydot")

from voprov.dot import prov_to_dot  # noqa: E402


def test_dot_graph(reference_doc):
    graph = prov_to_dot(reference_doc)
    assert isinstance(graph, pydot.Dot)
    text = graph.to_string()
    assert "ex:a1" in text and "ex:e1" in text
    assert len(graph.get_edges()) > 10


def test_dot_direction(reference_doc):
    assert "rankdir" in prov_to_dot(reference_doc, direction="LR").to_string()


def test_dot_empty_document(doc):
    assert isinstance(prov_to_dot(doc), pydot.Dot)


def test_dot_includes_bundles(reference_doc):
    assert "ex:be1" in prov_to_dot(reference_doc).to_string()
