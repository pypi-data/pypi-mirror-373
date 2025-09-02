import pytest

from drange.interval_set import IntervalSet, _get_order, _get_union, _get_intersection, _get_preceding_interval, _universal, Interval

# -----------------------------
# Helper builders for tests
# -----------------------------


def set_from_runs(*runs: tuple[int, int]) -> IntervalSet:
    """
    Build a finite IntervalSet from closed integer runs, by enumerating values.
    Only use for finite bounds.
    """
    vals = []
    for lo, hi in runs:
        assert lo is not None and hi is not None, "finite-only helper"
        assert lo <= hi
        vals.extend(range(lo, hi + 1))
    return IntervalSet.from_items(vals)


def singleton(x: int) -> IntervalSet:
    return IntervalSet.from_items([x])


# -----------------------------
# Top-level helper functions
# -----------------------------

def test_get_order_various_cases():
    A = (1, 5)
    B = (6, 9)
    assert _get_order(A, B) < 0
    assert _get_order(B, A) > 0
    assert _get_order(A, A) == 0

    # Starts equal; earlier end comes first
    A2 = (1, 3)
    assert _get_order(A2, A) < 0

    # Negative infinity starts first
    N10 = (None, 10)
    P10 = (10, None)
    assert _get_order(N10, A) < 0
    # Positive infinity ends last
    assert _get_order(A, P10) < 0
    # Universal compares equal to itself
    U = (None, None)
    assert _get_order(U, U) == 0


def test_get_union_overlap_nonoverlap_and_universal():
    # Overlapping -> one interval
    assert _get_union((1, 5), (4, 9)) == ((1, 9),)
    assert _get_union((4, 9), (1, 5)) == ((1, 9),)

    # Non-overlapping (no contiguity checks here) -> two intervals in order
    assert _get_union((1, 3), (5, 7)) == ((1, 3), (5, 7))

    # Identity with None
    assert _get_union(None, (2, 3)) == ((2, 3),)
    assert _get_union((2, 3), None) == ((2, 3),)

    # Universal absorbs
    assert _get_union((None, None), (5, 7)) == ((None, None),)
    assert _get_union((5, 7), (None, None)) == ((None, None),)


def test_get_intersection_boundaries_and_infinite():
    # Touching at a point (closed intervals) -> singleton
    assert _get_intersection((1, 5), (5, 9)) == (5, 5)
    # Overlap
    assert _get_intersection((1, 5), (3, 9)) == (3, 5)
    # Disjoint
    assert _get_intersection((1, 3), (5, 9)) is None

    # With infinities
    assert _get_intersection((None, 10), (5, None)) == (5, 10)
    assert _get_intersection((None, 10), (11, None)) is None


def test_get_preceding_interval_indexing_and_bounds():
    ivs = [(1, 3), (6, 9), (15, 20)]
    # Inside first
    idx = _get_preceding_interval(ivs, 2)
    assert idx == 0 and ivs[idx] == (1, 3)
    # Boundary inclusive
    idx = _get_preceding_interval(ivs, 3)
    assert idx == 0
    # Gap
    idx = _get_preceding_interval(ivs, 4)
    assert idx == 0
    # Inside last
    idx = _get_preceding_interval(ivs, 18)
    assert idx == 2 and ivs[idx] == (15, 20)


# -----------------------------
# IntervalSet.build and basics
# -----------------------------

def test_build_empty_and_universal():
    assert IntervalSet.from_items([]).is_empty
    assert IntervalSet.from_items(values=None).is_empty
    u = IntervalSet.from_items(universal=True)
    assert u.is_universal


def test_build_unsorted_with_duplicates_and_coalescing():
    s = IntervalSet.from_items([5, 2, 3, 3, 4, 8, 9])
    # Should coalesce into [2,5] and [8,9]
    assert str(s) == "([2:5],8,9)"
    # Membership spot checks
    assert s.contains_point(2)
    assert s.contains_point(5)
    assert not s.contains_point(6)
    assert s.contains_point(9)


def test_is_infinite_positive_negative_and_not_universal():
    u = IntervalSet.from_items(universal=True)
    assert u.is_universal
    assert u.is_infinite_negative
    assert u.is_infinite_positive

    s = set_from_runs((1, 3))
    assert not s.is_universal
    assert not s.is_infinite_negative
    assert not s.is_infinite_positive


# -----------------------------
# Set algebra via public helpers
# -----------------------------

def test_union_merges_adjacency_and_overlaps():
    a = set_from_runs((1, 3))
    b = set_from_runs((4, 6))
    c = a.union(b)  # should merge adjacency (closed intervals)
    assert str(c) == "([1:6])"

    d = set_from_runs((10, 15))
    e = c.union(d)
    assert str(e) == "([1:6],[10:15])"

    # Overlap union
    f = set_from_runs((5, 12))
    g = e.union(f)
    assert str(g) == "([1:15])"


def test_intersection_and_difference_and_complement_edges():
    a = set_from_runs((1, 10))
    b = set_from_runs((5, 7))
    assert str(a.intersection(b)) == "([5:7])"

    # Difference cases: removing middle → two pieces
    c = a.subtraction(set_from_runs((4, 8)))
    assert str(c) == "([1:3],9,10)"

    # Removing boundary
    d = a.subtraction(singleton(1))
    assert str(d) == "([2:10])"

    # Complement of empty is universal; complement of universal is empty
    e = IntervalSet.from_items([])
    assert e.complement().is_universal
    assert IntervalSet.from_items(universal=True).complement().is_empty


def test_symmetric_difference_equivalences():
    A = set_from_runs((1, 4))
    B = set_from_runs((3, 6))
    sym = A ^ B
    # Elements unique to either side: [1,2] and [5,6]
    assert str(sym) == "(1,2,5,6)"
    # Identities
    assert str(A ^ A) == "()"
    assert (A ^ B) == (A.union(B).subtraction(A.intersection(B)))


# -----------------------------
# Dunder operators (binary/reflected)
# -----------------------------

def test_add_and_radd_with_int_singleton():
    s = set_from_runs((2, 4))
    t = s + 5
    assert str(t) == "([2:5])"
    # reflected
    u = 1 + s
    assert str(u) == "([1:4])"


def test_sub_and_mul_with_int_singleton():
    s = set_from_runs((2, 6))
    # remove a point
    t = s - 4
    assert str(t) == "(2,3,5,6)"
    # intersection at a single point
    u = s * 2
    assert str(u) == "(2)"
    # reflected mul
    v = 6 * s
    assert str(v) == "(6)"


def test_or_requires_intervalset_operand():
    s = set_from_runs((1, 3))
    t = set_from_runs((5, 7))
    assert str(s | t) == "([1:3],[5:7])"
    # Unsupported right operand should raise TypeError after fallbacks
    with pytest.raises(TypeError):
        _ = s | 5  # int lacks __ror__ for IntervalSet


def test_xor_with_int_and_intervalset():
    s = set_from_runs((1, 4))
    u = s ^ 2
    assert str(u) == "(1,3,4)"
    t = set_from_runs((3, 6))
    v = s ^ t
    assert str(v) == "(1,2,5,6)"


def test_neg_and_invert_are_complement():
    s = set_from_runs((2, 3))
    assert s.complement() == -s == ~s


# -----------------------------
# Equality and comparisons
# -----------------------------

def test_equality_and_ne_mixed_types():
    s = set_from_runs((1, 2))
    assert (s == s) is True
    assert (s != s) is False
    # Mixed-type equality should be False (both eqs NotImplemented)
    assert (s == 123) is False
    assert (s != 123) is True


def test_subset_and_proper_subset_and_operators():
    A = set_from_runs((1, 3))
    B = set_from_runs((1, 4))
    C = set_from_runs((5, 9))

    assert A.is_subset_of(B)
    assert not B.is_subset_of(A)
    assert not A.is_subset_of(C)

    assert A.is_proper_subset_of(B)
    assert not A.is_proper_subset_of(A)

    # Operator forms
    assert A <= B
    assert A < B
    assert not (A < A)
    assert B >= A
    assert B > A

    # Mixed-type ordering should raise TypeError after both sides NotImplemented
    with pytest.raises(TypeError):
        _ = A < 123  # type: ignore[operator]


# -----------------------------
# contains_point (boundaries & gaps)
# -----------------------------

def test_contains_point_boundaries_and_gap():
    s = set_from_runs((1, 3), (6, 8))
    assert s.contains_point(1)
    assert s.contains_point(3)
    assert not s.contains_point(4)
    assert s.contains_point(7)
    assert not s.contains_point(9)


# -----------------------------
# List-level helpers (union/intersection/subtraction/negation)
# -----------------------------

def test_list_union_merges_and_orders():
    A = [(1, 3), (8, 10)]
    B = [(4, 7)]
    out = IntervalSet._get_intervals_union(A, B)
    # adjacency 3 & 4 should merge via coalescing inside the helper
    assert out == [(1, 10)]

    # Adding a disjoint far run stays separate
    out2 = IntervalSet._get_intervals_union(out, [(20, 21)])
    assert out2 == [(1, 10), (20, 21)]


def test_list_intersection_and_subtraction():
    A = [(1, 10)]
    B = [(4, 8)]
    inter = IntervalSet._get_intervals_intersection(A, B)
    assert inter == [(4, 8)]
    diff = IntervalSet._get_intervals_subtraction(A, B)
    assert diff == [(1, 3), (9, 10)]

    # Subtraction trimming to a single side
    C = [(1, 10)]
    D = [(9, 15)]
    assert IntervalSet._get_intervals_subtraction(C, D) == [(1, 8)]


def test_complement_of_empty_universal_and_middle_gap():
    # empty -> universal
    assert IntervalSet._get_intervals_complement([]) == [_universal]
    # universal -> empty
    assert IntervalSet._get_intervals_complement([_universal]) == []
    # Middle gap
    ivs = [(1, 3), (6, 8)]
    neg = IntervalSet._get_intervals_complement(ivs)
    assert neg == [(None, 0), (4, 5), (9, None)]


# -----------------------------
# TODOs / work-in-progress
# -----------------------------

@pytest.mark.xfail(reason="contains_interval not yet implemented")
def test_contains_interval_todo():
    s = set_from_runs((1, 5))
    assert s.contains_interval((2, 3))
    assert not s.contains_interval((0, 1))
    assert not s.contains_interval((4, 6))


# Helpers
def set_from_runs(*runs):
    vals = []
    for lo, hi in runs:
        assert lo is not None and hi is not None
        vals.extend(range(lo, hi + 1))
    return IntervalSet.from_items(vals)

# ---------- algebraic laws (selected identities) ----------


def test_commutativity_and_idempotence():
    A = set_from_runs((1, 3))
    B = set_from_runs((2, 5))
    assert A | B == B | A
    assert A & B == B & A
    assert (A | A) == A
    assert (A & A) == A


def test_absorption_and_distributivity():
    A = set_from_runs((1, 7))
    B = set_from_runs((4, 10))
    C = set_from_runs((12, 15))
    assert A | (A & B) == A
    assert A & (A | B) == A
    assert A & (B | C) == (A & B) | (A & C)


def test_de_morgan_laws():
    A = set_from_runs((1, 3))
    B = set_from_runs((5, 7))
    assert ~(A | B) == (~A) & (~B)
    assert ~(A & B) == (~A) | (~B)


def test_subtraction_identities():
    A = set_from_runs((1, 5))
    empty = IntervalSet.from_items([])
    U = IntervalSet.from_items(universal=True)
    assert A - A == empty
    assert A - empty == A
    assert empty - A == empty
    assert A - U == empty
    assert U - A == ~A


def test_symmetric_difference_identities():
    A = set_from_runs((1, 5))
    B = set_from_runs((4, 7))
    assert A ^ A == IntervalSet.from_items([])
    assert (A ^ B) == (B ^ A)
    assert (A ^ B) ^ B == A

# ---------- infinities & single-interval helpers ----------


def test_single_union_with_infinities_and_gaps():
    assert _get_union((None, 10), (12, 20)) == ((None, 10), (12, 20))
    assert _get_union((None, 10), (11, 20)) == ((None, 20),)
    assert _get_union((1, 5), (None, 2)) == ((None, 5),)
    assert _get_union((1, None), (5, 7)) == ((1, None),)
    assert _get_union(_universal, (5, 7)) == (_universal,)


def test_intersection_with_infinities():
    A = IntervalSet(_intervals=((None, 10),))
    B = IntervalSet(_intervals=((5, None),))
    assert A.intersection(B) == IntervalSet(_intervals=((5, 10),))

# ---------- ordering & error behavior ----------


def test_get_order_raises_on_none_interval():
    with pytest.raises(TypeError):
        _get_order(None, (1, 2))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        _get_order((1, 2), None)  # type: ignore[arg-type]


def test_preceding_interval_with_infinities_and_edges():
    ivs = [(None, 10), (20, None)]
    assert _get_preceding_interval(ivs, -1) == 0
    assert _get_preceding_interval(ivs, 10) == 0
    assert _get_preceding_interval(ivs, 15) == 0
    assert _get_preceding_interval(ivs, 25) == 1
    assert _get_preceding_interval([], 5) == -1

# ---------- iteration behavior ----------


def test_iter_runs_is_immutable_view():
    s = IntervalSet(_intervals=((1, 3), (6, 7)))
    it = iter(s)          # iter_runs
    first = next(it)
    with pytest.raises(TypeError):
        first[0] = 99     # tuples are immutable


def test_iter_values_requires_bounds_if_infinite():
    u = IntervalSet.from_items(universal=True)
    with pytest.raises(ValueError):
        list(u.iter_values())           # infinite without bounds
    # but clipping is fine
    assert list(u.iter_values(0, 2)) == [0, 1, 2]


def test_iter_values_clipping_and_empty_clip():
    s = set_from_runs((1, 10))
    assert list(s.iter_values(3, 5)) == [3, 4, 5]
    assert list(s.iter_values(11, 20)) == []   # clip outside -> empty

# ---------- “in-place” dunders are functional (non-mutating) ----------


def test_ior_iand_ixor_do_not_mutate_original():
    s = set_from_runs((2, 4))
    alias = s
    s |= 5        # returns a new IntervalSet
    assert str(alias) == "([2:4])"   # original unchanged

    s2 = set_from_runs((1, 3))
    alias2 = s2
    s2 &= 2
    assert str(alias2) == "([1:3])"

    s3 = set_from_runs((1, 3))
    alias3 = s3
    s3 ^= 2
    assert str(alias3) == "([1:3])"


def test_iand_fallback_typeerror_on_bad_type():
    s = set_from_runs((1, 2))
    with pytest.raises(TypeError):
        s &= "nope"   # __iand__ -> NotImplemented -> falls back -> TypeError

# ---------- repr / str / hashing ----------


def test_repr_round_trip_and_str_markers():
    u = IntervalSet.from_items(universal=True)
    s = set_from_runs((1, 3))
    # repr round-trip (constructor accepts _intervals kw)
    assert eval(repr(s)) == s
    # str uses "<" and ">" markers for infinities
    assert str(u) == "([<:>])"
    assert str(s) == "([1:3])"


def test_hash_consistency_and_mapping_key():
    A1 = set_from_runs((1, 3), (6, 9))
    A2 = set_from_runs((1, 3), (6, 9))
    B = set_from_runs((1, 4))

    # Equal objects have equal hashes
    assert A1 == A2
    assert hash(A1) == hash(A2)

    # Can be used as dict keys; lookup via an equal object succeeds
    d = {A1: "ok"}
    assert d[A2] == "ok"

    # Functional 'in-place' ops must not mutate the original (hash remains stable)
    h_before = hash(A1)
    _ = (A1 | B)        # returns a new object; A1 unchanged
    assert hash(A1) == h_before


def test_hash_edge_cases_empty_and_universal():
    empty = IntervalSet.from_items([])
    U = IntervalSet.from_items(universal=True)
    # Just ensure they are hashable and consistent with equality
    _ = hash(empty)
    _ = hash(U)
    assert (empty == IntervalSet.from_items([])) and (
        hash(empty) == hash(IntervalSet.from_items([])))
    assert (U == IntervalSet.from_items(universal=True)) and (
        hash(U) == hash(IntervalSet.from_items(universal=True)))

# ---------- contains_interval quick checks ----------


def test_contains_interval_finite_and_infinite_cases():
    sup = IntervalSet(_intervals=((None, 10), (20, 25)))
    assert sup.contains_interval((None, 5))
    assert sup.contains_interval((22, 25))
    assert not sup.contains_interval((9, 21))   # crosses the gap
