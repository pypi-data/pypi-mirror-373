Packaging and Project Commands
==============================

Scaffold
--------
```
sup init myapp
```
Creates `main.sup`, `sup.json`, and `README.md`.

Build (transpile project)
------------------------
```
sup build main.sup --out dist_sup
```
Produces Python modules and a `run.py` launcher. Sourcemaps are generated with `sourceMappingURL`.

Lockfile
--------
```
sup lock main.sup
```
Writes `sup.lock` containing module paths and SHA256 hashes for reproducible builds.

Test runner
-----------
```
sup test tests/
```
Runs all `.sup` files in a directory and reports pass count (zero exit code when all pass).

Publish (source tarball)
------------------------
```
sup publish .
```
Creates `dist_sup/<name>-<version>.tar.gz` using metadata from `sup.json`.


