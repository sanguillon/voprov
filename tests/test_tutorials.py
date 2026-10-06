"""Execute the tutorial notebooks, so that they keep working with the code."""
import shutil
from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat")
nbclient = pytest.importorskip("nbclient")
pytest.importorskip("ipykernel")

TUTORIALS = Path(__file__).parent.parent / "tutorials"
NOTEBOOKS = sorted(TUTORIALS.glob("*.ipynb"))

pytestmark = pytest.mark.skipif(shutil.which("dot") is None, reason="graphviz (dot) is needed to draw the graphs")


def test_notebooks_found():
    assert NOTEBOOKS


@pytest.mark.parametrize("notebook", NOTEBOOKS, ids=lambda p: p.stem)
def test_notebook_runs(notebook, tmp_path):
    nb = nbformat.read(str(notebook), as_version=4)
    # run in a temporary directory: the notebooks write files (json, xml, png) in the working directory
    nbclient.NotebookClient(nb, timeout=180, kernel_name="python3",
                            resources={"metadata": {"path": str(tmp_path)}}).execute()
    text = "".join(str(output.get("text", "")) for cell in nb.cells if cell.cell_type == "code"
                   for output in cell.get("outputs", []))
    assert "is deprecated, use" not in text, "a notebook uses a deprecated voprov import path"


def test_notebooks_do_not_use_old_import_paths():
    for notebook in NOTEBOOKS:
        source = notebook.read_text()
        assert "voprov.models" not in source and "voprov.visualization" not in source, notebook.name
