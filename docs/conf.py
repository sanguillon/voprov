"""Sphinx configuration of the VOProv documentation."""
import shutil
from importlib.metadata import version as _version
from pathlib import Path

DOCS = Path(__file__).parent

# -- Project information -----------------------------------------------------

project = "VOProv"
author = "Benjamin Parciany, Mathieu Servillat"
copyright = "2023-2026, " + author
release = _version("voprov")
version = release

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_nb",
    "sphinx_copybutton",
]
exclude_patterns = ["_build"]

# Markdown pages (MyST) and notebooks (myst-nb). The notebooks keep their stored outputs.
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3
nb_execution_mode = "off"
# the headings of the notebooks are not always consecutive
suppress_warnings = ["myst.header"]

# API pages
autodoc_member_order = "bysource"
autodoc_typehints = "none"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "prov": ("https://prov.readthedocs.io/en/latest/", None),
}

# -- HTML --------------------------------------------------------------------

html_theme = "furo"
html_title = "VOProv"
html_theme_options = {
    # self hosted GitLab: Furo cannot guess the links
    "source_view_link": "https://gitlab.obspm.fr/mservillat/voprov/-/blob/main/docs/{filename}",
    "source_edit_link": "https://gitlab.obspm.fr/mservillat/voprov/-/edit/main/docs/{filename}",
}


def _copy_notebooks(app):
    """The tutorials live in the tutorials folder of the repository: copy them in the documentation sources."""
    target = DOCS / "tutorials"
    target.mkdir(exist_ok=True)
    for notebook in (DOCS.parent / "tutorials").glob("*.ipynb"):
        shutil.copy(notebook, target / notebook.name)


def setup(app):
    app.connect("builder-inited", _copy_notebooks)
