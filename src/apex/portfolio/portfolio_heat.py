import csv
from pathlib import Path
from datetime import datetime

from apex.core.logger import get_logger

log = get_logger()

JOURNAL_PATH = Path("logs/trade_journal.csv")


def calculate_today_planned_risk() -> float:
    if not JOURNAL_PATH.exists():
        return 0.0

    today = datetime.utcnow().date()
    total_risk = 0.0

    with open(JOURNAL_PATH, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            timestamp = datetime.fromisoformat(row["timestamp"])

            if timestamp.date() == today:
                total_risk += float(row["dollar_risk"])

    return total_risk


def portfolio_heat_limit_reached(
    strategy_capital: float = 1000,
    max_portfolio_risk_pct: float = 0.05,
) -> bool:
    current_risk = calculate_today_planned_risk()
    max_allowed_risk = strategy_capital * max_portfolio_risk_pct

    log.info(f"Current planned portfolio risk: ${current_risk:.2f}")
    log.info(f"Max allowed portfolio risk: ${max_allowed_risk:.2f}")

    if current_risk >= max_allowed_risk:
        log.info("Portfolio heat block: max risk reached.")
        return True

    return False
