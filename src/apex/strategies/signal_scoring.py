from apex.core.logger import get_logger

log = get_logger()


def score_momentum_candidate(candidate):

    score = 0

    momentum = candidate["momentum_30d"]

    # Base momentum scoring
    if momentum > 20:
        score += 30

    if momentum > 40:
        score += 20

    if momentum > 80:
        score -= 25

    # Trend quality
    trend_strength = candidate.get("trend_strength", 0)

    score += min(trend_strength * 10, 30)

    # Volatility penalty
    volatility = candidate.get("volatility", 0)

    if volatility > 5:
        score -= 15

    # Reward smoother trends
    if volatility < 3:
        score += 10

    final_score = max(score, 0)

    log.info(
        f"{candidate['symbol']} scored {final_score}"
    )

    return final_score
