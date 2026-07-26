# 0002. The engine includes a failure it cannot detect

**Status:** Accepted

## Context

The first working version detected every failure it injected: a 100% scorecard. This felt like success and was actually a defect.

A chaos engine whose controls catch every failure it can generate is not measuring resilience. It is measuring the fact that each failure was built with a matching control. The scorecard was tautological.

A governance tool that always reports full coverage is worse than useless, because it manufactures false confidence -- the exact failure mode described in the governance framework's field notes, where a control that cannot fail teaches people to stop checking.

## Decision

The catalog includes compound evasion: a failure that keeps every checked field compliant, so no point-in-time control can detect it. The violation lives in the relationship between two individually-approved actions, which the state model does not represent.

This is not a control gap to be fixed later. It is a permanent, documented demonstration that point-in-time controls have a blind spot, drawn from a real open problem in replay and trajectory analysis.

## Consequences

**Gained:** The scorecard is honest. It reports 6 of 7 with one critical miss, and the miss is the most informative line in the output. The tool demonstrates that it can find a gap, which is the entire point of a chaos engine.

**Accepted:** A reader skimming for a headline number sees 85.7% rather than 100%. That is the correct number, and explaining why is more valuable than the higher figure would have been.

**Guarded:** A test asserts that compound evasion stays undetected. If a future change makes it appear detected, that is far more likely to be a false positive than a genuine advance, and the test forces that to be examined rather than celebrated.
