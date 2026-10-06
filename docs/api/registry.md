# Registration in prov

`prov` looks up record classes, PROV-N names, base types and attribute names in module level tables and has no hook
to extend them. `voprov.registry` is the one place where voprov adds its entries. It runs when
`voprov.model` is imported and can safely run again.

```{eval-rst}
.. automodule:: voprov.registry
   :members:
   :show-inheritance:
```
