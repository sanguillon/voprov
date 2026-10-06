import importlib.util
from pathlib import Path

import pytest

from voprov.model import VOProvDocument, VOPROV

_BUILD_DOC = Path(__file__).parent / "consistency" / "build_doc.py"


@pytest.fixture
def doc():
    """Empty document with an `ex` namespace."""
    d = VOProvDocument()
    d.add_namespace("ex", "http://example.org/")
    return d


@pytest.fixture
def reference_doc():
    """Document using most record types (same as the one used by tests/consistency)."""
    spec = importlib.util.spec_from_file_location("build_doc", _BUILD_DOC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build()


@pytest.fixture
def onestep():
    """Minimal dictionary for VOProvDocument.add_one_step."""
    return {
        "product_id": "obs:image1b",
        "product_role": "bias-subtracted-image",
        "contact_id": "staff:Emma",
        "contact_name": "Emma",
        "step_id": "ps:2459",
        "step_name": "ps:bias_subtraction",
        "step_parameters": {"gain": 1.5},
        "used_ids": ["obs:image1", "obs:bias"],
        "generated_ids": [],
        "workflow_name": "ps:ImageCalibration",
    }


@pytest.fixture
def onestep_doc():
    """Empty document with the namespaces used by the `onestep` fixture."""
    d = VOProvDocument()
    for prefix in ("obs", "ps", "staff"):
        d.add_namespace(prefix, "http://example.org/%s/" % prefix)
    return d


@pytest.fixture
def default_ns():
    return VOPROV.uri
