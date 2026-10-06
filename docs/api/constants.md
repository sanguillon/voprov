# Constants

`voprov.constants` holds the identifiers of the VOProv types and attributes, as `prov` qualified names, and the
tables that map them to names and classes. It has no behaviour of its own: it only contains data.

## Namespaces

| Name | Value |
|---|---|
| `VOPROV` | the `voprov` namespace, `http://www.ivoa.net/documents/ProvenanceDM/index.html#` |
| `DEFAULT_NAMESPACES` | the namespaces every document knows: `prov`, `xsd`, `xsi` and `voprov` |

## Record types

One constant per record type, named `VOPROV_<TYPE>`, whose value is a qualified name in the `voprov` namespace:

```python
from voprov.constants import VOPROV_ENTITY, VOPROV_ACTIVITY_DESCRIPTION

print(VOPROV_ENTITY)                  # voprov:Entity
print(VOPROV_ACTIVITY_DESCRIPTION)    # voprov:ActivityDescription
```

| Family | Constants |
|---|---|
| Elements | `VOPROV_ENTITY`, `VOPROV_VALUE_ENTITY`, `VOPROV_DATASET_ENTITY`, `VOPROV_ACTIVITY`, `VOPROV_AGENT`, `VOPROV_BUNDLE` |
| PROV relations | `VOPROV_USAGE`, `VOPROV_GENERATION`, `VOPROV_COMMUNICATION`, `VOPROV_START`, `VOPROV_END`, `VOPROV_INVALIDATION`, `VOPROV_DERIVATION`, `VOPROV_ATTRIBUTION`, `VOPROV_ASSOCIATION`, `VOPROV_DELEGATION`, `VOPROV_INFLUENCE`, `VOPROV_ALTERNATE`, `VOPROV_SPECIALIZATION`, `VOPROV_MENTION`, `VOPROV_MEMBERSHIP` |
| Descriptions | `VOPROV_ACTIVITY_DESCRIPTION`, `VOPROV_ENTITY_DESCRIPTION`, `VOPROV_VALUE_DESCRIPTION`, `VOPROV_DATASET_DESCRIPTION`, `VOPROV_USAGE_DESCRIPTION`, `VOPROV_GENERATION_DESCRIPTION`, `VOPROV_CONFIG_FILE_DESCRIPTION`, `VOPROV_PARAMETER_DESCRIPTION` |
| Configuration | `VOPROV_CONFIGURATION_FILE`, `VOPROV_CONFIGURATION_PARAMETER` |
| VOProv relations | `VOPROV_DESCRIPTION_RELATION`, `VOPROV_RELATED_TO_RELATION`, `VOPROV_CONFIGURATION_RELATION`, `VOPROV_REFERENCE_RELATION` |

## Attributes

Attribute names are named `VOPROV_ATTR_<NAME>`. Most are the PROV attributes (`VOPROV_ATTR_ENTITY` is `prov:entity`),
the others are in the `voprov` namespace (`VOPROV_ATTR_DESCRIBED` is `voprov:described`).

## Tables

| Name | Content |
|---|---|
| `VOPROV_N_MAP`, `VOPROV_ADDITIONAL_N_MAP` | PROV-N name of each VOProv record type |
| `VOPROV_BASE_CLS` | base type of each VOProv type (for example, `voprov:Revision` is a `voprov:Derivation`) |
| `VOPROV_ATTRIBUTE_QNAMES`, `VOPROV_ATTRIBUTE_LITERALS` | attributes that hold a qualified name, or a literal value |
| `PROV_N_MAP`, `PROV_BASE_CLS`, ... | the same tables merged with the ones of `prov` |

The `VOPROV_*` tables are only data: they are added to `prov`'s own tables by
[`voprov.registry.register`](registry.md).
