"""Run the Python examples of the documentation, so that they keep working with the code."""
import re
import shutil
from pathlib import Path

import pytest

DOCS = Path(__file__).parent.parent / "docs"
PAGES = sorted(p for p in DOCS.glob("*.md") if "```python" in p.read_text())
FENCE = re.compile(r"```python\n(.*?)```", re.S)


def test_pages_found():
    assert {p.name for p in PAGES} >= {"quickstart.md", "concepts.md"}


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_examples_run(page, tmp_path, monkeypatch):
    """The examples of a page run in order, in one namespace, in a temporary directory."""
    from voprov.model import VOProvDocument
    monkeypatch.chdir(tmp_path)
    # some pages continue an example that is not repeated: they use a document called `doc`
    namespace = {"doc": VOProvDocument()}
    for block in FENCE.findall(page.read_text()):
        if "prov_to_dot" in block and shutil.which("dot") is None:
            continue  # drawing needs graphviz
        exec(compile(block, str(page), "exec"), namespace)
