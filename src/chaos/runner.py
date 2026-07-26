"""The experiment runner and scorecard.

An experiment: take a healthy service, inject one governance failure, run every
control, and record whether the control that was supposed to catch it did.

The output is a detection scorecard -- not a pass/fail, but a measured
detection rate across failure classes, with each miss attributed to the control
that should have fired. A missed detection is a governance gap with a name and a
blast radius, which is more actionable than a single aggregate number.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from chaos.controls import run_all_controls
from chaos.environment import ServiceState, healthy_service
from chaos.failures import CATALOG, FailureClass, Severity, all_failures
from chaos.inject import inject


@dataclass
class ExperimentResult:
    """The outcome of injecting one failure into one service."""

    failure_class: str
    title: str
    severity: str
    expected_control: str
    detected: bool
    firing_controls: list[str]
    blast_radius: str

    @property
    def status(self) -> str:
        return "DETECTED" if self.detected else "MISSED"


@dataclass
class Scorecard:
    """The aggregate result of a chaos run."""

    results: list[ExperimentResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def detected(self) -> int:
        return sum(1 for r in self.results if r.detected)

    @property
    def missed(self) -> list[ExperimentResult]:
        return [r for r in self.results if not r.detected]

    @property
    def detection_rate(self) -> float:
        return round(100 * self.detected / self.total, 1) if self.total else 0.0

    @property
    def critical_misses(self) -> list[ExperimentResult]:
        return [r for r in self.missed if r.severity == Severity.CRITICAL.value]

    def to_dict(self) -> dict:
        return {
            "total_experiments": self.total,
            "detected": self.detected,
            "missed": len(self.missed),
            "detection_rate": self.detection_rate,
            "critical_misses": len(self.critical_misses),
            "results": [
                {
                    "failure_class": r.failure_class,
                    "title": r.title,
                    "severity": r.severity,
                    "expected_control": r.expected_control,
                    "status": r.status,
                    "firing_controls": r.firing_controls,
                    "blast_radius": r.blast_radius,
                }
                for r in self.results
            ],
        }


def run_experiment(
    failure_class: FailureClass,
    service: ServiceState | None = None,
) -> ExperimentResult:
    """Inject one failure into a fresh service and measure detection."""
    definition = CATALOG[failure_class]
    # A consequential service so criticality-gated controls apply.
    subject = service or healthy_service("subject", "Test Subject", "consequential")

    inject(subject, failure_class)
    firing = run_all_controls(subject)
    detected = definition.expected_control in firing

    return ExperimentResult(
        failure_class=failure_class.value,
        title=definition.title,
        severity=definition.severity.value,
        expected_control=definition.expected_control,
        detected=detected,
        firing_controls=firing,
        blast_radius=definition.blast_radius,
    )


def run_all() -> Scorecard:
    """Run every failure class and return the full scorecard."""
    card = Scorecard()
    for definition in all_failures():
        card.results.append(run_experiment(definition.failure_class))
    return card