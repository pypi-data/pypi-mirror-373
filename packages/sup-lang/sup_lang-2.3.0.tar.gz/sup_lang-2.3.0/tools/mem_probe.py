from __future__ import annotations

import gc
import sys
import time
import tracemalloc

from sup.cli import run_source


def run_loop(iterations: int = 200, sleep_s: float = 0.0) -> tuple[int, int]:
    code = """
sup
set total to 0
repeat 1000 times
set total to add total and 1
endrepeat
bye
""".strip()
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()
    for _ in range(iterations):
        run_source(code)
        if sleep_s:
            time.sleep(sleep_s)
        gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    top1 = sum(stat.size for stat in snapshot1.statistics("filename"))
    top2 = sum(stat.size for stat in snapshot2.statistics("filename"))
    return top1, top2


def main() -> int:
    before, after = run_loop()
    growth = after - before
    print(f"Memory before: {before} bytes; after: {after} bytes; growth: {growth} bytes")
    # Soft budget: less than 5 MB growth
    if growth > 5 * 1024 * 1024:
        print("Memory growth exceeds budget.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


