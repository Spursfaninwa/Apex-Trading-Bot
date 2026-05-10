import csv
from pathlib import Path
from datetime import datetime

from apex.core.logger import get_logger

log = get_logger()

SIGNAL_MEMORY_PATH = Path("logs/signal_memory.csv")


def initialize_signal_memory():
    SIGNAL_MEMORY_PATH.parent.mkdir(exist_ok=True)

    if SIGNAL_MEMORY_PATH.exists():
        return

    with open(SIGNAL_MEMORY_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "symbol",
            "status",
            "price",
            "momentum_30d",
            "score",
        ])

    log.info("Signal memory initialized.")


def log_signal_candidates(candidates: list[dict]):
    initialize_signal_memory()

    with open(SIGNAL_MEMORY_PATH, "a", newline="") as f:
        writer = csv.writer(f)

        for candidate in candidates:
            status = (
                "TRADE_APPROVED"
                if candidate.get("approved_for_trade")
                else "RESEARCH_ONLY"
            )

            writer.writerow([
                datetime.utcnow().isoformat(),
                candidate["symbol"],
                status,
                candidate["price"],
                candidate["momentum_30d"],
                candidate["score"],
            ])

    log.info(
        f"Signal memory updated with {len(candidates)} candidates."
    )
