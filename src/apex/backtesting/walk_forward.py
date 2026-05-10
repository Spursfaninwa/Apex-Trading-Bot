from statistics import mean

from apex.core.logger import get_logger
from apex.data.market_data import get_stock_bars

log = get_logger()


def run_walk_forward_test(
    symbol: str,
    train_window: int = 120,
    test_window: int = 30,
):
    df = get_stock_bars(symbol, days=300)

    closes = df["close"].reset_index(drop=True)

    start = 0

    results = []

    while start + train_window + test_window < len(closes):
        train_data = closes[
            start : start + train_window
        ]

        test_data = closes[
            start + train_window :
            start + train_window + test_window
        ]

        train_return = (
            (train_data.iloc[-1] / train_data.iloc[0]) - 1
        ) * 100

        test_return = (
            (test_data.iloc[-1] / test_data.iloc[0]) - 1
        ) * 100

        results.append(
            {
                "train_return": round(train_return, 2),
                "test_return": round(test_return, 2),
            }
        )

        start += test_window

    train_returns = [
        r["train_return"] for r in results
    ]

    test_returns = [
        r["test_return"] for r in results
    ]

    avg_train = mean(train_returns)
    avg_test = mean(test_returns)

    log.info("===== WALK FORWARD TEST =====")
    log.info(f"Symbol: {symbol}")
    log.info(f"Windows Tested: {len(results)}")
    log.info(f"Average Train Return: {avg_train:.2f}%")
    log.info(f"Average Test Return: {avg_test:.2f}%")

    stability_gap = avg_train - avg_test

    log.info(
        f"Stability Gap: {stability_gap:.2f}%"
    )

    if stability_gap > 10:
        log.info(
            "WARNING: Possible overfitting detected."
        )
    else:
        log.info(
            "Walk-forward stability acceptable."
        )

    log.info("============================")

    return results
