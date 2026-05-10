import csv
from collections import Counter
from pathlib import Path

from apex.core.logger import get_logger

log = get_logger()

SIGNAL_MEMORY_PATH = Path("logs/signal_memory.csv")


def calculate_signal_persistence(
    lookback_rows: int = 100,
) -> dict[str, int]:
    if not SIGNAL_MEMORY_PATH.exists():
        return {}

    with open(SIGNAL_MEMORY_PATH, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    recent_rows = rows[-lookback_rows:]

    symbols = [
        row["symbol"]
        for row in recent_rows
    ]

    return dict(Counter(symbols))


def persistence_bonus(symbol: str) -> int:
    persistence = calculate_signal_persistence()
    appearances = persistence.get(symbol, 0)

    if appearances >= 5:
        bonus = 15
    elif appearances >= 3:
        bonus = 10
    elif appearances >= 2:
        bonus = 5
    else:
        bonus = 0

    if bonus > 0:
        log.info(
            f"{symbol} persistence bonus: +{bonus} "
            f"({appearances} appearances)"
        )

    return bonus
