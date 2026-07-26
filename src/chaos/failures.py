"""The governance failure classes.

Each class is a specific, named way that governance can fail in a regulated
system. These are the "chaos experiments": a controlled injection of a known
violation whose detection can then be measured.

The premise, drawn from hard experience building governance controls: a control
that has never been tested against a deliberate failure is not a control, it is
a hope. This module enumerates the failures worth hoping against.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """How much damage an undetected instance of this failure can do."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


class FailureClass(str, Enum):
    """The six governance failure classes this engine can inject."""

    UNAUTHORIZED_DEPLOYMENT = "unauthorized_deployment"
    MISSING_CHANGE_RECORD = "missing_change_record"
    UNREGISTERED_MODEL = "unregistered_model"
    ABSENT_AUDIT_TRAIL = "absent_audit_trail"
    DISABLED_CONTROL = "disabled_control"
    CRITICALITY_WINDOW_VIOLATION = "criticality_window_violation"
    COMPOUND_EVASION = "compound_evasion"


@dataclass(frozen=True)
class FailureDefinition:
    """A description of one failure class: what it is and why it matters."""

    failure_class: FailureClass
    title: str
    description: str
    severity: Severity
    # The control that is supposed to catch this failure. Naming the expected
    # detector is what lets a miss be attributed rather than merely counted.
    expected_control: str
    blast_radius: str


# The catalog. Each entry pairs a failure with the control that should stop it,
# mirroring the GOV rules enforced by the governance gateway.
CATALOG: dict[FailureClass, FailureDefinition] = {
    FailureClass.UNAUTHORIZED_DEPLOYMENT: FailureDefinition(
        failure_class=FailureClass.UNAUTHORIZED_DEPLOYMENT,
        title="Unauthorized production deployment",
        description=(
            "A deployment reaches production without the authorization that "
            "policy requires -- no approval, no gate, no record of who allowed it."
        ),
        severity=Severity.CRITICAL,
        expected_control="deployment_authorization_gate",
        blast_radius=(
            "Unreviewed code in production. In a regulated system this is the "
            "failure that turns into an incident and then into a finding."
        ),
    ),
    FailureClass.MISSING_CHANGE_RECORD: FailureDefinition(
        failure_class=FailureClass.MISSING_CHANGE_RECORD,
        title="Change with no change record",
        description=(
            "A production change is made with no corresponding change record, "
            "leaving no evidence that it was reviewed or approved."
        ),
        severity=Severity.HIGH,
        expected_control="change_record_required",
        blast_radius=(
            "An examiner asking 'who approved this change' has no answer. The "
            "change may be fine; the absence of evidence is the problem."
        ),
    ),
    FailureClass.UNREGISTERED_MODEL: FailureDefinition(
        failure_class=FailureClass.UNREGISTERED_MODEL,
        title="Unregistered model in production",
        description=(
            "A model version is serving decisions without being recorded in the "
            "model registry, so its identity and lineage are unknown."
        ),
        severity=Severity.CRITICAL,
        expected_control="model_registry_check",
        blast_radius=(
            "A decision cannot be replayed because the model that made it cannot "
            "be identified. This defeats the entire replay imperative."
        ),
    ),
    FailureClass.ABSENT_AUDIT_TRAIL: FailureDefinition(
        failure_class=FailureClass.ABSENT_AUDIT_TRAIL,
        title="Consequential action with no audit trail",
        description=(
            "A consequential action executes without writing a decision record, "
            "leaving no reconstructable account of what happened."
        ),
        severity=Severity.CRITICAL,
        expected_control="audit_trail_required",
        blast_radius=(
            "The action is unreplayable. For a consequential decision in a "
            "regulated context this is an existential compliance gap."
        ),
    ),
    FailureClass.DISABLED_CONTROL: FailureDefinition(
        failure_class=FailureClass.DISABLED_CONTROL,
        title="Silently disabled control",
        description=(
            "A governing control is switched off without notice, so violations "
            "it would normally catch pass through unimpeded."
        ),
        severity=Severity.HIGH,
        expected_control="control_health_monitor",
        blast_radius=(
            "Every failure the control was meant to catch is now invisible. The "
            "gap is silent, which is what makes it dangerous."
        ),
    ),
    FailureClass.CRITICALITY_WINDOW_VIOLATION: FailureDefinition(
        failure_class=FailureClass.CRITICALITY_WINDOW_VIOLATION,
        title="Consequential change outside a change window",
        description=(
            "A change to a consequential service is made outside any approved "
            "change window, bypassing the timing control."
        ),
        severity=Severity.MEDIUM,
        expected_control="change_window_enforced",
        blast_radius=(
            "A high-stakes change lands at an unreviewed time, when fewer people "
            "are watching and rollback support is thin."
        ),
    ),
    FailureClass.COMPOUND_EVASION: FailureDefinition(
        failure_class=FailureClass.COMPOUND_EVASION,
        title="Compound evasion across individually-compliant actions",
        description=(
            "Two or more actions, each individually passing every control, that "
            "together constitute a violation no single action would. A change "
            "split into separately-approved parts that combine into something "
            "neither approval covered."
        ),
        severity=Severity.CRITICAL,
        expected_control="(none -- this is a known blind spot)",
        blast_radius=(
            "The violation is in the relationship between actions, not in any "
            "single action's state. Point-in-time control checks cannot see it. "
            "Detecting it requires trajectory-level analysis this control model "
            "does not perform. This is a deliberate demonstration of a real "
            "limit, not an oversight."
        ),
    ),
}


def all_failures() -> list[FailureDefinition]:
    """Every failure class, in a stable order."""
    return [CATALOG[fc] for fc in FailureClass]


def get(failure_class: FailureClass) -> FailureDefinition:
    return CATALOG[failure_class]