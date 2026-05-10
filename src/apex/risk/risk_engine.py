from dataclasses import dataclass

from apex.core.logger import get_logger

log = get_logger()


@dataclass
class PositionSizingResult:
    shares: float
    dollar_risk: float
    position_value: float


class RiskEngine:

    def __init__(
        self,
        strategy_capital: float = 1000,
        risk_per_trade: float = 0.01,
        max_position_pct: float = 0.20,
    ):
        self.strategy_capital = strategy_capital
        self.risk_per_trade = risk_per_trade
        self.max_position_pct = max_position_pct

    def calculate_position_size(
        self,
        entry_price: float,
        stop_price: float,
    ) -> PositionSizingResult:

        risk_amount = self.strategy_capital * self.risk_per_trade

        risk_per_share = abs(entry_price - stop_price)

        if risk_per_share <= 0:
            raise ValueError("Invalid stop price.")

        shares = risk_amount / risk_per_share

        max_position_value = (
            self.strategy_capital * self.max_position_pct
        )

        capped_shares = max_position_value / entry_price

        original_shares = shares

        shares = round(min(shares, capped_shares), 4)

        if shares < original_shares:

            log.info(
                "Position capped by max position sizing rules."
            )

        position_value = shares * entry_price
        dollar_risk = shares * risk_per_share

        log.info(f"Entry Price: ${entry_price:.2f}")
        log.info(f"Stop Price: ${stop_price:.2f}")
        log.info(f"Shares: {shares:.4f}")
        log.info(f"Position Value: ${position_value:.2f}")
        log.info(f"Dollar Risk: ${dollar_risk:.2f}")

        return PositionSizingResult(
            shares=shares,
            dollar_risk=dollar_risk,
            position_value=position_value,
        )
