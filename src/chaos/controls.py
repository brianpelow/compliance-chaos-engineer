"""The control model: the detectors that are supposed to catch each failure.

Each control is a deterministic predicate over a service's state. It returns
True when it detects a violation. A control only fires if it is active; a
disabled control cannot detect anything, which is precisely what makes the
disabled-control failure class dangerous and worth testing.

These controls mirror the GOV rules enforced by the governance gateway, but the
model is self-contained so this repo stands alone. The correspondence is noted
in the scorecard rather than created by importing the gateway.
"""

from __future__ import annotations

from collections.abc import Callable

from chaos.environment import ServiceState

# A control detects a violation in a service's state. Returns True on detection.
Detector = Callable[[ServiceState], bool]


def _active(service: ServiceState, control: str) -> bool:
    return control in service.active_controls


def deployment_authorization_gate(service: ServiceState) -> bool:
    """Detects a deployment that was not authorized."""
    if not _active(service, "deployment_authorization_gate"):
        return False
    return not service.deployment_authorized


def change_record_required(service: ServiceState) -> bool:
    """Detects a change made without a change record."""
    if not _active(service, "change_record_required"):
        return False
    return not service.has_change_record


def model_registry_check(service: ServiceState) -> bool:
    """Detects a model serving without being registered."""
    if not _active(service, "model_registry_check"):
        return False
    return not service.model_registered


def audit_trail_required(service: ServiceState) -> bool:
    """Detects a consequential action with no audit trail written."""
    if not _active(service, "audit_trail_required"):
        return False
    return not service.audit_trail_written


def control_health_monitor(service: ServiceState) -> bool:
    """Detects that a control that should be active is missing.

    This is the meta-control: the one that catches a silently disabled control.
    It compares the active set against the full expected set. It cannot detect
    its own absence -- a limitation the scorecard names explicitly.
    """
    if not _active(service, "control_health_monitor"):
        return False
    from chaos.environment import ALL_CONTROLS

    expected = set(ALL_CONTROLS)
    return service.active_controls != expected


def change_window_enforced(service: ServiceState) -> bool:
    """Detects a consequential change made outside a change window."""
    if not _active(service, "change_window_enforced"):
        return False
    if service.criticality != "consequential":
        return False
    return not service.change_window_open


# The control registry, keyed by the name each failure names as its expected
# detector. Evaluation order is stable for reproducibility.
CONTROLS: dict[str, Detector] = {
    "deployment_authorization_gate": deployment_authorization_gate,
    "change_record_required": change_record_required,
    "model_registry_check": model_registry_check,
    "audit_trail_required": audit_trail_required,
    "control_health_monitor": control_health_monitor,
    "change_window_enforced": change_window_enforced,
}


def run_all_controls(service: ServiceState) -> list[str]:
    """Return the names of every control that fires on this service state."""
    return [name for name, detector in CONTROLS.items() if detector(service)]