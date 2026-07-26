"""Each control must fire on its violation and stay silent otherwise.

A control that always fires is not a detector, it is an alarm stuck on. A
control that never fires is decorative. Both cases are tested.
"""

from __future__ import annotations

from chaos.controls import run_all_controls
from chaos.environment import healthy_service
from chaos.failures import FailureClass
from chaos.inject import inject


def fresh():
    return healthy_service("svc", "Service", "consequential")


def test_healthy_service_triggers_no_controls():
    """A fully compliant service should trip nothing."""
    assert run_all_controls(fresh()) == []


def test_unauthorized_deployment_detected():
    svc = inject(fresh(), FailureClass.UNAUTHORIZED_DEPLOYMENT)
    assert "deployment_authorization_gate" in run_all_controls(svc)


def test_missing_change_record_detected():
    svc = inject(fresh(), FailureClass.MISSING_CHANGE_RECORD)
    assert "change_record_required" in run_all_controls(svc)


def test_unregistered_model_detected():
    svc = inject(fresh(), FailureClass.UNREGISTERED_MODEL)
    assert "model_registry_check" in run_all_controls(svc)


def test_absent_audit_trail_detected():
    svc = inject(fresh(), FailureClass.ABSENT_AUDIT_TRAIL)
    assert "audit_trail_required" in run_all_controls(svc)


def test_criticality_window_violation_detected():
    svc = inject(fresh(), FailureClass.CRITICALITY_WINDOW_VIOLATION)
    assert "change_window_enforced" in run_all_controls(svc)


def test_each_control_fires_only_on_its_own_violation():
    """Injecting one failure should trip exactly one control (in the simple cases)."""
    single_control_failures = [
        (FailureClass.UNAUTHORIZED_DEPLOYMENT, "deployment_authorization_gate"),
        (FailureClass.MISSING_CHANGE_RECORD, "change_record_required"),
        (FailureClass.UNREGISTERED_MODEL, "model_registry_check"),
        (FailureClass.ABSENT_AUDIT_TRAIL, "audit_trail_required"),
        (FailureClass.CRITICALITY_WINDOW_VIOLATION, "change_window_enforced"),
    ]
    for failure_class, expected in single_control_failures:
        firing = run_all_controls(inject(fresh(), failure_class))
        assert firing == [expected], f"{failure_class.value}: expected only {expected}, got {firing}"


def test_change_window_control_ignores_non_consequential():
    """The window control only applies to consequential services."""
    svc = healthy_service("svc", "Service", "supporting")
    svc.change_window_open = False
    assert "change_window_enforced" not in run_all_controls(svc)


def test_disabled_control_cannot_detect():
    """A control removed from the active set cannot fire, even on its violation."""
    svc = fresh()
    svc.deployment_authorized = False           # a real violation
    svc.active_controls.discard("deployment_authorization_gate")  # but the control is off
    assert "deployment_authorization_gate" not in run_all_controls(svc)