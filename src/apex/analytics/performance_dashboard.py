import pandas as pd
from pathlib import Path

from apex.core.logger import get_logger

log = get_logger()

JOURNAL_PATH = Path("logs/trade_journal.csv")


def show_performance_dashboard():
    if not JOURNAL_PATH.exists():
        log.info("No trade journal found yet.")
        return

    df = pd.read_csv(JOURNAL_PATH)

    if df.empty:
        log.info("Trade journal is empty.")
        return

    total_plans = len(df)
    approved = df[df["decision"] == "Approved"]
    rejected = df[df["decision"] != "Approved"]

    total_position_value = df["position_value"].sum()
    total_dollar_risk = df["dollar_risk"].sum()
    avg_dollar_risk = df["dollar_risk"].mean()

    log.info("===== APEX PERFORMANCE DASHBOARD =====")
    log.info(f"Total trade plans: {total_plans}")
    log.info(f"Approved plans: {len(approved)}")
    log.info(f"Rejected plans: {len(rejected)}")
    log.info(f"Total planned exposure: ${total_position_value:.2f}")
    log.info(f"Total planned dollar risk: ${total_dollar_risk:.2f}")
    log.info(f"Average dollar risk: ${avg_dollar_risk:.2f}")

    log.info("Top symbols by plan count:")

    symbol_counts = df["symbol"].value_counts()

    for symbol, count in symbol_counts.items():
        log.info(f"{symbol}: {count}")

    log.info("======================================")
