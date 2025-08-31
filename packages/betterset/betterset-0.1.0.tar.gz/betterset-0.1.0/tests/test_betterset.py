import pytest

from betterset import BetterSet


def test_add_union_and_iadd():
    a = BetterSet({1, 2})
    b = BetterSet({2, 3})
    c = a + b
    assert isinstance(c, BetterSet)
    assert c == {1, 2, 3}

    a += {3, 4}
    assert a == {1, 2, 3, 4}


def test_mul_cartesian_and_imul():
    a = BetterSet({1, 2})
    b = BetterSet({"x", "y"})
    prod = a * b
    assert isinstance(prod, BetterSet)
    assert prod == {(1, "x"), (1, "y"), (2, "x"), (2, "y")}

    a2 = BetterSet({1, 2})
    a2 *= {10}
    assert a2 == {(1, 10), (2, 10)}


def test_pow_n_fold_cartesian():
    a = BetterSet({1, 2})
    assert a**0 == {()}  # singleton with empty tuple
    assert a**1 == {(1,), (2,)}
    assert a**2 == {(1, 1), (1, 2), (2, 1), (2, 2)}

    with pytest.raises(ValueError):
        _ = a**-1


def test_matmul_relation_composition():
    r1 = BetterSet({(1, 2), (2, 3)})
    r2 = BetterSet({(2, 5), (3, 7)})
    comp = r1 @ r2
    assert isinstance(comp, BetterSet)
    assert comp == {(1, 5), (2, 7)}


def test_powerset_counts_and_membership():
    a = BetterSet({1, 2, 3})
    ps = a.powerset()
    assert isinstance(ps, BetterSet)
    assert len(ps) == 2**3
    assert frozenset() in ps
    assert frozenset({1, 2, 3}) in ps


def test_cartesian_method():
    a = BetterSet({1, 2})
    b = BetterSet({"x"})
    assert a.cartesian(b) == {(1, "x"), (2, "x")}


def test_disjoint():
    a = BetterSet({1, 2})
    b = BetterSet({3})
    c = BetterSet({2})
    assert a.disjoint(b) is True
    assert a.disjoint(c) is False


def test_complement():
    universe = {1, 2, 3, 4}
    a = BetterSet({2, 4})
    comp = a.complement(universe)
    assert comp == {1, 3}


def test_partition_small_set():
    s = BetterSet({1, 2, 3})
    # k > n -> empty
    assert s.partition(4) == BetterSet()
    # k == 1 -> one block containing all
    p1 = s.partition(1)
    assert len(p1) == 1
    assert next(iter(p1)) == ((1, 2, 3),)
    # k == n -> singletons
    pn = s.partition(3)
    assert len(pn) == 1
    assert next(iter(pn)) == ((1,), (2,), (3,))
    # k == 2 -> S(3,2) == 3 partitions
    p2 = s.partition(2)
    assert len(p2) == 3
    # Validate canonical membership of expected partitions
    expected = {
        ((1,), (2, 3)),
        ((2,), (1, 3)),
        ((3,), (1, 2)),
    }
    assert p2 == expected

    with pytest.raises(ValueError):
        _ = s.partition(0)


def test_closure_finite_process():
    # Closure under op that increases to a bound then stops
    s = BetterSet({1})

    def op(x: int):
        return [x + 1] if x < 3 else []

    closed = s.closure(op)
    assert closed == {1, 2, 3}


def test_map_filter_reduce():
    s = BetterSet({1, 2, 3})
    # map with collisions
    m = s.map(lambda x: x % 2)
    assert m == {0, 1}
    # filter
    f = s.filter(lambda x: x >= 2)
    assert f == {2, 3}
    # reduce without initial (non-empty)
    total = s.reduce(lambda acc, x: acc + x, 0)
    assert total == 6

    # reduce without initial on empty should raise TypeError like functools.reduce
    empty = BetterSet()
    with pytest.raises(TypeError):
        empty.reduce(lambda acc, x: acc + x)  # type: ignore[arg-type]


def test_flatten_classmethod():
    out = BetterSet.flatten([[1, 2], {2, 3}, (3, 4)])
    assert isinstance(out, BetterSet)
    assert out == {1, 2, 3, 4}
    # empty input
    assert BetterSet.flatten([]) == BetterSet()
    # nested empty
    assert BetterSet.flatten([[], [], []]) == BetterSet()
