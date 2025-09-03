Modules, Imports, and Package Metadata
======================================

Resolution
----------
- Search order: current working directory, then paths in `SUP_PATH` (os‑path‑sep separated).
- A module `foo` is sourced from `foo.sup`.

Syntax
------
- `import foo` → binds namespace `foo.*` in current scope.
- `from foo import bar as baz` → binds symbol `bar` (function/var) as `baz`.

Execution model
---------------
- On import, the module executes in its own environment; exported top‑level variables and functions become available to importers.
- Circular import detection raises an error.

Package metadata (future)
-------------------------
- `sup.json` in project root:

```
{
  "name": "myapp",
  "version": "0.1.0",
  "description": "...",
  "entry": "main.sup",
  "dependencies": { "mathlib": "^1.0.0" }
}
```

- Used by a future package manager to resolve dependencies and publish packages.


