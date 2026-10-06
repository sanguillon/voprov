from voprov.constants import VOPROV
from voprov.model import VOProvDocument, VOProvNamespaceManager


def test_defaults_are_declared():
    m = VOProvNamespaceManager()
    assert set(m) == {"prov", "xsd", "xsi", "voprov"}
    assert {ns.prefix for ns in m.get_registered_namespaces()} == {"prov", "xsd", "xsi", "voprov"}


def test_user_namespaces():
    m = VOProvNamespaceManager(namespaces=[__import__("prov.identifier", fromlist=["x"]).Namespace(
        "ex", "http://example.org/")])
    assert "ex" in m and "voprov" in m


def test_default_namespace():
    m = VOProvNamespaceManager(default=VOPROV.uri)
    assert m.get_default_namespace().uri == VOPROV.uri


def test_parent_namespaces_are_visible():
    parent = VOProvNamespaceManager()
    parent.add_namespace(__import__("prov.identifier", fromlist=["x"]).Namespace("ex", "http://example.org/"))
    child = VOProvNamespaceManager(parent=parent)
    assert str(child.valid_qualified_name("ex:thing")) == "ex:thing"


def test_document_uses_voprov_namespace_manager(doc):
    assert isinstance(doc._namespaces, VOProvNamespaceManager)
    assert "voprov" in {ns.prefix for ns in doc.namespaces}
    assert "ex" in {ns.prefix for ns in doc.namespaces}


def test_bundle_namespaces_follow_document(doc):
    b = doc.bundle("ex:b")
    assert isinstance(b._namespaces, VOProvNamespaceManager)
    assert str(b.valid_qualified_name("voprov:Entity")) == "voprov:Entity"


def test_voprov_qualified_names(doc):
    assert doc.valid_qualified_name("voprov:Activity") == VOPROV["Activity"]
    assert doc.valid_qualified_name("ex:x").uri == "http://example.org/x"


def test_unknown_prefix_is_invalid(doc):
    assert doc.valid_qualified_name("nope:x") is None
