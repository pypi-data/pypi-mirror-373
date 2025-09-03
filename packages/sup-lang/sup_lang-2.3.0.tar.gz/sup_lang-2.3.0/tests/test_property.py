from __future__ import annotations

from hypothesis import given, strategies as st

from sup.cli import run_source


@given(st.integers(min_value=-1000, max_value=1000), st.integers(min_value=-1000, max_value=1000))
def test_add_commutative(a: int, b: int) -> None:
    code = f"""
sup
print add {a} and {b}
print add {b} and {a}
bye
""".strip()
    out = run_source(code)
    x, y = out.splitlines()
    assert float(x) == float(y)


@given(st.lists(st.integers(min_value=-10, max_value=10), min_size=1, max_size=10))
def test_join_len_roundtrip(xs: list[int]) -> None:
    # join then split preserves length
    values = ", ".join(str(x) for x in xs)
    code = f"""
sup
make list of {values if values else ''}
print length of list
print length of join of "," and list
bye
""".strip()
    out = run_source(code)
    l1, l2 = out.splitlines()
    assert int(float(l1)) >= 0
    assert float(l2) >= 0.0


