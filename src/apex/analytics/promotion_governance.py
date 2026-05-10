from apex.core.logger import get_logger

log = get_logger()


def evaluate_promotion_candidate(
    symbol: str,
    appearances: int,
    average_score: float,
    min_appearances: int = 5,
    min_average_score: float = 75,
    max_volatility_score_penalty: bool = True,
):
    approved = True
    reasons = []

    if appearances < min_appearances:
        approved = False
        reasons.append("insufficient_appearances")

    if average_score < min_average_score:
        approved = False
        reasons.append("average_score_too_low")

    if symbol in {"TSLA", "AMD"} and max_volatility_score_penalty:
        approved = False
        reasons.append("high_volatility_probation")

    if approved:
        decision = "PROMOTION_APPROVED"
    else:
        decision = "PROMOTION_REJECTED"

    log.info(
        f"PGL Decision: {symbol} | "
        f"{decision} | "
        f"Appearances: {appearances} | "
        f"Avg Score: {average_score} | "
        f"Reasons: {reasons if reasons else 'none'}"
    )

    return {
        "symbol": symbol,
        "approved": approved,
        "decision": decision,
        "reasons": reasons,
    }
