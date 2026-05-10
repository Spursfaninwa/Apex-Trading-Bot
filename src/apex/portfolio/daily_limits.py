import csv
from pathlib import Path
from datetime import datetime

from apex.core.logger import get_logger

log = get_logger()

JOURNAL_PATH = Path("logs/trade_journal.csv")


def daily_trade_count() -> int:

    if not JOURNAL_PATH.exists():
        return 0

    today = datetime.utcnow().date()

    count = 0

    with open(JOURNAL_PATH, "r") as f:

        reader = csv.DictReader(f)

        for row in reader:

            timestamp = datetime.fromisoformat(
                row["timestamp"]
            )

            if timestamp.date() == today:
                count += 1

    return count


def daily_trade_limit_reached(
    max_trades_per_day: int = 3,
) -> bool:

    count = daily_trade_count()

    log.info(
        f"Today's trade count: {count}"
    )

    if count >= max_trades_per_day:

        log.info(
            "Daily trade limit reached."
        )

        return True

    return False
