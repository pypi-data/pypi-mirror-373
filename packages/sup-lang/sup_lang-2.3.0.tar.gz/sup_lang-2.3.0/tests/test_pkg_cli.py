from __future__ import annotations

import json
import os
import subprocess as sp
import sys
import tarfile


def run_cli(*args: str, cwd: str | None = None) -> int:
    cmd = [sys.executable, "-u", "-m", "sup.cli", *args]
    return sp.run(cmd, cwd=cwd, stdout=sp.PIPE, stderr=sp.PIPE).returncode


def test_build_lock_publish_and_test_commands(tmp_path):
    proj = tmp_path / "app"
    proj.mkdir()
    (proj / "main.sup").write_text("""
sup
print "ok"
bye
""".strip(), encoding="utf-8")
    (proj / "sup.json").write_text(json.dumps({"name": "app", "version": "0.1.0", "entry": "main.sup"}), encoding="utf-8")

    # build
    rc = run_cli("build", "main.sup", "--out", "dist_sup", cwd=str(proj))
    assert rc == 0
    assert (proj / "dist_sup" / "run.py").exists()

    # lock
    rc = run_cli("lock", "main.sup", cwd=str(proj))
    assert rc == 0
    assert (proj / "sup.lock").exists()

    # test (create tests dir with one .sup)
    tests_dir = proj / "tests"
    tests_dir.mkdir()
    (tests_dir / "t.sup").write_text("""
sup
print "t"
bye
""".strip(), encoding="utf-8")
    rc = run_cli("test", "tests", cwd=str(proj))
    assert rc == 0

    # publish
    rc = run_cli("publish", ".", cwd=str(proj))
    assert rc == 0
    tgzs = list((proj / "dist_sup").glob("*.tar.gz"))
    assert tgzs, "no tarball created"
    # open tarball and verify main.sup present
    with tarfile.open(tgzs[0], "r:gz") as tf:
        names = tf.getnames()
        assert "main.sup" in names


