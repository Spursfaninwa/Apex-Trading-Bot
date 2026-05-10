from apex.data.market_data import get_stock_bars
from apex.analytics.backtester import run_momentum_backtest


def main():
    df = get_stock_bars("QQQ", days=365)
    run_momentum_backtest("QQQ", df)


if __name__ == "__main__":
    main()
