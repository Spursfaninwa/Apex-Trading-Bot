import csv
from pathlib import Path
from datetime import datetime

from apex.core.logger import get_logger

log = get_logger()

JOURNAL_PATH = Path("logs/trade_journal.csv")


def initialize_journal():

    if JOURNAL_PATH.exists():
        return

    with open(JOURNAL_PATH, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "timestamp",
            "symbol",
            "entry_price",
            "stop_price",
            "shares",
            "position_value",
            "dollar_risk",
            "decision",
        ])

    log.info("Trade journal initialized.")


def log_trade_plan(trade_plan):

    initialize_journal()

    with open(JOURNAL_PATH, "a", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            datetime.utcnow().isoformat(),
            trade_plan.symbol,
            trade_plan.entry_price,
            trade_plan.stop_price,
            trade_plan.shares,
            trade_plan.position_value,
            trade_plan.dollar_risk,
            trade_plan.reason,
        ])

    log.info(
        f"Trade journal updated for {trade_plan.symbol}"
    )
