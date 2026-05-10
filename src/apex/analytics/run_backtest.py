from apex.data.market_data import get_stock_bars
from apex.analytics.backtester import run_momentum_backtest
from apex.analytics.equity_curve import save_equity_curve

WATCHLIST = [
    "SPY",
    "QQQ",
    "NVDA",
    "AMZN",
    "GOOGL",
    "AAPL",
    "MSFT",
    "META",
    "TSLA",
    "AMD",
]


def main():
    results = []

    for symbol in WATCHLIST:
        try:
            df = get_stock_bars(symbol, days=365)

            result = run_momentum_backtest(
                symbol,
                df,
            )

            save_equity_curve(
                result.symbol,
                result.equity_curve,
            )

            results.append(result)

        except Exception as e:
            print(f"{symbol} failed: {e}")

    print("\n===== STRATEGY RANKINGS =====")

    ranked = sorted(
        results,
        key=lambda r: r.total_return_pct,
        reverse=True,
    )

    for r in ranked:
        print(
            f"{r.symbol} | "
            f"Return: {r.total_return_pct:.2f}% | "
            f"Win Rate: {r.win_rate:.2f}% | "
            f"Drawdown: {r.max_drawdown_pct:.2f}%"
        )

    print("=============================")
    print("Equity curves saved in reports/")


if __name__ == "__main__":
    main()
