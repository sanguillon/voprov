# Change log

## Unreleased

- Support for prov 3.x (prov>=2.0,<4 is tested with 2.0, 2.2 and 3.2)
- Package layout mirrors prov: `voprov.constants`, `voprov.model` (`records`, `namespaces`, `bundle`),
  `voprov.registry`, `voprov.dot`, `voprov.graph`, `voprov.plotly`, `voprov.serializers.provxml` and
  `provyaml`. The old paths (`voprov.models.*`, `voprov.visualization.*`, `voprov.serializers.xml` and
  `voyaml`) still work but emit a DeprecationWarning.
- voprov no longer modifies prov's namespaces on import, and registers its types in prov's tables in one place
  (`voprov.registry.register`)
- `VOProvNamespaceManager` now calls the parent constructor
- `lxml` is now a declared dependency
- `add_one_step` works without a default namespace and accepts a numeric `process_id`
- Fixes: `add_dataset_description` (undefined name, ignored arguments), `Activity.set_time` now parses strings,
  `voprov.read` no longer returns None for unreadable sources
- PROV-XML: documents written by voprov can now be read back (`VOProvXMLSerializer.deserialize`);
  `ConfigFileDescription` and `ParameterDescription` were missing from the base class table
- YAML: the serializer works with prov>=2.1 (it could not be instantiated), no longer crashes on relations
  referring to elements without attributes, writes to text streams, and keeps several `used`/`generated`
  entities. It is an export only: reading it raises NotImplementedError
- Known limitation: RDF serialization of voprov documents is not supported yet
- Documentation rebuilt with Sphinx, Furo and MyST (Markdown pages, notebooks rendered with myst-nb, links to the prov
  documentation); the API pages were empty before. The code examples of the documentation are tested.
- Packaging with `pyproject.toml` (setup.py and requirements*.txt removed), uv and just, pytest suite, GitLab CI


## v0.0.4, 20/06/2023

- Additional function add_* 
- function to import one step provenance
- YAML serialisation
- Sankey diagram visualisation with plotly


## v0.0.3, 28/04/2023

- Compatibility to Prov 2.0.0
- Removed support for EOL Python 2
- Added online documentation on readthedocs.org (autodoc)
