from __future__ import annotations

import os
import sys


def main() -> int:
    # Minimal smoke test: run a tiny SUP program through the CLI path
    program = """sup\n  print \"Hello, SUP!\"\nbye\n"""
    try:
        from sup.cli import run_source

        out = run_source(program)
        if "Hello, SUP!" in out:
            print("OK: smoke test passed")
            return 0
        print("FAIL: unexpected output", out)
        return 1
    except Exception as e:
        print("FAIL:", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


