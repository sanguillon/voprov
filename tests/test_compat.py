"""Old import paths keep working (with a DeprecationWarning) and point to the same objects."""
import importlib
import sys
import warnings

import pytest

OLD_TO_NEW = {
    "voprov.models": "voprov.model",
    "voprov.models.model": "voprov.model.bundle",
    "voprov.models.constants": "voprov.constants",
    "voprov.models.registry": "voprov.registry",
    "voprov.models.voprovDescriptions": "voprov.model.records",
    "voprov.models.voprovConfigurations": "voprov.model.records",
    "voprov.models.voprovRelations": "voprov.model.records",
    "voprov.visualization": "voprov.dot",
    "voprov.visualization.dot": "voprov.dot",
    "voprov.visualization.graph": "voprov.graph",
    "voprov.visualization.plotly": "voprov.plotly",
    "voprov.serializers.xml": "voprov.serializers.provxml",
    "voprov.serializers.voyaml": "voprov.serializers.provyaml",
}


def fresh_import(name):
    """Import a module again, so that its import-time DeprecationWarning is raised."""
    sys.modules.pop(name, None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        module = importlib.import_module(name)
    return module, [w for w in caught if issubclass(w.category, DeprecationWarning)]


@pytest.mark.parametrize("old", sorted(OLD_TO_NEW))
def test_old_path_warns(old):
    pytest.importorskip("pydot")
    module, deprecations = fresh_import(old)
    assert any(OLD_TO_NEW[old] in str(w.message) or old in str(w.message) for w in deprecations)


def test_old_names_are_the_new_objects():
    pytest.importorskip("pydot")
    from voprov.model import records, bundle, VOProvDocument
    old_model, _ = fresh_import("voprov.models.model")
    assert old_model.VOProvDocument is VOProvDocument is bundle.VOProvDocument
    assert old_model.VOProvEntity is records.VOProvEntity
    assert old_model.VOProvNamespaceManager.__module__ == "voprov.model.namespaces"
    old_desc, _ = fresh_import("voprov.models.voprovDescriptions")
    assert old_desc.VOProvActivityDescription is records.VOProvActivityDescription
    old_rel, _ = fresh_import("voprov.models.voprovRelations")
    assert old_rel.VOProvIsDescribedBy is records.VOProvIsDescribedBy
    old_const, _ = fresh_import("voprov.models.constants")
    from voprov import constants
    assert old_const.VOPROV is constants.VOPROV


def test_old_serializer_paths():
    from voprov.serializers import provxml, provyaml
    old_xml, _ = fresh_import("voprov.serializers.xml")
    old_yaml, _ = fresh_import("voprov.serializers.voyaml")
    assert old_xml.VOProvXMLSerializer is provxml.VOProvXMLSerializer
    assert old_yaml.VOProvYAMLSerializer is provyaml.VOProvYAMLSerializer


def test_new_paths_do_not_warn():
    """Importing through the new paths must not trigger voprov's own deprecation warnings."""
    code = ("import warnings\n"
            "with warnings.catch_warnings(record=True) as caught:\n"
            "    warnings.simplefilter('always')\n"
            "    import voprov, voprov.model, voprov.constants, voprov.registry, voprov.serializers\n"
            "    import voprov.dot, voprov.graph\n"
            "    voprov.serializers.Registry.load_serializers()\n"
            "for w in caught:\n"
            "    if 'is deprecated, use' in str(w.message):\n"
            "        print(w.message)\n")
    import subprocess
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == ""
