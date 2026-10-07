# Introduction

A library for IVOA Provenance Data Model supporting PROV-N, PROV-XML, PROV-JSON export

* Free software: MIT license (https://opensource.org/licenses/MIT)
* Documentation: https://voprov.readthedocs.io

## Features

* An implementation of the [IVOA Provenance Data Model](http://www.ivoa.net/documents/ProvenanceDM/) in Python.
* Serialization support: [PROV-N](http://www.w3.org/TR/prov-n/), [PROV-XML](http://www.w3.org/TR/prov-xml/) and [PROV-JSON](http://www.w3.org/Submission/prov-json/).
* Documents can be saved and read back as PROV-JSON, PROV-XML and RDF (PROV-O, needs `rdflib`). PROV-N and YAML (a readable summary) are export only.
* Exporting VOPROV documents into various graphical formats (e.g. PDF, PNG, SVG).
* Convert a VOPROV document to a [Prov Document](https://github.com/trungdong/prov).


## Uses

Tutorials are available as notebooks in the `tutorials` folder. A short one for using this package is here:

https://gitlab.obspm.fr/mservillat/voprov/-/blob/main/tutorials/voprov_tutorial.ipynb


## Development

The project uses [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/):

```bash
just sync       # create the virtual environment with all extras
just test       # run the test suite
just docs       # build the documentation in docs/_build/html
just with-prov 2.0.0 pytest   # run a command with a given version of prov
```

`tests/consistency/build_doc.py` (`just dump DIR`) writes a reference document in every format, to compare
the serialized output between two versions of the code.

### Releasing

The CI publishes to PyPI when a version tag is pushed, after the tests, the documentation and the build have passed.

One-off setup:

1. On pypi.org, create an API token scoped to the `voprov` project (Account settings > API tokens). You need to be
   a maintainer of the project.
2. In GitLab, add it as a CI/CD variable (Settings > CI/CD > Variables): key `UV_PUBLISH_TOKEN`, value `pypi-...`,
   with *Mask variable* and *Protect variable* ticked.
3. In GitLab, protect the version tags (Settings > Repository > Protected tags): `v*`. A protected variable is only
   available on protected branches and tags.

For each release:

1. Set the new `version` in `pyproject.toml`, and date the entry in `CHANGE.md`.
2. Commit and push to `main`, and wait for the pipeline to pass.
3. Tag and push the tag. The tag must be `v` followed by the version, or the job refuses to publish:

   ```bash
   git tag -a v0.1.0 -m "Release 0.1.0"
   git push origin v0.1.0
   ```
