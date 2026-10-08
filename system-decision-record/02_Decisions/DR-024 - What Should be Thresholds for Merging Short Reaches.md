#network-modification
## Description
This decision defines thresholds for alternatives in [[DR-023 - How to Deal with Short Reaches]].

Both alternatives below assume the junction exclusion resolved in [[DR-023 - How to Deal with Short Reaches]] ALT-B: a reach is only a merge candidate if it has exactly one upstream reach, so a confluence is not merged across.

## Alternatives

### ALT-A - 5% Drainage Area Difference, Upto 5 km

Length threshold here is read as a **ceiling** meaning walking upstream from a reach, keep merging until the combined length stays under the limit, and stop before exceeding it.

### ALT-B - 5% Drainage Area Difference, 5 km Minimum Merged Length
#current

Same 5% drainage-area criterion, measured against the drainage area of the reach the chain started from rather than the immediate neighbour. Three revisions to ALT-A:

**The length threshold is a floor, not a ceiling.** Merging continues *until* the chain clears the threshold, then stops. ALT-A's reading stopped short of it.

## Decision History
- 2026-02-09: First selection of ALT-A based on judgement
- 2026-08-12: Switched to ALT-B.
