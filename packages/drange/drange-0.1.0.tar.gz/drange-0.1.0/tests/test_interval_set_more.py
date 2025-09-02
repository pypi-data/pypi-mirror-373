import pytest

from drange.interval_set import IntervalSet, _get_union, _get_preceding_interval, _get_order, _universal

# ---------- helpers ----------


def set_from_runs(*runs):
    """Finite helper: build from closed runs by enumerating values."""
    vals = []
    for lo, hi in runs:
        assert lo is not None and hi is not None
        assert lo <= hi
        vals.extend(range(lo, hi + 1))
    return IntervalSet.from_items(vals)


def runs(s: IntervalSet):
    """Immutable view of runs (tuple-of-tuples)."""
    return tuple(s)


def check_canonical(s: IntervalSet):
    """No overlaps, no adjacency (closed intervals), sorted by start."""
    rs = runs(s)
    for i in range(1, len(rs)):
        (a_lo, a_hi), (b_lo, b_hi) = rs[i - 1], rs[i]
        assert (a_lo is None) or (b_lo is None) or (a_lo <= b_lo)
        # gap must be at least one integer between them (no overlap, no adjacency)
        if a_hi is not None and b_lo is not None:
            assert a_hi + 1 < b_lo

# ---------- __and__ sanity + bad-type behavior ----------


def test_and_operator_intervalset_and_bad_type():
    A = set_from_runs((1, 5))
    B = set_from_runs((4, 7))
    assert (A & B) == set_from_runs((4, 5))

    with pytest.raises(TypeError):
        _ = A & 3  # should return NotImplemented -> TypeError after fallbacks

    # reflected '&' with int should also TypeError (unless you add __rand__)
    with pytest.raises(TypeError):
        _ = 3 & A

# ---------- adjacency & infinities in union/intersection ----------


def test_adjacent_merges_to_single_run_and_infinite_edges():
    A = set_from_runs((1, 3))
    B = set_from_runs((4, 6))
    assert (A | B) == set_from_runs((1, 6))  # adjacency merges

    # (-inf, 10] U [11, +inf) -> universal
    left_inf = IntervalSet(_intervals=((None, 10),))
    right_inf = IntervalSet(_intervals=((11, None),))
    assert (left_inf | right_inf) == IntervalSet(_intervals=((None, None),))

    # (-inf, 10] U [12, +inf) -> two runs
    right_gap = IntervalSet(_intervals=((12, None),))
    assert (left_inf | right_gap) == IntervalSet(
        _intervals=((None, 10), (12, None)))


def test_intersection_with_infinities_and_point_touch():
    a = IntervalSet(_intervals=((None, 10),))
    b = IntervalSet(_intervals=((5, None),))
    assert (a & b) == IntervalSet(_intervals=((5, 10),))

    # point-touch (closed): [1,5] ∩ [5,9] == {5}
    A = set_from_runs((1, 5))
    B = set_from_runs((5, 9))
    assert (A & B) == set_from_runs((5, 5))

# ---------- complement laws & absorption ----------


def test_involution_and_absorption():
    A = set_from_runs((2, 4), (7, 9))
    empty = IntervalSet.from_items([])
    U = IntervalSet.from_items(universal=True)

    assert ~~A == A
    assert (A | ~A) == U
    assert (A & ~A) == empty

    # absorption
    B = set_from_runs((3, 8))
    assert A | (A & B) == A
    assert A & (A | B) == A

# ---------- difference associativity & equivalences ----------


def test_difference_associativity_and_equivalences():
    A = set_from_runs((1, 10))
    B = set_from_runs((4, 6))
    C = set_from_runs((8, 12))

    # (A - B) - C == A - (B ∪ C)
    left = (A - B) - C
    right = A - (B | C)
    assert left == right

    # A - B == A & ~B
    assert (A - B) == (A & ~B)

# ---------- symmetric difference associativity ----------


def test_symmetric_difference_associative():
    A = set_from_runs((1, 4))
    B = set_from_runs((3, 6))
    C = set_from_runs((6, 8))
    assert (A ^ (B ^ C)) == ((A ^ B) ^ C)

# ---------- subset/superset with infinities & across gaps ----------


def test_subset_with_infinities_and_gap_crossing():
    A = IntervalSet(_intervals=((None, 0),))
    B = IntervalSet(_intervals=((None, 1),))
    assert A <= B and A < B

    U = IntervalSet(_intervals=((None, None),))
    T = IntervalSet(_intervals=((5, None),))
    assert T <= U and T < U

    # across a gap: not a subset
    sup = IntervalSet(_intervals=((1, 3), (7, 9)))
    sub = IntervalSet(_intervals=((2, 8),))
    assert not (sub <= sup)

# ---------- predecessor semantics (renamed helper) ----------


def test_preceding_interval_edges_and_infinities():
    ivs = [(None, 10), (20, None)]
    assert _get_preceding_interval(ivs, -1000) == 0
    assert _get_preceding_interval(ivs, 10) == 0   # boundary inclusive
    assert _get_preceding_interval(ivs, 11) == 0
    assert _get_preceding_interval(ivs, 20) == 1
    assert _get_preceding_interval(ivs, 21) == 1
    assert _get_preceding_interval([], 5) == -1

# ---------- invariants hold after ops ----------


def test_canonical_invariants_after_many_ops():
    S = set_from_runs((1, 3))
    S = (S | set_from_runs((5, 7)))          # create a gap
    S = (S | set_from_runs((4, 4)))          # fill adjacency to merge
    check_canonical(S)

    S2 = (S ^ set_from_runs((2, 6)))         # symmetric difference split
    check_canonical(S2)

    S3 = (S2 - set_from_runs((1, 100)))      # big carve-out
    check_canonical(S3)

# ---------- hash/equality stability after non-mutating ops ----------


def test_hash_stability_and_dict_key_usage():
    A1 = set_from_runs((1, 3), (6, 9))
    A2 = set_from_runs((1, 3), (6, 9))
    B = set_from_runs((2, 4))

    h_before = hash(A1)
    M = {A1: "ok"}
    assert M[A2] == "ok"  # equal object finds the same key

    _ = A1 | B            # non-mutating; A1 unchanged
    assert hash(A1) == h_before

# ---------- single-interval helper robustness ----------


def test_get_union_shape_and_infinities():
    # shape: gap -> two intervals, no nesting tuple-of-tuples
    assert _get_union((1, 3), (6, 9)) == ((1, 3), (6, 9))
    # infinities
    assert _get_union((None, 10), (12, 20)) == ((None, 10), (12, 20))
    assert _get_union((None, 10), (11, 20)) == ((None, 20),)
    assert _get_union((5, 7), (None, None)) == (_universal,)
    assert _get_union((1, None), (5, 7)) == ((1, None),)

# ---------- error path for _get_order(None, ...) if you enforce it ----------


def test_get_order_raises_on_none_interval():
    with pytest.raises(TypeError):
        _get_order(None, (1, 2))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        _get_order((1, 2), None)  # type: ignore[arg-type]

# ---------- Following up on a false alarm in _get_intervals_complement ---------


def test_complement_leading_and_trailing_gaps():
    # Leading gap present (finite first start)
    ivs = [(3, 5)]
    comp = IntervalSet._get_intervals_complement(ivs)
    assert comp == [(None, 2), (6, None)]


def test_complement_no_leading_when_start_is_minus_inf():
    ivs = [(None, 5)]
    comp = IntervalSet._get_intervals_complement(ivs)
    assert comp == [(6, None)]


def test_complement_no_trailing_when_end_is_plus_inf():
    ivs = [(3, None)]
    comp = IntervalSet._get_intervals_complement(ivs)
    assert comp == [(None, 2)]


def test_complement_middle_gap_and_adjacency():
    # has a real gap  (5+1 < 9), and an adjacency (12 & 13) that shouldn't create a gap
    ivs = [(1, 5), (9, 12), (13, 20)]
    comp = IntervalSet._get_intervals_complement(ivs)
    assert comp == [(None, 0), (6, 8), (21, None)]


def test_complement_of_universal_and_empty():
    assert IntervalSet._get_intervals_complement([(None, None)]) == []
    assert IntervalSet._get_intervals_complement([]) == [(None, None)]


def rt(s): return IntervalSet.from_string(s).to_string()


def test_round_trip_examples():
    assert rt("()") == "()"
    assert rt("([<:>])") == "([<:>])"
    assert rt("(4,5,[7:12])") == "(4,5,[7:12])"
    assert rt("([<:10],[15:>])") == "([<:10],[15:>])"
    assert IntervalSet.from_string("([4:5],10,15,20,[22:25],[28:29])").to_string() \
        == "(4,5,10,15,20,[22:25],28,29)"


def test_parse_noncanonical_and_spaces():
    s = " ( [ 1 : 3 ] , 4 , [6:7] ) "
    S = IntervalSet.from_string(s)
    assert S.to_string() == "([1:4],6,7)"


def test_bad_tokens():
    for bad in ["(", ")", "(]", "[1:2]", "(1 2)", "([2:1])", "([>:5])", "([1:<])"]:
        with pytest.raises(ValueError):
            IntervalSet.from_string(bad)
            print(bad)


def test_singletons_merge_in_serialization():
    s = IntervalSet.from_string("([4:5],10,15,20,[22:25],28,29)")
    assert s.to_string() == "(4,5,10,15,20,[22:25],28,29)"


def test_spaces_require_commas_between_items():
    with pytest.raises(ValueError):
        IntervalSet.from_string("(1 2)")   # missing comma

    # but spaces around commas are fine
    ok = IntervalSet.from_string("( 1 , 2 , [ 4 : 5 ] )")
    assert ok.to_string() == "(1,2,4,5)"


def test_reject_internal_spaces_in_number():
    for bad in ["( - 3 )", "(1\t2)"]:
        with pytest.raises(ValueError):
            IntervalSet.from_string(bad)
