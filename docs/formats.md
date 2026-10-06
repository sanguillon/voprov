# Formats

A document is saved with `doc.serialize(destination, format=...)` and read with
`VOProvDocument.deserialize(source=..., format=...)`, or `voprov.read(path)` to let voprov guess the format.

| Format | `format=` | Write | Read | Notes |
|---|---|---|---|---|
| PROV-JSON | `"json"` | yes | yes | complete; the reference format |
| PROV-XML | `"xml"` | yes | yes | complete; structural elements are in the `voprov` namespace |
| PROV-N | `"provn"` | yes | no | human readable text |
| YAML | `"yaml"` | yes | no | compact summary, see below |
| RDF | `"rdf"` | no | no | not supported yet for VOProv documents |

"Complete" means that reading the file back gives a document equal to the one that was written.

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
