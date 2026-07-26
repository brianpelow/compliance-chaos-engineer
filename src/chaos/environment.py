"""The simulated environment a chaos experiment runs against.

A system-of-record the engine fully owns: services with governance state
(authorization, change records, registered models, audit trails, control
health, change windows). A failure injection mutates this state to create a
violation; the detection pass then reads it back. Nothing here touches real
infrastructure, which is what makes the experiments safe to run and
deterministic to test.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ServiceState:
    """The governance-relevant state of one service."""

    service_id: str
    name: str
    criticality: str  # consequential | supporting | advisory
    # Governance flags. In a healthy environment these hold; a failure
    # injection flips one to create a violation.
    deployment_authorized: bool = True
    has_change_record: bool = True
    model_registered: bool = True
    audit_trail_written: bool = True
    change_window_open: bool = True
    # Which controls are currently active. A disabled-control failure removes
    # an entry from this set.
    active_controls: set[str] = field(default_factory=set)

    def snapshot(self) -> dict:
        return {
            "service_id": self.service_id,
            "name": self.name,
            "criticality": self.criticality,
            "deployment_authorized": self.deployment_authorized,
            "has_change_record": self.has_change_record,
            "model_registered": self.model_registered,
            "audit_trail_written": self.audit_trail_written,
            "change_window_open": self.change_window_open,
            "active_controls": sorted(self.active_controls),
        }


ALL_CONTROLS: tuple[str, ...] = (
    "deployment_authorization_gate",
    "change_record_required",
    "model_registry_check",
    "audit_trail_required",
    "control_health_monitor",
    "change_window_enforced",
)


def healthy_service(service_id: str, name: str, criticality: str) -> ServiceState:
    """A service in full compliance, with every control active."""
    return ServiceState(
        service_id=service_id,
        name=name,
        criticality=criticality,
        active_controls=set(ALL_CONTROLS),
    )


def seed_environment() -> dict[str, ServiceState]:
    """A deterministic starting environment of healthy services."""
    services = [
        healthy_service("payments-api", "Payments API", "consequential"),
        healthy_service("fraud-scorer", "Fraud Scoring Service", "consequential"),
        healthy_service("notification-worker", "Notification Worker", "supporting"),
        healthy_service("reporting-dashboard", "Reporting Dashboard", "advisory"),
    ]
    return {s.service_id: s for s in services}