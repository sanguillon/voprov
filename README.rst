============
Introduction
============

A library for IVOA Provenance Data Model supporting PROV-O (RDF), PROV-XML, PROV-JSON import/export, PROV-VOTABLE

* Free software: MIT license
* Documentation: not yet available (see prov documentation at http://prov.readthedocs.io/).

Features
--------

* An implementation of the `IVOA Provenance Data Model <http://www.ivoa.net/documents/ProvenanceDM/>`_ in Python.
* Serialization and deserializiation support: RDF, XML, JSON and VOTABLE
* Exporting PROV documents into various graphical formats (e.g. PDF, PNG, SVG).
* Convert a PROV document to a `Networkx MultiDiGraph <http://networkx.github.io/documentation/latest/reference/classes.multidigraph.html>`_ and back.


Uses
^^^^

See `the implementation notes  <http://www.ivoa.net/documents/ProvenanceDM/20170921/index.html>`_ for using this package.

The original prov package is used extensively by `ProvStore <https://provenance.ecs.soton.ac.uk/store/>`_,
a free online repository for provenance documents.
