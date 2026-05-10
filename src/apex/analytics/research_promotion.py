import csv
from collections import Counter
from pathlib import Path

from apex.core.logger import get_logger

log = get_logger()

SIGNAL_MEMORY_PATH = Path("logs/signal_memory.csv")


def analyze_research_promotions(
    min_appearances: int = 3,
    min_average_score: float = 70,
):
    if not SIGNAL_MEMORY_PATH.exists():
        log.info("No signal memory found for promotion analysis.")
        return []

    with open(SIGNAL_MEMORY_PATH, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    research_rows = [
        row for row in rows
        if row["status"] == "RESEARCH_ONLY"
    ]

    appearances = Counter(
        row["symbol"] for row in research_rows
    )

    recommendations = []

    for symbol, count in appearances.items():
        scores = [
            float(row["score"])
            for row in research_rows
            if row["symbol"] == symbol
        ]

        avg_score = sum(scores) / len(scores)

        if count >= min_appearances and avg_score >= min_average_score:
            recommendations.append(
                {
                    "symbol": symbol,
                    "appearances": count,
                    "average_score": round(avg_score, 2),
                }
            )

    log.info("===== RESEARCH PROMOTION ENGINE =====")

    if not recommendations:
        log.info("No research-only symbols qualify for promotion yet.")
    else:
        for rec in recommendations:
            log.info(
                f"PROMOTION CANDIDATE: {rec['symbol']} | "
                f"Appearances: {rec['appearances']} | "
                f"Avg Score: {rec['average_score']}"
            )

    log.info("=====================================")

    return recommendations
