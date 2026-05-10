from dataclasses import dataclass

from apex.risk.risk_engine import RiskEngine
from apex.core.logger import get_logger

log = get_logger()


@dataclass
class TradePlan:
    symbol: str
    entry_price: float
    stop_price: float
    shares: int
    position_value: float
    dollar_risk: float
    approved: bool
    reason: str


def create_trade_plan(candidate, risk_engine: RiskEngine) -> TradePlan:
    symbol = candidate["symbol"]
    entry_price = float(candidate["price"])
    score = float(candidate["score"])

    stop_price = round(entry_price * 0.95, 2)

    sizing = risk_engine.calculate_position_size(
        entry_price=entry_price,
        stop_price=stop_price,
    )

    approved = True
    reason = "Approved"

    if score < 60:
        approved = False
        reason = "Rejected: signal score below 60"

    if sizing.shares <= 0:
        approved = False
        reason = "Rejected: position size too small"

    plan = TradePlan(
        symbol=symbol,
        entry_price=entry_price,
        stop_price=stop_price,
        shares=sizing.shares,
        position_value=sizing.position_value,
        dollar_risk=sizing.dollar_risk,
        approved=approved,
        reason=reason,
    )

    log.info("Trade Plan:")
    log.info(f"Symbol: {plan.symbol}")
    log.info(f"Entry: ${plan.entry_price:.2f}")
    log.info(f"Stop: ${plan.stop_price:.2f}")
    log.info(f"Shares: {plan.shares}")
    log.info(f"Position Value: ${plan.position_value:.2f}")
    log.info(f"Dollar Risk: ${plan.dollar_risk:.2f}")
    log.info(f"Decision: {plan.reason}")

    return plan
