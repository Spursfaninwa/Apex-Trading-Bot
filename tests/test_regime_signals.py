from apex.signals.regime_signals import build_regime_signal


def test_bull_regime():
    signal = build_regime_signal("BULL")

    assert signal.regime == "BULL"
    assert signal.max_positions == 8
    assert signal.risk_multiplier == 1.5
    assert signal.allow_new_positions is True


def test_neutral_regime():
    signal = build_regime_signal("NEUTRAL")

    assert signal.regime == "NEUTRAL"
    assert signal.max_positions == 3
    assert signal.risk_multiplier == 0.75
    assert signal.allow_new_positions is True


def test_risk_off_regime():
    signal = build_regime_signal("RISK_OFF")

    assert signal.regime == "RISK_OFF"
    assert signal.max_positions == 0
    assert signal.risk_multiplier == 0.0
    assert signal.allow_new_positions is False
