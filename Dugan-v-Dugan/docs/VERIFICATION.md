# Verification snapshot

Date: 2026-10-29. Runtime: Python 3.13.5.

- `python -m unittest discover -s Dugan-v-Dugan/tests -v`: 33 tests passed.
- `python Dugan-v-Dugan/bench.py validate`: 12 cases and 3 profiles validated.
- Full `demo`: 180 mock calls completed. Reported model tokens: 0.
- Both probability-change diagnostics were 0 for the constant-response mock.
- Semantic fidelity, author fidelity, and reasoning-quality scores were null.

Checks cover deterministic execution, evidence-fork isolation, synchronous peer
exchange, hidden evaluator labels, source hashes, invalid citations, budget
limits, response validation, failure records, metadata blinding, the stdio
bridge, paired effects, missing pairs, family weighting, and reviewer coverage.

These are local offline and subprocess checks. No live language model was
evaluated, no manuscripts were loaded, and no adapter was trained. Python 3.10
is the declared minimum; this snapshot was executed on Python 3.13.5 only.
