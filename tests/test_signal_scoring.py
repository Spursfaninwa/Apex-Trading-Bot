from apex.strategies.signal_scoring import score_momentum_candidate


def test_strong_momentum_scores_positive():
    candidate = {
        "symbol": "TEST",
        "momentum_30d": 35,
        "trend_strength": 2,
        "volatility": 2,
    }

    assert score_momentum_candidate(candidate) > 0


def test_extreme_momentum_gets_penalized():
    candidate = {
        "symbol": "TEST",
        "momentum_30d": 125,
        "trend_strength": 2,
        "volatility": 2,
    }

    assert score_momentum_candidate(candidate) < 100
