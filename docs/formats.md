# Formats

A document is saved with `doc.serialize(destination, format=...)` and read with
`VOProvDocument.deserialize(source=..., format=...)`, or `voprov.read(path)` to let voprov guess the format.

| Format | `format=` | Write | Read | Notes |
|---|---|---|---|---|
| PROV-JSON | `"json"` | yes | yes | complete; standard PROV-JSON, readable by any PROV tool |
| PROV-XML | `"xml"` | yes | yes | complete; standard PROV-XML, readable by any PROV tool |
| PROV-N | `"provn"` | yes | no | human readable text |
| YAML | `"yaml"` | yes | no | compact summary, see below |
| RDF | `"rdf"` | yes | yes | complete; PROV-O compatible (TriG, Turtle, JSON-LD, ...), needs `rdflib` |

"Complete" means that reading the file back gives a document equal to the one that was written.

## PROV-JSON

The file is standard [PROV-JSON](https://www.w3.org/Submission/prov-json/): it only has the sections of PROV-JSON
(`entity`, `activity`, `used`, `wasInfluencedBy`, ...), so the tools that read PROV-JSON, such as `prov`, can read it.
The VOProv records that PROV-JSON does not have are written in the section of the PROV record that they specialize,
and are marked with a `prov:type` of the `voprov` namespace. voprov uses the marker to give the record its class back.

```json
{
  "entity": {
    "ex:raw": {"prov:name": "raw image"},
    "ex:offset": {"prov:name": "offset", "voprov:value": {"$": 3.5, "type": "xsd:double"},
                  "prov:type": {"$": "voprov:ValueEntity", "type": "prov:QUALIFIED_NAME"}}
  },
  "wasInfluencedBy": {
    "_:id1": {"prov:influencee": "ex:run1", "prov:influencer": "ex:calibrate",
              "prov:type": {"$": "voprov:DescriptionRelation", "type": "prov:QUALIFIED_NAME"}}
  }
}
```

- The records that PROV has (entity, activity, agent, usage, ...) have no marker: that part of the file is the
  PROV-JSON that any tool writes. The specialized elements (value and dataset entities, parameters, configuration
  files, descriptions) are entities with a marker, and the relations of VOProv (`isDescribedBy`, `wasConfiguredBy`,
  `isRelatedTo`, `hadReference`) are influences with a marker.
- `doc.get_w3c()` followed by a serialization with `prov` gives a file that voprov reads back as the same document.
- The files written by voprov before 0.1.0, which had a section for each VOProv record (`valueEntity`,
  `isDescribedBy`, ...), are still read. The files of other tools are read as VOProv records: PROV records have no
  marker, so they cannot be told from the ones of VOProv. This is the same for the XML.

## PROV-XML

Like the JSON, the file is standard [PROV-XML](https://www.w3.org/TR/prov-xml/): the document and the records are
elements of the PROV namespace, with `prov:id` and `prov:ref`, so that the tools that read PROV-XML can read it. The
VOProv records that PROV-XML does not have are the PROV records that they specialize (entities and influences), with
a `prov:type` marker of the `voprov` namespace that gives them their class back when voprov reads the file.

```xml
<prov:document xmlns:prov="http://www.w3.org/ns/prov#"
               xmlns:voprov="http://www.ivoa.net/documents/ProvenanceDM/index.html#"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:ex="http://example.org/">
  <prov:entity prov:id="ex:offset">
    <prov:name>offset</prov:name>
    <prov:type xsi:type="xsd:QName">voprov:ValueEntity</prov:type>
    <voprov:value xsi:type="xsd:double">3.5</voprov:value>
  </prov:entity>
  <prov:wasInfluencedBy>
    <prov:influencee prov:ref="ex:run1"/>
    <prov:influencer prov:ref="ex:calibrate"/>
    <prov:type xsi:type="xsd:QName">voprov:DescriptionRelation</prov:type>
  </prov:wasInfluencedBy>
</prov:document>
```

The markers, and how the files of other tools and of former versions are read, are the same as for the JSON. The files
of voprov before 0.1.0, in which the elements were in the `voprov` namespace, are still read.

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
