# Formats

A document is saved with `doc.serialize(destination, format=...)` and read with
`VOProvDocument.deserialize(source=..., format=...)`, or `voprov.read(path)` to let voprov guess the format.

| Format | `format=` | Write | Read | Notes |
|---|---|---|---|---|
| PROV-JSON | `"json"` | yes | yes | complete; the reference format |
| PROV-XML | `"xml"` | yes | yes | complete; structural elements are in the `voprov` namespace |
| PROV-N | `"provn"` | yes | no | human readable text |
| YAML | `"yaml"` | yes | no | compact summary, see below |
| RDF | `"rdf"` | yes | yes | complete; PROV-O compatible (TriG, Turtle, JSON-LD, ...), needs `rdflib` |

"Complete" means that reading the file back gives a document equal to the one that was written.

## RDF

The RDF follows [PROV-O](https://www.w3.org/TR/prov-o/), so that it can be queried with SPARQL and used by any tool
that knows PROV-O, and adds the VOProv concepts in the `voprov` namespace. It needs the `rdflib` package
(`pip install voprov[rdf]`).

```python
from voprov.model import VOProvDocument

trig = doc.serialize(format="rdf")                           # TriG: the bundles are named graphs
turtle = doc.serialize(format="rdf", rdf_format="turtle")    # other formats of rdflib
again = VOProvDocument.deserialize(content=trig, format="rdf")
assert again == doc
```

An element is typed with its PROV-O class and with its VOProv class. A relation is written as the PROV-O
shortcut (`prov:used`) and as a *qualified* node, which holds its identifier, role, time and other attributes:

```turtle
ex:run1 a voprov:Activity, prov:Activity ;
    prov:name "calibration run" ;
    prov:startedAtTime "2023-01-01T10:00:00"^^xsd:dateTime ;
    prov:used ex:raw ;
    prov:qualifiedUsage [ a voprov:Usage, prov:Usage ;
            prov:entity ex:raw ;
            prov:hadRole "input" ] ;
    voprov:isDescribedBy ex:calibrate ;
    voprov:qualifiedIsDescribedBy [ a voprov:DescriptionRelation ;
            voprov:descriptor ex:calibrate ] .
```

| What | In RDF |
|---|---|
| element | a resource of the PROV-O class (`prov:Entity`, `prov:Activity`, `prov:Agent`) and of the VOProv class (`voprov:DatasetEntity`, ...) |
| attribute | a property: `prov:name`, `voprov:location`, ... (`prov:startedAtTime`, `prov:atLocation`, `rdfs:label`, `prov:hadRole` and `prov:atTime` as in PROV-O) |
| relation | the shortcut, and the qualified node linked with `prov:qualifiedUsage`, `prov:qualifiedGeneration`, ... |
| relation that PROV-O does not qualify (specialization, alternate, membership, mention) and VOProv relations | the shortcut (`prov:hadMember`, `voprov:isDescribedBy`, ...), and a node linked with `voprov:qualifiedMembership`, ... |
| bundle | a named graph, also typed `prov:Bundle` in the default graph |
| values | the XSD types of the values (numbers, booleans, dates), language tags and qualified names (as IRIs) are kept |

Some points to know:

- Two records with the same identifier are one resource, so they come back as one record: use `doc.unified()` to
  compare the document with what is read.
- Relations without identifier are blank nodes named from their content, so the same document is always written
  the same way, whatever the order of its records: the files can be followed in a repository.
- With `shortcuts=False`, only the qualified nodes are written (the relations that PROV-O does not qualify keep
  their shortcut). The shortcuts are redundant, and the RDF reader of `prov`, which expects a relation in one
  form or the other, reads some relations twice when it finds both. `prov` 2.0 cannot read the bundles of the
  files written by voprov: use `prov` 2.2 or later to read them with `prov`.
- The formats of rdflib without named graphs (`turtle`, `xml`, `nt`) merge the bundles with the document.
- RDF written by other tools can be read: PROV-O classes give plain `prov` records, and a relation that is only
  written as a shortcut is read as a relation.

## YAML summary

The YAML output is meant to be read by people (for example in a notebook). It keeps the main records, grouped
by kind, and loses the rest, so it cannot be read back:

```yaml
activity:
  ex:run1:
    name: calibration run
    used: ex:raw
    generated: ex:cal
    parameters: {}
entity:
  ex:raw:
    name: raw image
```

## W3C PROV

`doc.get_w3c()` converts a document to a plain `prov` document. That one can be written in all the formats of
`prov`, including those that voprov does not support:

```python
w3c = doc.get_w3c()
w3c.serialize(format="json")
```
