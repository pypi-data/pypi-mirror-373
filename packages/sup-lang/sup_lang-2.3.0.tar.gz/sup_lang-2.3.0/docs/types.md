Optional Static Typing (Gradual Types)
======================================

Goals
-----
- Preserve SUP’s readability while enabling tooling (errors, IDE, optimization).
- Opt‑in at file/function/variable level; type erasure at runtime unless `--typecheck` is enabled.

Surface syntax (proposed)
-------------------------
- Type annotations via comment directives on headers:

```
sup
note types: add(a: number, b: number) -> number
define function called add with a and b
  return add a and b
end function
bye
```

- Variables (optional): `note type: x: number`
- Containers: `list<number>`, `map<string, number>` (for docs/tooling; enforced by linter/typechecker).

Type system
-----------
- Primitives: number, string, bool, null
- Structural containers: list<T>, map<K,V>
- Functions: (T1, T2, ...) -> R
- Union and optional: `A | B`, `optional<T>`

Checker
-------
- Separate tool `suptype` (future) validates annotations; LSP uses it for diagnostics if configured.
- Gradual: missing annotations default to `any` and don’t block execution.


