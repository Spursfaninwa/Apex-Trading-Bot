from dataclasses import dataclass


@dataclass
class RegimeSignal:
    regime: str
    max_positions: int
    risk_multiplier: float
    allow_new_positions: bool


def build_regime_signal(regime: str) -> RegimeSignal:
    if regime == "BULL":
        return RegimeSignal(
            regime="BULL",
            max_positions=8,
            risk_multiplier=1.5,
            allow_new_positions=True,
        )

    if regime == "RISK_OFF":
        return RegimeSignal(
            regime="RISK_OFF",
            max_positions=0,
            risk_multiplier=0.0,
            allow_new_positions=False,
        )

    return RegimeSignal(
        regime="NEUTRAL",
        max_positions=3,
        risk_multiplier=0.75,
        allow_new_positions=True,
    )
