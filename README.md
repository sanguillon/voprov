# Introduction

A library for IVOA Provenance Data Model supporting PROV-N, PROV-XML, PROV-JSON export

* Free software: MIT license (https://opensource.org/licenses/MIT)
* Documentation: (incoming).

## Features

* An implementation of the [IVOA Provenance Data Model](http://www.ivoa.net/documents/ProvenanceDM/) in Python.
* Serialization support: [PROV-N](http://www.w3.org/TR/prov-n/), [PROV-XML](http://www.w3.org/TR/prov-xml/) and [PROV-JSON](http://www.w3.org/Submission/prov-json/).
* Documents can be saved and read back as PROV-JSON and PROV-XML. PROV-N and YAML (a readable summary) are export only, and RDF is not supported yet for VOProv documents.
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
just docs       # build the Sphinx documentation in docs/build
just with-prov 2.0.0 pytest   # run a command with a given version of prov
```

`tests/consistency/build_doc.py` (`just dump DIR`) writes a reference document in every format, to compare
the serialized output between two versions of the code.
