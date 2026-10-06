# API reference

voprov follows the layout of the `prov` package:

| voprov | like prov | contents |
|---|---|---|
| [`voprov.model`](model.md) | `prov.model` | records, namespace manager, bundle and document |
| [`voprov.constants`](constants.md) | `prov.constants` | identifiers of the VOProv types and attributes, and the tables of names |
| [`voprov.serializers`](serializers.md) | `prov.serializers` | JSON, XML, PROV-N and YAML serializers |
| [`voprov.dot`, `voprov.graph`, `voprov.plotly`](visualization.md) | `prov.dot`, `prov.graph` | drawing a document |
| [`voprov.registry`](registry.md) | | registration of the VOProv types in `prov` |

Classes derived from `prov` link to the [prov documentation](https://prov.readthedocs.io).
The paths used before version 0.1.0 still work, see [deprecated paths](deprecated.md).

```{toctree}
:hidden:

model
constants
serializers
visualization
registry
deprecated
```
