# 0001. Chaos experiments are deterministic

**Status:** Accepted

## Context

Infrastructure chaos engineering is often randomized: kill a random instance, inject random latency. Randomness suits resilience testing, where the goal is broad coverage over many runs.

Governance chaos has a different goal: producing evidence. An examiner or an engineer needs to know exactly which failure was injected and exactly which control did or did not catch it. A result that changes between runs cannot serve as evidence.

## Decision

Every experiment is deterministic. Each failure is a single, specified mutation of a known starting state. The control evaluation is a set of pure predicates. The same run always produces the same scorecard.

## Consequences

**Gained:** The scorecard is reproducible and citable. A missed detection is attributable to a specific control, because the injection changed exactly one thing.

**Accepted:** This engine does not discover unknown failure modes the way randomized fuzzing might. It tests a known catalog thoroughly rather than searching for surprises. Those are different tools; this is the evidence-producing one.
