# Quick start

## Build a document

A document is a `VOProvDocument`. Identifiers are qualified names (`prefix:name`), so declare the namespaces you use.

```python
from voprov.model import VOProvDocument

doc = VOProvDocument()
doc.add_namespace("ex", "http://example.org/")

# what the activity does (its description) and one run of it
doc.activityDescription("ex:calibrate", "Calibration", version="1.0", description="Remove the bias")
doc.activity("ex:run1", name="calibration run", startTime="2023-01-01T10:00:00",
             endTime="2023-01-01T10:05:00", activityDescription="ex:calibrate")

# the data it used and generated
doc.entity("ex:raw", name="raw image", location="/data/raw.fits")
doc.entity("ex:cal", name="calibrated image", location="/data/cal.fits")
doc.usage("ex:run1", "ex:raw", role="input")
doc.generation("ex:cal", "ex:run1", role="output")

# who is responsible
doc.agent("ex:alice", name="Alice", type="Person", email="alice@example.org")
doc.association("ex:run1", "ex:alice", role="operator")
```

Times can be given as `datetime` objects or as strings that `dateutil` can parse.

## Save and read

```python
doc.serialize("provenance.json", format="json")
doc.serialize("provenance.xml", format="xml")

again = VOProvDocument.deserialize(source="provenance.json", format="json")
assert again == doc
```

Without a destination, `serialize` returns a string. `voprov.read(path)` tries every format until one works.
The [formats](formats.md) page lists what each format supports.

## Look at it

```python
print(doc.serialize(format="provn"))
```

`provn` is the most readable text format. To draw the graph (this needs Graphviz):

```python
from voprov.dot import prov_to_dot

prov_to_dot(doc, direction="LR").write_png("provenance.png")
```

## Use it with `prov`

`get_w3c` returns a plain `prov.model.ProvDocument`, where the VOProv concepts are kept as `prov:type`
values. Any tool built for W3C PROV can read it.

```python
w3c = doc.get_w3c()
print(type(w3c))
```

## From a dictionary

`add_one_step` builds the records of a processing step (product, step, inputs, parameters, contact, ...)
from a dictionary. See the [one step tutorial](tutorials/voprov_tutorial_one_step.ipynb).

```python
from voprov.model import VOProvDocument

doc = VOProvDocument()
for prefix in ("obs", "ps", "staff"):
    doc.add_namespace(prefix, "http://example.org/%s/" % prefix)

doc.add_one_step({
    "product_id": "obs:image1b",
    "product_role": "bias-subtracted-image",
    "step_id": "ps:2459",
    "step_name": "ps:bias_subtraction",
    "step_parameters": {"gain": 1.5},
    "used_ids": ["obs:image1", "obs:bias"],
    "generated_ids": [],
    "contact_id": "staff:Emma",
    "contact_name": "Emma",
})
```
