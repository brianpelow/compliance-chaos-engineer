# compliance-chaos-engineer

> Chaos engineering for governance controls. Deliberately inject governance failures into a simulated environment, then measure whether the controls detect them. The output is a detection scorecard -- including the failures that are missed.

![CI](https://github.com/brianpelow/compliance-chaos-engineer/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)

## The idea

Netflix proved their infrastructure was resilient by breaking it on purpose with Chaos Monkey. This does the same for governance controls.

It injects a specific governance failure -- an unauthorized deployment, a change with no record, an unregistered model, an action with no audit trail, a silently disabled control -- into a simulated environment, then runs the controls and records whether the one that should have caught it did.

The premise, learned from building governance controls that turned out to be wrong: **a control that has never been tested against a deliberate failure is not a control, it is a hope.** This measures the hope.

## Why the scorecard is not 100%

A chaos engine that reports perfect detection is not testing anything. If every failure you can imagine is caught, you have not imagined enough failures.

This engine includes a seventh failure class it deliberately cannot catch: **compound evasion**, where two individually-compliant actions combine into a violation no single point-in-time check can see. Every field the controls inspect reads compliant; the violation lives in the relationship between actions. Detecting it would require trajectory-level analysis this control model does not perform.

So the scorecard reads **85.7% (6 of 7)**, with one critical miss, named and attributed. That miss is the most honest thing in the repo. It is drawn from a real open problem in AI governance replay -- see [ai-governance-framework/UNSOLVED.md](https://github.com/brianpelow/ai-governance-framework/blob/main/UNSOLVED.md).

## Run it

```bash
uv sync
uv run chaos run
```

```bash
uv run chaos list          # the failure classes
uv run chaos run --json    # machine-readable scorecard
uv run chaos run --out scorecard.json
```

## The failure classes

| Failure | Severity | Expected control |
|---------|----------|------------------|
| Unauthorized production deployment | critical | deployment_authorization_gate |
| Change with no change record | high | change_record_required |
| Unregistered model in production | critical | model_registry_check |
| Consequential action with no audit trail | critical | audit_trail_required |
| Silently disabled control | high | control_health_monitor |
| Consequential change outside a change window | medium | change_window_enforced |
| Compound evasion across compliant actions | critical | (none -- known blind spot) |

## How it works

The engine is deterministic. The same run always produces the same scorecard -- an experiment whose result changes between runs is not evidence. Each failure is a single-mutation injection into a simulated service, so a missed detection is unambiguously attributable to the control that should have fired. No language model participates.

The control model mirrors the GOV rules enforced by [mcp-governance-gateway](https://github.com/brianpelow/mcp-governance-gateway), the enforcement counterpart to this repo. Where the gateway blocks violations, this engine tries to slip them past. The two are attacker and defender over the same governance model.

## Design decisions

- [0001](./docs/adr/0001-deterministic-experiments.md) -- Experiments are deterministic
- [0002](./docs/adr/0002-a-designed-blind-spot.md) -- The engine includes a failure it cannot detect

## Related work

| Repo | Relationship |
|------|-------------|
| [mcp-governance-gateway](https://github.com/brianpelow/mcp-governance-gateway) | The enforcement counterpart. This engine attacks what that one defends. |
| [ai-governance-framework](https://github.com/brianpelow/ai-governance-framework) | Source of the replay imperative and the compound-evasion blind spot |
| [code-compliance-auditor](https://github.com/brianpelow/code-compliance-auditor) | The deterministic-tooling discipline this follows |

## License

Apache 2.0
