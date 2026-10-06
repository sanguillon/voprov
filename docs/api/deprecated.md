# Deprecated paths

The modules were reorganised to mirror `prov`. The old paths still work, and emit a `DeprecationWarning`.

| Old path | New path |
|---|---|
| `voprov.models` | `voprov.model` |
| `voprov.models.model` | `voprov.model` (`voprov.model.bundle` for the document and bundle) |
| `voprov.models.constants` | `voprov.constants` |
| `voprov.models.registry` | `voprov.registry` |
| `voprov.models.voprovDescriptions`, `voprovConfigurations`, `voprovRelations` | `voprov.model.records` |
| `voprov.visualization.dot` | `voprov.dot` |
| `voprov.visualization.graph` | `voprov.graph` |
| `voprov.visualization.plotly` | `voprov.plotly` |
| `voprov.serializers.xml` | `voprov.serializers.provxml` |
| `voprov.serializers.voyaml` | `voprov.serializers.provyaml` |
