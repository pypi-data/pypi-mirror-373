# drange

Discrete interval algebra on **integers** (with +/- infinity), stored as coalesced runs.

- Fast set-like operations over huge or infinite sets of integers.
- Canonical internal form: sorted, disjoint, adjacency-merged **closed** intervals.
- Human-readable serialization with simple round-trips.
- Hashable, fully typed, and tested.

> Examples:
([1:3],[7:9])           # {1,2,3,7,8,9}
()                      # empty
([<:>])                 # universal
([<:5],[7:12])          # negative infinity to 5, plus 7 through 12
([-10:>])               # all naturals from -10 to positive infinity
(4,5,10,20,[22:25])     # singletons amid runs. Note 4 and 5
([4:5],10,20,[22:25])   # [4:5] would also be valid
---

## Install

```bash
pip install drange

## How-tos

### Import
from drange.interval_set import IntervalSet

### Build from disparate sources:
A = IntervalSet.from_items([1,2,2,3,10,11,12])  # -> ([1:3],[10:12])
B = IntervalSet.from_string("([<:0],[100:>])")

### Merge adjacent and overlapping ranges:
A = IntervalSet.from_string("([1:3],[4:6])")
assert A.to_string() == "([1:6])"

### Compute complement within a finite window
S = IntervalSet.from_string("([2:5],[9:10])")
neg = ~S                                    # -> ([<:1],[6:8],[11:>])
list_not_S = list(neg.iter_values(0,12))    # -> [0,1,6,7,8,11,12]
S_not = IntervalSet.from_items(list_not_s)  # -> (0,1,[6:8],11,12)

### Subset checks (allowing infinities)
A = IntervalSet.from_string("([<:10])")
B = IntervalSet.from_string("([<:20])")
assert A <= B and A < B

### Equality
A = IntervalSet.from_string("([1:4])")
B = IntervalSet.from_string("([3:6])")
lhs = A ^ B
rhs = (A | B) - (A & B)
assert lhs == rhs

### Serialization/deserialization
s = "([4:5],10,15,20,[22:25],[28:29])"
iv_set = IntervalSet.from_string(s)
assert iv_set.to_string() == s


## Performance notes
- Operations are linear in the number of stored runs (`r`), not in the number of elements.
- Union/intersection/difference/symmetric-difference: O(A.r + B.r)
- Membership test: O(log r) via binary search on starts.
- Memory scales with the number of runs, not elements.

## License
MIT. See LICENSE

## Changelog
See CHANGELOG.md. Current release: 0.1.0
