import csv
from pathlib import Path
from datetime import datetime, timedelta

from apex.core.logger import get_logger

log = get_logger()

JOURNAL_PATH = Path("logs/trade_journal.csv")


def symbol_on_cooldown(
    symbol: str,
    cooldown_hours: int = 24,
) -> bool:

    if not JOURNAL_PATH.exists():
        return False

    now = datetime.utcnow()

    with open(JOURNAL_PATH, "r") as f:

        reader = csv.DictReader(f)

        rows = list(reader)

    rows.reverse()

    for row in rows:

        if row["symbol"] != symbol:
            continue

        timestamp = datetime.fromisoformat(
            row["timestamp"]
        )

        delta = now - timestamp

        if delta < timedelta(hours=cooldown_hours):

            log.info(
                f"{symbol} on cooldown "
                f"({delta.seconds // 3600}h elapsed)"
            )

            return True

        return False

    return False
