import pytest
from backend.core import StrategyRegistry, DataQualityGate, RiskGate, DecisionEngine, AIValidation


def test_registry_contains_377_core_and_25_advanced():
    registry = StrategyRegistry()
    assert registry.count_core() == 377
    assert registry.count_advanced() == 25
    assert len(registry.all()) == 402


def test_stale_or_missing_oi_volume_blocks_signal():
    gate = DataQualityGate(max_age_seconds=5)
    result = gate.check(age_seconds=9, has_oi=False, has_volume=False, duplicate=False)
    assert result.ok is False
    assert "STALE" in result.flags
    assert "MISSING_OI" in result.flags
    assert "MISSING_VOLUME" in result.flags


def test_single_rr_gate_is_the_only_risk_gate():
    assert RiskGate(min_rr=1.8).passes(1.8)
    assert RiskGate(min_rr=1.8).passes(2.0)
    assert not RiskGate(min_rr=1.8).passes(1.79)


def test_decision_does_not_pad_to_five_plans():
    engine = DecisionEngine(min_plans=5, risk_gate=RiskGate(1.8))
    plans = [
        {"side": "CALL", "strike": 25000, "entry": 100, "sl": 80, "target": 140, "rr": 2.0, "strategy_ids": ["S001"]}
    ]
    decision = engine.build(plans, ai=AIValidation(wait_override=False))
    assert len(decision.plans) == 1
    assert decision.suppressed_count == 0
    assert decision.verdict == "CALL BUY"


def test_ai_wait_override_forces_wait_without_inventing_trade_fields():
    engine = DecisionEngine(min_plans=5, risk_gate=RiskGate(1.8))
    plans = [{"side": "CALL", "strike": 25000, "entry": 100, "sl": 80, "target": 140, "rr": 2.0, "strategy_ids": ["S001"]}]
    decision = engine.build(plans, ai=AIValidation(wait_override=True))
    assert decision.verdict == "WAIT"


def test_ui_contract_has_exactly_30_screens():
    from backend.ui_contract import SCREENS
    assert len(SCREENS) == 30
    assert SCREENS[0]["title"] == "Splash / Launch"
    assert SCREENS[-1]["title"] == "Help / Education"
