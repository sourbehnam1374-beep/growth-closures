"""Ingress regressions: one address must never silently select a record."""
import copy
import itertools

import pytest

import growth_check as gc
from delete_growth import two_phase


def conflicting_atoms():
    return gc.atom("same-payload", "D1"), gc.atom("same-payload", "D2")


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("route", ["batch", "incremental", "two_phase"])
def test_conflict_rejected_in_either_order(route, reverse):
    pair = list(conflicting_atoms())
    if reverse:
        pair.reverse()
    context = [gc.atom("context-1", "D1"), gc.atom("context-2", "D1")]
    with pytest.raises(ValueError, match="content-address identity conflict"):
        if route == "batch":
            gc.close_field(context + pair)
        elif route == "incremental":
            existing, _ = gc.close_field(context + pair[:1])
            gc.close_incremental(existing, pair[1:])
        else:
            two_phase([("add", p) for p in context + pair])


@pytest.mark.parametrize("order", list(itertools.permutations(range(3))))
def test_tombstone_does_not_hide_conflicting_adds(order):
    a, b = conflicting_atoms()
    ops = [("add", a), ("add", b), ("remove", a["addr"])]
    with pytest.raises(ValueError, match="content-address identity conflict"):
        two_phase([ops[i] for i in order])


@pytest.mark.parametrize("route", ["batch", "incremental", "two_phase"])
def test_exact_duplicate_is_idempotent(route):
    atoms = [gc.atom("dup-%d" % i, "D1") for i in range(3)]
    expected = gc.close_field(atoms)
    duplicates = copy.deepcopy(atoms)
    if route == "batch":
        actual = gc.close_field(atoms + duplicates)
    elif route == "incremental":
        actual = gc.close_incremental(expected[0], duplicates)
    else:
        actual = two_phase([("add", p) for p in atoms + duplicates])[:2]
    assert actual == expected


def test_rejected_delta_does_not_partially_mutate_existing_store():
    a, b = conflicting_atoms()
    existing, _ = gc.close_field([a])
    snapshot = copy.deepcopy(existing)
    with pytest.raises(ValueError, match="identity conflict"):
        gc.close_incremental(existing, [gc.atom("new", "D1"), b])
    assert existing == snapshot


def test_conflict_inside_one_incremental_delta_is_rejected():
    with pytest.raises(ValueError, match="identity conflict"):
        gc.close_incremental({}, list(conflicting_atoms()))


def test_two_phase_copies_add_records_before_advancing_input_iterator():
    atom = gc.atom("mutable-input", "D1")
    expected = copy.deepcopy(atom)

    def operations():
        yield "add", atom
        atom["descriptor"] = atom["sign"] = "D2"

    parts, _, _, _ = two_phase(operations())
    assert parts[expected["addr"]] == expected


@pytest.mark.parametrize("remove_first", [False, True])
def test_identical_readds_remain_tombstoned(remove_first):
    atom = gc.atom("removed", "D1")
    ops = [("add", atom), ("remove", atom["addr"]), ("add", dict(atom))]
    if remove_first:
        ops = [ops[1], ops[0], ops[2]]
    parts, gov, adds, removes = two_phase(ops)
    assert parts == {} and gov == []
    assert adds == removes == {atom["addr"]}
