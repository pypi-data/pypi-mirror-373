from __future__ import annotations
from types import NotImplementedType
from dataclasses import dataclass, field

from typing import Iterator, Optional, Tuple, Sequence
import re

Interval = Tuple[Optional[int], Optional[int]]
_universal = (None, None,)


def _is_universal(iv: Interval) -> bool:
    return iv[0] is None and iv[1] is None


def _is_inf_neg(iv: Interval) -> bool:
    return iv[0] is None


def _is_inf_pos(iv: Interval) -> bool:
    return iv[1] is None


def _interval_str(iv: Interval) -> str:
    return f"[{'<' if iv[0] is None else iv[0]}:{'>' if iv[1] is None else iv[1]}]"


def _get_preceding_interval(intervals: Sequence[Interval], pt: int) -> int:
    """
    Return the index of the rightmost interval whose start <= x (or start == -∞).
    Returns -1 if all intervals start after x. O(log n).
    """
    if not intervals:
        return -1

    lo, hi = 0, len(intervals) - 1
    idx = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        iv = intervals[mid]
        if _is_inf_neg(iv) or iv[0] <= pt:
            idx = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return idx


def _get_intersection(a: Interval | None, b: Interval | None) -> Interval | None:

    # Handle empty cases
    if a is None or b is None:
        return None

    # The latter start
    cmp = _get_order(a, b, check_end=False)
    if cmp < 0:
        start = b[0]
    else:
        start = a[0]

    # The earlier end
    cmp = _get_order(a, b, check_start=False)
    if cmp < 0:
        end = a[1]
    else:
        end = b[1]

    # Watch out for empties and degenerate singletons
    if start is not None and end is not None:
        if start > end:
            return None
        elif start == end:
            return (start, start)

    # All other cases would be regularly-generated intervals.
    return (start, end)


def _get_order(a: Interval | None, b: Interval | None, check_start=True, check_end=True) -> int:
    """
    Returns a comparison for ordering: negative if `a` comes before `b`, 0 if they
    compare identically, and positive if `b` comes before `a`.
    """
    # If either is empty (None), the very first check will throw.

    # He who starts earlier returns first in order.
    if check_start:
        # negative-infinite analysis
        if a[0] is None and b[0] is not None:
            return -1
        if b[0] is None and a[0] is not None:
            return 1

        # At this point, the starts might be Nones if we're looking at universals (but if one
        # start is infinite, both are). Guard against that, then compare their start points.
        if a[0] is not None and b[0] is not None:
            if a[0] < b[0]:
                return -1
            elif a[0] > b[0]:
                return 1

        if not check_end:
            return 0

    # The start points are identical or ignored. Analyze from the ends. He who ends first
    # returns first in order.
    if check_end:
        # pos-infinite analysis
        if a[1] is None and b[1] is not None:
            return 1
        if b[1] is None and a[1] is not None:
            return -1

        # pos-infinites are identical, `a[1]` could still be infinite of `b[1]` is also
        # infinite. If both were infinite, the negative-infinite one would prevail if
        # check_start was true, or we'll return 0. Guard against start[1] being None.
        if a[1] is not None and b[1] is not None:
            if a[1] < b[1]:
                return -1
            elif a[1] > b[1]:
                return 1

    # We have ruled out all possibilities for ordering. The intervals are identical in all
    # attributes and will have the same ordering.
    return 0


def _get_union(a: Interval | None, b: Interval | None) -> Tuple[Interval, ...] | None:
    """
    identifies the union(s) based on hi/lo and universality. Either one or two intervals will be 
    returned. The input intervals are presumed to be in-order according to the get_order function. 
    Adjacent or overlapping intervals are returned as a single interval.
    """

    # Handle all empty cases
    if a is None:
        if b is not None:
            return (b,)
        return None
    if b is None:
        return (a,)

    # Rule out the gap situations
    if a[1] is not None and b[0] is not None and a[1] + 1 < b[0]:
        return (a, b)
    # if b[1] is not None and a[0] is not None and b[1] + 1 < a[0]:
    #     return (b, a)

    # Find the earliest start and the latest end
    start = None if a[0] is None or b[0] is None else min(a[0], b[0])
    end = None if a[1] is None or b[1] is None else max(a[1], b[1])

    # Just a simple interval
    return ((start, end),)


@dataclass(eq=True, frozen=True)
class IntervalSet():
    """
    Canonical, ordered, non-overlapping set of intervals between ints.
    """

    _intervals: Tuple[Interval, ...] = field(
        default_factory=tuple, repr=False, compare=False)

    def __post_init__(self):
        object.__setattr__(self, "_hash", None)

    @classmethod
    def from_items(cls, values: Optional[Sequence[int]] = None, universal=False) -> IntervalSet:
        """
        Build an integer-ordered interval set from first principles.
        - `values` may be unsorted and may contain duplicates.
        - Produces maximal closed runs [start, end] with end >= start.
        - Result is already canonical: sorted, disjoint, coalesced.
        """
        if universal:
            return IntervalSet(_intervals=((None, None),))
        if not values:
            return IntervalSet(_intervals=())

        # Sort the input (duplicates allowed; we'll collapse them during the sweep)
        vals = sorted(values)

        runs: list[Interval] = []

        run_start = vals[0]
        run_end = vals[0]

        for v in vals[1:]:
            if v == run_end:
                # ignore dupes
                continue
            if v == run_end + 1:  # contiguous by +1 for ints
                run_end = v
            else:
                # gap -> close current run and start a new one
                runs.append((run_start, run_end))
                run_start = run_end = v

        # For the last run
        runs.append((run_start, run_end))

        # Build the final IntervalSet with the pre-coalesced intervals
        return cls(_intervals=tuple(runs))

    @property
    def is_universal(self) -> bool:
        return bool(self._intervals) and _is_universal(self._intervals[0])

    @property
    def is_empty(self) -> bool:
        return not self._intervals

    @property
    def is_infinite_negative(self) -> bool:
        return bool(self._intervals) and _is_inf_neg(self._intervals[0])

    @property
    def is_infinite_positive(self) -> bool:
        return bool(self._intervals) and _is_inf_pos(self._intervals[-1])

    def contains_interval(self, iv: Interval) -> bool:
        a = ((iv[0], iv[1]),)
        return IntervalSet._is_subset(a, self._intervals)

    def contains_point(self, pt: int) -> bool:
        idx = _get_preceding_interval(self._intervals, pt)
        if idx < 0:
            return False
        _, hi = self._intervals[idx]
        return hi is None or pt <= hi

    @staticmethod
    def _coalesce(carry: Interval, next_iv: Interval, out: list[Interval]) -> Interval:
        # small local coalescer to merge `next_iv` into `carry`.

        pieces = _get_union(carry, next_iv)
        if not pieces:
            return carry

        if len(pieces) == 1:
            return pieces[0]

        # Check for possible contiguity
        a, b = pieces

        # disjoint: append the left piece, keep the right in carry
        if not _get_order(a, b, check_end=False) < 0:
            a, b = b, a
        out.append(a)
        return b

    @staticmethod
    def _get_intervals_union(A: Sequence[Interval] | None, B: Sequence[Interval] | None) -> list[Interval]:
        if not A:
            if not B:
                return []
            return B
        if not B:
            return A

        idx_a = idx_b = 0
        out: list[Interval] = []

        # seed the accumulator ("carry") with the earlier-starting head
        if _get_order(A[0], B[0], check_end=False) < 0:
            carry = A[0]
            idx_a = 1
        else:
            carry = B[0]
            idx_b = 1

        # main two-pointer sweep
        while idx_a < len(A) and idx_b < len(B):
            if _get_order(A[idx_a], B[idx_b], check_end=False) < 0:
                carry = IntervalSet._coalesce(carry, A[idx_a], out)
                if _is_universal(carry):
                    return [carry]
                idx_a += 1
            else:
                carry = IntervalSet._coalesce(carry, B[idx_b], out)
                if _is_universal(carry):
                    return [carry]
                idx_b += 1

        # drain the remainder (still folding—so adjacency across the boundary merges)
        while idx_a < len(A):
            carry = IntervalSet._coalesce(carry, A[idx_a], out)
            if _is_universal(carry):
                return [carry]
            idx_a += 1

        while idx_b < len(B):
            carry = IntervalSet._coalesce(carry, B[idx_b], out)
            if _is_universal(carry):
                return [carry]
            idx_b += 1

        # flush the final carry, and return
        out.append(carry)
        return out

    def union(self, other: IntervalSet) -> IntervalSet:
        ivs = IntervalSet._get_intervals_union(
            self._intervals, other._intervals)
        return IntervalSet(_intervals=tuple(ivs) or ())

    @staticmethod
    def _get_intervals_intersection(A: Sequence[Interval] | None, B: Sequence[Interval] | None) -> list[Interval]:
        """
        Linear-time zipper: walk both coalesced lists and emit overlaps.
        """
        if not A or not B:
            return []

        idx_a = idx_b = 0
        out: list[Interval] = []

        while idx_a < len(A) and idx_b < len(B):
            a, b = A[idx_a], B[idx_b]

            # compute overlap (single interval, possibly empty)
            iv = _get_intersection(a, b)
            if iv is not None:
                out.append(iv)

            # advance the one that ends first (ties: advance both)
            cmp = _get_order(a, b, check_start=False)
            if cmp <= 0:
                idx_a += 1
            if cmp >= 0:
                idx_b += 1

        return out

    def intersection(self, other: IntervalSet) -> IntervalSet:
        ivs = IntervalSet._get_intervals_intersection(
            self._intervals, other._intervals)
        return IntervalSet(_intervals=tuple(ivs) or ())

    @staticmethod
    def _get_intervals_complement(ivs: Sequence[Interval] | None) -> list[Interval]:
        if not ivs:
            return [_universal]
        result = []
        last_iv = ivs[0]
        if not _is_inf_neg(last_iv):
            result.append((None, last_iv[0] - 1))
        for iv in ivs[1:]:
            start = (last_iv[1] + 1)
            end = (iv[0] - 1)
            if (end - start) >= 0:
                result.append((start, end))
            last_iv = iv
        if not _is_inf_pos(ivs[-1]):
            result.append((ivs[-1][1] + 1, None))
        return result

    def complement(self) -> IntervalSet:
        """
        Complement or negation of this set with respect to the full universal domain (−∞, +∞).
        Assumes canonical internal representation. Produces gaps between runs.
        """
        ivs = IntervalSet._get_intervals_complement(self._intervals)
        return IntervalSet(_intervals=tuple(ivs))

    @staticmethod
    def _get_intervals_subtraction(A: Sequence[Interval], B: Sequence[Interval]) -> list[Interval]:
        b_neg = IntervalSet._get_intervals_complement(B)
        return IntervalSet._get_intervals_intersection(A, b_neg)

    def subtraction(self, other: IntervalSet) -> IntervalSet:
        ivs = IntervalSet._get_intervals_subtraction(
            self._intervals, other._intervals)
        return IntervalSet(_intervals=tuple(ivs))

    @staticmethod
    def _is_subset(sub: Sequence[Interval], sup: Sequence[Interval]) -> bool:
        inter = IntervalSet._get_intervals_intersection(sub, sup)
        return (tuple(inter) if inter else ()) == tuple(sub)

    def is_subset_of(self, other: IntervalSet) -> bool:
        return IntervalSet._is_subset(self._intervals, other._intervals)

    @staticmethod
    def _is_proper_subset(sub: Sequence[Interval], sup: Sequence[Interval]) -> bool:
        return IntervalSet._is_subset(sub, sup) and tuple(sub) != tuple(sup)

    def is_proper_subset_of(self, other: IntervalSet) -> bool:
        return IntervalSet._is_proper_subset(self._intervals, other._intervals)

    def __le__(self, other: object) -> bool:
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self.is_subset_of(other)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self.is_proper_subset_of(other)

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return other.__le__(self)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return other.__lt__(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IntervalSet):
            return NotImplemented
        if not self._intervals:
            return not other._intervals
        if not other._intervals:
            return False
        return self._intervals == other._intervals

    def __repr__(self) -> str:
        return f"IntervalSet(_intervals={self._intervals})"

    def __ne__(self, other: IntervalSet) -> bool:
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    def __add__(self, other: object):
        if isinstance(other, IntervalSet):
            return self.union(other)
        if not isinstance(other, int):
            return NotImplemented
        singleton = ((other, other),)
        ivs = IntervalSet._get_intervals_union(self._intervals, singleton)
        return IntervalSet(_intervals=tuple(ivs))

    def __radd__(self, other: object):
        """
        Allow element-to-set via x + set.
        """
        return self.__add__(other)

    def __sub__(self, other: object) -> IntervalSet:
        if isinstance(other, IntervalSet):
            return self.subtraction(other)
        if not isinstance(other, int):
            return NotImplemented
        singleton = ((other, other),)
        ivs = IntervalSet._get_intervals_subtraction(
            self._intervals, singleton)
        return IntervalSet(_intervals=ivs or ())

    def __mul__(self, other: object):
        if isinstance(other, IntervalSet):
            return self.intersection(other)
        if not isinstance(other, int):
            return NotImplemented
        singleton = ((other, other),)
        intersection = IntervalSet._get_intervals_intersection(
            self._intervals, singleton)
        return IntervalSet(_intervals=intersection or ())

    def __rmul__(self, other: object):
        return self.__mul__(other)

    def __or__(self, other: IntervalSet) -> IntervalSet:
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self.union(other)

    def __and__(self, other: IntervalSet) -> IntervalSet:
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self.intersection(other)

    def __xor__(self, other: object) -> IntervalSet:
        if isinstance(other, IntervalSet):
            u = IntervalSet._get_intervals_union(
                self._intervals, other._intervals)
            i = IntervalSet._get_intervals_intersection(
                self._intervals, other._intervals)
        elif not isinstance(other, int):
            return NotImplemented
        else:
            # treat scalars as singletons, consistent with __add__/__sub__/__mul__
            singleton = ((other, other),)
            u = IntervalSet._get_intervals_union(self._intervals, singleton)
            i = IntervalSet._get_intervals_intersection(
                self._intervals, singleton)

        # Your subtraction helper expects lists; coalesce Nones just in case.
        out = IntervalSet._get_intervals_subtraction(tuple(u), tuple(i))
        return IntervalSet(_intervals=tuple(out))

    def __neg__(self) -> IntervalSet:
        return self.complement()

    def __invert__(self) -> IntervalSet:
        return self.complement()

    def __str__(self):
        return self.to_string()

    def __hash__(self):
        h = getattr(self, "_hash", None)
        if h is None:
            h = hash(self._intervals)
            object.__setattr__(self, "_hash", h)
        return h

    # --- In-place (functional) operators -----------------------------------------

    def __ior__(self, other: object) -> IntervalSet | NotImplementedType:
        """
        Functional in-place union: returns a new IntervalSet (does not mutate self).
        Supports IntervalSet and int (singleton) operands.
        """
        if isinstance(other, IntervalSet):
            return self.union(other)
        if isinstance(other, int):
            singleton: Sequence[Interval] = ((other, other),)
            ivs = IntervalSet._get_intervals_union(self._intervals, singleton)
            return IntervalSet(_intervals=tuple(ivs) or ())
        return NotImplemented

    def __iand__(self, other: object) -> IntervalSet | NotImplementedType:
        """
        Functional in-place intersection.
        """
        if isinstance(other, IntervalSet):
            return self.intersection(other)
        if isinstance(other, int):
            singleton: Sequence[Interval] = ((other, other),)
            ivs = IntervalSet._get_intervals_intersection(
                self._intervals, singleton)
            return IntervalSet(_intervals=tuple(ivs) or ())
        return NotImplemented

    def __ixor__(self, other: object) -> IntervalSet | NotImplementedType:
        """
        Functional in-place symmetric difference: (A ∪ B) − (A ∩ B).
        """
        if isinstance(other, IntervalSet):
            u = IntervalSet._get_intervals_union(
                self._intervals, other._intervals)
            i = IntervalSet._get_intervals_intersection(
                self._intervals, other._intervals)
        elif isinstance(other, int):
            singleton: Sequence[Interval] = ((other, other),)
            u = IntervalSet._get_intervals_union(self._intervals, singleton)
            i = IntervalSet._get_intervals_intersection(
                self._intervals, singleton)
        else:
            return NotImplemented
        out = IntervalSet._get_intervals_subtraction(u or [], i or [])
        return IntervalSet(_intervals=tuple(out) or ())

    # --- Iteration over runs ------------------------------------------------------

    def iter_runs(self) -> Iterator[Interval]:
        """
        Yield the stored, canonical runs as (lo, hi) closed intervals.
        This is a zero-allocation view over the internal tuple; callers cannot mutate it.
        """
        # _intervals is a tuple-of-tuples; yielding it is safe (immutable)
        yield from self._intervals

    def __iter__(self) -> Iterator[Interval]:
        """
        Default iteration yields runs, not individual integers.
        Use .iter_values(...) to iterate elements.
        """
        return self.iter_runs()

    # --- Iteration over individual integers ---------------------------------------

    def iter_values(
        self,
        lo: Optional[int] = None,
        hi: Optional[int] = None,
    ) -> Iterator[int]:
        """
        Yield individual integers in the set, optionally clipped to [lo, hi] (closed).

        Examples
        --------
        list(S.iter_values(0, 10))  # safe, finite
        list(S.iter_values())       # only if S is finite. If S is infinite, this will raise.
        """

        # Be careful here. The meaning of hi or lo being None is that the user doesn't care if
        # an Interval is infinite. So (lo == None) and (S is neg-inf) would be an error, just as
        # (hi == None and S is pos-inf) would be an error. But at the same time ((lo,hi),) works
        # as a clipping interval to exclude the parts of S the caller doesn't want.
        clipped = IntervalSet._get_intervals_intersection(
            self._intervals, ((lo, hi),))
        if not clipped:
            return
        if clipped[0][0] is None:
            raise ValueError(
                "negative-infinite iteration lacks starting boundary")
        if clipped[-1][1] is None:
            raise ValueError(
                "positive-infinite iteration lacks ending boundary")
        for iv in clipped:
            for i in range(iv[0], iv[1] + 1):
                yield i

    # -------- serialization/deserialization---------

    def to_string(self) -> str:
        """
        Serialize to a compact, human-friendly wire format.

        Format (v1):
          ()                       -> empty
          ([lo:hi],...)            -> runs (closed intervals)
          [lo|< : hi|>]            -> '<' = -inf, '>' = +inf
          singletons as bare ints  -> e.g., (..., 10, ...), if use_singletons=True

        Examples:
          ([4:5],[7:12])
          ([<:10],[15:>])
          ([<:>])
          ()
          ([4:5],10,15,20,[22:25],28,29)   # with singletons

        The instance is assumed canonical (sorted, disjoint, adjacency-merged).
        """
        if not self._intervals:
            return "()"

        iv_strs: list[str] = []
        for lo, hi in self._intervals:

            if lo is None:
                if hi is None:
                    iv_strs.append("[<:>]")
                else:
                    iv_strs.append(f"[<:{hi}]")
            elif hi is None:
                iv_strs.append(f"[{lo}:>]")
            elif lo == hi:
                iv_strs.append(str(lo))
            elif lo + 1 == hi:
                iv_strs.append(f"{lo},{hi}")
            else:
                iv_strs.append(f"[{lo}:{hi}]")
        return "(" + ",".join(iv_strs) + ")"

    @classmethod
    def from_string(cls, s: str) -> IntervalSet:
        """
        Parse the wire format produced by to_string().

        Grammar (informal):
          intervalset  := '(' [ items ] ')'
          items        := item (',' item)*
          item         := run | int
          run          := '[' bound ':' bound ']'
          bound        := '<' | '>' | int
          int          := '-'? DIGITS
          whitespace   := ignored anywhere outside numbers

        Rules:
          - '<' only appears as a start bound; '>' only as an end bound.
          - '[n:n]' is accepted; it will be canonicalized (and may print as a singleton).
          - Overlaps/adjacencies are allowed in input; result is canonicalized.
        """
        if s is None:
            raise ValueError("from_string: input is None")
        s = s.strip()
        if not (s.startswith("(") and s.endswith(")")):
            raise ValueError(
                f"from_string: must start with '(' and end with ')': {s}")
        inner = s[1:-1].strip()
        if inner == "":
            return cls.from_items([])  # empty

        # Split on commas not inside [...] runs.
        items: list[str] = []
        buf: list[str] = []
        depth = 0
        i = 0
        while i < len(inner):
            ch = inner[i]
            if ch == "[":
                depth += 1
                buf.append(ch)
            elif ch == "]":
                if depth == 0:
                    raise ValueError("from_string: unmatched ']'")
                depth -= 1
                buf.append(ch)
            elif ch == "," and depth == 0:
                token = "".join(buf).strip()
                if token != "":
                    items.append(token)
                buf.clear()
            else:
                buf.append(ch)
            i += 1
        # last token
        token = "".join(buf).strip()
        if token != "":
            items.append(token)
        if depth != 0:
            raise ValueError("from_string: unmatched '['")

        # Parse items -> list of intervals (with None for ±inf)
        parsed: list[Interval] = []
        for tok in items:
            if tok.startswith("["):
                if not tok.endswith("]"):
                    raise ValueError(
                        f"from_string: run missing closing ']': {tok}")
                body = tok[1:-1].strip()
                # split exactly one colon
                parts = body.split(":")
                if len(parts) != 2:
                    raise ValueError(
                        f"from_string: run must contain one ':': {tok}")
                a_raw, b_raw = parts[0].strip(), parts[1].strip()
                # parse bounds
                if a_raw == "<":
                    lo = None
                elif a_raw == ">":
                    raise ValueError(
                        f"from_string: '>' not valid for start bound: {tok}")
                else:
                    try:
                        lo = int(a_raw)
                    except ValueError:
                        raise ValueError(
                            f"from_string: invalid start bound: {tok}") from None

                if b_raw == ">":
                    hi = None
                elif b_raw == "<":
                    raise ValueError(
                        f"from_string: '<' not valid for end bound: {tok}")
                else:
                    try:
                        hi = int(b_raw)
                    except ValueError:
                        raise ValueError(
                            f"from_string: invalid end bound: {tok}") from None

                # Validate finite ordering if both finite
                if lo is not None and hi is not None and lo > hi:
                    raise ValueError(f"from_string: start > end in run: {tok}")

                parsed.append((lo, hi))
            else:
                # singleton integer (allow surrounding whitespace, optional leading '-')
                t = tok.strip()
                if not re.fullmatch(r"-?\d+", t):
                    raise ValueError(
                        f"from_string: invalid integer token: {tok}")
                n = int(t)
                parsed.append((n, n))

        # Canonicalize: sort & coalesce (closed intervals, adjacency merges)
        def start_key(iv: Interval) -> int | float:
            lo, _ = iv
            return float("-inf") if lo is None else lo

        def end_key(iv: Interval) -> int | float:
            _, hi = iv
            return float("inf") if hi is None else hi

        parsed.sort(key=lambda iv: (start_key(iv), end_key(iv)))

        coalesced: list[Interval] = []
        carry: Optional[Interval] = None
        for lo, hi in parsed:
            if carry is None:
                carry = (lo, hi)
                continue
            a_lo, a_hi = carry
            b_lo, b_hi = lo, hi
            # merge if overlap or adjacency; guard None arithmetic
            no_gap = (
                a_hi is None or
                b_lo is None or
                a_hi + 1 >= b_lo
            )
            if no_gap:
                merged_lo = a_lo if (a_lo is None or (
                    b_lo is not None and a_lo <= b_lo)) else b_lo
                # max end with None=+inf
                if a_hi is None or b_hi is None:
                    merged_hi = None
                else:
                    merged_hi = a_hi if a_hi >= b_hi else b_hi
                carry = (merged_lo, merged_hi)
            else:
                coalesced.append(carry)
                carry = (b_lo, b_hi)
        if carry is not None:
            coalesced.append(carry)

        return cls(_intervals=tuple(coalesced))
