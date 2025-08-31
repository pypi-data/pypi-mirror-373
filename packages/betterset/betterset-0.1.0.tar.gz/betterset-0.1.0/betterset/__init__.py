"""BetterSet: an extended set with algebraic and functional utilities.

Implementation notes:
- Inherits from Python's built-in set and forwards to it when possible.
- Adds operator overloads and utility methods inspired by PLAN.md.

Public API (stable for this package scope):
- Operators: + (union), * (cartesian product), ** (n-fold cartesian), @ (relation composition)
- Methods: powerset, cartesian, disjoint, complement, partition, closure,
           map, filter, reduce
"""

from __future__ import annotations

import functools as ft
import itertools as it
from typing import (
    Any,
    Callable,
    FrozenSet,
    Generic,
    Iterable,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class BetterSet(set, Generic[T]):
    """Extended set.

    Notes:
    - We avoid overriding core behaviors like hashability (still unhashable like set).
    - Methods return BetterSet where a set is expected for fluency.
    """

    # ----------------------------- Constructors ---------------------------- #
    def __init__(self, iterable: Optional[Iterable[T]] = None) -> None:
        super().__init__(iterable or [])

    # ----------------------------- Helper utils ---------------------------- #
    @staticmethod
    def _to_better(iterable: Iterable[U]) -> "BetterSet[U]":
        return BetterSet(iterable)

    # ------------------------------ Operators ----------------------------- #
    def __add__(self, other: Iterable[T]) -> "BetterSet[T]":
        """Union via +.

        Mirrors self | set(other).
        """
        return BetterSet(super().union(other))

    def __radd__(self, other: Iterable[T]) -> "BetterSet[T]":
        return BetterSet(set(other).union(self))

    def __iadd__(self, other: Iterable[T]) -> "BetterSet[T]":
        self.update(other)
        return self

    def __mul__(self, other: Iterable[U]) -> "BetterSet[Tuple[T, U]]":
        """Cartesian product via *.

        Returns set of tuples (a, b) for a in self, b in other.
        """
        return BetterSet(it.product(self, other))

    def __rmul__(self, other: Iterable[U]) -> "BetterSet[Tuple[U, T]]":
        return BetterSet(it.product(other, self))

    def __imul__(self, other: Iterable[U]) -> "BetterSet[Any]":
        """In-place multiply => replace with cartesian product.

        Not strictly conventional, but consistent with __mul__.
        """
        new_values = list(it.product(self, other))
        super().clear()
        super().update(new_values)
        return self

    def __pow__(self, n: int) -> "BetterSet[Tuple[Any, ...]]":
        """n-fold cartesian product: A ** 0 -> {()}; A ** 1 -> A as 1-tuples; etc."""
        if n < 0:
            raise ValueError("Exponent must be non-negative")
        if n == 0:
            return BetterSet({()})
        # Start with tuples of length 1
        tuples: Iterable[Tuple[Any, ...]] = ((x,) for x in self)
        for _ in range(1, n):
            tuples = ((*t, x) for t in tuples for x in self)
        return BetterSet(tuples)

    def __matmul__(self, other: Iterable[Tuple[U, V]]) -> "BetterSet[Tuple[T, V]]":
        """Relation composition for sets of pairs.

        If self is set of (a,b) and other is set of (b,c), produce (a,c).
        """
        self_pairs = [(a, b) for (a, b) in self]  # type: ignore[misc]
        other_pairs = list(other)
        return BetterSet(
            (a, d) for (a, b) in self_pairs for (c, d) in other_pairs if b == c
        )

    # ------------------------------- Methods ------------------------------- #
    def powerset(self) -> "BetterSet[FrozenSet[T]]":
        """Return the powerset as a set of frozensets."""
        elements = tuple(self)
        all_subsets = (
            frozenset(comb)
            for r in range(len(elements) + 1)
            for comb in it.combinations(elements, r)
        )
        return BetterSet(all_subsets)

    def cartesian(self, other: Iterable[U]) -> "BetterSet[Tuple[T, U]]":
        return BetterSet(it.product(self, other))

    def disjoint(self, other: Iterable[T]) -> bool:
        return super().isdisjoint(other)

    def complement(self, universe: Iterable[T]) -> "BetterSet[T]":
        """Relative complement: universe - self.

        Caller is responsible for ensuring `universe` represents the domain of interest.
        """
        return BetterSet(set(universe).difference(self))

    def partition(self, k: int) -> "BetterSet[Tuple[Tuple[T, ...], ...]]":
        """Partition the set into k non-empty, disjoint, ordered blocks (as tuples).

        Returns a set of partitions where each partition is a tuple of blocks, and each
        block is a tuple of elements. Order of blocks and elements is canonicalized by
        sorting to provide deterministic output independent of hash order.
        Note: Number of set partitions grows quickly (Bell numbers). Use carefully.
        """
        if k <= 0:
            raise ValueError("k must be positive")
        elements = sorted(self, key=repr)
        n = len(elements)
        if k > n:
            return BetterSet()

        def _partitions(
            seq: Sequence[T], blocks: int
        ) -> Iterator[Tuple[Tuple[T, ...], ...]]:
            if not seq:
                if blocks == 0:
                    yield tuple()
                return
            if blocks == 0:
                return
            first, rest = seq[0], seq[1:]
            # Put first into a new block
            for parts in _partitions(rest, blocks - 1):
                yield ((first,),) + parts
            # Put first into any existing block
            for parts in _partitions(rest, blocks):
                for i in range(len(parts)):
                    new_block = tuple(sorted((first, *parts[i]), key=repr))
                    yield tuple(parts[:i]) + (new_block,) + tuple(parts[i + 1 :])

        # Canonicalize partitions (sort blocks and elements inside blocks)
        canonical: set[Tuple[Tuple[T, ...], ...]] = set()
        for p in _partitions(elements, k):
            normalized_blocks = tuple(
                sorted(
                    (tuple(sorted(b, key=repr)) for b in p),
                    key=lambda blk: (len(blk), repr(blk)),
                )
            )
            canonical.add(normalized_blocks)
        return BetterSet(canonical)

    def closure(self, op: Callable[[T], Iterable[T]]) -> "BetterSet[T]":
        """Compute closure under a unary operation op.

        Applies op repeatedly to newly discovered elements until fixpoint.
        """
        closed: set[T] = set(self)
        frontier: list[T] = list(self)
        while frontier:
            current = frontier.pop()
            for nxt in op(current):
                if nxt not in closed:
                    closed.add(nxt)
                    frontier.append(nxt)
        return BetterSet(closed)

    def map(self, func: Callable[[T], U]) -> "BetterSet[U]":
        return BetterSet(func(x) for x in self)

    def filter(self, predicate: Callable[[T], bool]) -> "BetterSet[T]":
        return BetterSet(x for x in self if predicate(x))

    def reduce(self, func: Callable[[U, T], U], initial: Optional[U] = None) -> U:
        if initial is None:
            return ft.reduce(func, self)  # type: ignore[arg-type]
        return ft.reduce(func, self, initial)  # type: ignore[arg-type]

    # ------------------------------ Class methods --------------------------- #
    @classmethod
    def flatten(cls, iterable: Iterable[Iterable[T]]) -> "BetterSet[T]":
        """Flatten an iterable of iterables into a BetterSet.

        Example:
            BetterSet.flatten([[1, 2], {2, 3}]) -> BetterSet({1, 2, 3})
        """
        return cls(it.chain.from_iterable(iterable))


__all__ = ["BetterSet"]
