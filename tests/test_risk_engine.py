from apex.risk.risk_engine import RiskEngine


def test_position_size_respects_risk_limits():
    engine = RiskEngine(
        strategy_capital=1000,
        risk_per_trade=0.01,
        max_position_pct=0.20,
    )

    result = engine.calculate_position_size(
        entry_price=100,
        stop_price=95,
    )

    assert result.dollar_risk <= 10.01
    assert result.position_value <= 200.01
    assert result.shares > 0
