# Contributing

## Setup

```bash
uv sync --all-extras
uv run pytest
uv run ruff check src tests
```

## The determinism rule

Experiments must stay deterministic. No randomness, no wall-clock dependence, no network. The same run must always produce the same scorecard.

## Adding a failure class

1. Add it to `FailureClass` and the `CATALOG` in `src/chaos/failures.py`.
2. Add its injector in `src/chaos/inject.py` -- a single-mutation change.
3. If it should be detectable, add a control in `src/chaos/controls.py` and name it as the failure's `expected_control`. If it is a blind spot, name no control and document why.
4. Add a detection test either way.

## The honesty rule

Do not add a control that makes compound evasion appear detected. A point-in-time check that claims to catch a trajectory-level violation is a false positive, and false positives in a governance tool are worse than misses. See ADR 0002.
