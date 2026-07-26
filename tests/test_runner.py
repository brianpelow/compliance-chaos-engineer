"""The experiment runner and scorecard behavior."""

from __future__ import annotations

from chaos.failures import FailureClass
from chaos.runner import run_all, run_experiment


def test_every_simple_failure_is_detected():
    """The five directly-controlled failures should all be caught."""
    for fc in [
        FailureClass.UNAUTHORIZED_DEPLOYMENT,
        FailureClass.MISSING_CHANGE_RECORD,
        FailureClass.UNREGISTERED_MODEL,
        FailureClass.ABSENT_AUDIT_TRAIL,
        FailureClass.CRITICALITY_WINDOW_VIOLATION,
    ]:
        result = run_experiment(fc)
        assert result.detected, f"{fc.value} should be detected"


def test_disabled_control_is_caught_by_health_monitor():
    """When a control is silently disabled, the health monitor should catch it.

    The disabled-control failure removes the audit-trail control. The control
    health monitor compares the active set to the expected set and fires. So the
    failure IS detected -- but by the meta-control, not by the audit control the
    failure disabled.
    """
    result = run_experiment(FailureClass.DISABLED_CONTROL)
    assert result.detected
    assert result.expected_control == "control_health_monitor"
    assert "control_health_monitor" in result.firing_controls


def test_scorecard_aggregates():
    card = run_all()
    assert card.total == 7
    assert 0 <= card.detected <= 7
    assert 0.0 <= card.detection_rate <= 100.0


def test_scorecard_is_deterministic():
    """The whole point: same run, same scorecard."""
    a = run_all().to_dict()
    b = run_all().to_dict()
    assert a == b


def test_scorecard_serializes():
    card = run_all()
    d = card.to_dict()
    assert "detection_rate" in d
    assert len(d["results"]) == 7
    for r in d["results"]:
        assert r["status"] in ("DETECTED", "MISSED")


def test_result_status_matches_detection():
    result = run_experiment(FailureClass.UNAUTHORIZED_DEPLOYMENT)
    assert result.status == ("DETECTED" if result.detected else "MISSED")


def test_compound_evasion_is_not_detected():
    """The blind spot must genuinely be a blind spot.

    Compound evasion keeps every checked field compliant, so no point-in-time
    control fires. This is a deliberate demonstration of a real limit. If a
    future change makes this test pass by "detecting" it, that detection is
    almost certainly a false positive and should be scrutinized.
    """
    from chaos.failures import FailureClass
    result = run_experiment(FailureClass.COMPOUND_EVASION)
    assert not result.detected
    assert result.firing_controls == []


def test_scorecard_reports_the_known_gap():
    """The scorecard should surface exactly one miss, and it should be critical."""
    card = run_all()
    assert len(card.missed) == 1
    assert len(card.critical_misses) == 1
    assert card.missed[0].failure_class == "compound_evasion"


def test_detection_rate_reflects_the_gap():
    """Six of seven detected is the honest number."""
    card = run_all()
    assert card.detected == 6
    assert card.detection_rate == 85.7
