from __future__ import annotations

import os
import runpy
import tempfile

from sup.cli import transpile_project
from sup.sourcemap import remap_exception


def test_sourcemap_remaps_traceback(tmp_path):
    # Create a small program that raises ZeroDivisionError after transpilation
    src = """
sup
print divide 1 by 0
bye
""".strip()
    sup_file = tmp_path / "boom.sup"
    sup_file.write_text(src, encoding="utf-8")
    out_dir = tmp_path / "dist_py"
    transpile_project(str(sup_file), str(out_dir))
    # Find generated module for boom
    py_file = out_dir / "boom.py"
    assert py_file.exists()
    # Running should raise; remap the exception
    try:
        runpy.run_path(str(py_file))
    except Exception as e:  # noqa: BLE001
        msg = remap_exception(e)
        assert "boom.sup" in msg
        # Original line is 2 (print line)
        assert ":2" in msg
    else:
        raise AssertionError("Expected exception not raised")


