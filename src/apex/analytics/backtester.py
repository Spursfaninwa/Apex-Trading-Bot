from dataclasses import dataclass

import pandas as pd

from apex.analytics.indicators import calculate_atr
from apex.core.logger import get_logger

log = get_logger()


@dataclass
class BacktestResult:
    symbol: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    total_return_pct: float
    max_drawdown_pct: float


def run_momentum_backtest(
    symbol: str,
    df: pd.DataFrame,
    initial_capital: float = 1000,
    risk_per_trade: float = 0.01,
) -> BacktestResult:
    cash = initial_capital
    equity_curve = []
    trades = []
    in_position = False
    entry_price = 0
    stop_price = 0
    shares = 0

    df = df.copy()
    df["sma20"] = df["close"].rolling(20).mean()
    df["sma50"] = df["close"].rolling(50).mean()

    for i in range(60, len(df)):
        row = df.iloc[i]
        price = row["close"]

        if not in_position:
            bullish = price > row["sma20"] > row["sma50"]

            if bullish:
                lookback = df.iloc[: i + 1]
                atr = calculate_atr(lookback)

                entry_price = price
                stop_price = entry_price - (2 * atr)

                risk_amount = cash * risk_per_trade
                risk_per_share = entry_price - stop_price

                if risk_per_share <= 0:
                    continue

                shares = risk_amount / risk_per_share

                position_value = shares * entry_price

                if position_value > cash:
                    shares = cash / entry_price

                cash -= shares * entry_price
                in_position = True

        else:
            exit_signal = (
                price <= stop_price
                or price < row["sma20"]
            )

            if exit_signal:
                cash += shares * price
                pnl = (price - entry_price) * shares
                trades.append(pnl)
                in_position = False
                shares = 0

        equity = cash + (shares * price if in_position else 0)
        equity_curve.append(equity)

    if in_position:
        final_price = df.iloc[-1]["close"]
        cash += shares * final_price
        pnl = (final_price - entry_price) * shares
        trades.append(pnl)

    equity_series = pd.Series(equity_curve)

    if equity_series.empty:
        max_drawdown_pct = 0
    else:
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak
        max_drawdown_pct = drawdown.min() * 100

    total_return_pct = ((cash / initial_capital) - 1) * 100
    wins = len([t for t in trades if t > 0])
    losses = len([t for t in trades if t <= 0])
    trade_count = len(trades)
    win_rate = (wins / trade_count * 100) if trade_count else 0

    result = BacktestResult(
        symbol=symbol,
        trades=trade_count,
        wins=wins,
        losses=losses,
        win_rate=win_rate,
        total_return_pct=total_return_pct,
        max_drawdown_pct=max_drawdown_pct,
    )

    log.info("===== BACKTEST RESULT =====")
    log.info(f"Symbol: {result.symbol}")
    log.info(f"Trades: {result.trades}")
    log.info(f"Wins: {result.wins}")
    log.info(f"Losses: {result.losses}")
    log.info(f"Win Rate: {result.win_rate:.2f}%")
    log.info(f"Total Return: {result.total_return_pct:.2f}%")
    log.info(f"Max Drawdown: {result.max_drawdown_pct:.2f}%")
    log.info("===========================")

    return result
