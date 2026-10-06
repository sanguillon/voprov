# Concepts

## VOProv and W3C PROV

The IVOA Provenance Data Model is built on the W3C PROV model: *activities* use and generate *entities*, under the
responsibility of *agents*. VOProv adds what is needed to describe astronomical data processing, mostly the
**descriptions** of activities and entities, and the **parameters** and **configuration files** of a run.

In the code, each VOProv record class derives from the matching `prov` class
(`VOProvActivity` from `prov.model.ProvActivity`, and so on), and its type is in the `voprov` namespace
(`http://www.ivoa.net/documents/ProvenanceDM/index.html#`), for example `voprov:Activity`.
The `get_w3c()` method of a document gives the same information as plain PROV records, with the VOProv
concept kept as a `prov:type`.

## Elements

| Builder | Record | What it represents |
|---|---|---|
| `activity` | `VOProvActivity` | something that happened over a period of time (a run of a processing step) |
| `entity` | `VOProvEntity` | a piece of data or a thing |
| `valueEntity` | `VOProvValueEntity` | an entity with a value |
| `datasetEntity` | `VOProvDataSetEntity` | an entity that is a dataset (a file, a table, ...) |
| `parameter` | `VOProvParameter` | a parameter value used by an activity |
| `configFile` | `VOProvConfigFile` | a configuration file used by an activity |
| `agent` | `VOProvAgent` | a person, an organisation or software responsible for something |

## Descriptions

A description says what *kind* of activity or entity something is, independently of one particular run:
an activity description is shared by every run of the same step.

| Builder | Record |
|---|---|
| `activityDescription` | `VOProvActivityDescription` |
| `usageDescription`, `generationDescription` | `VOProvUsageDescription`, `VOProvGenerationDescription` (the roles an activity expects its inputs and outputs to play) |
| `entityDescription`, `valueDescription`, `datasetDescription` | `VOProvEntityDescription`, `VOProvValueDescription`, `VOProvDataSetDescription` |
| `parameterDescription`, `configFileDescription` | `VOProvParameterDescription`, `VOProvConfigFileDescription` |

## Relations

The PROV relations keep their usual meaning, and are built with the builder or with the PROV-N style name:

| Builder | PROV-N name | Between |
|---|---|---|
| `usage` | `used` | activity, entity |
| `generation` | `wasGeneratedBy` | entity, activity |
| `start`, `end` | `wasStartedBy`, `wasEndedBy` | activity, trigger |
| `invalidation` | `wasInvalidatedBy` | entity, activity |
| `communication` | `wasInformedBy` | activity, activity |
| `attribution` | `wasAttributedTo` | entity, agent |
| `association` | `wasAssociatedWith` | activity, agent |
| `delegation` | `actedOnBehalfOf` | agent, agent |
| `derivation`, `revision`, `quotation`, `primary_source` | `wasDerivedFrom`, ... | entity, entity |
| `influence`, `specialization`, `alternate`, `mention`, `membership` | `wasInfluencedBy`, ... | |

VOProv adds four relations:

| Builder | Record | Meaning |
|---|---|---|
| `description` | `VOProvIsDescribedBy` | an activity or entity *is described by* its description |
| `configuration` | `VOProvWasConfiguredBy` | an activity *was configured by* a parameter or a configuration file |
| `relate` | `VOProvIsRelatedTo` | a generic link between two records |
| `reference` | `VOProvHadReference` | a record *had a reference* to another one |

## Namespaces and identifiers

Every record has an identifier that is a qualified name: `prefix:name`. Declare the prefixes with
`doc.add_namespace(prefix, uri)`. The `voprov:`, `prov:` and `xsd:` prefixes are always known.

An identifier with no prefix (such as `"7531"`) is only valid if the document has a default namespace:

```python
from voprov.constants import VOPROV
doc.set_default_namespace(VOPROV.uri)
```

## Dedicated bundles

The `add_*` helpers (`add_activity_description`, `add_parameter`, `add_one_step`, ...) store the descriptions and
the configuration of an element in a dedicated *bundle* of the document, named `#description#<id>` or
`#configuration#<id>`. These names are local names of the default namespace; when the document has none,
the `voprov:` prefix is used instead.

## Relation to the prov package

voprov registers its record types in `prov`'s own tables when `voprov.model` is imported (see
[Registration in prov](api/registry.md)). This is why `prov` can name, list and serialize VOProv records.
Plain `prov` documents are not affected: they keep building plain `prov` records.
