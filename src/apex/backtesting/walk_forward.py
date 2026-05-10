from statistics import mean

import pandas as pd

from apex.analytics.backtester import run_momentum_backtest
from apex.core.logger import get_logger
from apex.data.market_data import get_stock_bars

log = get_logger()


def run_strategy_walk_forward_test(
    symbol: str,
    train_window: int = 120,
    test_window: int = 60,
):
    df = get_stock_bars(symbol, days=365).reset_index(drop=True)

    start = 0
    results = []

    while start + train_window + test_window < len(df):
        train_df = df.iloc[start : start + train_window]
        test_df = df.iloc[
            start + train_window :
            start + train_window + test_window
        ]

        train_result = run_momentum_backtest(
            symbol=f"{symbol}_TRAIN",
            df=train_df,
        )

        test_result = run_momentum_backtest(
            symbol=f"{symbol}_TEST",
            df=test_df,
        )

        results.append(
            {
                "train_return": train_result.total_return_pct,
                "test_return": test_result.total_return_pct,
                "train_drawdown": train_result.max_drawdown_pct,
                "test_drawdown": test_result.max_drawdown_pct,
                "train_win_rate": train_result.win_rate,
                "test_win_rate": test_result.win_rate,
            }
        )

        start += test_window

    if not results:
        log.info(f"No walk-forward windows available for {symbol}")
        return []

    avg_train = mean([r["train_return"] for r in results])
    avg_test = mean([r["test_return"] for r in results])
    avg_test_drawdown = mean([r["test_drawdown"] for r in results])
    avg_test_win_rate = mean([r["test_win_rate"] for r in results])

    stability_gap = avg_train - avg_test

    log.info("===== STRATEGY WALK FORWARD TEST =====")
    log.info(f"Symbol: {symbol}")
    log.info(f"Windows Tested: {len(results)}")
    log.info(f"Average Strategy Train Return: {avg_train:.2f}%")
    log.info(f"Average Strategy Test Return: {avg_test:.2f}%")
    log.info(f"Average Test Win Rate: {avg_test_win_rate:.2f}%")
    log.info(f"Average Test Drawdown: {avg_test_drawdown:.2f}%")
    log.info(f"Stability Gap: {stability_gap:.2f}%")

    if avg_test <= 0:
        log.info("WARNING: Strategy failed forward test.")
    elif stability_gap > 10:
        log.info("WARNING: Strategy may be unstable.")
    else:
        log.info("Strategy walk-forward acceptable.")

    log.info("======================================")

    return results
