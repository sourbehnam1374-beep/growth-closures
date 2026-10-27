"""Negative controls: a failed ledger must fail the process, not just print."""
from pathlib import Path
import runpy

import pytest

import growth_check as gc


def test_growth_ledger_failure_raises(monkeypatch):
    original = gc.m0
    monkeypatch.setattr(gc, "m0", lambda *args: original(*args) + 1)
    with pytest.raises(AssertionError, match="Growth ledger failed"):
        gc.self_check()


def test_unified_failure_returns_nonzero(monkeypatch):
    original = gc.composite
    def wrong_sign(kind, rule, sign, children):
        return original(kind, rule, "D1" if sign == "D2" else sign, children)
    monkeypatch.setattr(gc, "composite", wrong_sign)
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(Path(__file__).with_name("verify_unified.py")), run_name="__main__")
    assert exc.value.code == 1


def test_necessity_failure_returns_nonzero(monkeypatch):
    original = gc.close_field
    def missing_block(*args, **kwargs):
        parts, gov = original(*args, **kwargs)
        block = next(a for a, p in parts.items() if p["kind"] == "Block")
        return {a: p for a, p in parts.items() if a != block}, gov
    monkeypatch.setattr(gc, "close_field", missing_block)
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(Path(__file__).with_name("verify_o1_necessity.py")), run_name="__main__")
    assert exc.value.code == 1
