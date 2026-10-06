# VOProv

VOProv is a Python implementation of the [IVOA Provenance Data Model](http://www.ivoa.net/documents/ProvenanceDM/).
It extends the [prov](https://prov.readthedocs.io) package, which implements the W3C PROV data model:
every VOProv record specializes a PROV record and adds the attributes defined by the IVOA.

## Features

- Build provenance documents with the VOProv concepts: activities, entities, agents, their *descriptions*,
  parameters and configuration files, and the relations between them.
- Save and read documents as PROV-JSON and PROV-XML; export to PROV-N and to a readable YAML summary
  (see [formats](formats.md)).
- Convert a document to a plain W3C `prov` document.
- Draw the provenance graph with Graphviz, or as an interactive Sankey diagram with Plotly.
- Build the records of a processing step from a single dictionary (`add_one_step`).

## Installation

```bash
pip install voprov
```

Optional extras: `voprov[dot]` for Graphviz graphs (needs the [Graphviz](https://graphviz.org) program), and
`voprov[rdf]` for the RDF dependencies of `prov`.

voprov works with `prov` 2.0 up to 3.x and Python 3.9 or later.

## Where to go next

- [Quick start](quickstart.md): build, save and draw a first document.
- [Concepts](concepts.md): the VOProv records and how they relate to W3C PROV.
- [Tutorials](tutorials/voprov_tutorial.ipynb): notebooks with a complete example.
- [API reference](api/index.md).

```{toctree}
:hidden:
:maxdepth: 2

quickstart
concepts
formats
tutorials/index
api/index
changelog
authors
```
