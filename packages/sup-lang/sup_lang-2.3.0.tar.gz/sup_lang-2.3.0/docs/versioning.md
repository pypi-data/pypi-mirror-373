Versioning, Stability, and Releases
===================================

Versioning policy
-----------------
- Semantic Versioning (SemVer): MAJOR.MINOR.PATCH
  - Breaking language changes: MAJOR
  - Backward‑compatible features: MINOR
  - Bug fixes/perf improvements: PATCH
- Stability windows: no breaking changes within a MINOR line; deprecations are announced one MINOR ahead.

LTS releases
------------
- Designate select MINOR versions as LTS (e.g., 1.4, 2.6) supported for 12–18 months with backported fixes.
- Tooling (compiler/VM/LSP) keeps compatibility with LTS minor within its MAJOR.

Deprecations
------------
- Mark features as deprecated in docs and diagnostics; provide migration tips.
- Remove deprecations only on next MAJOR.

Migration policy
----------------
- Each deprecation entry includes: affected syntax/API, replacement, examples, and an automated lint fix if feasible.
- Provide a `--migrate` tool (future) to rewrite common patterns; changelog links to guides.

Release cadence
---------------
- Regular MINOR releases (4–8 weeks), PATCH as needed.
- RC tags for release candidates; issue a changelog with migration notes.


