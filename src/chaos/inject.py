"""Failure injection.

Each injector takes a healthy service and mutates exactly one aspect of its
state to create exactly one violation. Keeping each injection to a single
mutation is what lets detection be attributed cleanly: if a control fails to
fire, the injected failure is unambiguous.
"""

from __future__ import annotations

from chaos.environment import ServiceState
from chaos.failures import FailureClass


def inject(service: ServiceState, failure_class: FailureClass) -> ServiceState:
    """Apply one failure to a service, returning the mutated state.

    The service is mutated in place and also returned for convenience.
    """
    if failure_class is FailureClass.UNAUTHORIZED_DEPLOYMENT:
        service.deployment_authorized = False
    elif failure_class is FailureClass.MISSING_CHANGE_RECORD:
        service.has_change_record = False
    elif failure_class is FailureClass.UNREGISTERED_MODEL:
        service.model_registered = False
    elif failure_class is FailureClass.ABSENT_AUDIT_TRAIL:
        service.audit_trail_written = False
    elif failure_class is FailureClass.DISABLED_CONTROL:
        # Silently remove the control that a real attacker would disable to
        # hide their tracks. We disable the audit trail control as the
        # canonical case: it is the one whose absence is hardest to notice.
        service.active_controls.discard("audit_trail_required")
    elif failure_class is FailureClass.CRITICALITY_WINDOW_VIOLATION:
        service.change_window_open = False
    elif failure_class is FailureClass.COMPOUND_EVASION:
        # Deliberately mutate nothing that a point-in-time control checks. The
        # violation lives in the relationship between two individually-compliant
        # actions, which this state model does not represent. The service looks
        # fully compliant on every checked field -- and that is exactly why the
        # controls miss it.
        pass
    else:
        raise ValueError(f"Unknown failure class: {failure_class}")
    return service